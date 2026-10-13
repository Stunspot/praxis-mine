#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import os
import stat
from functools import wraps
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
POSITIVE_KEYS = {
    "new_outcome",
    "executable_leverage",
    "domain_judgment",
    "evidence_quality",
    "maintainability",
    "portability",
    "context_efficiency",
}
RISK_KEYS = {"security", "privacy", "license", "cost_dependency", "overlap"}
DISPOSITIONS = {"pilot", "quarry", "adapt", "monitor", "reject"}
IGNORE_PARTS = {".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def load_storage():
    import_root = SKILL_ROOT / "scripts" / "vendor"
    if not (import_root / "praxis_store" / "storage.py").is_file():
        raise RuntimeError("the packaged Praxis Mine record store is missing")
    sys.path.insert(0, str(import_root))
    from praxis_store import storage

    return storage


def strict_json(text: str) -> Any:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result: raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    def nonfinite(value): raise ValueError(f"nonfinite JSON value: {value}")
    return json.loads(text, object_pairs_hook=pairs, parse_constant=nonfinite)


def read_json(path: Path) -> Any:
    try:
        return strict_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise RuntimeError(f"could not read JSON from {path}: {exc}") from exc


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def slug(value: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return clean[:40] or "candidate"


def stable_key(prefix: str, locator: str) -> str:
    suffix = hashlib.sha256(locator.encode("utf-8")).hexdigest()[:12]
    return f"{slug(prefix)}_{suffix}"


def existing_store(storage, home: Path) -> dict[str, Any]:
    registry = home.expanduser().resolve(strict=False) / "registry.sqlite"
    if not registry.is_file():
        raise RuntimeError(f"No Praxis ledger at {home}. Select your existing data home or run init to create one.")
    storage.initialize_home(home)  # Existing registries are validated, never relabelled.
    records = {r["store_name"]: r for r in storage.list_stores(home)}
    row = records.get("praxis_mine")
    if row is None or row["status"] != "active" or Path(row["store_path"]).resolve() != storage.store_path(home, "praxis_mine"):
        raise RuntimeError("Praxis store is missing, inactive or registered at a different location; preserve it for recovery")
    health = storage.check_store(home, "praxis_mine")
    if not health["healthy"]:
        raise RuntimeError("Praxis ledger failed integrity checks; stop writes and recover from a verified backup")
    return health


def ensure_store(storage, home: Path, actor: str) -> dict[str, Any]:
    registry = home.expanduser().resolve(strict=False) / "registry.sqlite"
    if registry.is_file():
        storage.initialize_home(home)
        stores = {item["store_name"] for item in storage.list_stores(home)}
    else:
        storage.initialize_home(home)
        stores = set()
    if "praxis_mine" not in stores:
        storage.create_store(home, "praxis_mine", "External praxis discovery and admission ledger", actor, "internal")
    health = existing_store(storage, home)
    if health["contract_versions"] == 0:
        storage.install_contract(home, "praxis_mine", read_json(SKILL_ROOT / "assets" / "praxis_mine.contract.json"), actor)
    return existing_store(storage, home)


def atomic_operation(function):
    @wraps(function)
    def wrapped(storage, home, *args, **kwargs):
        ensure_store(storage, home, kwargs.get("actor", "praxis-mine"))
        with storage.transaction(home, "praxis_mine"):
            return function(storage, home, *args, **kwargs)
    return wrapped


def candidate_snapshot(storage, home, candidate):
    payload = candidate["payload"] if "payload" in candidate else candidate
    source = find_record(storage, home, "source", "source_key", payload["source_key"])
    if source is None: raise RuntimeError("candidate source is not active")
    material = {key: payload.get(key) for key in ("candidate_key", "source_key", "locator", "candidate_kind", "summary", "content_hash", "license", "evidence_state")}
    source_material = {key: source["payload"].get(key) for key in ("source_key", "kind", "locator", "access_posture")}
    return {"candidate": material, "source": source_material}


def evaluation_is_current(storage, home, candidate, evaluation):
    snapshot = evaluation.get("provenance", {}).get("assessed_snapshot")
    return snapshot is not None and snapshot == candidate_snapshot(storage, home, candidate)


def find_record(storage, home: Path, record_type: str, key_field: str, key: str) -> dict[str, Any] | None:
    for record in storage.list_records(home, "praxis_mine", record_type, status="active"):
        if record["payload"].get(key_field) == key:
            return record
    return None


def latest_evaluation(storage, home: Path, candidate_key: str, *, include_stale=False):
    candidate = find_record(storage, home, "candidate", "candidate_key", candidate_key)
    if candidate is None: return None
    matches = (record for record in storage.list_records(home, "praxis_mine", "evaluation")
               if record["payload"]["candidate_key"] == candidate_key and
               (include_stale or evaluation_is_current(storage, home, candidate, record)))
    return max(matches, key=lambda record: (record["payload"]["evaluated_at"], record["recorded_at"], record["record_id"]), default=None)


def upsert(storage, home: Path, record_type: str, key_field: str, payload: dict[str, Any], actor: str, provenance: dict[str, Any], source_kind: str) -> tuple[dict[str, Any], str]:
    key = payload[key_field]
    existing = find_record(storage, home, record_type, key_field, key)
    if existing is None:
        record_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"praxis-mine:{record_type}:{key}"))
        record = storage.add_record(home, "praxis_mine", record_type, payload, actor, source_kind, provenance, record_id=record_id)
        return record, "created"
    if canonical(existing["payload"]) == canonical(payload):
        return existing, "unchanged"
    record = storage.revise_record(home, "praxis_mine", existing["record_id"], payload, actor, source_kind, provenance, "source refresh", expected_version=existing["current_version"])
    return record, "revised"


def normalize_source(source: dict[str, Any]) -> dict[str, Any]:
    required = {"source_key", "title", "kind", "locator", "access_posture"}
    if not isinstance(source, dict):
        raise RuntimeError("source must be a JSON object")
    missing = sorted(key for key in required if not isinstance(source.get(key), str) or not source[key].strip())
    if missing:
        raise RuntimeError(f"source needs nonempty text for: {', '.join(missing)}")
    return {key: source[key] for key in ("source_key", "title", "kind", "locator", "access_posture", "cadence", "notes") if key in source}


def normalize_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    required = {"source_key", "title", "locator", "candidate_kind", "summary"}
    if not isinstance(candidate, dict):
        raise RuntimeError("candidate must be a JSON object")
    missing = sorted(key for key in required if not isinstance(candidate.get(key), str) or not candidate[key].strip())
    if missing:
        raise RuntimeError(f"candidate needs nonempty text for: {', '.join(missing)}")
    result = dict(candidate)
    result["candidate_key"] = result.get("candidate_key") or stable_key(result["title"], result["locator"])
    if not isinstance(result["candidate_key"], str) or not result["candidate_key"].strip():
        raise RuntimeError("candidate_key must be nonempty text")
    result.setdefault("candidate_status", "triage")
    result.setdefault("evidence_state", "reported_unverified")
    if not isinstance(result["candidate_status"], str) or result["candidate_status"] not in DISPOSITIONS | {"triage"}:
        raise RuntimeError("candidate_status is not a supported assessment state; adoption is a separate owner acceptance")
    if "tags" in result and not (isinstance(result["tags"], dict) or isinstance(result["tags"], list) and all(isinstance(v, str) for v in result["tags"])):
        raise RuntimeError("candidate tags must be an object or a legacy text list")
    allowed = {"candidate_key", "source_key", "title", "locator", "candidate_kind", "summary", "content_hash", "license", "candidate_status", "evidence_state", "tags"}
    return {key: result[key] for key in allowed if key in result}


def prepare_manifest(storage, home: Path, manifest: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(manifest, dict) or not isinstance(manifest.get("sources"), list) or not isinstance(manifest.get("candidates"), list):
        raise RuntimeError("manifest requires sources and candidates arrays")
    if set(manifest) - {"sources", "candidates", "notes"}:
        raise RuntimeError("manifest has unknown top-level fields")
    source_payloads = [normalize_source(item) for item in manifest["sources"]]
    candidate_payloads = [normalize_candidate(item) for item in manifest["candidates"]]
    for label, payloads in (("source", source_payloads), ("candidate", candidate_payloads)):
        keys = [item[label + "_key"] for item in payloads]
        if len(keys) != len(set(keys)):
            raise RuntimeError(f"manifest repeats a {label} identity")
    connection = storage.require_store(home, "praxis_mine", read_only=True)[1]
    try:
        definitions = {kind: storage.record_definition(connection, kind) for kind in ("source", "candidate")}
        for payload in source_payloads:
            storage.validate_payload(definitions["source"], payload)
        for payload in candidate_payloads:
            storage.validate_payload(definitions["candidate"], payload)
    finally:
        connection.close()
    sources = {item["payload"]["source_key"] for item in storage.list_records(home, "praxis_mine", "source", status=None)}
    sources.update(item["source_key"] for item in source_payloads)
    existing = {item["payload"]["candidate_key"]: item["payload"]["source_key"]
                for item in storage.list_records(home, "praxis_mine", "candidate", status=None)}
    for payload in candidate_payloads:
        if payload["source_key"] not in sources:
            raise RuntimeError(f"candidate references unknown source: {payload['source_key']}")
        if payload["candidate_key"] not in existing and payload["candidate_status"] != "triage":
            raise RuntimeError("new imported candidates begin in triage; disposition requires a native evaluation")
        if payload["candidate_key"] in existing and existing[payload["candidate_key"]] != payload["source_key"]:
            raise RuntimeError("candidate source identity cannot change; preserve its provenance trail")
    return source_payloads, candidate_payloads


@atomic_operation
def ingest_manifest(storage, home: Path, path: Path, actor: str) -> dict[str, Any]:
    raw = path.read_bytes()
    manifest = strict_json(raw.decode("utf-8"))
    source_payloads, candidate_payloads = prepare_manifest(storage, home, manifest)
    source_records: dict[str, dict[str, Any]] = {}
    counts = {"sources_created": 0, "sources_revised": 0, "sources_unchanged": 0, "candidates_created": 0, "candidates_revised": 0, "candidates_unchanged": 0}
    provenance = {"manifest": str(path.resolve()), "manifest_sha256": hashlib.sha256(raw).hexdigest()}
    started = utc_now()
    for payload in source_payloads:
        record, action = upsert(storage, home, "source", "source_key", payload, actor, provenance, "supplied")
        source_records[payload["source_key"]] = record
        counts[f"sources_{action}"] += 1
    for payload in candidate_payloads:
        payload = dict(payload)
        existing = find_record(storage, home, "candidate", "candidate_key", payload["candidate_key"])
        if existing:
            # Optional owner metadata survives an acquisition refresh unless explicitly supplied.
            payload = {**existing["payload"], **payload}
        assessment = latest_evaluation(storage, home, payload["candidate_key"])
        payload["candidate_status"] = assessment["payload"]["disposition"] if assessment and evaluation_is_current(storage, home, payload, assessment) else "triage"
        source = source_records.get(payload["source_key"]) or find_record(storage, home, "source", "source_key", payload["source_key"])
        if source is None:
            raise RuntimeError(f"candidate references unknown source: {payload['source_key']}")
        record, action = upsert(storage, home, "candidate", "candidate_key", payload, actor, provenance, "supplied")
        counts[f"candidates_{action}"] += 1
        if action == "created":
            storage.add_relation(home, "praxis_mine", "source_contains_candidate", source["record_id"], record["record_id"], actor, provenance)
    run_key = stable_key(path.stem, f"{provenance['manifest_sha256']}:{started}")
    for source_key in source_records:
        run_payload = {"run_key": f"{run_key}_{slug(source_key)}", "source_key": source_key, "started_at": started, "completed_at": utc_now(), "route": "manifest", "counts": counts, "notes": manifest.get("notes", "")}
        upsert(storage, home, "run", "run_key", run_payload, actor, provenance, "deterministic")
    return {"manifest": str(path.resolve()), "counts": counts, "run_key": run_key}


def checked_tree(root: Path):
    root = root.expanduser().absolute()
    # Inspect lexical ancestors BEFORE resolve: a selected junction is not authority to follow it.
    for path in (root, *root.parents):
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise RuntimeError(f"linked/reparse scan path refused: {path}")
    if not root.is_dir(): raise RuntimeError("scan root must be a directory")
    files = []
    def failed(error): raise error
    for base, directories, names in os.walk(root, followlinks=False, onerror=failed):
        directories[:] = sorted(name for name in directories if name not in IGNORE_PARTS)
        for name in directories + names:
            path = Path(base) / name
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise RuntimeError(f"linked/reparse scan member refused: {path}")
            if name in names:
                if not stat.S_ISREG(info.st_mode): raise RuntimeError(f"nonregular scan member: {path}")
                files.append(path)
    return root, sorted(files, key=lambda path: path.relative_to(root).as_posix())


def directory_hash(root: Path) -> tuple[str, int]:
    root, files = checked_tree(root)
    digest = hashlib.sha256(b"praxis-tree-v2\0")
    for path in files:
        before = path.stat()
        content = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                content.update(chunk)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
            raise RuntimeError(f"scan member changed while reading: {path}")
        frame = canonical([path.relative_to(root).as_posix(), before.st_size, content.hexdigest()]).encode("utf-8")
        digest.update(len(frame).to_bytes(8, "big")); digest.update(frame)
    return digest.hexdigest(), len(files)


def title_and_summary(root: Path) -> tuple[str, str]:
    for name in ("SKILL.md", "README.md", "README", "pyproject.toml", "package.json"):
        path = root / name
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        title = root.name
        description = ""
        if name == "SKILL.md":
            match_name = re.search(r"(?m)^name:\s*[\"']?([^\n\"']+)", text)
            match_description = re.search(r"(?m)^description:\s*[\"']?([^\n\"']+)", text)
            title = match_name.group(1).strip() if match_name else title
            description = match_description.group(1).strip() if match_description else ""
        else:
            for line in text.splitlines():
                clean = line.strip().lstrip("#").strip()
                if clean and not clean.startswith(("---", "{", "[")):
                    description = clean
                    break
        return title[:200], (description or f"Local candidate rooted at {root}")[:1000]
    return root.name, f"Local candidate rooted at {root}"


def local_candidate_roots(root: Path) -> list[Path]:
    root, files = checked_tree(root)
    markers = {"SKILL.md", "pyproject.toml", "package.json"}
    return sorted({path.parent for path in files if path.name in markers}, key=lambda p: p.as_posix())


def scan_local(storage, home: Path, root: Path, source_key: str, actor: str) -> dict[str, Any]:
    root, _ = checked_tree(root)
    source_payload = {"source_key": source_key, "title": root.name or str(root), "kind": "local_directory", "locator": str(root), "access_posture": "read_only_local", "cadence": "manual", "notes": "Local metadata and complete framed content hashes; license files are not interpreted."}
    payloads = []
    for candidate_root in local_candidate_roots(root):
        title, summary = title_and_summary(candidate_root)
        digest, file_count = directory_hash(candidate_root)
        payloads.append(normalize_candidate({"source_key": source_key, "title": title, "locator": str(candidate_root), "candidate_kind": "agent_skill" if (candidate_root / "SKILL.md").is_file() else "software_tool", "summary": summary, "content_hash": digest, "evidence_state": "locally_observed", "tags": {"file_count": file_count, "license_files": [p.name for p in candidate_root.glob("LICENSE*") if p.is_file()]}}))
    # No ledger writes until every selected candidate has been read successfully.
    ensure_store(storage, home, actor)
    with storage.transaction(home, "praxis_mine"):
        started = utc_now()
        source, _ = upsert(storage, home, "source", "source_key", source_payload, actor, {"route": "local_scan"}, "observed")
        counts = {"created": 0, "revised": 0, "unchanged": 0}
        for payload in payloads:
            existing = find_record(storage, home, "candidate", "candidate_key", payload["candidate_key"])
            if existing:
                if existing["payload"]["source_key"] != source_key: raise RuntimeError("candidate source identity cannot change")
                payload = {**existing["payload"], **payload, "tags": {**(existing["payload"].get("tags", {}) if isinstance(existing["payload"].get("tags", {}), dict) else {"retained_tags": existing["payload"]["tags"]}), **payload["tags"]}}
            assessment = latest_evaluation(storage, home, payload["candidate_key"])
            payload["candidate_status"] = assessment["payload"]["disposition"] if assessment and evaluation_is_current(storage, home, payload, assessment) else "triage"
            record, action = upsert(storage, home, "candidate", "candidate_key", payload, actor, {"root": str(root), "route": "local_scan", "hash_format": "praxis-tree-v2"}, "observed")
            counts[action] += 1
            if action == "created": storage.add_relation(home, "praxis_mine", "source_contains_candidate", source["record_id"], record["record_id"], actor, {"route": "local_scan"})
        run_key = stable_key(source_key, f"{root}:{started}")
        run_payload = {"run_key": run_key, "source_key": source_key, "started_at": started, "completed_at": utc_now(), "route": "local_scan", "counts": counts}
        upsert(storage, home, "run", "run_key", run_payload, actor, {"root": str(root)}, "deterministic")
    return {"source_key": source_key, "root": str(root), "counts": counts, "run_key": run_key}


def validate_score_map(value: Any, expected: set[str], label: str) -> dict[str, int]:
    if not isinstance(value, dict) or set(value) != expected:
        raise RuntimeError(f"{label} must contain exactly: {', '.join(sorted(expected))}")
    if any(not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 5 for score in value.values()):
        raise RuntimeError(f"{label} values must be integers from 0 through 5")
    return value


def decide(positive: dict[str, int], risks: dict[str, int], preferred: str) -> tuple[float, str]:
    positive_score = sum(positive.values()) / (5 * len(POSITIVE_KEYS)) * 100
    risk_penalty = sum(risks.values()) / (5 * len(RISK_KEYS)) * 40
    score = round(max(0.0, positive_score - risk_penalty), 2)
    if preferred == "reject": return score, "reject"
    if max(risks[key] for key in ("security", "privacy", "license")) >= 4:
        return score, "reject"
    # A score ranks candidates; it never expands the evaluator's requested action.
    if preferred == "monitor": return score, "monitor"
    if risks["overlap"] >= 4 and preferred == "pilot":
        return score, "monitor"
    return score, preferred


def decision_gaps(supplied):
    context = supplied.get("decision_context", {})
    if not isinstance(context, dict): raise RuntimeError("decision_context must be an object")
    allowed = {"baseline", "comparison", "rights_basis", "reason", "owner", "action_scope", "rights_status"}
    if set(context) - allowed: raise RuntimeError("unknown decision_context fields")
    if any(not isinstance(value, str) for value in context.values()): raise RuntimeError("decision_context fields must be text")
    placeholders = {"unknown", "n/a", "none", "todo", "tbd", "not checked", "not verified"}
    missing = [key for key in ("baseline", "comparison", "rights_basis", "reason") if not context.get(key, "").strip() or context[key].strip().lower() in placeholders]
    rights_status = context.get("rights_status", "unresolved")
    if rights_status not in {"compatible", "not_applicable", "unresolved", "incompatible"}:
        raise RuntimeError("rights_status must be compatible, not_applicable, unresolved or incompatible")
    if rights_status == "unresolved": missing.append("rights_status")
    return context, missing


@atomic_operation

def evaluate(storage, home: Path, candidate_key: str, evaluation_path: Path, actor: str) -> dict[str, Any]:
    candidate = find_record(storage, home, "candidate", "candidate_key", candidate_key)
    if candidate is None:
        raise RuntimeError(f"unknown candidate: {candidate_key}")
    raw = evaluation_path.read_bytes()
    supplied = strict_json(raw.decode("utf-8"))
    if not isinstance(supplied, dict):
        raise RuntimeError("evaluation must be a JSON object")
    positive = validate_score_map(supplied.get("positive_scores"), POSITIVE_KEYS, "positive_scores")
    risks = validate_score_map(supplied.get("risk_scores"), RISK_KEYS, "risk_scores")
    preferred = supplied.get("preferred_disposition", "monitor")
    if not isinstance(preferred, str) or preferred not in DISPOSITIONS:
        raise RuntimeError(f"preferred_disposition must be one of: {', '.join(sorted(DISPOSITIONS))}")
    if preferred == "reject" and not supplied.get("next_test"):
        supplied["next_test"] = "No further test required for this rejection; revisit only if its stated reason changes."
    for required in ("capability_delta", "next_test"):
        if not isinstance(supplied.get(required), str) or not supplied[required].strip():
            raise RuntimeError(f"evaluation requires nonempty text for {required}")
    if not isinstance(supplied.get("evidence"), list) or not supplied["evidence"]:
        raise RuntimeError("evaluation requires a nonempty evidence list")
    if any(not isinstance(item, str) or not item.strip() for item in supplied["evidence"]):
        raise RuntimeError("evaluation evidence must contain nonempty references")
    context, gaps = decision_gaps(supplied)
    snapshot = candidate_snapshot(storage, home, candidate)
    fingerprint = hashlib.sha256(canonical([supplied, snapshot]).encode("utf-8")).hexdigest()[:20]
    evaluation_key = f"{candidate_key}_{fingerprint}"
    existing_evaluation = find_record(storage, home, "evaluation", "evaluation_key", evaluation_key)
    score, disposition = decide(positive, risks, preferred)
    if context.get("rights_status") == "incompatible": disposition = "reject"
    license_label = str(candidate["payload"].get("license", "unknown")).strip().lower()
    if context.get("rights_status") == "compatible" and (license_label in {"", "unknown", "not checked", "n/a"} or re.fullmatch(r"licen[sc]e(?:\.[a-z]+)?", license_label)):
        gaps.append("candidate license conclusion (a filename is not a license)")
    if disposition in {"pilot", "adapt", "quarry"} and gaps:
        disposition = "monitor"
    evaluated_at = existing_evaluation["payload"]["evaluated_at"] if existing_evaluation else utc_now()
    payload = {"evaluation_key": evaluation_key, "candidate_key": candidate_key, "evaluated_at": evaluated_at, "positive_scores": positive, "risk_scores": risks, "weighted_score": score, "capability_delta": supplied["capability_delta"], "evidence": supplied["evidence"], "disposition": disposition, "next_test": supplied["next_test"], "notes": supplied.get("notes", "")}
    provenance = {"evaluation_file": str(evaluation_path.resolve()), "evaluation_sha256": hashlib.sha256(raw).hexdigest(), "assessed_snapshot": snapshot, "decision_context": context, "decision_gaps": gaps, "requested_disposition": preferred, "assessment_boundary": "Declared evidence and judgment; references and rights are not independently verified by this ledger"}
    record, action = upsert(storage, home, "evaluation", "evaluation_key", payload, actor, provenance, "derived")
    if action == "created":
        storage.add_relation(home, "praxis_mine", "candidate_has_evaluation", candidate["record_id"], record["record_id"], actor, provenance)
    current_assessment = latest_evaluation(storage, home, candidate_key)
    current_disposition = current_assessment["payload"]["disposition"]
    if candidate["payload"]["candidate_status"] != current_disposition:
        candidate_payload = dict(candidate["payload"])
        candidate_payload["candidate_status"] = current_disposition
        storage.revise_record(home, "praxis_mine", candidate["record_id"], candidate_payload, actor, "derived", provenance, "evaluation disposition", expected_version=candidate["current_version"])
    return {"candidate_key": candidate_key, "evaluation_key": payload["evaluation_key"], "weighted_score": score, "disposition": disposition, "current_disposition": current_disposition, "decision_gaps": gaps, "action": action}


def candidate_report(storage, home, record):
    item = record["payload"]
    evaluation = latest_evaluation(storage, home, item["candidate_key"])
    historical = latest_evaluation(storage, home, item["candidate_key"], include_stale=True)
    state = "current material snapshot" if evaluation else "stale or legacy unbound evaluation; reassess" if historical else "not evaluated"
    disposition = evaluation["payload"]["disposition"] if evaluation else "triage"
    lines = [f"## {item['title']}", "", f"- Candidate: `{item['candidate_key']}`", f"- Kind: {item['candidate_kind']}", f"- Source: `{item['source_key']}`", f"- Locator: {item['locator']}", f"- Evidence state: {item['evidence_state']}", f"- Assessment: {state}", f"- Disposition: **{disposition}**", f"- Summary: {item['summary']}", f"- Owner context: {canonical(item.get('tags', {}))}"]
    if evaluation:
        value = evaluation["payload"]; provenance = evaluation["provenance"]
        lines += [f"- Weighted priority score: {value['weighted_score']} (not proof)", f"- Capability delta: {value['capability_delta']}", f"- Next test/action: {value['next_test']}", f"- Risks: {canonical(value['risk_scores'])}", f"- Judgment notes: {value.get('notes', '')}", f"- Missing decision basis: {', '.join(provenance.get('decision_gaps', [])) or 'none declared'}"]
        lines += [f"- {key.replace('_', ' ').title()}: {val}" for key, val in provenance.get("decision_context", {}).items()]
        lines += ["", "Evidence references (supplied, not independently verified by the ledger):"] + [f"- {ref}" for ref in value["evidence"]]
    if historical and not evaluation:
        lines += [f"- Historical disposition: {historical['payload']['disposition']} at {historical['payload']['evaluated_at']}; not current authority."]
    return "\n".join(lines) + "\n"


def report(storage, home: Path) -> str:
    existing_store(storage, home)
    with storage.transaction(home, "praxis_mine", read_only=True):
        candidates = storage.list_records(home, "praxis_mine", "candidate")
        evaluations = storage.list_records(home, "praxis_mine", "evaluation")
        lines = ["# Praxis Mine report", "", f"Generated: {utc_now()}", "", f"Candidates: {len(candidates)} | Evaluations: {len(evaluations)}", "", "Assessment is not installation, integration or production acceptance. Confirm recipient scope before sharing private source details.", ""]
        lines += [candidate_report(storage, home, r) for r in sorted(candidates, key=lambda r: r["payload"]["title"].lower())]
        return "\n".join(lines)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Source-agnostic external praxis discovery and admission ledger")
    result.add_argument("--data-home", type=Path, help="Praxis Mine data home (default: PRAXIS_MINE_DATA_HOME or ~/.praxis-mine/data)")
    result.add_argument("--actor", default="praxis-mine")
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    ingest = commands.add_parser("ingest-manifest")
    ingest.add_argument("manifest", type=Path)
    scan = commands.add_parser("scan-local")
    scan.add_argument("root", type=Path)
    scan.add_argument("--source-key", required=True)
    assess = commands.add_parser("evaluate")
    assess.add_argument("candidate_key")
    assess.add_argument("evaluation", type=Path)
    output = commands.add_parser("report")
    output.add_argument("--output", type=Path)
    commands.add_parser("status")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        storage = load_storage()
        home = args.data_home.expanduser() if args.data_home else storage.default_home()
        if args.command == "init":
            value = ensure_store(storage, home, args.actor)
        elif args.command == "ingest-manifest":
            value = ingest_manifest(storage, home, args.manifest, args.actor)
        elif args.command == "scan-local":
            value = scan_local(storage, home, args.root, args.source_key, args.actor)
        elif args.command == "evaluate":
            value = evaluate(storage, home, args.candidate_key, args.evaluation, args.actor)
        elif args.command == "report":
            rendered = report(storage, home)
            if args.output:
                output_path = args.output.expanduser().resolve(strict=False)
                with output_path.open("x", encoding="utf-8", newline="\n") as stream:
                    stream.write(rendered + "\n")
                value = {"output": str(output_path), "sha256": hashlib.sha256(output_path.read_bytes()).hexdigest()}
            else:
                print(rendered)
                return 0
        else:
            existing_store(storage, home)
            candidates = storage.list_records(home, "praxis_mine", "candidate", status=None)
            evaluations = storage.list_records(home, "praxis_mine", "evaluation", status=None)
            value = {"health": storage.check_store(home, "praxis_mine"), "candidates": len(candidates), "evaluations": len(evaluations), "awaiting_evaluation": sum(1 for item in candidates if latest_evaluation(storage, home, item["payload"]["candidate_key"]) is None)}
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

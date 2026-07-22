#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
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


def load_substrate():
    override = os.environ.get("CD_DATA_SUBSTRATE_ROOT")
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    root = Path(override).expanduser() if override else codex_home / "data-substrate"
    if (root / "cd_data_substrate" / "storage.py").is_file():
        import_root = root
    else:
        bundled = SKILL_ROOT / "scripts" / "vendor"
        if not (bundled / "cd_data_substrate" / "storage.py").is_file():
            raise RuntimeError(
                f"CD Data Substrate is not installed at {root} and the packaged runtime is absent"
            )
        import_root = bundled
    sys.path.insert(0, str(import_root))
    from cd_data_substrate import storage

    return storage


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"could not read JSON from {path}: {exc}") from exc


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return clean[:40] or "candidate"


def stable_key(prefix: str, locator: str) -> str:
    suffix = hashlib.sha256(locator.encode("utf-8")).hexdigest()[:12]
    return f"{slug(prefix)}_{suffix}"


def ensure_store(storage, home: Path, actor: str) -> dict[str, Any]:
    registry = home.expanduser().resolve(strict=False) / "registry.sqlite"
    if registry.is_file():
        stores = {item["store_name"] for item in storage.list_stores(home)}
    else:
        storage.initialize_home(home)
        stores = set()
    if "praxis_mine" not in stores:
        storage.create_store(home, "praxis_mine", "External praxis discovery and admission ledger", actor, "internal")
    health = storage.check_store(home, "praxis_mine")
    if health["contract_versions"] == 0:
        contract = read_json(SKILL_ROOT / "assets" / "praxis_mine.contract.json")
        storage.install_contract(home, "praxis_mine", contract, actor)
    return storage.check_store(home, "praxis_mine")


def find_record(storage, home: Path, record_type: str, key_field: str, key: str) -> dict[str, Any] | None:
    for record in storage.list_records(home, "praxis_mine", record_type, status=None):
        if record["payload"].get(key_field) == key:
            return record
    return None


def upsert(storage, home: Path, record_type: str, key_field: str, payload: dict[str, Any], actor: str, provenance: dict[str, Any], source_kind: str) -> tuple[dict[str, Any], str]:
    key = payload[key_field]
    existing = find_record(storage, home, record_type, key_field, key)
    if existing is None:
        record_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"cd:praxis-mine:{record_type}:{key}"))
        record = storage.add_record(home, "praxis_mine", record_type, payload, actor, source_kind, provenance, record_id=record_id)
        return record, "created"
    if canonical(existing["payload"]) == canonical(payload):
        return existing, "unchanged"
    record = storage.revise_record(home, "praxis_mine", existing["record_id"], payload, actor, source_kind, provenance, "source refresh")
    return record, "revised"


def normalize_source(source: dict[str, Any]) -> dict[str, Any]:
    required = {"source_key", "title", "kind", "locator", "access_posture"}
    missing = sorted(required - set(source))
    if missing:
        raise RuntimeError(f"source missing fields: {', '.join(missing)}")
    return {key: source[key] for key in ("source_key", "title", "kind", "locator", "access_posture", "cadence", "notes") if key in source}


def normalize_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    required = {"source_key", "title", "locator", "candidate_kind", "summary"}
    missing = sorted(required - set(candidate))
    if missing:
        raise RuntimeError(f"candidate missing fields: {', '.join(missing)}")
    result = dict(candidate)
    result["candidate_key"] = result.get("candidate_key") or stable_key(result["title"], result["locator"])
    result.setdefault("candidate_status", "triage")
    result.setdefault("evidence_state", "reported_unverified")
    allowed = {"candidate_key", "source_key", "title", "locator", "candidate_kind", "summary", "content_hash", "license", "candidate_status", "evidence_state", "tags"}
    return {key: result[key] for key in allowed if key in result}


def ingest_manifest(storage, home: Path, path: Path, actor: str) -> dict[str, Any]:
    manifest = read_json(path)
    if not isinstance(manifest, dict) or not isinstance(manifest.get("sources"), list) or not isinstance(manifest.get("candidates"), list):
        raise RuntimeError("manifest requires sources and candidates arrays")
    ensure_store(storage, home, actor)
    source_records: dict[str, dict[str, Any]] = {}
    counts = {"sources_created": 0, "sources_revised": 0, "sources_unchanged": 0, "candidates_created": 0, "candidates_revised": 0, "candidates_unchanged": 0}
    provenance = {"manifest": str(path.resolve()), "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    started = utc_now()
    for raw in manifest["sources"]:
        payload = normalize_source(raw)
        record, action = upsert(storage, home, "source", "source_key", payload, actor, provenance, "supplied")
        source_records[payload["source_key"]] = record
        counts[f"sources_{action}"] += 1
    for raw in manifest["candidates"]:
        payload = normalize_candidate(raw)
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


def directory_hash(root: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    count = 0
    for path in sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.as_posix().lower()):
        if any(part in IGNORE_PARTS for part in path.relative_to(root).parts):
            continue
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        try:
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
        except OSError:
            continue
        count += 1
    return digest.hexdigest(), count


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
    markers = {"SKILL.md", "pyproject.toml", "package.json"}
    roots = {path.parent for marker in markers for path in root.rglob(marker) if not any(part in IGNORE_PARTS for part in path.relative_to(root).parts)}
    if any((root / marker).is_file() for marker in markers):
        roots.add(root)
    return sorted(roots, key=lambda p: p.as_posix().lower())


def scan_local(storage, home: Path, root: Path, source_key: str, actor: str) -> dict[str, Any]:
    root = root.expanduser().resolve(strict=True)
    ensure_store(storage, home, actor)
    source_payload = {"source_key": source_key, "title": root.name or str(root), "kind": "local_directory", "locator": str(root), "access_posture": "read_only_local", "cadence": "manual", "notes": "Local metadata and content hashes only."}
    source, _ = upsert(storage, home, "source", "source_key", source_payload, actor, {"route": "local_scan"}, "observed")
    counts = {"created": 0, "revised": 0, "unchanged": 0}
    started = utc_now()
    for candidate_root in local_candidate_roots(root):
        title, summary = title_and_summary(candidate_root)
        digest, file_count = directory_hash(candidate_root)
        if (candidate_root / "SKILL.md").is_file():
            kind = "agent_skill"
        else:
            kind = "software_tool"
        license_files = sorted(candidate_root.glob("LICENSE*"))
        payload = normalize_candidate({"source_key": source_key, "title": title, "locator": str(candidate_root), "candidate_kind": kind, "summary": summary, "content_hash": digest, "license": license_files[0].name if license_files else "unknown", "candidate_status": "triage", "evidence_state": "locally_observed", "tags": {"file_count": file_count}})
        record, action = upsert(storage, home, "candidate", "candidate_key", payload, actor, {"root": str(root), "route": "local_scan"}, "observed")
        counts[action] += 1
        if action == "created":
            storage.add_relation(home, "praxis_mine", "source_contains_candidate", source["record_id"], record["record_id"], actor, {"route": "local_scan"})
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
    if max(risks[key] for key in ("security", "privacy", "license")) >= 4:
        return score, "reject"
    if risks["overlap"] >= 4:
        return score, "quarry" if positive["domain_judgment"] >= 3 or positive["evidence_quality"] >= 3 else "reject"
    if preferred in {"quarry", "adapt"} and score >= 45:
        return score, preferred
    if score >= 70:
        return score, "pilot"
    if score >= 45:
        return score, "monitor" if preferred == "reject" else preferred
    return score, "reject" if preferred == "reject" else "monitor"


def evaluate(storage, home: Path, candidate_key: str, evaluation_path: Path, actor: str) -> dict[str, Any]:
    ensure_store(storage, home, actor)
    candidate = find_record(storage, home, "candidate", "candidate_key", candidate_key)
    if candidate is None:
        raise RuntimeError(f"unknown candidate: {candidate_key}")
    supplied = read_json(evaluation_path)
    positive = validate_score_map(supplied.get("positive_scores"), POSITIVE_KEYS, "positive_scores")
    risks = validate_score_map(supplied.get("risk_scores"), RISK_KEYS, "risk_scores")
    preferred = supplied.get("preferred_disposition", "monitor")
    if preferred not in DISPOSITIONS:
        raise RuntimeError(f"preferred_disposition must be one of: {', '.join(sorted(DISPOSITIONS))}")
    for required in ("capability_delta", "evidence", "next_test"):
        if not supplied.get(required):
            raise RuntimeError(f"evaluation requires {required}")
    fingerprint = hashlib.sha256(canonical(supplied).encode("utf-8")).hexdigest()[:12]
    evaluation_key = f"{candidate_key}_{fingerprint}"
    existing_evaluation = find_record(storage, home, "evaluation", "evaluation_key", evaluation_key)
    score, disposition = decide(positive, risks, preferred)
    evaluated_at = existing_evaluation["payload"]["evaluated_at"] if existing_evaluation else utc_now()
    payload = {"evaluation_key": evaluation_key, "candidate_key": candidate_key, "evaluated_at": evaluated_at, "positive_scores": positive, "risk_scores": risks, "weighted_score": score, "capability_delta": supplied["capability_delta"], "evidence": supplied["evidence"], "disposition": disposition, "next_test": supplied["next_test"], "notes": supplied.get("notes", "")}
    provenance = {"evaluation_file": str(evaluation_path.resolve()), "evaluation_sha256": hashlib.sha256(evaluation_path.read_bytes()).hexdigest()}
    record, action = upsert(storage, home, "evaluation", "evaluation_key", payload, actor, provenance, "derived")
    if action == "created":
        storage.add_relation(home, "praxis_mine", "candidate_has_evaluation", candidate["record_id"], record["record_id"], actor, provenance)
    if candidate["payload"]["candidate_status"] != disposition:
        candidate_payload = dict(candidate["payload"])
        candidate_payload["candidate_status"] = disposition
        storage.revise_record(home, "praxis_mine", candidate["record_id"], candidate_payload, actor, "derived", provenance, "evaluation disposition")
    return {"candidate_key": candidate_key, "evaluation_key": payload["evaluation_key"], "weighted_score": score, "disposition": disposition, "action": action}


def report(storage, home: Path) -> str:
    ensure_store(storage, home, "praxis-mine")
    candidates = storage.list_records(home, "praxis_mine", "candidate", status=None)
    evaluations = storage.list_records(home, "praxis_mine", "evaluation", status=None)
    latest: dict[str, dict[str, Any]] = {}
    for item in evaluations:
        key = item["payload"]["candidate_key"]
        if key not in latest or item["payload"]["evaluated_at"] > latest[key]["evaluated_at"]:
            latest[key] = item["payload"]
    lines = ["# Praxis Mine report", "", f"Generated: {utc_now()}", "", f"Candidates: {len(candidates)} | Evaluations: {len(evaluations)}", ""]
    for record in sorted(candidates, key=lambda item: item["payload"]["title"].lower()):
        item = record["payload"]
        evaluation = latest.get(item["candidate_key"])
        disposition = evaluation["disposition"] if evaluation else item["candidate_status"]
        lines.extend([f"## {item['title']}", "", f"- Candidate: `{item['candidate_key']}`", f"- Kind: {item['candidate_kind']}", f"- Source: `{item['source_key']}`", f"- Locator: {item['locator']}", f"- Evidence state: {item['evidence_state']}", f"- Disposition: **{disposition}**", f"- Summary: {item['summary']}"])
        if evaluation:
            lines.extend([f"- Weighted priority score: {evaluation['weighted_score']}", f"- Capability delta: {evaluation['capability_delta']}", f"- Next test: {evaluation['next_test']}"])
        lines.append("")
    return "\n".join(lines)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Source-agnostic external praxis discovery and admission ledger")
    result.add_argument("--data-home", type=Path, help="CD Data Substrate home")
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
        storage = load_substrate()
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
            ensure_store(storage, home, args.actor)
            candidates = storage.list_records(home, "praxis_mine", "candidate", status=None)
            evaluations = storage.list_records(home, "praxis_mine", "evaluation", status=None)
            value = {"health": storage.check_store(home, "praxis_mine"), "candidates": len(candidates), "evaluations": len(evaluations), "awaiting_evaluation": sum(1 for item in candidates if item["payload"]["candidate_status"] == "triage")}
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

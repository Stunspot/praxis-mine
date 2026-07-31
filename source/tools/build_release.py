#!/usr/bin/env python3
"""Build the immutable Praxis Mine v1.0.0 customer release."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "1.0.0"
SLUG = "praxis-mine"
REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "source"
PLUGIN_SOURCE = SOURCE_ROOT / "plugin"
SKILL_SOURCE = PLUGIN_SOURCE / "skills" / SLUG
RELEASE_ROOT = REPO_ROOT / f"release-v{VERSION}"
ZIP_TIME = (2026, 7, 30, 12, 0, 0)


def release_files(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix.lower() not in {".pyc", ".pyo"}
    ]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def inventory(root: Path) -> list[dict[str, Any]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in release_files(root)
    ]


def write_json(path: Path, value: Any) -> None:
    path.write_text(canonical_json(value), encoding="utf-8", newline="\n")


def deterministic_zip(source: Path, destination: Path, top_level: str | None = None) -> dict[str, Any]:
    files = release_files(source)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(source).as_posix()
            member = f"{top_level}/{relative}" if top_level else relative
            info = zipfile.ZipInfo(member, date_time=ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    return {
        "file": destination.name,
        "sha256": sha256_file(destination),
        "bytes": destination.stat().st_size,
        "members": len(files),
    }


def copy_customer_docs(destination: Path, *, include_review: bool) -> list[str]:
    manifest_path = REPO_ROOT / "documentation-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    docs = manifest["customer_docs"]
    for relative in docs:
        source = REPO_ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    documentation_assets = REPO_ROOT / "docs" / "assets" / "brand"
    if documentation_assets.is_dir():
        shutil.copytree(
            documentation_assets,
            destination / "docs" / "assets" / "brand",
        )
    shutil.copy2(manifest_path, destination / "documentation-manifest.json")
    shutil.copy2(REPO_ROOT / "documentation-authorship.json", destination / "documentation-authorship.json")
    if include_review:
        shutil.copy2(REPO_ROOT / "documentation-review.json", destination / "documentation-review.json")
    return docs


def load_verifier():
    path = SOURCE_ROOT / "tools" / "verify_release.py"
    spec = importlib.util.spec_from_file_location("praxis_verify_release", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load release verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(*, staging: bool = False) -> int:
    global RELEASE_ROOT
    if staging:
        RELEASE_ROOT = REPO_ROOT / f".staging-v{VERSION}"
    if RELEASE_ROOT.exists():
        raise RuntimeError(f"release destination already exists: {RELEASE_ROOT}")
    RELEASE_ROOT.mkdir()

    plugin_target = RELEASE_ROOT / "codex" / SLUG
    shutil.copytree(
        PLUGIN_SOURCE,
        plugin_target,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    docs = copy_customer_docs(RELEASE_ROOT, include_review=not staging)
    shutil.copytree(REPO_ROOT / "assets", RELEASE_ROOT / "assets")
    tools_target = RELEASE_ROOT / "tools"
    tools_target.mkdir()
    shutil.copy2(SOURCE_ROOT / "tools" / "verify_release.py", tools_target / "verify_release.py")
    verification_target = RELEASE_ROOT / "verification"
    verification_target.mkdir()
    for name in ("verification-summary.json", "reviewer-attestation.json"):
        shutil.copy2(SOURCE_ROOT / "verification" / name, verification_target / name)

    claude_dir = RELEASE_ROOT / "claude"
    archives_dir = RELEASE_ROOT / "archives"
    claude_dir.mkdir()
    archives_dir.mkdir()

    claude_path = claude_dir / f"{SLUG}-v{VERSION}.zip"
    standalone_path = archives_dir / f"{SLUG}-skill-v{VERSION}.zip"
    plugin_path = archives_dir / f"{SLUG}-plugin-v{VERSION}.zip"
    claude_record = deterministic_zip(SKILL_SOURCE, claude_path, SLUG)
    standalone_record = deterministic_zip(SKILL_SOURCE, standalone_path, SLUG)
    plugin_record = deterministic_zip(PLUGIN_SOURCE, plugin_path, SLUG)

    archives = [
        {"kind": "claude-skill", "path": claude_path.relative_to(RELEASE_ROOT).as_posix(), **claude_record},
        {"kind": "standalone-skill", "path": standalone_path.relative_to(RELEASE_ROOT).as_posix(), **standalone_record},
        {"kind": "plugin", "path": plugin_path.relative_to(RELEASE_ROOT).as_posix(), **plugin_record},
    ]
    component_custody_records = [
        {
            "file": Path(record["path"]).name,
            "kind": record["kind"],
            "sha256": record["sha256"],
            "bytes": record["bytes"],
            "members": record["members"],
        }
        for record in archives
    ]
    write_json(
        RELEASE_ROOT / "component-custody.json",
        {
            "schema": "praxis-mine-component-custody/v1",
            "name": "Praxis Mine",
            "version": VERSION,
            "archives": component_custody_records,
        },
    )
    manifest = {
        "schema": "praxis-mine-release/v1",
        "name": "Praxis Mine",
        "slug": SLUG,
        "version": VERSION,
        "repository": "https://github.com/Stunspot/praxis-mine",
        "visibility": "PUBLIC_AUTHORIZED",
        "customer_object": f"Praxis-Mine-v{VERSION}.zip",
        "plugin_files": inventory(plugin_target),
        "skill_files": inventory(plugin_target / "skills" / SLUG),
        "customer_docs": docs,
        "archives": archives,
        "claim_boundary": "Static package, runtime integration, documentation, and archive evidence only; host activation, directory approval, and customer outcomes are separate.",
    }
    write_json(RELEASE_ROOT / "manifest.json", manifest)
    write_json(
        RELEASE_ROOT / "package-receipt.json",
        {
            "schema": "praxis-mine-package-receipt/v1",
            "name": "Praxis Mine",
            "version": VERSION,
            "status": "staging-candidate-built" if staging else "release-candidate-built",
            "customer_object": f"Praxis-Mine-v{VERSION}.zip",
            "host_components": [item["path"] for item in archives],
            "documentation_manifest": "documentation-manifest.json",
        },
    )

    verifier = load_verifier()
    component_report = verifier.verify(RELEASE_ROOT, require_complete=False)
    if not component_report["ok"]:
        raise RuntimeError(f"component verification failed: {component_report['findings']}")
    write_json(RELEASE_ROOT / "verification-report.json", component_report)

    kit_path = RELEASE_ROOT / f"Praxis-Mine-v{VERSION}.zip"
    kit_record = deterministic_zip(RELEASE_ROOT, kit_path)
    checksum_path = RELEASE_ROOT / f"Praxis-Mine-v{VERSION}.zip.sha256"
    checksum_path.write_text(f"{kit_record['sha256']}  {kit_path.name}\n", encoding="utf-8", newline="\n")

    custody_records = [
        {
            "file": kit_path.name,
            "kind": "complete-augment",
            "sha256": kit_record["sha256"],
            "bytes": kit_record["bytes"],
            "members": kit_record["members"],
        }
    ]
    custody_records.extend(component_custody_records)
    write_json(
        RELEASE_ROOT / "archive-custody.json",
        {
            "schema": "praxis-mine-archive-custody/v1",
            "name": "Praxis Mine",
            "version": VERSION,
            "archives": custody_records,
        },
    )
    write_json(
        RELEASE_ROOT / "receipt.json",
        {
            "schema": "praxis-mine-build-receipt/v1",
            "name": "Praxis Mine",
            "version": VERSION,
            "canonical_zip": kit_path.name,
            "canonical_zip_sha256": kit_record["sha256"],
            "canonical_zip_member_count": kit_record["members"],
            "status": "staging-candidate-built" if staging else "release-candidate-built",
            "built_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
    )

    final_report = verifier.verify(RELEASE_ROOT, require_complete=True)
    if not final_report["ok"]:
        raise RuntimeError(f"final verification failed: {final_report['findings']}")
    write_json(RELEASE_ROOT / "postbuild-verification-report.json", final_report)
    print(canonical_json({
        "ok": True,
        "release_root": str(RELEASE_ROOT),
        "customer_object": str(kit_path),
        "sha256": kit_record["sha256"],
        "archives": custody_records,
    }), end="")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] != "--staging"):
        raise SystemExit("usage: build_release.py [--staging]")
    raise SystemExit(main(staging=len(sys.argv) == 2))

#!/usr/bin/env python3
"""Run and retain the deterministic Praxis Mine v1.0.1 verification layer."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "source" / "plugin" / "skills" / "praxis-mine"
PLUGIN = ROOT / "source" / "plugin"
STAGING = ROOT / ".staging-v1.0.1"
RELEASE = ROOT / "release-v1.0.1"
TARGET = RELEASE if RELEASE.is_dir() else STAGING
EVIDENCE = ROOT / "source" / "verification" / "deterministic-run"
CODEX_ROOT = Path.home() / ".codex"
BUILDER = CODEX_ROOT / "skills" / "augment-skill-builder" / "scripts"
PLUGIN_CREATOR = CODEX_ROOT / "skills" / ".system" / "plugin-creator" / "scripts"
SKILL_CREATOR = CODEX_ROOT / "skills" / ".system" / "skill-creator" / "scripts"
HESPEROS = (
    CODEX_ROOT
    / "plugins"
    / "cache"
    / "personal"
    / "scribe-hesperos-clearpath"
    / "0.1.0"
    / "skills"
    / "hesperos-documentation"
    / "SKILL.md"
)


def run(name: str, command: list[str], cwd: Path) -> dict[str, object]:
    started = time.perf_counter()
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
        env=environment,
    )
    return {
        "name": name,
        "command": command,
        "cwd": str(cwd),
        "exit_code": completed.returncode,
        "duration_seconds": round(time.perf_counter() - started, 3),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def normalize_public_evidence(value: object, temporary_root: str) -> object:
    replacements = [
        (temporary_root, "<temporary-extracted-kit>"),
        (str(HESPEROS), "<hesperos-entrypoint>"),
        (str(BUILDER), "<augment-builder-scripts>"),
        (str(PLUGIN_CREATOR), "<plugin-validator-scripts>"),
        (str(SKILL_CREATOR), "<skill-validator-scripts>"),
        (str(ROOT), "<repository-root>"),
        (sys.executable, "python"),
    ]
    if isinstance(value, str):
        for source, replacement in replacements:
            value = value.replace(source, replacement)
        return value
    if isinstance(value, list):
        return [normalize_public_evidence(item, temporary_root) for item in value]
    if isinstance(value, dict):
        return {
            key: normalize_public_evidence(item, temporary_root)
            for key, item in value.items()
        }
    return value


def main() -> int:
    if not TARGET.is_dir():
        raise SystemExit("release or staging candidate is missing")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    checks = [
        run(
            "unit_and_integration_tests",
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            SKILL,
        ),
        run(
            "plugin_validator",
            [sys.executable, str(PLUGIN_CREATOR / "validate_plugin.py"), str(PLUGIN)],
            ROOT,
        ),
        run(
            "skill_validator",
            [sys.executable, str(SKILL_CREATOR / "quick_validate.py"), str(SKILL)],
            ROOT,
        ),
        run(
            "augment_bundle_profile",
            [
                sys.executable,
                str(BUILDER / "validate_augment_package.py"),
                str(PLUGIN),
                "--profile",
                "bundle",
                "--json",
            ],
            ROOT,
        ),
        run(
            "augment_codex_profile",
            [
                sys.executable,
                str(BUILDER / "validate_augment_package.py"),
                str(SKILL),
                "--profile",
                "codex",
                "--json",
            ],
            ROOT,
        ),
        run(
            "augment_claude_profile",
            [
                sys.executable,
                str(BUILDER / "validate_augment_package.py"),
                str(SKILL),
                "--profile",
                "claude",
                "--json",
            ],
            ROOT,
        ),
        run(
            "hesperos_authorship_receipt",
            [
                sys.executable,
                str(BUILDER / "hesperos_authorship.py"),
                "validate",
                "--root",
                str(ROOT),
                "--receipt",
                "documentation-authorship.json",
                "--capability-entrypoint",
                str(HESPEROS),
            ],
            ROOT,
        ),
        run(
            "documentation_structure_and_fingerprint",
            [
                sys.executable,
                str(BUILDER / "validate_customer_documentation.py"),
                str(ROOT),
                "--manifest",
                "documentation-manifest.json",
                "--fingerprint",
                "--json",
            ],
            ROOT,
        ),
        run(
            "outer_release_verifier",
            [sys.executable, str(TARGET / "tools" / "verify_release.py"), str(TARGET)],
            ROOT,
        ),
    ]

    kit = TARGET / "Praxis-Mine-v1.0.1.zip"
    with tempfile.TemporaryDirectory(prefix="praxis-mine-verify-") as temporary:
        extracted = Path(temporary)
        with zipfile.ZipFile(kit) as archive:
            archive.extractall(extracted)
        checks.append(
            run(
                "extracted_kit_component_verifier",
                [
                    sys.executable,
                    str(extracted / "tools" / "verify_release.py"),
                    str(extracted),
                    "--component-only",
                ],
                extracted,
            )
        )

    submission = (ROOT / "PLUGIN-DIRECTORY-SUBMISSION-v1.0.1.md").read_text(
        encoding="utf-8"
    )
    structural = {
        "name": "structural_release_assertions",
        "positive_submission_cases": submission.count("### Positive case "),
        "negative_submission_cases": submission.count("### Negative case "),
        "private_runtime_tokens": [
            token
            for token in ("CODEX_HOME", "CD_DATA_SUBSTRATE_ROOT", "Omnicompetence")
            if token
            in (SKILL / "scripts" / "praxis_mine.py").read_text(encoding="utf-8")
        ],
        "generated_cache_files_in_release": [
            path.relative_to(TARGET).as_posix()
            for path in TARGET.rglob("*")
            if path.is_file()
            and ("__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".pyo"})
        ],
    }
    structural["ok"] = (
        structural["positive_submission_cases"] == 5
        and structural["negative_submission_cases"] == 3
        and not structural["private_runtime_tokens"]
        and not structural["generated_cache_files_in_release"]
    )
    report = {
        "format": "praxis-mine-deterministic-verification-run/v1",
        "product": "praxis-mine",
        "version": "1.0.1",
        "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "checks": checks,
        "structural_assertions": structural,
        "evidence_normalization": "Absolute executable, workspace, skill-installation, and temporary paths are replaced with stable public placeholders after execution.",
    }
    report["ok"] = all(item["exit_code"] == 0 for item in checks) and structural["ok"]
    report = normalize_public_evidence(report, temporary)
    (EVIDENCE / "run.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "checks": [
                    {"name": item["name"], "exit_code": item["exit_code"]}
                    for item in checks
                ],
                "structural_assertions": structural,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

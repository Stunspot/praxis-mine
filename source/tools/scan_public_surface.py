#!/usr/bin/env python3
"""Scan Git history and nested ZIP payloads for obvious secret material."""

from __future__ import annotations

import io
import json
import re
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "source" / "verification" / "public-surface-scan.json"
PATTERNS = {
    "aws_access_key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "github_token": re.compile(rb"gh[pousr]_[A-Za-z0-9_]{20,}"),
    "openai_key": re.compile(rb"sk-[A-Za-z0-9_-]{20,}"),
    "private_key": re.compile(rb"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    "credential_assignment": re.compile(
        rb"(?i)(?:password|passwd|api[_-]?key|access[_-]?token)"
        rb"\s*[:=]\s*[\"']?[A-Za-z0-9_./+=:-]{12,}"
    ),
}
SENSITIVE_NAMES = re.compile(
    r"(?i)(?:^|/)(?:\.env(?:\..*)?|id_rsa|id_ed25519|credentials|secrets?)(?:$|\.)"
)


def git(*arguments: str) -> bytes:
    return subprocess.check_output(["git", *arguments], cwd=ROOT)


def scan_bytes(label: str, payload: bytes, findings: list[dict[str, str]], depth: int = 0) -> None:
    for name, pattern in PATTERNS.items():
        if pattern.search(payload):
            findings.append({"kind": name, "location": label})
    if depth >= 3 or not label.lower().endswith(".zip"):
        return
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                nested_label = f"{label}!/{info.filename}"
                if SENSITIVE_NAMES.search(info.filename):
                    findings.append({"kind": "sensitive_filename", "location": nested_label})
                scan_bytes(nested_label, archive.read(info), findings, depth + 1)
    except zipfile.BadZipFile:
        findings.append({"kind": "invalid_zip", "location": label})


def main() -> int:
    findings: list[dict[str, str]] = []
    commits = git("rev-list", "--all").decode("ascii").split()
    objects_scanned = 0
    for commit in commits:
        paths = git("ls-tree", "-r", "--name-only", commit).decode("utf-8").splitlines()
        for path in paths:
            objects_scanned += 1
            if SENSITIVE_NAMES.search(path):
                findings.append({"kind": "sensitive_filename", "location": f"{commit}:{path}"})
            scan_bytes(f"{commit}:{path}", git("show", f"{commit}:{path}"), findings)
    worktree_paths = git(
        "ls-files", "--cached", "--others", "--exclude-standard"
    ).decode("utf-8").splitlines()
    for relative in worktree_paths:
        path = ROOT / relative
        if not path.is_file():
            continue
        if SENSITIVE_NAMES.search(relative):
            findings.append({"kind": "sensitive_filename", "location": f"worktree:{relative}"})
        scan_bytes(f"worktree:{relative}", path.read_bytes(), findings)
    report = {
        "format": "praxis-mine-public-surface-scan/v1",
        "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "commits_scanned": len(commits),
        "git_objects_scanned": objects_scanned,
        "worktree_files_scanned": len(worktree_paths),
        "nested_zip_depth": 3,
        "finding_count": len(findings),
        "findings": findings,
        "claim_boundary": "Pattern scan for common credential forms and sensitive filenames; not a proof that no secret or private data exists.",
    }
    OUTPUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run Hesperos Markdown lint across the declared customer corpus."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LINTER = (
    Path.home()
    / ".codex"
    / "plugins"
    / "cache"
    / "personal"
    / "scribe-hesperos-clearpath"
    / "0.1.0"
    / "skills"
    / "hesperos-documentation"
    / "scripts"
    / "lint_accessible_markdown.py"
)
OUTPUT = ROOT / "source" / "verification" / "hesperos-lint.json"
ACCEPTED_LICENSE_FINDING = "13: directional reference may not survive reflow"
STANDARD_LICENSE_LINE = (
    "The above copyright notice and this permission notice shall be included "
    "in all copies or substantial portions of the Software."
)


def main() -> int:
    manifest = json.loads(
        (ROOT / "documentation-manifest.json").read_text(encoding="utf-8")
    )
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    results = []
    blocking = []
    for relative in manifest["customer_docs"]:
        completed = subprocess.run(
            [sys.executable, str(LINTER), relative],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
            env=environment,
        )
        output = completed.stdout.strip()
        accepted = (
            relative == "LICENSE.md"
            and completed.returncode == 1
            and output == ACCEPTED_LICENSE_FINDING
            and (ROOT / relative).read_text(encoding="utf-8").splitlines()[12]
            == STANDARD_LICENSE_LINE
        )
        result = {
            "path": relative,
            "exit_code": completed.returncode,
            "output": output,
            "stderr": completed.stderr,
            "accepted_heuristic_false_positive": accepted,
        }
        results.append(result)
        if completed.returncode != 0 and not accepted:
            blocking.append(result)
    report = {
        "format": "praxis-mine-hesperos-markdown-lint/v1",
        "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "declared_documents": len(results),
        "passed": sum(item["exit_code"] == 0 for item in results),
        "accepted_heuristic_false_positives": sum(
            item["accepted_heuristic_false_positive"] for item in results
        ),
        "blocking_findings": len(blocking),
        "results": results,
    }
    report["ok"] = not blocking
    OUTPUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

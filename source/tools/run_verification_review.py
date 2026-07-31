#!/usr/bin/env python3
"""Run and retain a fresh independent verification review via local Ollama."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / ".staging-v1.0.0"
EVIDENCE = ROOT / "source" / "verification" / "verification-review"
REQUEST = ROOT / "source" / "verification" / "verification-review-request.md"
MODEL = "qwen35:latest"
ENDPOINT = "http://127.0.0.1:11434/api/generate"
INPUTS = [
    "source/design-record/positive-product-contract.md",
    "source/design-record/praxis-mine-augment-map.md",
    "source/plugin/.codex-plugin/plugin.json",
    "source/plugin/skills/praxis-mine/SKILL.md",
    "source/plugin/skills/praxis-mine/tests/test_praxis_mine.py",
    "source/tools/build_release.py",
    "source/tools/verify_release.py",
    "source/verification/deterministic-run/run.json",
    "source/verification/documentation-review-final-7/review-response.md",
    "documentation-authorship.json",
    "documentation-review.json",
    "PLUGIN-DIRECTORY-SUBMISSION-v1.0.0.md",
]
STAGING_INPUTS = [
    "manifest.json",
    "component-custody.json",
    "archive-custody.json",
    "postbuild-verification-report.json",
]


def main() -> int:
    sections = [REQUEST.read_text(encoding="utf-8")]
    for relative in INPUTS:
        path = ROOT / relative
        sections.extend(
            [
                f"\n\n===== BEGIN EVIDENCE: {relative} =====\n",
                path.read_text(encoding="utf-8"),
                f"\n===== END EVIDENCE: {relative} =====\n",
            ]
        )
    for relative in STAGING_INPUTS:
        path = STAGING / relative
        sections.extend(
            [
                f"\n\n===== BEGIN STAGING EVIDENCE: {relative} =====\n",
                path.read_text(encoding="utf-8"),
                f"\n===== END STAGING EVIDENCE: {relative} =====\n",
            ]
        )
    prompt = "".join(sections)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "assembled-review-input.md").write_text(
        prompt, encoding="utf-8", newline="\n"
    )
    request_payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "keep_alive": "10m",
        "options": {"num_ctx": 32768, "num_predict": 2048},
    }
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(request_payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=900) as response:
            response_body = response.read()
    except urllib.error.HTTPError as error:
        error_body = error.read()
        (EVIDENCE / "http-error.json").write_bytes(error_body)
        raise
    api_response = json.loads(response_body.decode("utf-8"))
    review_response = str(api_response.get("response", ""))
    (EVIDENCE / "api-response.json").write_bytes(response_body)
    (EVIDENCE / "review-response.md").write_text(
        review_response, encoding="utf-8", newline="\n"
    )
    (EVIDENCE / "run.json").write_text(
        json.dumps(
            {
                "format": "praxis-mine-verification-review-run/v1",
                "model": MODEL,
                "endpoint": ENDPOINT,
                "request": {
                    "model": MODEL,
                    "stream": False,
                    "think": False,
                    "keep_alive": "10m",
                    "options": {"num_ctx": 32768, "num_predict": 2048},
                },
                "http_status": 200,
                "completed_at": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
                "inputs": INPUTS,
                "staging_inputs": STAGING_INPUTS,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(review_response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

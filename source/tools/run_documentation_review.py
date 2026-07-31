#!/usr/bin/env python3
"""Run a fresh local-model documentation review and retain exact evidence."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUEST = ROOT / "source" / "verification" / "documentation-review-request.md"
MANIFEST = ROOT / "documentation-manifest.json"
EVIDENCE = ROOT / "source" / "verification" / "documentation-review-final-8"
MODEL = "gpt-oss:20b"
OLLAMA_GENERATE = "http://127.0.0.1:11434/api/generate"


def fingerprint(paths: list[str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(paths):
        data = (ROOT / relative).read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(data).digest())
    return digest.hexdigest()


def main() -> int:
    corpus_root = ROOT
    manifest_path = MANIFEST
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    paths = manifest["customer_docs"]
    current_fingerprint = fingerprint(paths)
    sections = [
        REQUEST.read_text(encoding="utf-8"),
        f"\nDOCUMENTATION_FINGERPRINT_INPUT: {current_fingerprint}\n",
        "\nDOCUMENTATION_MANIFEST:\n",
        manifest_path.read_text(encoding="utf-8"),
    ]
    for relative in paths:
        sections.extend([
            f"\n\n===== BEGIN DOCUMENT: {relative} =====\n",
            (corpus_root / relative).read_text(encoding="utf-8"),
            f"\n===== END DOCUMENT: {relative} =====\n",
        ])
    prompt = "".join(sections)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "assembled-review-input.md").write_text(prompt, encoding="utf-8", newline="\n")
    request_body = json.dumps(
        {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "think": "medium",
            "keep_alive": "10m",
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_GENERATE,
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        response_body = response.read()
    api_response = json.loads(response_body.decode("utf-8"))
    review_response = str(api_response.get("response", ""))
    (EVIDENCE / "api-response.json").write_bytes(response_body)
    (EVIDENCE / "review-response.md").write_text(
        review_response, encoding="utf-8", newline="\n"
    )
    run = {
        "format": "praxis-mine-documentation-review-run/v1",
        "model": MODEL,
        "endpoint": OLLAMA_GENERATE,
        "request": {"model": MODEL, "stream": False, "think": "medium", "keep_alive": "10m"},
        "started_and_completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "http_status": 200,
        "documentation_fingerprint": current_fingerprint,
        "customer_docs": paths,
        "release_candidate_root": None,
    }
    input_evidence = {
        "format": "cd-documentation-review-input/v1",
        "review_run_id": "praxis-mine-hesperos-pages-final-8",
        "contents_supplied": True,
        "documentation_fingerprint": current_fingerprint,
        "supplied_files": paths,
        "transport": (
            "Local Ollama fresh-context UTF-8 API with the exact current "
            "customer-document corpus"
        ),
        "review_response_evidence": (
            "source/verification/documentation-review-final-8/review-response.md"
        ),
        "execution_evidence": [
            "source/verification/documentation-review-request.md",
            "source/verification/documentation-review-final-8/assembled-review-input.md",
            "source/verification/documentation-review-final-8/api-response.json",
            "source/verification/documentation-review-final-8/run.json",
            "source/verification/documentation-review-final-8/review-response.md",
        ],
    }
    (EVIDENCE / "run.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (EVIDENCE / "review-input-evidence.json").write_text(
        json.dumps(input_evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(review_response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

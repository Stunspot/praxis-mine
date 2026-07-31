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
EVIDENCE = ROOT / "source" / "verification" / "documentation-review-final-7"
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
    release_root = ROOT / ".staging-v1.0.0"
    corpus_root = release_root if release_root.is_dir() else ROOT
    manifest_path = corpus_root / "documentation-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    paths = manifest["customer_docs"]
    current_fingerprint = fingerprint(paths)
    sections = [
        REQUEST.read_text(encoding="utf-8"),
        f"\nDOCUMENTATION_FINGERPRINT_INPUT: {current_fingerprint}\n",
        "\nDOCUMENTATION_MANIFEST:\n",
        manifest_path.read_text(encoding="utf-8"),
    ]
    if release_root.is_dir():
        inventory = [
            path.relative_to(release_root).as_posix()
            for path in sorted(release_root.rglob("*"))
            if path.is_file()
        ]
        sections.extend([
            "\n\nRELEASE_CANDIDATE_ROOT: extracted complete-kit staging root\n",
            "RELEASE_CANDIDATE_INVENTORY:\n",
            "\n".join(inventory),
            "\n\nARCHIVE_CUSTODY:\n",
            (release_root / "archive-custody.json").read_text(encoding="utf-8"),
        ])
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
        "release_candidate_root": ".staging-v1.0.0" if release_root.is_dir() else None,
    }
    (EVIDENCE / "run.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(review_response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Troubleshoot Praxis Mine

Begin with the observed symptom. Preserve the error, version, selected path, and command before reinstalling or deleting anything.

## The release verifier fails

1. Confirm you are running `python tools/verify_release.py . --component-only` from the extracted complete-kit root.
2. Compare the kit's SHA-256 with the detached checksum.
3. If the digest differs, download the release again. Do not repair the archive by recompressing it.
4. If the digest matches but verification fails, preserve the findings and file an issue with the release version and operating system.

Do not continue to installation when archive paths, manifests, hashes, or runtime files fail verification.

## The plugin installs but Praxis Mine is not discoverable

1. Confirm the installed plugin root contains `.codex-plugin/plugin.json`.
2. Confirm the manifest version is `1.0.1` and `skills` points to `./skills/`.
3. Start a fresh task or chat after the host reloads plugins.
4. Invoke **Praxis Mine** by name once:

   > Use Praxis Mine to assess this outside skill.

5. If another copy exists, identify its path and version before disabling or removing it.

A copied folder is not evidence that the host discovered it. Preserve the host's plugin listing or error.

## Claude rejects the Skill ZIP

1. Use `claude/praxis-mine-v1.0.1.zip` unchanged.
2. Confirm its digest matches the detached `archive-custody.json` release asset.
3. Confirm the current Claude product and workspace expose custom Skills.
4. Upload the fresh official ZIP.

If the digest matches and the host still rejects it, preserve the exact host message. Recompression changes the reviewed bytes and is not an evidence-preserving fix.

## Python is not found

Install or select Python 3.11 or newer, then reopen the terminal and run:

```text
python --version
```

If the host uses `python3` instead of `python`, substitute that command consistently. Do not install unrelated packages; Praxis Mine uses the standard library.

## The ledger cannot create its data home

1. Note the selected path and error.
2. Choose an existing directory where the active process has write permission:

   ```powershell
   python scripts\praxis_mine.py --data-home C:\path\you\control\praxis-data init
   ```

3. Confirm the command reports `"healthy": true`.

A host grant, operating-system permission, and actual process identity all affect file writes. Do not weaken system security or broadly grant a shell merely to satisfy the default path.

## A repeated ingest creates unexpected revisions

Compare the manifest bytes, normalized fields, file paths, and content hashes. The same semantic idea in different JSON or at a different path may carry different provenance. Revisions are expected when a record's normalized payload changes.

## A report path already exists

Praxis Mine refuses to overwrite reports. Choose a new filename:

```text
python scripts/praxis_mine.py --data-home .\praxis-data report --output .\praxis-report-2.md
```

Delete or replace an old report only after deciding it is no longer needed. The ledger remains the durable source.

## An evaluation returns a weaker disposition than expected

Inspect the missing evidence and the highest security, privacy, license, cost-dependency, and overlap scores. Severe unresolved risk constrains the automatic result. High overlap favors `quarry` or `reject`.

Do not tune scores to obtain a preferred label. Improve the evidence, narrow the candidate, or design a safer test.

## Escalate with useful evidence

Follow [Support](https://github.com/Stunspot/praxis-mine/blob/main/SUPPORT.md). Include the exact boundary, version, host, command or prompt, expected result, observed result, and validator output. Remove secrets and unrelated private data.

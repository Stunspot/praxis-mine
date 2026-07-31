# Praxis Mine validation

Validation is evidence about declared boundaries. It is not a magic certificate for every host, candidate, or future use.

## Verify the complete kit

From the extracted `Praxis-Mine-v1.0.0.zip` root:

```text
python tools/verify_release.py . --component-only
```

Require exit code `0`, `"ok": true`, and an empty findings list.

The release verifier checks:

- plugin manifest identity, version, paths, metadata limits, legal URLs, and declared assets;
- skill metadata and required runtime files;
- absence of private harness and workstation-path dependencies;
- JSON parsing and seed/evaluation structure;
- Claude and standalone skill archive roots, path safety, and byte parity;
- plugin archive root, path safety, and byte parity;
- documentation inventory and relative links;
- archive digests recorded in the release manifest and internal
  `component-custody.json`.

## Run the integration tests

From `codex/praxis-mine/skills/praxis-mine/`:

```text
python -m unittest discover -s tests -v
```

The tests use a temporary data home. They exercise initialization, seed ingestion, idempotence, evaluation, report creation, status, local scanning, and self-contained store loading.

## Verify release assets

Download `Praxis-Mine-v1.0.0.zip.sha256` or `archive-custody.json` beside the
complete kit, then compare the detached value with a local SHA-256 calculation.
On PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 .\Praxis-Mine-v1.0.0.zip
Get-Content .\Praxis-Mine-v1.0.0.zip.sha256
```

The external `archive-custody.json` records the complete kit, plugin archive,
standalone skill archive, and Claude archive digests. It is deliberately not
inside the kit whose hash it records. A public GitHub release is verified only
after the exposed assets are read back and match those values.

## Documentation evidence

`documentation-manifest.json` identifies the exact customer corpus and reader moments. `documentation-authorship.json` binds the current bytes to the Hesperos pass. `documentation-review.json` records the separate fresh-context reviewer disposition. Structural Markdown lint and link checks remain narrower than assistive-technology or representative-user testing.

## What the recorded evidence does not prove

- every Codex, ChatGPT, or Claude account can install custom plugins or Skills;
- natural-language routing is reliable across models and hosts;
- any candidate is safe, licensed, maintained, or fit for adoption;
- legal, privacy, security, accessibility, or policy compliance;
- OpenAI Plugins Directory approval or public directory discoverability;
- customer outcomes.

See [Host compatibility](HOST-COMPATIBILITY.md) and [Limitations](LIMITATIONS.md).

# Praxis Mine validation

Validation is evidence about declared boundaries. It is not a magic certificate for every host, candidate, or future use.

## Verify the complete kit

From the extracted **Praxis Mine v1.2.0.zip** root:

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

## Product delivery and integrity

The supplied product is one complete ZIP with its artwork, installation prompt, and Extra companion. Host archives are components inside that ZIP, not separate product downloads. The included verifier checks their filenames, contents, and hashes after extraction.

The governed release shelf retains the complete bundle’s SHA-256 and fingerprint. A detached checksum may be supplied for an independent whole-ZIP check, but it is not required as an extra shelf artifact and the installation path does not depend on a GitHub release. A checksum for the complete ZIP is kept outside that ZIP to avoid self-reference.

## Documentation evidence

`documentation-manifest.json` identifies the exact customer corpus and reader moments. `documentation-authorship.json` binds the current bytes to the Hesperos pass. `documentation-review.json` records the separate fresh-context reviewer disposition. Structural Markdown lint and link checks remain narrower than assistive-technology or representative-user testing.

## Visual workspace evidence

The current Windows workspace was checked in both themes at desktop, ultrawide, and narrow phone widths. Reader navigation, comparison, original activity dates, registered sources without findings, and findings without native evaluations were exercised. These observations cover the local implementation; they do not establish native macOS execution, fresh-customer host activation, screen-reader efficacy, or formal accessibility conformance. The packaged verification records retain the scope of each check.

## What the recorded evidence does not prove

- every Codex, ChatGPT, or Claude account can install custom plugins or Skills;
- natural-language routing is reliable across models and hosts;
- any candidate is safe, licensed, maintained, or fit for adoption;
- legal, privacy, security, accessibility, or policy compliance;
- OpenAI Plugins Directory approval or public directory discoverability;
- customer outcomes.

See [Host compatibility](HOST-COMPATIBILITY.md) and [Limitations](LIMITATIONS.md).

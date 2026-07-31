# Maintain and release Praxis Mine

Build each release into a new versioned directory. Preserve prior tags, archives, receipts, and release trees; do not mutate released bytes.

## Source of truth

The paths in this section belong to a checkout of the public
[`Stunspot/praxis-mine`](https://github.com/Stunspot/praxis-mine) repository;
they are not promised inside the extracted customer kit.

- `source/plugin/`: canonical installable plugin source;
- `source/design-record/`: positive product contract and approved Augment map;
- `docs/` plus root responsibility files: current customer corpus;
- `source/tools/`: deterministic release assembly and verification;
- `documentation-manifest.json`: exact customer-document inventory;
- `source/verification/`: TestForge and Hesperos evidence.

The generated `release-v1.0.0/` directory is a release artifact, not the preferred authoring surface.

## Change classification

Reopen the relevant evidence when a change affects:

- `SKILL.md`, model-visible descriptions, starter prompts, or host routing;
- dispositions, scoring, contracts, persistence, or CLI behavior;
- dependencies, permissions, filesystem, network, privacy, or security;
- plugin paths, images, metadata, legal URLs, or archive topology;
- installation, first value, recovery, support, provenance, or public claims.

Pure typo corrections still change documentation fingerprints and require current authorship/review receipts for a done-done release.

## Narrow verification

Run from the source skill root:

```text
python -m unittest discover -s tests -v
```

Validate the plugin:

Run the current official plugin validator against `source/plugin/` from the
maintainer's development environment. Record the validator version, command,
exit status, and findings in the verification evidence; do not publish a
workstation-specific validator path.

Validate the skill and Augment package through the installed Builder scripts. Record tool version and exact command in the verification manifest.

## Documentation pass

Give Hesperos the current product map, plugin and host artifacts, representative workflows, executed checks, limitations, privacy and security posture, support route, provenance, and intended readiness claim. Preserve:

- `documentation-manifest.json`;
- `source/verification/documentation-evidence-packet.md`;
- `source/verification/assets/documentation-authorship-response.md`;
- `documentation-authorship.json`;
- separate fresh-context reviewer evidence and `documentation-review.json`.

Any customer-document change makes the prior fingerprint stale.

## Assemble and verify

Run the release builder only against a clean, version-consistent source:

```text
python source/tools/build_release.py
```

Then run:

```text
python release-v1.0.0/tools/verify_release.py release-v1.0.0
```

The builder must fail rather than overwrite an existing versioned release. Inspect the actual customer kit, plugin ZIP, Claude ZIP, and standalone skill ZIP after extraction.

## Public launch

Before push, require a clean Git status except for the intended release change, passing TestForge and Hesperos dispositions, current hashes, and an explicit public-visibility authority record. Commit and tag the exact release tree. Push main and tag. Create the GitHub release from the canonical local assets, then read back repository visibility, main and tag commits, release notes, asset names, sizes, and digests.

OpenAI Plugins Directory submission is a later external state machine: draft, submitted, approved, publisher-released, and discoverable are distinct. The accountable publisher owns verified identity, organization selection, availability, and policy attestations.

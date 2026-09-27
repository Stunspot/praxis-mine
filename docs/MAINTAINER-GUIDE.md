# Maintain and release Praxis Mine

Build each release into a new versioned directory. Preserve prior tags, archives, receipts, and release trees; do not mutate released bytes.

## Source of truth

The paths in this section belong to a checkout of the public
[`Stunspot/praxis-mine`](https://github.com/Stunspot/praxis-mine) repository;
they are not promised inside the extracted customer kit.

- `source/plugin/`: canonical installable plugin source;
- `source/design-record/`: positive product contract and approved Augment map;
- `docs/` plus root responsibility files: current customer corpus and Pages source;
- `source/tools/`: deterministic release assembly and verification;
- `documentation-manifest.json`: exact customer-document inventory;
- `source/verification/`: TestForge and Hesperos evidence.

The generated `release-v1.2.0/` directory is a release artifact, not the preferred authoring surface.

## Change classification

Reopen the relevant evidence when a change affects:

- `SKILL.md`, model-visible descriptions, starter prompts, or host routing;
- dispositions, scoring, contracts, persistence, or CLI behavior;
- dependencies, permissions, filesystem, network, privacy, or security;
- plugin paths, images, metadata, legal URLs, or archive topology;
- installation, first value, recovery, support, provenance, or public claims.

Pure typo corrections still change documentation fingerprints and require current authorship/review receipts for a done-done release.

## Public documentation surfaces

Keep the three brand images compositionally and dimensionally distinct:

- `docs/assets/brand/praxis-mine-readme-hero.png`: `2244 × 701`, panoramic product identity and mining metaphor;
- `docs/assets/brand/praxis-mine-pages-hero.png`: `1200 × 800`, text-free human assay-workshop scene;
- `docs/assets/brand/praxis-mine-social-card.jpg`: `1200 × 630`, specimen-table Open Graph card with the exact product title and identifying line.

The three source-controlled compositions have different jobs, aspect ratios, and visual structures. Replace them only through a new approved visual-authorship pass; do not synthesize presentation artwork from programmed graphic primitives. Open and inspect every final raster after sizing. Dimensions and filenames alone are not acceptance evidence. The square image under `assets/` remains the plugin icon, not a README banner.

GitHub Pages is built from `docs/`. Check the live home page, responsive navigation, internal routes, image loading, keyboard focus, Open Graph metadata, and the repository social preview after publication. A successful local render does not establish a successful Pages deployment.

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
python release-v1.2.0/tools/verify_release.py release-v1.2.0
```

The builder must fail rather than overwrite an existing versioned release. For a same-version correction, use `python source/tools/build_release.py --repair-candidate` to create a new timestamped candidate while preserving the prior release bytes. Classify the correction and approve its exact final bundle before replacing the shelf bundle. Inspect the actual customer kit, plugin ZIP, Claude ZIP, and standalone skill ZIP after extraction.

## Governed product release

Read the owner’s current shelf contract before execution. A release updates the complete product bundle: the installable ZIP, product artwork, installation prompt, and Extra companion. Preserve its assigned shelf and distribution channel. Record the baseline, customer-visible delta, edit/update decision, and reason before packaging; bind the final bundle fingerprint through the shelf’s release-decision gate.

Reconcile the complete bundle, shelf/catalog manifest, sidecar source record, and applicable installed copy. Keep superseded bytes and engineering recovery material in private historical custody. Generate current upload status from actual deployed fingerprints; a prepared shelf bundle does not establish that anyone uploaded it to Discord or a storefront.

Updating an existing source repository is separate from publishing a GitHub release or opening another distribution route. A request for a release ZIP does not authorize those publication actions. Perform them only when explicitly requested. Marketplace submission and announcements likewise require their own authority.

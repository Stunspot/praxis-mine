# Maintain and release Praxis Mine

Build into a new candidate directory and verify that exact output. Preserve prior tags, archives, receipts and release trees. A same-version correction gets new candidate custody before replacing an accepted delivery.

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

The `release-v1.2.0/` directory is retained historical output. Do not rebuild it, use it as current source, or verify it as evidence for a newly built candidate.

## Change classification

Reopen the relevant evidence when a change affects:

- `SKILL.md`, model-visible descriptions, starter prompts, or host routing;
- dispositions, scoring, contracts, persistence, or CLI behavior;
- dependencies, permissions, filesystem, network, privacy, or security;
- plugin paths, images, metadata, legal URLs, or archive topology;
- installation, first value, recovery, support, provenance, or public claims.

Even a typo changes the documentation fingerprint. Bind the exact changed documents and record the review appropriate to the change. Preserve unchanged authorship; use a byte-custody continuation for line-ending-only corrections rather than claiming a new authoring run.

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

Give Hesperos the current product behavior, host artifacts, useful workflows, executed checks, limitations and intended claim. The root `documentation-manifest.json` declares the full customer corpus. A material revision uses a separate manifest containing only the changed documents and retains its evidence packet, authoring response and execution record under a new verification folder. The current `documentation-authorship.json` binds that exact run; `documentation-custody.json` retains unchanged earlier authorship and explicit byte-only amendments. Keep earlier receipts and independent review as historical evidence, with their own cutoff.

## Assemble and verify the current candidate

Run these commands from the repository root. Replace `NEW-NAME` with a new candidate name; the output directory must not exist. Check version consistency and record the edit/update decision before building. Unrelated working changes do not become part of the approved scope merely because they share the checkout.

```text
python -B source/tools/build_release.py --output-dir repair-candidates/NEW-NAME
python -B repair-candidates/NEW-NAME/package/tools/verify_release.py repair-candidates/NEW-NAME/package --component-only
```

The builder creates an inspectable `package/` directory, `Praxis-Mine-v1.2.1.zip`, a detached checksum and the three delivery companions beside it. It checks linked sources, portable archive paths, current documentation custody inputs and preserved artwork. It refuses to overwrite an existing candidate. Historical reviewer verdicts remain outside the new kit.

Verify the ZIP itself after native extraction into another new directory. On Windows, from the same repository root:

```powershell
Expand-Archive -LiteralPath 'repair-candidates/NEW-NAME/Praxis-Mine-v1.2.1.zip' -DestinationPath 'repair-candidates/NEW-NAME/native-check'
python -B repair-candidates/NEW-NAME/native-check/tools/verify_release.py repair-candidates/NEW-NAME/native-check --component-only
```

Use the candidate ZIP name for the version being built. These commands inspect the new output and its embedded plugin, Claude and standalone skill archives. `--component-only` verifies the extracted customer kit; it does not require an outer ZIP inside its own extraction. Compare the extracted source bytes with the intended current source, and run the checks that could change acceptance of this delta. For runtime changes, use the extracted skill at `native-check/codex/praxis-mine/skills/praxis-mine/` for relevant tests and user journeys. A successful package check establishes file and archive consistency, not model behavior or host activation.

Never substitute `release-v1.2.0/` or another previous candidate for these paths. Record the exact new ZIP hash and evidence cutoff before governed delivery. Keep superseded releases intact.

## Governed product release

Read the owner’s current shelf contract before execution. A release updates the complete product bundle: the installable ZIP, product artwork, installation prompt, and Extra companion. Preserve its assigned shelf and distribution channel. Record the baseline, customer-visible delta, edit/update decision, and reason before packaging; bind the final bundle fingerprint through the shelf’s release-decision gate.

Reconcile the complete bundle, shelf/catalog manifest, sidecar source record, and applicable installed copy. Keep superseded bytes and engineering recovery material in private historical custody. Generate current upload status from actual deployed fingerprints; a prepared shelf bundle does not establish that anyone uploaded it to Discord or a storefront.

Updating an existing source repository is separate from publishing a GitHub release or opening another distribution route. A request for a release ZIP does not authorize those publication actions. Perform them only when explicitly requested. Marketplace submission and announcements likewise require their own authority.

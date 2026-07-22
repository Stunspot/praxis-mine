# Praxis Mine: maintainer guide

Promote only from a selected-source ledger that passes source, profile, and description validation. Build into a new empty versioned output; never mutate a previous release or backup artifact.

## Required custody inputs

- `source-selection.json`
- `description-registry.json`
- `verification/draft-stable-content-profiles-2026-07-21.json`
- `verification/settled-family-release-plan-2026-07-21.json`
- `tools/build_settled_family_releases.py`
- `tools/verify_settled_family_releases.py`

## Rebuild procedure

1. Confirm the plan names `praxis-mine` version `0.1.0` and the intended repository, visibility, handles, descriptions, starter prompt, and backup filename.
2. Confirm every selected source still matches its profile and lies outside excluded active-development roots.
3. From the reconciliation repository, choose a new empty output directory and run:

   ```powershell
   $releaseOutput = Join-Path $PWD 'settled-family-release-candidate'
   python -B tools/build_settled_family_releases.py --plan verification/settled-family-release-plan-2026-07-21.json --source-selection source-selection.json --description-registry description-registry.json --profiles verification/draft-stable-content-profiles-2026-07-21.json --output-root $releaseOutput
   ```

4. Verify the complete estate candidate:

   ```powershell
   python -B tools/verify_settled_family_releases.py --plan verification/settled-family-release-plan-2026-07-21.json --source-selection source-selection.json --description-registry description-registry.json --release-root $releaseOutput
   ```

5. Run the official Codex plugin validator against `families/praxis-mine/v0.1.0/codex/praxis-mine/`.
6. Run the installed documentation accessibility linter across `families/praxis-mine/v0.1.0/docs/`.
7. Require an independent review of archive safety, byte parity, description custody, and customer working paths.
8. Promote to the [custody repository](https://github.com/Stunspot/praxis-mine) only after every gate passes. Re-clone the remote and compare hashes before crediting GitHub custody.

## Family maintenance responsibilities

## praxis-mine

- Data Substrate and ledger commands
- evaluation-gate/source-adapter references
- source/rights/dependency/security/context-cost record requirements
- idempotent stable-key behavior

## Evidence pointers

- [manifest.json](../manifest.json): included source-file hashes and Claude archive receipts.
- [verification-report.json](../verification-report.json): portable post-build verification.
- [description-custody.json](../description-custody.json): exact model-visible and UI-short prompt surfaces.
- [package-receipt.json](../package-receipt.json): family, version, and static claim boundary inside the canonical archive.
- Estate staging root `validation.json`: all-family build receipt.
- Detached `receipt.json` and `Praxis-Mine-v0.1.0.zip.sha256`: canonical and backup archive custody.

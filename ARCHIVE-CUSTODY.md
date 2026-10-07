# Praxis Mine archive custody

Praxis Mine is one product with several independently useful distribution objects.

## Version 1.0.0 archive set

- `Praxis-Mine-v1.0.0.zip`: complete customer kit with plugin, Claude upload, standalone archive, documentation, validation, and package evidence;
- `praxis-mine-plugin-v1.0.0.zip`: installable skills-only Codex/ChatGPT plugin;
- `praxis-mine-skill-v1.0.0.zip`: standalone self-contained skill;
- `praxis-mine-v1.0.0.zip`: Claude custom-Skill upload.

`release-v1.0.0/archive-custody.json` records each archive's SHA-256, byte size, member count, version, and role. `Praxis-Mine-v1.0.0.zip.sha256` is the detached checksum for the complete kit.

The same logical skill appears in the plugin, standalone archive, and Claude archive. Release verification compares their files to the canonical `source/plugin/skills/praxis-mine/` tree. The complete kit is the customer handoff; host archives are components, not separate products.

GitHub release assets must match the local custody ledger exactly. A successful upload is followed by public readback of asset names, sizes, and digests before publication is called verified.

Older tagged releases remain historical custody records. The current convenience recovery object is the latest verified complete kit; copying it never transfers or deletes the canonical release.

## Current 1.2.0 maintenance

The current builder creates a new private candidate and preserves prior accepted archives. The native manifest covers every delivered member; embedded host archives are byte-checked against the same skill. Current verification belongs to the exact new candidate. Prior authoring and reviewer records remain historical and do not become current approval merely by being copied into a ZIP. Routine owner-authorized shelf reconciliation is separate from a new public announcement.

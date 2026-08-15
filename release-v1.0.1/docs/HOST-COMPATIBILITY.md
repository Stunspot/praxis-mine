# Host compatibility and evidence

Praxis Mine v1.0.1 ships as one Augment with two host components.

## Codex and ChatGPT

Use the skills-only plugin under `codex/praxis-mine/` or the separately archived plugin ZIP. The plugin contains `.codex-plugin/plugin.json`, product assets, public responsibility documents, and the complete `skills/praxis-mine/` tree.

The source package and official validator support the plugin's static structure. A host installation, fresh-task discovery, natural-language routing, and representative use remain separate observations.

## Claude

Upload `claude/praxis-mine-v1.0.1.zip` unchanged through a Claude environment that supports custom Skills. The archive contains exactly one top-level `praxis-mine/` directory with `SKILL.md` directly inside it and the complete runtime dependency closure beneath it.

Claude upload controls, plan availability, UI labels, and activation behavior may vary by product and workspace. Follow the current host interface rather than inventing a button that this package cannot observe.

## Python ledger

The optional deterministic ledger requires Python 3.11 or newer with the standard library. It includes its own SQLite record store. No package installation, network connection, account, or external database is required.

The default data home is `~/.praxis-mine/data`. `PRAXIS_MINE_DATA_HOME` and `--data-home` can select another path. File-write permission still depends on the actual host, operating system, selected path, and executing process.

## Claim ladder

| State | What establishes it |
|---|---|
| Packaged | Manifest, archive, path, hash, and structural checks pass |
| Installed | The target host reports installation or import |
| Discoverable | A fresh task or chat exposes the expected plugin or skill |
| Invoked | An explicit or natural request reaches Praxis Mine |
| Ledger-healthy | The Python commands complete against a selected data home |
| First value | A representative candidate receives a useful bounded disposition |
| Published | The intended public destination exposes the reviewed release |
| Directory-published | OpenAI approves and the publisher releases the plugin in the universal directory |

Evidence at one row does not establish the next. [Validation](VALIDATION.md) names what this release exercised.

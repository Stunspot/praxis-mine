# Install Praxis Mine in Codex or ChatGPT

Use this path for the skills-only plugin. Installation controls vary by Codex or ChatGPT surface, account, workspace policy, and release date; the package cannot truthfully pretend every host has the same button.

## What you need

- `praxis-mine-plugin-v1.0.0.zip` or the `codex/praxis-mine/` directory from the complete customer kit;
- a Codex or ChatGPT environment that supports local, repository, or uploaded plugins;
- permission to install a plugin in that environment.

## Verify the download

From the extracted complete kit, run:

```text
python tools/verify_release.py . --component-only
```

Continue only when the command exits `0` and reports `"ok": true` with no
findings. The extracted kit includes `component-custody.json` for its three
embedded host archives. Verify the complete kit itself before extraction with
the detached `.sha256` or `archive-custody.json` asset published beside it.

## Install

1. Keep the plugin root intact. It must contain `.codex-plugin/plugin.json`, `assets/`, and `skills/`.
2. Open the host's supported plugin installation or marketplace flow.
3. Choose the complete `praxis-mine` plugin directory or upload the untouched plugin ZIP, according to the host's current control.
4. Confirm the host reports the plugin installed or available.
5. Start a fresh task or chat so discovery is not inherited from stale context.
6. Look for **Praxis Mine** and then try:

   > Assess this outside skill and steal only the good bits.

## Expected result

Installation, discovery, and invocation are three observations:

1. the host accepts the plugin;
2. a fresh task exposes Praxis Mine;
3. the request produces a bounded assessment rather than a generic summary.

If the first succeeds and the second fails, use [Troubleshooting](TROUBLESHOOTING.md#the-plugin-installs-but-praxis-mine-is-not-discoverable). If the skill activates but the ledger command fails, treat that as a Python or filesystem boundary rather than an installation failure.

## Updating

Install the new version through the host's supported update or reinstall flow. Start a fresh task, confirm version `1.0.0`, and rerun one representative request. Do not delete an older copy until you know which installation owns it and have preserved any data you need.

# Uninstall Praxis Mine and manage its data

Plugin removal and ledger deletion are separate actions. Removing one does not prove the other changed.

## Remove the plugin or Skill

Use the current host's supported plugin or Skill removal control. Confirm Praxis Mine is no longer listed in a fresh task or chat. If the host installed a marketplace-managed copy, remove it through that marketplace flow rather than deleting an arbitrary cache directory.

## Find the ledger

The data home was selected by:

1. `--data-home`;
2. `PRAXIS_MINE_DATA_HOME`;
3. the default `~/.praxis-mine/data`.

Run `status` with the same path before changing it:

```text
python scripts/praxis_mine.py --data-home PATH status
```

This confirms which store is healthy; it does not back it up.

## Preserve data you need

Copy the selected data directory to a user-controlled backup location while Praxis Mine is not writing to it. Verify the copied SQLite files exist and record their hashes when exact custody matters.

The embedded storage library also contains backup and export primitives for maintainers, but Praxis Mine v1.0.0 exposes no end-user backup or restore command. Do not invent one from the file names.

## Delete data

Data deletion is a user-controlled filesystem action outside the skill's automatic workflow. Resolve the exact data-home path, confirm it contains the intended Praxis Mine registry and store, preserve any needed backup, then remove it through the operating system's normal file-management controls.

Do not delete `~/.praxis-mine` by assumption if you used a custom path. Do not delete a shared parent directory. After deletion, confirm the exact target no longer exists.

## Reinstall

Reinstalling the plugin does not recreate or import an old ledger unless the same data home remains available. A fresh `init` creates a new empty store. Restoring old data is a separate maintenance action and should preserve source, version, and integrity evidence.

# Add a Praxis Mine entry

The complete plugin and standalone skill include product ICO and ICNS files converted from the approved Praxis Mine logo. The existing browser icon and authored environments remain unchanged.

From the installed skills/praxis-mine directory, create an entry only when you want one. Choose an existing destination:

```text
python -B workspace/create_entry.py --directory "your chosen directory" --platform windows
python3 -B workspace/create_entry.py --directory "your chosen directory" --platform mac
```

Windows creates Praxis Mine.lnk pointing to the skill's Open.cmd, with empty arguments and the product ICO. Mac creates Praxis Mine.app with an ICNS-bound plist and executable launcher opening the same skill's Open.command. Python 3.11+ remains required; Windows shortcut creation requires Windows. Mac construction works on either platform, with native Mac execution qualified separately.

The helper refuses existing entries, linked destinations and missing launchers/icons. It writes only the requested new entry and does not open the mine, change research or remove another entry. Failed Mac construction is retained for inspection. Keep the installed skill in its stable location; recreate an entry at a new path after moving it.

An entry does not store a previous CLI --data-root choice. It preserves the original launcher's behavior: an explicit PRAXIS_MINE_HOME selects the room; otherwise the launcher obtains the native home from PRAXIS_MINE_DATA_HOME or ~/.praxis-mine/data. Recover the intended existing home first. Continue using the original launcher with --data-root for an explicit home, or supply the appropriate environment when launching. CLI --data-home and the native data-home setting remain available.

Remove only the entry you created to remove that shortcut or app. Preserve your separate SQLite home. See [the mine room](MINE-ROOM.md) for launch, return and recovery.

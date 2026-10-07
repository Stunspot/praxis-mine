# Praxis Mine ledger reference

The ledger is optional. Use it when candidate evidence, repeated scans, changing dispositions, or later review deserve durable local custody.

## Requirements

- Python 3.11 or newer;
- write permission to the selected data home;
- the complete `skills/praxis-mine/` directory.

No third-party Python package or network connection is required.

## Data location

Praxis Mine resolves the data home in this order:

1. `--data-home PATH`;
2. `PRAXIS_MINE_DATA_HOME`;
3. `~/.praxis-mine/data`.

The data home contains a registry database and a `stores/praxis_mine.sqlite` database. It may also contain `backups/` and `exports/` directories used by the embedded record-store library.

## Commands

Run commands from the skill root.

### Initialize

```text
python scripts/praxis_mine.py [--data-home PATH] init
```

Creates the data home, registry, Praxis Mine store, and current data contract when absent. Repeating the command checks the existing store rather than replacing it.

### Ingest a manifest

```text
python scripts/praxis_mine.py [--data-home PATH] ingest-manifest MANIFEST.json
```

Requires top-level `sources` and `candidates` arrays. The complete manifest is validated before its records commit together. A candidate must reference a known source_key, and a new candidate starts in triage. Imported labels cannot substitute for an evaluation. Duplicate JSON keys and nonfinite numbers are rejected.

### Scan a local directory

```text
python scripts/praxis_mine.py [--data-home PATH] scan-local DIRECTORY --source-key SOURCE_KEY
```

The directory must exist. The scanner records candidate roots and content hashes but does not execute the files.

### Evaluate

```text
python scripts/praxis_mine.py [--data-home PATH] evaluate CANDIDATE_KEY EVALUATION.json
```

The evaluation contains every positive/risk score, a capability delta, evidence references, preferred disposition and next test/action (optional for reject). For an actionable choice, decision_context must state baseline, comparison, rights_basis, rights_status and reason; optional owner/action_scope supports handoff. Missing substantive basis holds the result at monitor; no source or rights claim is authenticated by this helper. Scores must be integers from `0` through `5`.

### Report

```text
python scripts/praxis_mine.py [--data-home PATH] report [--output REPORT.md]
```

Without `--output`, the report is printed. With `--output`, Praxis Mine creates a new file and returns its SHA-256. It will not overwrite an existing path.

### Status

```text
python scripts/praxis_mine.py [--data-home PATH] status
```

Reports store health, candidate and evaluation counts, and how many candidates lack a current material-bound evaluation. Status and report require an existing selected home and never create an empty replacement. Unsupported schema, inconsistent registration or integrity failure is an error.

## Records

- `source`: origin, locator, access posture, cadence, and notes;
- `candidate`: source relationship, classification, summary, hash, license state, status, and evidence state;
- `run`: route, times, counts, and source;
- `evaluation`: scores, capability delta, evidence, disposition, and next test.

The ledger stores provenance and immutable revisions. Evaluation provenance binds the material candidate and source snapshot plus decision context; legacy unbound assessments remain historical. Export uses a consistent logical SQLite snapshot, with snapshot_sha256 covering the exact UTF-8 row lines, including final line feeds; it is not a hash of the main SQLite file alone. A report is a readable snapshot; use the ledger when exact record history matters.

## Exit behavior

Successful commands exit `0`; they return JSON except report without --output, which prints Markdown. Failures return a JSON object containing `"ok": false` and an error message to standard error, then exit `1`.

Preserve the exact error before changing state. See [Troubleshooting](TROUBLESHOOTING.md).

## Embedded backup and restore

The record-store Python API exposes backup_store and restore_as_store; there is no additional CLI backup command. Both reserve a new destination exclusively. Restore validates the backup and adds it as a differently named store; it does not silently replace praxis_mine or choose an active ledger. An ordinary final registry failure removes the owned restore artifact. After a power interruption, preserve any unregistered store and registry for recovery instead of deleting or relabelling them. A structural backup check is narrower than a demonstrated recovery of your particular working collection.

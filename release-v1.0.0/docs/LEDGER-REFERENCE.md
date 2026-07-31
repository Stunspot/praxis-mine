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

Requires top-level `sources` and `candidates` arrays. Sources are recorded before candidates. A candidate must reference a known `source_key`.

### Scan a local directory

```text
python scripts/praxis_mine.py [--data-home PATH] scan-local DIRECTORY --source-key SOURCE_KEY
```

The directory must exist. The scanner records candidate roots and content hashes but does not execute the files.

### Evaluate

```text
python scripts/praxis_mine.py [--data-home PATH] evaluate CANDIDATE_KEY EVALUATION.json
```

The evaluation must contain every required positive and risk score, a capability delta, evidence, preferred disposition, and next test. Scores must be integers from `0` through `5`.

### Report

```text
python scripts/praxis_mine.py [--data-home PATH] report [--output REPORT.md]
```

Without `--output`, the report is printed. With `--output`, Praxis Mine creates a new file and returns its SHA-256. It will not overwrite an existing path.

### Status

```text
python scripts/praxis_mine.py [--data-home PATH] status
```

Reports store health, candidate and evaluation counts, and how many candidates remain in `triage`.

## Records

- `source`: origin, locator, access posture, cadence, and notes;
- `candidate`: source relationship, classification, summary, hash, license state, status, and evidence state;
- `run`: route, times, counts, and source;
- `evaluation`: scores, capability delta, evidence, disposition, and next test.

The ledger stores provenance and immutable revisions. A report is a readable snapshot; use the ledger when exact record history matters.

## Exit behavior

Successful commands return JSON to standard output and exit `0`. Failures return a JSON object containing `"ok": false` and an error message to standard error, then exit `1`.

Preserve the exact error before changing state. See [Troubleshooting](TROUBLESHOOTING.md).

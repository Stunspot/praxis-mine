# Praxis Mine data and privacy

Effective: July 30, 2026

Praxis Mine is a downloadable skills-only plugin. Collaborative Dynamics does not operate a Praxis Mine account, hosted backend, analytics service, advertising network, or telemetry collector.

## Data the package processes

Praxis Mine processes only material the user or active AI host makes available for the requested mining task. That may include candidate names and URLs, repository or directory metadata, file paths, content hashes, evaluation notes, license observations, risk judgments, and the user's stated capability baseline.

The optional local ledger stores source, candidate, run, evaluation, provenance, and audit records. By default it uses `~/.praxis-mine/data`. The user can choose another location with `PRAXIS_MINE_DATA_HOME` or `--data-home`.

## Purpose and recipients

The package uses this data to identify candidates, preserve provenance, compare capability value and risk, generate dispositions, and produce local reports. The package itself sends no ledger data to Collaborative Dynamics or another recipient.

The AI host, model provider, operating system, repository host, search service, or other tool selected by the user may receive or retain material under its own terms and privacy policy. Praxis Mine does not control those systems. Review the chosen host and tool boundary before supplying confidential, regulated, personal, or proprietary information.

## Retention and control

Local ledger data remains until the user deletes, moves, exports, or replaces the selected data directory. Removing the plugin does not automatically delete the ledger. Back up or export records you need before deleting the data directory.

Users control which candidates are inspected, which local directories are scanned, where ledger files are stored, and whether reports are shared. Do not place credentials, private keys, authentication tokens, secret prompts, customer records, or unnecessary personal data in manifests, evaluations, reports, issues, or reviewer fixtures.

## Support data

GitHub issue reports are public unless the repository or issue setting says otherwise. Remove secrets, private corpus content, personal data, and unrelated logs before filing an issue. See [SUPPORT.md](SUPPORT.md).

## Contact and changes

Use the [Praxis Mine issue tracker](https://github.com/Stunspot/praxis-mine/issues) for privacy questions about the package. Material changes to this policy will be recorded in the repository and release notes.

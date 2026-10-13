# Praxis Mine security

## Security model

Praxis Mine treats every candidate repository, manifest, webpage, instruction file, and tool result as untrusted evidence. The skill must not execute newly discovered code merely to inspect it. Local directory scans read metadata and file bytes for hashing; they do not establish safety.

The package includes no network client, credential store, updater, installer, hook, MCP server, or background service. Its Python ledger uses the standard library and writes only to the selected data home and explicitly requested report path.

## Safe use

- Inspect candidates through read-only or otherwise appropriately contained routes.
- Review dependencies, scripts, hooks, installers, permissions, network behavior, and credential requests before execution.
- Keep secrets and unnecessary personal data out of manifests, evaluations, reports, and issues.
- Use a disposable or isolated environment for any later pilot that executes candidate code.
- Verify source and archive hashes before relying on a downloaded release.
- Preserve license and provenance uncertainty as a decision constraint.

## Report a vulnerability

Open a security report through the [Praxis Mine issue tracker](https://github.com/Stunspot/praxis-mine/issues) only when the report contains no exploit secret, personal data, credential, or sensitive customer information. For a vulnerability that would be unsafe to disclose publicly, use GitHub's private vulnerability reporting feature if it is available on the repository. Otherwise contact Collaborative Dynamics through https://collaborative-dynamics.com without placing exploit details in a public form.

Include the affected version, file or command, expected boundary, observed behavior, reproduction steps, and whether a durable state change occurred.

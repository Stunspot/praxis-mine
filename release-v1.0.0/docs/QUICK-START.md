# Your first Praxis Mine result

This walkthrough takes one candidate from vague interest to a bounded next move. It does not install or execute the candidate.

## Choose a candidate

Bring one outside AI skill, repository, tool, prompt pack, or workflow. You need:

- its name and link or local path;
- the outcome you hope it improves;
- what you already use for that outcome;
- any hard limits on privacy, security, license, money, runtime, or dependencies.

Sparse input is acceptable. Praxis Mine should identify the missing evidence that changes the disposition instead of making you complete an intake form from the Ministry of Forms.

## Ask for the mine

Use:

> Assess this outside skill and steal only the good bits. I want it to improve [outcome]. My current baseline is [baseline]. The candidate is [link, path, or description]. My hard limits are [limits].

If the host cannot access the link or path, attach or paste the smallest relevant files. Do not provide credentials or private material merely to make the analysis look complete.

## Inspect the result

Require six elements:

1. **Disposition:** `pilot`, `quarry`, `adapt`, `monitor`, or `reject`.
2. **Capability delta:** the outcome that becomes possible, better, cheaper, faster, or safer.
3. **Evidence:** what was observed, supplied, inferred, or remains unknown.
4. **Costs and risks:** dependencies, permissions, privacy, rights, maintenance, money, context, and overlap.
5. **Baseline comparison:** why this beats—or fails to beat—what you already have.
6. **Next test:** a small falsifiable check with a clear result.

If the answer says `adopt` without a separate acceptance gate, or recommends installation because a package is popular, the result failed Praxis Mine's governing boundary.

## Optional: create a local ledger

Open a terminal in the installed `skills/praxis-mine` directory:

```powershell
python scripts\praxis_mine.py --data-home .\praxis-data init
python scripts\praxis_mine.py --data-home .\praxis-data ingest-manifest assets\seed-manifest.json
python scripts\praxis_mine.py --data-home .\praxis-data status
```

Expected results:

- `init` reports a healthy `praxis_mine` store;
- `ingest-manifest` creates ten seed candidates on the first run;
- repeating the ingest reports those candidates unchanged;
- `status` reports candidate, evaluation, and awaiting-evaluation counts.

The `.\praxis-data` directory is disposable first-run data. See [Ledger reference](LEDGER-REFERENCE.md) before choosing a durable location.

## You are done when

You can explain what is worth keeping, why the current evidence warrants that disposition, and which observation would change the recommendation. Nothing has been installed or executed merely because it looked shiny.

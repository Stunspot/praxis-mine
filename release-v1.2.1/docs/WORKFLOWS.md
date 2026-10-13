# Praxis Mine workflows

Use the smallest workflow that answers the adoption question. A mine is not improved by moving more rock.

## Assess one outside skill

Use when you have one candidate and a real capability gap.

Provide the candidate, desired outcome, current baseline, and hard constraints. Ask Praxis Mine to inspect source, dependencies, permissions, network and credential behavior, maintenance, host fit, context cost, license state, and overlap. The result should name the disposition first and then the evidence chain.

## Compare several candidates

Use when several packages claim to solve the same problem.

Ask for one shared baseline, one representative task set, and one acceptance oracle. Compare capability delta, executable leverage, domain judgment, evidence quality, maintainability, portability, context efficiency, and material risk. Do not let each candidate define its own flattering test.

The useful output is a small ordered decision field: preferred pilot, quarry candidates, monitored alternatives, rejected duplicates, and the evidence that could reverse the order.

## Quarry a mechanism

Use when a candidate contains one excellent rubric, evaluator, schema, prompt pattern, or architecture but the complete package adds cost, overlap, or risk.

Ask Praxis Mine to identify the mechanism, the relations that make it work, its source and rights posture, what does not transfer, and the smallest native adaptation. Preserve attribution. Reimplementing a pattern is not a license invisibility cloak.

## Design a bounded pilot

Use only after a candidate earns `pilot`.

Define:

- the current baseline;
- representative work and held-out cases;
- the accepted outcome and observable oracle;
- quality, cost, latency, context, privacy, and safety guardrails;
- a disposable or contained execution environment;
- stop conditions and recovery;
- who can authorize installation, credentials, data access, and production acceptance.

A pilot tests the candidate. It does not prove the entire category or authorize rollout.

## Scan a local collection

Use the deterministic ledger when you have a directory of skill or software roots:

```powershell
python scripts\praxis_mine.py --data-home .\praxis-data scan-local C:\path\to\collection --source-key local_collection
```

The scanner identifies roots containing `SKILL.md`, `pyproject.toml`, or `package.json`, hashes the complete selected file set with framed paths and per-file hashes, and records metadata. Linked/reparse roots and members, unreadable files and files changing during a read fail the scan before candidate writes. It skips common dependency, virtual-environment, version-control, and cache directories.

The scan does not execute code, resolve transitive dependencies, read remote history, prove licensing, or judge behavior. Review the candidate before assigning a strong disposition.

## Ingest researched candidates

Normalize current research into the source and candidate arrays described by `assets/seed-manifest.json`, then run:

```powershell
python scripts\praxis_mine.py --data-home .\praxis-data ingest-manifest C:\path\to\manifest.json
```

Manifests should contain bounded evidence, not scraped secrets or a dump of every page encountered. Read the packaged `references/source-adapters.md` before automating a source.

## Evaluate and report

Copy `assets/evaluation.template.json`, replace its example text, choose explicit scores and disposition, and fill decision_context with the baseline, comparison, rights basis/status and reason. Then run:

```powershell
python scripts\praxis_mine.py --data-home .\praxis-data evaluate CANDIDATE_KEY C:\path\to\evaluation.json
python scripts\praxis_mine.py --data-home .\praxis-data report --output .\praxis-report.md
```

The score prioritizes attention; it does not make the final adoption decision. The report path must not already exist, which prevents accidental overwrite. Choose a new filename or deliberately remove the obsolete derivative after preserving anything you need.

## Resume later

Use the same data home and run `status`. Stable keys make repeated source/candidate ingestion idempotent when observed content has not changed; each completed acquisition still records a run. Unchanged local scans preserve owner tags, license conclusions and current assessments. Revised evidence creates a new record version rather than erasing the prior state.

If the candidate, source, baseline, or evaluation changed, name what changed and why before interpreting the new disposition.

## Finish authorized adaptation

For “assess this,” stop with the justified decision. For “adapt the useful part into our existing parser,” locate that parser's canonical owner, preserve upstream provenance, make the bounded change and run the owner's consequential success/failure checks. Existing scope carries through its applicable delivery. A ledger handoff is useful context, not proof of that integration. If the repository is inaccessible, say what was inspected and which exact evidence remains unavailable; do not invent a successful trial.

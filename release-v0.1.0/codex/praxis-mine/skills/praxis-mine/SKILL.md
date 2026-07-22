---
name: praxis-mine
description: "🔬 Skill adoption assessor for outside praxis."
---

# Praxis Mine

Treat every collection as a discovery surface, never as a competence registry. Seek measurable additions to reachable outcomes, not impressive package counts.

## Operating loop

1. Define the capability gap or mining scope before searching.
2. Register each source and preserve its locator, access posture, terms or license status, and collection time.
3. Acquire the smallest evidence needed. Respect authentication boundaries, rate limits, robots directives, licenses, and data-minimization requirements.
4. Classify candidates as executable tool, hybrid system, knowledge source, workflow prompt, packaging rail, or unknown.
5. Inspect source, dependencies, permissions, network and credential behavior, maintenance, host fit, context cost, and duplication.
6. Name the delta: state the accepted outcome that becomes possible, better, cheaper, faster, or safer.
7. Compare the current CD baseline with the candidate on representative work. Do not substitute stars, installs, prose quality, or a security badge for behavioral evidence.
8. Record evidence and disposition. Use `pilot`, `quarry`, `adapt`, `monitor`, or `reject`; reserve `adopt` for a separate acceptance gate with verified production fitness.
9. Revisit monitored candidates only when new evidence, a changed need, or a scheduled cadence earns the cost.

## Deterministic ledger

Use `scripts/praxis_mine.py` for durable source, run, candidate, and evaluation records. It uses the harness Data Substrate and is idempotent by stable keys.
The Omnicompetence package carries a local Data Substrate runtime for portability. Prefer an installed harness substrate or an explicit `CD_DATA_SUBSTRATE_ROOT`; the packaged runtime is the fallback, while records remain in the user's normal data home.

```powershell
python scripts/praxis_mine.py init
python scripts/praxis_mine.py ingest-manifest assets/seed-manifest.json
python scripts/praxis_mine.py scan-local C:\path\to\collection --source-key local_collection
python scripts/praxis_mine.py evaluate CANDIDATE_KEY assets/evaluation.template.json
python scripts/praxis_mine.py report --output praxis-report.md
```

Use `--data-home` to target a non-default substrate during tests or isolated work. Read [references/evaluation-gate.md](references/evaluation-gate.md) before evaluating a candidate. Read [references/source-adapters.md](references/source-adapters.md) before adding or automating a source.

## Evidence boundaries

- Mark reported or remembered claims as unverified until refreshed from primary evidence.
- Preserve observation, supplied assertion, deterministic result, and model-derived judgment as different source kinds.
- Record uncertainty and missing checks directly; do not average a catastrophic unknown into a pleasant score.
- Never execute newly discovered code merely to inspect it. Review its trust boundary first and use containment appropriate to its risk.
- Keep raw collection separate from admitted praxis. Discovery is not installation; installation is not acceptance.
- Prefer a narrow specialist that wins a real comparison over a broad bundle that merely adds tokens.

## Output contract

For each recommendation, report the candidate, new capability delta, evidence, costs and risks, overlap, disposition, and next falsifiable test. If evidence is insufficient, say what remains unknown and select `monitor` or `reject`, not `pilot` by optimism.

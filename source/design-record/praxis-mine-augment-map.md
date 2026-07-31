# Praxis Mine v1.0.0 Augment map

## Operating concept

Praxis Mine is capability-scouting intelligence for people building serious AI systems. It turns an outside candidate from “interesting thing on the internet” into an inspectable disposition: pilot it, quarry a mechanism, adapt it natively, monitor it, or reject it. It is for prompt engineers, AI systems designers, agent builders, product leads, and technically curious operators who need stronger judgment than stars, install counts, persuasive README prose, or a security badge can provide.

The useful world-change is concrete: an unbounded external candidate becomes a provenance-bearing record with a named capability delta, costs, risks, overlap, evidence state, and next falsifiable test. The user can act without importing an unknown package wholesale or pretending discovery proved production fitness.

Nova owns product integration. Praxis Mine itself supplies the specialist adoption judgment. Hesperos owns the customer journey, TestForge owns release evidence, and the user retains installation, execution, adoption, publication-attestation, and consequential-risk decisions.

## Responsibility topology

Candidate framing defines the current baseline and the missing outcome before search begins. Source custody records origin, access posture, license state, collection time, and evidence kind. Capability analysis identifies the candidate's real machinery and the outcome delta it might create. Risk and overlap analysis tests dependencies, permissions, network and credential behavior, privacy, rights, maintenance, host fit, context cost, and duplication. Admission judgment assigns one bounded disposition. Pilot design specifies a baseline, representative work, oracle, guardrails, stop condition, and evidence needed before `adopt` can even be considered.

These responsibilities form a loop rather than a conveyor belt. New evidence can reopen a disposition; a changed need can make a previously rejected candidate relevant; a failed pilot returns evidence to the candidate record. Discovery never routes directly to adoption.

## Artifact and state ecology

The skill consumes URLs, repository or directory paths, supplied manifests, candidate descriptions, local skill folders, prior baselines, and user constraints. It produces source, candidate, run, and evaluation records in a local SQLite ledger; a Markdown report; and a conversational recommendation. The ledger preserves idempotent stable keys, immutable revisions, provenance, and relations. The report is a readable derivative, not the source of record.

The state transition is `unbounded candidate → scoped evidence → disposition → falsifiable next test`. A later acceptance gate may produce `adopt`, but v1 deliberately refuses to mint that state from the mining score.

## Praxis assignment

Model cognition owns ambiguous classification, capability-delta analysis, comparison, risk interpretation, and the final recommendation. Progressive references carry the evaluation rubric and source-adapter doctrine. Python and SQLite own hashing, stable identifiers, schema validation, idempotent ingestion, immutable revision history, local scanning, report assembly, and health checks. The user owns authorization to inspect files, run candidate code, install packages, expose private data, accept license risk, and adopt a candidate.

## Package architecture

One self-contained skill is sufficient. A router or reviewer subskill would add coordination cost without owning a distinct customer job. The skill root contains `SKILL.md`, two references, JSON contracts and examples, one Python CLI, an embedded standard-library SQLite store, deterministic tests, host metadata, and its license. The public Augment wraps that skill in a skills-only plugin with production metadata and art. The customer kit contains the Codex/ChatGPT plugin, a Claude ZIP with exactly one top-level `praxis-mine` directory, a separately named standalone skill ZIP, documentation, release evidence, and checksums.

The v0.1.0 harness-dependent loader is rejected. v1 uses the embedded store directly and defaults to `~/.praxis-mine/data`, with `PRAXIS_MINE_DATA_HOME` and `--data-home` overrides. No Omnicompetence package, private substrate installation, `CODEX_HOME`, hosted service, or third-party Python dependency participates in runtime.

## First-release boundary

Version 1.0.0 includes curated-manifest ingestion, read-only local directory scanning, deterministic scoring, bounded dispositions, durable local records, reports, Codex/ChatGPT and Claude distributions, public documentation, plugin-directory review fixtures, and release verification.

It does not include automatic web crawling, account authentication, candidate execution, unattended installation, marketplace-wide ingestion, autonomous source scheduling, semantic code analysis, vulnerability scanning, or production adoption. Those additions would enlarge rights, security, infrastructure, or host assumptions without being needed to prove the distinctive value.

## Trust posture

Every candidate, website, repository, manifest, and tool result is untrusted evidence. The package does not execute discovered code during inspection. Local scans hash visible files but do not establish safety, quality, or ownership. Manifests must exclude credentials and unnecessary sensitive data. The ledger stays local unless the user explicitly moves or shares it. Consequential unknowns constrain the disposition instead of being averaged into a pleasant score.

## Proof of value

The launch demo presents an outside skill repository with impressive adoption signals and an unclear license. Praxis Mine identifies one useful evaluation mechanism, records the missing license as decision-critical, detects overlap with the user's current system, chooses `quarry` rather than installation, and specifies a small held-out comparison. The visible improvement is not a prettier summary; it is a safer, testable route to value.

## Verification and release intent

Static gates cover plugin shape, skill metadata, runtime containment, absence of private topology, JSON parsing, ZIP safety, manifest/archive parity, documentation links, and checksums. Integration tests exercise init, ingestion, idempotence, evaluation, reporting, local scan, and embedded-store loading. TestForge challenges catastrophic omissions, oracle strength, evidence custody, and the readiness claim. Hesperos authors the complete orientation-to-recovery journey; a separate fresh-context reviewer challenges it.

The public claim is bounded: Praxis Mine v1.0.0 is a self-contained, publicly obtainable skills-only Augment package whose deterministic ledger and static release paths passed the recorded checks. Live OpenAI Directory approval, broad host routing consistency, customer outcomes, and candidate fitness are not part of that claim.

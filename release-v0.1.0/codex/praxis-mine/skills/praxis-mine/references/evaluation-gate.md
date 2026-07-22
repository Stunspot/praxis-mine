# Evaluation gate

Score each positive dimension from 0 to 5 and preserve the evidence behind the number:

- `new_outcome`: enables an accepted result the current stack cannot reliably produce;
- `executable_leverage`: supplies working machinery rather than instructions alone;
- `domain_judgment`: contributes nontrivial specialist decisions or source material;
- `evidence_quality`: has meaningful tests, comparisons, traces, or inspectable outputs;
- `maintainability`: shows intelligible architecture, maintenance posture, and recoverability;
- `portability`: fits the required hosts and operating environments;
- `context_efficiency`: earns the tokens and attention it consumes.

Score risks from 0 (none found) to 5 (severe or unresolved):

- `security`, `privacy`, `license`, `cost_dependency`, and `overlap`.

The deterministic score is a prioritization aid, not the decision. The miner will not automatically return `adopt`. Missing license or severe security/privacy risk constrains the automatic result to `reject` or `monitor`. High overlap favors `quarry` or `reject`. A strong score normally earns a bounded `pilot` with a stated baseline and acceptance oracle.

Disposition meanings:

- `pilot`: run a bounded comparison against the current baseline;
- `quarry`: extract knowledge, schema, evaluator, or architectural pattern without importing the whole package;
- `adapt`: build a CD-native implementation from a useful pattern;
- `monitor`: defer until a need, evidence change, or cadence trigger;
- `reject`: no decision-relevant gain or unacceptable risk;
- `adopt`: allowed only after a separate acceptance gate verifies production fitness.

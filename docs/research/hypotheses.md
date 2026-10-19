# Preregisterable hypotheses

All hypotheses are unproven. Freeze dataset, prompts, model configuration, scoring, and exclusions before a confirmatory run.

| Hypothesis | Comparison and measurement |
|---|---|
| H1: debate improves some factual tasks | Paired correctness: debate versus single; report per-category effects and uncertainty |
| H2: retrieval reduces unsupported claims | Evidence-grounded debate versus debate with identical models; separately report information access |
| H3: explicit conflict inspection exposes unresolved disagreements | Human audit of stored disagreements against arguments; report precision and missed conflicts |
| H4: reported confidence predicts correctness imperfectly | Brier score, ECE, reliability plot, missing-confidence rate |
| H5: extra computation has a quality tradeoff | Accuracy with measured latency and available provider usage; unknown costs remain unknown |

H2 and human-audit metrics require additional evaluation beyond the current shared API. A negative or inconclusive result is valid. Do not select only categories with improvements after seeing outcomes.

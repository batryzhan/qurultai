# Evaluation method

Use paired questions across all strategies with frozen configuration. The supplied arithmetic fixture checks software behavior only; obtain a licensed, independently reviewed, sufficiently varied dataset before scientific evaluation. Keep ground-truth answers out of model prompts and retrieval context.

Correctness uses a frozen normalization rule and exact-match target for short answers. Audit extraction failures separately; this scoring is unsuitable for unrestricted essays. Define a policy for abstentions before running. Report failures and missing answers, including both all-attempt and completed-only denominators where appropriate.

For correctness y in {0,1} and reported probability p, Brier score is mean((p-y)^2). ECE is the sum across fixed confidence bins of bin_count/N times abs(bin_accuracy-bin_mean_confidence). Disclose bin boundaries, N, missing-confidence exclusions, and per-bin counts; ECE is sensitive to binning and sample size. Self-reported confidence is not automatically calibrated.

Record raw answers and run configuration. Compare paired accuracy differences and question-level uncertainty intervals; use a preselected paired test when sample size permits. Repeated runs on one question are clustered, not independent extra questions. Do not infer significance from tiny software fixtures. No significance calculation or live experimental result is supplied here.

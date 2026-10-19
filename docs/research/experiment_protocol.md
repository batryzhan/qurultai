# Reproducible experiment protocol

1. Validate and freeze dataset provenance, licensing, answers, categories and version. Review leakage risk. Set aside development questions before prompt tuning.
2. Archive exact prompt text and version/hash, source corpus version/hash, commit, dependency lockfiles, provider endpoint, actual model IDs, supported generation parameters and environment. If the API does not store a field, preserve an external run manifest; do not claim full reproducibility from the present contract alone.
3. Run `demo` to test orchestration only. Every such export is simulated and excluded from empirical reports.
4. Verify provider configuration with an actual authorized request. Do not invent supported model IDs, streaming, seeds, pricing or usage fields.
5. Import JSON through `POST /api/v1/datasets/import`; launch the same dataset using `POST /api/v1/benchmarks` with strategies `single`, `majority`, `debate`, `mode: live`, `repetitions: 1`. Additional repetitions require separate recorded runs under the current contract. Record execution order and possible temporal/provider effects.
6. Export `/api/v1/exports/benchmarks/{id}`. Retain failed attempts, raw answers, normalized answers, correctness, confidence, latency and available usage. Never replace failed calls with fabricated answers.
7. Audit labels and extraction without editing original exports. Analyze paired questions and missingness, then publish configuration, exclusions, uncertainty, and limitations together with results.

Prompt changes require a new configuration/run. No actual live benchmark has been executed by this documentation task. Human citation assessment must use a frozen support rubric and preferably blinded independent annotators with agreement reporting.

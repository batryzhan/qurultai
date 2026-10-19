# Final implementation review

Reviewed 2026-10-19 against `MASTER_SPEC.md` and the shared contract in `IMPLEMENTATION.md`. Read-only source review of backend, frontend API interactions, persistence, scientific documentation and prior review fixes. Reviewer writes only this report. No actual provider requests, credentials, commits or publishing used. Frontend and integration owners are independently completing their checks.

## Verdict

The implementation is a coherent local functional prototype: frontend routes call the shared API, sessions persist and progress through actual separate provider calls, deterministic demo outputs carry simulation labels, the benchmark runner executes three strategies without passing ground truth to providers, and exports preserve failures and missing measurements. It is suitable for a local simulated demonstration after the integration owner's browser verification. It is **not a completed empirical study or full competition-ready implementation**. Live Alem compatibility remains unverified.

Backend code is small and inspectable; strict inputs, sanitized provider errors, server-side credentials, bounded calls, timeouts, concurrency controls, safe source links and plain-text model rendering are appropriate for the documented loopback prototype. Authentication/public deployment security is explicitly outside current scope. Frontend concentrates most behavior in one App.tsx; this is manageable at present but separating feature components will help future maintenance.

## Concrete findings sent to implementation owner

1. **P2 — Research result eligibility filter.** `Research()` includes every completed non-simulated benchmark, ignoring `config.official_research_eligible`. Thus a live run using an unverified imported dataset appears in Research charts. Require explicit eligibility or visibly separate unverified exploratory runs. Backend eligibility itself is only a user assertion of dataset verification, not external certification.
2. **P2 — Provider configuration is labeled as connection success.** `i18n.ready` says “Provider connected” (and equivalents), while `/models/config` only checks endpoint/credential/model configuration. No request has necessarily succeeded. Use “Provider configured”; preserve the separate actual connection-test result.
3. **P2 — Attempt count labeled scored.** Backend metrics `count` includes failed attempts while the table heading says “Scored”. A run with one successful and one failed result displays Scored=2. Rename to Attempted or expose separate scored/calibration counts. Calibration denominators remain an advanced reporting limitation.
4. **P2 — Question length contract mismatch.** Composer allows 12,000 characters while SessionInput allows 8,000. Align the browser limit so an apparently valid input does not fail at submission.

These findings describe the reviewed snapshot; implementation owners may resolve them during final integration. Recheck source/tests before treating this report as an outstanding-issue list.

## Prior backend review status

All five actionable findings in `backend-review.md` are addressed in reviewed source: complete debate token totals are summed only when every component reports usage; interrupted sessions append terminal failure SSE events; provider concise answers are mandatory; majority confidence is omitted rather than order-dependent; application initialization runs the Alembic migration. The current backend suite passes.

## Honest scope limits and deferred requirements

- Curated local evidence contains two real source excerpts, lexical retrieval and `retrieved_unverified` / `context` labels. The claim field stores the user question. No structured claim extraction, entailment verification, citation-support metric, web retrieval or evidence-grounded benchmark ablation is implemented.
- Disagreements compare initial concise answers and preserve unresolved differences. Semantic taxonomy, evolution/resolution after revision and full graph/table interaction are incomplete.
- Cross-examination/revision/synthesis receive prior records and stage names, but stage-specific protocol instructions and validated semantic adherence remain minimal. Multiple roles may use the same model; independence of model families is not claimed.
- Benchmark exact-match normalization also strips trailing periods, beyond the stored `casefold_whitespace_exact_match` label. Freeze/document this precise rule before empirical study. Present metrics omit scored/calibration sample counts and per-bin detail. Majority has no confidence aggregation; missing values stay null.
- Complete reproducibility requires the external run manifest described in experiment_protocol.md: exact prompt/archive, provider endpoint, commit, dependency versions and timing. The current API records only part of this. Costs, paired tests, confidence intervals, repeated-run orchestration, human support judgments and empirical findings are absent.
- Persistence uses generic JSON aggregate records with an event table rather than the fully normalized master-spec data model. Lists are fetched in full; browser history pagination does not implement backend pagination. No job cancellation/resume or multi-worker queue exists.
- Localization is partial: kk/ru dictionaries inherit untranslated English strings, including some research prose; some raw stage/status/model labels and related-work table cells are English.
- Frontend unit coverage is narrow. Live integration, deployed production serving, full accessibility auditing and scientific dataset validity are not established by unit tests.

These are transparent prototype limitations, not grounds to invent research results or claim all master-spec phases complete.

## Actual checks performed by this reviewer

- `.venv/Scripts/python.exe -m pytest backend/tests -q`: **15 passed**, 2.26 seconds; one upstream Starlette TestClient/httpx deprecation warning.
- `.venv/Scripts/python.exe -m ruff check backend`: **All checks passed**.
- Reviewed full frontend API call shapes against contract, polling/SSE fallback, session panels, benchmark status/error display, research filter, imports, source URL rendering, settings labels, backend orchestration/provider/persistence/metrics, and methodological limitations.
- No real provider call or independent browser E2E was run by this reviewer. Final frontend quality-gate/browser results belong in the integration record, not inferred from this review.

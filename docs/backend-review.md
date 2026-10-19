# Independent backend review

Reviewed 2026-10-19 against `MASTER_SPEC.md` and `IMPLEMENTATION.md`; implementation was still changing. Read-only source review; only this report is reviewer-owned. No live provider requests or credentials used.

## Actionable findings

1. **P2 — Debate benchmark discards available token measurements.** `backend/app/engine.py:164` sets debate result `token_usage` to null even when every argument and synthesis reports valid usage. Reproduce with a mock live adapter returning `usage.total_tokens=17` on each of the ten one-round council calls: single reports 17, majority reports 51, debate reports null despite 170 known tokens. Sum all calls only when every call has reported usage; otherwise retain null. This blocks measured cross-strategy token comparisons, not the basic council demo.

2. **P2 — Restart failure is absent from the SSE event log.** `backend/app/main.py:32`–35 changes a running session to failed using `store.put`, without changing its stage or appending a failed event. Reproduce by persisting a running session with its last event at `revision`, restarting the app, then connecting to its events endpoint with that event's `Last-Event-ID`: the stream closes with no terminal event. An existing UI relying on event-triggered refetch can retain a running display. Use the normal session failure-event path during recovery; benchmark recovery can remain a record update.

3. **P2 — Missing concise answer passes provider validation and changes scoring semantics.** `backend/app/providers.py:28` defaults `answer` to empty; the benchmark then falls back to prose. A mock provider response `{ "content": "The result is 4.", "confidence": 0.7 }` is accepted, but a question whose answer is `4` is scored false because explanation text is exact-matched. Empty answers also suppress disagreement detection when all agents omit the field. Require a nonempty concise answer or record an extraction/schema failure; do not silently score explanation prose.

4. **P2 — Majority confidence depends on agent ordering.** `backend/app/metrics.py:19` returns the first winning reply, including its confidence. For answers `[4,4,5]` with confidences `[0.2,0.9,0.6]`, permuting the first two replies changes Brier score/ECE while votes and final answer remain identical. Define and record a reproducible aggregation policy (for example, mean confidence among winning votes), or omit aggregate confidence until such a policy exists. This is a research validity issue; it does not mean majority confidence is calibrated.

5. **P2 — Application-first database initialization conflicts with later initial migration.** `backend/app/storage.py` calls `Base.metadata.create_all` without recording an Alembic revision; `backend/alembic/versions/0001_initial.py` unconditionally creates the same tables. On a new database, start the app first, stop it, then run `alembic upgrade head` against that database: the initial migration attempts to recreate existing tables. Document and enforce migration-before-app setup, or provide a checked adoption/stamping path for application-created databases. Migration command not yet executed by reviewer because the dependency environment was incomplete.

## Scientific interpretation and scope

The current evidence adapter provides two local primary-source abstract excerpts and correctly marks them `retrieved_unverified` / `context`. It does not perform network retrieval, extract structured claims from arguments, or assess claim support. The stored `claim` is the entire question. This can satisfy a narrow, honestly described basic evidence slice; it does not establish the full claim-verification or evidence-grounded experimental condition.

Disagreement detection is lexical comparison of initial concise answers only. It honestly labels answer differences rather than inferred contradictions, but never updates resolution after revision. Semantic taxonomy, temporal disagreement analysis and resolution tracking remain advanced missing requirements.

Prompts supply prior records and source excerpts with a clear untrusted-data instruction. Stage behavior is specified only by a stage name; there are no explicit cross-examination, revision, citation-association, or unresolved-disagreement instructions. The orchestration genuinely makes separate stage calls, but detailed protocol adherence is not validated.

Metrics correctly exclude failed responses from accuracy and missing confidence from calibration; `count` is total attempted results, whereas calibration sample size is not exported. Report successful/scored and confidence-bearing denominators explicitly before interpreting research charts. Normalization additionally strips trailing periods despite the evaluation label only mentioning casefold/whitespace.

Persistence is a generic JSON-record table plus event log, not the fully normalized relational domain model in the master specification. The shared API's minimal persistence needs are implemented, but full relational constraints, history pagination, paired statistics, repeated runs, abstention metrics, citation-support metrics, monetary costs and complete experiment timing metadata are absent. Do not claim full research-ready or competition-ready completion from the minimum slice.

## Actual checks

- `.venv/Scripts/python.exe -m pytest backend/tests/test_units.py -q`: **8 passed** (1.08 s).
- `.venv/Scripts/python.exe -m pytest backend/tests -q`: **collection failed**, two importing test modules raised `ModuleNotFoundError: dotenv`; no integration tests executed in that invocation.
- Provider success/error/timeout unit checks used `httpx.MockTransport`; no live provider behavior was verified.

Verdict: the basic council/benchmark implementation has coherent, inspectable seams and preserves simulation labels, but the findings above should be resolved or explicitly scoped before describing reproducible research comparison or reliable SSE recovery as complete. Re-run integration and migration checks after dependency installation and source stabilization.

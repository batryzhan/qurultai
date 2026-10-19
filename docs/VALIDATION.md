# Validation record

Environment: Windows 11; Python 3.14.6; Node.js 24.18.1; npm 12.0.0. Date: 2026-10-19. Commands and results are actual local runs; no live provider credentials were used.

## Passed

- Backend unit and API integration tests plus benchmark CLI boundary test: `17 passed`. Covers persisted simulated debate, stage history/SSE, benchmark strategies and export, mathematical cases for accuracy/Brier/ECE, provider valid/error/timeout paths via a mock transport, budget limits, config fallback/redaction, and input validation.
- Ruff: `python -m ruff check backend scripts` passes.
- Frontend tests: `8 passed`. Covers Kazakh onboarding/language and localized related-method comparison, question submission/failure, evidence/disagreement/synthesis, honest benchmark empty state, rejected dataset import, exclusion of unverified live research results, and provider configuration wording.
- TypeScript: `npm run typecheck` passes.
- ESLint: `npm run lint` passes.
- Production build: `npm run build` passes. Recharts is lazy-loaded as a separate chart chunk. Vite reports third-party Rollup annotation comments in Zod that it removes; the build succeeds.
- npm dependency audit: `0 vulnerabilities`.
- Playwright browser suite: `3 passed`. Covers four-step first run and a full persisted demo session across evidence, disagreement and synthesis; JSON dataset import and all benchmark strategies with JSON/CSV exports; mobile council with no horizontal overflow.
- Manual in-app browser check: created and reopened the completed demo; reviewed the real locally curated Transformer excerpt with its `retrieved_unverified` label and the honest simulation/uncalibrated-confidence limitations. All three portrait assets loaded; 390 px viewport produced a 375 px document without horizontal scroll.
- Local CLI benchmark: `scripts/run_benchmark.py` imported the four-question arithmetic software fixture, completed single/majority/debate demo runs, and wrote the raw explicitly simulated export at `experiments/outputs/demo-validation.json`.
- `docker compose config --quiet` passes after copying `.env.example` to the ignored local `.env`.
- `datasets/examples/arithmetic_fixture.json` was independently checked against Python `factorial`, `gcd`, `comb`, and `isqrt`; expected answers are `[120, 6, 10, 9]`.

## Not verified

- Alem endpoint compatibility, model IDs, supported request parameters, output compliance, live cost/latency, and empirical benchmark outcomes. The server connection test requires user-configured credentials/models.
- Docker image build or runtime. Docker CLI is installed, but the local Docker Desktop Linux engine is unavailable.
- Deployment/public access and non-Windows setup instructions.

## Known warning and limitations

The backend tests emit one dependency warning: Starlette's `TestClient` reports that direct `httpx` integration is deprecated and suggests `httpx2`. Tests still pass; Qurultai depends only on documented Starlette interfaces. The JSON aggregate database, tiny lexical corpus, initial-answer comparison, user-asserted dataset verification, one repetition, absent claim-entailment review, no significance tests/reliability diagram, and in-process single-worker jobs remain prototype limits described in the reports.

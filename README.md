# QURULTAI · ҚҰРЫЛТАЙ

**Collective Wisdom, Measurable Intelligence.**

Qurultai is a local AI council and experiment workbench. Three symbolic software roles independently examine a question, review one another's arguments, revise their conclusions, and produce a synthesis. The roles draw on Kazakh council tradition without impersonating historical people:

- **Төле би / Tole Bi — Analyst:** assumptions, definitions, and logical support.
- **Қазыбек би / Kazybek Bi — Critic:** counterexamples and unsupported certainty.
- **Әйтеке би / Aiteke Bi — Synthesizer:** tradeoffs and unresolved uncertainty.

The research question is whether structured debate improves correctness and calibration compared with a single response or independent voting. **This hypothesis is unproven.** Agreement, model-reported confidence, evidence support, and factual correctness are different quantities.

## Run locally on Windows

Requires Python 3.11+ and Node.js 22.12+ (tested with Python 3.14.6 and Node 24.18.1).

```powershell
./scripts/setup.ps1
./scripts/start.ps1
```

Open [Qurultai](http://127.0.0.1:5173). No account or API key is needed for the clearly labeled deterministic demo. Setup creates `.venv`, installs Python/Node dependencies, and copies `.env.example` to `.env` if absent. Stop with Ctrl+C; the start script also stops its backend process.

Alternatively, run in separate terminals from the repository root:

```powershell
./.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm.cmd run dev
```

On macOS/Linux use `make setup`, copy `.env.example` to `.env`, then `make backend` and `make frontend` in separate terminals. These commands are provided but have not been tested on those platforms.

API: [health](http://127.0.0.1:8000/api/v1/health), [OpenAPI documentation](http://127.0.0.1:8000/docs). Vite proxies `/api` to the backend. Bind locally; this prototype has no authentication.

## Live Alem configuration

Edit the ignored root `.env`, then restart the backend:

```dotenv
ALEM_API_KEY=your-server-side-key
ALEM_BASE_URL=https://llm.alem.ai/v1
ALEM_MODEL=your-provider-supported-model-id
# Optional per-role overrides:
ALEM_MODEL_TOLE=
ALEM_MODEL_KAZYBEK=
ALEM_MODEL_AITEKE=
# Optional per-role credentials, useful when each model has a separate key:
ALEM_API_KEY_TOLE=
ALEM_API_KEY_KAZYBEK=
ALEM_API_KEY_AITEKE=
```

No model IDs are guessed. Blank role model settings fall back to `ALEM_MODEL`; blank role keys fall back to `ALEM_API_KEY`. Role-specific credentials are sent only in server-side Authorization headers and never returned by the configuration API. If every role uses the same model, it is a shared-base-model experiment; different prompts do not guarantee independence. Settings displays configuration status and offers a real server-side connection test. “Configured” does not mean the provider has been verified.

The adapter initially assumes Chat Completions with `model`, `messages`, and `max_tokens`. It requests textual JSON containing `content`, a concise `answer`, and optional `confidence`. It does not assume native JSON mode, tool calls, seeds, embeddings, or token streaming. Missing usage remains null. Actual provider compatibility and supported parameters remain **unverified without credentials**. Malformed output fails explicitly rather than being represented as a successful answer. Automatic retries are intentionally absent to avoid hidden duplicate charges.

Other environment variables: `DATABASE_URL` (default local SQLite), `CORS_ORIGINS` (comma-separated allowed origins), `LLM_TIMEOUT_SECONDS`. `ALEM_ENDPOINT` can override the completion URL; credential-bearing/query URLs are rejected. Keys never enter the frontend. The `.env.example` documents defaults; per-run rounds are selected in the app (1–3).

## What is implemented

- React/TypeScript frontend, responsive navigation, four-step onboarding, Kazakh/Russian/English UI dictionaries and independent output-language control.
- AI-generated artistic portraits with provenance and a historical-interpretation disclaimer.
- FastAPI/Pydantic request validation, SQLAlchemy SQLite persistence, and automatic Alembic startup migration.
- Distinct role prompts; independent initial calls; bounded cross examination; preserved revisions; synthesis; partial results and failure states.
- Stored stage events with SSE replay and polling fallback in the client. Progress reflects backend activity; token streaming is not simulated.
- Lexical retrieval over two locally curated primary-source excerpts. Results remain **retrieved, unverified**; a match is not proof of claim support.
- Initial concise-answer differences linked to stored arguments for basic disagreement inspection. This is not validated semantic contradiction detection.
- Validated JSON dataset imports; the frontend can convert CSV with `id,question,answer,category,source_url` columns plus provenance metadata into that API format.
- Persisted single-response, independent-voting, and debate benchmark strategies; exact-match scoring; accuracy, Brier score, ten-bin ECE, latency, available token accounting, charts and JSON/CSV exports.
- Server-side secrets, safe provider errors, restricted CORS, input limits, bounded concurrency/call counts/timeouts, and neutralized spreadsheet formula fields in CSV exports.

Database storage uses JSON aggregate records with an indexed relational event log. It does not yet normalize every claim/argument/result into separate SQL tables. Work is in-process and intended for one server worker. Interrupted running jobs become failed on restart, retaining partial records; jobs cannot be resumed or cancelled.

## Demonstrate the council

1. Complete the four-step introduction and select a UI language.
2. Enter “What is the Transformer attention architecture?” and leave execution mode on **Demo / Simulated**.
3. Open the stored debate, evidence, disagreement, and synthesis tabs. Demo work may complete immediately; no artificial delay is inserted.
4. Import `datasets/examples/arithmetic_fixture.json` in Datasets. It contains four independently computed arithmetic ground truths; it is a software fixture, not a representative research dataset.
5. Run the three strategies in Benchmark studio. Simulation deliberately abstains on most arbitrary questions. Its scores validate the pipeline, not intelligence or scientific superiority.

Run and save a raw benchmark export from the terminal:

```powershell
./.venv/Scripts/python.exe scripts/run_benchmark.py datasets/examples/arithmetic_fixture.json --output experiments/outputs/my-demo.json
```

`--mode live` enables billable configured provider calls. Failed runs and individual errors are retained. Exports record prompt version, model IDs, dataset version, scoring and evidence access. Preserve a separate frozen manifest and dependency snapshot for real research; see [experiment protocol](docs/research/experiment_protocol.md). Dataset `verified` is a user assertion, not independent certification.

## Verification

```powershell
./.venv/Scripts/python.exe -m pytest backend/tests scripts/test_benchmark_cli.py -q
./.venv/Scripts/python.exe -m ruff check backend scripts
cd frontend
npm.cmd test
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build
# With API and Vite running:
npx.cmd playwright install chromium
./node_modules/.bin/playwright.cmd test --config ../playwright.config.ts
```

See [validation record](docs/VALIDATION.md) for actual checks and limitations. Python dependency versions used during validation are in `backend/requirements-tested.txt`; Node dependencies are locked in `frontend/package-lock.json`.

## Research and competition readiness

This is a functional local prototype with evaluation infrastructure, not a completed scientific study. No live Alem benchmark, measured debate superiority, empirical confidence calibration model, or official competition certification is claimed. Simulated runs are visibly marked and excluded from the Research results view.

Current limits include a tiny retrieval corpus, question-level evidence associations instead of validated semantic claim extraction, lexical initial-answer disagreement detection, no automated entailment/human-review workflow, no monetary pricing estimates, no paired significance tests or reliability diagram, one repetition per run, and no server-side history pagination. Accuracy is completed-scored-answer accuracy; inspect failed counts and raw exports alongside it. Brier/ECE exclude missing confidence. Sample sizes are too small for scientific claims.

The research and defense materials are in `docs/research/` and `docs/competition/`; architecture diagrams are in `docs/architecture/`. The supplied rubric is used as user-provided guidance and has not been independently authenticated. Priorities for research readiness: configure/verify the provider, obtain licensed reviewed datasets, freeze experimental controls, collect real repeated paired runs, audit citation support, and analyze uncertainty before drawing conclusions.

## Docker option

Copy `.env.example` to `.env`, then `docker compose up --build`. Frontend is on loopback port 5173 and API on 8000; SQLite persists in a named volume. Nginx proxies SSE without buffering. Compose files are supplied; container build/runtime validation depends on an available Docker engine. See the validation record before relying on this path.

## Attribution

Original project implementation was produced with AI coding assistance. Track human contributions in `docs/competition/contributions_template.md`. Dependencies retain their respective licenses. The design follows the supplied Qurultai brief; portraits were generated with imagegen ([prompt/provenance record](docs/portrait-assets.md)).

Scientific context includes [self-consistency](https://arxiv.org/abs/2203.11171), [multi-agent debate](https://arxiv.org/abs/2305.14325), [retrieval-augmented generation](https://arxiv.org/abs/2005.11401), and [Karpathy's LLM Council](https://github.com/karpathy/llm-council). These are prior work, not evidence that this implementation performs better. See the verified literature review for scope and differences.

Development workflow references supplied by the user: [frontend design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md), [TDD](https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md), [subagent development](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md), [systematic debugging](https://github.com/obra/superpowers/blob/main/skills/systematic-debugging/SKILL.md), and [skill creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md). No reusable skill was created because this task builds an application.

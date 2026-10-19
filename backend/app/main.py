import asyncio
import csv
import io
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse

from .engine import benchmark_config, new_session, run_benchmark, run_council
from .providers import Provider, ProviderError
from .schemas import BenchmarkInput, DatasetInput, SessionInput, configuration
from .storage import Store, now, uid

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)


def create_app(database_url=None):
    store = Store(database_url or os.getenv("DATABASE_URL", "sqlite:///./qurultai.db"))
    active = set()

    @asynccontextmanager
    async def lifespan(app):
        # In-process work cannot survive a process restart; retain partial records honestly.
        for kind in ("session", "benchmark"):
            for record in store.all(kind):
                if record["status"] == "running":
                    record["status"] = "failed"
                    record["error"] = "Execution interrupted by server restart; partial records retained."
                    if kind == "session":
                        store.event(record, "failed", "failed")
                    else:
                        store.put(kind, record)
        yield
        store.engine.dispose()

    app = FastAPI(title="Qurultai API", version="0.1.0", lifespan=lifespan)
    app.state.store = store
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Last-Event-ID"],
    )

    @app.middleware("http")
    async def size_limit(request, call_next):
        if request.method == "POST":
            body = await request.body()
            if len(body) > 1_000_000:
                return JSONResponse(
                    {
                        "error": {
                            "code": "REQUEST_TOO_LARGE",
                            "message": "Request exceeds 1 MB.",
                            "retryable": False,
                        }
                    },
                    status_code=413,
                )
        return await call_next(request)

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return JSONResponse(
            {"error": {"code": f"HTTP_{exc.status_code}", "message": str(exc.detail), "retryable": False}},
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def invalid(request, exc):
        return JSONResponse(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request fields do not match the API schema.",
                    "retryable": False,
                }
            },
            status_code=422,
        )

    @app.exception_handler(Exception)
    async def failure(request, exc):
        return JSONResponse(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "The request could not be completed.",
                    "retryable": False,
                }
            },
            status_code=500,
        )

    router = APIRouter(prefix="/api/v1")

    def get(kind, key):
        result = store.get(kind, key)
        if result is None:
            raise HTTPException(404, "Record not found.")
        return result

    async def execute(key, worker, *args):
        try:
            await worker(*args)
        finally:
            active.discard(key)

    def reserve(key):
        if key in active:
            raise HTTPException(409, "Execution is already running.")
        if len(active) >= 2:
            raise HTTPException(429, "Two jobs are already active; try again when one completes.")
        active.add(key)

    @router.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/health", include_in_schema=False)
    def health_alias():
        return health()

    @router.get("/models/config")
    def models():
        return configuration()

    @router.post("/models/test")
    async def test_models():
        try:
            await Provider("live").ask(
                "tole", "Reply with a short connection confirmation.", "connection_test"
            )
            return {
                "ok": True,
                "message": "Provider accepted the configured model and returned validated JSON.",
            }
        except ProviderError as exc:
            return {"ok": False, "message": exc.message}

    @router.post("/sessions", status_code=201)
    def create_session(body: SessionInput):
        s = new_session(body.model_dump())
        store.event(s, "created", "created")
        return s

    @router.get("/sessions")
    def sessions():
        return store.all("session")

    @router.get("/sessions/{key}")
    def session(key: str):
        return get("session", key)

    @router.post("/sessions/{key}/start", status_code=202)
    async def start(key: str, tasks: BackgroundTasks):
        s = get("session", key)
        if s["status"] != "created":
            raise HTTPException(409, "Only a created session can be started.")
        reserve(key)
        store.event(s, "independent_analysis", "running")
        tasks.add_task(execute, key, run_council, store, s)
        return s

    @router.get("/sessions/{key}/events")
    async def events(key: str, request: Request):
        get("session", key)
        try:
            after = int(request.headers.get("Last-Event-ID", "0"))
        except ValueError:
            after = 0

        async def stream():
            cursor = after
            while not await request.is_disconnected():
                rows = store.events(key, cursor)
                for item in rows:
                    cursor = item["id"]
                    yield f"id: {cursor}\ndata: {json.dumps(item)}\n\n"
                if get("session", key)["status"] in ("completed", "failed"):
                    break
                yield ": heartbeat\n\n"
                await asyncio.sleep(0.25)

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @router.get("/sessions/{key}/{resource}")
    def subresource(key: str, resource: str):
        s = get("session", key)
        if resource == "agents":
            return s["arguments"]
        if resource == "debate":
            return [a for a in s["arguments"] if a["stage"] in ("cross_examination", "revision")]
        if resource in ("evidence", "disagreements", "synthesis"):
            return s[resource]
        raise HTTPException(404, "Unknown session resource.")

    @router.get("/datasets")
    def datasets():
        return store.all("dataset")

    @router.post("/datasets/import", status_code=201)
    def import_dataset(body: DatasetInput):
        d = {"id": uid(), **body.model_dump(), "created_at": now()}
        store.put("dataset", d)
        return d

    @router.get("/datasets/{key}")
    def dataset(key: str):
        return get("dataset", key)

    @router.post("/benchmarks", status_code=202)
    async def benchmark(body: BenchmarkInput, tasks: BackgroundTasks):
        d = get("dataset", body.dataset_id)
        # Live runs are bounded to keep request/cost exposure explicit.
        if body.mode == "live" and len(d["questions"]) > 20:
            raise HTTPException(422, "Live benchmarks allow at most 20 questions per run.")
        key = uid()
        reserve(key)
        run = {
            "id": key,
            "dataset_id": d["id"],
            "status": "running",
            "simulated": body.mode == "demo",
            "config": benchmark_config(body.model_dump(), d),
            "created_at": now(),
            "results": [],
            "metrics": {},
            "error": None,
        }
        store.put("benchmark", run)
        tasks.add_task(execute, key, run_benchmark, store, run, d)
        return run

    @router.get("/benchmarks")
    def benchmarks():
        return store.all("benchmark")

    @router.get("/benchmarks/{key}")
    def get_benchmark(key: str):
        return get("benchmark", key)

    @router.get("/benchmarks/{key}/{resource}")
    def benchmark_resource(key: str, resource: str):
        if resource not in ("results", "metrics"):
            raise HTTPException(404, "Unknown benchmark resource.")
        return get("benchmark", key)[resource]

    @router.get("/exports/sessions/{key}")
    def export_session(key: str):
        return get("session", key)

    @router.get("/exports/benchmarks/{key}")
    def export_benchmark(key: str, format: str = "json"):
        r = get("benchmark", key)
        if format == "json":
            return r
        if format != "csv":
            raise HTTPException(422, "Use json or csv export format.")
        out = io.StringIO()
        columns = [
            "question_id",
            "strategy",
            "raw_answer",
            "normalized_answer",
            "is_correct",
            "confidence",
            "latency_ms",
            "token_usage",
            "error",
        ]
        writer = csv.DictWriter(out, fieldnames=columns)
        writer.writeheader()
        for row in r["results"]:
            # Neutralize spreadsheet formula injection in user/model supplied fields.
            writer.writerow(
                {
                    k: (
                        "'" + v
                        if isinstance(v, str) and v.startswith(("=", "+", "-", "@", "\t", "\r"))
                        else v
                    )
                    for k, v in row.items()
                }
            )
        return Response(
            out.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="benchmark-{key}.csv"'},
        )

    app.include_router(router)
    return app


app = create_app()

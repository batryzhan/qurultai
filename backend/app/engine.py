import asyncio
from time import perf_counter

from .metrics import majority, metrics, normalize
from .providers import PROMPT_VERSION, Provider, ProviderError, prompt_snapshot
from .schemas import AGENTS, configuration
from .storage import now, uid

# Curated records, not fetched pages or claim verification.
SOURCES = [
    {
        "title": "Attention Is All You Need",
        "url": "https://arxiv.org/abs/1706.03762",
        "snippet": "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
        "terms": {"transformer", "attention", "трансформер"},
    },
    {
        "title": "Language Models are Few-Shot Learners",
        "url": "https://arxiv.org/abs/2005.14165",
        "snippet": "For all tasks, GPT-3 is applied without any gradient updates or fine-tuning",
        "terms": {"language", "model", "gpt", "язык", "тіл"},
    },
]


def evidence(question):
    words = set(normalize(question).split())
    return [
        {
            "id": uid(),
            "title": s["title"],
            "url": s["url"],
            "snippet": s["snippet"],
            "claim": question,
            "verification_status": "retrieved_unverified",
            "relationship": "context",
            "publisher": "arXiv",
            "retrieved_at": "2026-10-19",
            "provenance": "Locally curated primary-source abstract excerpt, checked during implementation.",
        }
        for s in SOURCES
        if words & s["terms"]
    ]


def disagreements(arguments):
    # Compare only explicit final-answer fields, never infer semantic contradiction from prose.
    initial = [a for a in arguments if a["stage"] == "initial_arguments"]
    if len({normalize(a.get("answer", "")) for a in initial}) <= 1:
        return []
    return [
        {
            "id": uid(),
            "classification": "answer_difference",
            "description": "Independent concise answers differ; this is not automatically a logical contradiction.",
            "agent_positions": {a["agent"]: a["answer"] for a in initial},
            "status": "unresolved",
            "argument_ids": [a["id"] for a in initial],
        }
    ]


async def run_council(store, s, provider=None):
    p = provider or Provider(s["mode"])

    async def stage(name):
        store.event(s, name)
        await asyncio.sleep(0)

    async def batch(name, round_number, context):
        async def one(agent):
            reply = await p.ask(agent, s["question"], name, context, s["language"])
            item = {"id": uid(), "agent": agent, "stage": name, "round": round_number, **reply}
            s["arguments"].append(item)
            store.put("session", s)

        # Independent calls share only the context snapshot from before this batch.
        outcomes = await asyncio.gather(*(one(a) for a in AGENTS), return_exceptions=True)
        for outcome in outcomes:
            if isinstance(outcome, BaseException):
                raise outcome

    try:
        await stage("independent_analysis")
        await batch("initial_arguments", 0, [])
        await stage("evidence_gathering")
        s["evidence"] = evidence(s["question"]) if s["evidence_enabled"] else []
        await stage("initial_arguments")
        store.put("session", s)
        s["disagreements"] = disagreements(s["arguments"])
        for round_number in range(1, s["rounds"] + 1):
            await stage("cross_examination")
            await batch("cross_examination", round_number, list(s["arguments"]) + s["evidence"])
        await stage("revision")
        await batch("revision", s["rounds"], list(s["arguments"]) + s["evidence"])
        await stage("synthesis")
        reply = await p.ask(
            "aiteke",
            s["question"],
            "synthesis",
            list(s["arguments"]) + s["evidence"] + s["disagreements"],
            s["language"],
        )
        s["synthesis"] = {
            "answer": reply["content"],
            "final_answer": reply["answer"],
            "token_usage": reply["token_usage"],
            "limitations": [
                "Demo outputs are deterministic simulations, not empirical model results."
                if s["simulated"]
                else "Model-reported confidence is uncalibrated.",
                "Curated local excerpts do not establish claim support; retrieval requires human review.",
            ],
            "unresolved_disagreements": [d["description"] for d in s["disagreements"]],
            "confidence": reply["confidence"],
        }
        store.event(s, "completed", "completed")
    except Exception as exc:  # noqa: BLE001 - preserve partial runs and sanitize failures
        s["error"] = exc.message if isinstance(exc, ProviderError) else "Council execution failed safely."
        store.event(s, "failed", "failed")
    return s


def new_session(body):
    return {
        "id": uid(),
        **body,
        "simulated": body["mode"] == "demo",
        "status": "created",
        "stage": "created",
        "created_at": now(),
        "arguments": [],
        "evidence": [],
        "disagreements": [],
        "synthesis": None,
        "error": None,
    }


async def run_benchmark(store, run, dataset):
    run["status"] = "running"
    store.put("benchmark", run)
    for q in dataset["questions"]:
        for strategy in run["config"]["strategies"]:
            p = Provider(run["config"]["mode"])
            start = perf_counter()
            try:
                if strategy == "debate":
                    s = new_session(
                        {
                            "question": q["question"],
                            "mode": run["config"]["mode"],
                            "language": "en",
                            "rounds": 1,
                            "evidence_enabled": False,
                            "domain": q["category"],
                        }
                    )
                    store.event(s, "created", "created")
                    await run_council(store, s, p)
                    if s["status"] == "failed":
                        raise ProviderError("DEBATE_FAILED", s["error"])
                    # Score the synthesis, never choose a ground-truth-matching agent.
                    r = {
                        "answer": s["synthesis"]["final_answer"],
                        "content": s["synthesis"]["answer"],
                        "confidence": s["synthesis"]["confidence"],
                        "token_usage": (
                            sum(a["token_usage"] for a in s["arguments"]) + s["synthesis"]["token_usage"]
                        )
                        if s["synthesis"]["token_usage"] is not None
                        and all(a["token_usage"] is not None for a in s["arguments"])
                        else None,
                    }
                else:
                    replies = await asyncio.gather(
                        *(
                            p.ask(a, q["question"], "benchmark", [], "en")
                            for a in (AGENTS if strategy == "majority" else ("tole",))
                        )
                    )
                    r = majority(replies) if strategy == "majority" else replies[0]
                    r = {
                        **r,
                        "token_usage": sum(x["token_usage"] for x in replies)
                        if all(x["token_usage"] is not None for x in replies)
                        else None,
                    }
                answer = r["answer"] or r["content"]
                result = {
                    "question_id": q["id"],
                    "strategy": strategy,
                    "raw_answer": answer,
                    "normalized_answer": normalize(answer),
                    "is_correct": normalize(answer) == normalize(q["answer"]),
                    "confidence": r["confidence"],
                    "token_usage": r.get("token_usage"),
                    "error": None,
                }
            except Exception as exc:  # noqa: BLE001 - preserve partial runs and sanitize failures
                result = {
                    "question_id": q["id"],
                    "strategy": strategy,
                    "raw_answer": "",
                    "normalized_answer": "",
                    "is_correct": None,
                    "confidence": None,
                    "token_usage": None,
                    "error": exc.message
                    if isinstance(exc, ProviderError)
                    else "Strategy execution failed safely.",
                }
            result["latency_ms"] = round((perf_counter() - start) * 1000, 3)
            run["results"].append(result)
            store.put("benchmark", run)
    run["metrics"] = {
        strategy: metrics([r for r in run["results"] if r["strategy"] == strategy])
        for strategy in run["config"]["strategies"]
    }
    run["status"] = "completed" if not any(r["error"] for r in run["results"]) else "failed"
    run["error"] = "One or more strategy executions failed." if run["status"] == "failed" else None
    store.put("benchmark", run)


def benchmark_config(body, dataset):
    return {
        **body,
        "dataset_version": dataset["version"],
        "models": configuration()["models"],
        "prompt_version": PROMPT_VERSION,
        "prompt_snapshot": prompt_snapshot(),
        "sampling": {"provider_defaults": True, "max_tokens": 1200},
        "evaluation_method": "casefold_whitespace_exact_match",
        "evidence_access": "none for every strategy",
        "confidence": "model reported; uncalibrated",
        "environment": __import__("sys").version,
        "official_research_eligible": body["mode"] == "live" and dataset["verified"],
    }

import re
from collections import Counter


def normalize(value):
    return re.sub(r"\s+", " ", value.strip().casefold()).rstrip(".")


def majority(replies):
    counts = Counter(normalize(r["answer"] or r["content"]) for r in replies)
    top = counts.most_common()
    if len(top) > 1 and top[0][1] == top[1][1]:
        return {
            "content": "No unique majority; independent answers disagree.",
            "answer": "ABSTAIN",
            "confidence": None,
        }
    return {
        **next(r for r in replies if normalize(r["answer"] or r["content"]) == top[0][0]),
        "confidence": None,
    }


def metrics(results):
    valid = [r for r in results if r["is_correct"] is not None and not r["error"]]
    calibrated = [r for r in valid if r["confidence"] is not None]
    ece = 0.0
    for i in range(10):
        group = [
            r
            for r in calibrated
            if i / 10 <= r["confidence"] < (i + 1) / 10 or (i == 9 and r["confidence"] == 1)
        ]
        if group:
            ece += (
                len(group)
                / len(calibrated)
                * abs(
                    sum(r["confidence"] for r in group) / len(group)
                    - sum(r["is_correct"] for r in group) / len(group)
                )
            )
    return {
        "accuracy": sum(r["is_correct"] for r in valid) / len(valid) if valid else None,
        "brier_score": sum((r["confidence"] - int(r["is_correct"])) ** 2 for r in calibrated)
        / len(calibrated)
        if calibrated
        else None,
        "ece": ece if calibrated else None,
        "count": len(results),
        "failed": sum(bool(r["error"]) for r in results),
        "mean_latency_ms": sum(r["latency_ms"] for r in results) / len(results) if results else None,
    }

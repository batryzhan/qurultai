"""Run a persisted benchmark via the local API; demo mode is the safe default."""

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Validated dataset import JSON")
    parser.add_argument("--api", default="http://127.0.0.1:8000/api/v1")
    parser.add_argument(
        "--mode",
        choices=["demo", "live"],
        default="demo",
        help="Live mode makes billable configured provider calls",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("experiments/outputs/latest.json")
    )
    parser.add_argument(
        "--timeout", type=float, default=600, help="Maximum job wait in seconds"
    )
    args = parser.parse_args()

    def request(route, body=None):
        payload = json.dumps(body).encode("utf-8") if body is not None else None
        req = Request(
            args.api.rstrip("/") + route,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urlopen(req, timeout=30) as response:
            return json.load(response)

    try:
        dataset = request(
            "/datasets/import", json.loads(args.dataset.read_text(encoding="utf-8-sig"))
        )
        run = request(
            "/benchmarks",
            {
                "dataset_id": dataset["id"],
                "mode": args.mode,
                "strategies": ["single", "majority", "debate"],
                "repetitions": 1,
            },
        )
        print(f"{'SIMULATED' if args.mode == 'demo' else 'LIVE'} benchmark {run['id']}")
        deadline = time.monotonic() + args.timeout
        while True:
            stored = request("/benchmarks/" + run["id"])
            if stored["status"] in ("completed", "failed"):
                break
            if time.monotonic() >= deadline:
                print(
                    "Wait timed out. The server job may still be running; inspect its saved run ID.",
                    file=sys.stderr,
                )
                return 2
            time.sleep(1)
        exported = request("/exports/benchmarks/" + run["id"])
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(exported, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"{stored['status']}: raw export saved to {args.output.resolve()}")
        return 0 if stored["status"] == "completed" else 1
    except HTTPError as exc:
        print(
            f"API rejected the request (HTTP {exc.code}). Check dataset validation and server status.",
            file=sys.stderr,
        )
    except (URLError, OSError, ValueError, KeyError):
        print(
            "Could not run the benchmark. Check the input JSON, API connection and output path.",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

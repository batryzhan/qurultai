"""Tests the standalone runner's HTTP boundary and saved raw export."""

import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def test_runner_imports_runs_and_exports_without_enabling_live(tmp_path):
    received = []

    class API(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            received.append((self.path, body))
            self.reply({"id": "d1"} if self.path.endswith("/import") else {"id": "b1"})

        def do_GET(self):
            self.reply(
                {"id": "b1", "status": "completed", "simulated": True, "results": []}
            )

        def reply(self, body):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(body).encode())

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), API)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps({"name": "Fixture", "questions": []}))
    output = tmp_path / "result.json"
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).with_name("run_benchmark.py")),
                str(fixture),
                "--api",
                f"http://127.0.0.1:{server.server_port}/api/v1",
                "--output",
                str(output),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, result.stderr
        assert received[0][1]["name"] == "Fixture"
        assert received[1][1] == {
            "dataset_id": "d1",
            "mode": "demo",
            "strategies": ["single", "majority", "debate"],
            "repetitions": 1,
        }
        assert json.loads(output.read_text())["simulated"] is True
        assert "SIMULATED" in result.stdout
    finally:
        server.shutdown()
        server.server_close()

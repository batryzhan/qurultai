# Experiment outputs

Start the API and import/run a fixture with:

```powershell
.\.venv\Scripts\python.exe scripts/run_benchmark.py datasets/examples/arithmetic_fixture.json --output experiments/outputs/demo.json
```

The default is simulated. Add `--mode live` only after configuring actual Alem credentials/model IDs and verifying the connection; this performs provider calls. Outputs are raw persisted server exports. An HTTP wait timeout does not cancel a running job. The run ID remains available in the app.

Do not interpret the arithmetic fixture or simulated outputs as evidence of factual superiority. Preserve separate output files and the frozen configuration for each real experiment. See `docs/research/experiment_protocol.md`.

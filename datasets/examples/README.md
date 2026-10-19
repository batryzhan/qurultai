# Example dataset

`arithmetic_fixture.json` matches the dataset import body in `docs/IMPLEMENTATION.md`. Import through `/api/v1/datasets/import`. It contains four project-authored software checks with mathematically verified answers; official Python documentation supplies operation definitions, not a published benchmark or individual answer labels.

No model outputs are included. The fixture is too small and narrow to support scientific performance claims. A `verified` flag records ground-truth review only; it does not establish a research sampling protocol. Demo run scores remain simulated.

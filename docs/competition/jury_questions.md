# Jury questions and defensible answers

| Question | Answer |
|---|---|
| Why three agents? | Three is a manageable design choice for distinct perspectives. Optimal agent count remains an ablation question. |
| Can all make the same mistake? | Yes. Shared models and training can produce correlated errors and false consensus. |
| What is novel? | The intended combination of inspectable protocol, disagreement and reproducible comparison is the contribution to test; debate itself has prior art. |
| How is evidence verified? | A source record and relevant snippet establish provenance/relevance only. Claim support needs explicit entailment and authority assessment. |
| What is calibrated confidence? | Across many answers with confidence near p, roughly proportion p should be correct. A model's assertion alone does not establish this. |
| How are fabricated citations prevented? | Use only configured source records and preserve status; unsupported references must remain unverified. Source existence still does not prove a claim. |
| Does it outperform one LLM? | No conclusion without paired live results, audited labels and uncertainty estimates. Demo scores cannot answer this. |
| Discussion versus voting? | Voting aggregates independent answers; discussion exposes prior answers and permits critique/revision, adding influence and cost. |
| Computational cost? | Measure actual latency and provider usage; unknown usage/prices remain unknown. More stages generally require more calls. |
| API failure? | Record failed/incomplete status and surface the error. Never replace it with an undisclosed simulation. |
| Are agents independent? | Separate invocations can use the same model. Role diversity is not statistical independence or distinct training. |
| What if they disagree? | Preserve unresolved positions and qualify the synthesis; agreement must not be forced. |
| Is a high demo accuracy scientific evidence? | No. A small deterministic fixture is a software regression check. |

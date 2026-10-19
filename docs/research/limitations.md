# Methodological limitations

| Limitation | Consequence and mitigation |
|---|---|
| Tiny arithmetic fixture | Tests plumbing, not scientific generalization; use a broader reviewed dataset |
| Same base model across roles | Correlated errors; record mapping and compare model diversity separately |
| Self-reported confidence | Uncalibrated until evaluated; show missing values and sample sizes |
| Curated source matches | Relevance is not entailment; audit exact claim support and source authority |
| More calls for debate | Accuracy alone hides cost; report latency and available usage |
| Unknown provider accounting | No invented token or price estimates; preserve null values |
| Prompt tuning and leakage | Freeze held-out questions and record every prompt revision |
| Small samples / bins | Unstable ECE and effects; avoid superiority and significance claims |
| Shared API has limited run metadata | Archive a separate immutable experiment manifest |
| Supplied rubric unverified | Check official current rules before submission |

Evidence-grounded benchmark ablation, human support scoring, statistical testing and calibration validation may remain planned even when a demo works. See implementation checks before claiming any feature is validated.

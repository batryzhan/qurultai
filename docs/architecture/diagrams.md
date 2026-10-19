# Architecture diagrams

Contract-aligned design snapshot: `../IMPLEMENTATION.md`, 2026-10-19. These diagrams describe API concepts and intended execution, not a claim that all implementation paths have passed validation. Database entities below are logical JSON aggregates, not asserted physical SQL tables.

```mermaid
flowchart LR
    UI[React browser] -->|JSON /api/v1| API[FastAPI backend]
    API --> DB[(SQLite persistence)]
    API --> ORCH[Debate and benchmark orchestration]
    ORCH --> MOCK[Deterministic demo provider]
    ORCH --> LIVE[Configured live adapter]
    LIVE --> EXT[External LLM endpoint]
    ORCH --> CUR[Curated source records]
    API -->|SSE stage/status then refetch| UI
```

Credentials belong on the backend. Source text and model output are untrusted data.

```mermaid
flowchart TD
    created --> independent_analysis --> evidence_gathering --> initial_arguments
    initial_arguments --> cross_examination --> revision
    revision -->|additional configured round| cross_examination
    revision --> synthesis --> completed
    independent_analysis -->|provider or validation error| failed
    cross_examination -->|provider or validation error| failed
    synthesis -->|provider or validation error| failed
```

Evidence gathering may have no records when disabled or unmatched. Preserve incomplete sessions on failure.

```mermaid
erDiagram
    Session ||--o{ Argument : contains
    Session ||--o{ Evidence : contains
    Session ||--o{ Disagreement : contains
    Session ||--o| Synthesis : contains
    Disagreement }o--o{ Argument : argument_ids
    Dataset ||--|{ Question : contains
    Dataset ||--o{ Benchmark : dataset_id
    Benchmark ||--o{ Result : contains
    Question ||--o{ Result : question_id
```

```mermaid
flowchart TD
    Import[Import dataset JSON] --> Validate[Validate fields and provenance]
    Validate --> Freeze[Freeze dataset and external run manifest]
    Freeze --> Run[POST /benchmarks]
    Run --> Single[single]
    Run --> Majority[majority]
    Run --> Debate[debate]
    Single --> Store[Persist raw answers and failures]
    Majority --> Store
    Debate --> Store
    Store --> Score[Normalize and score against ground truth]
    Score --> Metrics[Accuracy Brier ECE latency with missingness]
    Metrics --> Export[JSON or CSV export]
    Export --> Audit[Audit simulation flag before empirical analysis]
```

```mermaid
flowchart TD
    Claim[Claim from argument] --> Match[Match configured source records]
    Match -->|none| Missing[Mark missing or unsupported]
    Match --> Record[Store title URL snippet claim relationship]
    Record --> Relevant[Assess relevance]
    Relevant --> Support[Assess exact claim support and authority]
    Support --> Status[Persist explicit verification_status]
    Status --> UI[Evidence inspection]
```

The evidence diagram includes a required assessment boundary. A curated match alone must not be represented as having passed support verification; human/automated entailment evaluation may remain future work.

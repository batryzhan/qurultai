# Verified literature and provenance

Primary pages opened on 2026-10-19. Bibliographic identity and abstract-level descriptions were checked; this is a concise starting review, not a systematic review or replication.

- Xuezhi Wang et al. (2022 preprint; ICLR 2023), [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171). Samples reasoning paths and aggregates answers. Motivates an independent-answer baseline; published gains do not establish Qurultai's performance.
- Yilun Du, Shuang Li, Antonio Torralba, Joshua B. Tenenbaum, Igor Mordatch (2023), [Improving Factuality and Reasoning in Language Models through Multiagent Debate](https://arxiv.org/abs/2305.14325). Studies multiple model instances exchanging and revising answers. Supports testing interaction separately from independent aggregation.
- Patrick Lewis et al. (2020), [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401). Combines retrieval with generation. Motivates explicit source access; Qurultai's curated-source layer should not be described as a replication of the trained RAG architecture.
- Andrej Karpathy, [LLM Council repository](https://github.com/karpathy/llm-council), accessed 2026-10-19. README describes individual answers, anonymized peer review/ranking, and a chairman synthesis. This is software inspiration, not evidence that a council is always more accurate. No commit snapshot was pinned during this review.

Remaining literature work: systematic search criteria, negative debate results, calibration references, benchmark licenses, and version-pinned source archives. No performance statistics from these sources are claimed for this implementation.

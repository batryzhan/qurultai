# Implementation ledger

Authority: MASTER_SPEC.md. Empty repository inspected 2026-10-19. Work on implementation branch.

## Tasks
- [x] Backend: persistence, providers, staged debate, evidence, SSE, validated datasets and benchmark strategies.
- [x] Frontend: visual system, four-step onboarding, council, sessions, evidence, disagreements, datasets, benchmarks, research, settings.
- [x] Integration: verify shared contract, migrations, local setup and scientific documentation.
- [x] Review and quality gates: backend tests/lint, frontend tests/typecheck/lint/build, browser journey.

## Shared contract
JSON API prefix `/api/v1`. IDs are strings. UTC times are ISO strings. Errors `{error:{code,message,retryable}}`.
GET `/health` -> `{status:"ok"}`.
GET `/models/config` -> `{configured:boolean, endpoint:string, models:{tole:string,kazybek:string,aiteke:string}, simulated_available:true}`. POST `/models/test` -> `{ok:boolean,message:string}`.
POST `/sessions` body `{question, mode:"demo"|"live", language:"kk"|"ru"|"en", rounds:1|2|3, evidence_enabled:boolean, domain:string}` -> Session.
Session `{id,question,mode,simulated,status,stage,language,rounds,evidence_enabled,domain,created_at,arguments:Argument[],evidence:Evidence[],disagreements:Disagreement[],synthesis:Synthesis|null,error:string|null}`.
Argument `{id,agent:"tole"|"kazybek"|"aiteke",stage,round,content,confidence:number|null,model:string,token_usage:number|null}`.
Evidence `{id,title,url,snippet,claim,verification_status,relationship}`. Curated matches are not automatically claim verified.
Disagreement `{id,classification,description,agent_positions:Record<string,string>,status,argument_ids:string[]}`.
Synthesis `{answer,limitations:string[],unresolved_disagreements:string[],confidence:number|null}`.
GET `/sessions` -> Session[]. GET `/sessions/{id}` -> Session. POST `/sessions/{id}/start` starts background execution -> Session (202). GET `/sessions/{id}/events` SSE `data: {id,stage,status}`; frontend refetches session. Stage names: created, independent_analysis, evidence_gathering, initial_arguments, cross_examination, revision, synthesis, completed, failed.
Subresources `/agents`, `/debate`, `/evidence`, `/disagreements`, `/synthesis` return corresponding session data.
GET `/datasets` -> Dataset[]. Dataset `{id,name,version,provenance,verified,questions:Question[],created_at}`. Question `{id,question,answer,category,source_url}`.
POST `/datasets/import` JSON `{name,version,provenance,verified,questions}` -> Dataset.
GET `/datasets/{id}` -> Dataset.
POST `/benchmarks` body `{dataset_id,mode:"demo"|"live",strategies:string[],repetitions:1}` -> Benchmark. Strategies `single`, `majority`, `debate`.
Benchmark `{id,dataset_id,status,simulated,config,created_at,results:Result[],metrics:Record<string,Metrics>,error:string|null}`.
Result `{question_id,strategy,raw_answer,normalized_answer,is_correct:boolean|null,confidence:number|null,latency_ms,token_usage:number|null,error:string|null}`.
Metrics `{accuracy:number|null,brier_score:number|null,ece:number|null,count:number,failed:number,mean_latency_ms:number|null}`. GET `/benchmarks` -> Benchmark[]. GET `/benchmarks/{id}` -> Benchmark. Subresources `/results`, `/metrics`. Exports `/exports/sessions/{id}`, `/exports/benchmarks/{id}` JSON; optional `?format=csv` for benchmarks.

## Preflight interface review
| Tasks | Shared interface | Finding |
|---|---|---|
| Backend / frontend | Above API | Fixed common names and shapes before implementation |
| Backend | Tests / implementation | Tests first; mock transport for live adapter |
| Frontend | Tests / UI | Behavioral tests before components; design from supplied palette |
| Integration / backend | migrations and documentation | Integrator reads implementation before documenting |

Ruling: parallel independent frontend/backend ownership is permitted by the master specification; no shared source files will be edited concurrently. The referenced skill's sequential default is adapted to that explicit authorization.
Ruling: portraits are a separate asset task; marked placeholders until generated assets exist. No historical impersonation.
Ruling: supplied competition rubric is unverified external context, used as supplied and not independently certified.

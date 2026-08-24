# Deployment

## On-premise

```
Enterprise Network → Load Balancer → API Gateway → Claim API Service
                                                         │
                                         ┌───────────────┴───────────────┐
                                    Agent Service                 Receipt Service
                                         │                               │
                           ┌─────────────┼──────────┐            OCR / Document Processing
                      Policy RAG    Duplicate    Calculator
                           │
                      Vector DB → PostgreSQL → Audit DB
```

Suggested stack: Kubernetes/OpenShift, FastAPI, vLLM or an enterprise LLM
endpoint, PostgreSQL, pgvector, MinIO, Redis, Kafka. Preferred when data
residency and network control for employee financial data are hard
requirements.

## GCP

```
Employee → API Gateway → Cloud Run API
                              │
                ┌─────────────┴─────────────┐
          Cloud Storage                Cloud SQL
        (receipt docs)              (claim metadata)
                │
          Document AI / Gemini
                │
        Travel Agent on Cloud Run
                │
   ┌────────────┼─────────────────┐
BigQuery    Vertex AI/Gemini    Cloud SQL (rules)
                │
          Vector Search → Policy RAG → Decision Engine
                │
        Pub/Sub / Workflows → Finance / ERP System
```

| Requirement | GCP service |
|---|---|
| API Gateway / compute | Cloud Run |
| Agent | Vertex AI / Gemini + ADK |
| Documents | Cloud Storage |
| OCR | Document AI |
| Policy data | BigQuery / Cloud SQL |
| Vector search | Vertex AI Vector Search |
| Workflow | Workflows |
| Async events | Pub/Sub |
| Secrets | Secret Manager |
| Identity | IAM |
| Encryption | Cloud KMS |
| Monitoring / Logs / Audit | Cloud Monitoring / Cloud Logging / Cloud Audit Logs |
| CI/CD | Cloud Build / Artifact Registry |
| Network | VPC / Private Service Connect |

## Event-driven flow

```
POST /claims → API Gateway → Cloud Run
                                  ├── Store claim → Cloud SQL
                                  ├── Store receipt → GCS
                                  └── Publish event → Pub/Sub
                                              │
                                        Cloud Run Worker
                                              │
                                  Document extraction → Agent invocation
                                              │
                                  Policy retrieval → Tool execution
                                              │
                                        Decision Engine
                                       ┌──────┴───────┐
                                Finance System   Human Review
```

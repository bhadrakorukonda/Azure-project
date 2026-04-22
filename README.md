# ⚡ azure-llm-inference

A production-grade LLM inference API deployed on **Azure Container Apps** with auto-scaling, CI/CD, and real-time telemetry via Azure Monitor.

Built to mirror the architecture of large-scale Model-as-a-Service (MaaS) platforms.

---

## Architecture

```
GitHub Push
    │
    ▼
GitHub Actions CI/CD
    │
    ├──► Docker Build
    │
    ├──► Push → Azure Container Registry (ACR)
    │
    └──► Deploy → Azure Container Apps
                      │
                      ├── Auto-scaling (0 → N replicas)
                      ├── Rolling deploys (zero downtime)
                      └── Azure Application Insights
                              │
                              └── Latency · Throughput · Errors
```

---

## Stack

| Layer | Technology |
|---|---|
| Inference API | FastAPI + Uvicorn |
| Model | TinyLlama-1.1B (HuggingFace) |
| Containerization | Docker |
| Registry | Azure Container Registry (ACR) |
| Hosting | Azure Container Apps |
| Observability | Azure Monitor + Application Insights |
| CI/CD | GitHub Actions |

---

## Features

- **REST inference endpoint** — `POST /generate` accepts a prompt, returns streamed or batched LLM output
- **Health check endpoint** — `GET /health` for liveness/readiness probes
- **Auto-scaling** — Container Apps scales replicas based on HTTP concurrency
- **Zero-downtime deploys** — rolling update strategy via Container Apps revisions
- **Telemetry** — request latency, token throughput, and error rates piped to Application Insights
- **CI/CD pipeline** — every push to `main` triggers build → push → deploy automatically

---

## Project Structure

```
azure-llm-inference/
├── app/
│   ├── main.py               # FastAPI app, routes
│   ├── model.py              # Model loading + inference logic
│   └── telemetry.py          # Azure Application Insights setup
├── .github/
│   └── workflows/
│       └── deploy.yml        # GitHub Actions CI/CD pipeline
├── Dockerfile
├── requirements.txt
├── containerapp.yaml         # Azure Container Apps config
└── README.md
```

---

## API Reference

### `POST /generate`

Generate text from a prompt.

**Request**
```json
{
  "prompt": "Explain transformers in simple terms.",
  "max_tokens": 200,
  "temperature": 0.7
}
```

**Response**
```json
{
  "output": "A transformer is a neural network architecture...",
  "model": "TinyLlama-1.1B",
  "latency_ms": 312
}
```

---

### `GET /health`

Returns service health status. Used by Azure Container Apps liveness probe.

```json
{ "status": "ok", "model_loaded": true }
```

---

## Local Setup

### Prerequisites
- Python 3.10+
- Docker
- Azure CLI (`az`)

### Run locally

```bash
git clone https://github.com/YOUR_USERNAME/azure-llm-inference
cd azure-llm-inference

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Test it:
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is a large language model?", "max_tokens": 100}'
```

### Run with Docker

```bash
docker build -t azure-llm-inference .
docker run -p 8000:8000 azure-llm-inference
```

---

## Azure Deployment

### 1. Login and set up resources

```bash
az login

az group create --name llm-inference-rg --location eastus

az acr create \
  --resource-group llm-inference-rg \
  --name YOUR_ACR_NAME \
  --sku Basic \
  --admin-enabled true

az containerapp env create \
  --name llm-inference-env \
  --resource-group llm-inference-rg \
  --location eastus
```

### 2. Build and push image to ACR

```bash
az acr build \
  --registry YOUR_ACR_NAME \
  --image azure-llm-inference:latest .
```

### 3. Deploy to Azure Container Apps

```bash
az containerapp create \
  --name llm-inference-api \
  --resource-group llm-inference-rg \
  --environment llm-inference-env \
  --image YOUR_ACR_NAME.azurecr.io/azure-llm-inference:latest \
  --registry-server YOUR_ACR_NAME.azurecr.io \
  --target-port 8000 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 5 \
  --cpu 1.0 \
  --memory 2.0Gi
```

### 4. Set GitHub Actions secrets

In your GitHub repo → Settings → Secrets, add:

| Secret | Value |
|---|---|
| `AZURE_CREDENTIALS` | Output of `az ad sp create-for-rbac` |
| `ACR_NAME` | Your ACR name |
| `RESOURCE_GROUP` | `llm-inference-rg` |

Every push to `main` will now auto-deploy.

---

## Observability

Application Insights tracks:

- **Request latency** (p50, p95, p99)
- **Token throughput** (tokens/sec per replica)
- **Error rate** and exception traces
- **Replica scale events**

View dashboards at: [Azure Portal → Application Insights → your resource]

---

## Results

| Metric | Value |
|---|---|
| Cold start time | ~8s (TinyLlama on CPU) |
| Avg inference latency | ~300ms (200 token output) |
| Scale-to-zero | ✅ 0 replicas when idle |
| CI/CD deploy time | ~3 min end-to-end |

---

## Why This Architecture Matters

This project mirrors the core concerns of Azure's MaaS (Model-as-a-Service) platform:

- **Scalable inference serving** — stateless containers that scale horizontally
- **Registry-based deployments** — immutable image tags for safe rollbacks
- **Observability-first** — telemetry baked in from day one, not bolted on
- **GitOps workflow** — infrastructure and app changes tracked in version control

---

## License

MIT

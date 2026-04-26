import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.model import load_model, generate_text
from app.telemetry import track_request

app = FastAPI(title="Azure LLM Inference API", version="1.0.0")

model = None

@app.on_event("startup")
async def startup_event():
    global model
    model, _ = load_model()


class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 200
    temperature: float = 0.7


class GenerateResponse(BaseModel):
    output: str
    model: str
    latency_ms: float


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")

    start = time.time()
    output = generate_text(
        model=model,
        tokenizer=None,
        prompt=request.prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
    )
    latency_ms = (time.time() - start) * 1000

    track_request(
        prompt_length=len(request.prompt),
        output_length=len(output),
        latency_ms=latency_ms,
    )

    return GenerateResponse(
        output=output,
        model="phi-2-Q4_K_M",
        latency_ms=round(latency_ms, 2),
    )
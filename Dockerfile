FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install llama-cpp-python (CPU build) and FastAPI
RUN pip install --no-cache-dir \
    fastapi==0.116.1 \
    uvicorn[standard]==0.29.0 \
    pydantic==2.6.4 \
    llama-cpp-python==0.2.57 \
    opencensus-ext-azure==1.1.13 \
    opencensus==0.11.4

# Download quantized model (~500MB, runs fine on 2GB RAM)
RUN curl -L -o /app/model.gguf \
    "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf"

COPY app/ ./app/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
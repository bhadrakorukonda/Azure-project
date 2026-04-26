from llama_cpp import Llama
import os

MODEL_PATH = "/app/model.gguf"

_model = None

def load_model():
    global _model
    print(f"Loading model from {MODEL_PATH}")
    _model = Llama(
        model_path=MODEL_PATH,
        n_ctx=512,
        n_threads=2,
        verbose=False,
    )
    print("Model loaded successfully.")
    return _model, None  # No separate tokenizer needed


def generate_text(model, tokenizer, prompt: str, max_tokens: int = 200, temperature: float = 0.7) -> str:
    response = model(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        stop=["</s>", "\n\n\n"],
        echo=False,
    )
    return response["choices"][0]["text"].strip()
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = "microsoft/phi-1_5"


def load_model():
    """Load tokenizer and model from HuggingFace Hub."""
    print(f"Loading model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float32,
        trust_remote_code=True,
    )
    model.eval()
    print("Model loaded successfully.")
    return model, tokenizer


def generate_text(
    model,
    tokenizer,
    prompt: str,
    max_tokens: int = 200,
    temperature: float = 0.7,
) -> str:
    """Run inference and return generated text."""
    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs["input_ids"]

    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.1,
        )

    new_tokens = output_ids[0][input_ids.shape[-1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)
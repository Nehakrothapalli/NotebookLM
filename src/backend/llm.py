import os
import gradio as gr
from huggingface_hub import InferenceClient
from huggingface_hub.utils import HfHubHTTPError

HF_INFERENCE_TOKEN = os.environ.get("HF_INFERENCE_TOKEN","").strip()
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
HF_API_TOKEN = HF_INFERENCE_TOKEN or HF_TOKEN
HF_LLM_MODEL = os.environ.get("HF_LLM_MODEL","HuggingFaceH4/zephyr-7b-beta").strip()

_client = InferenceClient(model=HF_LLM_MODEL, token=HF_API_TOKEN) if HF_API_TOKEN else None

def llm_generate(prompt: str, max_new_tokens=450, temperature=0.2) -> str:
    if _client is None:
        raise gr.Error("Set HF_INFERENCE_TOKEN (or HF_TOKEN) in Space secrets or local environment.")
    try:
        out = _client.text_generation(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            return_full_text=False,
        )
        return (out or "").strip()
    except ValueError as e:
        msg = str(e)
        if "not supported for task text-generation" in msg or "Supported task: conversational" in msg:
            try:
                resp = _client.chat.completions.create(
                    model=HF_LLM_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_new_tokens,
                    temperature=temperature,
                )
                choice = (resp.choices or [None])[0]
                content = getattr(getattr(choice, "message", None), "content", "") if choice else ""
                return (content or "").strip()
            except Exception as inner:
                raise gr.Error(f"LLM request failed after conversational fallback: {inner}")
        raise gr.Error(f"LLM request failed: {msg}")
    except HfHubHTTPError as e:
        msg = str(e)
        if "api-inference.huggingface.co is no longer supported" in msg or "410 Client Error" in msg:
            raise gr.Error(
                "Your Hugging Face Hub client is outdated for inference routing. "
                "Upgrade `huggingface_hub` and restart the app."
            )
        raise gr.Error(f"LLM request failed: {msg}")
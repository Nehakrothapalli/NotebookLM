import os
import gradio as gr


def require_login(request: gr.Request) -> str:
    """
    Hugging Face Spaces OAuth provides user info via request in some Gradio versions,
    but not always. We use multiple fallbacks:
    1) request.username (best case)
    2) HF-proxy headers (x-forwarded-*)
    3) local/dev fallback
    """
    # 1) Best-case Gradio field
    username = getattr(request, "username", None)
    if username:
        return str(username)

    # 2) Fallback: HF spaces headers (varies by proxy/version)
    headers = getattr(request, "headers", {}) or {}
    for key in [
        "x-forwarded-user",
        "x-hf-user",
        "x-forwarded-preferred-username",
        "x-auth-request-preferred-username",
    ]:
        if key in headers and headers[key]:
            return str(headers[key])

    # 3) Optional local fallback (so app doesn't hard-crash during dev)
    if os.getenv("HF_SPACE_ID") is None:
        return "localuser"

    raise gr.Error("Please log in using 'Sign in with Hugging Face' to use this app.")
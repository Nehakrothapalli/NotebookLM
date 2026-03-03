#"use client"

import os

# Disable Chroma telemetry noise
os.environ["ANONYMIZED_TELEMETRY"] = "FALSE"

from src.frontend.ui import build_app

demo = build_app()

if __name__ == "__main__":
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7860")),
        show_api=False,
    )
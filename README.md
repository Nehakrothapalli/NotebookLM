---
title: NotebookLM Clone (GPP1)
emoji: 📓
colorFrom: blue
colorTo: pink
sdk: gradio
sdk_version: "4.44.1"
app_file: app.py
pinned: false
hf_oauth: true
---

# NotebookLM Clone (HF OAuth + Chroma + RAG)

## Overview

This project is a simplified clone of Google NotebookLM. Users can create multiple notebooks, upload sources (PDF/PPTX/TXT/URL), chat with their sources using Retrieval-Augmented Generation (RAG) with citations, and generate study artifacts (report, quiz, podcast).

## Features

- HF OAuth login (per-user isolation)
- Multi-notebook support: create/rename/delete
- Ingestion: PDF / PPTX / TXT / URL
- Chunking + Embedding (Sentence-Transformers all-MiniLM-L6-v2)
- Vector search using ChromaDB (persistent per notebook)
- Chat with citations
- Artifact generation:
  - report (.md)
  - quiz with answer key (.md)
  - podcast transcript (.md) + audio (.mp3)

## Environment Variables

### Hugging Face Space

- DATA_ROOT=/data

## Local Dev

1. Create venv + install dependencies:
   - pip install -r requirements.txt

- **Use Python 3.12**: this project is pinned to 3.12.x for compatibility. The repo includes `runtime.txt` for Hugging Face Spaces and a Python 3.12 `Dockerfile` for containers.

2. Run:
   - python app.py
     Note: HF OAuth is best tested in a Space.

## Container / Space Deployment

You can package the app in a Docker container or push it to a Hugging Face Space. A sample `Dockerfile` is included:

```dockerfile
# Dockerfile (Python 3.12)
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./
EXPOSE 7860
CMD ["python", "app.py"]
```

For a Space, the `runtime.txt` file pins the Python version to 3.12.18. Make sure to commit both `requirements.txt` and `runtime.txt` so the build uses the correct interpreter.

Deployment examples: 

```bash
# build locally
docker build -t notebooklm .
docker run -p 7860:7860 notebooklm

# or push to HF Space (CLI)
hf repo create <your-space> --type=space
git push hf main
```

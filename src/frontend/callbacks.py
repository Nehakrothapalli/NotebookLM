import os
import time
from datetime import datetime
import gradio as gr

from src.backend.notebooks import create_notebook, rename_notebook, delete_notebook
from src.storage.index_store import list_notebooks
from src.storage.paths import ensure_tree, nb_root
from src.storage.chat_store import append_chat, load_chat
from src.storage.artifact_store import list_artifacts as list_artifacts_store, next_artifact_path
from src.backend.ingest import ingest_files as ingest_files_backend, ingest_url as ingest_url_backend
from src.backend.rag import retrieve, rag_answer
from src.backend.artifacts import (
    generate_report,
    generate_quiz,
    generate_podcast_transcript,
    transcript_to_mp3,
)


def now_iso():
    return datetime.utcnow().isoformat() + "Z"


def _require_notebook(notebook_id: str):
    if not notebook_id:
        raise gr.Error("Please create/select a notebook first.")


def chat_pairs(history):
    pairs = []
    last_user = None
    for m in history:
        if m.get("role") == "user":
            last_user = m.get("content", "")
        elif m.get("role") == "assistant":
            pairs.append((last_user or "", m.get("content", "")))
            last_user = None
    return pairs


def ui_bootstrap(username: str):
    nbs = list_notebooks(username)

    if not nbs:
        nb_id = create_notebook(username, "My First Notebook")
        nbs = list_notebooks(username)
        current = nb_id
    else:
        current = nbs[0][1]

    ensure_tree(username, current)
    history = load_chat(username, current)
    artifacts = list_artifacts_store(username, current)

    return gr.Dropdown(choices=nbs, value=current), chat_pairs(history), artifacts


def on_switch_notebook(username: str, notebook_id: str):
    _require_notebook(notebook_id)
    ensure_tree(username, notebook_id)
    history = load_chat(username, notebook_id)
    return chat_pairs(history), list_artifacts_store(username, notebook_id)


def on_create_notebook(username: str, name: str):
    name = (name or "").strip() or "Untitled Notebook"
    nb_id = create_notebook(username, name)
    nbs = list_notebooks(username)
    ensure_tree(username, nb_id)
    return gr.Dropdown(choices=nbs, value=nb_id), [], list_artifacts_store(username, nb_id)


def on_rename_notebook(username: str, notebook_id: str, new_name: str):
    _require_notebook(notebook_id)
    new_name = (new_name or "").strip()
    if not new_name:
        raise gr.Error("Enter a new notebook name.")
    rename_notebook(username, notebook_id, new_name)
    return gr.Dropdown(choices=list_notebooks(username), value=notebook_id)


def on_delete_notebook(username: str, notebook_id: str):
    _require_notebook(notebook_id)
    delete_notebook(username, notebook_id)
    # Return the bootstrap tuple (dropdown, chat, artifacts)
    return ui_bootstrap(username)


def on_ingest_files(username: str, notebook_id: str, files):
    _require_notebook(notebook_id)
    if not files:
        raise gr.Error("Upload at least one file.")
    try:
        added = ingest_files_backend(username, notebook_id, files)
    except Exception as e:
        raise gr.Error(f"File ingest failed: {e}")
    if added == 0:
        raise gr.Error("No chunks were indexed. Use supported files (PDF/PPTX/TXT) with extractable text.")
    return f"Ingested files. Added {added} chunks."


def on_ingest_url(username: str, notebook_id: str, url: str):
    _require_notebook(notebook_id)
    url = (url or "").strip()
    if not url:
        raise gr.Error("Enter a URL.")
    try:
        added = ingest_url_backend(username, notebook_id, url)
    except Exception as e:
        raise gr.Error(f"URL ingest failed: {e}")
    if added == 0:
        raise gr.Error("No chunks were indexed from the URL.")
    return f"Ingested URL. Added {added} chunks."


def on_chat(username: str, notebook_id: str, chatbot, msg: str):
    _require_notebook(notebook_id)

    msg = (msg or "").strip()
    if not msg:
        return chatbot, ""

    t0 = time.time()

    append_chat(username, notebook_id, {"role": "user", "content": msg, "ts": now_iso()})

    hits = retrieve(username, notebook_id, msg, k=6)
    ans = rag_answer(msg, hits)

    append_chat(
        username,
        notebook_id,
        {
            "role": "assistant",
            "content": ans,
            "ts": now_iso(),
            "latency_ms": int((time.time() - t0) * 1000),
        },
    )

    chatbot = chatbot + [(msg, ans)]
    return chatbot, ""


def on_report(username: str, notebook_id: str, topic: str, extra: str):
    _require_notebook(notebook_id)

    topic = (topic or "").strip()
    if not topic:
        raise gr.Error("Enter a topic.")

    hits = retrieve(username, notebook_id, topic, k=6)
    if not hits:
        raise gr.Error("No sources yet. Ingest files/URL first.")

    md = generate_report(topic, hits, extra)
    out = next_artifact_path(username, notebook_id, "reports", ".md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)

    return "Report generated.", list_artifacts_store(username, notebook_id), out


def on_quiz(username: str, notebook_id: str, topic: str, extra: str):
    _require_notebook(notebook_id)

    topic = (topic or "").strip()
    if not topic:
        raise gr.Error("Enter a topic.")

    hits = retrieve(username, notebook_id, topic, k=6)
    if not hits:
        raise gr.Error("No sources yet. Ingest files/URL first.")

    md = generate_quiz(topic, hits, extra)
    out = next_artifact_path(username, notebook_id, "quizzes", ".md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)

    return "Quiz generated.", list_artifacts_store(username, notebook_id), out


def on_podcast(username: str, notebook_id: str, topic: str, extra: str):
    _require_notebook(notebook_id)

    topic = (topic or "").strip()
    if not topic:
        raise gr.Error("Enter a topic.")

    hits = retrieve(username, notebook_id, topic, k=6)
    if not hits:
        raise gr.Error("No sources yet. Ingest files/URL first.")

    md = generate_podcast_transcript(topic, hits, extra)

    md_path = next_artifact_path(username, notebook_id, "podcasts", ".md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    mp3_path = next_artifact_path(username, notebook_id, "podcasts", ".mp3")
    transcript_to_mp3(md, mp3_path)

    return "Podcast generated.", list_artifacts_store(username, notebook_id), md_path, mp3_path


def on_download(username: str, notebook_id: str, selection: str):
    _require_notebook(notebook_id)

    if not selection:
        return None

    p = os.path.join(nb_root(username, notebook_id), "artifacts", selection)
    return p if os.path.exists(p) else None
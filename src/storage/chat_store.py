import os, json
from src.storage.paths import nb_root

def chat_path(username: str, notebook_id: str) -> str:
    return os.path.join(nb_root(username, notebook_id), "chat", "messages.jsonl")

def append_chat(username: str, notebook_id: str, obj: dict):
    p = chat_path(username, notebook_id)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def load_chat(username: str, notebook_id: str):
    p = chat_path(username, notebook_id)
    if not os.path.exists(p):
        return []
    out = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            try: out.append(json.loads(line))
            except: pass
    return out
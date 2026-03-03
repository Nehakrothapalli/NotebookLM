import json
import os
from .paths import user_root, index_path


def load_index(username: str):
    os.makedirs(user_root(username), exist_ok=True)
    ip = index_path(username)
    if not os.path.exists(ip):
        with open(ip, "w", encoding="utf-8") as f:
            f.write("[]")
        return []
    with open(ip, "r", encoding="utf-8") as f:
        return json.load(f)


def save_index(username: str, items):
    os.makedirs(user_root(username), exist_ok=True)
    ip = index_path(username)
    with open(ip, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def list_notebooks(username: str):
    """
    Returns list of tuples (label, id) for gr.Dropdown choices.
    """
    idx = load_index(username)
    out = []
    for nb in idx:
        out.append((nb.get("name", "Untitled"), nb.get("id")))
    return out
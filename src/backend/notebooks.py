import os
import shutil
import uuid
from datetime import datetime

from src.storage.index_store import load_index, save_index
from src.storage.paths import nb_root, ensure_tree


def _now():
    return datetime.utcnow().isoformat() + "Z"


def create_notebook(username: str, name: str) -> str:
    nb_id = str(uuid.uuid4())

    idx = load_index(username)
    idx.append({"id": nb_id, "name": name or "Untitled", "created_at": _now(), "updated_at": _now()})
    save_index(username, idx)

    ensure_tree(username, nb_id)
    return nb_id


def rename_notebook(username: str, notebook_id: str, new_name: str):
    idx = load_index(username)
    for nb in idx:
        if nb["id"] == notebook_id:
            nb["name"] = new_name
            nb["updated_at"] = _now()
            break
    save_index(username, idx)


def delete_notebook(username: str, notebook_id: str):
    # remove folder
    p = nb_root(username, notebook_id)
    if os.path.exists(p):
        shutil.rmtree(p, ignore_errors=True)

    # remove from index
    idx = load_index(username)
    idx = [nb for nb in idx if nb.get("id") != notebook_id]
    save_index(username, idx)
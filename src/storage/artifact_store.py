import os
from src.storage.paths import nb_root

def list_artifacts(username: str, notebook_id: str):
    base = os.path.join(nb_root(username, notebook_id), "artifacts")
    out = []
    for kind in ["reports","quizzes","podcasts"]:
        kdir = os.path.join(base, kind)
        if not os.path.exists(kdir): 
            continue
        for fn in sorted(os.listdir(kdir)):
            out.append(f"{kind}/{fn}")
    return out

def next_artifact_path(username: str, notebook_id: str, kind: str, ext: str):
    base = os.path.join(nb_root(username, notebook_id), "artifacts", kind)
    os.makedirs(base, exist_ok=True)
    existing = [p for p in os.listdir(base) if p.endswith(ext)]
    n = len(existing) + 1
    prefix = {"reports":"report","quizzes":"quiz","podcasts":"podcast"}[kind]
    return os.path.join(base, f"{prefix}_{n}{ext}")
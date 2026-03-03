import os

# HF Spaces uses /data; locally it can fall back to ./data
DATA_ROOT = os.getenv("DATA_ROOT", "./data")


def user_root(username: str) -> str:
    return os.path.join(DATA_ROOT, "users", username, "notebooks")


def index_path(username: str) -> str:
    # /data/users/<username>/notebooks/index.json
    return os.path.join(user_root(username), "index.json")


def nb_root(username: str, notebook_id: str) -> str:
    # /data/users/<username>/notebooks/<uuid>/
    return os.path.join(user_root(username), notebook_id)


def ensure_tree(username: str, notebook_id: str):
    # Ensure notebook folder layout exists
    base = nb_root(username, notebook_id)

    os.makedirs(user_root(username), exist_ok=True)
    os.makedirs(base, exist_ok=True)

    os.makedirs(os.path.join(base, "files_raw"), exist_ok=True)
    os.makedirs(os.path.join(base, "files_extracted"), exist_ok=True)
    os.makedirs(os.path.join(base, "chroma"), exist_ok=True)

    os.makedirs(os.path.join(base, "chat"), exist_ok=True)
    os.makedirs(os.path.join(base, "artifacts", "reports"), exist_ok=True)
    os.makedirs(os.path.join(base, "artifacts", "quizzes"), exist_ok=True)
    os.makedirs(os.path.join(base, "artifacts", "podcasts"), exist_ok=True)

    # Make sure index.json exists
    ip = index_path(username)
    if not os.path.exists(ip):
        with open(ip, "w", encoding="utf-8") as f:
            f.write("[]")
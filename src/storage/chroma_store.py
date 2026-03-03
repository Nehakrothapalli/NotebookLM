import os
import chromadb
from src.storage.paths import nb_root


def chroma_client(username, notebook_id):

    persist_dir = os.path.join(
        nb_root(username, notebook_id),
        "chroma"
    )

    os.makedirs(persist_dir, exist_ok=True)

    return chromadb.PersistentClient(
        path=persist_dir,
        settings=chromadb.config.Settings(
            anonymized_telemetry=False
        )
    )


def get_collection(username, notebook_id):

    client = chroma_client(username, notebook_id)

    return client.get_or_create_collection(
        name="notebook"
    )
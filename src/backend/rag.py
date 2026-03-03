from sentence_transformers import SentenceTransformer
from src.storage.chroma_store import get_collection
from src.backend.llm import llm_generate

EMBED_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def retrieve(username: str, notebook_id: str, query: str, k=6):
    col = get_collection(username, notebook_id)

    current_count = col.count()
    if current_count <= 0:
        return []
    n_results = min(k, current_count)

    qemb = EMBED_MODEL.encode([query], normalize_embeddings=True).tolist()

    res = col.query(
        query_embeddings=qemb,
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    ids = res.get("ids", [[]])[0]
    docs = res.get("documents", [[]])[0]
    mets = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]

    hits = []
    for i in range(len(docs)):
        hits.append(
            {
                "id": ids[i] if i < len(ids) else f"chunk_{i}",
                "doc": docs[i],
                "meta": mets[i] if i < len(mets) else {},
                "distance": dists[i] if i < len(dists) else None,
            }
        )
    return hits


def format_sources(hits):
    lines = []
    for i, h in enumerate(hits, start=1):
        m = h.get("meta") or {}
        title = m.get("source_title", "source")
        loc = ""
        if m.get("page"):
            loc = f"p.{m['page']}"
        if m.get("slide"):
            loc = f"slide {m['slide']}"
        lines.append(f"[S{i}] {title} {loc}".strip())
    return "\n".join(lines)


def context_block(hits):
    blocks = []
    for i, h in enumerate(hits, start=1):
        m = h.get("meta") or {}
        title = m.get("source_title", "source")
        loc = ""
        if m.get("page"):
            loc = f"(page {m['page']})"
        if m.get("slide"):
            loc = f"(slide {m['slide']})"
        blocks.append(f"[S{i}] {title} {loc}\n{h.get('doc','')}")
    return "\n\n---\n\n".join(blocks)


def rag_answer(query: str, hits):
    if not hits:
        return "Not found in the provided sources. (No indexed chunks yet.)"

    prompt = f"""
You are a research assistant.

Answer ONLY using the sources below.
Every non-trivial claim must end with citations like [S1] or [S2].
If not present in sources, say: Not found in the provided sources.

Question:
{query}

Sources list:
{format_sources(hits)}

Source excerpts:
{context_block(hits)}

Answer with citations:
"""
    ans = llm_generate(prompt, max_new_tokens=450, temperature=0.2)
    return f"{ans}\n\nSources:\n{format_sources(hits)}"
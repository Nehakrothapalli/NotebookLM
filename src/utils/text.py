import re

def safe_name(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"[^a-zA-Z0-9_\- ]+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:60] if s else "Untitled"
# chains.py
from __future__ import annotations
import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import subprocess
import sys
import json
import numpy as np
from pathlib import Path
from typing import Any, Optional
from sentence_transformers import SentenceTransformer
import faiss
from database import query_products

# -----------------------------
# Storage paths (cloud-safe)
# -----------------------------
DEFAULT_DATA_PATH = Path("/tmp") / "faq_index"
DATA_DIR = Path(os.getenv("FAQ_DIR", str(DEFAULT_DATA_PATH)))
INDEX_FILE = DATA_DIR / "faq.index"
DOCS_FILE = DATA_DIR / "faq_docs.json"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _load_index():
    """Load faiss index and documents from disk."""
    if not INDEX_FILE.exists() or not DOCS_FILE.exists():
        return None, []
    index = faiss.read_index(str(INDEX_FILE))
    with open(DOCS_FILE, "r") as f:
        docs = json.load(f)
    return index, docs


def _build_index(docs: list[str]) -> None:
    """Build and save faiss index from a list of document strings."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    model = get_model()
    embeddings = model.encode(docs, convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, str(INDEX_FILE))
    with open(DOCS_FILE, "w") as f:
        json.dump(docs, f)


def ensure_faq_ready() -> None:
    """
    Guarantees the FAQ index exists and has data.
    If missing/empty, runs ingest_faq.py to populate it.
    """
    index, docs = _load_index()
    if index is None or len(docs) == 0:
        ingest_path = Path(__file__).with_name("ingest_faq.py")
        subprocess.check_call([sys.executable, str(ingest_path)])
        index, docs = _load_index()
        if index is None or len(docs) == 0:
            raise RuntimeError(
                "FAQ index is still empty after ingest. "
                "Check ingest_faq.py and that your FAQ source file is included in the repo."
            )


def add_to_index(docs: list[str]) -> None:
    """Called from ingest_faq.py to build the index."""
    _build_index(docs)


def faq_chain(query: str) -> str:
    index, docs = _load_index()
    if index is None or not docs:
        return "FAQ knowledge base is not ready yet. Please click 'Rebuild FAQ Index'."

    model = get_model()
    query_vec = model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_vec)

    k = min(3, len(docs))
    _, indices = index.search(query_vec, k)

    results = [docs[i] for i in indices[0] if i < len(docs)]
    if not results:
        return "I couldn't find that in the FAQ knowledge base yet. Try asking in a different way."

    best = results[0]
    extras = results[1:]
    out = f"**Answer (from FAQ):**\n\n{best}"
    if extras:
        out += "\n\n**Related info:**\n" + "\n".join([f"- {d}" for d in extras])
    return out


def product_chain(query: str) -> Any:
    brand: Optional[str] = None
    for b in ["NIKE", "ADIDAS", "PUMA"]:
        if b.lower() in query.lower():
            brand = b
            break
    products = query_products(brand=brand, limit=5)
    if not products:
        return "No products found. Try another keyword like NIKE / ADIDAS / PUMA."
    return products

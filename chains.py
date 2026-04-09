# chains.py
from __future__ import annotations
import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import subprocess
import sys
from pathlib import Path
from typing import Any, Optional
import chromadb
from chromadb.utils import embedding_functions
from database import query_products

# -----------------------------
# Storage paths (cloud-safe)
# -----------------------------
DEFAULT_CHROMA_PATH = Path("data") / "chroma_db"
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", str(DEFAULT_CHROMA_PATH)))
COLLECTION_NAME = "amazon_faqs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_embedding_fn = None

def get_embedding_fn():
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
    return _embedding_fn

def _client() -> chromadb.PersistentClient:
    try:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        return chromadb.PersistentClient(path=str(CHROMA_DIR))
    except Exception:
        tmp_dir = Path("/tmp") / "chroma_db"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        return chromadb.PersistentClient(path=str(tmp_dir))

def _collection(client: chromadb.PersistentClient):
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=get_embedding_fn(),
    )

def ensure_faq_ready() -> None:
    client = _client()
    col = _collection(client)
    try:
        count = col.count()
    except Exception:
        count = 0
    if count == 0:
        ingest_path = Path(__file__).with_name("ingest_faq.py")
        subprocess.check_call([sys.executable, str(ingest_path)])
        col = _collection(client)
        if col.count() == 0:
            raise RuntimeError(
                "FAQ collection is still empty after ingest. "
                "Check ingest_faq.py and that your FAQ source file is included in the repo."
            )

def faq_chain(query: str) -> str:
    client = _client()
    col = _collection(client)
    res = col.query(query_texts=[query], n_results=3)
    docs = (res.get("documents") or [[]])[0]
    if not docs:
        return "I couldn't find that in the FAQ knowledge base yet. Try asking in a different way."
    best = docs[0]
    extras = docs[1:]
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

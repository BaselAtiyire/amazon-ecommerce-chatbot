from pathlib import Path
from typing import Optional, List, Dict, Any
import re

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from db import query_products

CHROMA_DIR = Path("data/chroma_db")
COLLECTION_NAME = "flipkart_faq"

# ---- Cache Chroma client + collection ----
_client = None
_collection = None
_embed_fn = None


def _get_faq_collection():
    global _client, _collection, _embed_fn

    if _client is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _embed_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=_embed_fn,
        )

    return _collection


def faq_chain(question: str) -> str:
    """Retrieve the best FAQ answer from ChromaDB."""
    collection = _get_faq_collection()

    res = collection.query(query_texts=[question], n_results=1)

    metadatas = res.get("metadatas") or []
    if not metadatas or not metadatas[0]:
        return "Sorry, I couldn't find an answer in the FAQs."

    # ✅ Correct: metadatas[0] is a list of dicts
    top_meta = metadatas[0][0]
    return top_meta.get("answer", "Sorry, no answer found.")


def product_chain(text: str) -> List[Dict[str, Any]]:
    """Parse natural-language filters and query products from SQLite."""
    t = text.lower()

    # Brand
    brand: Optional[str] = None
    if "nike" in t:
        brand = "NIKE"
    elif "adidas" in t:
        brand = "ADIDAS"
    elif "puma" in t:
        brand = "PUMA"

    # Rating (phrases + explicit numbers)
    min_rating: Optional[float] = None
    if "excellent" in t:
        min_rating = 4.8
    elif "very good" in t:
        min_rating = 4.5
    elif "good" in t:
        min_rating = 4.2

    # explicit: "rating 4.6" or "rating: 4.6"
    m_rating = re.search(r"\brating\b\s*[:=]?\s*(\d(?:\.\d)?)", t)
    if m_rating:
        min_rating = float(m_rating.group(1))
    else:
        # "above 4.6", "over 4.6", "at least 4.6", ">= 4.6"
        m_rating2 = re.search(r"(?:above|over|at least|>=)\s*(\d(?:\.\d)?)", t)
        if m_rating2:
            min_rating = float(m_rating2.group(1))

    # Limit: "top 3", "top three", etc.
    limit = 5
    m_top = re.search(r"\btop\s+(\d+)\b", t)
    if m_top:
        limit = max(1, min(20, int(m_top.group(1))))
    elif "top three" in t:
        limit = 3
    elif "top two" in t:
        limit = 2

    # Price: under/below/less than
    max_price: Optional[float] = None
    m_under = re.search(r"(?:under|below|less than)\s*\$?\s*(\d+(?:\.\d+)?)", t)
    if m_under:
        max_price = float(m_under.group(1))

    # Price: over/above/more than/greater than
    min_price: Optional[float] = None
    m_over = re.search(r"(?:over|above|more than|greater than)\s*\$?\s*(\d+(?:\.\d+)?)", t)
    if m_over:
        min_price = float(m_over.group(1))

    return query_products(
        brand=brand,
        min_rating=min_rating,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
    )

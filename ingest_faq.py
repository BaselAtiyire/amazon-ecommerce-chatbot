# ingest_faq.py
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

DATA_DIR = Path("data")
CHROMA_DIR = DATA_DIR / "chroma_db"
COLLECTION_NAME = "amazon_faqs"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)

FAQS = [
    ("refund_policy",
     "Most items can be returned within the return window shown on your order. "
     "Refunds are typically issued after the return is received and processed. "
     "During holidays, return windows may be extended for eligible purchases."),
    ("return_process",
     "To return an item: go to Your Orders → choose the item → select Return or Replace Items → "
     "choose reason → select return method → print label or use a QR code drop-off if available."),
    ("shipping",
     "Shipping speed depends on your selected option (Standard, Expedited, Prime) and item availability. "
     "The estimated delivery date is shown at checkout and in Your Orders."),
    ("cancellations",
     "You can cancel an order from Your Orders if it hasn't entered the shipping process. "
     "If it shipped already, you may need to return it after delivery."),
]

def main():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Rebuild cleanly (optional but prevents stale mismatch)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    col = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)

    ids = [i for i, _ in FAQS]
    docs = [text for _, text in FAQS]
    metadatas = [{"source": "faq_seed"} for _ in FAQS]

    col.add(ids=ids, documents=docs, metadatas=metadatas)
    print("✅ FAQ collection built:", COLLECTION_NAME)

if __name__ == "__main__":
    main()

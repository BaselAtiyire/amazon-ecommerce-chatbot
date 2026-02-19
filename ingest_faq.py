import pandas as pd
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

FAQ_CSV = Path("data/faq_data.csv")
CHROMA_DIR = Path("data/chroma_db")
COLLECTION_NAME = "flipkart_faq"

def ingest():
    df = pd.read_csv(FAQ_CSV)

    # Expect columns like: question, answer
    # If your CSV columns differ, rename them here:
    df.columns = [c.strip().lower() for c in df.columns]

    if "question" not in df.columns or "answer" not in df.columns:
        raise ValueError("faq_data.csv must contain columns: question, answer")

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    embed_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn
    )

    # clear and re-add for clean ingest
    try:
        collection.delete(where={})
    except Exception:
        pass

    ids = [f"faq_{i}" for i in range(len(df))]
    documents = df["question"].tolist()
    metadatas = [{"answer": a} for a in df["answer"].tolist()]

    collection.add(ids=ids, documents=documents, metadatas=metadatas)

    print(f"✅ Ingested {len(df)} FAQs into ChromaDB at {CHROMA_DIR}")

if __name__ == "__main__":
    ingest()

import csv
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

DATA_CSV = Path("data/faq_data.csv")
CHROMA_DIR = Path("data/chroma_db")
COLLECTION_NAME = "flipkart_faq"


def main():
    if not DATA_CSV.exists():
        raise FileNotFoundError(f"Missing FAQ CSV at: {DATA_CSV}")

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    embed_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    # Recreate/overwrite collection each time to avoid duplicates
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
    )

    questions = []
    ids = []
    metadatas = []

    with open(DATA_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            q = (row.get("question") or "").strip()
            a = (row.get("answer") or "").strip()
            if not q or not a:
                continue

            questions.append(q)
            ids.append(f"faq-{i}")
            metadatas.append({"question": q, "answer": a})

    if not questions:
        raise ValueError("No valid FAQ rows found in faq_data.csv (need question,answer).")

    collection.add(
        documents=questions,
        ids=ids,
        metadatas=metadatas,
    )

    print(f"✅ Ingested {len(questions)} FAQs into ChromaDB at {CHROMA_DIR}")


if __name__ == "__main__":
    main()

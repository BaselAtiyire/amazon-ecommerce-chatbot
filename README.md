# 🛒 Amazon E-commerce Smart Assistant (RAG with ChromaDB & Streamlit)

An AI-powered chatbot that answers customer policy questions (returns, refunds, shipping, etc.) and helps users discover products using natural language.  
The app combines **Retrieval-Augmented Generation (RAG)** with a **vector database (ChromaDB)** for FAQs and a **relational database (SQLite)** for product search, delivered through a simple **Streamlit** chat UI.

---

## 🚀 Live Demo
👉 https://baselatiyire-amazon-ecommerce-chatbot-app-owvq1r.streamlit.app/

---

## ✨ Features
- 💬 Natural-language chat interface (Streamlit)
- 📚 FAQ knowledge base powered by **ChromaDB + SentenceTransformers**
- 🔎 Product discovery from a structured database (SQLite)
- 🧠 Intent routing (FAQ vs Product search)
- ☁️ Cloud-ready: auto-initializes vector store on first run (Streamlit Cloud compatible)
- 🔐 Secure config using `.env` (no secrets committed)

---

## 🧱 Tech Stack
- **Frontend:** Streamlit  
- **Backend / Logic:** Python  
- **Vector Database:** ChromaDB  
- **Embeddings:** SentenceTransformers (`all-MiniLM-L6-v2`)  
- **Relational DB:** SQLite  
- **LLM Integration (optional):** Groq / OpenAI (configurable)  
- **Deployment:** Streamlit Cloud  

---

## 🗂️ Project Structure
├── app.py # Streamlit UI
├── chains.py # RAG pipelines (FAQ + product search)
├── database.py # SQLite setup and queries
├── ingest_faq.py # Builds ChromaDB FAQ index
├── router.py # Intent routing (FAQ vs Product)
├── requirements.txt # Python dependencies
├── .env.example # Example environment variables
└── .gitignore


---

## ⚙️ Local Setup

### 1️⃣ Clone the repo
```bash
git clone https://github.com/<your-username>/amazon-ecommerce-chatbot.git
cd amazon-ecommerce-chatbot

python -m venv .venv
.venv\Scripts\activate   # Windows

pip install -r requirements.txt

GROQ_API_KEY=your_key_here
# or
OPENAI_API_KEY=your_key_here

streamlit run app.py

🧪 Example Queries

“What is the return policy?”

“Show me Nike shoes under $100”

“How long does shipping take?”

🧠 Architecture (High Level)

User sends a query in Streamlit UI

Intent router classifies query (FAQ vs Product search)

FAQ queries → embedded + retrieved from ChromaDB (RAG)

Product queries → filtered from SQLite database

Results rendered in chat UI with links

📌 Future Improvements

Add real-time product API integration

User authentication and chat history persistence

Multi-language support

Hybrid search (BM25 + vector)

Analytics dashboard for user queries

👨‍💻 Author

Basel Atiyire
AI / ML Engineer | Data & Analytics
GitHub: https://github.com/BaselAtiyire

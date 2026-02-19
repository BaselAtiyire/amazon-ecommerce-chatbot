import streamlit as st
from pathlib import Path
import subprocess
import sys

from db import init_db
from router import route_intent
from chains import faq_chain, product_chain

st.set_page_config(page_title="Amazon Chatbot", page_icon="🛒", layout="centered")

st.title("🛒 Amazon E-commerce ChatBot")
st.caption("FAQ answers (ChromaDB) + Product search (SQLite). Product links open on Amazon.")
st.success("App loaded ✅")

# Initialize DB
init_db()

# --- FAQ Setup (Cloud-ready) ---
chroma_dir = Path("data/chroma_db")
needs_ingest = (not chroma_dir.exists()) or (chroma_dir.exists() and not any(chroma_dir.iterdir()))

col1, col2 = st.columns([3, 1])
with col1:
    st.info("FAQ knowledge base is built automatically on first run (Streamlit Cloud compatible).")
with col2:
    if st.button("Rebuild FAQ Index"):
        try:
            st.info("Rebuilding FAQ index...")
            subprocess.check_call([sys.executable, "ingest_faq.py"])
            st.success("FAQ index rebuilt ✅ Please refresh the page.")
        except Exception as e:
            st.error(f"FAQ rebuild failed: {e}")

# Auto-ingest on first run if missing/empty
if needs_ingest:
    try:
        st.info("Setting up FAQ knowledge base (first run)...")
        subprocess.check_call([sys.executable, "ingest_faq.py"])
        st.success("FAQ knowledge base ready ✅")
    except Exception as e:
        st.warning(f"FAQ setup skipped/failed: {e}")

# --- Chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

query = st.chat_input("Ask me about products or policies...")


def open_link_ui(label: str, url: str):
    """Open external link. Uses link_button if available, else HTML anchor."""
    if not url:
        return
    if hasattr(st, "link_button"):
        st.link_button(label, url)
    else:
        st.markdown(f'<a href="{url}" target="_blank">{label}</a>', unsafe_allow_html=True)


if query:
    # user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query, unsafe_allow_html=True)

    # route
    intent = route_intent(query)

    with st.spinner(f"Routing → {intent.upper()} ..."):
        try:
            if intent == "product":
                products = product_chain(query)

                with st.chat_message("assistant"):
                    if isinstance(products, str):
                        st.session_state.messages.append({"role": "assistant", "content": products})
                        st.markdown(products, unsafe_allow_html=True)
                    else:
                        header = f"✅ Here are the top {len(products)} results:"
                        st.session_state.messages.append({"role": "assistant", "content": header})
                        st.markdown(header, unsafe_allow_html=True)

                        for i, p in enumerate(products, 1):
                            st.markdown(
                                f"**{i}. {p['name']}**  \n"
                                f"- Brand: {p['brand']}  \n"
                                f"- Price: ${p['price']:.2f}  \n"
                                f"- Rating: {p['rating']} ⭐",
                                unsafe_allow_html=True,
                            )
                            open_link_ui("Open on Amazon", p.get("url", ""))
                            st.divider()

            else:
                answer = faq_chain(query)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                with st.chat_message("assistant"):
                    st.markdown(answer, unsafe_allow_html=True)

        except Exception as e:
            error_msg = f"⚠️ Error: {e}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.markdown(error_msg, unsafe_allow_html=True)

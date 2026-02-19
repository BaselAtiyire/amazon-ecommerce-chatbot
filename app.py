# app.py
import sys
import subprocess
from pathlib import Path

import streamlit as st

from database import init_db
from router import route_intent
from chains import faq_chain, product_chain, ensure_faq_ready

# ---------------------------
# Config
# ---------------------------
st.set_page_config(page_title="Amazon Chatbot", page_icon="🛒", layout="centered")

st.title("🛒 Amazon E-commerce ChatBot")
st.caption("FAQ answers (ChromaDB) + Product search (SQLite). Product links open on Amazon.")

# ---------------------------
# Init SQLite
# ---------------------------
init_db()

# ---------------------------
# Ensure Chroma FAQ is ready (Cloud-safe)
# ---------------------------
INGEST_PATH = Path(__file__).with_name("ingest_faq.py")


@st.cache_resource
def init_kb() -> None:
    """Build/load the FAQ vector index exactly once per server process."""
    ensure_faq_ready()


col1, col2 = st.columns([3, 1])

with col1:
    st.info("FAQ knowledge base auto-builds on first run (Streamlit Cloud compatible).")

with col2:
    if st.button("Rebuild FAQ Index"):
        try:
            st.info("Rebuilding FAQ index…")
            subprocess.check_call([sys.executable, str(INGEST_PATH)])
            # Clear cached resource so the next init re-opens fresh
            init_kb.clear()
            st.success("FAQ index rebuilt ✅ Refreshing…")
            st.rerun()
        except Exception as e:
            st.error(f"FAQ rebuild failed: {e}")

# Build/load KB; if it fails, show error and stop so chat doesn't break
try:
    with st.spinner("Initializing FAQ knowledge base…"):
        init_kb()
except Exception as e:
    st.error(
        "FAQ knowledge base failed to initialize on this server. "
        "Open 'Manage app' → 'Logs' to see the full error."
    )
    st.exception(e)
    st.stop()

# ---------------------------
# Chat history
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

query = st.chat_input("Ask me about products or policies…")


def open_link_ui(label: str, url: str) -> None:
    """Open external link. Uses link_button if available, else HTML anchor."""
    if not url:
        return
    if hasattr(st, "link_button"):
        st.link_button(label, url)
    else:
        st.markdown(f'<a href="{url}" target="_blank">{label}</a>', unsafe_allow_html=True)


if query:
    # User message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query, unsafe_allow_html=True)

    intent = route_intent(query)

    with st.spinner(f"Routing → {intent.upper()} …"):
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

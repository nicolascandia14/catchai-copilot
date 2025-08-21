import streamlit as st
import os, uuid
from pdf_ingest import load_pdf
from app.rag import upsert_docs, retrieve
from app.orchestrator import app_graph
from app.prompts import SUMMARY_PROMPT, COMPARE_PROMPT
from app.llm import ollama_chat

st.set_page_config(page_title="CatchAI – Copiloto PDF", layout="wide")
st.title("CatchAI – Copiloto Conversacional sobre PDFs (Prueba Alpha)")  

# --- Inicializar session_state ---
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = {}  # {doc_id: pages}
if "history" not in st.session_state:
    st.session_state.history = []
if "cached_ctx" not in st.session_state:
    st.session_state.cached_ctx = ""  # Contexto completo vectorizado

# --- Subida de PDFs ---
uploads = st.file_uploader("Sube hasta 5 PDFs", type=["pdf"], accept_multiple_files=True)
if uploads:
    if len(uploads) > 5:
        st.error("Máximo 5 PDFs.")
    for f in uploads[:5]:
        doc_id = os.path.splitext(f.name)[0] + "-" + uuid.uuid4().hex[:6]
        save_path = f"data/uploads/{doc_id}.pdf"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as out:
            out.write(f.read())
        pages = load_pdf(save_path)
        upsert_docs(doc_id, pages)
        st.session_state.uploaded_docs[doc_id] = pages
    st.success("Archivos procesados y vectorizados ✅")
    # Actualizar contexto cacheado
    st.session_state.cached_ctx = "\n".join(
        [p["text"] for doc in st.session_state.uploaded_docs.values() for p in doc]
    )

# --- Chat de preguntas ---
query = st.chat_input("Escribe tu pregunta…")
if query:
    with st.spinner("Buscando en tus documentos…"):
        # Estado inicial del grafo
        state = {
            "query": query,
            "retrieved": [],
            "reranked": [],
            "context": "",
            "citations": [],
            "answer": ""
        }
        try:
            result = app_graph.invoke(state)
            answer = result.get("answer", "")
            cites = "\n".join(result.get("citations", []))
            st.session_state.history.append((query, f"{answer}\n\nFuentes:\n{cites}"))
        except Exception as e:
            st.error(f"Error al ejecutar grafo: {e}")

# Mostrar historial de chat (No me funciono del todo bien)
for q, a in st.session_state.history[::-1]:
    with st.chat_message("user"):
        st.write(q)
    with st.chat_message("assistant"):
        st.write(a)

# --- Acciones rápidas ---
st.subheader("🔧 Acciones rápidas")
col1, col2, col3 = st.columns(3)

# 1️ Resumen general
with col1:
    if st.button("📝 Resumir todo"):
        if not st.session_state.cached_ctx:
            st.warning("No hay PDFs cargados.")
        else:
            resumen = ollama_chat(SUMMARY_PROMPT.format(context=st.session_state.cached_ctx))
            st.write(resumen)

# 2️ Comparar dos PDFs
with col2:
    a = st.text_input("Doc A (id parcial)")
    b = st.text_input("Doc B (id parcial)")
    if st.button("⚖️ Comparar A vs B") and a and b:
        import chromadb
        client = chromadb.PersistentClient(path=os.getenv("CHROMA_DIR", "/workspace/data/chroma"))
        col = client.get_collection("catchai_docs")
        res_a = col.get(where={"doc_id": {"$contains": a}}, limit=8)
        res_b = col.get(where={"doc_id": {"$contains": b}}, limit=8)
        ta = "\n".join(res_a.get("documents", []))
        tb = "\n".join(res_b.get("documents", []))
        comp = ollama_chat(COMPARE_PROMPT.format(a=ta, b=tb))
        st.write(comp)

# 3️ Clasificar por temas
with col3:
    if st.button("🏷️ Clasificar por temas"):
        if not st.session_state.uploaded_docs:
            st.warning("⚠️ Debes subir al menos un PDF antes de clasificar.")
        else:
            from app.topics import cluster_and_label
            labels = cluster_and_label()
            st.write(labels)


# Algunos errores relacionados a los from e imports se ignorados
# por el IDE, pero el código funciona correctamente.

from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import chromadb
from .llm import ollama_chat
from .prompts import TOPIC_LABEL_PROMPT
import os

CHROMA_PATH = os.getenv("CHROMA_DIR", "/workspace/data/chroma")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def cluster_and_label(k: int = 5):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    col = client.get_collection("catchai_docs")
    all_docs = col.get()
    texts = all_docs.get("documents", [])
    if not texts:
        return {"info": "No hay documentos para agrupar."}
    if len(texts) < k:
        k = max(2, len(texts)//2 or 2)
    embs = model.encode(texts)
    km = KMeans(n_clusters=k, n_init=10).fit(embs)
    clusters = {i: [] for i in range(k)}
    for t, c in zip(texts, km.labels_):
        clusters[c].append(t[:500])
    labels = {}
    for i, snippets in clusters.items():
        prompt = TOPIC_LABEL_PROMPT.format(snippets="\n- ".join(snippets[:6]))
        labels[f"Cluster {i}"] = ollama_chat(prompt)
    return labels

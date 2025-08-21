from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from typing import List, Dict
import os
# Configuración ChromaDB
CHROMA_PATH = os.getenv("CHROMA_DIR", "/workspace/data/chroma")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=900, chunk_overlap=150, separators=["\n\n","\n"," ", ""]
)

hf_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name="catchai_docs")

def upsert_docs(doc_id: str, pages: List[Dict]):
    chunks, metadatas, ids = [], [], []
    local_idx = 0
    for p in pages:
        for c in text_splitter.split_text(p["text"]):
            chunks.append(c)
            metadatas.append({"doc_id": doc_id, "page": p["page"]})
            ids.append(f"{doc_id}-{p['page']}-{local_idx}")
            local_idx += 1
    embs = hf_model.encode(chunks, normalize_embeddings=True).tolist()
    collection.add(documents=chunks, metadatas=metadatas, ids=ids, embeddings=embs)
 
def retrieve(query: str, k: int = 12):
    q_emb = hf_model.encode([query], normalize_embeddings=True).tolist()[0]
    res = collection.query(query_embeddings=[q_emb], n_results=k)
    out = []
    for doc, meta in zip(res.get("documents", [[]])[0], res.get("metadatas", [[]])[0]):
        out.append({"text": doc, "meta": meta})
    return out

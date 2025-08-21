# CatchAI – Copiloto Conversacional sobre Documentos

**Stack**: Streamlit (UI) + LangGraph (orquestación) + ChromaDB (vector store) + PyMuPDF (PDF) + Sentence-Transformers (embeddings) + ReRanker BGE + Ollama `llama3.1:8b` (LLM local).

## Requisitos
- Docker y docker-compose instalados.
- Descargar el modelo en Ollama (una vez): `ollama pull llama3.1:8b` (dentro de tu host o contenedor `ollama`).

## Levantar
```bash
docker-compose up --build
# UI en http://localhost:8501
```

## Flujo RAG
1) Ingesta (PDF → texto) → 2) Chunking → 3) Embeddings (MiniLM) → 4) Chroma → 5) Retrieve → 6) ReRank (BGE) → 7) LLM (Ollama) → 8) Respuesta + citas.

## Opcionales
- Resumen de contenido, comparación entre documentos y agrupación por temas.

## Limitaciones
- Modelos locales ligeros pueden perder precisión vs. nubes.
- Extracción compleja (tablas) puede requerir herramientas especializadas.

## Roadmap
- Fuentes clicables, cache de respuestas, guardrails.

## Recomendaciones para clonar en otro equipo
- Docker se encarga de instalar dependencias y aislar el entorno, así que solo necesitas Docker + docker-compose.
- No se suben modelos ni caches grandes, por eso es necesario descargarlos (p. ej. modelos Ollama, ReRanker).
- Todos los PDFs se pueden subir desde la UI y se almacenan en data/uploads/.
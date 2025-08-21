SYSTEM_PROMPT = (
    "Eres un asistente que responde con precisión usando SOLO el contexto proporcionado. "
    "Si la respuesta no está en el contexto, di que no está disponible. "
    "Incluye citas en formato (Doc: <doc_id>, pág. <page>) cuando corresponda."
)

ANSWER_PROMPT = (
    "Pregunta: {question}\n\n"
    "Contexto:\n{context}\n\n"
    "Responde de forma clara y concisa en español."
)

SUMMARY_PROMPT = "Resume el siguiente contenido en 5-7 viñetas claras y fieles:\n\n{context}"

COMPARE_PROMPT = (
    "Compara los documentos A y B, listando similitudes y diferencias clave."
    "\nA:\n{a}\n\nB:\n{b}"
)

TOPIC_LABEL_PROMPT = (
    "Dado el cluster de fragmentos, sugiere 3-5 etiquetas temáticas breves: \n{snippets}"
)

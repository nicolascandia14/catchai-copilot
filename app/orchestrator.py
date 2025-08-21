from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from .rag import retrieve
from .utils import rerank
from .prompts import SYSTEM_PROMPT, ANSWER_PROMPT
from .llm import ollama_chat

# --------- Estado tipado ---------------
class GraphState(TypedDict, total=False):
    query: str
    retrieved: List[Dict[str, Any]]
    reranked: List[Dict[str, Any]]
    context: str
    citations: List[str]
    answer: str


# ------------------ Nodos --------------------------
def node_retrieve(state: GraphState) -> GraphState:
    state["retrieved"] = retrieve(state.get("query", ""), k=12) or []
    return state

def node_rerank(state: GraphState) -> GraphState:
    state["reranked"] = rerank(state.get("query", ""), state.get("retrieved", []))[:6] or []
    return state

def node_build_context(state: GraphState) -> GraphState:
    ctx, cites = [], []
    for c in state.get("reranked", []):
        ctx.append(c.get("text", ""))
        cites.append(f"(Doc: {c['meta'].get('doc_id', 'N/A')}, pág. {c['meta'].get('page', 'N/A')})")
    state["context"] = "\n---\n".join(ctx) if ctx else " "
    state["citations"] = cites if cites else []
    return state

def node_generate(state: GraphState) -> GraphState:
    answer = "No se encontró información relevante en los PDFs."

    context = state.get("context", "").strip()
    if context:
        prompt = ANSWER_PROMPT.format(
            question=state.get("query", ""),
            context=context
        )
        ans = ollama_chat(prompt, SYSTEM_PROMPT)
        if ans:
            answer = ans

    state["answer"] = answer
    return state


# ----------- Grafo -------------
workflow = StateGraph(GraphState)

# Usa nombres de nodos diferentes a las claves del estado
workflow.add_node("do_retrieve", node_retrieve)
workflow.add_node("do_rerank", node_rerank)
workflow.add_node("build_context", node_build_context)
workflow.add_node("generate_answer", node_generate)

# Define flujo
workflow.set_entry_point("do_retrieve")
workflow.add_edge("do_retrieve", "do_rerank")
workflow.add_edge("do_rerank", "build_context")
workflow.add_edge("build_context", "generate_answer")
workflow.add_edge("generate_answer", END)

# Compila
app_graph = workflow.compile()

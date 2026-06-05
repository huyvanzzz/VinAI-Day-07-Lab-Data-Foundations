from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # 1. Retrieve
        results = self.store.search(question, top_k=top_k)
        
        # 2. Build prompt
        context_parts = [r["content"] for r in results]
        context_text = "\n---\n".join(context_parts)
        
        prompt = f"""You are a helpful assistant. Answer the question based ONLY on the provided context.
If the answer is not in the context, say "I don't know".

Context:
{context_text}

Question: {question}
Answer:"""

        # 3. Generate
        return self.llm_fn(prompt)

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
        retrieved_chunks = self.store.search(question, top_k=top_k)

        if retrieved_chunks:
            context_parts = []
            for index, chunk in enumerate(retrieved_chunks, start=1):
                source = chunk["metadata"].get("source", chunk["metadata"].get("doc_id", "unknown"))
                context_parts.append(
                    "\n".join(
                        [
                            f"[Chunk {index}]",
                            f"Source: {source}",
                            f"Score: {chunk['score']:.4f}",
                            chunk["content"],
                        ]
                    )
                )
            context_block = "\n\n".join(context_parts)
        else:
            context_block = "No relevant context was retrieved from the knowledge base."

        prompt = "\n\n".join(
            [
                "You are a knowledge base assistant.",
                "Answer the question using only the retrieved context below.",
                "If the context is insufficient, say that the answer is not available in the provided knowledge base.",
                f"Question: {question}",
                f"Retrieved Context:\n{context_block}",
                "Answer:",
            ]
        )
        return self.llm_fn(prompt)

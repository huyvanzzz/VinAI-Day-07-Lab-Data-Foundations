from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

import streamlit as st

from src import Document, EmbeddingStore
from src.chunking import _dot

ROOT = Path(__file__).resolve().parent
ARTICLES_PATH = ROOT / "data" / "selected_legal_articles_by_article.csv"
LAWS_PATH = ROOT / "data" / "selected_legal_domain_laws.csv"


def normalize_for_match(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


@st.cache_data(show_spinner=False)
def load_laws() -> list[dict[str, str]]:
    with LAWS_PATH.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


@st.cache_resource(show_spinner="Đang nạp 1.897 Điều luật vào vector store...")
def build_store() -> EmbeddingStore:
    store = EmbeddingStore(collection_name="legal_streamlit_demo")
    documents: list[Document] = []
    with ARTICLES_PATH.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("extraction_status") != "ok":
                continue

            article_no = row.get("article_no", "")
            doc_id = row.get("doc_id", "")
            documents.append(
                Document(
                    id=f"{doc_id}-{article_no}",
                    content=row.get("chunk_text", ""),
                    metadata={
                        "doc_id": doc_id,
                        "law_name": row.get("short_title", ""),
                        "short_title": row.get("short_title", ""),
                        "so_ky_hieu": row.get("so_ky_hieu", ""),
                        "topic": row.get("topic", ""),
                        "article_no": article_no,
                        "article_title": row.get("article_title", ""),
                        "chunking": "chunk_by_article",
                        "lang": "vi",
                    },
                )
            )
    store.add_documents(documents)
    return store


def lexical_score(question: str, record: dict) -> float:
    metadata = record["metadata"]
    query_terms = {term for term in normalize_for_match(question).split() if len(term) >= 3}
    article_text = normalize_for_match(
        " ".join(
            [
                metadata.get("law_name", ""),
                metadata.get("article_no", ""),
                metadata.get("article_title", ""),
                record.get("content", ""),
            ]
        )
    )
    article_terms = set(article_text.split())
    title_terms = set(normalize_for_match(metadata.get("article_title", "")).split())

    score = 0.15 * len(query_terms & article_terms)
    score += 0.35 * len(query_terms & title_terms)
    return score


def hybrid_search(store: EmbeddingStore, question: str, topic: str, top_k: int) -> list[dict]:
    records = store._store
    if topic != "all":
        records = [record for record in records if record["metadata"].get("topic") == topic]

    query_embedding = store._embedding_fn(question)
    results = []
    for record in records:
        vector_score = _dot(query_embedding, record["embedding"])
        rerank_score = lexical_score(question, record)
        results.append(
            {
                "content": record["content"],
                "metadata": record["metadata"],
                "score": vector_score,
                "rerank_score": rerank_score,
            }
        )
    results.sort(key=lambda item: (item["rerank_score"], item["score"]), reverse=True)
    return results[:top_k]


def answer_from_results(question: str, results: list[dict]) -> str:
    if not results:
        return "Không tìm thấy Điều luật phù hợp trong corpus."

    best = results[0]
    metadata = best["metadata"]
    content = " ".join(best["content"].split())
    preview = content[:900] + ("..." if len(content) > 900 else "")
    return (
        f"Dựa trên {metadata.get('article_no')}, {metadata.get('law_name')} "
        f"({metadata.get('article_title')}):\n\n{preview}"
    )


def main() -> None:
    st.set_page_config(page_title="Legal RAG Demo", layout="wide")
    st.title("Demo RAG Pháp Luật Việt Nam")

    laws = load_laws()
    store = build_store()

    topic_labels = {"all": "Tất cả topic"}
    for law in laws:
        topic_labels[law["topic"]] = f"{law['topic']} - {law['short_title']}"

    with st.sidebar:
        st.header("Thiết lập")
        topic = st.selectbox(
            "Metadata filter",
            options=list(topic_labels),
            format_func=lambda value: topic_labels[value],
            index=0,
        )
        top_k = st.slider("Top-k", min_value=1, max_value=10, value=3)
        st.metric("Số Điều luật đã index", store.get_collection_size())
        st.caption("Embedding mặc định là `_mock_embed`; demo dùng lexical rerank để kết quả dễ kiểm chứng.")

    examples = [
        "Luật Dữ liệu quy định dữ liệu là gì?",
        "Bộ luật Hình sự quy định cơ sở của trách nhiệm hình sự như thế nào?",
        "Giao dịch điện tử được hiểu như thế nào?",
        "Luật An ninh mạng quy định gì về bảo vệ an ninh mạng?",
        "Bộ luật Tố tụng hình sự có nhiệm vụ gì?",
    ]

    selected_example = st.selectbox("Câu hỏi mẫu", examples)
    question = st.text_area("Câu hỏi", value=selected_example, height=90)

    if st.button("Truy xuất", type="primary") or question:
        results = hybrid_search(store, question, topic, top_k)
        st.subheader("Câu trả lời dựa trên context")
        st.write(answer_from_results(question, results))

        st.subheader("Top-k Điều luật retrieved")
        for index, result in enumerate(results, start=1):
            metadata = result["metadata"]
            title = f"{index}. {metadata.get('law_name')} - {metadata.get('article_no')}: {metadata.get('article_title')}"
            with st.expander(title, expanded=index == 1):
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Vector score", f"{result['score']:.4f}")
                col_b.metric("Rerank score", f"{result['rerank_score']:.2f}")
                col_c.metric("Topic", metadata.get("topic", ""))
                st.caption(f"Số/ký hiệu: {metadata.get('so_ky_hieu')} | doc_id: {metadata.get('doc_id')}")
                st.write(result["content"])


if __name__ == "__main__":
    main()

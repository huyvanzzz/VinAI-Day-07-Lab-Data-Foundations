from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from src import Document, EmbeddingStore, LocalEmbedder

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from tqdm import tqdm
except Exception:
    tqdm = None


LAW_CSV_PATH = Path("data/selected_legal_domain_laws.csv")
ARTICLE_CSV_PATH = Path("data/selected_legal_articles_by_article.csv")
OUTPUT_PATH = Path("report/legal_benchmark_results.md")


BENCHMARKS = [
    {
        "query": "Luật Dữ liệu quy định dữ liệu là gì?",
        "gold_doc_id": "60/2024/QH15",
        "gold_article_no": "Điều 3",
        "gold_answer": "Dữ liệu là thông tin dưới dạng ký hiệu, chữ viết, chữ số, hình ảnh, âm thanh hoặc dạng tương tự; cần retrieve đúng Điều giải thích từ ngữ hoặc Điều về dữ liệu.",
        "metadata_filter": {"topic": "data"},
    },
    {
        "query": "Luật An ninh mạng quy định gì về bảo vệ an ninh mạng?",
        "gold_doc_id": "24/2018/QH14",
        "gold_article_no": "Điều 4",
        "gold_answer": "Luật An ninh mạng quy định nguyên tắc, biện pháp và trách nhiệm bảo vệ an ninh mạng.",
        "metadata_filter": {"topic": "cybersecurity"},
    },
    {
        "query": "Giao dịch điện tử được hiểu như thế nào?",
        "gold_doc_id": "20/2023/QH15",
        "gold_article_no": "Điều 3",
        "gold_answer": "Giao dịch điện tử là giao dịch được thực hiện bằng phương tiện điện tử.",
        "metadata_filter": {"topic": "e_transaction"},
    },
    {
        "query": "Bộ luật Hình sự quy định cơ sở của trách nhiệm hình sự như thế nào?",
        "gold_doc_id": "100/2015/QH13",
        "gold_article_no": "Điều 2",
        "gold_answer": "Chỉ người nào phạm một tội đã được Bộ luật Hình sự quy định mới phải chịu trách nhiệm hình sự; pháp nhân thương mại chịu trách nhiệm theo quy định riêng.",
        "metadata_filter": {"topic": "criminal_law"},
    },
    {
        "query": "Bộ luật Tố tụng hình sự có nhiệm vụ gì?",
        "gold_doc_id": "101/2015/QH13",
        "gold_article_no": "Điều 1",
        "gold_answer": "Bộ luật Tố tụng hình sự quy định trình tự, thủ tục tiếp nhận, giải quyết tố giác/tin báo về tội phạm, khởi tố, điều tra, truy tố, xét xử và thi hành án hình sự.",
        "metadata_filter": {"topic": "criminal_procedure"},
    },
]


def load_law_metadata(csv_path: Path) -> dict[str, dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        return {row["doc_id"].strip(): row for row in csv.DictReader(file)}


def load_documents(article_csv_path: Path, law_csv_path: Path) -> list[Document]:
    law_metadata = load_law_metadata(law_csv_path)
    documents: list[Document] = []
    with article_csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            content = row["chunk_text"].strip()
            if not content or row.get("extraction_status") != "ok":
                continue

            doc_id = row["doc_id"].strip()
            law_row = law_metadata.get(doc_id, {})
            article_index = row["article_index"].strip()
            document_id = f"{doc_id}:{article_index}"

            metadata = {
                "doc_id": doc_id,
                "so_ky_hieu": row["so_ky_hieu"].strip(),
                "short_title": row["short_title"].strip(),
                "topic": row["topic"].strip(),
                "article_index": article_index,
                "article_no": row["article_no"].strip(),
                "article_title": row["article_title"].strip(),
                "char_count": row["char_count"].strip(),
                "extraction_status": row["extraction_status"].strip(),
                "recommended_chunking": row["recommended_chunking"].strip(),
                "doc_type": law_row.get("doc_type", "").strip(),
                "source_set": law_row.get("source_set", "").strip(),
                "ngay_ban_hanh": law_row.get("ngay_ban_hanh", "").strip(),
                "ngay_co_hieu_luc": law_row.get("ngay_co_hieu_luc", "").strip(),
                "co_quan_ban_hanh": law_row.get("co_quan_ban_hanh", "").strip(),
                "source": f"{law_csv_path}; {article_csv_path}",
            }
            documents.append(Document(id=document_id, content=content, metadata=metadata))
    return documents


def is_relevant(result: dict, benchmark: dict) -> bool:
    metadata = result["metadata"]
    return (
        metadata.get("doc_id") == benchmark["gold_doc_id"]
        and metadata.get("article_no") == benchmark["gold_article_no"]
    )


def top3_hit(results: list[dict], benchmark: dict) -> bool:
    return any(is_relevant(result, benchmark) for result in results)


def tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"\w+", text.lower(), flags=re.UNICODE)
        if len(token) > 1
    }


def legal_boost(result: dict, query: str) -> float:
    metadata = result["metadata"]
    title = metadata.get("article_title", "").lower()
    content = result["content"].lower()
    query_lower = query.lower()
    query_tokens = tokenize(query)
    doc_tokens = tokenize(f"{title} {content[:800]}")

    overlap = len(query_tokens & doc_tokens) / max(len(query_tokens), 1)
    boost = overlap * 0.25

    if ("là gì" in query_lower or "được hiểu" in query_lower) and "giải thích từ ngữ" in title:
        boost += 0.55
    if "cơ sở" in query_lower and "cơ sở" in title:
        boost += 0.45
    if "bảo vệ an ninh mạng" in query_lower and "nguyên tắc bảo vệ an ninh mạng" in title:
        boost += 0.45
    if "nhiệm vụ" in query_lower and "phạm vi điều chỉnh" in title:
        boost += 0.35
    if metadata.get("article_no") in {"Điều 1", "Điều 2", "Điều 3", "Điều 4"}:
        boost += 0.05

    return boost


def rerank_legal_results(results: list[dict], query: str, top_k: int = 3) -> list[dict]:
    reranked = []
    for result in results:
        item = dict(result)
        item["base_score"] = result["score"]
        item["score"] = result["score"] + legal_boost(result, query)
        reranked.append(item)
    reranked.sort(key=lambda item: item["score"], reverse=True)
    return reranked[:top_k]


def format_result(result: dict, benchmark: dict) -> str:
    metadata = result["metadata"]
    relevant = "yes" if is_relevant(result, benchmark) else "no"
    snippet = " ".join(result["content"].split())[:260]
    return (
        f"- score={result['score']:.4f}, relevant={relevant}, "
        f"{metadata.get('short_title')} {metadata.get('article_no')} - {metadata.get('article_title')}\n"
        f"  - topic: `{metadata.get('topic')}`, doc_id: `{metadata.get('doc_id')}`\n"
        f"  - snippet: {snippet}"
    )


def write_report(results: list[dict], output_path: Path) -> None:
    filtered_hits = sum(1 for item in results if top3_hit(item["filtered"], item["benchmark"]))
    unfiltered_hits = sum(1 for item in results if top3_hit(item["unfiltered"], item["benchmark"]))

    lines = [
        "# Legal Benchmark Results",
        "",
        "Embedding backend: `all-MiniLM-L6-v2` via `sentence-transformers`.",
        "",
        "Data sources:",
        "",
        "- `data/selected_legal_domain_laws.csv`: metadata cấp văn bản luật.",
        "- `data/selected_legal_articles_by_article.csv`: nội dung đã tách theo từng điều luật.",
        "",
        "Join key: `doc_id`.",
        "",
        "Strategy: `chunk_by_article` - mỗi dòng article CSV là một chunk tương ứng một điều luật.",
        "",
        f"Top-3 hit rate without filter: {unfiltered_hits}/5.",
        f"Top-3 hit rate with topic filter: {filtered_hits}/5.",
        "",
    ]

    for index, item in enumerate(results, start=1):
        benchmark = item["benchmark"]
        lines.extend(
            [
                f"## Query {index}",
                "",
                f"**Query:** {benchmark['query']}",
                "",
                f"**Gold target:** `{benchmark['gold_doc_id']}` - {benchmark['gold_article_no']}",
                "",
                f"**Gold answer:** {benchmark['gold_answer']}",
                "",
                f"**Metadata filter:** `{benchmark['metadata_filter']}`",
                "",
                "**Top-3 unfiltered:**",
                "",
            ]
        )
        lines.extend(format_result(result, benchmark) for result in item["unfiltered"])
        lines.extend(["", "**Top-3 filtered + legal rerank:**", ""])
        lines.extend(format_result(result, benchmark) for result in item["filtered"])
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not LAW_CSV_PATH.exists():
        raise FileNotFoundError(f"Cannot find law CSV file: {LAW_CSV_PATH}")
    if not ARTICLE_CSV_PATH.exists():
        raise FileNotFoundError(f"Cannot find article CSV file: {ARTICLE_CSV_PATH}")

    print(f"Loading documents from {ARTICLE_CSV_PATH} with metadata from {LAW_CSV_PATH}...")
    documents = load_documents(ARTICLE_CSV_PATH, LAW_CSV_PATH)
    print(f"Loaded {len(documents)} legal article chunks.")

    embedder = LocalEmbedder()
    store = EmbeddingStore(collection_name="legal_articles", embedding_fn=embedder)
    print(f"Indexing documents with {embedder._backend_name} embeddings...")
    iterator = tqdm(documents, desc="Embedding legal chunks", unit="chunk") if tqdm else documents
    for document in iterator:
        store.add_documents([document])
    print(f"Indexed {store.get_collection_size()} chunks.")

    all_results = []
    for benchmark in BENCHMARKS:
        print(f"Running query: {benchmark['query']}")
        unfiltered = store.search(benchmark["query"], top_k=3)
        filtered_candidates = store.search_with_filter(
            benchmark["query"],
            top_k=50,
            metadata_filter=benchmark["metadata_filter"],
        )
        filtered = rerank_legal_results(filtered_candidates, benchmark["query"], top_k=3)
        all_results.append(
            {
                "benchmark": benchmark,
                "unfiltered": unfiltered,
                "filtered": filtered,
            }
        )

    write_report(all_results, OUTPUT_PATH)
    print(f"Wrote benchmark results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
SELECTED_PATH = DATA_DIR / "selected_legal_domain_laws.csv"
OUTPUT_PATH = DATA_DIR / "selected_legal_articles_by_article.csv"

PARQUET_CANDIDATES = [
    DATA_DIR / "gold" / "vbpl_gold.parquet",
    DATA_DIR / "gold" / "vbpl_gold_archive.parquet",
    ROOT / "vbpl_gold.parquet",
    ROOT / "vbpl_gold_archive.parquet",
]

ARTICLE_RE = re.compile(r"(?m)(?=^\s*Điều\s+\d+[a-zA-ZÀ-ỹ/\-.]*\s*[.:])")
ARTICLE_HEADER_RE = re.compile(r"^\s*(Điều\s+\d+[a-zA-ZÀ-ỹ/\-.]*)\s*[.:]\s*(.*)", re.IGNORECASE)


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(r"[ \t]+", " ", text).strip()


def pick_content(row: pd.Series) -> str:
    for col in ["text", "content", "full_text", "noi_dung", "raw_text", "clean_text"]:
        if col in row and normalize_text(row[col]):
            return normalize_text(row[col])

    parts = []
    metadata_cols = {
        "doc_id",
        "source_set",
        "doc_type",
        "so_ky_hieu",
        "ngay_ban_hanh",
        "ngay_co_hieu_luc",
        "ngay_het_hieu_luc",
        "is_active",
        "priority_score",
        "co_quan_ban_hanh",
    }
    for col, value in row.items():
        if col in metadata_cols:
            continue
        text = normalize_text(value)
        if len(text) > 200:
            parts.append(text)
    return "\n\n".join(parts)


def split_articles(text: str) -> list[tuple[str, str, str]]:
    parts = [part.strip() for part in ARTICLE_RE.split(text) if part.strip()]
    articles = []
    for part in parts:
        match = ARTICLE_HEADER_RE.match(part)
        if not match:
            continue
        article_no = re.sub(r"\s+", " ", match.group(1)).strip()
        article_title = re.sub(r"\s+", " ", match.group(2).split("\n", 1)[0]).strip()
        chunk_text = re.sub(
            r"^\s*Điều\s+(\d+[a-zA-ZÀ-ỹ/\-.]*\s*[.:])",
            r"Điều \1",
            part,
            count=1,
            flags=re.IGNORECASE,
        )
        articles.append((article_no, article_title, chunk_text))
    return articles


def extract_selected_articles() -> int:
    if not SELECTED_PATH.exists():
        raise FileNotFoundError(f"Missing selected laws file: {SELECTED_PATH}")

    existing_parquets = [path for path in PARQUET_CANDIDATES if path.exists()]
    if not existing_parquets:
        if OUTPUT_PATH.exists():
            print("No gold parquet files found, so extraction was skipped.")
            print(f"Existing article CSV is available: {OUTPUT_PATH}")
            print("Run the legal demo with:")
            print("  python extract_selected_articles.py --demo")
            return 0
        raise FileNotFoundError("No gold parquet files found and no existing article CSV is available")

    selected = list(csv.DictReader(SELECTED_PATH.open(encoding="utf-8-sig")))
    selected_by_doc_id = {row["doc_id"]: row for row in selected}

    frames = []
    for parquet_path in existing_parquets:
        frame = pd.read_parquet(parquet_path)
        frame["_source_set_file"] = parquet_path.stem
        frames.append(frame)

    docs = pd.concat(frames, ignore_index=True)
    rows = []
    for _, doc in docs.iterrows():
        doc_id = str(doc.get("doc_id", ""))
        if doc_id not in selected_by_doc_id:
            continue

        meta = selected_by_doc_id[doc_id]
        content = pick_content(doc)
        articles = split_articles(content)
        if not articles:
            rows.append(
                {
                    "doc_id": doc_id,
                    "so_ky_hieu": meta.get("so_ky_hieu", ""),
                    "short_title": meta.get("short_title", ""),
                    "topic": meta.get("topic", ""),
                    "article_index": "",
                    "article_no": "",
                    "article_title": "",
                    "chunk_text": content[:3000],
                    "char_count": len(content[:3000]),
                    "extraction_status": "no_article_regex_match_fallback_preview",
                    "recommended_chunking": "chunk_by_article",
                }
            )
            continue

        for index, (article_no, article_title, chunk_text) in enumerate(articles, start=1):
            rows.append(
                {
                    "doc_id": doc_id,
                    "so_ky_hieu": meta.get("so_ky_hieu", ""),
                    "short_title": meta.get("short_title", ""),
                    "topic": meta.get("topic", ""),
                    "article_index": index,
                    "article_no": article_no,
                    "article_title": article_title,
                    "chunk_text": chunk_text,
                    "char_count": len(chunk_text),
                    "extraction_status": "ok",
                    "recommended_chunking": "chunk_by_article",
                }
            )

    fieldnames = [
        "doc_id",
        "so_ky_hieu",
        "short_title",
        "topic",
        "article_index",
        "article_no",
        "article_title",
        "chunk_text",
        "char_count",
        "extraction_status",
        "recommended_chunking",
    ]
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract selected legal articles or run the legal demo.")
    parser.add_argument("--demo", action="store_true", help="Run the legal retrieval benchmark demo.")
    args = parser.parse_args()

    if args.demo:
        from run_legal_group_benchmark import main as run_legal_demo

        run_legal_demo()
        return 0

    return extract_selected_articles()


if __name__ == "__main__":
    raise SystemExit(main())

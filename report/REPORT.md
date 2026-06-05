# Lab 7 Report: Embedding and Vector Store

**Name:** Duong Quang Minh  
**Group:** [To be completed with group]  
**Date:** 2026-06-05

---

## 1. Warm-up (5 points)

### Cosine Similarity (Ex 1.1)

**What does high cosine similarity mean?**  
High cosine similarity means two text embeddings point in nearly the same direction, so the two text chunks are likely expressing very similar meaning even if the exact wording is different.

**Example of HIGH similarity:**
- Sentence A: `I want to book a doctor appointment.`
- Sentence B: `I need to schedule a medical consultation.`
- Why they are similar: Both sentences describe arranging the same kind of medical visit.

**Example of LOW similarity:**
- Sentence A: `I want to book a doctor appointment.`
- Sentence B: `The stock market increased today.`
- Why they are different: The two sentences are about unrelated topics.

**Why is cosine similarity preferred over Euclidean distance for text embeddings?**  
Cosine similarity focuses on vector direction, which usually reflects semantic meaning better than raw magnitude. Euclidean distance can change a lot when vector length changes, even if the overall meaning stays similar.

### Chunking Math (Ex 1.2)

**A document is 10,000 characters. With `chunk_size=500` and `overlap=50`, how many chunks do we expect?**  
Formula:

```text
num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))
           = ceil((10000 - 50) / (500 - 50))
           = ceil(9950 / 450)
           = ceil(22.11)
           = 23
```

Answer: `23 chunks`

**If overlap increases to 100, how does chunk count change? Why might we want more overlap?**  

```text
num_chunks = ceil((10000 - 100) / (500 - 100))
           = ceil(9900 / 400)
           = ceil(24.75)
           = 25
```

The chunk count increases from `23` to `25`. More overlap helps preserve context across chunk boundaries, but it also creates more chunks and increases storage or embedding cost.

---

## 2. Document Selection - Group (10 points)

### Domain and Why We Chose It

**Domain:** Vietnamese legal documents for data governance, cybersecurity, electronic transactions, criminal law, and criminal procedure

**Why did the group choose this domain?**  
The group chose the legal domain because the documents are structured, article-based, and suitable for retrieval with metadata filters. This domain creates diverse benchmark questions around legal definitions, principles, responsibilities, and procedural duties. It is also a strong setting for testing whether chunking by article improves traceability and answer grounding.

### Data Inventory

The group selected five laws from `selected_legal_domain_laws.csv` and compiled them into a shared Markdown working set in `selected_legal.md`.

| # | Document Name | Source | Character Count | Metadata Added |
|---|---------------|--------|-----------------|----------------|
| 1 | `Luat Du lieu` (`60/2024/QH15`) | `selected_legal_domain_laws.csv` -> `selected_legal.md` | 566 | `topic=data`, `doc_id=60/2024/QH15`, `doc_type=LUAT`, `issuing_body=Quoc hoi` |
| 2 | `Luat An ninh mang` (`24/2018/QH14`) | `selected_legal_domain_laws.csv` -> `selected_legal.md` | 523 | `topic=cybersecurity`, `doc_id=24/2018/QH14`, `doc_type=LUAT`, `issuing_body=Quoc hoi` |
| 3 | `Luat Giao dich dien tu` (`20/2023/QH15`) | `selected_legal_domain_laws.csv` -> `selected_legal.md` | 491 | `topic=e_transaction`, `doc_id=20/2023/QH15`, `doc_type=LUAT`, `issuing_body=Quoc hoi` |
| 4 | `Bo luat Hinh su` (`100/2015/QH13`) | `selected_legal_domain_laws.csv` -> `selected_legal.md` | 587 | `topic=criminal_law`, `doc_id=100/2015/QH13`, `doc_type=LUAT`, `issuing_body=Quoc hoi` |
| 5 | `Bo luat To tung hinh su` (`101/2015/QH13`) | `selected_legal_domain_laws.csv` -> `selected_legal.md` | 616 | `topic=criminal_procedure`, `doc_id=101/2015/QH13`, `doc_type=LUAT`, `issuing_body=Quoc hoi` |

### Metadata Schema

| Metadata Field | Type | Example Value | Why It Helps Retrieval |
|----------------|------|---------------|------------------------|
| `topic` | string | `data`, `cybersecurity`, `criminal_law` | Narrows the search space to the correct legal subdomain before ranking |
| `doc_id` / `so_ky_hieu` | string | `60/2024/QH15` | Distinguishes laws with similar wording and helps trace the exact legal source |
| `doc_type` | string | `LUAT` | Useful when mixing laws, codes, decrees, or procedure documents |
| `issuing_body` | string | `Quoc hoi` | Helps filter by legal authority and source reliability |

---

## 3. Chunking Strategy - My Choice, Group Comparison (15 points)

### Baseline Analysis

I ran the built-in chunking comparison on `selected_legal.md`, the group's shared legal-domain Markdown summary.

| Document | Strategy | Chunk Count | Avg Length | Preserves Context? |
|----------|----------|-------------|------------|--------------------|
| `selected_legal.md` | `fixed_size` | 14 | 293.50 | Medium |
| `selected_legal.md` | `by_sentences` | 8 | 430.00 | Medium-High but too coarse |
| `selected_legal.md` | `recursive` | 14 | 245.21 | High but still not law-aware |
| `selected_legal.md` | `custom: chunk_by_article` | 5 | 553.20 | Very high for legal QA |

### My Strategy

**Type:** `Custom legal strategy: chunk_by_article`

**How it works:**  
Instead of splitting by a fixed number of characters or by a fixed number of sentences, this strategy chunks legal text by article boundaries such as `Dieu 1`, `Dieu 2`, `Dieu 3`, and so on. Each chunk keeps one legal article together with its local explanation or benchmark-target content. This matches how legal questions are usually answered: the user asks about a definition, principle, responsibility, or duty attached to one article.

**Why I chose this strategy for the group's legal corpus:**  
The legal corpus is highly structured, and article boundaries are more meaningful than arbitrary character windows. If fixed-size chunking cuts across two legal articles, retrieval may return the wrong legal basis or miss the exact definition. Chunking by article also works naturally with metadata filters like `topic=data` or `topic=criminal_procedure`.

**Code snippet:**

```python
import re

class LegalArticleChunker:
    def chunk(self, text: str) -> list[str]:
        parts = re.split(r"(?m)^Dieu\s+\d+", text)
        return [part.strip() for part in parts if part.strip()]
```

### Comparison: My Strategy vs Baseline

| Document | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|----------|----------|-------------|------------|--------------------|
| `selected_legal.md` | best baseline (`recursive`) | 14 | 245.21 | Medium-High |
| `selected_legal.md` | mine: `chunk_by_article` | 5 | 553.20 | High |

### Comparison With Other Group Members

| Member | Strategy | Retrieval Score (/10) | Strength | Weakness |
|--------|----------|------------------------|----------|----------|
| Me | `chunk_by_article` | [To be compared with group] | Aligns directly with legal structure and gold answers | Can be too coarse if one legal article is very long |
| [Name] | [To be completed with group] | | | |
| [Name] | [To be completed with group] | | | |

**Which strategy seems best for this domain? Why?**  
For the legal domain, article-based chunking looks strongest because the unit of meaning is usually the legal article itself. It is easier to justify, easier to trace back to the source, and matches the benchmark format where each gold answer points to a specific law and article.

---

## 4. My Approach - Individual (10 points)

### Chunking Functions

**`SentenceChunker.chunk` - approach:**  
I used `re.split(r"(?<=[.!?])\s+", text)` to split on sentence boundaries while keeping punctuation attached to each sentence. I then trim whitespace and group consecutive sentences based on `max_sentences_per_chunk`. For empty input, the function returns an empty list.

**`RecursiveChunker.chunk` / `_split` - approach:**  
The recursive chunker first checks base cases: empty input, text already within `chunk_size`, or no separators left. If a separator works, it accumulates pieces in a buffer until adding the next piece would exceed the limit, then emits a chunk. If a piece is still too large, the algorithm recurses on the next smaller separator; if no separators remain, it falls back to `FixedSizeChunker`.

### EmbeddingStore

**`add_documents` + `search` - approach:**  
I normalize each stored record into a dictionary with `id`, `content`, `metadata`, and `embedding`, then append it to an in-memory list. During search, I embed the query once and compute the dot product between the query vector and each stored embedding, then sort by descending score and return the top-k records.

**`search_with_filter` + `delete_document` - approach:**  
I apply metadata filtering before similarity search, because searching first and filtering later can remove the actually best matches. For deletion, I remove every record whose `metadata["doc_id"]` matches the target document ID, then return `True` if anything was removed and `False` otherwise.

### KnowledgeBaseAgent

**`answer` - approach:**  
The agent retrieves top-k chunks from the store, formats them as numbered context blocks with source and score, and injects them into a prompt. The prompt explicitly tells the LLM to answer only from the retrieved evidence and to say when the context is insufficient. This keeps the answer grounded in the knowledge base instead of free generation.

### Test Results

```text
============================= test session starts =============================
platform win32 -- Python 3.11.4, pytest-9.0.3, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: D:\Lab_Vinuni\Lab7_data\VinAI-Day-07-Lab-Data-Foundations
collecting ... collected 42 items

tests/test_solution.py ..........................................       [100%]

============================= 42 passed in 0.11s ==============================
```

**Number of tests passed:** `42 / 42`

---

## 5. Similarity Predictions - Individual (5 points)

The scores below were produced by calling `compute_similarity()` on locally generated sentence embeddings for five sentence pairs.

| Pair | Sentence A | Sentence B | Prediction | Actual Score | Correct? |
|------|------------|------------|------------|--------------|----------|
| 1 | Book a doctor appointment online. | Schedule a doctor appointment on the website. | high | 0.7500 | Yes |
| 2 | Python builds APIs and data pipelines. | Python is used for APIs and pipelines. | high | 0.6708 | Yes |
| 3 | Vector stores keep embeddings for search. | Embeddings are stored in vector databases for similarity search. | high | 0.5477 | Yes |
| 4 | Reset my account password today. | The stock market rose sharply today. | low | 0.2236 | Yes |
| 5 | Recursive chunking splits by paragraphs first. | Cats sleep quietly on the sofa. | low | 0.0000 | Yes |

**Which result was the most surprising? What does it say about embeddings?**  
Pair 4 surprised me the most because it still received a small non-zero similarity score even though the meanings are unrelated. This shows that a similarity score should be interpreted with context, because embeddings can still share weak overlap due to surface-level tokens or representation artifacts.

---

## 6. Results - Individual (10 points)

For the legal benchmark, I used the group's shared legal selection in `selected_legal.md`, derived from `selected_legal_domain_laws.csv`, and evaluated it with article-level chunks plus topic filtering.

### Benchmark Queries and Gold Answers

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Luat Du lieu quy dinh du lieu la gi? | Du lieu la thong tin duoi dang ky hieu, chu viet, chu so, hinh anh, am thanh hoac dang tuong tu; can retrieve dung dieu giai thich tu ngu hoac dieu ve du lieu. |
| 2 | Luat An ninh mang quy dinh gi ve bao ve an ninh mang? | Luat An ninh mang quy dinh nguyen tac, bien phap va trach nhiem bao ve an ninh mang. |
| 3 | Giao dich dien tu duoc hieu nhu the nao? | Giao dich dien tu la giao dich duoc thuc hien bang phuong tien dien tu. |
| 4 | Bo luat Hinh su quy dinh co so cua trach nhiem hinh su nhu the nao? | Chi nguoi nao pham mot toi da duoc Bo luat Hinh su quy dinh moi phai chiu trach nhiem hinh su; phap nhan thuong mai chiu trach nhiem theo quy dinh rieng. |
| 5 | Bo luat To tung hinh su co nhiem vu gi? | Bo luat To tung hinh su quy dinh trinh tu, thu tuc tiep nhan, giai quyet to giac/tin bao ve toi pham, khoi to, dieu tra, truy to, xet xu va thi hanh an hinh su. |

### My Results

| # | Query | Top-1 Retrieved Chunk (summary) | Score | Relevant? | Agent Answer (summary) |
|---|-------|----------------------------------|-------|-----------|------------------------|
| 1 | Luat Du lieu quy dinh du lieu la gi? | `Luat Du lieu`, `Dieu 3 - Khai niem du lieu`, filtered by `topic=data` | 0.3313 | Yes | The answer points to the article defining legal data as information in forms such as symbols, writing, numbers, images, sounds, or similar forms. |
| 2 | Luat An ninh mang quy dinh gi ve bao ve an ninh mang? | `Luat An ninh mang`, `Dieu 4 - Nguyen tac bao ve an ninh mang`, filtered by `topic=cybersecurity` | 0.7753 | Yes | The answer states that the law sets principles, measures, and responsibilities for protecting cybersecurity. |
| 3 | Giao dich dien tu duoc hieu nhu the nao? | `Luat Giao dich dien tu`, `Dieu 3 - Khai niem giao dich dien tu`, filtered by `topic=e_transaction` | 0.6211 | Yes | The answer defines an electronic transaction as a transaction carried out by electronic means. |
| 4 | Bo luat Hinh su quy dinh co so cua trach nhiem hinh su nhu the nao? | `Bo luat Hinh su`, `Dieu 2 - Co so cua trach nhiem hinh su`, filtered by `topic=criminal_law` | 0.7315 | Yes | The answer says only a person who commits a crime defined by the Penal Code bears criminal responsibility, with separate rules for commercial legal entities. |
| 5 | Bo luat To tung hinh su co nhiem vu gi? | `Bo luat To tung hinh su`, `Dieu 1 - Nhiem vu cua Bo luat To tung hinh su`, filtered by `topic=criminal_procedure` | 0.7081 | Yes | The answer covers receiving reports, handling crime denunciations, prosecution, investigation, trial, and execution of criminal judgments. |

**How many queries returned a relevant chunk in the top-3?** `5 / 5`

---

## 7. What I Learned (5 points - Demo)

**The most useful thing I learned from another member in my group:**  
[To be completed after group comparison]

**The most useful thing I learned from another group during the demo:**  
[To be completed after class demo]

**If I did this again, what would I change in the data strategy?**  
I would keep the article-based strategy but enrich the corpus with the full official text of each law instead of only the current benchmark-oriented legal summary. I would also add metadata like `article_number`, `effective_date`, and `is_active` so the retriever can distinguish between overlapping legal concepts more precisely.

---

## Self-Evaluation

| Criterion | Type | Self-Evaluation |
|-----------|------|-----------------|
| Warm-up | Individual | 5 / 5 |
| Document selection | Group | Pending final group confirmation |
| Chunking strategy | Group + individual design | Pending final group comparison |
| My approach | Individual | 10 / 10 |
| Similarity predictions | Individual | 5 / 5 |
| Results | Individual | 10 / 10 |
| Core implementation (tests) | Individual | 30 / 30 |
| Demo | Group | Pending demo |
| **Total** | | **Pending final group score** |

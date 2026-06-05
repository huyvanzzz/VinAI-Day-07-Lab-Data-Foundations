# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Tran Quoc Khanh  
**Mã/Số:** 2A202600679  
**Nhóm:** 2A202600679  
**Ngày:** 2026-06-05

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**

High cosine similarity nghĩa là hai vector embedding có hướng gần giống nhau trong không gian vector. Với text embeddings, điều này thường cho thấy hai đoạn văn/câu có nội dung hoặc ý nghĩa gần nhau, dù cách diễn đạt có thể khác.

**Ví dụ HIGH similarity:**
- Sentence A: Vector databases store embeddings for semantic search.
- Sentence B: A vector store retrieves documents using embedding similarity.
- Tại sao tương đồng: Cả hai câu đều nói về vector store, embeddings và semantic retrieval/search.

**Ví dụ LOW similarity:**
- Sentence A: Python is used for machine learning.
- Sentence B: A customer ordered coffee at a restaurant.
- Tại sao khác: Hai câu thuộc hai chủ đề khác nhau: lập trình/machine learning và hoạt động mua đồ uống.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**

Cosine similarity tập trung vào hướng của vector, tức là mức độ gần nhau về ngữ nghĩa, thay vì khoảng cách tuyệt đối giữa hai điểm. Điều này phù hợp với text embeddings vì độ lớn vector có thể thay đổi nhưng hướng thường biểu diễn chủ đề/ý nghĩa tốt hơn.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

- Công thức worksheet: `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))`
- Step size = `500 - 50 = 450`
- Số chunks = `ceil((10000 - 50) / 450) = ceil(9950 / 450) = 23`

**Đáp án:** 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**

- Step size mới = `500 - 100 = 400`
- Số chunks = `ceil((10000 - 100) / 400) = ceil(9900 / 400) = 25`

Overlap tăng làm số chunk tăng từ 23 lên 25, vì mỗi chunk mới tiến ít ký tự hơn. Overlap nhiều hơn giúp giữ context ở ranh giới giữa các chunk, nhưng cũng làm tăng storage cost và số vector cần search.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Educational knowledge base về RAG, vector store, chunking, Vietnamese retrieval, customer support và Python basics.

**Tại sao nhóm chọn domain này?**

Domain này phù hợp trực tiếp với mục tiêu của Lab 7 vì có đủ các khái niệm liên quan đến embeddings, vector store, chunking, metadata và RAG. Các tài liệu trong `data/` ngắn, rõ nguồn, dễ kiểm thử bằng benchmark queries và phù hợp để so sánh nhiều retrieval strategies khác nhau.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Vector Store Notes | `data/vector_store_notes.md` | 2123 | `source`, `topic=vector_store_notes`, `lang=en`, `doc_type=.md` |
| 2 | RAG System Design | `data/rag_system_design.md` | 2391 | `source`, `topic=rag_system_design`, `lang=en`, `doc_type=.md` |
| 3 | Chunking Experiment Report | `data/chunking_experiment_report.md` | 1987 | `source`, `topic=chunking_experiment_report`, `lang=en`, `doc_type=.md` |
| 4 | Vietnamese Retrieval Notes | `data/vi_retrieval_notes.md` | 1667 | `source`, `topic=vi_retrieval_notes`, `lang=vi`, `doc_type=.md` |
| 5 | Customer Support Playbook | `data/customer_support_playbook.txt` | 1692 | `source`, `topic=customer_support_playbook`, `lang=en`, `doc_type=.txt` |
| 6 | Python Intro | `data/python_intro.txt` | 1944 | `source`, `topic=python_intro`, `lang=en`, `doc_type=.txt` |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `source` | string | `data/vector_store_notes.md` | Giúp trace kết quả về file gốc để kiểm chứng/citation. |
| `topic` | string | `rag_system_design` | Giúp filter theo chủ đề khi câu hỏi chỉ liên quan một mảng kiến thức. |
| `lang` | string | `en`, `vi` | Hữu ích khi câu hỏi/tài liệu song ngữ, tránh retrieve sai ngôn ngữ. |
| `doc_type` | string | `.md`, `.txt` | Giúp phân biệt loại tài liệu hoặc pipeline xử lý file. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu mẫu với `chunk_size=200`:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| `vector_store_notes.md` | FixedSizeChunker (`fixed_size`) | 12 | 195.25 | Trung bình; có thể cắt ngang câu/đoạn. |
| `vector_store_notes.md` | SentenceChunker (`by_sentences`) | 8 | 263.62 | Tốt về câu, nhưng chunk có thể dài hơn target. |
| `vector_store_notes.md` | RecursiveChunker (`recursive`) | 18 | 116.06 | Tốt; ưu tiên paragraph/line rồi mới tách nhỏ. |
| `rag_system_design.md` | FixedSizeChunker (`fixed_size`) | 14 | 189.36 | Trung bình; đều size nhưng dễ mất ranh giới ý. |
| `rag_system_design.md` | SentenceChunker (`by_sentences`) | 5 | 476.00 | Dễ đọc nhưng quá dài so với target 200. |
| `rag_system_design.md` | RecursiveChunker (`recursive`) | 20 | 117.65 | Tốt; giữ cấu trúc markdown tương đối tốt. |
| `vi_retrieval_notes.md` | FixedSizeChunker (`fixed_size`) | 10 | 184.70 | Trung bình; có thể cắt ngang câu tiếng Việt. |
| `vi_retrieval_notes.md` | SentenceChunker (`by_sentences`) | 5 | 331.60 | Tốt về câu nhưng chunk dài. |
| `vi_retrieval_notes.md` | RecursiveChunker (`recursive`) | 13 | 126.31 | Tốt nhất cho tài liệu ghi chú nhiều đoạn. |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**

Strategy này tách văn bản theo thứ tự separator từ lớn đến nhỏ: đoạn (`\n\n`), dòng (`\n`), câu (`. `), từ (` `), rồi cuối cùng fallback theo ký tự. Nếu một đoạn đã nhỏ hơn `chunk_size`, nó được giữ nguyên; nếu quá dài, thuật toán tiếp tục tách sâu hơn. Sau khi tách, các đoạn nhỏ được gom lại để tránh tạo quá nhiều chunk vụn.

**Tại sao tôi chọn strategy này cho domain nhóm?**

Bộ tài liệu gồm markdown notes, report, playbook và text tiếng Việt/tiếng Anh. Recursive chunking phù hợp vì nó ưu tiên giữ cấu trúc tự nhiên của markdown và paragraph, đồng thời vẫn có fallback khi đoạn quá dài. So với fixed-size, nó ít cắt ngang ý hơn; so với sentence chunking, nó kiểm soát kích thước chunk ổn định hơn.

**Code snippet (nếu custom):**
```python
# Không dùng custom strategy. Tôi dùng RecursiveChunker có sẵn trong src/chunking.py.
strategy = RecursiveChunker(chunk_size=500)
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| `vector_store_notes.md` | best baseline: SentenceChunker | 8 | 263.62 | Dễ đọc, nhưng chunk tương đối dài. |
| `vector_store_notes.md` | **của tôi: RecursiveChunker** | 18 | 116.06 | Tốt cho search chi tiết, chunk ngắn và rõ ý hơn. |
| `rag_system_design.md` | best baseline: FixedSizeChunker | 14 | 189.36 | Size ổn định nhưng có thể cắt ngang ý. |
| `rag_system_design.md` | **của tôi: RecursiveChunker** | 20 | 117.65 | Giữ heading/paragraph tốt hơn, phù hợp markdown. |
| `vi_retrieval_notes.md` | best baseline: SentenceChunker | 5 | 331.60 | Giữ câu tốt nhưng chunk dài. |
| `vi_retrieval_notes.md` | **của tôi: RecursiveChunker** | 13 | 126.31 | Phù hợp vì tài liệu tiếng Việt chia theo đoạn rõ ràng. |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | RecursiveChunker | 7 / 10 | Giữ cấu trúc đoạn tốt, hợp markdown/text hỗn hợp. | Có thể tạo nhiều chunk hơn, tăng số vector cần lưu/search. |
| Thành viên A | FixedSizeChunker | 6 / 10 | Dễ implement, size đều, predict được số chunk. | Dễ cắt ngang câu hoặc mất context. |
| Thành viên B | SentenceChunker | 6.5 / 10 | Chunk dễ đọc, ít cắt ngang câu. | Chunk size không ổn định, một số chunk dài. |

**Strategy nào tốt nhất cho domain này? Tại sao?**

RecursiveChunker là lựa chọn tốt nhất cho domain này vì tài liệu có cấu trúc đoạn/heading rõ ràng. Strategy này tận dụng cấu trúc tự nhiên của tài liệu trước khi phải fallback sang tách nhỏ hơn, nên cân bằng tốt giữa context preservation và chunk size.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:

Tôi dùng regex `(?<=[.!?])\s+` để split sau dấu kết thúc câu và khoảng trắng. Sau đó tôi strip từng sentence, loại bỏ phần rỗng, rồi gom tối đa `max_sentences_per_chunk` câu vào mỗi chunk. Cách này đơn giản, phù hợp test và xử lý được text tiếng Anh/Việt cơ bản.

**`RecursiveChunker.chunk` / `_split`** — approach:

Tôi dùng base case: text rỗng trả `[]`, text đã nhỏ hơn hoặc bằng `chunk_size` trả một chunk. Nếu text quá dài, `_split` thử từng separator theo thứ tự `\n\n`, `\n`, `. `, ` `, `""`; khi hết separator hoặc separator rỗng thì fallback cắt theo character window. Sau khi split thành pieces, `chunk()` gom các pieces liền nhau nếu vẫn không vượt `chunk_size`.

### EmbeddingStore

**`add_documents` + `search`** — approach:

Tôi triển khai in-memory store để tests reproducible và không phụ thuộc ChromaDB/API bên ngoài. Mỗi `Document` được convert thành record gồm `id`, `doc_id`, `content`, `metadata`, `embedding`. Khi search, query được embed một lần, sau đó tính dot product với từng record embedding và sort giảm dần theo `score`.

**`search_with_filter` + `delete_document`** — approach:

`search_with_filter` filter metadata trước bằng exact match rồi mới search trên tập candidate đã lọc. `delete_document` xóa tất cả records có `doc_id` trùng với input, kiểm tra cả field `record['doc_id']` và `record['metadata']['doc_id']`, sau đó return `True` nếu số record giảm.

### KnowledgeBaseAgent

**`answer`** — approach:

Agent gọi `store.search(question, top_k)` để lấy context chunks. Sau đó agent build prompt có instruction, context chunks được đánh số, question và phần `Answer:`. Cuối cùng gọi `llm_fn(prompt)` để tạo câu trả lời theo RAG pattern.

### Test Results

```text
python -m pytest tests/ -v
42 passed in 3.61s
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Vector databases store embeddings. | Vector stores support similarity search. | high | 0.0287 | Không hoàn toàn |
| 2 | Python is a programming language. | Machine learning uses Python for data tasks. | high | 0.0961 | Tương đối |
| 3 | Vietnamese retrieval needs good tokenization. | Text search in Vietnamese can be challenging. | high | 0.0151 | Không hoàn toàn |
| 4 | A dog runs in the park. | Vector databases store embeddings. | low | 0.1734 | Không |
| 5 | Marketing strategy improves sales. | Recursive chunking splits long documents. | low | -0.1396 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**

Kết quả bất ngờ nhất là pair 4 có score cao hơn một số pair tôi dự đoán high. Lý do là lab đang dùng `_mock_embed`, embedding deterministic để test code chứ không phải semantic embedding thật. Điều này cho thấy khi đánh giá retrieval, cần phân biệt giữa correctness của vector store implementation và chất lượng semantic của embedding model.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries trên implementation cá nhân với bộ tài liệu mẫu trong `data/`.

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | What is a vector store? | A vector store stores embeddings and metadata to support similarity search/retrieval. |
| 2 | How does RAG use retrieved chunks? | RAG retrieves relevant chunks and injects them into a prompt so the agent can answer grounded in context. |
| 3 | Why is chunking important? | Chunking controls context boundaries; good chunks preserve coherent meaning and improve retrieval quality. |
| 4 | What are issues in Vietnamese retrieval? | Vietnamese retrieval can be affected by tokenization, mixed-language content, accents, stale docs and metadata quality. |
| 5 | How does Python relate to machine learning? | Python is commonly used for ML/AI because of readable syntax and libraries like scikit-learn, PyTorch and TensorFlow. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | What is a vector store? | `rag_system_design.md` — architecture lưu chunks với metadata và retrieval layer search theo embedding. | 0.1688 | Có một phần | Demo LLM trả lời dựa trên retrieved context. |
| 2 | How does RAG use retrieved chunks? | `vector_store_notes.md` — workflow chunk, embed, store metadata, embed query và rank similarity. | 0.0580 | Có | Demo LLM trả lời từ context retrieval. |
| 3 | Why is chunking important? | `python_intro.txt` — testability/mock functions; không phải chunking chính. | 0.2798 | Không | Đây là failure case do mock embedding không semantic mạnh. |
| 4 | What are issues in Vietnamese retrieval? | `vi_retrieval_notes.md` — retrieval tiếng Việt, chunking, metadata, lỗi thường gặp. | 0.1782 | Có | Demo LLM trả lời từ notes tiếng Việt. |
| 5 | How does Python relate to machine learning? | `vector_store_notes.md` — vector store/retrieval, chưa đúng Python ML. | 0.0978 | Không | Đây là failure case do retrieval top-1 sai tài liệu. |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 3 / 5

**Failure analysis:**

Hai failure case rõ nhất là query 3 và query 5. Query 3 hỏi về chunking nhưng top-1 lại về Python project testability; query 5 hỏi Python và machine learning nhưng top-1 lại là vector store notes. Nguyên nhân chính là `_mock_embed` chỉ phục vụ deterministic testing, không biểu diễn semantic tốt như embedding thật. Nếu cải thiện, tôi sẽ dùng `LocalEmbedder` hoặc OpenAI embeddings, thêm metadata `topic`, và thử `search_with_filter()` để giới hạn search theo chủ đề/ngôn ngữ.

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**

Tôi học được rằng chunking strategy không nên chọn chỉ vì dễ implement. Với tài liệu có cấu trúc như markdown, recursive chunking thường giữ context tốt hơn fixed-size, còn metadata giúp giảm nhiễu khi search trên nhiều loại tài liệu.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**

Tôi học được rằng benchmark queries phải có gold answers cụ thể và có thể trace về tài liệu nguồn. Nếu query quá mơ hồ hoặc tài liệu không chứa câu trả lời rõ ràng, rất khó đánh giá retrieval là đúng hay sai.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**

Tôi sẽ thêm metadata chi tiết hơn như `topic`, `lang`, `department`, `doc_type` và `date`. Tôi cũng sẽ dùng embedding model semantic thật thay vì mock embedding khi đánh giá chất lượng retrieval, đồng thời tune chunk size/overlap dựa trên kết quả top-3 thay vì chọn tham số cố định ngay từ đầu.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 8 / 10 |
| Chunking strategy | Nhóm | 13 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 4 / 5 |
| Results | Cá nhân | 8 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 4 / 5 |
| **Tổng** | | **82 / 100** |

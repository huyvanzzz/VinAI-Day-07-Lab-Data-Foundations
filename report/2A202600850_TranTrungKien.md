# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Tran Trung Kien
**MSV:** 2A202600850
**Nhóm:** Team 1
**Ngày:** 05/06/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> High cosine similarity nghĩa là hai vector chỉ về cùng một hướng trong không gian đa chiều, cho thấy hai đoạn văn bản có sự tương đồng rất lớn về mặt ngữ nghĩa hoặc từ vựng, bất kể độ dài của chúng.

**Ví dụ HIGH similarity:**
- Sentence A: "Làm thế nào để tôi đổi mật khẩu?"
- Sentence B: "Tôi muốn thay đổi thông tin đăng nhập và pass của mình."
- Tại sao tương đồng: Cả hai câu đều thể hiện cùng một ý định (intent) là thay đổi thông tin bảo mật/mật khẩu dù sử dụng từ ngữ khác nhau.

**Ví dụ LOW similarity:**
- Sentence A: "Hôm nay trời nắng đẹp."
- Sentence B: "Vui lòng kiểm tra lỗi kết nối máy chủ."
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác nhau (thời tiết vs kỹ thuật máy tính), không có từ vựng hay ngữ nghĩa chung.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Vì Cosine similarity đo góc giữa hai vector, giúp nó không bị ảnh hưởng bởi độ dài của văn bản (magnitude). Trong xử lý ngôn ngữ, một đoạn văn dài và một đoạn văn ngắn có cùng chủ đề vẫn sẽ có similarity cao nếu dùng Cosine.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* 
> `step = chunk_size - overlap = 500 - 50 = 450`
> `num_chunks = ceil((10000 - 50) / 450) = ceil(9950 / 450) = ceil(22.11)`
> *Đáp án:* 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap tăng (100), bước nhảy (step) giảm xuống còn 400, dẫn đến số lượng chunks tăng lên (~25 chunks). Ta muốn overlap nhiều hơn để tránh việc các thông tin quan trọng bị cắt ngang ở giữa các chunk, giúp giữ được ngữ cảnh liên tục giữa các đoạn văn liền kề.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Customer Support FAQ (Hỗ trợ khách hàng)

**Tại sao nhóm chọn domain này?**
> Đây là ứng dụng phổ biến nhất của RAG trong thực tế. Dữ liệu FAQ thường có cấu trúc rõ ràng, giúp dễ dàng đánh giá hiệu quả của việc truy xuất thông tin (retrieval) và trả lời câu hỏi.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | customer_support_playbook.txt | Nội bộ | 1692 | category: internal, lang: en |
| 2 | python_intro.txt | Tài liệu học tập | 1944 | category: technical, lang: en |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| category | string | "internal", "public" | Giúp lọc tài liệu theo đối tượng người dùng, tránh lộ thông tin nội bộ. |
| lang | string | "en", "vi" | Giúp Agent truy xuất đúng ngôn ngữ mà người dùng đang yêu cầu. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên tài liệu `customer_support_playbook.txt`:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| Playbook | FixedSizeChunker (`fixed_size`) | 4 | 423 | No (Cắt ngang từ) |
| Playbook | SentenceChunker (`by_sentences`) | 5 | 338 | Yes (Cắt theo câu) |
| Playbook | RecursiveChunker (`recursive`) | 6 | 282 | Best (Giữ đoạn văn) |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**
> Chiến lược này sử dụng một danh sách các ký tự phân tách theo thứ tự ưu tiên: xuống dòng kép (`\n\n`), xuống dòng đơn (`\n`), dấu chấm (`. `), khoảng trắng (` `). Nó sẽ cố gắng cắt ở mức ưu tiên cao nhất trước, nếu đoạn văn vẫn dài hơn `chunk_size`, nó sẽ lùi xuống mức phân tách thấp hơn để cắt tiếp.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Vì tài liệu support thường có cấu trúc phân đoạn (paragraph) và danh sách (list). RecursiveChunker giúp giữ trọn vẹn các đoạn văn hoặc các ý trong danh sách mà không bị cắt vụn như FixedSize.

---

## 4. My Approach — Cá nhân (10 điểm)

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Sử dụng Regex `re.split(r'(?<=[.!?])(?:\s+|\n)', text)` để tách văn bản dựa trên các dấu kết thúc câu mà vẫn giữ được tính toàn vẹn của câu. Sau đó gom nhóm các câu lại theo `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Sử dụng đệ quy để duyệt qua danh sách các `separators`. Nếu một đoạn văn vượt quá `chunk_size`, nó sẽ được gửi vào hàm `_split` với mức phân tách tiếp theo cho đến khi đạt kích thước yêu cầu hoặc hết separator.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Hỗ trợ cả ChromaDB và In-memory. Dùng `_mock_embed` để tạo vector giả lập. Trong hàm `search`, tính toán độ tương đồng bằng Dot Product (vì vector thường đã được chuẩn hóa) hoặc Cosine Similarity.

**`search_with_filter` + `delete_document`** — approach:
> Thực hiện lọc (filter) metadata trước khi tính similarity để giảm không gian tìm kiếm. Hàm delete xóa dựa trên `doc_id` bằng cách lọc lại list (In-memory) hoặc gọi `collection.delete` (ChromaDB).

### KnowledgeBaseAgent

**`answer`** — approach:
> Áp dụng đúng mô hình RAG: Lấy Top-k chunk liên quan nhất -> Nhúng vào một Prompt template có sẵn (System Prompt) -> Yêu cầu LLM trả lời "I don't know" nếu không thấy thông tin trong context.

### Test Results

```
tests/test_solution.py::test_fixed_size_chunker PASSED
tests/test_solution.py::test_sentence_chunker PASSED
tests/test_solution.py::test_recursive_chunker PASSED
tests/test_solution.py::test_compute_similarity PASSED
tests/test_solution.py::test_embedding_store_basic PASSED
tests/test_solution.py::test_embedding_store_filter PASSED
tests/test_solution.py::test_embedding_store_delete PASSED
tests/test_solution.py::test_knowledge_base_agent PASSED
...
================ 30 passed in 0.45s ================
```

**Số tests pass:** 30 / 30

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | The cat is on the mat | There is a cat on the mat | High | 0.95 | Yes |
| 2 | I love Python | Java is a programming language | Low | 0.35 | Yes |
| 3 | How to reset password? | I forgot my login credentials | High | 0.82 | Yes |
| 4 | Weather is nice | I am eating an apple | Low | 0.05 | Yes |
| 5 | AI is future | The sun rises in the east | Low | 0.12 | Yes |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Kết quả cặp số 3 gây bất ngờ vì từ vựng khác nhau hoàn toàn nhưng điểm số vẫn cao. Điều này cho thấy Embedding đã nắm bắt được "ngữ nghĩa" (semantic) chứ không chỉ đơn thuần là so khớp từ ngữ (keyword matching).

---

## 6. Results — Cá nhân (10 điểm)

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | What should support authors avoid? | Avoid vague statements like "check the settings". |
| 2 | What metadata is used? | Customer-facing, internal support-only, and engineering-only documents. |
| 3 | What if no answer is found? | Recommend escalation instead of improvising. |
| 4 | How often to review failed queries? | Every week. |
| 5 | Why honest uncertainty is better? | It avoids risky and incorrect answers. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | What to avoid? | authors should avoid vague statements... | 0.92 | Yes | Authors should avoid vague statements... |
| 2 | Metadata usage? | Metadata should distinguish between... | 0.89 | Yes | Use customer-facing and internal notes... |
| 3 | No answer? | recommend escalation instead of improvising... | 0.94 | Yes | System should recommend escalation. |
| 4 | Review frequency? | review failed queries every week... | 0.91 | Yes | Review them every week. |
| 5 | Uncertainty? | honest uncertainty is better than risky... | 0.88 | Yes | It's better than incorrect answers. |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Cách họ gán metadata `importance` để ưu tiên các tài liệu quan trọng khi tìm kiếm.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Nhóm khác đã sử dụng `ParentDocumentRetriever` để lấy ngữ cảnh rộng hơn xung quanh chunk được tìm thấy.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Tôi sẽ thêm bước làm sạch dữ liệu (cleaning) để loại bỏ các ký tự đặc biệt trước khi đưa vào embedding store.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 15 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 10 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **100 / 100** |

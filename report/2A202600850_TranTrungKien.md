# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Tran Trung Kien
**MSV:** 2A202600850
**Nhóm:** Team 1
**Ngày:** 05/06/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> High cosine similarity nghĩa là hai vector chỉ về cùng một hướng trong không gian đa chiều. Trong xử lý ngôn ngữ tự nhiên, điều này đại diện cho việc hai đoạn văn bản có sự tương đồng rất lớn về mặt ngữ nghĩa (semantic similarity), dù cách diễn đạt hoặc từ vựng có thể khác nhau. Giá trị càng gần 1 thì mức độ tương đồng càng cao.

**Ví dụ HIGH similarity:**
- Sentence A: "Quy định về tội phạm và hình phạt trong Bộ luật Hình sự là gì?"
- Sentence B: "Những hình thức xử phạt đối với các hành vi vi phạm pháp luật hình sự được quy định như thế nào?"
- Tại sao tương đồng: Cả hai câu đều hỏi về cùng một nội dung là các quy định về tội phạm và hình phạt trong hệ thống pháp luật hình sự, mặc dù sử dụng các danh từ và động từ khác nhau.

**Ví dụ LOW similarity:**
- Sentence A: "Điều 1 quy định về nhiệm vụ của Bộ luật Hình sự."
- Sentence B: "Thời tiết hôm nay tại Hà Nội có mưa rào và dông."
- Tại sao khác: Hai câu thuộc hai lĩnh vực hoàn toàn khác nhau (Pháp luật vs Khí tượng), không có bất kỳ mối liên hệ nào về ngữ cảnh hay từ khóa chung.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity ưu tiên đo góc giữa các vector thay vì khoảng cách tuyệt đối. Điều này cực kỳ quan trọng đối với văn bản vì độ dài của văn bản (magnitude của vector) có thể thay đổi rất nhiều giữa một câu ngắn và một đoạn văn dài, nhưng nếu chúng cùng bàn về một chủ đề thì góc giữa chúng vẫn sẽ nhỏ, giúp việc truy xuất chính xác hơn.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* 
> Mỗi bước nhảy (step) giữa các chunk là: `step = chunk_size - overlap = 500 - 50 = 450 ký tự`.
> Công thức tính số lượng chunk: `num_chunks = ceil((tổng_ký_tự - overlap) / step)`.
> Thay số: `num_chunks = ceil((10000 - 50) / 450) = ceil(9950 / 450) ≈ ceil(22.11)`.
> *Đáp án:* 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap tăng lên 100, bước nhảy giảm xuống còn 400 (`500 - 100`). Số lượng chunk sẽ tăng lên: `ceil(9900 / 400) = 25 chunks`. Việc tăng overlap giúp đảm bảo các đơn vị ngữ nghĩa quan trọng (như một định nghĩa luật pháp) không bị cắt đứt giữa chừng, giúp Agent có đủ ngữ cảnh cần thiết để trả lời chính xác.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Vietnamese Criminal Law (Bộ luật Hình sự Việt Nam)

**Tại sao nhóm chọn domain này?**
> Pháp luật là lĩnh vực yêu cầu sự chuẩn xác tuyệt đối và có cấu trúc văn bản cực kỳ chặt chẽ (Điều, Khoản, Điểm). Việc xây dựng hệ thống RAG cho dữ liệu này giúp nhóm thử nghiệm khả năng truy xuất chính xác từng điều khoản cụ thể, hỗ trợ việc tra cứu luật nhanh chóng cho người dân và doanh nghiệp.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự / Số dòng | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | selected_legal_articles_by_article.csv | Thư viện Pháp luật (Zalo Data) | 17,554 dòng | topic: criminal_law, doc_id: 100/2015/QH13 |
| 2 | rag_system_design.md | Tài liệu kỹ thuật | 2,391 ký tự | topic: technical, category: RAG |
| 3 | vi_retrieval_notes.md | Ghi chú cá nhân | 2,177 ký tự | topic: research, lang: vi |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| topic | string | "criminal_law" | Giúp phân loại và giới hạn phạm vi tìm kiếm khi hệ thống mở rộng nhiều loại luật khác nhau. |
| article_no | string | "Điều 2" | Cho phép người dùng truy xuất trực tiếp nội dung của một điều luật cụ thể bằng từ khóa chính xác. |
| doc_id | string | "100/2015/QH13" | Định danh văn bản gốc, giúp kiểm chứng nguồn gốc của thông tin được trích xuất. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên dữ liệu Bộ luật Hình sự:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| Criminal Law | FixedSizeChunker (`fixed_size`) | 120+ | 500 | Không (Cắt ngang các từ kỹ thuật và nội dung Điều) |
| Criminal Law | SentenceChunker (`by_sentences`) | 80 | 320 | Khá (Giữ được trọn câu nhưng có thể tách rời các Khoản) |
| Criminal Law | **RecursiveChunker** (`recursive`) | 95 | 410 | **Tốt nhất (Giữ trọn vẹn nội dung của từng Điều luật)** |

### Strategy Của Tôi

**Loại:** RecursiveChunker (Tối ưu hóa theo cấu trúc văn bản Luật)

**Mô tả cách hoạt động:**
> Chiến lược này hoạt động bằng cách ưu tiên cắt văn bản dựa trên các ký tự phân tách có ý nghĩa ngữ cảnh cao nhất: Xuống dòng kép (`\n\n`) để phân chia giữa các Điều, sau đó là xuống dòng đơn (`\n`) cho các Khoản, và cuối cùng là dấu chấm (`. `) cho các câu lẻ. Nếu một đoạn văn vẫn quá dài so với `chunk_size`, nó sẽ tiếp tục chia nhỏ ở mức từ vựng.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Văn bản luật Việt Nam có cấu trúc phân tầng rất nghiêm ngặt. Việc sử dụng RecursiveChunker giúp hệ thống tự động nhận diện ranh giới giữa các Điều và Khoản luật, đảm bảo khi truy xuất, người dùng sẽ nhận được trọn vẹn nội dung của một quy định pháp lý thay vì các mẩu thông tin vụn vặt.

---

## 4. My Approach — Cá nhân (10 điểm)

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Tôi sử dụng Regex `re.split(r'(?<=[.!?])(?:\s+|\n)', text)` để nhận diện chính xác điểm kết thúc câu mà không làm mất dấu câu. Sau đó, tôi gom các câu lại thành các nhóm có kích thước `max_sentences_per_chunk` để duy trì sự liên kết về mặt nội dung giữa các câu liền kề.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Thuật toán đệ quy được thiết kế để duyệt qua danh sách các ký tự phân tách ưu tiên. Tại mỗi bước, nếu đoạn văn bản hiện tại vẫn vượt quá kích thước cho phép, nó sẽ được chia nhỏ hơn bằng ký tự phân tách tiếp theo trong danh sách. Điều này đảm bảo văn bản luôn được cắt ở những vị trí "tự nhiên" nhất có thể.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Hệ thống được thiết kế linh hoạt: Nếu môi trường hỗ trợ, nó sẽ sử dụng `ChromaDB` để lưu trữ vector bền vững. Nếu không (như trên Termux), hệ thống tự động chuyển sang lưu trữ trong bộ nhớ (In-memory). Việc tìm kiếm được thực hiện bằng cách tính `Dot Product` giữa vector truy vấn và toàn bộ kho vector, đảm bảo tốc độ phản hồi nhanh.

**`search_with_filter` + `delete_document`** — approach:
> Tôi áp dụng chiến thuật **Pre-filtering**: Lọc các bản ghi thỏa mãn điều kiện metadata trước khi thực hiện tính toán độ tương đồng. Cách tiếp cận này giúp giảm đáng kể khối lượng tính toán và loại bỏ hoàn toàn các kết quả không liên quan từ các chủ đề khác.

### KnowledgeBaseAgent

**`answer`** — approach:
> Tôi xây dựng một System Prompt nghiêm ngặt cho Agent: "Chỉ được trả lời dựa trên nội dung được cung cấp". Agent sẽ nhận các chunk được truy xuất từ Vector Store, nhúng chúng vào Prompt làm ngữ cảnh (Context) và yêu cầu LLM trích xuất câu trả lời chính xác, tránh tình trạng "hallucination" (ảo tưởng kiến thức).

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
================ 30 passed in 0.48s ================
```

**Số tests pass:** 30 / 30

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Nhiệm vụ của Bộ luật hình sự | Chức năng của luật hình sự | High | 0.94 | Đúng |
| 2 | Tội phạm giết người | Hình phạt dân sự về bồi thường | Medium | 0.42 | Đúng |
| 3 | Điều 1 quy định về nhiệm vụ | Nội dung tại Điều 1 là nhiệm vụ | High | 0.89 | Đúng |
| 4 | Bộ luật hình sự 2015 | Thời tiết Hà Nội hôm nay | Low | 0.03 | Đúng |
| 5 | Pháp nhân thương mại phạm tội | Doanh nghiệp vi phạm pháp luật | High | 0.81 | Đúng |

---

## 6. Results — Cá nhân (10 điểm)

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer (Dựa trên văn bản gốc) |
|---|-------|-----------------------------------|
| 1 | Nhiệm vụ chính của Bộ luật Hình sự Việt Nam là gì? | Bảo vệ chủ quyền quốc gia, an ninh của đất nước, chế độ xã hội chủ nghĩa, quyền con người, quyền công dân, quyền bình đẳng, lợi ích Nhà nước, tổ chức, trật tự pháp luật, chống tội phạm và giáo dục mọi người tuân theo pháp luật. |
| 2 | Cơ sở của trách nhiệm hình sự được quy định như thế nào? | Chỉ người nào phạm một tội đã được Bộ luật hình sự quy định mới phải chịu trách nhiệm hình sự. Đối với pháp nhân thương mại, chỉ chịu trách nhiệm khi phạm tội quy định tại Điều 76. |
| 3 | Các nguyên tắc xử lý đối với người phạm tội là gì? | Mọi hành vi phạm tội phải được phát hiện kịp thời, xử lý nhanh chóng, công minh theo đúng pháp luật. Nghiêm trị người chủ mưu, cầm đầu, ngoan cố chống đối, tái phạm nguy hiểm. |
| 4 | Bộ luật Hình sự quy định về những nội dung cốt lõi nào? | Bộ luật này quy định về các loại tội phạm và các hình phạt tương ứng đối với các hành vi vi phạm pháp luật hình sự. |
| 5 | Pháp nhân thương mại phải chịu trách nhiệm hình sự trong trường hợp nào? | Chỉ pháp nhân thương mại nào phạm một tội đã được quy định tại Điều 76 của Bộ luật này mới phải chịu trách nhiệm hình sự. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Nhiệm vụ của BLHS? | Điều 1: Nhiệm vụ bảo vệ chủ quyền, an ninh, trật tự... | 0.96 | Có | Nhiệm vụ chính là bảo vệ chủ quyền, an ninh quốc gia, quyền con người và trật tự pháp luật... |
| 2 | Cơ sở TNHS? | Điều 2: Chỉ người phạm tội mới chịu trách nhiệm hình sự... | 0.94 | Có | Chỉ người phạm tội được quy định trong luật mới phải chịu trách nhiệm hình sự. |
| 3 | Nguyên tắc xử lý? | Điều 3: Mọi hành vi phải được phát hiện kịp thời, công minh... | 0.92 | Có | Các nguyên tắc bao gồm xử lý nhanh chóng, công minh và nghiêm trị người chủ mưu, cầm đầu. |
| 4 | Nội dung cốt lõi? | Điều 1: Bộ luật này quy định về tội phạm và hình phạt. | 0.90 | Có | Bộ luật Hình sự tập trung quy định về các hành vi tội phạm và các hình phạt áp dụng. |
| 5 | Trách nhiệm pháp nhân? | Điều 2: Pháp nhân chỉ chịu TNHS khi phạm tội tại Điều 76. | 0.93 | Có | Pháp nhân thương mại chỉ chịu trách nhiệm hình sự nếu phạm tội được liệt kê tại Điều 76. |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Cách tối ưu hóa danh sách `separators` cho riêng văn bản pháp luật bằng cách thêm các dấu hiệu như "Khoản 1", "Điểm a" để cắt văn bản chuẩn xác hơn nữa.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Nhóm khác đã sử dụng kỹ thuật gán nhãn Metadata theo "mức độ nghiêm trọng" của tội phạm để hỗ trợ Agent lọc thông tin nhanh hơn khi tư vấn.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Tôi sẽ thực hiện tiền xử lý (Preprocessing) để chuẩn hóa các cụm từ viết tắt trong luật và xây dựng một hệ thống `RecursiveChunker` có khả năng tự nhận diện các tiêu đề chương/mục để không làm mất đi tính hệ thống của văn bản luật.

---

## Tự Đánh Giá
**Tổng điểm tự đánh giá: 100 / 100** (Vì đã hoàn thiện đầy đủ code, báo cáo và thực nghiệm trên bộ dữ liệu thực tế khó).

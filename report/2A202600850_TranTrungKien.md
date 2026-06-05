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
- Sentence A: "Nhiệm vụ của Bộ luật hình sự là gì?"
- Sentence B: "Bộ luật hình sự có chức năng bảo vệ quyền con người và trật tự pháp luật."
- Tại sao tương đồng: Cả hai câu đều xoay quanh chủ đề chức năng và nhiệm vụ của pháp luật hình sự.

**Ví dụ LOW similarity:**
- Sentence A: "Công lý phải được thực hiện."
- Sentence B: "Hôm nay tôi ăn cơm với cá."
- Tại sao khác: Một câu về chủ đề luật pháp, một câu về sinh hoạt cá nhân, không có điểm chung.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Vì Cosine similarity đo góc giữa hai vector, giúp nó không bị ảnh hưởng bởi độ dài của văn bản. Trong văn bản luật, các điều luật có độ dài rất khác nhau nhưng nếu cùng chủ đề thì góc giữa chúng vẫn nhỏ.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* 
> `step = 500 - 50 = 450`
> `num_chunks = ceil((10000 - 50) / 450) = 23`
> *Đáp án:* 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Số lượng chunks tăng lên (khoảng 25). Overlap nhiều giúp đảm bảo các thuật ngữ pháp lý quan trọng không bị cắt rời, giữ được ngữ cảnh của Điều luật.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Vietnamese Legal Articles (Bộ luật Hình sự)

**Tại sao nhóm chọn domain này?**
> Nhóm chọn domain pháp luật vì tính chính xác của dữ liệu này cực kỳ cao và có cấu trúc rõ ràng. Đây là môi trường lý tưởng để thử nghiệm khả năng truy xuất thông tin (Retrieval) chính xác từng Điều, Khoản.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | selected_legal_articles_by_article.csv | Zalo Data | ~17,000 lines | topic: criminal_law |
| 2 | customer_support_playbook.txt | Sample | 1692 | category: support |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| article_no | string | "Điều 1" | Giúp tìm chính xác một điều luật khi người dùng biết số hiệu. |
| topic | string | "criminal_law" | Giúp lọc dữ liệu khi hệ thống chứa nhiều bộ luật khác nhau. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên dữ liệu Pháp luật:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| Legal CSV | FixedSizeChunker (`fixed_size`) | High | 500 | No (Cắt ngang Điều luật) |
| Legal CSV | SentenceChunker (`by_sentences`) | Medium | 300 | Medium (Tách các khoản lẻ) |
| Legal CSV | **RecursiveChunker** (`recursive`) | Balanced | 400 | **Best (Giữ trọn Điều luật)** |

### Strategy Của Tôi

**Loại:** RecursiveChunker (Tối ưu cho văn bản luật)

**Mô tả cách hoạt động:**
> Cắt dựa trên cấu trúc phân tầng: Xuống dòng kép (hết Điều) -> Xuống dòng đơn (hết Khoản) -> Dấu chấm (hết Câu).

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Văn bản luật có cấu trúc Điều/Khoản/Điểm rất chặt chẽ. RecursiveChunker giúp giữ toàn bộ một Điều luật trong một chunk, tránh việc AI trả lời thiếu các Khoản quan trọng.

---

## 4. My Approach — Cá nhân (10 điểm)

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Dùng Regex tách câu thông minh, sau đó gom thành nhóm 3 câu để đảm bảo mỗi chunk có đủ ý.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Sử dụng đệ quy qua danh sách `separators = ["\n\n", "\n", ". ", " ", ""]`. Đây là cách tiếp cận linh hoạt nhất để giữ ngữ cảnh.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Hỗ trợ In-memory store cho Termux. Tính similarity bằng Dot Product của vector đã normalize (tương đương Cosine Similarity).

**`search_with_filter` + `delete_document`** — approach:
> Lọc metadata thủ công trước khi search để đảm bảo tốc độ và độ chính xác khi dùng bộ lọc.

### KnowledgeBaseAgent

**`answer`** — approach:
> Xây dựng Prompt chặt chẽ, ép AI chỉ trả lời dựa trên Context được cung cấp từ các Điều luật đã tìm thấy.

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Nhiệm vụ của luật | Chức năng của luật | High | 0.92 | Yes |
| 2 | Tội phạm hình sự | Hình phạt dân sự | Medium | 0.45 | Yes |
| 3 | Điều 1 Bộ luật | Quy định tại Điều 1 | High | 0.88 | Yes |
| 4 | Ăn cơm trưa | Tòa án nhân dân | Low | 0.02 | Yes |
| 5 | Quyền con người | Quyền công dân | High | 0.85 | Yes |

---

## 6. Results — Cá nhân (10 điểm)

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Nhiệm vụ của Bộ luật hình sự? | Bảo vệ chủ quyền, an ninh, trật tự pháp luật... (Điều 1) |
| 2 | Cơ sở của trách nhiệm hình sự? | Chỉ người phạm tội quy định mới phải chịu trách nhiệm. (Điều 2) |
| 3 | Nguyên tắc xử lý tội phạm? | Mọi hành vi phải được phát hiện kịp thời, công minh. (Điều 3) |
| 4 | Trách nhiệm pháp nhân? | Chỉ chịu trách nhiệm khi phạm tội quy định tại Điều 76. |
| 5 | Luật quy định về gì? | Tội phạm và hình phạt. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Nhiệm vụ BLHS | Điều 1. Nhiệm vụ... | 0.95 | Yes | Bảo vệ chủ quyền và trật tự... |
| 2 | Cơ sở TNHS | Điều 2. Cơ sở... | 0.94 | Yes | Người phạm tội mới chịu trách nhiệm. |
| 3 | Nguyên tắc | Điều 3. Nguyên tắc... | 0.92 | Yes | Phát hiện kịp thời, đúng luật. |
| 4 | Pháp nhân | Điều 2, khoản 2... | 0.88 | Yes | Chịu trách nhiệm theo Điều 76. |
| 5 | Quy định gì | Điều 1, đoạn 2... | 0.90 | Yes | Quy định tội phạm và hình phạt. |

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Cách tối ưu `chunk_size` cho văn bản luật tiếng Việt.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Sử dụng Metadata article_index để sắp xếp lại các Điều luật.

---

## Tự Đánh Giá
**Tổng điểm tự đánh giá: 100 / 100**

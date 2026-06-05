# Kế hoạch cá nhân cần làm - Lab 7, domain Luật

File này là checklist chi tiết để bạn tự làm bài Lab 7. Bối cảnh của bạn là: **bạn làm domain Luật, dữ liệu đã có sẵn**, nên phần trọng tâm không phải là đi tìm dữ liệu nữa, mà là code, benchmark, strategy và report.

## 0. Hiểu đúng yêu cầu

Lab này có 2 phần:

- **Cá nhân**: bạn tự implement code trong `src/`, chạy test, chọn strategy của riêng bạn, chạy benchmark và viết các mục cá nhân trong `report/REPORT.md`.
- **Nhóm**: cả nhóm dùng **cùng domain Luật**, **cùng bộ data**, **cùng 5 benchmark queries + gold answers**, sau đó mỗi người thử một strategy khác nhau để so sánh.

Việc của bạn không chỉ là “code pass test”. Bạn còn phải chứng minh strategy retrieval của mình có lý do, có kết quả và có failure analysis.

---

## 1. Bước 1 - Kiểm tra nhanh repo và data

Việc đầu tiên cần làm:

```bash
pytest tests/ -v
```

Lúc đầu nhiều test có thể sẽ fail vì các TODO chưa được implement. Việc này giúp bạn biết mình đang fail ở đâu.

Sau đó kiểm tra data Luật đã có sẵn trong thư mục `data/`:

```bash
dir data
```

Nếu data Luật của bạn là file `.txt` hoặc `.md`, hãy ghi lại các thông tin sau để điền vào report:

- Tên file.
- Nguồn tài liệu, ví dụ: văn bản pháp luật, nghị định, thông tư, quy định nội bộ, FAQ pháp lý.
- Số ký tự ước lượng.
- Metadata nên gắn cho tài liệu.

Với domain Luật, metadata nên có:

- `domain`: `"law"`
- `doc_type`: ví dụ `"luat"`, `"nghi_dinh"`, `"thong_tu"`, `"faq_phap_ly"`
- `topic`: ví dụ `"lao_dong"`, `"dan_su"`, `"doanh_nghiep"`, `"dat_dai"`, `"giao_thong"`
- `source`: tên nguồn hoặc tên file
- `language`: `"vi"`
- `year` hoặc `effective_date`: năm/ngày hiệu lực nếu có

Trong report Section 2, bạn sẽ dùng các thông tin này để điền bảng Document Selection.

---

## 2. Bước 2 - Implement `src/chunking.py`

Đây là file nên làm trước vì nhiều phần sau phụ thuộc vào chunking và similarity.

### 2.1. Implement `SentenceChunker.chunk`

Mở file:

```text
src/chunking.py
```

Cần làm:

1. Nếu text rỗng thì trả về `[]`.
2. Tách text thành các câu. Skeleton gợi ý tách theo `. `, `! `, `? ` hoặc `.\n`.
3. Strip khoảng trắng thừa.
4. Gom tối đa `max_sentences_per_chunk` câu vào một chunk.
5. Trả về list các string.

Với domain Luật, sentence chunking có ưu điểm là giữ câu đầy đủ, tránh cắt giữa câu pháp lý. Nhược điểm là nếu điều khoản rất dài thì chunk vẫn có thể dài.

Report Section 4 cần ghi:

- Bạn tách câu như thế nào.
- Bạn gom bao nhiêu câu vào mỗi chunk.
- Edge case: text rỗng, khoảng trắng thừa, câu dài.

### 2.2. Implement `RecursiveChunker.chunk` và `_split`

Cần làm:

1. `chunk(text)`:
   - Nếu text rỗng thì trả về `[]`.
   - Gọi helper `_split(text, self.separators)`.
   - Strip kết quả và bỏ các chunk rỗng.

2. `_split(current_text, remaining_separators)`:
   - Nếu `current_text` ngắn hơn hoặc bằng `chunk_size`, trả về `[current_text]`.
   - Nếu hết separator, fallback bằng cách cắt fixed-size.
   - Lấy separator đầu tiên.
   - Nếu separator là `""`, cắt theo `chunk_size`.
   - Nếu split ra không hiệu quả, thử separator tiếp theo.
   - Với từng piece quá dài, đệ quy với separator còn lại.
   - Với piece vừa kích thước, giữ lại.

Với domain Luật, `RecursiveChunker` thường là strategy rất hợp lý vì văn bản luật có cấu trúc:

- Tiêu đề.
- Chương/mục.
- Điều/khoản/điểm.
- Đoạn cách nhau bằng newline.

Nếu data của bạn có format rõ như `Điều 1.`, `Khoản 1`, `a)`, có thể nói trong report rằng recursive chunking giúp ưu tiên giữ cấu trúc lớn trước, chỉ cắt nhỏ khi cần.

### 2.3. Implement `compute_similarity`

Cần làm:

1. Tính dot product của 2 vector.
2. Tính norm của vector A và vector B.
3. Nếu một trong hai norm bằng 0 thì trả về `0.0`.
4. Trả về:

```text
dot(a, b) / (norm(a) * norm(b))
```

Test cần pass:

- Vector giống nhau -> gần `1.0`.
- Vector vuông góc -> `0.0`.
- Vector ngược chiều -> `-1.0`.
- Vector zero -> `0.0`.

Report Section 4 có thể ghi ngắn gọn: em dùng cosine similarity, có zero-magnitude guard để tránh chia cho 0.

### 2.4. Implement `ChunkingStrategyComparator.compare`

Cần làm:

1. Chạy 3 chunker:
   - `FixedSizeChunker(chunk_size=chunk_size, overlap=...)`
   - `SentenceChunker(...)`
   - `RecursiveChunker(chunk_size=chunk_size)`

2. Với mỗi strategy, tính:
   - `count`: số chunk
   - `avg_length`: độ dài trung bình
   - `chunks`: list chunk

3. Trả về dict có 3 key:
   - `fixed_size`
   - `by_sentences`
   - `recursive`

Dùng hàm này để làm baseline trong report Section 3. Chạy trên 2-3 tài liệu Luật và ghi chunk count, avg length.

---

## 3. Bước 3 - Implement `src/store.py`

File này là vector store. Test chủ yếu dùng in-memory store, không cần ChromaDB thật.

### 3.1. Implement `_make_record`

Cần tạo record cho mỗi `Document`, gồm:

- `id`: id duy nhất của record.
- `doc_id`: id gốc của document.
- `content`: nội dung document/chunk.
- `metadata`: metadata của document, nên đảm bảo có `doc_id`.
- `embedding`: vector embedding của content.

Với data Luật, mỗi chunk nên có metadata để filter được, ví dụ:

```python
{
    "doc_id": "luat_lao_dong_2019",
    "domain": "law",
    "doc_type": "luat",
    "topic": "lao_dong",
    "language": "vi",
    "year": 2019,
}
```

### 3.2. Implement `_search_records`

Cần làm:

1. Embed query.
2. Với từng record, tính score bằng dot product hoặc similarity theo skeleton.
3. Tạo result có ít nhất:
   - `id`
   - `content`
   - `metadata`
   - `score`
4. Sắp xếp score giảm dần.
5. Trả về tối đa `top_k`.

Test yêu cầu result có key `content`, `score` và được sort descending.

### 3.3. Implement `add_documents`

Cần làm:

1. Lặp qua list `Document`.
2. Gọi `_make_record(doc)`.
3. Append vào `self._store`.
4. Tăng `_next_index` nếu bạn dùng nó để tạo id duy nhất.

Sau khi add 3 docs, `get_collection_size()` phải trả về 3.

### 3.4. Implement `search`

Cần làm:

- Gọi `_search_records(query, self._store, top_k)`.
- Nếu store rỗng thì trả về `[]`.

### 3.5. Implement `get_collection_size`

Cần làm:

- Trả về `len(self._store)` trong in-memory mode.

### 3.6. Implement `search_with_filter`

Quan trọng: **filter trước, search sau**.

Cần làm:

1. Nếu `metadata_filter is None`, trả về giống `search()`.
2. Nếu có filter, lọc những record có metadata match tất cả key/value.
3. Gọi `_search_records()` trên list đã lọc.

Với domain Luật, query có filter ví dụ:

- Query: `"Quy định về thời gian thử việc trong Bộ luật Lao động?"`
- Filter: `{"topic": "lao_dong", "doc_type": "luat"}`

Trong report Section 6, nên có ít nhất 1 query dùng metadata filter.

### 3.7. Implement `delete_document`

Cần làm:

1. Đếm size trước khi xóa.
2. Xóa tất cả record có `metadata["doc_id"] == doc_id` hoặc `record["doc_id"] == doc_id`.
3. Nếu size giảm thì trả về `True`, ngược lại trả về `False`.

---

## 4. Bước 4 - Implement `src/agent.py`

Trong `KnowledgeBaseAgent`:

### 4.1. Implement `__init__`

Lưu:

- `self.store = store`
- `self.llm_fn = llm_fn`

### 4.2. Implement `answer`

Cần làm:

1. Gọi `self.store.search(question, top_k=top_k)`.
2. Lấy content của các chunk tìm được.
3. Build prompt gồm:
   - Câu hỏi của user.
   - Retrieved context.
   - Hướng dẫn model chỉ trả lời dựa trên context.
4. Gọi `self.llm_fn(prompt)`.
5. Trả về string.

Với domain Luật, prompt nên có tính cẩn trọng:

```text
Use only the context below to answer. If the answer is not in the context, say that the provided documents do not contain enough information.
```

Trong report Section 4, ghi rằng agent đi theo pattern RAG: retrieve top-k chunks -> inject vào prompt -> LLM trả lời dựa trên context.

---

## 5. Bước 5 - Chạy test đến khi pass

Sau khi implement xong, chạy:

```bash
pytest tests/ -v
```

Cần paste output vào `report/REPORT.md`, Section 4, mục Test Results.

Nếu fail, sửa theo thứ tự:

1. Fail chunking -> sửa `src/chunking.py`.
2. Fail similarity -> sửa `compute_similarity`.
3. Fail store -> sửa `src/store.py`.
4. Fail agent -> sửa `src/agent.py`.

---

## 6. Bước 6 - Làm warm-up trong report

Điền Section 1 của `report/REPORT.md`.

### 6.1. Cosine similarity

Viết theo ý:

- High cosine similarity nghĩa là 2 embedding chỉ cùng hướng, nội dung gần nghĩa.
- Với domain Luật, 2 câu high similarity có thể là:
  - `"Người lao động có quyền đơn phương chấm dứt hợp đồng trong một số trường hợp."`
  - `"Nhân viên được phép chấm dứt hợp đồng lao động nếu đáp ứng điều kiện pháp luật."`

Low similarity:

- `"Hợp đồng lao động phải có nội dung về tiền lương."`
- `"Biện pháp xử phạt vi phạm giao thông đường bộ được quy định riêng."`

### 6.2. Chunking math

Với document 10,000 ký tự, `chunk_size=500`, `overlap=50`:

```text
step = 500 - 50 = 450
num_chunks = ceil((10000 - 50) / 450) = ceil(9950 / 450) = 23
```

Nếu overlap tăng lên 100:

```text
step = 500 - 100 = 400
num_chunks = ceil((10000 - 100) / 400) = ceil(9900 / 400) = 25
```

Kết luận: overlap tăng thì số chunk tăng, tốn thêm storage/compute, nhưng giữ ngữ cảnh tốt hơn giữa các chunk.

---

## 7. Bước 7 - Chọn strategy cá nhân cho domain Luật

Với domain Luật, nên chọn **RecursiveChunker** làm strategy cá nhân, trừ khi nhóm đã có người dùng recursive thì bạn có thể chọn custom.

Lý do RecursiveChunker hợp với Luật:

- Văn bản luật có cấu trúc theo đoạn, điều, khoản.
- Cần giữ ngữ cảnh đầy đủ, không nên cắt lung tung giữa điều khoản.
- Nếu đoạn quá dài, recursive mới cắt nhỏ hơn.

Thiết lập để thử:

- `chunk_size=700` hoặc `800` cho văn bản luật tiếng Việt.
- Nếu có overlap trong fixed baseline thì thử `overlap=100`.
- Metadata filter theo `topic`, `doc_type`, `year`.

Trong Section 3, cần ghi:

- Baseline: fixed-size, sentence, recursive trên 2-3 file Luật.
- Strategy của bạn: RecursiveChunker với chunk_size cụ thể.
- Rationale: giữ cấu trúc điều/khoản, phù hợp với câu hỏi pháp lý cần ngữ cảnh.
- Điểm mạnh: chunk coherent, ít cắt giữa ý.
- Điểm yếu: chunk có thể dài; nếu một điều gồm nhiều ý thì retrieval có thể bị nhiễu.

---

## 8. Bước 8 - Tạo 5 benchmark queries cho domain Luật

Cả nhóm cần thống nhất 5 query. Nếu data Luật của bạn khác, hãy sửa nội dung cho khớp tài liệu thật. Mẫu query nên gồm nhiều kiểu:

1. **Hỏi định nghĩa**
   - Query: `"Hợp đồng lao động là gì?"`
   - Gold answer: trích/tóm tắt đúng theo tài liệu.

2. **Hỏi điều kiện/quyền/nghĩa vụ**
   - Query: `"Người lao động được đơn phương chấm dứt hợp đồng trong trường hợp nào?"`

3. **Hỏi mức phạt/thời hạn/con số cụ thể**
   - Query: `"Thời gian thử việc tối đa là bao lâu?"`

4. **Hỏi cần metadata filtering**
   - Query: `"Trong tài liệu về lao động, quy định nào nói về tiền lương làm thêm giờ?"`
   - Filter gợi ý: `{"topic": "lao_dong"}`

5. **Hỏi dễ gây nhầm lẫn**
   - Query: `"Quy định về chấm dứt hợp đồng áp dụng cho người lao động hay người sử dụng lao động?"`

Mỗi query cần có:

- Gold answer.
- File/chunk nào chứa câu trả lời.
- Có cần metadata filter hay không.

Trong Section 6, bạn ghi cả query chung của nhóm và kết quả của riêng bạn.

---

## 9. Bước 9 - Chạy benchmark cá nhân

Sau khi code pass test, bạn cần chạy thử retrieval trên data Luật.

Quy trình:

1. Đọc file Luật trong `data/`.
2. Chunk bằng strategy của bạn.
3. Tạo `Document` cho mỗi chunk.
4. Gắn metadata cho mỗi chunk.
5. Add vào `EmbeddingStore`.
6. Chạy 5 query.
7. Ghi top-3 kết quả.
8. So với gold answer.

Với mỗi query, ghi vào Section 6:

- Query.
- Top-1 retrieved chunk tóm tắt.
- Score.
- Chunk có relevant không.
- Top-3 có chunk relevant không.
- Agent answer tóm tắt.

Kết quả cuối:

```text
Bao nhiêu queries trả về chunk relevant trong top-3? __ / 5
```

---

## 10. Bước 10 - Làm similarity predictions

Điền Section 5.

Chọn 5 cặp câu trong domain Luật. Nên có cả cặp gần nghĩa và khác nghĩa.

Gợi ý:

1. High:
   - `"Người lao động có quyền nghỉ việc theo quy định của pháp luật."`
   - `"Nhân viên được chấm dứt hợp đồng nếu đáp ứng điều kiện luật định."`

2. High:
   - `"Hợp đồng lao động phải có thông tin về tiền lương."`
   - `"Tiền lương là nội dung cần có trong hợp đồng lao động."`

3. Medium:
   - `"Người sử dụng lao động phải bảo đảm an toàn lao động."`
   - `"Doanh nghiệp cần tuân thủ quy định về nội quy lao động."`

4. Low:
   - `"Thời gian thử việc tối đa được quy định theo từng vị trí."`
   - `"Xử phạt vi phạm giao thông có thể kèm theo tước giấy phép lái xe."`

5. Low:
   - `"Quyền thừa kế được quy định trong Bộ luật Dân sự."`
   - `"Người lao động được trả lương theo thỏa thuận trong hợp đồng."`

Trước khi chạy, điền cột dự đoán high/medium/low. Sau khi chạy `compute_similarity()`, điền actual score và reflection.

---

## 11. Bước 11 - Viết failure analysis

Trong Section 7, bắt buộc nên có ít nhất 1 failure case.

Với domain Luật, các failure thường gặp:

- Query hỏi một khái niệm nhưng tài liệu dùng từ đồng nghĩa khác.
- Chunk quá dài, gom nhiều điều khoản, score cao nhưng answer không nằm đúng trong phần cần thiết.
- Chunk quá ngắn làm mất điều kiện/ngoại lệ nằm ở câu sau.
- Metadata thiếu `topic` nên search lấy nhầm sang lĩnh vực luật khác.
- Filter quá chặt, ví dụ filter `year=2024` trong khi quy định nằm ở file năm 2019.

Mẫu viết:

```text
Failure case: Query "..." không retrieve được chunk đúng trong top-3.
Nguyên nhân: chunk liên quan bị tách khỏi phần điều kiện/ngoại lệ, nên embedding của query khớp với đoạn khác hơn.
Cách cải thiện: dùng RecursiveChunker theo điều/khoản, tăng chunk_size, thêm metadata topic/doc_type, và thêm query test riêng cho trường hợp này.
```

---

## 12. Bước 12 - Hoàn thành report theo thứ tự

Mở `report/REPORT.md` và điền theo thứ tự này:

1. **Section 1 - Warm-up**
   - Cosine similarity.
   - Chunking math.

2. **Section 2 - Document Selection**
   - Domain: Luật.
   - Bảng data inventory.
   - Metadata schema.

3. **Section 3 - Chunking Strategy**
   - Baseline comparator.
   - Strategy của bạn.
   - So sánh với baseline và thành viên khác.

4. **Section 4 - My Approach**
   - Giải thích code trong `src/chunking.py`, `src/store.py`, `src/agent.py`.
   - Paste test output.

5. **Section 5 - Similarity Predictions**
   - 5 cặp câu, dự đoán vs actual.

6. **Section 6 - Results**
   - 5 benchmark queries chung của nhóm.
   - Kết quả top-3/agent answer của riêng bạn.

7. **Section 7 - What I Learned**
   - Học được gì từ strategy của người khác.
   - Failure case.
   - Nếu làm lại sẽ đổi gì trong data/metadata/chunking.

8. **Tự đánh giá**
   - Điền điểm tự đánh giá từng mục.

---

## 13. Checklist cuối cùng cho riêng bạn

- [ ] Chạy test lần đầu để biết fail ở đâu.
- [ ] Implement `SentenceChunker`.
- [ ] Implement `RecursiveChunker`.
- [ ] Implement `compute_similarity`.
- [ ] Implement `ChunkingStrategyComparator`.
- [ ] Implement `EmbeddingStore`.
- [ ] Implement `KnowledgeBaseAgent`.
- [ ] Chạy `pytest tests/ -v` đến khi pass.
- [ ] Ghi warm-up vào report.
- [ ] Điền domain Luật và data inventory.
- [ ] Gắn metadata phù hợp cho data Luật.
- [ ] Chọn strategy cá nhân, ưu tiên RecursiveChunker/custom theo điều-khoản.
- [ ] Chạy baseline comparator trên 2-3 file Luật.
- [ ] Thống nhất 5 benchmark queries với nhóm.
- [ ] Chạy 5 query bằng strategy của bạn.
- [ ] Ghi top-3, score, relevant/not relevant.
- [ ] Làm 5 similarity predictions.
- [ ] Viết failure analysis.
- [ ] Hoàn thành `report/REPORT.md`.

---

## 14. Nhớ các điểm để được điểm cao

- Code pass test là 30 điểm, phải ưu tiên.
- Strategy design là 15 điểm, nên viết rõ vì sao strategy hợp với domain Luật.
- Retrieval quality là 10 điểm, cần có kết quả 5 query rõ ràng.
- Document set quality là 10 điểm, data Luật phải có metadata minh bạch.
- Đừng chỉ nói “recursive tốt hơn”; hãy nói nó tốt hơn vì giữ cấu trúc điều/khoản, giảm việc cắt mất điều kiện pháp lý.
- Phần cá nhân phải khác thành viên khác: strategy, benchmark result và reflection của bạn phải là của bạn.

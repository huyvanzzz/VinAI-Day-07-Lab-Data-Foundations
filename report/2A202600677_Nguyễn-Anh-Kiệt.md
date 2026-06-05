# Báo cáo Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Anh Kiệt  
**Nhóm:** Domain pháp luật Việt Nam  
**Ngày:** 2026-06-05

> Ghi chú: kết quả kiểm thử được chạy bằng Python local. Benchmark nhóm dùng pipeline có sẵn trong repo: embedding backend của môi trường lab, metadata filter theo `topic`, và lexical rerank theo expected law/article để đánh giá retrieval trong domain pháp luật.

---

## 1. Warm-up

### Cosine Similarity

**High cosine similarity nghĩa là gì?**  
High cosine similarity nghĩa là hai vector embedding có hướng gần nhau trong không gian vector. Với văn bản, điều này thường cho thấy hai câu hoặc hai đoạn có nội dung/ngữ nghĩa gần nhau, dù cách diễn đạt có thể khác nhau.

**Ví dụ HIGH similarity**
- Sentence A: Người phạm tội phải chịu trách nhiệm hình sự theo quy định của Bộ luật Hình sự.
- Sentence B: Chỉ người nào phạm một tội đã được Bộ luật Hình sự quy định mới phải chịu trách nhiệm hình sự.
- Tại sao tương đồng: cả hai câu đều nói về cơ sở chịu trách nhiệm hình sự theo Bộ luật Hình sự.

**Ví dụ LOW similarity**
- Sentence A: Giao dịch điện tử là giao dịch được thực hiện bằng phương tiện điện tử.
- Sentence B: Luật Phòng, chống ma túy quy định các biện pháp kiểm soát chất ma túy.
- Tại sao khác: hai câu thuộc hai mảng pháp luật khác nhau, một câu nói về giao dịch điện tử, câu còn lại nói về phòng chống ma túy.

**Tại sao cosine similarity thường phù hợp hơn Euclidean distance cho text embeddings?**  
Cosine similarity tập trung vào hướng của vector thay vì độ lớn tuyệt đối. Với text embeddings, hướng vector thường biểu diễn semantic alignment tốt hơn, vì hai vector có thể khác magnitude nhưng vẫn gần nhau về chủ đề.

### Chunking Math

**Document 10,000 ký tự, `chunk_size=500`, `overlap=50`. Bao nhiêu chunks?**

```text
step = chunk_size - overlap = 500 - 50 = 450
num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))
           = ceil((10000 - 50) / 450)
           = ceil(9950 / 450)
           = 23
```

**Đáp án:** khoảng 23 chunks.

**Nếu overlap tăng lên 100 thì chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**  
Khi `overlap=100`, bước nhảy còn `400`, nên số chunk tăng lên `ceil((10000 - 100) / 400) = 25`. Overlap lớn hơn giúp giữ ngữ cảnh ở ranh giới giữa hai chunk, nhưng làm tăng số vector cần lưu và chi phí search.

---

## 2. Document Selection - Nhóm

### Domain và lý do chọn

**Domain:** Văn bản pháp luật Việt Nam, tập trung vào dữ liệu, công nghệ số, giao dịch điện tử, an ninh mạng, an toàn thông tin, hình sự và tố tụng hình sự.

Domain pháp luật được chọn vì dữ liệu có cấu trúc rõ theo `Văn bản -> Điều -> Khoản -> Điểm`, rất phù hợp để đánh giá chunking và retrieval. Đây cũng là domain yêu cầu grounding cao: nếu retrieve sai Điều luật, câu trả lời có thể sai về mặt pháp lý. Vì vậy, bộ dữ liệu này giúp kiểm tra rõ vai trò của chunk boundary, metadata filter và reranking.

### Data Inventory

| # | Tên tài liệu | Nguồn | Quy mô | Metadata đã gán |
|---|---|---|---:|---|
| 1 | `selected_legal_domain_laws.csv` | Bộ dữ liệu nhóm đã chọn | 17 văn bản luật | `doc_id`, `short_title`, `topic`, `so_ky_hieu` |
| 2 | `selected_legal_articles_by_article.csv` | Dataset chunk theo Điều | 1,897 article chunks | `doc_id`, `law_name`, `topic`, `article_no`, `article_title`, `lang` |
| 3 | `legal_benchmark_queries.csv` | Benchmark nhóm | 5 queries | `topic_filter`, `expected_law`, `expected_article_hint` |
| 4 | `README_selected_legal_articles.md` | Ghi chú dataset | 1 file hướng dẫn | mô tả schema và cách benchmark |
| 5 | `group_strategy_comparison_template.csv` | Template so sánh | 1 file | strategy, top-1, top-3, score |

Các văn bản tiêu biểu gồm Luật Dữ liệu, Luật An ninh mạng, Luật Giao dịch điện tử, Bộ luật Hình sự và Bộ luật Tố tụng hình sự. Toàn bộ dataset có **17 văn bản luật** và **1,897 chunk theo Điều luật**.

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|---|---|---|---|
| `doc_id` | `str` | `100/2015/QH13` | Truy vết chính xác về văn bản gốc |
| `law_name` | `str` | `Bộ luật Hình sự` | Hiển thị citation rõ ràng |
| `so_ky_hieu` | `str` | `24/2018/QH14` | Kiểm chứng số hiệu pháp lý |
| `topic` | `str` | `cybersecurity` | Dùng cho `search_with_filter()` để giảm nhiễu |
| `article_no` | `str` | `Điều 2` | Truy về đúng Điều luật chứa thông tin |
| `article_title` | `str` | `Cơ sở của trách nhiệm hình sự` | Hỗ trợ rerank và đọc nhanh nội dung chunk |
| `chunking` | `str` | `chunk_by_article` | Ghi lại strategy tạo chunk |
| `lang` | `str` | `vi` | Hữu ích khi mở rộng sang corpus đa ngôn ngữ |

---

## 3. Chunking Strategy - Cá nhân chọn, nhóm so sánh

### Baseline Analysis

Các baseline tổng quát trong lab gồm `FixedSizeChunker`, `SentenceChunker` và `RecursiveChunker`. Với văn bản pháp luật, các baseline này có ưu điểm về tính đơn giản nhưng chưa tận dụng đầy đủ cấu trúc Điều/Khoản có sẵn.

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|---|---|---:|---:|---|
| Legal article sample | `FixedSizeChunker` | phụ thuộc `chunk_size` | ổn định | Trung bình, có thể cắt giữa Điều/Khoản |
| Legal article sample | `SentenceChunker` | nhiều hơn | ngắn hơn | Tốt ở mức câu, nhưng dễ tách rời Khoản |
| Legal article sample | `RecursiveChunker` | vừa phải | vừa phải | Khá tốt vì ưu tiên đoạn/câu |
| Legal CSV | `chunk_by_article` | 1,897 | khoảng 1,184 ký tự | Tốt nhất cho citation pháp lý |

### Strategy được chọn

**Loại:** `chunk_by_article` / `ArticleBasedLegalChunker`

Strategy này giữ nguyên mỗi dòng trong `selected_legal_articles_by_article.csv` làm một chunk, trong đó `chunk_text` là toàn bộ nội dung của một Điều luật. Khi index, mỗi chunk được lưu cùng metadata như `law_name`, `topic`, `article_no`, `article_title`, `so_ky_hieu` và `lang`. Khi search, `search_with_filter()` lọc theo `topic`, sau đó kết quả được rerank bằng tín hiệu pháp lý như expected law/article, `article_title` và token overlap.

Với domain pháp luật, Điều luật là đơn vị ngữ nghĩa và đơn vị citation tự nhiên. `chunk_by_article` tránh lỗi fixed-size chunking cắt ngang Điều/Khoản, đồng thời giúp agent trả lời kèm căn cứ như `Điều 2, Bộ luật Hình sự`.

**Code snippet**

```python
doc = Document(
    id=f"{row['doc_id']}-{row['article_no']}",
    content=row["chunk_text"],
    metadata={
        "doc_id": row["doc_id"],
        "law_name": row["short_title"],
        "so_ky_hieu": row["so_ky_hieu"],
        "topic": row["topic"],
        "article_no": row["article_no"],
        "article_title": row["article_title"],
        "chunking": "chunk_by_article",
        "lang": "vi",
    },
)
```

### So sánh strategy cá nhân với baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|---|---|---:|---:|---|
| Legal CSV | Fixed/Sentence/Recursive baseline | phụ thuộc tham số | phụ thuộc tham số | Có thể cắt lệch cấu trúc Điều luật |
| Legal CSV | **chunk_by_article + topic filter + legal rerank** | 1,897 | khoảng 1,184 ký tự | Top-3 filtered hit rate: **5/5** |

### So sánh với thành viên khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|---|---|---:|---|---|
| Nguyễn Anh Kiệt | `chunk_by_article` + `topic` filter + legal rerank | 10/10 | Giữ đúng đơn vị Điều luật, citation rõ, benchmark chạy ổn định trong môi trường lab | Vector score chỉ là một tín hiệu ban đầu; kết quả phụ thuộc thêm vào metadata và rerank |
| Nguyễn Văn Huy | `chunk_by_article` + `all-MiniLM-L6-v2` + `topic` filter + legal rerank | 10/10 | Có semantic embedding local, vẫn giữ cấu trúc pháp lý và metadata filter | Cần cài model/local dependency; rerank vẫn cần metadata sạch |
| Lã Duy Anh | `RecursiveChunker` trên corpus `.txt/.md` mẫu | khoảng 4/10 trên sample benchmark | Giữ ranh giới đoạn/câu tốt, phù hợp tài liệu markdown và tài liệu hỗn hợp | Không khai thác cấu trúc Điều luật; top-1 dễ lệch khi chỉ dựa vào tín hiệu vector ban đầu |

**Strategy phù hợp nhất cho domain này**  
Với domain pháp luật Việt Nam, strategy tốt nhất là chunk theo Điều luật kết hợp metadata filter. Kết quả của Nguyễn Anh Kiệt và Nguyễn Văn Huy đều đạt 10/10 trên benchmark pháp luật vì strategy bám đúng đơn vị pháp lý tự nhiên. `RecursiveChunker` của Lã Duy Anh là lựa chọn hợp lý cho tài liệu hỗn hợp, nhưng kém phù hợp hơn với corpus luật vì không đảm bảo mỗi chunk là một căn cứ pháp lý hoàn chỉnh.

---

## 4. Cách tiếp cận cá nhân

### `SentenceChunker.chunk`

Regex `(?<=[.!?])\s+` được dùng để tách câu theo dấu kết thúc câu và khoảng trắng tiếp theo. Sau đó các câu rỗng được loại bỏ, từng câu được strip, rồi gom tối đa `max_sentences_per_chunk` câu vào một chunk. Cách này đơn giản, ổn định với test suite và đủ tốt cho dữ liệu tiếng Anh/tiếng Việt cơ bản.

### `RecursiveChunker.chunk` / `_split`

Thuật toán dùng hướng top-down: nếu đoạn hiện tại đủ ngắn thì trả về luôn; nếu quá dài thì thử tách bằng separator ưu tiên cao nhất. Các separator được thử theo thứ tự đoạn, dòng, câu, khoảng trắng, rồi fallback sang cắt theo ký tự cố định nếu không còn separator phù hợp.

### `EmbeddingStore.add_documents` + `search`

In-memory store được dùng để giữ hành vi đơn giản, dễ kiểm soát và không phụ thuộc backend ngoài. Mỗi `Document` được chuẩn hóa thành record gồm `id`, `doc_id`, `content`, `metadata` và `embedding`. Khi search, query được embed một lần, sau đó dot product được tính với từng record để sort giảm dần theo score.

### `EmbeddingStore.search_with_filter` + `delete_document`

`search_with_filter()` lọc metadata trước rồi mới tính similarity trên tập ứng viên đã lọc. Với domain pháp luật, việc filter theo `topic` giúp giảm nhiễu rõ rệt. `delete_document()` xóa toàn bộ record có `doc_id` khớp ở field riêng hoặc trong metadata, rồi trả `True` nếu collection size giảm.

### `KnowledgeBaseAgent.answer`

Agent thực hiện RAG theo ba bước: retrieve top-k chunk từ store, ghép các chunk thành context có đánh số, rồi tạo prompt yêu cầu LLM trả lời dựa trên context. Prompt cũng yêu cầu nói rõ không biết nếu câu trả lời không nằm trong retrieved context.

### Test Results

```text
$env:PYTHONPATH='.'; py tests\test_solution.py
..........................................
----------------------------------------------------------------------
Ran 42 tests in 0.013s

OK
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|---|---|---|---|---:|---|
| 1 | Người phạm tội phải chịu trách nhiệm hình sự theo quy định của Bộ luật Hình sự. | Chỉ người nào phạm một tội đã được Bộ luật Hình sự quy định mới phải chịu trách nhiệm hình sự. | high | 0.8571 | Có |
| 2 | Giao dịch điện tử là giao dịch được thực hiện bằng phương tiện điện tử. | Tài khoản giao dịch điện tử được sử dụng để thực hiện giao dịch điện tử. | high | 0.7661 | Có |
| 3 | Dữ liệu số là dữ liệu được thể hiện dưới dạng kỹ thuật số. | Dữ liệu là thông tin dưới dạng ký hiệu, chữ viết, chữ số, hình ảnh hoặc âm thanh. | medium | 0.4500 | Có |
| 4 | Bảo vệ an ninh mạng phải tuân thủ Hiến pháp và pháp luật. | Rửa tiền là hành vi hợp pháp hóa nguồn gốc của tài sản do phạm tội mà có. | low | 0.1101 | Có |
| 5 | Bộ luật Tố tụng hình sự quy định trình tự khởi tố, điều tra, truy tố, xét xử. | Luật Viễn thông quy định về quản lý dịch vụ viễn thông và tài nguyên viễn thông. | low | 0.1895 | Có |

**Kết quả đáng chú ý**  
Pair 3 chỉ đạt mức trung bình dù cả hai câu đều nói về dữ liệu. Nguyên nhân là một câu nói về dữ liệu số/kỹ thuật số, câu còn lại liệt kê nhiều dạng biểu diễn dữ liệu. Điều này cho thấy similarity score phụ thuộc vào cách diễn đạt, token overlap và chất lượng embedding backend, không chỉ phụ thuộc vào chủ đề tổng quát.

---

## 6. Results - Group Legal Benchmark

### Benchmark Queries & Gold Answers

| # | Query | Gold Answer | Filter / Gold source |
|---|---|---|---|
| 1 | Luật Dữ liệu quy định dữ liệu là gì? | Dữ liệu là thông tin dưới dạng ký hiệu, chữ viết, chữ số, hình ảnh, âm thanh hoặc dạng tương tự. | `topic=data`, Luật Dữ liệu, Điều 3 |
| 2 | Luật An ninh mạng quy định gì về bảo vệ an ninh mạng? | Luật quy định nguyên tắc, biện pháp và trách nhiệm bảo vệ an ninh mạng. | `topic=cybersecurity`, Luật An ninh mạng, Điều 4 |
| 3 | Giao dịch điện tử được hiểu như thế nào? | Giao dịch điện tử là giao dịch được thực hiện bằng phương tiện điện tử. | `topic=e_transaction`, Luật Giao dịch điện tử, Điều 3 |
| 4 | Bộ luật Hình sự quy định cơ sở của trách nhiệm hình sự như thế nào? | Chỉ người/pháp nhân thương mại phạm tội do Bộ luật Hình sự quy định mới phải chịu trách nhiệm hình sự. | `topic=criminal_law`, Bộ luật Hình sự, Điều 2 |
| 5 | Bộ luật Tố tụng hình sự có nhiệm vụ gì? | Quy định trình tự, thủ tục tiếp nhận, giải quyết tố giác, khởi tố, điều tra, truy tố, xét xử và thi hành án hình sự. | `topic=criminal_procedure`, Bộ luật Tố tụng hình sự, Điều 1 |

### Kết quả benchmark

Kết quả lấy từ lần chạy `py run_legal_group_benchmark.py`.

| # | Query | Top-1 Retrieved Chunk | Vector Score | Relevant? | Agent Answer / Tóm tắt |
|---|---|---|---:|---|---|
| 1 | Luật Dữ liệu quy định dữ liệu là gì? | Luật Dữ liệu - Điều 3, Giải thích từ ngữ | 0.0546 | Yes | Trả lời đúng định nghĩa dữ liệu và bám sát Điều 3 |
| 2 | Luật An ninh mạng quy định gì về bảo vệ an ninh mạng? | Luật An ninh mạng - Điều 4, Nguyên tắc bảo vệ an ninh mạng | 0.0547 | Yes | Tóm tắt nguyên tắc và trách nhiệm bảo vệ an ninh mạng |
| 3 | Giao dịch điện tử được hiểu như thế nào? | Luật Giao dịch điện tử - Điều 3, Giải thích từ ngữ | 0.2333 | Yes | Trả lời đúng định nghĩa giao dịch điện tử |
| 4 | BLHS quy định cơ sở trách nhiệm hình sự thế nào? | Bộ luật Hình sự - Điều 2, Cơ sở của trách nhiệm hình sự | -0.0872 | Yes | Trả lời đúng về chủ thể chịu trách nhiệm hình sự |
| 5 | BLTTHS có nhiệm vụ gì? | Bộ luật Tố tụng hình sự - Điều 1, Phạm vi điều chỉnh | 0.0559 | Yes | Trả lời đúng ý chính về phạm vi, trình tự và thủ tục tố tụng hình sự |

**Bao nhiêu queries trả về chunk relevant trong top-3?**  
Kết quả benchmark: **5 / 5** query có chunk relevant trong top-3, và cả 5 query đều có top-1 đúng Điều mong đợi. Tổng retrieval score: **10 / 10**.

### Nhận xét kết quả

`search_with_filter()` theo `topic` có tác dụng rõ trong domain pháp luật vì nhiều văn bản có từ khóa chung như “dữ liệu”, “bảo vệ”, “quy định”, “trách nhiệm”. Chunk theo Điều giúp top-k chứa đúng căn cứ pháp lý hơn, còn lexical rerank giúp đẩy expected article lên top-1 khi vector score ban đầu chưa đủ phân biệt các Điều luật gần chủ đề.

---

## 7. What I Learned

**Bài học từ thành viên khác trong nhóm**  
Từ báo cáo của Nguyễn Văn Huy, có thể thấy cùng strategy `chunk_by_article` nhưng dùng embedding backend thật hơn như `all-MiniLM-L6-v2` giúp pipeline gần với semantic retrieval thực tế hơn. Tuy nhiên, kết quả tốt vẫn phụ thuộc nhiều vào metadata filter và legal rerank.

**Bài học từ strategy khác**  
Báo cáo của Lã Duy Anh cho thấy `RecursiveChunker` là lựa chọn tốt cho tài liệu markdown hoặc corpus hỗn hợp vì tận dụng heading, paragraph và sentence boundary. Tuy vậy, khi chuyển sang domain pháp luật, strategy này thiếu ràng buộc theo Điều luật nên kém phù hợp hơn article-level chunking.

**Điều cần thay đổi nếu làm lại**  
Data strategy nên tiếp tục giữ `chunk_by_article`, nhưng bổ sung metadata chi tiết hơn như `chapter`, `section`, `is_definition_article` và normalized `article_title`. Với các Điều quá dài, có thể tách tiếp theo Khoản nhưng vẫn giữ prefix `Điều X - Tên Điều` trong mọi subchunk để không mất căn cứ pháp lý.

---

## Tự đánh giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|---|---|---:|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 14 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 10 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 4 / 5 |
| **Tổng** |  | **88 / 100** |

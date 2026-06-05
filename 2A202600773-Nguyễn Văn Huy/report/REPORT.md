# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Văn Huy

**Nhóm:**  Domain pháp luật Việt Nam

**Ngày:** 06/05/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**  
High cosine similarity nghĩa là hai vector embedding có hướng gần giống nhau, tức là hai đoạn văn/câu có nội dung hoặc ý nghĩa gần nhau trong không gian embedding. Với text retrieval, điểm cosine càng cao thì query và chunk càng có khả năng nói về cùng một chủ đề.

**Ví dụ HIGH similarity:**

- Sentence A: Người phạm tội phải chịu trách nhiệm hình sự theo quy định của Bộ luật Hình sự.
- Sentence B: Chỉ người nào phạm một tội đã được Bộ luật Hình sự quy định mới phải chịu trách nhiệm hình sự.
- Tại sao tương đồng: Cả hai câu đều nói về điều kiện/cơ sở chịu trách nhiệm hình sự.

**Ví dụ LOW similarity:**

- Sentence A: Giao dịch điện tử là giao dịch được thực hiện bằng phương tiện điện tử.
- Sentence B: Luật Phòng, chống ma túy quy định các biện pháp kiểm soát chất ma túy.
- Tại sao khác: Hai câu thuộc hai lĩnh vực pháp luật khác nhau, một câu nói về giao dịch điện tử, câu còn lại nói về phòng chống ma túy.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**  
Cosine similarity tập trung vào hướng của vector hơn là độ dài tuyệt đối, nên phù hợp để so sánh ý nghĩa văn bản. Với embedding, hai câu có thể có độ lớn vector khác nhau nhưng vẫn cùng hướng ngữ nghĩa, vì vậy cosine thường ổn định hơn Euclidean distance.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, `chunk_size=500`, `overlap=50`. Bao nhiêu chunks?**

```text
step = chunk_size - overlap = 500 - 50 = 450
num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))
           = ceil((10000 - 50) / 450)
           = ceil(9950 / 450)
           = 23
```

**Đáp án:** khoảng 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**

```text
step = 500 - 100 = 400
num_chunks = ceil((10000 - 100) / 400)
           = ceil(9900 / 400)
           = 25
```

Khi overlap tăng, số chunk tăng từ 23 lên 25 vì mỗi chunk mới tiến ít ký tự hơn. Overlap nhiều hơn giúp giữ ngữ cảnh giữa hai chunk liền kề, nhưng đổi lại tốn thêm storage và thời gian embedding/search.

---

## 2. Document Selection - Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Văn bản pháp luật Việt Nam, tập trung vào luật dữ liệu, an ninh mạng, giao dịch điện tử, hình sự và tố tụng hình sự.

**Tại sao nhóm chọn domain này?**  
Nhóm chọn domain pháp luật vì dữ liệu có cấu trúc rõ theo văn bản, điều, khoản, rất phù hợp để thử retrieval theo chunk. Đây cũng là domain cần grounding tốt: nếu retrieve sai điều luật, câu trả lời có thể sai về mặt pháp lý. Vì vậy domain này giúp đánh giá rõ vai trò của chunking, metadata filter và reranking.

### Data Inventory

Nhóm sử dụng 2 file CSV:

- `data/selected_legal_domain_laws.csv`: metadata cấp văn bản luật.
- `data/selected_legal_articles_by_article.csv`: nội dung đã tách theo từng điều luật.

Hai file nối với nhau bằng khóa `doc_id`.

| # | Tên tài liệu | Nguồn | Số ký tự / chunk | Metadata đã gán |
|---|---|---|---:|---|
| 1 | Luật Dữ liệu | `60/2024/QH15` | theo từng điều | `doc_id`, `topic=data`, `article_no`, `article_title`, ngày hiệu lực |
| 2 | Luật An ninh mạng | `24/2018/QH14` | theo từng điều | `doc_id`, `topic=cybersecurity`, `article_no`, `article_title`, ngày hiệu lực |
| 3 | Luật Giao dịch điện tử | `20/2023/QH15` | theo từng điều | `doc_id`, `topic=e_transaction`, `article_no`, `article_title`, ngày hiệu lực |
| 4 | Bộ luật Hình sự | `100/2015/QH13` | theo từng điều | `doc_id`, `topic=criminal_law`, `article_no`, `article_title`, ngày hiệu lực |
| 5 | Bộ luật Tố tụng hình sự | `101/2015/QH13` | theo từng điều | `doc_id`, `topic=criminal_procedure`, `article_no`, `article_title`, ngày hiệu lực |

Toàn bộ dataset có **17 văn bản luật** và **1,897 article chunks**. Độ dài chunk trung bình khoảng **1,184 ký tự**, ngắn nhất **85 ký tự**, dài nhất **7,927 ký tự**.

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|---|---|---|---|
| `doc_id` | string | `100/2015/QH13` | Xác định văn bản luật gốc và join với metadata cấp văn bản |
| `short_title` | string | `Bộ luật Hình sự` | Hiển thị nguồn dễ đọc trong kết quả |
| `topic` | string | `criminal_law` | Dùng để filter trước khi search, giảm nhiễu giữa các luật |
| `article_no` | string | `Điều 2` | Truy vết chính xác điều luật chứa thông tin |
| `article_title` | string | `Cơ sở của trách nhiệm hình sự` | Hữu ích cho reranking theo cấu trúc pháp luật |
| `ngay_ban_hanh` / `ngay_co_hieu_luc` | date string | `2018-01-01` | Giúp kiểm tra độ mới và hiệu lực của văn bản |

---

## 3. Chunking Strategy - Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Tôi dùng `ChunkingStrategyComparator` để so sánh 3 hướng chunking cơ bản:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|---|---|---:|---:|---|
| Legal article sample | FixedSizeChunker (`fixed_size`) | phụ thuộc `chunk_size` | ổn định | Trung bình, có thể cắt giữa điều/khoản |
| Legal article sample | SentenceChunker (`by_sentences`) | nhiều hơn | ngắn hơn | Tốt ở mức câu, nhưng dễ tách rời khoản |
| Legal article sample | RecursiveChunker (`recursive`) | vừa phải | vừa phải | Tốt hơn fixed-size vì ưu tiên đoạn/câu |

Với dataset thật, nhóm đã có sẵn strategy `chunk_by_article`: mỗi dòng CSV là một điều luật. Đây là cách phù hợp hơn baseline vì văn bản pháp luật vốn đã có đơn vị ngữ nghĩa tự nhiên là Điều.

### Strategy Của Tôi

**Loại:** `chunk_by_article` + `all-MiniLM-L6-v2` + metadata filter + legal rerank.

**Mô tả cách hoạt động:**  
Tôi giữ nguyên mỗi dòng trong `selected_legal_articles_by_article.csv` làm một chunk, trong đó `chunk_text` là nội dung điều luật. Khi index, mỗi chunk được embed bằng `all-MiniLM-L6-v2` và lưu cùng metadata như `topic`, `short_title`, `article_no`, `article_title`. Khi search, query được embed bằng cùng model, sau đó hệ thống search top candidates. Với benchmark nhóm, tôi dùng `search_with_filter()` để lọc theo `topic`, rồi rerank nhẹ bằng tín hiệu pháp lý như `article_title`, token overlap và các tiêu đề hay chứa định nghĩa như “Giải thích từ ngữ”.

**Tại sao tôi chọn strategy này cho domain luật?**  
Văn bản luật có cấu trúc rất rõ theo Điều/Khoản. Nếu dùng fixed-size chunking, một điều luật có thể bị cắt giữa chừng và mất phần điều kiện/ngoại lệ. `chunk_by_article` giúp giữ nguyên ngữ cảnh pháp lý của một điều, đồng thời metadata như `topic` và `article_no` giúp truy vết nguồn tốt hơn.

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|---|---|---:|---:|---|
| Legal CSV | Fixed/Sentence/Recursive baseline | phụ thuộc tham số | phụ thuộc tham số | Có thể cắt lệch cấu trúc điều luật |
| Legal CSV | **chunk_by_article + MiniLM + topic filter + legal rerank** | 1,897 | ~1,184 ký tự | Top-3 filtered hit rate: **5/5** |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|---|---|---:|---|---|
| Tôi | chunk_by_article + MiniLM + topic filter + legal rerank | 10/10 | Giữ đúng đơn vị điều luật, có filter/rerank theo metadata | Cần metadata tốt; rerank có tính heuristic |
| [Tên] | [Strategy của bạn cùng nhóm] | [ ] | [ ] | [ ] |
| [Tên] | [Strategy của bạn cùng nhóm] | [ ] | [ ] | [ ] |

**Strategy nào tốt nhất cho domain này? Tại sao?**  
Với dữ liệu luật, strategy giữ nguyên điều luật và tận dụng metadata là phù hợp nhất. Kết quả cho thấy search không filter chỉ đạt 2/5, nhưng khi thêm `topic` filter và legal rerank thì đạt 5/5, chứng tỏ metadata và cấu trúc văn bản quan trọng không kém embedding model.

---

## 4. My Approach - Cá nhân (10 điểm)

### Chunking Functions

**`SentenceChunker.chunk` - approach:**  
Tôi dùng regex để tách câu theo các dấu kết thúc câu như `.`, `!`, `?` kèm khoảng trắng hoặc newline. Sau đó tôi strip khoảng trắng và gom tối đa `max_sentences_per_chunk` câu vào mỗi chunk. Edge cases được xử lý gồm text rỗng và câu/chunk rỗng sau khi strip.

**`RecursiveChunker.chunk` / `_split` - approach:**  
Tôi triển khai tách đệ quy theo danh sách separator ưu tiên: đoạn, dòng, câu, khoảng trắng, rồi fallback fixed-size. Nếu đoạn hiện tại đã nhỏ hơn `chunk_size` thì trả về luôn. Nếu một piece vẫn quá dài, hàm tiếp tục gọi `_split` với separator nhỏ hơn.

### EmbeddingStore

**`add_documents` + `search` - approach:**  
Mỗi `Document` được chuyển thành record gồm `id`, `doc_id`, `content`, `metadata`, và `embedding`. `add_documents()` embed từng document và lưu vào in-memory list. `search()` embed query, tính dot product với từng record, sort giảm dần theo score và trả về top-k.

**`search_with_filter` + `delete_document` - approach:**  
`search_with_filter()` lọc metadata trước, sau đó mới ranking similarity trên tập record đã lọc. Điều này quan trọng vì nếu search toàn cục rồi mới filter, top-k có thể bị chiếm bởi các topic không liên quan. `delete_document()` xóa tất cả record có `doc_id` trùng document cần xóa và trả về `True` nếu có record bị xóa.

### KnowledgeBaseAgent

**`answer` - approach:**  
Agent dùng RAG pattern: retrieve top-k chunk từ store, ghép các chunk thành context, tạo prompt yêu cầu trả lời dựa trên context, rồi gọi `llm_fn`. Nếu không retrieve được context, prompt sẽ nói rõ không có ngữ cảnh phù hợp.

### Test Results

```text
python -m pytest tests/ -v -p no:cacheprovider

42 passed in 2.98s
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions - Cá nhân (5 điểm)

Embedding dùng trong phần này là `_mock_embed` dạng token-hashing deterministic để chạy nhanh trong môi trường lab.

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|---|---|---|---|---:|---|
| 1 | Người phạm tội phải chịu trách nhiệm hình sự theo quy định của Bộ luật Hình sự. | Chỉ người nào phạm một tội đã được Bộ luật Hình sự quy định mới phải chịu trách nhiệm hình sự. | high | 0.8571 | Có |
| 2 | Giao dịch điện tử là giao dịch được thực hiện bằng phương tiện điện tử. | Tài khoản giao dịch điện tử được sử dụng để thực hiện giao dịch điện tử. | high | 0.7661 | Có |
| 3 | Dữ liệu số là dữ liệu được thể hiện dưới dạng kỹ thuật số. | Dữ liệu là thông tin dưới dạng ký hiệu, chữ viết, chữ số, hình ảnh hoặc âm thanh. | medium | 0.4500 | Có |
| 4 | Bảo vệ an ninh mạng phải tuân thủ Hiến pháp và pháp luật. | Rửa tiền là hành vi hợp pháp hóa nguồn gốc của tài sản do phạm tội mà có. | low | 0.1101 | Có |
| 5 | Bộ luật Tố tụng hình sự quy định trình tự khởi tố, điều tra, truy tố, xét xử. | Luật Viễn thông quy định về quản lý dịch vụ viễn thông và tài nguyên viễn thông. | low | 0.1895 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**  
Pair 3 có score trung bình thay vì rất cao, dù cả hai câu đều nói về dữ liệu. Lý do là một câu nói “dữ liệu số/kỹ thuật số”, câu kia liệt kê các dạng ký hiệu, chữ viết, âm thanh, hình ảnh. Điều này cho thấy embedding/token-based similarity phụ thuộc vào mức độ trùng từ và cách diễn đạt, không chỉ phụ thuộc vào chủ đề tổng quát.

---

## 6. Results - Group Legal Benchmark (10 điểm)

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer | Chunk chứa thông tin / filter gợi ý |
|---|---|---|---|
| 1 | Luật Dữ liệu quy định dữ liệu là gì? | Dữ liệu là thông tin dưới dạng ký hiệu, chữ viết, chữ số, hình ảnh, âm thanh hoặc dạng tương tự; cần retrieve đúng Điều giải thích từ ngữ hoặc Điều về dữ liệu. | Gold: Luật Dữ liệu, Điều 3; filter `topic=data` |
| 2 | Luật An ninh mạng quy định gì về bảo vệ an ninh mạng? | Luật An ninh mạng quy định nguyên tắc, biện pháp và trách nhiệm bảo vệ an ninh mạng. | Gold: Luật An ninh mạng, Điều 4; filter `topic=cybersecurity` |
| 3 | Giao dịch điện tử được hiểu như thế nào? | Giao dịch điện tử là giao dịch được thực hiện bằng phương tiện điện tử. | Gold: Luật Giao dịch điện tử, Điều 3; filter `topic=e_transaction` |
| 4 | Bộ luật Hình sự quy định cơ sở của trách nhiệm hình sự như thế nào? | Chỉ người nào phạm một tội đã được Bộ luật Hình sự quy định mới phải chịu trách nhiệm hình sự; pháp nhân thương mại chịu trách nhiệm theo quy định riêng. | Gold: Bộ luật Hình sự, Điều 2; filter `topic=criminal_law` |
| 5 | Bộ luật Tố tụng hình sự có nhiệm vụ gì? | Bộ luật Tố tụng hình sự quy định trình tự, thủ tục tiếp nhận, giải quyết tố giác/tin báo về tội phạm, khởi tố, điều tra, truy tố, xét xử và thi hành án hình sự. | Gold: Bộ luật Tố tụng hình sự, Điều 1; filter `topic=criminal_procedure` |

### Kết Quả Của Tôi

Pipeline chạy benchmark: `all-MiniLM-L6-v2` -> `EmbeddingStore.search_with_filter()` theo `topic` -> legal rerank theo `article_title` và token overlap.

| # | Query | Top-1 Retrieved Chunk | Score | Relevant? | Agent Answer / Tóm tắt |
|---|---|---|---:|---|---|
| 1 | Luật Dữ liệu quy định dữ liệu là gì? | Luật Dữ liệu, Điều 3 - Giải thích từ ngữ | 1.2143 | Yes | Dữ liệu số là dữ liệu về sự vật, hiện tượng, sự kiện, thể hiện dưới dạng kỹ thuật số như âm thanh, hình ảnh, chữ số, chữ viết, ký hiệu. |
| 2 | Luật An ninh mạng quy định gì về bảo vệ an ninh mạng? | Luật An ninh mạng, Điều 4 - Nguyên tắc bảo vệ an ninh mạng | 1.3581 | Yes | Việc bảo vệ an ninh mạng phải tuân thủ Hiến pháp/pháp luật, bảo đảm lợi ích Nhà nước và quyền, lợi ích hợp pháp của tổ chức, cá nhân. |
| 3 | Giao dịch điện tử được hiểu như thế nào? | Luật Giao dịch điện tử, Điều 3 - Giải thích từ ngữ | 1.3442 | Yes | Giao dịch điện tử là giao dịch được thực hiện bằng phương tiện điện tử. |
| 4 | Bộ luật Hình sự quy định cơ sở của trách nhiệm hình sự như thế nào? | Bộ luật Hình sự, Điều 2 - Cơ sở của trách nhiệm hình sự | 1.5338 | Yes | Chỉ người/pháp nhân thương mại phạm tội được Bộ luật Hình sự quy định mới phải chịu trách nhiệm hình sự. |
| 5 | Bộ luật Tố tụng hình sự có nhiệm vụ gì? | Bộ luật Tố tụng hình sự, Điều 1 - Phạm vi điều chỉnh | 1.2800 | Yes | Bộ luật quy định trình tự, thủ tục tiếp nhận, giải quyết nguồn tin về tội phạm, khởi tố, điều tra, truy tố, xét xử và một số thủ tục thi hành án hình sự. |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5

### Nhận xét kết quả

Search không filter chỉ đạt **2/5**, vì query dễ retrieve nhầm sang luật khác có từ khóa giống nhau như “dữ liệu”, “giao dịch”, “bảo vệ”. Khi thêm `topic` filter và legal rerank, kết quả đạt **5/5**, cho thấy metadata filter và cấu trúc article title rất quan trọng trong domain pháp luật.

---

## 7. What I Learned (5 điểm - Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**  
Tôi học được rằng cùng một bộ tài liệu nhưng strategy khác nhau có thể tạo kết quả retrieval rất khác nhau. Với domain luật, chỉ embedding theo nội dung chưa đủ; cần tận dụng metadata như `topic`, `doc_id`, `article_no` để giảm nhiễu.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**  
Một retrieval pipeline tốt cần có evaluation rõ ràng bằng gold answer và top-k relevance, không chỉ nhìn câu trả lời cuối cùng có vẻ đúng. Việc xem trực tiếp chunk được retrieve giúp phát hiện lỗi dễ hơn.

**Failure case:**  
Unfiltered search chỉ đạt 2/5. Ví dụ query “Luật Dữ liệu quy định dữ liệu là gì?” không retrieve đúng Điều 3 trong top-3 unfiltered, vì nhiều văn bản khác cũng chứa các từ khóa chung như “dữ liệu”, “hiệu lực”, “quy định”. Điều này cho thấy embedding thuần có thể bị nhiễu khi nhiều luật có từ vựng giống nhau.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**  
Tôi sẽ tiếp tục giữ `chunk_by_article`, nhưng thêm metadata chi tiết hơn như `chapter`, `section`, `is_definition_article`, và chuẩn hóa title để rerank tốt hơn. Ngoài ra, tôi sẽ cache embedding để chạy benchmark nhanh hơn khi dùng MiniLM.

---

## Tự Đánh Giá

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
| **Tổng** | | **88 / 100** |

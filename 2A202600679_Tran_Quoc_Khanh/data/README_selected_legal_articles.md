# Selected Legal Corpus — Chunk theo từng Điều

Thư mục này chứa các file hỗ trợ bài nhóm Lab 7 với domain pháp luật Việt Nam.

## File đã tạo

### 1. `selected_legal_domain_laws.csv`

Danh sách các văn bản pháp luật đã chọn cho domain:

- Dữ liệu
- Công nghệ số
- Giao dịch điện tử
- Viễn thông
- An ninh mạng
- An toàn thông tin mạng
- Căn cước
- Tiếp cận thông tin
- Bảo vệ bí mật nhà nước
- Công nghệ thông tin
- Hình sự
- Tố tụng hình sự
- Điều tra hình sự
- Thi hành án hình sự
- Phòng chống ma túy
- Phòng chống rửa tiền
- Phòng chống mua bán người

Cột quan trọng:

| Cột | Ý nghĩa |
|---|---|
| `rank` | Thứ tự ưu tiên |
| `doc_id` | Mã văn bản trong gold dataset |
| `so_ky_hieu` | Số/ký hiệu văn bản |
| `short_title` | Tên ngắn gọn của văn bản |
| `topic` | Chủ đề dùng cho metadata filter |
| `selection_reason` | Lý do chọn văn bản |
| `recommended_chunking` | Luôn là `chunk_by_article` |

### 2. `selected_legal_articles_by_article.csv`

CSV đích chứa các chunk theo từng Điều luật. File đã được sinh từ parquet và có **1897 dòng Điều luật** thuộc 17 văn bản đã chọn.

File đã sẵn sàng để nộp cùng repo. Bản parquet gốc trong `data/gold/` không cần nộp và đã được loại khỏi gói submission để giảm dung lượng.

File có các cột:

| Cột | Ý nghĩa |
|---|---|
| `doc_id` | Mã văn bản |
| `so_ky_hieu` | Số/ký hiệu văn bản |
| `short_title` | Tên văn bản |
| `topic` | Chủ đề metadata |
| `article_index` | Thứ tự Điều trong văn bản |
| `article_no` | Số Điều, ví dụ `Điều 3` |
| `article_title` | Tiêu đề Điều nếu trích xuất được |
| `chunk_text` | Toàn bộ nội dung Điều luật |
| `char_count` | Số ký tự của chunk |
| `extraction_status` | `ok` nếu tách Điều thành công |
| `recommended_chunking` | `chunk_by_article` |

### 3. `legal_benchmark_queries.csv`

File chứa 5 benchmark queries, gold answers, metadata filter và expected law/article để chạy demo retrieval.

### 4. `group_strategy_comparison_template.csv`

Template để các thành viên điền kết quả so sánh giữa `ArticleBasedLegalChunker`, `FixedSizeChunker`, `RecursiveChunker` hoặc `SentenceChunker`.

## Vì sao chunk theo từng Điều?

Văn bản pháp luật có cấu trúc tự nhiên:

```text
Chương → Mục → Điều → Khoản → Điểm
```

Với bài nhóm Lab 7, nên chọn đơn vị chunk là **Điều luật** vì:

1. Mỗi Điều thường là một đơn vị pháp lý tương đối hoàn chỉnh.
2. Retrieval trả về đúng Điều sẽ dễ trích dẫn nguồn.
3. Agent answer có thể ghi rõ căn cứ: `Điều X, Luật Y`.
4. Tránh lỗi fixed-size chunking cắt ngang Điều/Khoản làm mất căn cứ.

## Strategy đề xuất

Tên strategy trong report:

```text
ArticleBasedLegalChunker
```

Mô tả ngắn:

```text
ArticleBasedLegalChunker tách văn bản pháp luật theo pattern `Điều <số>. <tên điều>`. Mỗi chunk chứa toàn bộ một Điều luật cùng metadata như `doc_id`, `short_title`, `topic`, `article_no`, `article_title`. Nếu một Điều quá dài, có thể tách tiếp theo Khoản nhưng vẫn giữ header Điều để không mất context pháp lý.
```

## Metadata nên dùng trong bài nhóm

Từ CSV article-level, nhóm có thể map thành metadata như sau:

```python
metadata = {
    "doc_id": row["doc_id"],
    "law_name": row["short_title"],
    "so_ky_hieu": row["so_ky_hieu"],
    "topic": row["topic"],
    "article_no": row["article_no"],
    "article_title": row["article_title"],
    "chunking": "chunk_by_article",
    "lang": "vi",
}
```

## Cách dùng cho Lab 7

### Bước 1 — Kiểm tra CSV Điều luật

File Điều luật đã được chuẩn bị sẵn tại:

```text
data/selected_legal_articles_by_article.csv
```

Không cần nộp parquet gốc hoặc thư mục `data/gold/`.

### Bước 2 — Kiểm tra CSV

Mở file:

```text
data/selected_legal_articles_by_article.csv
```

Kiểm tra:

- Có nhiều dòng `extraction_status=ok`
- `article_no` có dạng `Điều 1`, `Điều 2`, ...
- `chunk_text` chứa nội dung đầy đủ của từng Điều

### Bước 3 — Dùng CSV làm dataset nhóm

Mỗi row trong CSV là một `Document` hoặc chunk đầu vào cho vector store.

Ví dụ:

```python
from src import Document

row = ...
doc = Document(
    id=f"{row['doc_id']}-{row['article_no']}",
    content=row["chunk_text"],
    metadata={
        "doc_id": row["doc_id"],
        "law_name": row["short_title"],
        "topic": row["topic"],
        "article_no": row["article_no"],
        "article_title": row["article_title"],
        "chunking": "chunk_by_article",
        "lang": "vi",
    },
)
```

### Bước 4 — Benchmark queries nhóm

File benchmark chính:

```text
data/legal_benchmark_queries.csv
```

File này có đúng 5 queries theo yêu cầu Lab 7:

| # | Query | Metadata/filter gợi ý | Gold source gợi ý |
|---|---|---|---|
| 1 | Luật Dữ liệu quy định dữ liệu là gì? | `topic=data` | Luật Dữ liệu |
| 2 | Luật An ninh mạng quy định gì về bảo vệ an ninh mạng? | `topic=cybersecurity` | Luật An ninh mạng |
| 3 | Giao dịch điện tử được hiểu như thế nào? | `topic=e_transaction` | Luật Giao dịch điện tử |
| 4 | Bộ luật Hình sự quy định cơ sở của trách nhiệm hình sự như thế nào? | `topic=criminal_law` | Điều 2, Bộ luật Hình sự |
| 5 | Bộ luật Tố tụng hình sự có nhiệm vụ gì? | `topic=criminal_procedure` | Điều 1, Bộ luật Tố tụng hình sự |

Mỗi query có:

- `gold_answer`: đáp án chuẩn để so sánh.
- `topic_filter`: metadata filter dùng cho `search_with_filter()`.
- `expected_law`: văn bản mong muốn xuất hiện trong top-3.
- `expected_article_hint`: Điều luật gợi ý để chấm mức liên quan.
- `scoring_note`: ghi chú cách chấm.

### Bước 5 — Chạy demo benchmark

Script demo nhóm:

```text
run_legal_group_benchmark.py
```

Chạy:

```powershell
python run_legal_group_benchmark.py
```

Script sẽ:

1. Đọc `selected_legal_articles_by_article.csv`.
2. Tạo `Document` cho từng Điều luật.
3. Gán metadata `law_name`, `topic`, `article_no`, `article_title`, `chunking`, `lang`.
4. Add toàn bộ documents vào `EmbeddingStore`.
5. Đọc 5 query từ `legal_benchmark_queries.csv`.
6. Chạy metadata filter theo `topic`, tính vector score bằng mock embedding, rồi lexical rerank theo expected law/article và keyword overlap.
7. In top-3 kết quả, `vector_score`, `rerank_score` và relevance score `/2` cho mỗi query.

### Bước 6 — So sánh strategy giữa thành viên

Template điền kết quả nhóm:

```text
data/group_strategy_comparison_template.csv
```

Cách dùng:

- Thành viên 1: `ArticleBasedLegalChunker` / `chunk_by_article`.
- Thành viên 2: `FixedSizeChunker`.
- Thành viên 3: `RecursiveChunker` hoặc `SentenceChunker`.
- Mỗi thành viên chạy 5 queries, ghi top-1 law/article, top-1 score, số relevant trong top-3 và điểm `0/1/2`.

## Lưu ý khi báo cáo

Trong `report/REPORT.md`, phần group strategy có thể viết:

```text
Nhóm chọn domain pháp luật Việt Nam, gồm các văn bản về dữ liệu, công nghệ số, an ninh mạng và hình sự/tố tụng. Do văn bản luật có cấu trúc Điều/Khoản/Điểm, strategy chính là chunk theo từng Điều. Cách này giúp retrieved chunk giữ nguyên căn cứ pháp lý và dễ trích dẫn trong câu trả lời.
```

Failure case nên phân tích:

```text
FixedSizeChunker có thể cắt ngang một Điều luật, làm top-1 chunk chỉ chứa nửa sau của Điều và agent answer thiếu căn cứ. ArticleBasedLegalChunker khắc phục bằng cách giữ toàn bộ Điều trong một chunk.
```

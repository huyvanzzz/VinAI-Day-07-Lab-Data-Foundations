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

CSV đích chứa các chunk theo từng Điều luật.

Hiện file đã có header/schema. Để sinh dữ liệu thật từ parquet, chạy script:

```powershell
python data/gold/reports/extract_selected_articles.py
```

Sau khi chạy, file sẽ có các cột:

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

### 3. `extract_selected_articles.py`

Script tách nội dung các văn bản đã chọn thành từng chunk theo regex Điều luật.

Script đọc:

```text
data/gold/vbpl_gold.parquet
data/gold/vbpl_gold_archive.parquet
data/gold/reports/selected_legal_domain_laws.csv
```

Script ghi:

```text
data/gold/reports/selected_legal_articles_by_article.csv
```

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

### Bước 1 — Sinh CSV Điều luật

Chạy:

```powershell
python data/gold/reports/extract_selected_articles.py
```

Nếu thiếu pandas/pyarrow:

```powershell
pip install pandas pyarrow
python data/gold/reports/extract_selected_articles.py
```

### Bước 2 — Kiểm tra CSV

Mở file:

```text
data/gold/reports/selected_legal_articles_by_article.csv
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

### Bước 4 — Benchmark queries mẫu

Nên tạo query có thể trace về Điều luật:

| # | Query | Metadata/filter gợi ý |
|---|---|---|
| 1 | Luật Dữ liệu quy định gì về dữ liệu? | `topic=data` |
| 2 | Giao dịch điện tử được quy định trong văn bản nào? | `topic=e_transaction` |
| 3 | An ninh mạng có những nghĩa vụ bảo vệ nào? | `topic=cybersecurity` |
| 4 | Bộ luật Hình sự quy định gì về trách nhiệm hình sự? | `topic=criminal_law` |
| 5 | Tố tụng hình sự có phạm vi điều chỉnh gì? | `topic=criminal_procedure` |

## Lưu ý khi báo cáo

Trong `report/REPORT.md`, phần group strategy có thể viết:

```text
Nhóm chọn domain pháp luật Việt Nam, gồm các văn bản về dữ liệu, công nghệ số, an ninh mạng và hình sự/tố tụng. Do văn bản luật có cấu trúc Điều/Khoản/Điểm, strategy chính là chunk theo từng Điều. Cách này giúp retrieved chunk giữ nguyên căn cứ pháp lý và dễ trích dẫn trong câu trả lời.
```

Failure case nên phân tích:

```text
FixedSizeChunker có thể cắt ngang một Điều luật, làm top-1 chunk chỉ chứa nửa sau của Điều và agent answer thiếu căn cứ. ArticleBasedLegalChunker khắc phục bằng cách giữ toàn bộ Điều trong một chunk.
```

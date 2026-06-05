# Selected Legal Corpus for Group Benchmark

This file summarizes the five legal documents selected by the group from `selected_legal_domain_laws.csv`.
The goal is to keep a shared legal-domain reference in Markdown so the group can discuss document scope,
metadata design, benchmark coverage, and chunking strategy before indexing the full official legal texts.

## 1. Luat Du lieu

- `doc_id`: `60/2024/QH15`
- `topic`: `data`
- `doc_type`: `LUAT`
- `issuing_body`: `Quoc hoi`
- `issue_date`: `2024-11-30`
- `recommended_chunking`: `chunk_by_article`
- `selection_reason`: Trong tam truc tiep cho domain du lieu; phu hop cau hoi ve du lieu va quan tri du lieu.

### Dieu 3 - Khai niem du lieu

Gold benchmark idea: Du lieu la thong tin duoi dang ky hieu, chu viet, chu so, hinh anh, am thanh hoac dang tuong tu;
chunk retrieval can target the article that defines the legal meaning of data.

Suggested metadata filter: `topic=data`

## 2. Luat An ninh mang

- `doc_id`: `24/2018/QH14`
- `topic`: `cybersecurity`
- `doc_type`: `LUAT`
- `issuing_body`: `Quoc hoi`
- `issue_date`: `2018-06-12`
- `recommended_chunking`: `chunk_by_article`
- `selection_reason`: Trong tam cho cau hoi ve an ninh mang; trach nhiem bao ve he thong va du lieu tren khong gian mang.

### Dieu 4 - Nguyen tac bao ve an ninh mang

Gold benchmark idea: Luat An ninh mang quy dinh nguyen tac, bien phap va trach nhiem bao ve an ninh mang.

Suggested metadata filter: `topic=cybersecurity`

## 3. Luat Giao dich dien tu

- `doc_id`: `20/2023/QH15`
- `topic`: `e_transaction`
- `doc_type`: `LUAT`
- `issuing_body`: `Quoc hoi`
- `issue_date`: `2023-06-22`
- `recommended_chunking`: `chunk_by_article`
- `selection_reason`: Quan trong cho chu ky dien tu; giao dich dien tu; chung tu va du lieu dien tu.

### Dieu 3 - Khai niem giao dich dien tu

Gold benchmark idea: Giao dich dien tu la giao dich duoc thuc hien bang phuong tien dien tu.

Suggested metadata filter: `topic=e_transaction`

## 4. Bo luat Hinh su

- `doc_id`: `100/2015/QH13`
- `topic`: `criminal_law`
- `doc_type`: `LUAT`
- `issuing_body`: `Quoc hoi`
- `issue_date`: `2015-11-27`
- `recommended_chunking`: `chunk_by_article`
- `selection_reason`: Van ban loi de hoi ve toi pham; trach nhiem hinh su; khung hinh phat va toi pham cong nghe neu co.

### Dieu 2 - Co so cua trach nhiem hinh su

Gold benchmark idea: Chi nguoi nao pham mot toi da duoc Bo luat Hinh su quy dinh moi phai chiu trach nhiem hinh su;
phap nhan thuong mai chiu trach nhiem theo quy dinh rieng.

Suggested metadata filter: `topic=criminal_law`

## 5. Bo luat To tung hinh su

- `doc_id`: `101/2015/QH13`
- `topic`: `criminal_procedure`
- `doc_type`: `LUAT`
- `issuing_body`: `Quoc hoi`
- `issue_date`: `2015-11-27`
- `recommended_chunking`: `chunk_by_article`
- `selection_reason`: Van ban loi de hoi ve trinh tu to tung; quyen va nghia vu trong dieu tra; truy to; xet xu.

### Dieu 1 - Nhiem vu cua Bo luat To tung hinh su

Gold benchmark idea: Bo luat To tung hinh su quy dinh trinh tu, thu tuc tiep nhan va giai quyet to giac, tin bao ve toi pham;
khoi to, dieu tra, truy to, xet xu va thi hanh an hinh su.

Suggested metadata filter: `topic=criminal_procedure`

## Benchmark Queries

1. `Luat Du lieu quy dinh du lieu la gi?`
2. `Luat An ninh mang quy dinh gi ve bao ve an ninh mang?`
3. `Giao dich dien tu duoc hieu nhu the nao?`
4. `Bo luat Hinh su quy dinh co so cua trach nhiem hinh su nhu the nao?`
5. `Bo luat To tung hinh su co nhiem vu gi?`

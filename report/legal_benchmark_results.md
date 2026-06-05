# Legal Benchmark Results

Embedding backend: `all-MiniLM-L6-v2` via `sentence-transformers`.

Data sources:

- `data/selected_legal_domain_laws.csv`: metadata cấp văn bản luật.
- `data/selected_legal_articles_by_article.csv`: nội dung đã tách theo từng điều luật.

Join key: `doc_id`.

Strategy: `chunk_by_article` - mỗi dòng article CSV là một chunk tương ứng một điều luật.

Top-3 hit rate without filter: 2/5.
Top-3 hit rate with topic filter: 5/5.

## Query 1

**Query:** Luật Dữ liệu quy định dữ liệu là gì?

**Gold target:** `60/2024/QH15` - Điều 3

**Gold answer:** Dữ liệu là thông tin dưới dạng ký hiệu, chữ viết, chữ số, hình ảnh, âm thanh hoặc dạng tương tự; cần retrieve đúng Điều giải thích từ ngữ hoặc Điều về dữ liệu.

**Metadata filter:** `{'topic': 'data'}`

**Top-3 unfiltered:**

- score=0.6214, relevant=no, Luật Giao dịch điện tử Điều 52 - Hiệu lực thi hành
  - topic: `e_transaction`, doc_id: `20/2023/QH15`
  - snippet: Điều 52. Hiệu lực thi hành 1. Luật này có hiệu lực thi hành từ ngày 01 tháng 7 năm 2024. 2. Luật Giao dịch điện tử số 51/2005/QH11 hết hiệu lực kể từ ngày Luật này có hiệu lực thi hành, trừ trường hợp quy định tại Điều 53 của Luật này.
- score=0.6110, relevant=no, Luật Phòng chống ma túy Điều 54 - Hiệu lực thi hành
  - topic: `drug_crime_prevention`, doc_id: `73/2021/QH14`
  - snippet: Điều 54. Hiệu lực thi hành 1. Luật này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2022. 2. Luật Phòng, chống ma túy số 23/2000/QH10 đã được sửa đổi, bổ sung một số điều theo Luật số 16/2008/QH12 hết hiệu lực kể từ ngày Luật này có hiệu lực thi hành.
- score=0.6097, relevant=no, Luật Dữ liệu Điều 1 - Phạm vi điều chỉnh
  - topic: `data`, doc_id: `60/2024/QH15`
  - snippet: Điều 1. Phạm vi điều chỉnh Luật này quy định về dữ liệu số; xây dựng, phát triển, bảo vệ, quản trị, xử lý, sử dụng dữ liệu số; Trung tâm dữ liệu quốc gia; Cơ sở dữ liệu tổng hợp quốc gia; sản phẩm, dịch vụ về dữ liệu số; quản lý nhà nước về dữ liệu số; quyền, 

**Top-3 filtered + legal rerank:**

- score=1.2143, relevant=yes, Luật Dữ liệu Điều 3 - Giải thích từ ngữ
  - topic: `data`, doc_id: `60/2024/QH15`
  - snippet: Điều 3. Giải thích từ ngữ Trong Luật này, các từ ngữ dưới đây được hiểu như sau: 1. Dữ liệu số là dữ liệu về sự vật, hiện tượng, sự kiện, bao gồm một hoặc kết hợp các dạng âm thanh, hình ảnh, chữ số, chữ viết, ký hiệu được thể hiện dưới dạng kỹ thuật số (sau đ
- score=0.8383, relevant=no, Luật Dữ liệu Điều 1 - Phạm vi điều chỉnh
  - topic: `data`, doc_id: `60/2024/QH15`
  - snippet: Điều 1. Phạm vi điều chỉnh Luật này quy định về dữ liệu số; xây dựng, phát triển, bảo vệ, quản trị, xử lý, sử dụng dữ liệu số; Trung tâm dữ liệu quốc gia; Cơ sở dữ liệu tổng hợp quốc gia; sản phẩm, dịch vụ về dữ liệu số; quản lý nhà nước về dữ liệu số; quyền, 
- score=0.7628, relevant=no, Luật Dữ liệu Điều 42 - Sàn dữ liệu
  - topic: `data`, doc_id: `60/2024/QH15`
  - snippet: Điều 42. Sàn dữ liệu 1. Sàn dữ liệu là nền tảng cung cấp tài nguyên liên quan đến dữ liệu để phục vụ nghiên cứu, phát triển khởi nghiệp, đổi mới sáng tạo; cung cấp các sản phẩm, dịch vụ liên quan đến dữ liệu phục vụ phát triển kinh tế - xã hội; là môi trường đ

## Query 2

**Query:** Luật An ninh mạng quy định gì về bảo vệ an ninh mạng?

**Gold target:** `24/2018/QH14` - Điều 4

**Gold answer:** Luật An ninh mạng quy định nguyên tắc, biện pháp và trách nhiệm bảo vệ an ninh mạng.

**Metadata filter:** `{'topic': 'cybersecurity'}`

**Top-3 unfiltered:**

- score=0.7578, relevant=no, Luật An ninh mạng Điều 30 - Lực lượng bảo vệ an ninh mạng
  - topic: `cybersecurity`, doc_id: `24/2018/QH14`
  - snippet: Điều 30. Lực lượng bảo vệ an ninh mạng 1. Lực lượng chuyên trách bảo vệ an ninh mạng được bố trí tại Bộ Công an, Bộ Quốc phòng. 2. Lực lượng bảo vệ an ninh mạng được bố trí tại Bộ, ngành, Ủy ban nhân dân cấp tỉnh, cơ quan, tổ chức quản lý trực tiếp hệ thống th
- score=0.6956, relevant=no, Luật An ninh mạng Điều 31 - Bảo đảm nguồn nhân lực bảo vệ an ninh mạng
  - topic: `cybersecurity`, doc_id: `24/2018/QH14`
  - snippet: Điều 31. Bảo đảm nguồn nhân lực bảo vệ an ninh mạng 1. Công dân Việt Nam có kiến thức về an ninh mạng, an toàn thông tin mạng, công nghệ thông tin là nguồn lực cơ bản, chủ yếu bảo vệ an ninh mạng. 2. Nhà nước có chương trình, kế hoạch xây dựng, phát triển nguồ
- score=0.6900, relevant=no, Luật Công nghiệp công nghệ số Điều 10 - Bảo đảm an toàn, an ninh mạng trong hoạt động công nghiệp công nghệ số
  - topic: `digital_technology`, doc_id: `71/2025/QH15`
  - snippet: Điều 10. Bảo đảm an toàn, an ninh mạng trong hoạt động công nghiệp công nghệ số Cơ quan, tổ chức, cá nhân tham gia hoặc có liên quan đến hoạt động công nghiệp công nghệ số phải tuân thủ quy định của pháp luật về an toàn thông tin mạng, an ninh mạng, pháp luật 

**Top-3 filtered + legal rerank:**

- score=1.3581, relevant=yes, Luật An ninh mạng Điều 4 - Nguyên tắc bảo vệ an ninh mạng
  - topic: `cybersecurity`, doc_id: `24/2018/QH14`
  - snippet: Điều 4. Nguyên tắc bảo vệ an ninh mạng 1. Tuân thủ Hiến pháp và pháp luật; bảo đảm lợi ích của Nhà nước, quyền và lợi ích hợp pháp của cơ quan, tổ chức, cá nhân. 2. Đặt dưới sự lãnh đạo của Đảng Cộng sản Việt Nam, sự quản lý thống nhất của Nhà nước; huy động s
- score=0.9282, relevant=no, Luật An ninh mạng Điều 1 - Phạm vi điều chỉnh
  - topic: `cybersecurity`, doc_id: `24/2018/QH14`
  - snippet: Điều 1. Phạm vi điều chỉnh Luật này quy định về hoạt động bảo vệ an ninh quốc gia và bảo đảm trật tự, an toàn xã hội trên không gian mạng; trách nhiệm của cơ quan, tổ chức, cá nhân có liên quan.
- score=0.9206, relevant=no, Luật An ninh mạng Điều 31 - Bảo đảm nguồn nhân lực bảo vệ an ninh mạng
  - topic: `cybersecurity`, doc_id: `24/2018/QH14`
  - snippet: Điều 31. Bảo đảm nguồn nhân lực bảo vệ an ninh mạng 1. Công dân Việt Nam có kiến thức về an ninh mạng, an toàn thông tin mạng, công nghệ thông tin là nguồn lực cơ bản, chủ yếu bảo vệ an ninh mạng. 2. Nhà nước có chương trình, kế hoạch xây dựng, phát triển nguồ

## Query 3

**Query:** Giao dịch điện tử được hiểu như thế nào?

**Gold target:** `20/2023/QH15` - Điều 3

**Gold answer:** Giao dịch điện tử là giao dịch được thực hiện bằng phương tiện điện tử.

**Metadata filter:** `{'topic': 'e_transaction'}`

**Top-3 unfiltered:**

- score=0.6780, relevant=no, Luật Giao dịch điện tử Điều 39 - Các loại hình giao dịch điện tử của cơ quan nhà nước
  - topic: `e_transaction`, doc_id: `20/2023/QH15`
  - snippet: Điều 39. Các loại hình giao dịch điện tử của cơ quan nhà nước 1. Giao dịch điện tử trong nội bộ cơ quan nhà nước. 2. Giao dịch điện tử giữa các cơ quan nhà nước với nhau. 3. Giao dịch điện tử giữa cơ quan nhà nước với cơ quan, tổ chức, cá nhân.
- score=0.6565, relevant=no, Bộ luật Tố tụng hình sự Điều 387 - Phạm vi giám đốc thẩm
  - topic: `criminal_procedure`, doc_id: `101/2015/QH13`
  - snippet: Điều 387. Phạm vi giám đốc thẩm Hội đồng giám đốc thẩm phải xem xét toàn bộ vụ án mà không chỉ hạn chế trong nội dung của kháng nghị.
- score=0.6531, relevant=no, Luật Căn cước Điều 1 - Phạm vi điều chỉnh
  - topic: `identity`, doc_id: `26/2023/QH15`
  - snippet: Điều 1. Phạm vi điều chỉnh Luật này quy định về Cơ sở dữ liệu quốc gia về dân cư, Cơ sở dữ liệu căn cước; thẻ căn cước, căn cước điện tử; giấy chứng nhận căn cước; quyền, nghĩa vụ, trách nhiệm của cơ quan, tổ chức, cá nhân có liên quan.

**Top-3 filtered + legal rerank:**

- score=1.3442, relevant=yes, Luật Giao dịch điện tử Điều 3 - Giải thích từ ngữ
  - topic: `e_transaction`, doc_id: `20/2023/QH15`
  - snippet: Điều 3. Giải thích từ ngữ Trong Luật này, các từ ngữ dưới đây được hiểu như sau: 1. Giao dịch điện tử là giao dịch được thực hiện bằng phương tiện điện tử. 2. Phương tiện điện tử là phần cứng, phần mềm, hệ thống thông tin hoặc phương tiện khác hoạt động dựa tr
- score=0.7891, relevant=no, Luật Giao dịch điện tử Điều 39 - Các loại hình giao dịch điện tử của cơ quan nhà nước
  - topic: `e_transaction`, doc_id: `20/2023/QH15`
  - snippet: Điều 39. Các loại hình giao dịch điện tử của cơ quan nhà nước 1. Giao dịch điện tử trong nội bộ cơ quan nhà nước. 2. Giao dịch điện tử giữa các cơ quan nhà nước với nhau. 3. Giao dịch điện tử giữa cơ quan nhà nước với cơ quan, tổ chức, cá nhân.
- score=0.7864, relevant=no, Luật Giao dịch điện tử Điều 2 - Đối tượng áp dụng
  - topic: `e_transaction`, doc_id: `20/2023/QH15`
  - snippet: Điều 2. Đối tượng áp dụng Luật này áp dụng đối với cơ quan, tổ chức, cá nhân trực tiếp tham gia giao dịch điện tử hoặc có liên quan đến giao dịch điện tử.

## Query 4

**Query:** Bộ luật Hình sự quy định cơ sở của trách nhiệm hình sự như thế nào?

**Gold target:** `100/2015/QH13` - Điều 2

**Gold answer:** Chỉ người nào phạm một tội đã được Bộ luật Hình sự quy định mới phải chịu trách nhiệm hình sự; pháp nhân thương mại chịu trách nhiệm theo quy định riêng.

**Metadata filter:** `{'topic': 'criminal_law'}`

**Top-3 unfiltered:**

- score=0.8195, relevant=yes, Bộ luật Hình sự Điều 2 - Cơ sở của trách nhiệm hình sự
  - topic: `criminal_law`, doc_id: `100/2015/QH13`
  - snippet: Điều 2. Cơ sở của trách nhiệm hình sự 1. Chỉ người nào phạm một tội đã được Bộ luật hình sự quy định mới phải chịu trách nhiệm hình sự. 2. Chỉ pháp nhân thương mại nào phạm một tội đã được quy định tại Điều 76 của Bộ luật này mới phải chịu trách nhiệm hình sự.
- score=0.7605, relevant=no, Bộ luật Hình sự Điều 16 - Tự ý nửa chừng chấm dứt việc phạm tội
  - topic: `criminal_law`, doc_id: `100/2015/QH13`
  - snippet: Điều 16. Tự ý nửa chừng chấm dứt việc phạm tội Tự ý nửa chừng chấm dứt việc phạm tội là tự mình không thực hiện tội phạm đến cùng, tuy không có gì ngăn cản. Người tự ý nửa chừng chấm dứt việc phạm tội được miễn trách nhiệm hình sự về tội định phạm; nếu hành vi
- score=0.7583, relevant=no, Bộ luật Hình sự Điều 1 - Nhiệm vụ của Bộ luật hình sự
  - topic: `criminal_law`, doc_id: `100/2015/QH13`
  - snippet: Điều 1. Nhiệm vụ của Bộ luật hình sự Bộ luật hình sự có nhiệm vụ bảo vệ chủ quyền quốc gia, an ninh của đất nước, bảo vệ chế độ xã hội chủ nghĩa, quyền con người, quyền công dân, bảo vệ quyền bình đẳng giữa đồng bào các dân tộc, bảo vệ lợi ích của Nhà nước, tổ

**Top-3 filtered + legal rerank:**

- score=1.5338, relevant=yes, Bộ luật Hình sự Điều 2 - Cơ sở của trách nhiệm hình sự
  - topic: `criminal_law`, doc_id: `100/2015/QH13`
  - snippet: Điều 2. Cơ sở của trách nhiệm hình sự 1. Chỉ người nào phạm một tội đã được Bộ luật hình sự quy định mới phải chịu trách nhiệm hình sự. 2. Chỉ pháp nhân thương mại nào phạm một tội đã được quy định tại Điều 76 của Bộ luật này mới phải chịu trách nhiệm hình sự.
- score=0.9511, relevant=no, Bộ luật Hình sự Điều 1 - Nhiệm vụ của Bộ luật hình sự
  - topic: `criminal_law`, doc_id: `100/2015/QH13`
  - snippet: Điều 1. Nhiệm vụ của Bộ luật hình sự Bộ luật hình sự có nhiệm vụ bảo vệ chủ quyền quốc gia, an ninh của đất nước, bảo vệ chế độ xã hội chủ nghĩa, quyền con người, quyền công dân, bảo vệ quyền bình đẳng giữa đồng bào các dân tộc, bảo vệ lợi ích của Nhà nước, tổ
- score=0.9042, relevant=no, Bộ luật Hình sự Điều 74 - Áp dụng quy định của Bộ luật hình sự đối với pháp nhân thương mại phạm tội
  - topic: `criminal_law`, doc_id: `100/2015/QH13`
  - snippet: Điều 74. Áp dụng quy định của Bộ luật hình sự đối với pháp nhân thương mại phạm tội Pháp nhân thương mại phạm tội phải chịu trách nhiệm hình sự theo những quy định của Chương này; theo quy định khác của Phần thứ nhất của Bộ luật này không trái với quy định của

## Query 5

**Query:** Bộ luật Tố tụng hình sự có nhiệm vụ gì?

**Gold target:** `101/2015/QH13` - Điều 1

**Gold answer:** Bộ luật Tố tụng hình sự quy định trình tự, thủ tục tiếp nhận, giải quyết tố giác/tin báo về tội phạm, khởi tố, điều tra, truy tố, xét xử và thi hành án hình sự.

**Metadata filter:** `{'topic': 'criminal_procedure'}`

**Top-3 unfiltered:**

- score=0.6744, relevant=no, Bộ luật Tố tụng hình sự Điều 7 - Bảo đảm pháp chế xã hội chủ nghĩa trong tố tụng hình sự
  - topic: `criminal_procedure`, doc_id: `101/2015/QH13`
  - snippet: Điều 7. Bảo đảm pháp chế xã hội chủ nghĩa trong tố tụng hình sự Mọi hoạt động tố tụng hình sự phải được thực hiện theo quy định của Bộ luật này. Không được giải quyết nguồn tin về tội phạm, khởi tố, điều tra, truy tố, xét xử ngoài những căn cứ và trình tự, thủ
- score=0.6550, relevant=yes, Bộ luật Tố tụng hình sự Điều 1 - Phạm vi điều chỉnh
  - topic: `criminal_procedure`, doc_id: `101/2015/QH13`
  - snippet: Điều 1. Phạm vi điều chỉnh Bộ luật tố tụng hình sự quy định trình tự, thủ tục tiếp nhận, giải quyết nguồn tin về tội phạm, khởi tố, điều tra, truy tố, xét xử và một số thủ tục thi hành án hình sự; nhiệm vụ, quyền hạn và mối quan hệ giữa các cơ quan có thẩm quy
- score=0.6471, relevant=no, Luật Tổ chức cơ quan điều tra hình sự Điều 10 - Nhiệm vụ, quyền hạn của cơ quan được giao nhiệm vụ tiến hành một số hoạt động điều tra
  - topic: `criminal_investigation`, doc_id: `99/2015/QH13`
  - snippet: Điều 10. Nhiệm vụ, quyền hạn của cơ quan được giao nhiệm vụ tiến hành một số hoạt động điều tra Cơ quan được giao nhiệm vụ tiến hành một số hoạt động điều tra khi thực hiện nhiệm vụ trong lĩnh vực quản lý của mình mà tiếp nhận tố giác, tin báo về tội phạm hoặc

**Top-3 filtered + legal rerank:**

- score=1.2800, relevant=yes, Bộ luật Tố tụng hình sự Điều 1 - Phạm vi điều chỉnh
  - topic: `criminal_procedure`, doc_id: `101/2015/QH13`
  - snippet: Điều 1. Phạm vi điều chỉnh Bộ luật tố tụng hình sự quy định trình tự, thủ tục tiếp nhận, giải quyết nguồn tin về tội phạm, khởi tố, điều tra, truy tố, xét xử và một số thủ tục thi hành án hình sự; nhiệm vụ, quyền hạn và mối quan hệ giữa các cơ quan có thẩm quy
- score=0.8801, relevant=no, Bộ luật Tố tụng hình sự Điều 2 - Nhiệm vụ của Bộ luật tố tụng hình sự
  - topic: `criminal_procedure`, doc_id: `101/2015/QH13`
  - snippet: Điều 2. Nhiệm vụ của Bộ luật tố tụng hình sự Bộ luật tố tụng hình sự có nhiệm vụ bảo đảm phát hiện chính xác và xử lý công minh, kịp thời mọi hành vi phạm tội, phòng ngừa, ngăn chặn tội phạm, không để lọt tội phạm, không làm oan người vô tội; góp phần bảo vệ c
- score=0.8616, relevant=no, Bộ luật Tố tụng hình sự Điều 4 - Giải thích từ ngữ
  - topic: `criminal_procedure`, doc_id: `101/2015/QH13`
  - snippet: Điều 4. Giải thích từ ngữ 1. Trong Bộ luật này, các từ ngữ dưới đây được hiểu như sau: a) Cơ quan có thẩm quyền tiến hành tố tụng gồm cơ quan tiến hành tố tụng và cơ quan được giao nhiệm vụ tiến hành một số hoạt động điều tra. b) Người có thẩm quyền tiến hành 

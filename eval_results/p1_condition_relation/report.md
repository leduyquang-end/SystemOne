# Báo cáo test P1 - condition relation

- Dữ liệu đầu vào model: `p1_condition_relation_poc_200_1.csv`
- Dữ liệu nguồn (nối metadata): `p1_condition_relation_poc_200.csv`
- Số mẫu: **200**
- Checkpoint: auto-routing
- Device: cpu
- Revisions: `{"multilingual": "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851"}`
- Batch: batch_size=8, chunks=25, max_chunk=8

## 1. Kết quả tổng

| metric | value |
|---|---|
| choice_accuracy | 0.2800 |
| cost_per_decision_p50_ms | 403.5979 |
| cost_per_decision_p95_ms | 976.2142 |
| ece | 0.4235 |
| latency_p50_ms | 3228.7829 |
| latency_p95_ms | 7809.7140 |
| mean_confidence | 0.6995 |

Accuracy tính lại từ predictions.csv: **56/200 = 0.2800** (khớp `choice_accuracy`)

## 2. Ma trận nhầm lẫn (hàng = expected, cột = predicted)

| expected | and | or | insufficient_evidence | (trả lời rỗng) | tổng | đúng | sai |
|---|---|---|---|---|---|---|---|
| and | 3 | 121 | 3 | 0 | 127 | 3 | 124 |
| or | 0 | 53 | 0 | 0 | 53 | 53 | 0 |
| insufficient_evidence | 0 | 20 | 0 | 0 | 20 | 0 | 20 |

## 3. Kết quả theo `--slice tag`

| tag | choice_accuracy | ece | mean_confidence |
|---|---|---|---|
| curated | 0.1333 | 0.5068 | 0.6401 |
| flat | 0.2718 | 0.4352 | 0.7028 |
| nested_inner | 0.5000 | 0.2318 | 0.5601 |
| nested_outer | 1.0000 | 0.3919 | 0.6081 |
| synthetic_checked | 0.3226 | 0.3993 | 0.7167 |

## 3. Kết quả theo `--slice model`

| model | choice_accuracy | ece | mean_confidence |
|---|---|---|---|
| multilingual | 0.2800 | 0.4235 | 0.6995 |

## 4. Mẫu sai (144/200)

| sample_id | expected | predicted | conf | pair_scope | label_status | left_condition | right_condition |
|---|---|---|---|---|---|---|---|
| CR-001 | and | or | 0.7560 | flat | curated | có trạng thái hoạt động | không bị khóa ghi nợ |
| CR-001S | and | or | 0.7943 | flat | synthetic_checked | không bị khóa ghi nợ | có trạng thái hoạt động |
| CR-001P | and | or | 0.5859 | flat | synthetic_checked | có trạng thái hoạt động | không bị khóa ghi nợ |
| CR-002 | and | or | 0.6794 | flat | curated | không bị khóa ghi nợ | không đồng sở hữu |
| CR-002S | and | or | 0.6914 | flat | synthetic_checked | không đồng sở hữu | không bị khóa ghi nợ |
| CR-002P | and | or | 0.6477 | flat | synthetic_checked | không bị khóa ghi nợ | không đồng sở hữu |
| CR-003 | and | or | 0.6392 | flat | curated | không đồng sở hữu | không có người giám hộ |
| CR-003S | and | or | 0.6432 | flat | synthetic_checked | không có người giám hộ | không đồng sở hữu |
| CR-003P | and | or | 0.6948 | flat | synthetic_checked | không đồng sở hữu | không có người giám hộ |
| CR-004 | and | or | 0.8200 | flat | curated | có trạng thái hoạt động | không bị khóa ghi có |
| CR-004S | and | or | 0.7528 | flat | synthetic_checked | không bị khóa ghi có | có trạng thái hoạt động |
| CR-004P | and | or | 0.6211 | flat | synthetic_checked | có trạng thái hoạt động | không bị khóa ghi có |
| CR-005 | and | or | 0.7342 | flat | curated | không bị khóa ghi có | không đồng sở hữu |
| CR-005S | and | or | 0.7484 | flat | synthetic_checked | không đồng sở hữu | không bị khóa ghi có |
| CR-005P | and | or | 0.6613 | flat | synthetic_checked | không bị khóa ghi có | không đồng sở hữu |
| CR-006 | and | or | 0.6181 | flat | curated | không đồng sở hữu | không có người giám hộ |
| CR-006S | and | or | 0.6432 | flat | synthetic_checked | không có người giám hộ | không đồng sở hữu |
| CR-006P | and | or | 0.6948 | flat | synthetic_checked | không đồng sở hữu | không có người giám hộ |
| CR-007 | and | or | 0.5718 | flat | curated | có CCCD/Thẻ căn cước 12 số | còn hạn sử dụng tính đến ngày đăng ký |
| CR-007S | and | or | 0.7914 | flat | synthetic_checked | còn hạn sử dụng tính đến ngày đăng ký | có CCCD/Thẻ căn cước 12 số |
| CR-007P | and | or | 0.6452 | flat | synthetic_checked | có CCCD/Thẻ căn cước 12 số | còn hạn sử dụng tính đến ngày đăng ký |
| CR-008 | and | or | 0.6492 | flat | curated | đã thu thập STH | được xác thực bởi cơ quan có thẩm quyền (C06) |
| CR-008S | and | or | 0.7595 | flat | synthetic_checked | được xác thực bởi cơ quan có thẩm quyền (C06) | đã thu thập STH |
| CR-008P | and | or | 0.5490 | flat | synthetic_checked | đã thu thập STH | được xác thực bởi cơ quan có thẩm quyền (C06) |
| CR-009F | and | or | 0.6308 | flat | synthetic_checked | KH chưa có thẻ tín dụng | đã có thẻ tín dụng nhưng tất cả đã hết hiệu lực |
| CR-010 | and | or | 0.5721 | nested_inner | curated | tất cả đã hết hiệu lực (trạng thái thẻ tham số động) | toàn bộ dư nợ <= 0 |
| CR-010S | and | or | 0.7793 | flat | synthetic_checked | toàn bộ dư nợ <= 0 | tất cả đã hết hiệu lực (trạng thái thẻ tham số động) |
| CR-010P | and | or | 0.5501 | flat | synthetic_checked | tất cả đã hết hiệu lực (trạng thái thẻ tham số động) | toàn bộ dư nợ <= 0 |
| CR-011S | and | or | 0.6777 | flat | synthetic_checked | ruleDebit = 1 | Loại = Thanh toán |
| CR-011P | and | or | 0.5728 | flat | synthetic_checked | Loại = Thanh toán | ruleDebit = 1 |
| CR-012S | and | or | 0.8205 | flat | synthetic_checked | ccy = VND | ruleDebit = 1 |
| CR-012P | and | or | 0.7006 | flat | synthetic_checked | ruleDebit = 1 | ccy = VND |
| CR-013 | and | or | 0.5728 | flat | curated | ccy = VND | đúng Mã dịch vụ Phong tỏa TK |
| CR-013S | and | or | 0.6760 | flat | synthetic_checked | đúng Mã dịch vụ Phong tỏa TK | ccy = VND |
| CR-013P | and | or | 0.6420 | flat | synthetic_checked | ccy = VND | đúng Mã dịch vụ Phong tỏa TK |
| CR-014 | and | or | 0.9191 | flat | curated | không bị chặn ghi nợ | không đồng sở hữu |
| CR-014S | and | or | 0.6914 | flat | synthetic_checked | không đồng sở hữu | không bị chặn ghi nợ |
| CR-014P | and | or | 0.6529 | flat | synthetic_checked | không bị chặn ghi nợ | không đồng sở hữu |
| CR-015F | and | or | 0.7661 | flat | synthetic_checked | TK CKH không quay vòng (autoRenewalCode = 2 hoặc 0) | TK tích lũy |
| CR-016 | and | or | 0.5090 | nested_inner | curated | > ngày hiện tại | < ngày đến hạn |
| CR-016S | and | or | 0.8373 | flat | synthetic_checked | < ngày đến hạn | > ngày hiện tại |
| CR-016P | and | or | 0.5723 | flat | synthetic_checked | > ngày hiện tại | < ngày đến hạn |
| CR-017F | and | or | 0.5181 | flat | synthetic_checked | TK thu phí ≠ TK phong tỏa | phí = 0 |
| CR-018 | and | insufficient_evidence | 0.7264 | flat | curated | Trạng thái = Đã ghi sổ | Tuỳ chọn hoá đơn ≠ "Không có hoá đơn" |
| CR-018S | and | or | 0.7527 | flat | synthetic_checked | Tuỳ chọn hoá đơn ≠ "Không có hoá đơn" | Trạng thái = Đã ghi sổ |
| CR-018P | and | or | 0.6273 | flat | synthetic_checked | Trạng thái = Đã ghi sổ | Tuỳ chọn hoá đơn ≠ "Không có hoá đơn" |
| CR-019 | and | insufficient_evidence | 0.7319 | flat | curated | Tuỳ chọn hoá đơn ≠ "Không có hoá đơn" | Số hoá đơn khai thẳng trên chứng từ = rỗng |
| CR-019S | and | or | 0.5546 | flat | synthetic_checked | Số hoá đơn khai thẳng trên chứng từ = rỗng | Tuỳ chọn hoá đơn ≠ "Không có hoá đơn" |
| CR-019P | and | or | 0.6613 | flat | synthetic_checked | Tuỳ chọn hoá đơn ≠ "Không có hoá đơn" | Số hoá đơn khai thẳng trên chứng từ = rỗng |
| CR-020 | and | insufficient_evidence | 0.6171 | flat | curated | Số hoá đơn khai thẳng trên chứng từ = rỗng | chưa có chứng từ nghiệp vụ khác nào ghi nhận hoá đơn cho nó |
| CR-020S | and | or | 0.5642 | flat | synthetic_checked | chưa có chứng từ nghiệp vụ khác nào ghi nhận hoá đơn cho nó | Số hoá đơn khai thẳng trên chứng từ = rỗng |
| CR-020P | and | or | 0.6042 | flat | synthetic_checked | Số hoá đơn khai thẳng trên chứng từ = rỗng | chưa có chứng từ nghiệp vụ khác nào ghi nhận hoá đơn cho nó |
| CR-021 | and | or | 0.7214 | flat | curated | chứng từ thoả BR-03 | Nhà cung cấp = giá trị đã chọn |
| CR-021S | and | or | 0.4609 | flat | synthetic_checked | Nhà cung cấp = giá trị đã chọn | chứng từ thoả BR-03 |
| CR-021P | and | or | 0.5635 | flat | synthetic_checked | chứng từ thoả BR-03 | Nhà cung cấp = giá trị đã chọn |
| CR-022 | and | or | 0.6386 | flat | curated | Nhà cung cấp = giá trị đã chọn | Loại chứng từ = giá trị đã chọn |
| CR-022S | and | or | 0.6363 | flat | synthetic_checked | Loại chứng từ = giá trị đã chọn | Nhà cung cấp = giá trị đã chọn |
| CR-022P | and | or | 0.6141 | flat | synthetic_checked | Nhà cung cấp = giá trị đã chọn | Loại chứng từ = giá trị đã chọn |
| CR-023 | and | or | 0.5445 | flat | curated | Loại chứng từ = giá trị đã chọn | Ngày HT từ ≤ Ngày hạch toán ≤ đến ngày |
| CR-023S | and | or | 0.7370 | flat | synthetic_checked | Ngày HT từ ≤ Ngày hạch toán ≤ đến ngày | Loại chứng từ = giá trị đã chọn |
| CR-023P | and | or | 0.6593 | flat | synthetic_checked | Loại chứng từ = giá trị đã chọn | Ngày HT từ ≤ Ngày hạch toán ≤ đến ngày |
| CR-024 | and | or | 0.7485 | flat | curated | Ngày HT từ ≤ Ngày hạch toán ≤ đến ngày | khớp từ khoá trên Số chứng từ · Nhà cung cấp · Diễn giải |
| CR-024S | and | or | 0.8323 | flat | synthetic_checked | khớp từ khoá trên Số chứng từ · Nhà cung cấp · Diễn giải | Ngày HT từ ≤ Ngày hạch toán ≤ đến ngày |
| CR-024P | and | or | 0.6986 | flat | synthetic_checked | Ngày HT từ ≤ Ngày hạch toán ≤ đến ngày | khớp từ khoá trên Số chứng từ · Nhà cung cấp · Diễn giải |
| CR-025 | and | or | 0.5181 | flat | curated | đã chọn chứng từ gốc | đã nhập Ngày chứng từ và Ngày hạch toán |
| CR-025S | and | or | 0.5363 | flat | synthetic_checked | đã nhập Ngày chứng từ và Ngày hạch toán | đã chọn chứng từ gốc |
| CR-025P | and | or | 0.4724 | flat | synthetic_checked | đã chọn chứng từ gốc | đã nhập Ngày chứng từ và Ngày hạch toán |
| CR-026 | and | or | 0.4830 | flat | curated | đã nhập Ngày chứng từ và Ngày hạch toán | Ngày hạch toán không thuộc kỳ đã khoá sổ |
| CR-026S | and | or | 0.4808 | flat | synthetic_checked | Ngày hạch toán không thuộc kỳ đã khoá sổ | đã nhập Ngày chứng từ và Ngày hạch toán |
| CR-026P | and | or | 0.4708 | flat | synthetic_checked | đã nhập Ngày chứng từ và Ngày hạch toán | Ngày hạch toán không thuộc kỳ đã khoá sổ |
| CR-027 | and | or | 0.4435 | flat | curated | mọi dòng hàng đã được gán về một tờ hoá đơn | tờ đó đủ Ký hiệu · Số hoá đơn · Ngày hoá đơn |
| CR-027S | and | or | 0.4814 | flat | synthetic_checked | tờ đó đủ Ký hiệu · Số hoá đơn · Ngày hoá đơn | mọi dòng hàng đã được gán về một tờ hoá đơn |
| CR-027P | and | or | 0.5134 | flat | synthetic_checked | mọi dòng hàng đã được gán về một tờ hoá đơn | tờ đó đủ Ký hiệu · Số hoá đơn · Ngày hoá đơn |
| CR-028 | and | or | 0.3840 | flat | curated | mọi dòng có % thuế GTGT | Ngày hạch toán không lớn hơn ngày hiện tại |
| CR-028S | and | or | 0.5779 | flat | synthetic_checked | Ngày hạch toán không lớn hơn ngày hiện tại | mọi dòng có % thuế GTGT |
| CR-028P | and | or | 0.6048 | flat | synthetic_checked | mọi dòng có % thuế GTGT | Ngày hạch toán không lớn hơn ngày hiện tại |
| CR-029 | and | or | 0.5884 | flat | curated | Ký hiệu | Số hoá đơn |
| CR-029S | and | or | 0.5469 | flat | synthetic_checked | Số hoá đơn | Ký hiệu |
| CR-029P | and | or | 0.3805 | flat | synthetic_checked | Ký hiệu | Số hoá đơn |
| CR-030 | and | or | 0.5042 | flat | curated | Số hoá đơn | Ngày hoá đơn |
| CR-030S | and | or | 0.6555 | flat | synthetic_checked | Ngày hoá đơn | Số hoá đơn |
| CR-031 | and | or | 0.6203 | flat | curated | chứng từ ở trạng thái Chưa ghi sổ | Ngày hạch toán không thuộc kỳ đã khoá sổ |
| CR-031S | and | or | 0.8185 | flat | synthetic_checked | Ngày hạch toán không thuộc kỳ đã khoá sổ | chứng từ ở trạng thái Chưa ghi sổ |
| CR-031P | and | or | 0.6129 | flat | synthetic_checked | chứng từ ở trạng thái Chưa ghi sổ | Ngày hạch toán không thuộc kỳ đã khoá sổ |
| CR-032 | and | or | 0.8367 | flat | curated | chứng từ ở trạng thái Chưa ghi sổ | Ngày hạch toán không thuộc kỳ đã khoá sổ |
| CR-032S | and | or | 0.8185 | flat | synthetic_checked | Ngày hạch toán không thuộc kỳ đã khoá sổ | chứng từ ở trạng thái Chưa ghi sổ |
| CR-032P | and | or | 0.6129 | flat | synthetic_checked | chứng từ ở trạng thái Chưa ghi sổ | Ngày hạch toán không thuộc kỳ đã khoá sổ |
| CR-033F | and | or | 0.5938 | flat | synthetic_checked | 1 cá nhân | 1 bộ phận |
| CR-034 | and | or | 0.5879 | flat | curated | đã được khai báo trên SalesGO | đang ở trạng thái hoạt động |
| CR-034S | and | or | 0.8144 | flat | synthetic_checked | đang ở trạng thái hoạt động | đã được khai báo trên SalesGO |
| CR-034P | and | or | 0.6463 | flat | synthetic_checked | đã được khai báo trên SalesGO | đang ở trạng thái hoạt động |
| CR-035 | and | or | 0.7016 | flat | curated | đã được khai báo trên SalesGO | đang ở trạng thái hoạt động |
| CR-035S | and | or | 0.8144 | flat | synthetic_checked | đang ở trạng thái hoạt động | đã được khai báo trên SalesGO |
| CR-035P | and | or | 0.6463 | flat | synthetic_checked | đã được khai báo trên SalesGO | đang ở trạng thái hoạt động |
| CR-036 | and | or | 0.8728 | flat | curated | field bắt buộc ở phần khởi tạo | trong template của Loại công việc đã chọn |
| CR-036S | and | or | 0.5899 | flat | synthetic_checked | trong template của Loại công việc đã chọn | field bắt buộc ở phần khởi tạo |
| CR-036P | and | or | 0.7043 | flat | synthetic_checked | field bắt buộc ở phần khởi tạo | trong template của Loại công việc đã chọn |
| CR-037 | and | or | 0.5979 | flat | curated | được nhập/chọn đầy đủ | hợp lệ |
| CR-037S | and | or | 0.8104 | flat | synthetic_checked | hợp lệ | được nhập/chọn đầy đủ |
| CR-037P | and | or | 0.7392 | flat | synthetic_checked | được nhập/chọn đầy đủ | hợp lệ |
| CR-038 | and | or | 0.7546 | flat | curated | được định danh | xác thực sinh trắc học |
| CR-038S | and | or | 0.8803 | flat | synthetic_checked | xác thực sinh trắc học | được định danh |
| CR-038P | and | or | 0.6723 | flat | synthetic_checked | được định danh | xác thực sinh trắc học |
| CR-039 | and | or | 0.6445 | flat | curated | xác thực sinh trắc học | liên kết tài khoản ngân hàng |
| CR-039S | and | or | 0.7131 | flat | synthetic_checked | liên kết tài khoản ngân hàng | xác thực sinh trắc học |
| CR-039P | and | or | 0.4038 | flat | synthetic_checked | xác thực sinh trắc học | liên kết tài khoản ngân hàng |
| CR-040 | and | or | 0.6925 | flat | curated | tồn tại | ở trạng thái hoạt động |
| CR-040S | and | or | 0.7607 | flat | synthetic_checked | ở trạng thái hoạt động | tồn tại |
| CR-040P | and | or | 0.4526 | flat | synthetic_checked | tồn tại | ở trạng thái hoạt động |
| CR-041 | and | or | 0.5349 | flat | curated | ở trạng thái hoạt động | có hỗ trợ rút tiền về Ngân hàng liên kết |
| CR-041S | and | or | 0.5119 | flat | synthetic_checked | có hỗ trợ rút tiền về Ngân hàng liên kết | ở trạng thái hoạt động |
| CR-041P | and | or | 0.3864 | flat | synthetic_checked | ở trạng thái hoạt động | có hỗ trợ rút tiền về Ngân hàng liên kết |
| CR-042 | and | or | 0.7939 | flat | curated | không đồng sở hữu | không bị lien/lost/blocked |
| CR-042S | and | or | 0.6001 | flat | synthetic_checked | không bị lien/lost/blocked | không đồng sở hữu |
| CR-042P | and | or | 0.4943 | flat | synthetic_checked | không đồng sở hữu | không bị lien/lost/blocked |
| CR-043 | and | or | 0.8045 | flat | curated | có Tên | Địa chỉ |
| CR-043S | and | or | 0.7944 | flat | synthetic_checked | Địa chỉ | có Tên |
| CR-043P | and | or | 0.5610 | flat | synthetic_checked | có Tên | Địa chỉ |
| CR-044 | and | or | 0.4547 | flat | curated | >= ngày hóa đơn gốc | <= ngày hiện tại |
| CR-044S | and | or | 0.7955 | flat | synthetic_checked | <= ngày hiện tại | >= ngày hóa đơn gốc |
| CR-044P | and | or | 0.7529 | flat | synthetic_checked | >= ngày hóa đơn gốc | <= ngày hiện tại |
| CR-045 | and | or | 0.4040 | flat | curated | <= ngày hiện tại | >= T-1 |
| CR-045S | and | or | 0.6069 | flat | synthetic_checked | >= T-1 | <= ngày hiện tại |
| CR-045P | and | or | 0.5581 | flat | synthetic_checked | <= ngày hiện tại | >= T-1 |
| CR-U001 | insufficient_evidence | or | 0.6192 | flat | synthetic_checked | có trạng thái hoạt động | không bị khóa ghi nợ |
| CR-U002 | insufficient_evidence | or | 0.5164 | flat | synthetic_checked | không bị khóa ghi nợ | không đồng sở hữu |
| CR-U003 | insufficient_evidence | or | 0.5911 | flat | synthetic_checked | không đồng sở hữu | không có người giám hộ |
| CR-U004 | insufficient_evidence | or | 0.7208 | flat | synthetic_checked | có trạng thái hoạt động | không bị khóa ghi có |
| CR-U005 | insufficient_evidence | or | 0.6974 | flat | synthetic_checked | không bị khóa ghi có | không đồng sở hữu |
| CR-U006 | insufficient_evidence | or | 0.5911 | flat | synthetic_checked | không đồng sở hữu | không có người giám hộ |
| CR-U007 | insufficient_evidence | or | 0.7235 | flat | synthetic_checked | có CCCD/Thẻ căn cước 12 số | còn hạn sử dụng tính đến ngày đăng ký |
| CR-U008 | insufficient_evidence | or | 0.7504 | flat | synthetic_checked | đã thu thập STH | được xác thực bởi cơ quan có thẩm quyền (C06) |
| CR-U009 | insufficient_evidence | or | 0.6959 | flat | synthetic_checked | KH chưa có thẻ tín dụng | đã có thẻ tín dụng nhưng tất cả đã hết hiệu lực |
| CR-U010 | insufficient_evidence | or | 0.6933 | flat | synthetic_checked | tất cả đã hết hiệu lực (trạng thái thẻ tham số động) | toàn bộ dư nợ <= 0 |
| CR-U011 | insufficient_evidence | or | 0.7524 | flat | synthetic_checked | Loại = Thanh toán | ruleDebit = 1 |
| CR-U012 | insufficient_evidence | or | 0.6407 | flat | synthetic_checked | ruleDebit = 1 | ccy = VND |
| CR-U013 | insufficient_evidence | or | 0.7061 | flat | synthetic_checked | ccy = VND | đúng Mã dịch vụ Phong tỏa TK |
| CR-U014 | insufficient_evidence | or | 0.6498 | flat | synthetic_checked | không bị chặn ghi nợ | không đồng sở hữu |
| CR-U015 | insufficient_evidence | or | 0.7744 | flat | synthetic_checked | TK CKH không quay vòng (autoRenewalCode = 2 hoặc 0) | TK tích lũy |
| CR-U016 | insufficient_evidence | or | 0.8589 | flat | synthetic_checked | > ngày hiện tại | < ngày đến hạn |
| CR-U017 | insufficient_evidence | or | 0.6551 | flat | synthetic_checked | TK thu phí ≠ TK phong tỏa | phí = 0 |
| CR-U018 | insufficient_evidence | or | 0.8988 | flat | synthetic_checked | Trạng thái = Đã ghi sổ | Tuỳ chọn hoá đơn ≠ "Không có hoá đơn" |
| CR-U019 | insufficient_evidence | or | 0.8262 | flat | synthetic_checked | Tuỳ chọn hoá đơn ≠ "Không có hoá đơn" | Số hoá đơn khai thẳng trên chứng từ = rỗng |
| CR-U020 | insufficient_evidence | or | 0.7655 | flat | synthetic_checked | Số hoá đơn khai thẳng trên chứng từ = rỗng | chưa có chứng từ nghiệp vụ khác nào ghi nhận hoá đơn cho nó |

Tổng hợp lỗi (expected -> predicted):

| expected | predicted | so mau |
|---|---|---|
| and | or | 121 |
| insufficient_evidence | or | 20 |
| and | insufficient_evidence | 3 |

## 5. Phân bố nhãn

| expected | so mau | ty le |
|---|---|---|
| and | 127 | 63.5% |
| or | 53 | 26.5% |
| insufficient_evidence | 20 | 10.0% |

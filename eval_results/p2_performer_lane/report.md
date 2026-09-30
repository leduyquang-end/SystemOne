# Báo cáo test P2 - performer lane

- Dữ liệu đầu vào model: `p2_performer_lane_poc_200_1.csv`
- Dữ liệu nguồn (nối metadata): `p2_performer_lane_poc_200.csv`
- Số mẫu: **200** (3 câu hỏi/mẫu = 600 case)
- Device: cpu
- Revisions: `{"multilingual": "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851"}`
- Batch: batch_size=None, chunks=200, max_chunk=1

## 1. Kết quả tổng (laya-evals)

| metric | value |
|---|---|
| choice_accuracy | 0.5475 |
| cost_per_decision_p50_ms | 2065.3490 |
| cost_per_decision_p95_ms | 3089.7434 |
| ece | 0.3518 |
| latency_p50_ms | 2065.3490 |
| latency_p95_ms | 3089.7434 |
| mean_confidence | 0.7918 |
| noul_accuracy | 0.2250 |

## 2. Accuracy theo từng câu hỏi

| câu hỏi | đúng/tổng | accuracy |
|---|---|---|
| performer (chọn cấu phần) | 95/200 | 0.4750 |
| evidence (verb/object/context) | 124/200 | 0.6200 |
| mixed_lanes (noul) | 45/200 | 0.2250 |

## 3. Ma trận nhầm lẫn - performer

| expected | insufficient_evidence | merchant_app_client | merchant_app_server | pmkt_core | pmkt_frontend | vcb_mobile | vcb_server | (trống) | tổng | đúng | sai |
|---|---|---|---|---|---|---|---|---|---|---|---|
| insufficient_evidence | 1 | 0 | 1 | 0 | 5 | 0 | 0 | 0 | 7 | 1 | 6 |
| merchant_app_client | 21 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 25 | 2 | 23 |
| merchant_app_server | 7 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 9 | 1 | 8 |
| pmkt_core | 0 | 0 | 0 | 0 | 33 | 0 | 0 | 0 | 33 | 0 | 33 |
| pmkt_frontend | 1 | 0 | 0 | 0 | 42 | 0 | 0 | 0 | 43 | 42 | 1 |
| vcb_mobile | 1 | 0 | 0 | 0 | 0 | 14 | 19 | 0 | 34 | 14 | 20 |
| vcb_server | 1 | 0 | 0 | 0 | 0 | 13 | 35 | 0 | 49 | 35 | 14 |

## 4. Ma trận nhầm lẫn - evidence

| expected | verb | object | context | (trống) | tổng | đúng | sai |
|---|---|---|---|---|---|---|---|
| verb | 121 | 24 | 44 | 0 | 189 | 121 | 68 |
| object | 2 | 0 | 0 | 0 | 2 | 0 | 2 |
| context | 6 | 0 | 3 | 0 | 9 | 3 | 6 |

## 5. Ma trận nhầm lẫn - mixed_lanes

| expected | true | false | tổng | đúng | sai |
|---|---|---|---|---|---|
| true | 45 | 0 | 45 | 45 | 0 |
| false | 155 | 0 | 155 | 0 | 155 |

## 6. Kết quả theo `--slice qid`

| qid | choice_accuracy | ece | mean_confidence | noul_accuracy |
|---|---|---|---|---|
| evidence | 0.6200 | 0.0693 | 0.6435 | - |
| mixed_lanes | - | 0.7750 | 1.0000 | 0.2250 |
| performer | 0.4750 | 0.2571 | 0.7321 | - |

## 6. Kết quả theo `--slice tag`

| tag | choice_accuracy | ece | mean_confidence | noul_accuracy |
|---|---|---|---|---|
| dev | 0.6331 | 0.3710 | 0.8155 | 0.1694 |
| eval | 0.4079 | 0.3761 | 0.7533 | 0.3158 |
| needs_domain_review | 0.5487 | 0.3486 | 0.7913 | 0.2308 |
| spec_confirmed | 0.5000 | 0.5553 | 0.8116 | 0.0000 |

## 6. Kết quả theo `--slice model`

| model | choice_accuracy | ece | mean_confidence | noul_accuracy |
|---|---|---|---|---|
| multilingual | 0.5475 | 0.3518 | 0.7918 | 0.2250 |

## 7. Mẫu sai performer (105/200)

| sample_id | split | expected | predicted | conf | label_status | variant_type | bước con |
|---|---|---|---|---|---|---|---|
| T15-001 | dev | pmkt_core | pmkt_frontend | 0.9896 | spec_confirmed | real | kế thừa toàn bộ dòng hàng sang bảng Dòng hàng trên hoá đơn theo quan h |
| T15-002 | eval | vcb_server | vcb_mobile | 0.6893 | spec_confirmed | real | Thực hiện kiểm tra thông tin thụ hưởng |
| T15-004 | eval | vcb_mobile | vcb_server | 0.4986 | spec_confirmed | real | hiển thị màn hình kết quả giao dịch |
| T15-008 | dev | insufficient_evidence | pmkt_frontend | 0.9052 | needs_domain_review | source_excerpt | Điều hướng theo số doanh nghiệp người dùng thuộc về |
| T15-010 | dev | pmkt_core | pmkt_frontend | 1.0000 | needs_domain_review | real | * Cập nhật thông tin doanh nghiệp: gắn người khai báo làm người quản t |
| T15-011 | dev | pmkt_core | pmkt_frontend | 1.0000 | needs_domain_review | real | Validate toàn bộ form, kiểm tra MST đã tồn tại hay chưa |
| T15-012 | dev | pmkt_core | pmkt_frontend | 1.0000 | needs_domain_review | real | Validate toàn bộ form, kiểm tra MST đã tồn tại hay chưa; ; * Cập nhật  |
| T15-015 | eval | pmkt_core | pmkt_frontend | 0.7025 | needs_domain_review | real | kiểm tra MST đã tồn tại trên hệ thống chưa (BR 13) |
| T15-017 | eval | merchant_app_client | merchant_app_server | 0.5173 | needs_domain_review | real | Với user thuộc Merchant là Cá nhân/ Hộ kinh doanh hoặc là Công ty/ Doa |
| T15-018 | eval | merchant_app_client | insufficient_evidence | 0.4642 | needs_domain_review | real | Với user thuộc Merchant là Công ty/ Doanh nghiệp và chưa xác thực C06  |
| T15-020 | eval | merchant_app_client | insufficient_evidence | 0.4065 | needs_domain_review | real | Hiển thị popup chọn CIF Công nợ ; Tham chiếu theo Quy tắc nghiệp vụ về |
| T15-021 | eval | merchant_app_client | insufficient_evidence | 0.5661 | needs_domain_review | real | Hiển thị popup chọn tài khoản Công nợ |
| T15-022 | eval | merchant_app_client | insufficient_evidence | 0.5943 | needs_domain_review | real | Hiển thị popup chọn tài khoản Công nợ ; Tham chiếu theo Quy tắc nghiệp |
| T15-023 | eval | merchant_app_client | insufficient_evidence | 0.3908 | needs_domain_review | real | Hiển thị popup chọn ngân hàng liên kết Ví |
| T15-024 | eval | merchant_app_server | insufficient_evidence | 0.6086 | needs_domain_review | real | Kiểm tra thông tin rút và hiển thị màn hình xác nhận giao dịch |
| T15-025 | eval | merchant_app_server | insufficient_evidence | 0.4796 | needs_domain_review | real | Kiểm tra thông tin rút và hiển thị màn hình xác nhận giao dịch ; Tham  |
| T15-026 | eval | insufficient_evidence | merchant_app_server | 0.3634 | needs_domain_review | source_excerpt | Luồng xử lý xác thực SoftOTP hay SMSOTP sẽ theo logic xác thực giao dị |
| T15-027 | eval | merchant_app_client | insufficient_evidence | 0.7209 | needs_domain_review | real | Với trường hợp giao dịch yêu cầu xác thực SMS OTP: hiển thị màn hình n |
| T15-028 | eval | merchant_app_client | insufficient_evidence | 0.5559 | needs_domain_review | real | Với trường hợp giao dịch yêu cầu xác thực SoftOTP: hiển thị màn hình n |
| T15-029 | eval | merchant_app_client | insufficient_evidence | 0.6548 | needs_domain_review | real | Với trường hợp giao dịch yêu cầu xác thực SoftOTP: hiển thị màn hình n |
| T15-030 | eval | merchant_app_server | insufficient_evidence | 0.3583 | needs_domain_review | real | Sau khi xác thực thành công, xử lý rút tiền về ngân hàng liên kết ví v |
| T15-033 | dev | vcb_mobile | vcb_server | 0.5004 | needs_domain_review | real | Hiển thị màn hình Thẻ lệ sản phẩm và cam kết |
| T15-034 | dev | vcb_mobile | vcb_server | 0.9650 | needs_domain_review | real | Hiển thị màn hình Đăng ký phát hành thẻ tín dụng cầm cố tiết kiệm (màn |
| T15-035 | dev | vcb_mobile | vcb_server | 0.4947 | needs_domain_review | real | Hiển thị MH Xác nhận giao dịch |
| T15-039 | dev | vcb_mobile | vcb_server | 0.6074 | needs_domain_review | real | Hiển thị màn hình khởi tạo giao dịch thanh toán bao gồm: |
| T15-043 | dev | vcb_server | vcb_mobile | 0.5063 | needs_domain_review | real | Thực hiện thanh toán cho giao dịch của khách hàng và hiển thị màn hình |
| T15-053 | dev | pmkt_core | pmkt_frontend | 0.7877 | needs_domain_review | real | Ghi nhận giá trị vừa nhập, không vẽ lại màn |
| T15-054 | dev | insufficient_evidence | pmkt_frontend | 0.6174 | needs_domain_review | source_excerpt | Ánh bốn trường vừa nhập xuống mọi dòng hàng thuộc tờ hoá đơn đó |
| T15-055 | dev | pmkt_core | pmkt_frontend | 0.9734 | needs_domain_review | real | Tính lại Tiền thuế GTGT của dòng vừa đổi, gợi lại TK thuế GTGT theo tà |
| T15-056 | dev | pmkt_core | pmkt_frontend | 0.9972 | needs_domain_review | real | Tính lại Tiền thuế GTGT của dòng vừa đổi, gợi lại TK thuế GTGT theo tà |
| T15-057 | dev | insufficient_evidence | pmkt_frontend | 0.6858 | needs_domain_review | source_excerpt | Thêm một tờ hoá đơn rỗng |
| T15-058 | dev | pmkt_core | pmkt_frontend | 0.8812 | needs_domain_review | real | Gán dòng về tờ hoá đơn đã chọn, ánh bốn trường hoá đơn của tờ đó xuống |
| T15-059 | dev | insufficient_evidence | pmkt_frontend | 0.8487 | needs_domain_review | source_excerpt | Bỏ tờ hoá đơn đó, trả những dòng đang gán về nó về trạng thái chưa gán |
| T15-060 | dev | pmkt_core | pmkt_frontend | 0.9833 | needs_domain_review | real | sinh bút toán Nợ TK thuế GTGT / Có TK 331 theo tổng tiền thuế |
| T15-062 | dev | pmkt_core | pmkt_frontend | 0.6727 | needs_domain_review | real | Kiểm số chứng từ như bước 34 |
| T15-063 | dev | pmkt_core | pmkt_frontend | 0.9949 | needs_domain_review | real | Kiểm số chứng từ như bước 34; không trùng thì sinh chứng từ nghiệp vụ  |
| T15-065 | dev | insufficient_evidence | pmkt_frontend | 0.6061 | needs_domain_review | source_excerpt | Chứng từ gốc vẫn rời khỏi popup Chọn chứng từ gốc ngay từ lúc lưu nháp |
| T15-068 | dev | pmkt_frontend | insufficient_evidence | 0.4099 | needs_domain_review | real | Quay về màn Hoá đơn |
| T15-069 | dev | pmkt_core | pmkt_frontend | 0.9872 | needs_domain_review | real | Đổi trạng thái về Chưa ghi sổ, hiện thông báo và vẽ lại màn ở chế độ X |
| T15-070 | dev | pmkt_core | pmkt_frontend | 0.9914 | needs_domain_review | real | Đổi trạng thái về Chưa ghi sổ, hiện thông báo và vẽ lại màn ở chế độ X |
| T15-072 | dev | pmkt_core | pmkt_frontend | 0.9885 | needs_domain_review | real | Nút bật theo cùng điều kiện với chế độ Thêm; kiểm số chứng từ không tr |
| T15-073 | dev | pmkt_core | pmkt_frontend | 0.9248 | needs_domain_review | real | kiểm số chứng từ không trùng, không tính chính chứng từ đang sửa |
| T15-075 | dev | pmkt_core | pmkt_frontend | 0.9988 | needs_domain_review | real | Xoá chứng từ nghiệp vụ khác cùng toàn bộ hoá đơn nó giữ, nên những dòn |
| T15-076 | dev | pmkt_core | pmkt_frontend | 0.9955 | needs_domain_review | real | Xoá chứng từ nghiệp vụ khác cùng toàn bộ hoá đơn nó giữ, nên những dòn |
| T15-078 | eval | vcb_mobile | vcb_server | 0.9260 | needs_domain_review | real | Hiển thị màn hình khởi tạo giao dịch với: |
| T15-079 | eval | vcb_mobile | vcb_server | 0.9984 | needs_domain_review | real | Hiển thị màn hình khởi tạo giao dịch với:; - Danh sách tài khoản nguồn |
| T15-081 | eval | vcb_server | vcb_mobile | 0.7353 | needs_domain_review | real | Kiểm tra tính hợp lệ của tài khoản nguồn và tài khoản thụ hưởng, kiểm  |
| T15-082 | eval | vcb_server | vcb_mobile | 0.4660 | needs_domain_review | real | Thực hiện xác thực giao dịch cho khách hàng, hạch toán tài giao dịch,  |
| T15-083 | eval | vcb_mobile | vcb_server | 0.6437 | needs_domain_review | real | Hiển thị màn hình khởi tạo giao dịch với danh sách tài khoản nguồn hợp |
| T15-092 | dev | vcb_mobile | vcb_server | 1.0000 | needs_domain_review | real | 7/ Hiển thị màn hình Thẻ lệ sản phẩm và cam kết |
| T15-094 | dev | vcb_server | insufficient_evidence | 0.4683 | needs_domain_review | real | 2/ Truy vấn danh sách tài khoản FD từ core bank trả về và lọc lấy tài  |
| T15-095 | dev | vcb_server | vcb_mobile | 0.5166 | needs_domain_review | real | 3/ Truy vấn danh sách DD từ core bank trả về và lọc lấy danh sách tài  |
| T15-096 | dev | vcb_mobile | insufficient_evidence | 0.6076 | needs_domain_review | real | 6/ Hiển thị màn hình Đăng ký phát hành thẻ tín dụng cầm cố tiết kiệm ( |
| T15-103 | dev | vcb_mobile | vcb_server | 0.9313 | needs_domain_review | real | 7/ Hiển thị MH Xác nhận giao dịch |
| T15-108 | dev | vcb_server | vcb_mobile | 0.4055 | needs_domain_review | real | 2/ Xử lý xác nhận giao dịch |
| T15-111 | dev | pmkt_core | pmkt_frontend | 0.8506 | needs_domain_review | reduced_context | kế thừa toàn bộ dòng hàng sang bảng Dòng hàng trên hoá đơn theo quan h |
| T15-112 | eval | vcb_server | vcb_mobile | 0.4990 | needs_domain_review | paraphrase | Thực hiện đối chiếu thông tin thụ hưởng |
| T15-113 | eval | vcb_server | vcb_mobile | 0.5573 | needs_domain_review | reduced_context | Thực hiện kiểm tra thông tin thụ hưởng |
| T15-116 | eval | vcb_mobile | vcb_server | 0.9839 | needs_domain_review | paraphrase | cho người dùng thấy màn hình kết quả giao dịch |
| T15-118 | eval | vcb_server | vcb_mobile | 0.9352 | needs_domain_review | reduced_context | thông báo kết quả cho KH qua OTT và email |
| T15-122 | dev | pmkt_core | pmkt_frontend | 0.7738 | needs_domain_review | reduced_context | * Cập nhật thông tin doanh nghiệp: gắn người khai báo làm người quản t |
| T15-123 | dev | pmkt_core | pmkt_frontend | 1.0000 | needs_domain_review | paraphrase | Validate toàn bộ form, đối chiếu MST đã tồn tại hay chưa |
| T15-124 | dev | pmkt_core | pmkt_frontend | 0.9958 | needs_domain_review | reduced_context | Validate toàn bộ form, kiểm tra MST đã tồn tại hay chưa |
| T15-125 | dev | pmkt_core | pmkt_frontend | 1.0000 | needs_domain_review | paraphrase | Validate toàn bộ form, đối chiếu MST đã tồn tại hay chưa; ; * Cập nhật |
| T15-128 | eval | pmkt_core | pmkt_frontend | 0.5702 | needs_domain_review | paraphrase | đối chiếu MST đã tồn tại trên hệ thống chưa (BR 13) |
| T15-129 | eval | pmkt_core | pmkt_frontend | 0.5653 | needs_domain_review | reduced_context | kiểm tra MST đã tồn tại trên hệ thống chưa (BR 13) |
| T15-130 | eval | merchant_app_server | insufficient_evidence | 0.3834 | needs_domain_review | paraphrase | Đối chiếu các thông tin về quyền user, tài khoản công nợ hợp lệ để rút |
| T15-131 | eval | merchant_app_server | insufficient_evidence | 0.4181 | needs_domain_review | reduced_context | Kiểm tra các thông tin về quyền user, tài khoản công nợ hợp lệ để rút  |
| T15-132 | eval | merchant_app_client | merchant_app_server | 0.4447 | needs_domain_review | paraphrase | Với user thuộc Merchant là Cá nhân/ Hộ kinh doanh hoặc là Công ty/ Doa |
| T15-134 | eval | merchant_app_client | insufficient_evidence | 0.4062 | needs_domain_review | paraphrase | Với user thuộc Merchant là Công ty/ Doanh nghiệp và chưa xác thực C06  |
| T15-135 | eval | merchant_app_client | insufficient_evidence | 0.7083 | needs_domain_review | reduced_context | Với user thuộc Merchant là Công ty/ Doanh nghiệp và chưa xác thực C06  |
| T15-136 | eval | merchant_app_client | insufficient_evidence | 0.4961 | needs_domain_review | paraphrase | Cho người dùng thấy popup chọn CIF Công nợ |
| T15-137 | eval | merchant_app_client | insufficient_evidence | 0.3994 | needs_domain_review | reduced_context | Hiển thị popup chọn CIF Công nợ |
| T15-138 | eval | merchant_app_client | insufficient_evidence | 0.5932 | needs_domain_review | paraphrase | Cho người dùng thấy popup chọn CIF Công nợ ; Tham chiếu theo Quy tắc n |
| T15-139 | eval | merchant_app_client | insufficient_evidence | 0.8421 | needs_domain_review | paraphrase | Cho người dùng thấy popup chọn tài khoản Công nợ |
| T15-140 | eval | merchant_app_client | insufficient_evidence | 0.6967 | needs_domain_review | reduced_context | Hiển thị popup chọn tài khoản Công nợ |
| T15-141 | eval | merchant_app_client | insufficient_evidence | 0.8014 | needs_domain_review | paraphrase | Cho người dùng thấy popup chọn tài khoản Công nợ ; Tham chiếu theo Quy |
| T15-142 | eval | merchant_app_client | insufficient_evidence | 0.6239 | needs_domain_review | paraphrase | Cho người dùng thấy popup chọn ngân hàng liên kết Ví |
| T15-143 | eval | merchant_app_server | insufficient_evidence | 0.5360 | needs_domain_review | paraphrase | Kiểm tra thông tin rút và cho người dùng thấy màn hình xác nhận giao d |
| T15-144 | eval | merchant_app_server | merchant_app_client | 0.5891 | needs_domain_review | paraphrase | Kiểm tra thông tin rút và cho người dùng thấy màn hình xác nhận giao d |
| T15-145 | eval | merchant_app_client | insufficient_evidence | 0.5965 | needs_domain_review | paraphrase | Với trường hợp giao dịch yêu cầu xác thực SMS OTP: cho người dùng thấy |
| T15-146 | eval | merchant_app_client | insufficient_evidence | 0.5936 | needs_domain_review | reduced_context | Với trường hợp giao dịch yêu cầu xác thực SMS OTP: hiển thị màn hình n |
| T15-147 | eval | merchant_app_client | insufficient_evidence | 0.6059 | needs_domain_review | paraphrase | Với trường hợp giao dịch yêu cầu xác thực SoftOTP: cho người dùng thấy |
| T15-148 | eval | merchant_app_client | insufficient_evidence | 0.6436 | needs_domain_review | paraphrase | Với trường hợp giao dịch yêu cầu xác thực SoftOTP: cho người dùng thấy |
| T15-149 | eval | merchant_app_server | insufficient_evidence | 0.4564 | needs_domain_review | paraphrase | Sau khi xác thực thành công, xử lý rút tiền về ngân hàng liên kết ví v |
| T15-152 | dev | vcb_mobile | vcb_server | 0.5829 | needs_domain_review | paraphrase | Cho người dùng thấy màn hình Đăng ký phát hành thẻ tín dụng cầm cố tiế |
| T15-153 | dev | vcb_mobile | vcb_server | 0.6373 | needs_domain_review | paraphrase | Cho người dùng thấy MH Xác nhận giao dịch |
| T15-158 | dev | vcb_mobile | vcb_server | 0.6261 | needs_domain_review | paraphrase | Cho người dùng thấy màn hình khởi tạo giao dịch thanh toán bao gồm: |
| T15-159 | dev | vcb_mobile | vcb_server | 0.6268 | needs_domain_review | reduced_context | Hiển thị màn hình khởi tạo giao dịch thanh toán bao gồm: |
| T15-162 | dev | vcb_mobile | vcb_server | 0.6948 | needs_domain_review | paraphrase | Cho người dùng thấy màn hình popup cho khách hàng thực hiện xác thực g |
| T15-163 | dev | vcb_server | vcb_mobile | 0.5653 | needs_domain_review | paraphrase | Thực hiện thanh toán cho giao dịch của khách hàng và cho người dùng th |
| T15-171 | dev | pmkt_core | pmkt_frontend | 0.5268 | needs_domain_review | paraphrase | Lưu lại giá trị vừa nhập, không vẽ lại màn |
| T15-172 | dev | pmkt_core | pmkt_frontend | 0.9803 | needs_domain_review | paraphrase | Tính lại giá trị Tiền thuế GTGT của dòng vừa đổi, gợi lại TK thuế GTGT |
| T15-173 | dev | pmkt_core | pmkt_frontend | 0.9960 | needs_domain_review | paraphrase | Tính lại giá trị Tiền thuế GTGT của dòng vừa đổi, gợi lại TK thuế GTGT |
| T15-174 | dev | pmkt_core | pmkt_frontend | 0.5767 | needs_domain_review | paraphrase | Gán dòng về tờ hoá đơn đã chọn, ánh bốn trường hoá đơn của tờ đó xuống |
| T15-175 | dev | pmkt_core | pmkt_frontend | 0.4177 | needs_domain_review | reduced_context | sinh bút toán Nợ TK thuế GTGT / Có TK 331 theo tổng tiền thuế |
| T15-176 | dev | pmkt_core | pmkt_frontend | 0.6379 | needs_domain_review | reduced_context | Kiểm số chứng từ như bước 34 |
| T15-180 | dev | pmkt_core | pmkt_frontend | 0.9607 | needs_domain_review | reduced_context | kiểm số chứng từ không trùng, không tính chính chứng từ đang sửa |
| T15-182 | dev | pmkt_core | pmkt_frontend | 0.9460 | needs_domain_review | reduced_context | Xoá chứng từ nghiệp vụ khác cùng toàn bộ hoá đơn nó giữ, nên những dòn |
| T15-184 | eval | vcb_mobile | vcb_server | 0.9541 | needs_domain_review | paraphrase | Cho người dùng thấy màn hình khởi tạo giao dịch với: |
| T15-186 | eval | vcb_mobile | vcb_server | 0.9700 | needs_domain_review | paraphrase | Cho người dùng thấy màn hình khởi tạo giao dịch với:; - Danh sách tài  |
| T15-187 | eval | vcb_server | vcb_mobile | 0.5410 | needs_domain_review | paraphrase | Thực hiện kiểm tra thông tin thụ hưởng và cho người dùng thấy tên ngườ |
| T15-188 | eval | vcb_server | vcb_mobile | 0.8304 | needs_domain_review | paraphrase | Kiểm tra tính hợp lệ của tài khoản nguồn và tài khoản thụ hưởng, kiểm  |
| T15-189 | eval | vcb_server | vcb_mobile | 0.3930 | needs_domain_review | paraphrase | Thực hiện xác thực giao dịch cho khách hàng, hạch toán tài giao dịch,  |
| T15-190 | eval | vcb_mobile | vcb_server | 0.7664 | needs_domain_review | paraphrase | Cho người dùng thấy màn hình khởi tạo giao dịch với danh sách tài khoả |

Tổng hợp lỗi performer (expected -> predicted):

| expected | predicted | so mau |
|---|---|---|
| pmkt_core | pmkt_frontend | 33 |
| merchant_app_client | insufficient_evidence | 21 |
| vcb_mobile | vcb_server | 19 |
| vcb_server | vcb_mobile | 13 |
| merchant_app_server | insufficient_evidence | 7 |
| insufficient_evidence | pmkt_frontend | 5 |
| merchant_app_client | merchant_app_server | 2 |
| insufficient_evidence | merchant_app_server | 1 |
| pmkt_frontend | insufficient_evidence | 1 |
| vcb_server | insufficient_evidence | 1 |
| vcb_mobile | insufficient_evidence | 1 |
| merchant_app_server | merchant_app_client | 1 |

## 8. Mẫu sai evidence (76) và mixed_lanes (155)

| sample_id | expected | predicted | conf |
|---|---|---|---|
| T15-001 | object | verb | 0.7942 |
| T15-005 | context | verb | 0.5961 |
| T15-006 | verb | context | 0.7953 |
| T15-008 | context | verb | 0.4420 |
| T15-009 | verb | context | 0.4745 |
| T15-011 | verb | object | 0.4754 |
| T15-013 | verb | context | 0.5972 |
| T15-017 | verb | object | 0.7161 |
| T15-018 | verb | object | 0.7004 |
| T15-019 | verb | object | 0.6099 |
| T15-020 | verb | object | 0.7742 |
| T15-021 | verb | context | 0.6355 |
| T15-022 | verb | context | 0.6258 |
| T15-023 | verb | context | 0.5219 |
| T15-027 | verb | object | 0.4361 |
| T15-028 | verb | object | 0.5384 |
| T15-031 | verb | context | 0.5216 |
| T15-033 | verb | context | 0.5400 |
| T15-036 | verb | context | 0.4434 |
| T15-042 | verb | context | 0.6464 |
| T15-044 | verb | context | 0.4141 |
| T15-052 | verb | context | 0.4003 |
| T15-054 | context | verb | 0.4684 |
| T15-057 | context | verb | 0.5038 |
| T15-059 | context | verb | 0.5633 |
| T15-060 | verb | object | 0.4808 |
| T15-067 | verb | object | 0.5641 |
| T15-068 | verb | context | 0.6039 |
| T15-082 | verb | context | 0.5530 |
| T15-083 | verb | context | 0.7482 |
| T15-085 | verb | context | 0.4955 |
| T15-110 | verb | object | 0.4876 |
| T15-111 | object | verb | 0.5783 |
| T15-117 | verb | context | 0.4682 |
| T15-118 | context | verb | 0.5889 |
| T15-121 | verb | context | 0.6792 |
| T15-122 | verb | context | 0.5626 |
| T15-123 | verb | object | 0.4240 |
| T15-124 | verb | context | 0.7431 |
| T15-126 | verb | context | 0.5386 |
| T15-127 | verb | context | 0.5331 |
| T15-129 | verb | context | 0.7881 |
| T15-132 | verb | object | 0.7084 |
| T15-133 | verb | object | 0.3695 |
| T15-134 | verb | object | 0.7604 |
| T15-135 | verb | context | 0.4763 |
| T15-136 | verb | object | 0.5642 |
| T15-137 | verb | object | 0.5626 |
| T15-138 | verb | object | 0.5020 |
| T15-139 | verb | context | 0.6319 |
| T15-140 | verb | context | 0.6543 |
| T15-141 | verb | context | 0.5959 |
| T15-142 | verb | context | 0.6941 |
| T15-145 | verb | object | 0.4873 |
| T15-146 | verb | context | 0.5608 |
| T15-147 | verb | object | 0.6998 |
| T15-148 | verb | object | 0.4643 |
| T15-150 | verb | context | 0.4131 |
| T15-151 | verb | context | 0.5615 |
| T15-153 | verb | context | 0.5788 |
| T15-154 | verb | context | 0.6407 |
| T15-159 | verb | context | 0.6328 |
| T15-162 | verb | context | 0.8272 |
| T15-165 | verb | object | 0.5574 |
| T15-168 | verb | object | 0.5424 |
| T15-170 | verb | context | 0.5980 |
| T15-171 | verb | context | 0.6593 |
| T15-178 | verb | object | 0.5472 |
| T15-179 | verb | object | 0.4189 |
| T15-180 | verb | context | 0.4672 |
| T15-181 | verb | context | 0.5908 |
| T15-183 | verb | context | 0.5073 |
| T15-184 | verb | context | 0.7345 |
| T15-185 | verb | context | 0.6245 |
| T15-190 | verb | context | 0.6848 |
| T15-192 | verb | context | 0.6357 |

| sample_id | expected | noul | predicted |
|---|---|---|---|
| T15-001 | false | 1.0000 | true |
| T15-002 | false | 1.0000 | true |
| T15-003 | false | 1.0000 | true |
| T15-004 | false | 1.0000 | true |
| T15-005 | false | 1.0000 | true |
| T15-006 | false | 1.0000 | true |
| T15-007 | false | 1.0000 | true |
| T15-008 | false | 1.0000 | true |
| T15-009 | false | 1.0000 | true |
| T15-010 | false | 1.0000 | true |
| T15-011 | false | 1.0000 | true |
| T15-012 | false | 1.0000 | true |
| T15-013 | false | 1.0000 | true |
| T15-014 | false | 1.0000 | true |
| T15-015 | false | 1.0000 | true |
| T15-016 | false | 1.0000 | true |
| T15-017 | false | 1.0000 | true |
| T15-018 | false | 1.0000 | true |
| T15-019 | false | 1.0000 | true |
| T15-020 | false | 1.0000 | true |
| T15-021 | false | 1.0000 | true |
| T15-022 | false | 1.0000 | true |
| T15-023 | false | 1.0000 | true |
| T15-026 | false | 1.0000 | true |
| T15-027 | false | 1.0000 | true |
| T15-031 | false | 1.0000 | true |
| T15-033 | false | 1.0000 | true |
| T15-034 | false | 1.0000 | true |
| T15-035 | false | 1.0000 | true |
| T15-036 | false | 1.0000 | true |
| T15-037 | false | 1.0000 | true |
| T15-039 | false | 1.0000 | true |
| T15-040 | false | 1.0000 | true |
| T15-041 | false | 1.0000 | true |
| T15-042 | false | 1.0000 | true |
| T15-044 | false | 0.9996 | true |
| T15-049 | false | 1.0000 | true |
| T15-050 | false | 1.0000 | true |
| T15-052 | false | 1.0000 | true |
| T15-053 | false | 1.0000 | true |
| T15-054 | false | 1.0000 | true |
| T15-057 | false | 1.0000 | true |
| T15-058 | false | 1.0000 | true |
| T15-059 | false | 0.9998 | true |
| T15-060 | false | 0.9996 | true |
| T15-061 | false | 1.0000 | true |
| T15-062 | false | 1.0000 | true |
| T15-064 | false | 1.0000 | true |
| T15-065 | false | 1.0000 | true |
| T15-066 | false | 1.0000 | true |
| T15-067 | false | 1.0000 | true |
| T15-068 | false | 0.9999 | true |
| T15-071 | false | 0.9999 | true |
| T15-073 | false | 1.0000 | true |
| T15-074 | false | 1.0000 | true |
| T15-075 | false | 1.0000 | true |
| T15-077 | false | 1.0000 | true |
| T15-078 | false | 1.0000 | true |
| T15-079 | false | 1.0000 | true |
| T15-083 | false | 1.0000 | true |
| T15-086 | false | 1.0000 | true |
| T15-087 | false | 1.0000 | true |
| T15-088 | false | 1.0000 | true |
| T15-089 | false | 1.0000 | true |
| T15-090 | false | 1.0000 | true |
| T15-091 | false | 1.0000 | true |
| T15-092 | false | 1.0000 | true |
| T15-093 | false | 1.0000 | true |
| T15-094 | false | 1.0000 | true |
| T15-095 | false | 1.0000 | true |
| T15-096 | false | 1.0000 | true |
| T15-097 | false | 1.0000 | true |
| T15-098 | false | 1.0000 | true |
| T15-099 | false | 1.0000 | true |
| T15-100 | false | 1.0000 | true |
| T15-101 | false | 1.0000 | true |
| T15-102 | false | 1.0000 | true |
| T15-103 | false | 1.0000 | true |
| T15-104 | false | 1.0000 | true |
| T15-105 | false | 1.0000 | true |
| T15-106 | false | 1.0000 | true |
| T15-108 | false | 1.0000 | true |
| T15-109 | false | 1.0000 | true |
| T15-110 | false | 1.0000 | true |
| T15-111 | false | 0.9999 | true |
| T15-112 | false | 1.0000 | true |
| T15-113 | false | 1.0000 | true |
| T15-114 | false | 1.0000 | true |
| T15-115 | false | 1.0000 | true |
| T15-116 | false | 1.0000 | true |
| T15-117 | false | 1.0000 | true |
| T15-118 | false | 1.0000 | true |
| T15-119 | false | 1.0000 | true |
| T15-120 | false | 1.0000 | true |
| T15-121 | false | 1.0000 | true |
| T15-122 | false | 1.0000 | true |
| T15-123 | false | 0.9999 | true |
| T15-124 | false | 1.0000 | true |
| T15-125 | false | 1.0000 | true |
| T15-126 | false | 1.0000 | true |
| T15-127 | false | 1.0000 | true |
| T15-128 | false | 1.0000 | true |
| T15-129 | false | 1.0000 | true |
| T15-130 | false | 1.0000 | true |
| T15-131 | false | 1.0000 | true |
| T15-132 | false | 1.0000 | true |
| T15-133 | false | 1.0000 | true |
| T15-134 | false | 1.0000 | true |
| T15-135 | false | 1.0000 | true |
| T15-136 | false | 1.0000 | true |
| T15-137 | false | 1.0000 | true |
| T15-138 | false | 1.0000 | true |
| T15-139 | false | 1.0000 | true |
| T15-140 | false | 1.0000 | true |
| T15-141 | false | 1.0000 | true |
| T15-142 | false | 1.0000 | true |
| T15-145 | false | 1.0000 | true |
| T15-146 | false | 1.0000 | true |
| T15-151 | false | 1.0000 | true |
| T15-152 | false | 1.0000 | true |
| T15-153 | false | 1.0000 | true |
| T15-154 | false | 1.0000 | true |
| T15-155 | false | 1.0000 | true |
| T15-156 | false | 1.0000 | true |
| T15-158 | false | 1.0000 | true |
| T15-159 | false | 1.0000 | true |
| T15-160 | false | 1.0000 | true |
| T15-161 | false | 1.0000 | true |
| T15-162 | false | 1.0000 | true |
| T15-164 | false | 0.9999 | true |
| T15-169 | false | 1.0000 | true |
| T15-170 | false | 1.0000 | true |
| T15-171 | false | 1.0000 | true |
| T15-174 | false | 1.0000 | true |
| T15-175 | false | 1.0000 | true |
| T15-176 | false | 0.9999 | true |
| T15-177 | false | 1.0000 | true |
| T15-178 | false | 1.0000 | true |
| T15-179 | false | 1.0000 | true |
| T15-180 | false | 0.9996 | true |
| T15-181 | false | 1.0000 | true |
| T15-182 | false | 1.0000 | true |
| T15-183 | false | 1.0000 | true |
| T15-184 | false | 1.0000 | true |
| T15-185 | false | 1.0000 | true |
| T15-186 | false | 1.0000 | true |
| T15-190 | false | 1.0000 | true |
| T15-193 | false | 1.0000 | true |
| T15-194 | false | 1.0000 | true |
| T15-195 | false | 1.0000 | true |
| T15-196 | false | 1.0000 | true |
| T15-197 | false | 1.0000 | true |
| T15-198 | false | 1.0000 | true |
| T15-199 | false | 1.0000 | true |
| T15-200 | false | 1.0000 | true |

## 9. Phân bố nhãn

| expected_performer | so mau | ty le |
|---|---|---|
| vcb_server | 49 | 24.5% |
| pmkt_frontend | 43 | 21.5% |
| vcb_mobile | 34 | 17.0% |
| pmkt_core | 33 | 16.5% |
| merchant_app_client | 25 | 12.5% |
| merchant_app_server | 9 | 4.5% |
| insufficient_evidence | 7 | 3.5% |

Phân bố evidence / mixed_lanes:

| nhãn | so mau |
|---|---|
| context | 9 |
| object | 2 |
| verb | 189 |
| false | 155 |
| true | 45 |

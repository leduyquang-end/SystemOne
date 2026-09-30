# Đánh giá data Công ty trên chuẩn Laya

Ba tiêu chí: **độ chính xác theo threshold confidence (0.8 / 0.9) - tốc độ - token sử dụng**. Mọi số liệu lấy từ một lần chạy thật trên CPU (PyTorch 2.14.0+cpu, 4 luồng, checkpoint `multilingual` revision `55cf4c4`, dataset `seed=13`).

## 0. Kiểm tra tính vòng

| kiểm tra | giá trị tính lại | giá trị tham chiếu |
|---|---|---|
| P1 gốc - `laya-evals` choice_accuracy | 0.2800 | 0.2800 |
| P2 gốc - `laya-evals` choice_accuracy | 0.5475 | 0.5475 |
| P1 gốc - tính lại từ `usage.csv` | 0.2800 | 0.2800 |
| P1 gốc - ECE tính lại (laya-evals: 0.4235) | 0.4235 | 0.4235 |

## 1. Bộ data

| tập | cột đầu vào | phân bố nhãn | số mẫu |
|---|---|---|---|
| P1 condition relation<br>`Data_cty/p1_condition_relation_poc_200.csv` | `sample_id`, `input_json` (clause_text + left_condition/right_condition), `pair_scope` (flat/nested - chỉ dùng phân tích), `expected_relation`, `label_status` (curated / synthetic_checked) | and 127 - or 53 - insufficient_evidence 20 | 200 |
| P2 performer lane<br>`Data_cty/p2_performer_lane_poc_200.csv` | `sample_id`, `split` (dev 124 / eval 76), `input_json` (câu nghiệp vụ, tác nhân, bước con, cấu phần được chọn, gợi ý), `expected_performer` (ID member - không phải chữ client/server), `expected_evidence` (verb/object/context), `expected_mixed_lanes` (true/false), `label_status` | performer: 7 ID (7-49 mẫu/lớp); evidence: verb 189 - context 9 - object 2; mixed_lanes: false 155 - true 45 | 200 (spec_confirmed 5 / needs_domain_review 195) |


## 2. Tham chiếu chuẩn Laya (3 dataset công khai, cùng checkpoint)

| dataset | số mẫu | acc (laya-evals) | acc (tính lại) | ECE (laya-evals) | ECE (tính lại) | baseline đa số | latency p50 | token tb/mẫu |
|---|---|---|---|---|---|---|---|---|
| ag_news | 200 | 0.9300 | 0.9300 | 0.0608 | 0.0608 | 0.2500 | 291 ms | 122.165 |
| emotion | 200 | 0.5600 | 0.5600 | 0.2671 | 0.2671 | 0.3500 | 243 ms | 100.695 |
| enron_spam | 200 | 0.7950 | 0.7950 | 0.1711 | 0.1711 | 0.5050 | 498 ms | 351.17 |

Chạy với `laya-evals --model multilingual --batch-size 8` để cùng checkpoint với data Công ty; bản gộp đầy đủ nằm trong `standard_benchmarks/*_report.json`.

## 3. Độ chính xác theo threshold confidence

Chỉ trả lời khi `answer_confidence >= threshold`, còn lại **từ chối (abstain)**. `acc@t` tính trên các mẫu **đã trả lời**; coverage là tỷ lệ được trả lời. Hai cột `0.8` và `0.9` in đậm theo yêu cầu.

| tập / câu hỏi | threshold | số case | acc (không gate) | baseline | đã trả lời | coverage | acc@t |
|---|---|---|---|---|---|---|---|
| P1 relation - data cty (gốc) | 0.5 | 200 | 0.2800 | 0.6350 | 183/200 | 91.5% | 0.2951 |
| P1 relation - data cty (gốc) | 0.8 | 200 | 0.2800 | 0.6350 | 58/200 | 29.0% | **0.7069** |
| P1 relation - data cty (gốc) | 0.9 | 200 | 0.2800 | 0.6350 | 15/200 | 7.5% | **0.9333** |
| P1 relation - sửa nhãn (requires_both/requires_either) | 0.5 | 200 | 0.4050 | 0.6350 | 172/200 | 86.0% | 0.4012 |
| P1 relation - sửa nhãn (requires_both/requires_either) | 0.8 | 200 | 0.4050 | 0.6350 | 7/200 | 3.5% | **0.5714** |
| P1 relation - sửa nhãn (requires_both/requires_either) | 0.9 | 200 | 0.4050 | 0.6350 | 1/200 | 0.5% | **0.0000** |
| P1 relation - sửa nhãn + cân bằng lớp | 0.5 | 120 | 0.4583 | 0.3333 | 98/120 | 81.7% | 0.4388 |
| P1 relation - sửa nhãn + cân bằng lớp | 0.8 | 120 | 0.4583 | 0.3333 | 6/120 | 5.0% | **0.6667** |
| P1 relation - sửa nhãn + cân bằng lớp | 0.9 | 120 | 0.4583 | 0.3333 | 0/120 | 0.0% | **-** |
| P2 performer - data cty (gốc) | 0.5 | 200 | 0.4750 | 0.2450 | 166/200 | 83.0% | 0.5000 |
| P2 performer - data cty (gốc) | 0.8 | 200 | 0.4750 | 0.2450 | 85/200 | 42.5% | **0.5647** |
| P2 performer - data cty (gốc) | 0.9 | 200 | 0.4750 | 0.2450 | 70/200 | 35.0% | **0.5571** |
| P2 evidence - data cty (gốc) | 0.5 | 200 | 0.6200 | 0.9450 | 166/200 | 83.0% | 0.6627 |
| P2 evidence - data cty (gốc) | 0.8 | 200 | 0.6200 | 0.9450 | 34/200 | 17.0% | **0.9706** |
| P2 evidence - data cty (gốc) | 0.9 | 200 | 0.6200 | 0.9450 | 12/200 | 6.0% | **1.0000** |
| P2 mixed_lanes noul - data cty (gốc) | 0.5 | 200 | 0.2250 | 0.7750 | 200/200 | 100.0% | 0.2250 |
| P2 mixed_lanes noul - data cty (gốc) | 0.8 | 200 | 0.2250 | 0.7750 | 200/200 | 100.0% | **0.2250** |
| P2 mixed_lanes noul - data cty (gốc) | 0.9 | 200 | 0.2250 | 0.7750 | 200/200 | 100.0% | **0.2250** |
| P2 3 câu hỏi - data cty (gốc) | 0.5 | 600 | 0.4400 | 0.3150 | 532/600 | 88.7% | 0.4474 |
| P2 3 câu hỏi - data cty (gốc) | 0.8 | 600 | 0.4400 | 0.3150 | 319/600 | 53.2% | **0.3950** |
| P2 3 câu hỏi - data cty (gốc) | 0.9 | 600 | 0.4400 | 0.3150 | 282/600 | 47.0% | **0.3404** |
| P2 3 câu hỏi - sửa nhãn (mixed_lanes -> choice) | 0.5 | 600 | 0.6183 | 0.3150 | 532/600 | 88.7% | 0.6485 |
| P2 3 câu hỏi - sửa nhãn (mixed_lanes -> choice) | 0.8 | 600 | 0.6183 | 0.3150 | 212/600 | 35.3% | **0.6981** |
| P2 3 câu hỏi - sửa nhãn (mixed_lanes -> choice) | 0.9 | 600 | 0.6183 | 0.3150 | 105/600 | 17.5% | **0.6286** |
| P2 performer - cân bằng lớp | 0.5 | 280 | 0.3571 | 0.1429 | 219/280 | 78.2% | 0.3790 |
| P2 performer - cân bằng lớp | 0.8 | 280 | 0.3571 | 0.1429 | 98/280 | 35.0% | **0.4490** |
| P2 performer - cân bằng lớp | 0.9 | 280 | 0.3571 | 0.1429 | 83/280 | 29.6% | **0.4337** |
| P2 evidence - cân bằng lớp | 0.5 | 120 | 0.3333 | 0.3333 | 108/120 | 90.0% | 0.3611 |
| P2 evidence - cân bằng lớp | 0.8 | 120 | 0.3333 | 0.3333 | 14/120 | 11.7% | **1.0000** |
| P2 evidence - cân bằng lớp | 0.9 | 120 | 0.3333 | 0.3333 | 1/120 | 0.8% | **1.0000** |
| P2 mixed_lanes noul - cân bằng lớp | 0.5 | 80 | 0.5000 | 0.5000 | 80/80 | 100.0% | 0.5000 |
| P2 mixed_lanes noul - cân bằng lớp | 0.8 | 80 | 0.5000 | 0.5000 | 80/80 | 100.0% | **0.5000** |
| P2 mixed_lanes noul - cân bằng lớp | 0.9 | 80 | 0.5000 | 0.5000 | 80/80 | 100.0% | **0.5000** |
| P2 mixed_lanes choice - sửa nhãn + cân bằng | 0.5 | 80 | 0.5125 | 0.5000 | 80/80 | 100.0% | 0.5125 |
| P2 mixed_lanes choice - sửa nhãn + cân bằng | 0.8 | 80 | 0.5125 | 0.5000 | 42/80 | 52.5% | **0.4762** |
| P2 mixed_lanes choice - sửa nhãn + cân bằng | 0.9 | 80 | 0.5125 | 0.5000 | 13/80 | 16.2% | **0.3846** |
| Laya benchmark ag_news | 0.5 | 200 | 0.9300 | 0.2500 | 199/200 | 99.5% | 0.9347 |
| Laya benchmark ag_news | 0.8 | 200 | 0.9300 | 0.2500 | 189/200 | 94.5% | **0.9418** |
| Laya benchmark ag_news | 0.9 | 200 | 0.9300 | 0.2500 | 184/200 | 92.0% | **0.9511** |
| Laya benchmark emotion | 0.5 | 200 | 0.5600 | 0.3500 | 180/200 | 90.0% | 0.5944 |
| Laya benchmark emotion | 0.8 | 200 | 0.5600 | 0.3500 | 135/200 | 67.5% | **0.6296** |
| Laya benchmark emotion | 0.9 | 200 | 0.5600 | 0.3500 | 115/200 | 57.5% | **0.6435** |
| Laya benchmark enron_spam | 0.5 | 200 | 0.7950 | 0.5050 | 200/200 | 100.0% | 0.7950 |
| Laya benchmark enron_spam | 0.8 | 200 | 0.7950 | 0.5050 | 189/200 | 94.5% | **0.8201** |
| Laya benchmark enron_spam | 0.9 | 200 | 0.7950 | 0.5050 | 178/200 | 89.0% | **0.8258** |

## 4. So sánh data Công ty với data Laya

| tập | acc | baseline | acc@0.8 / coverage | acc@0.9 / coverage | ECE |
|---|---|---|---|---|---|
| P1 relation - data cty (gốc) | 0.2800 | 0.6350 | 0.7069 / 29.0% | 0.9333 / 7.5% | 0.4235 |
| P1 relation - sửa nhãn (requires_both/requires_either) | 0.4050 | 0.6350 | 0.5714 / 3.5% | 0.0000 / 0.5% | 0.2207 |
| P1 relation - sửa nhãn + cân bằng lớp | 0.4583 | 0.3333 | 0.6667 / 5.0% | - / 0.0% | 0.2208 |
| P2 performer - data cty (gốc) | 0.4750 | 0.2450 | 0.5647 / 42.5% | 0.5571 / 35.0% | 0.2571 |
| P2 evidence - data cty (gốc) | 0.6200 | 0.9450 | 0.9706 / 17.0% | 1.0000 / 6.0% | 0.0693 |
| P2 mixed_lanes noul - data cty (gốc) | 0.2250 | 0.7750 | 0.2250 / 100.0% | 0.2250 / 100.0% | 0.7750 |
| P2 3 câu hỏi - data cty (gốc) | 0.4400 | 0.3150 | 0.3950 / 53.2% | 0.3404 / 47.0% | 0.3518 |
| P2 3 câu hỏi - sửa nhãn (mixed_lanes -> choice) | 0.6183 | 0.3150 | 0.6981 / 35.3% | 0.6286 / 17.5% | 0.0992 |
| P2 performer - cân bằng lớp | 0.3571 | 0.1429 | 0.4490 / 35.0% | 0.4337 / 29.6% | 0.3362 |
| P2 evidence - cân bằng lớp | 0.3333 | 0.3333 | 1.0000 / 11.7% | 1.0000 / 0.8% | 0.3494 |
| P2 mixed_lanes noul - cân bằng lớp | 0.5000 | 0.5000 | 0.5000 / 100.0% | 0.5000 / 100.0% | 0.5000 |
| P2 mixed_lanes choice - sửa nhãn + cân bằng | 0.5125 | 0.5000 | 0.4762 / 52.5% | 0.3846 / 16.2% | 0.2937 |
| Laya benchmark ag_news | 0.9300 | 0.2500 | 0.9418 / 94.5% | 0.9511 / 92.0% | 0.0608 |
| Laya benchmark emotion | 0.5600 | 0.3500 | 0.6296 / 67.5% | 0.6435 / 57.5% | 0.2671 |
| Laya benchmark enron_spam | 0.7950 | 0.5050 | 0.8201 / 94.5% | 0.8258 / 89.0% | 0.1711 |

## 5. Tốc độ

| tập | yêu cầu | tb (ms) | p50 (ms) | p95 (ms) | câu hỏi/yêu cầu |
|---|---|---|---|---|---|
| P1 relation - data cty (gốc) | 200 | 482 | 378 | 710 | 1.0 |
| P1 relation - sửa nhãn (requires_both/requires_either) | 200 | 474 | 377 | 770 | 1.0 |
| P1 relation - sửa nhãn + cân bằng lớp | 120 | 487 | 365 | 546 | 1.0 |
| P2 3 câu hỏi - data cty (gốc) | 200 | 2261 | 2070 | 3013 | 3.0 |
| P2 3 câu hỏi - sửa nhãn (mixed_lanes -> choice) | 200 | 2197 | 1999 | 2941 | 3.0 |
| P2 performer - cân bằng lớp | 280 | 817 | 717 | 1064 | 1.0 |
| P2 evidence - cân bằng lớp | 120 | 691 | 547 | 830 | 1.0 |
| P2 mixed_lanes noul - cân bằng lớp | 80 | 799 | 600 | 953 | 1.0 |
| P2 mixed_lanes choice - sửa nhãn + cân bằng | 80 | 869 | 684 | 974 | 1.0 |
| Laya benchmark ag_news | 200 | 389 | 291 | 370 | 1.0 |
| Laya benchmark emotion | 200 | 314 | 243 | 309 | 1.0 |
| Laya benchmark enron_spam | 200 | 941 | 498 | 2707 | 1.0 |

- Số liệu từ một request thật cho mỗi mẫu (không batch), nên so sánh trực tiếp giữa các tập; số `laya-evals` đã gộp batch `--batch-size 8` nằm ở mục 2.

## 6. Token sử dụng

| tập | yêu cầu | tổng input token | tb/yêu cầu | p95/yêu cầu | tổng output token |
|---|---|---|---|---|---|
| P1 relation - data cty (gốc) | 200 | 32907 | 164.5 | 300 | 0 |
| P1 relation - sửa nhãn (requires_both/requires_either) | 200 | 33707 | 168.5 | 304 | 0 |
| P1 relation - sửa nhãn + cân bằng lớp | 120 | 19652 | 163.8 | 255 | 0 |
| P2 3 câu hỏi - data cty (gốc) | 200 | 174352 | 871.8 | 1202 | 0 |
| P2 3 câu hỏi - sửa nhãn (mixed_lanes -> choice) | 200 | 181952 | 909.8 | 1240 | 0 |
| P2 performer - cân bằng lớp | 280 | 91519 | 326.9 | 440 | 0 |
| P2 evidence - cân bằng lớp | 120 | 29838 | 248.7 | 353 | 0 |
| P2 mixed_lanes noul - cân bằng lớp | 80 | 21725 | 271.6 | 380 | 0 |
| P2 mixed_lanes choice - sửa nhãn + cân bằng | 80 | 24286 | 303.6 | 412 | 0 |
| Laya benchmark ag_news | 200 | 24433 | 122.2 | 150 | 0 |
| Laya benchmark emotion | 200 | 20139 | 100.7 | 118 | 0 |
| Laya benchmark enron_spam | 200 | 70234 | 351.2 | 1024 | 0 |

- `output_tokens = 0` ở mọi request: Laya là mô hình System 1 phi tự hồi quy, chỉ đọc input và trả về xác suất, không sinh token.
- Token đếm lại đúng pipeline encode của Laya (`attention_mask` của forward).

## 7. Kết luận theo ba tiêu chí

| tiêu chí | data Công ty (sau tối ưu) | data Laya (3 benchmark) |
|---|---|---|
| độ chính xác (acc / baseline đa số) | P1: 0.2800 &rarr; 0.4050 (sửa nhãn) &rarr; 0.4583 (sửa nhãn + cân bằng, baseline 0.3333)<br>P2 gộp: 0.4400 &rarr; 0.6183 (chuyển mixed_lanes từ noul true/false sang choice, baseline 0.3150) | ag_news 0.9300 - emotion 0.5600 - enron_spam 0.7950<br>(baseline đa số 0.2500 - 0.3500 - 0.5050) |
| acc@0.8 / coverage | P1 gốc 0.7069 / 29.0% &rarr; P1 sửa nhãn 0.5714 / 3.5%<br>P2 gốc 0.3950 / 53.2% &rarr; P2 sửa nhãn 0.6981 / 35.3% | ag_news 0.9418 / 94.5% - emotion 0.6296 / 67.5% - enron_spam 0.8201 / 94.5% |
| acc@0.9 / coverage | P1 gốc 0.9333 / 7.5% &rarr; P1 sửa nhãn 0.0000 / 0.5%<br>P2 gốc 0.3404 / 47.0% &rarr; P2 sửa nhãn 0.6286 / 17.5% | ag_news 0.9511 / 92.0% - emotion 0.6435 / 57.5% - enron_spam 0.8258 / 89.0% |
| tốc độ p50 / p95 (ms) | P1 377 / 770; P2 gộp 2070 / 3013 (3 câu/request), P2 1 câu 547 - 830 | ag_news 291 / 370; emotion 243 / 309; enron_spam 498 / 2707 |
| token input tb/yêu cầu (output = 0) | P1 169; P2 872 (3 câu) = 291/câu | ag_news 122 - emotion 101 - enron_spam 351 |
| ECE (calibration) | P1 0.4235 &rarr; 0.2207 (sửa nhãn); P2 0.3518 &rarr; 0.0992 (sửa nhãn) | 0.0608 (ag_news) - 0.2671 (emotion) - 0.1711 (enron_spam) |

- **Sửa nhãn có hiệu quả thật:** `and`/`or` là boolean-word - đổi thành `requires_both`/`requires_either` nâng P1 từ 0.2800 lên 0.4050; chuyển `mixed_lanes` từ noul `true`/`false` sang choice `tach_rieng`/`khong_can_tach` nâng P2 gộp từ 0.4400 lên 0.6183 và ECE từ 0.3518 xuống 0.0992.
- **Threshold 0.8/0.9 đáng dùng trên data Laya:** ag_news giữ 94.5%/92.0% coverage và acc@0.8 0.9418 / acc@0.9 0.9511; emotion 67.5%/57.5%; enron_spam 94.5%/89.0%.
- **Trên data Công ty, threshold kém hơn do confidence lệch chuẩn** (ECE 0.22-0.42): P1 gốc @0.8 đạt 0.7069 nhưng chỉ trả lời 29.0% mẫu; @0.9 đạt 0.9333 trên 7.5%. P2 sửa nhãn @0.8 đạt 0.6981 (coverage 35.3%), @0.9 đạt 0.6286 (17.5%).
- **Cân bằng lớp làm accuracy giảm nhưng trung thực hơn:** P2 evidence từ 0.6200 (thua baseline 0.9450) xuống 0.3333 = mức random với 3 lớp đều nhau; P2 performer cân bằng 0.3571 so với baseline 0.1429 (vẫn gấp 2.5 lần).
- **Chất lượng ground truth còn thấp:** 195/200 mẫu P2 mang `label_status = needs_domain_review`, nên mọi accuracy ở đây là so với nhãn POC, chưa phải nhãn domain đã chốt.
- **Về mapping nhãn (`guide.py`):** repo và checkpoint `convaiinnovations/laya-multilingual` trên HuggingFace **không chứa file guide.py**. Thứ tự các option được xác định bởi thứ tự `criteria` trong `build_sequence` (`laya/common.py:156-185`), đầu ra là chuỗi nhãn (`answer.choice`) hoặc ngưỡng 0.5 với noul - không tồn tại bảng label&rarr;id riêng để bị sai lệch. Kết luận: số liệu dưới đây dùng đúng chuỗi nhãn, không cần sửa mapping.
- **Lưu ý @0.9 của P1 sửa nhãn:** chỉ còn 1/200 mẫu đạt confidence >= 0.9 nên `0.0000` ở đây không có ý nghĩa thống kê - nhãn mới làm model tự tin ít hơn, không phải model sai nhiều hơn.
- **Checkpoint:** mọi lượt chạy dùng `multilingual` (`--model multilingual`) để so sánh cùng điều kiện; benchmark tiếng Anh vì vậy chưa phải số tốt nhất của checkpoint `laya` (English) - muốn dùng bản đó thì chạy lại với auto-route.

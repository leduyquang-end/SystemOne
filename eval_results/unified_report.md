# Báo cáo tổng hợp - Laya trên 2 tập POC

Bộ tiêu chí: **độ chính xác (theo threshold confidence) - tốc độ - token sử dụng**.

## 0. Cấu hình chạy

| hạng mục | giá trị |
|---|---|
| checkpoint | multilingual (auto-route) |
| revisions | `{"multilingual": "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851"}` |
| device / luồng | cpu / OMP_NUM_THREADS=4 (PyTorch 2.14.0+cpu) |
| dữ liệu | 4 file CSV trong `input\` (bản `_1` làm đầu vào model, bản đầy đủ nối metadata) |
| số mẫu | P1 = 200 (1 câu hỏi), P2 = 200 (3 câu hỏi = 600 case) |
| metric chuẩn | `laya-evals` (choice_accuracy, noul_accuracy, ece, latency) |

## 1. Độ chính xác tổng

| tập / câu hỏi | đúng/tổng | accuracy | baseline đa số | chênh | @t=0.5 | @t=0.8 | @t=0.9 |
|---|---|---|---|---|---|---|---|
| P1 relation (choice) | 56/200 | 0.2800 | 0.6350 | -0.3550 | 0.2951 | 0.7069 | 0.9333 |
| P2 performer (choice) | 95/200 | 0.4750 | 0.2450 | +0.2300 | 0.5000 | 0.5647 | 0.5571 |
| P2 evidence (choice) | 124/200 | 0.6200 | 0.9450 | -0.3250 | 0.6627 | 0.9706 | 1.0000 |
| P2 mixed_lanes (noul) | 45/200 | 0.2250 | 0.7750 | -0.5500 | 0.2250 | 0.2250 | 0.2250 |

`laya-evals`: P1 choice_accuracy=0.2800 (ece=0.4235) | P2 choice_accuracy=0.5475, noul_accuracy=0.2250 (ece=0.3518)

## 2. Độ chính xác theo threshold confidence

Chỉ trả lời khi `answer_confidence >= threshold`, còn lại **từ chối (abstain)**. `accuracy@t` tính trên các mẫu **đã trả lời**.

| tập / câu hỏi | threshold | trả lời | coverage | đúng | accuracy@t | từ chối | đúng (bị từ chối) |
|---|---|---|---|---|---|---|---|
| P1 relation (choice) | 0.5 | 183/200 | 91.5% | 54 | 29.5% | 17 | 2 |
| P1 relation (choice) | 0.6 | 149/200 | 74.5% | 52 | 34.9% | 51 | 4 |
| P1 relation (choice) | 0.7 | 96/200 | 48.0% | 46 | 47.9% | 104 | 10 |
| P1 relation (choice) | 0.8 | 58/200 | 29.0% | 41 | **70.7%** | 142 | 15 |
| P1 relation (choice) | 0.9 | 15/200 | 7.5% | 14 | **93.3%** | 185 | 42 |
| P1 relation (choice) | 0.95 | 3/200 | 1.5% | 3 | 100.0% | 197 | 53 |
| P2 performer (choice) | 0.5 | 166/200 | 83.0% | 83 | 50.0% | 34 | 12 |
| P2 performer (choice) | 0.6 | 132/200 | 66.0% | 69 | 52.3% | 68 | 26 |
| P2 performer (choice) | 0.7 | 100/200 | 50.0% | 56 | 56.0% | 100 | 39 |
| P2 performer (choice) | 0.8 | 85/200 | 42.5% | 48 | **56.5%** | 115 | 47 |
| P2 performer (choice) | 0.9 | 70/200 | 35.0% | 39 | **55.7%** | 130 | 56 |
| P2 performer (choice) | 0.95 | 53/200 | 26.5% | 28 | 52.8% | 147 | 67 |
| P2 evidence (choice) | 0.5 | 166/200 | 83.0% | 110 | 66.3% | 34 | 14 |
| P2 evidence (choice) | 0.6 | 108/200 | 54.0% | 80 | 74.1% | 92 | 44 |
| P2 evidence (choice) | 0.7 | 69/200 | 34.5% | 57 | 82.6% | 131 | 67 |
| P2 evidence (choice) | 0.8 | 34/200 | 17.0% | 33 | **97.1%** | 166 | 91 |
| P2 evidence (choice) | 0.9 | 12/200 | 6.0% | 12 | **100.0%** | 188 | 112 |
| P2 evidence (choice) | 0.95 | 3/200 | 1.5% | 3 | 100.0% | 197 | 121 |
| P2 mixed_lanes (noul) | 0.5 | 200/200 | 100.0% | 45 | 22.5% | 0 | 0 |
| P2 mixed_lanes (noul) | 0.6 | 200/200 | 100.0% | 45 | 22.5% | 0 | 0 |
| P2 mixed_lanes (noul) | 0.7 | 200/200 | 100.0% | 45 | 22.5% | 0 | 0 |
| P2 mixed_lanes (noul) | 0.8 | 200/200 | 100.0% | 45 | **22.5%** | 0 | 0 |
| P2 mixed_lanes (noul) | 0.9 | 200/200 | 100.0% | 45 | **22.5%** | 0 | 0 |
| P2 mixed_lanes (noul) | 0.95 | 200/200 | 100.0% | 45 | 22.5% | 0 | 0 |
| P2 gộp 3 câu hỏi (600 case) | 0.5 | 532/600 | 88.7% | 238 | 44.7% | 68 | 26 |
| P2 gộp 3 câu hỏi (600 case) | 0.6 | 440/600 | 73.3% | 194 | 44.1% | 160 | 70 |
| P2 gộp 3 câu hỏi (600 case) | 0.7 | 369/600 | 61.5% | 158 | 42.8% | 231 | 106 |
| P2 gộp 3 câu hỏi (600 case) | 0.8 | 319/600 | 53.2% | 126 | **39.5%** | 281 | 138 |
| P2 gộp 3 câu hỏi (600 case) | 0.9 | 282/600 | 47.0% | 96 | **34.0%** | 318 | 168 |
| P2 gộp 3 câu hỏi (600 case) | 0.95 | 256/600 | 42.7% | 76 | 29.7% | 344 | 188 |

## 3. Tốc độ

| chỉ số | P1 condition relation | P2 performer lane |
|---|---|---|
| số yêu cầu | 200 | 200 |
| số câu hỏi/request | 1 | 3 |
| tổng thời gian (s) | 93.5 | 452.2 |
| trung bình (ms) | 467 | 2261 |
| p50 (ms) | 360 | 2070 |
| p95 (ms) | 685 | 3013 |
| max (ms) | 15258 | 14714 |
| throughput (request/s) | 2.14 | 0.44 |
| laya-evals latency p50/p95 (ms, batch=8) | 3228 / 7809 | 2065 / 3089 (khong batch) |
| cost/decision p50 (ms) | 403 | 2065 |

- Số liệu `max` gồm lần tải checkpoint ở request đầu tiên (~15s), bỏ qua khi đọc p50/p95.
- P1 chạy `--batch-size 8`: latency mỗi request lên ~3.2s nhưng **giá mỗi quyết định chỉ ~404ms** (chia sẻ forward pass); chạy lẻ 1 request thì p50 = 360 ms.
- P2 không batch được (mỗi mẫu có bộ cấu phần riêng -> questions khác nhau), 3 câu hỏi chung 1 forward pass nên p50 = 2070 ms/request.

## 4. Token sử dụng

| chỉ số | P1 condition relation | P2 performer lane |
|---|---|---|
| số request | 200 | 200 |
| tổng input token | 32907 | 174352 |
| trung bình/request | 164 | 871 |
| min / p50 / p95 / max | 126 / 152 / 300 / 413 | 620 / 824 / 1202 / 1301 |
| trung bình/câu hỏi | 164 | 291 |
| tổng output token | 0 | 0 |

- `output_tokens = 0` ở mọi request: Laya là mô hình **System 1 phi tự hồi quy**, không sinh token văn bản - chỉ đọc input và trả về xác suất.
- P2 tốn nhiều token hơn/request vì 1 state mang 3 câu hỏi + danh sách cấu phần.
- Token được đếm lại bằng đúng pipeline encode của Laya (`attention_mask` của forward, gồm state + mọi câu hỏi sau khi cắt bớt ngân sách).

## 5. Nhận xét

| tiêu chí | đánh giá |
|---|---|
| độ chính xác | P1 = 0.2800 (thua baseline 0.6350); P2 performer = 0.4750 (vượt baseline 0.2450); evidence = 0.6200 (thua baseline 0.9450); mixed_lanes = 0.2250 (thua baseline 0.7750) |
| threshold 0.8 | xem dòng `0.8` ở mục 2: coverage giảm mạnh, accuracy trên mẫu đã trả lời 0.7069 (P1) / 0.3950 (P2 gộp) |
| threshold 0.9 | coverage tiếp tục giảm, accuracy trên mẫu đã trả lời 0.9333 (P1) / 0.3404 (P2 gộp) |
| tốc độ | P1 p50 = 360 ms, P2 p50 = 2070 ms trên CPU 4 luồng |
| token | P1 trung bình 164 input token/request, P2 871 - output token = 0 |
| rủi ro | model thiên về 1 nhãn (P1->or 194/200, P2 mixed_lanes->true 200/200); confidence cao nhưng sai nên threshold không lọc được hết lỗi |
| threshold với P2 | accuracy@t của P2 gộp GIẢM khi tăng threshold vì `mixed_lanes` luôn conf ~ 1.0 nhưng sai hết (22.5%) - nhóm này lọt hết vào nhóm trả lời tại mọi ngưỡng, kéo accuracy xuống |

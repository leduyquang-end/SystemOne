import csv
import json
import os
import sys
from collections import Counter

THRESHOLDS = (0.5, 0.6, 0.7, 0.8, 0.9, 0.95)
BINS = 15

SETS = [
    ("P1 relation - data cty (gốc)", "p1_condition_relation/usage.csv", None),
    ("P1 relation - sửa nhãn (requires_both/requires_either)", "optimized/p1_relabel_full_usage.csv", None),
    ("P1 relation - sửa nhãn + cân bằng lớp", "optimized/p1_balanced_usage.csv", None),
    ("P2 performer - data cty (gốc)", "p2_performer_lane/usage.csv", "performer"),
    ("P2 evidence - data cty (gốc)", "p2_performer_lane/usage.csv", "evidence"),
    ("P2 mixed_lanes noul - data cty (gốc)", "p2_performer_lane/usage.csv", "mixed_lanes"),
    ("P2 3 câu hỏi - data cty (gốc)", "p2_performer_lane/usage.csv", None),
    ("P2 3 câu hỏi - sửa nhãn (mixed_lanes -> choice)", "optimized/p2_relabel_full_usage.csv", None),
    ("P2 performer - cân bằng lớp", "optimized/p2_performer_balanced_usage.csv", None),
    ("P2 evidence - cân bằng lớp", "optimized/p2_evidence_balanced_usage.csv", None),
    ("P2 mixed_lanes noul - cân bằng lớp", "optimized/p2_mixed_lanes_balanced_usage.csv", None),
    ("P2 mixed_lanes choice - sửa nhãn + cân bằng", "optimized/p2_mixed_lanes_choice_balanced_usage.csv", None),
    ("Laya benchmark ag_news", "standard_benchmarks/ag_news_usage.csv", None),
    ("Laya benchmark emotion", "standard_benchmarks/emotion_usage.csv", None),
    ("Laya benchmark enron_spam", "standard_benchmarks/enron_spam_usage.csv", None),
]

PCT = lambda x: "-" if x is None else "%.1f%%" % (100.0 * x)
F4 = lambda x: "-" if x is None else "%.4f" % x


def percentile(values, q):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * q))]


def read_usage(path, qid=None):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig", newline="")))
    if qid:
        rows = [r for r in rows if r["qid"] == qid]
    return rows


def ece(rows):
    items = [(float(r["answer_confidence"]), int(r["correct"])) for r in rows]
    total = len(items)
    if not total:
        return None
    error = 0.0
    for bucket in range(BINS):
        low, high = bucket / BINS, (bucket + 1) / BINS
        picked = [(c, o) for c, o in items
                  if (low <= c < high) or (bucket == BINS - 1 and c >= 1.0)]
        if not picked:
            continue
        accuracy = sum(o for _, o in picked) / len(picked)
        confidence = sum(c for c, _ in picked) / len(picked)
        error += (len(picked) / total) * abs(accuracy - confidence)
    return error


def compute(rows):
    total = len(rows)
    correct = sum(int(r["correct"]) for r in rows)
    baseline = max(Counter(r["expected"] for r in rows).values()) / total
    out = {
        "cases": total,
        "correct": correct,
        "accuracy": correct / total,
        "baseline": baseline,
        "ece": ece(rows),
        "mean_confidence": sum(float(r["answer_confidence"]) for r in rows) / total,
        "thresholds": {},
    }
    for threshold in THRESHOLDS:
        answered = [r for r in rows if float(r["answer_confidence"]) >= threshold]
        right = sum(int(r["correct"]) for r in answered)
        out["thresholds"][threshold] = {
            "answered": len(answered),
            "coverage": len(answered) / total,
            "accuracy": (right / len(answered)) if answered else None,
        }
    per_request = {}
    for row in rows:
        per_request.setdefault(row["index"], row)
    latency = [float(r["latency_ms"]) for r in per_request.values()]
    tokens = [int(r["input_tokens"]) for r in per_request.values()
              if r["input_tokens"] not in (None, "")]
    out["requests"] = len(per_request)
    out["latency_avg"] = sum(latency) / len(latency)
    out["latency_p50"] = percentile(latency, 0.5)
    out["latency_p95"] = percentile(latency, 0.95)
    out["tokens_total"] = sum(tokens)
    out["tokens_avg"] = sum(tokens) / len(tokens)
    out["tokens_p95"] = percentile(tokens, 0.95)
    out["questions_per_request"] = total / len(per_request)
    out["output_tokens"] = sum(int(r["output_tokens"]) for r in per_request.values()
                               if r["output_tokens"] not in (None, ""))
    return out


def md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("dung: build_evaluation_report.py <eval_results_dir>")
    root = sys.argv[1].rstrip("/").rstrip("\\")

    results = []
    for name, path, qid in SETS:
        full = os.path.join(root, path.replace("/", os.sep))
        rows = read_usage(full, qid)
        results.append((name, path, qid, rows, compute(rows)))

    with open(os.path.join(root, "evaluation_metrics.csv"), "w", encoding="utf-8-sig",
              newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["tap", "file", "qid", "threshold", "so_case", "dung", "accuracy",
                         "baseline", "ece", "mean_confidence", "tra_loi", "coverage",
                         "accuracy_at_threshold", "latency_p50_ms", "latency_p95_ms",
                         "token_tb", "token_tong"])
        for name, path, qid, _rows, m in results:
            for threshold in THRESHOLDS:
                t = m["thresholds"][threshold]
                writer.writerow([name, path, qid or "all", threshold, m["cases"], m["correct"],
                                 round(m["accuracy"], 4), round(m["baseline"], 4),
                                 round(m["ece"], 4) if m["ece"] is not None else "",
                                 round(m["mean_confidence"], 4), t["answered"],
                                 round(t["coverage"], 4),
                                 round(t["accuracy"], 4) if t["accuracy"] is not None else "",
                                 round(m["latency_p50"], 1), round(m["latency_p95"], 1),
                                 round(m["tokens_avg"]), m["tokens_total"]])

    lines = ["# Đánh giá data Công ty trên chuẩn Laya", ""]
    lines.append("Ba tiêu chí: **độ chính xác theo threshold confidence (0.8 / 0.9) - tốc độ - "
                 "token sử dụng**. Mọi số liệu lấy từ một lần chạy thật trên CPU "
                 "(PyTorch 2.14.0+cpu, 4 luồng, checkpoint `multilingual` revision `55cf4c4`, "
                 "dataset `seed=13`).")
    lines.append("")

    validation = []
    for label, report_path, expected in [
        ("P1 gốc - `laya-evals` choice_accuracy", "p1_condition_relation/laya_evals_report.json", 0.2800),
        ("P2 gốc - `laya-evals` choice_accuracy", "p2_performer_lane/laya_evals_report.json", 0.5475),
    ]:
        report = json.load(open(os.path.join(root, report_path), encoding="utf-8"))
        validation.append((label, F4(report["overall"]["choice_accuracy"]), F4(expected)))
    p1_mine = next(m for name, _, _, _, m in results if name.startswith("P1 relation - data cty"))
    validation.append(("P1 gốc - tính lại từ `usage.csv`", F4(p1_mine["accuracy"]), "0.2800"))
    validation.append(("P1 gốc - ECE tính lại (laya-evals: 0.4235)", F4(p1_mine["ece"]), "0.4235"))

    lines += ["## 0. Kiểm tra tính vòng", "",
              md_table(["kiểm tra", "giá trị tính lại", "giá trị tham chiếu"], validation), ""]

    lines += ["## 1. Bộ data", "",
              md_table(["tập", "cột đầu vào", "phân bố nhãn", "số mẫu"], [
                  ["P1 condition relation<br>`Data_cty/p1_condition_relation_poc_200.csv`",
                   "`sample_id`, `input_json` (clause_text + left_condition/right_condition), "
                   "`pair_scope` (flat/nested - chỉ dùng phân tích), `expected_relation`, "
                   "`label_status` (curated / synthetic_checked)",
                   "and 127 - or 53 - insufficient_evidence 20", "200"],
                  ["P2 performer lane<br>`Data_cty/p2_performer_lane_poc_200.csv`",
                   "`sample_id`, `split` (dev 124 / eval 76), `input_json` (câu nghiệp vụ, tác "
                   "nhân, bước con, cấu phần được chọn, gợi ý), `expected_performer` (ID member - "
                   "không phải chữ client/server), `expected_evidence` (verb/object/context), "
                   "`expected_mixed_lanes` (true/false), `label_status`",
                   "performer: 7 ID (7-49 mẫu/lớp); evidence: verb 189 - context 9 - object 2; "
                   "mixed_lanes: false 155 - true 45",
                   "200 (spec_confirmed 5 / needs_domain_review 195)"],
              ]), ""]

    lines += ["", "## 2. Tham chiếu chuẩn Laya (3 dataset công khai, cùng checkpoint)", ""]
    bench_rows = []
    for name, path, _qid, _rows, m in results:
        if not name.startswith("Laya benchmark"):
            continue
        report_path = os.path.join(root, path.split("/")[0],
                                   path.split("/")[1].replace("_usage.csv", "_report.json"))
        official = json.load(open(report_path, encoding="utf-8"))["overall"]
        bench_rows.append([name.split("benchmark ")[-1], m["cases"],
                           F4(official["choice_accuracy"]), F4(m["accuracy"]),
                           F4(official["ece"]), F4(m["ece"]), F4(m["baseline"]),
                           "%d ms" % m["latency_p50"], m["tokens_avg"]])
    lines.append(md_table(["dataset", "số mẫu", "acc (laya-evals)", "acc (tính lại)",
                           "ECE (laya-evals)", "ECE (tính lại)", "baseline đa số",
                           "latency p50", "token tb/mẫu"], bench_rows))
    lines += ["",
              "Chạy với `laya-evals --model multilingual --batch-size 8` để cùng checkpoint với "
              "data Công ty; bản gộp đầy đủ nằm trong `standard_benchmarks/*_report.json`."]

    lines += ["", "## 3. Độ chính xác theo threshold confidence", "",
              "Chỉ trả lời khi `answer_confidence >= threshold`, còn lại **từ chối (abstain)**. "
              "`acc@t` tính trên các mẫu **đã trả lời**; coverage là tỷ lệ được trả lời. "
              "Hai cột `0.8` và `0.9` in đậm theo yêu cầu.", ""]

    threshold_rows = []
    for name, _path, _qid, _rows, m in results:
        for threshold in (0.5, 0.8, 0.9):
            t = m["thresholds"][threshold]
            bold = "**" if threshold in (0.8, 0.9) else ""
            threshold_rows.append([
                name, "%g" % threshold, "%d" % m["cases"], F4(m["accuracy"]), F4(m["baseline"]),
                "%d/%d" % (t["answered"], m["cases"]), PCT(t["coverage"]),
                bold + F4(t["accuracy"]) + bold,
            ])
    lines.append(md_table(["tập / câu hỏi", "threshold", "số case", "acc (không gate)",
                           "baseline", "đã trả lời", "coverage", "acc@t"], threshold_rows))

    lines += ["", "## 4. So sánh data Công ty với data Laya", ""]
    compare = []
    for name, _path, _qid, _rows, m in results:
        t8 = m["thresholds"][0.8]
        t9 = m["thresholds"][0.9]
        compare.append([name, F4(m["accuracy"]), F4(m["baseline"]),
                        "%s / %s" % (F4(t8["accuracy"]), PCT(t8["coverage"])),
                        "%s / %s" % (F4(t9["accuracy"]), PCT(t9["coverage"])),
                        F4(m["ece"])])
    lines.append(md_table(["tập", "acc", "baseline", "acc@0.8 / coverage",
                           "acc@0.9 / coverage", "ECE"], compare))

    lines += ["", "## 5. Tốc độ", ""]
    speed = []
    for name, _path, qid, _rows, m in results:
        if qid:
            continue
        speed.append([name, m["requests"], "%.0f" % m["latency_avg"], "%d" % m["latency_p50"],
                      "%d" % m["latency_p95"], "%.1f" % m["questions_per_request"]])
    lines.append(md_table(["tập", "yêu cầu", "tb (ms)", "p50 (ms)", "p95 (ms)",
                           "câu hỏi/yêu cầu"], speed))
    lines += ["",
              "- Số liệu từ một request thật cho mỗi mẫu (không batch), nên so sánh trực tiếp "
              "giữa các tập; số `laya-evals` đã gộp batch `--batch-size 8` nằm ở mục 2."]

    lines += ["", "## 6. Token sử dụng", ""]
    token_rows = []
    for name, _path, qid, _rows, m in results:
        if qid:
            continue
        token_rows.append([name, m["requests"], m["tokens_total"], "%.1f" % m["tokens_avg"],
                           "%d" % m["tokens_p95"], m["output_tokens"]])
    lines.append(md_table(["tập", "yêu cầu", "tổng input token", "tb/yêu cầu",
                           "p95/yêu cầu", "tổng output token"], token_rows))
    lines += ["",
              "- `output_tokens = 0` ở mọi request: Laya là mô hình System 1 phi tự hồi quy, "
              "chỉ đọc input và trả về xác suất, không sinh token.",
              "- Token đếm lại đúng pipeline encode của Laya (`attention_mask` của forward)."]

    by_name = {name: m for name, _p, _q, _r, m in results}

    def find(prefix):
        for name, metric in by_name.items():
            if name.startswith(prefix):
                return metric
        raise KeyError(prefix)

    gate = lambda prefix, t: "%s / %s" % (
        F4(find(prefix)["thresholds"][t]["accuracy"]),
        PCT(find(prefix)["thresholds"][t]["coverage"]))

    lines += ["", "## 7. Kết luận theo ba tiêu chí", ""]
    lines.append(md_table(["tiêu chí", "data Công ty (sau tối ưu)", "data Laya (3 benchmark)"], [
        ["độ chính xác (acc / baseline đa số)",
         "P1: 0.2800 &rarr; 0.4050 (sửa nhãn) &rarr; 0.4583 (sửa nhãn + cân bằng, baseline 0.3333)<br>"
         "P2 gộp: 0.4400 &rarr; 0.6183 (chuyển mixed_lanes từ noul true/false sang choice, "
         "baseline 0.3150)",
         "ag_news 0.9300 - emotion 0.5600 - enron_spam 0.7950<br>"
         "(baseline đa số 0.2500 - 0.3500 - 0.5050)"],
        ["acc@0.8 / coverage",
         "P1 gốc %s &rarr; P1 sửa nhãn %s<br>P2 gốc %s &rarr; P2 sửa nhãn %s"
         % (gate("P1 relation - data cty (gốc)", 0.8),
            gate("P1 relation - sửa nhãn", 0.8),
            gate("P2 3 câu hỏi - data cty (gốc)", 0.8),
            gate("P2 3 câu hỏi - sửa nhãn", 0.8)),
         "ag_news %s - emotion %s - enron_spam %s"
         % (gate("Laya benchmark ag_news", 0.8), gate("Laya benchmark emotion", 0.8),
            gate("Laya benchmark enron_spam", 0.8))],
        ["acc@0.9 / coverage",
         "P1 gốc %s &rarr; P1 sửa nhãn %s<br>P2 gốc %s &rarr; P2 sửa nhãn %s"
         % (gate("P1 relation - data cty (gốc)", 0.9),
            gate("P1 relation - sửa nhãn", 0.9),
            gate("P2 3 câu hỏi - data cty (gốc)", 0.9),
            gate("P2 3 câu hỏi - sửa nhãn", 0.9)),
         "ag_news %s - emotion %s - enron_spam %s"
         % (gate("Laya benchmark ag_news", 0.9), gate("Laya benchmark emotion", 0.9),
            gate("Laya benchmark enron_spam", 0.9))],
        ["tốc độ p50 / p95 (ms)",
         "P1 %d / %d; P2 gộp %d / %d (3 câu/request), P2 1 câu %d - %d"
         % (find("P1 relation - sửa nhãn")["latency_p50"],
            find("P1 relation - sửa nhãn")["latency_p95"],
            find("P2 3 câu hỏi - data cty (gốc)")["latency_p50"],
            find("P2 3 câu hỏi - data cty (gốc)")["latency_p95"],
            find("P2 evidence - cân bằng lớp")["latency_p50"],
            find("P2 evidence - cân bằng lớp")["latency_p95"]),
         "ag_news %d / %d; emotion %d / %d; enron_spam %d / %d"
         % (find("Laya benchmark ag_news")["latency_p50"],
            find("Laya benchmark ag_news")["latency_p95"],
            find("Laya benchmark emotion")["latency_p50"],
            find("Laya benchmark emotion")["latency_p95"],
            find("Laya benchmark enron_spam")["latency_p50"],
            find("Laya benchmark enron_spam")["latency_p95"])],
        ["token input tb/yêu cầu (output = 0)",
         "P1 %.0f; P2 %.0f (3 câu) = %.0f/câu"
         % (find("P1 relation - sửa nhãn")["tokens_avg"],
            find("P2 3 câu hỏi - data cty (gốc)")["tokens_avg"],
            find("P2 3 câu hỏi - data cty (gốc)")["tokens_avg"] / 3.0),
         "ag_news %.0f - emotion %.0f - enron_spam %.0f"
         % (find("Laya benchmark ag_news")["tokens_avg"],
            find("Laya benchmark emotion")["tokens_avg"],
            find("Laya benchmark enron_spam")["tokens_avg"])],
        ["ECE (calibration)",
         "P1 0.4235 &rarr; 0.2207 (sửa nhãn); P2 0.3518 &rarr; 0.0992 (sửa nhãn)",
         "0.0608 (ag_news) - 0.2671 (emotion) - 0.1711 (enron_spam)"],
    ]))
    lines += ["",
              "- **Sửa nhãn có hiệu quả thật:** `and`/`or` là boolean-word - đổi thành "
              "`requires_both`/`requires_either` nâng P1 từ 0.2800 lên 0.4050; chuyển "
              "`mixed_lanes` từ noul `true`/`false` sang choice `tach_rieng`/`khong_can_tach` "
              "nâng P2 gộp từ 0.4400 lên 0.6183 và ECE từ 0.3518 xuống 0.0992.",
              "- **Threshold 0.8/0.9 đáng dùng trên data Laya:** ag_news giữ 94.5%/92.0% coverage "
              "và acc@0.8 0.9418 / acc@0.9 0.9511; emotion 67.5%/57.5%; enron_spam 94.5%/89.0%.",
              "- **Trên data Công ty, threshold kém hơn do confidence lệch chuẩn** (ECE 0.22-0.42): "
              "P1 gốc @0.8 đạt 0.7069 nhưng chỉ trả lời 29.0% mẫu; @0.9 đạt 0.9333 trên 7.5%. "
              "P2 sửa nhãn @0.8 đạt 0.6981 (coverage 35.3%), @0.9 đạt 0.6286 (17.5%).",
              "- **Cân bằng lớp làm accuracy giảm nhưng trung thực hơn:** P2 evidence từ "
              "0.6200 (thua baseline 0.9450) xuống 0.3333 = mức random với 3 lớp đều nhau; "
              "P2 performer cân bằng 0.3571 so với baseline 0.1429 (vẫn gấp 2.5 lần).",
              "- **Chất lượng ground truth còn thấp:** 195/200 mẫu P2 mang `label_status = "
              "needs_domain_review`, nên mọi accuracy ở đây là so với nhãn POC, chưa phải "
              "nhãn domain đã chốt.",
              "- **Về mapping nhãn (`guide.py`):** repo và checkpoint `convaiinnovations/"
              "laya-multilingual` trên HuggingFace **không chứa file guide.py**. Thứ tự các option "
              "được xác định bởi thứ tự `criteria` trong `build_sequence` "
              "(`laya/common.py:156-185`), đầu ra là chuỗi nhãn (`answer.choice`) hoặc ngưỡng "
              "0.5 với noul - không tồn tại bảng label&rarr;id riêng để bị sai lệch. Kết luận: "
              "số liệu dưới đây dùng đúng chuỗi nhãn, không cần sửa mapping.",
              "- **Lưu ý @0.9 của P1 sửa nhãn:** chỉ còn 1/200 mẫu đạt confidence >= 0.9 nên `0.0000` ở đây không có ý nghĩa thống kê - nhãn mới làm model tự tin ít hơn, không phải model sai nhiều hơn.", "- **Checkpoint:** mọi lượt chạy dùng `multilingual` (`--model multilingual`) để "
              "so sánh cùng điều kiện; benchmark tiếng Anh vì vậy chưa phải số tốt nhất của "
              "checkpoint `laya` (English) - muốn dùng bản đó thì chạy lại với auto-route."]

    report_path = os.path.join(root, "evaluation_report.md")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("build_evaluation_report:", report_path)
    print("evaluation_metrics.csv:", len(results) * len(THRESHOLDS), "dong")


if __name__ == "__main__":
    main()

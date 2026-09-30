import csv
import json
import os
import sys
from collections import Counter, defaultdict

THRESHOLDS = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
PCT = lambda x: "-" if x is None else "%.1f%%" % (100.0 * x)
F4 = lambda x: "-" if x is None else "%.4f" % x


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def percentile(values, q):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * q))]


def stats(values):
    if not values:
        return {}
    return {
        "total": sum(values),
        "avg": sum(values) / len(values),
        "min": min(values),
        "p50": percentile(values, 0.5),
        "p95": percentile(values, 0.95),
        "max": max(values),
        "n": len(values),
    }


def usage_stats(path):
    rows = read_csv(path)
    per_request = {}
    for row in rows:
        key = row["index"]
        if key not in per_request:
            per_request[key] = row
    latency = [float(r["latency_ms"]) for r in per_request.values()]
    tokens = [int(r["input_tokens"]) for r in per_request.values()
              if r.get("input_tokens") not in (None, "")]
    outputs = [int(r["output_tokens"]) for r in per_request.values()
               if r.get("output_tokens") not in (None, "")]
    return stats(latency), stats(tokens), sum(outputs), len(per_request)


def threshold_rows(items):
    total = len(items)
    out = []
    for threshold in THRESHOLDS:
        answered = [(conf, ok) for conf, ok in items if conf is not None and conf >= threshold]
        abstained = [(conf, ok) for conf, ok in items if conf is None or conf < threshold]
        correct = sum(ok for _, ok in answered)
        out.append({
            "threshold": threshold,
            "total": total,
            "answered": len(answered),
            "coverage": (len(answered) / total) if total else None,
            "correct": correct,
            "accuracy": (correct / len(answered)) if answered else None,
            "abstained": len(abstained),
            "correct_abstained": sum(ok for _, ok in abstained),
        })
    return out


def majority_baseline(items):
    total = len(items)
    if not total:
        return None
    return max(Counter(label for label, _ in items).values()) / total


def md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def threshold_table(block):
    rows = []
    for group, entries in block:
        for entry in entries:
            mark = "**" if entry["threshold"] in (0.8, 0.9) else ""
            rows.append([
                group, "%g" % entry["threshold"], "%d/%d" % (entry["answered"], entry["total"]),
                PCT(entry["coverage"]), "%d" % entry["correct"],
                mark + PCT(entry["accuracy"]) + mark,
                "%d" % entry["abstained"], "%d" % entry["correct_abstained"],
            ])
    return md_table(["tập / câu hỏi", "threshold", "trả lời", "coverage", "đúng",
                     "accuracy@t", "từ chối", "đúng (bị từ chối)"], rows)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("dung: build_unified_report.py <eval_results_dir>")
    root = sys.argv[1].rstrip("/").rstrip("\\")

    p1_dir = os.path.join(root, "p1_condition_relation")
    p2_dir = os.path.join(root, "p2_performer_lane")
    p1_pred = read_csv(os.path.join(p1_dir, "predictions.csv"))
    p2_pred = read_csv(os.path.join(p2_dir, "predictions.csv"))
    p1_eval = json.load(open(os.path.join(p1_dir, "laya_evals_report.json"), encoding="utf-8"))
    p2_eval = json.load(open(os.path.join(p2_dir, "laya_evals_report.json"), encoding="utf-8"))
    p1_lat, p1_tok, p1_out, p1_req = usage_stats(os.path.join(p1_dir, "usage.csv"))
    p2_lat, p2_tok, p2_out, p2_req = usage_stats(os.path.join(p2_dir, "usage.csv"))

    p1_items = [(float(r["answer_confidence"]), int(r["correct"])) for r in p1_pred]
    groups = [
        ("P1 relation (choice)", p1_items, majority_baseline(
            [(r["expected"], int(r["correct"])) for r in p1_pred])),
        ("P2 performer (choice)", [(float(r["perf_confidence"]), int(r["ok_performer"])) for r in p2_pred],
         majority_baseline([(r["expected_performer"], 1) for r in p2_pred])),
        ("P2 evidence (choice)", [(float(r["evi_confidence"]), int(r["ok_evidence"])) for r in p2_pred],
         majority_baseline([(r["expected_evidence"], 1) for r in p2_pred])),
        ("P2 mixed_lanes (noul)",
         [(max(float(r["noul_mixed_lanes"]), 1 - float(r["noul_mixed_lanes"])),
           int(r["ok_mixed_lanes"])) for r in p2_pred],
         majority_baseline([(r["expected_mixed_lanes"], 1) for r in p2_pred])),
    ]
    p2_all = groups[1][1] + groups[2][1] + groups[3][1]

    thr = [(name, threshold_rows(items)) for name, items, _ in groups]
    thr.append(("P2 gộp 3 câu hỏi (600 case)", threshold_rows(p2_all)))

    with open(os.path.join(root, "threshold_analysis.csv"), "w", encoding="utf-8-sig",
              newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["tap", "threshold", "tong", "tra_loi", "coverage", "dung",
                         "accuracy_at_threshold", "tu_choi", "dung_bi_tu_choi"])
        for name, entries in thr:
            for entry in entries:
                writer.writerow([name, entry["threshold"], entry["total"], entry["answered"],
                                 round(entry["coverage"], 4) if entry["coverage"] is not None else "",
                                 entry["correct"],
                                 round(entry["accuracy"], 4) if entry["accuracy"] is not None else "",
                                 entry["abstained"], entry["correct_abstained"]])

    lines = ["# Báo cáo tổng hợp - Laya trên 2 tập POC", ""]
    lines += ["Bộ tiêu chí: **độ chính xác (theo threshold confidence) - tốc độ - token sử dụng**.", ""]

    lines += ["## 0. Cấu hình chạy", ""]
    lines.append(md_table(["hạng mục", "giá trị"], [
        ["checkpoint", "multilingual (auto-route)"],
        ["revisions", "`%s`" % json.dumps(p1_eval["config"].get("revisions") or {}, ensure_ascii=False)],
        ["device / luồng", "cpu / OMP_NUM_THREADS=4 (PyTorch 2.14.0+cpu)"],
        ["dữ liệu", "4 file CSV trong `input\\` (bản `_1` làm đầu vào model, bản đầy đủ nối metadata)"],
        ["số mẫu", "P1 = 200 (1 câu hỏi), P2 = 200 (3 câu hỏi = 600 case)"],
        ["metric chuẩn", "`laya-evals` (choice_accuracy, noul_accuracy, ece, latency)"],
    ]))

    lines += ["", "## 1. Độ chính xác tổng", ""]
    acc_rows = []
    for (name, items, baseline), (_thr_name, entries) in zip(groups, thr):
        correct = sum(ok for _, ok in items)
        acc = correct / len(items)
        acc_rows.append([name, "%d/%d" % (correct, len(items)), F4(acc), F4(baseline),
                         "%+.4f" % (acc - baseline),
                         F4(next(e["accuracy"] for e in entries if e["threshold"] == 0.5)),
                         F4(next(e["accuracy"] for e in entries if e["threshold"] == 0.8)),
                         F4(next(e["accuracy"] for e in entries if e["threshold"] == 0.9))])
    lines.append(md_table(["tập / câu hỏi", "đúng/tổng", "accuracy", "baseline đa số",
                           "chênh", "@t=0.5", "@t=0.8", "@t=0.9"], acc_rows))
    lines.append("")
    lines.append("`laya-evals`: P1 choice_accuracy=%.4f (ece=%.4f) | P2 choice_accuracy=%.4f, "
                 "noul_accuracy=%.4f (ece=%.4f)"
                 % (p1_eval["overall"]["choice_accuracy"], p1_eval["overall"]["ece"],
                    p2_eval["overall"]["choice_accuracy"],
                    p2_eval["overall"].get("noul_accuracy", float("nan")),
                    p2_eval["overall"]["ece"]))

    lines += ["", "## 2. Độ chính xác theo threshold confidence", "",
              "Chỉ trả lời khi `answer_confidence >= threshold`, còn lại **từ chối (abstain)**. "
              "`accuracy@t` tính trên các mẫu **đã trả lời**.", ""]
    lines.append(threshold_table(thr))

    lines += ["", "## 3. Tốc độ", ""]
    p1_eval_overall = p1_eval["overall"]
    p2_eval_overall = p2_eval["overall"]
    lines.append(md_table(["chỉ số", "P1 condition relation", "P2 performer lane"], [
        ["số yêu cầu", p1_lat["n"], p2_lat["n"]],
        ["số câu hỏi/request", 1, 3],
        ["tổng thời gian (s)", "%.1f" % (p1_lat["total"] / 1000.0),
         "%.1f" % (p2_lat["total"] / 1000.0)],
        ["trung bình (ms)", "%d" % p1_lat["avg"], "%d" % p2_lat["avg"]],
        ["p50 (ms)", "%d" % p1_lat["p50"], "%d" % p2_lat["p50"]],
        ["p95 (ms)", "%d" % p1_lat["p95"], "%d" % p2_lat["p95"]],
        ["max (ms)", "%d" % p1_lat["max"], "%d" % p2_lat["max"]],
        ["throughput (request/s)", "%.2f" % (1000.0 / p1_lat["avg"]),
         "%.2f" % (1000.0 / p2_lat["avg"])],
        ["laya-evals latency p50/p95 (ms, batch=8)",
         "%d / %d" % (p1_eval_overall["latency_p50_ms"], p1_eval_overall["latency_p95_ms"]),
         "%d / %d (khong batch)" % (p2_eval_overall["latency_p50_ms"],
                                    p2_eval_overall["latency_p95_ms"])],
        ["cost/decision p50 (ms)",
         "%d" % p1_eval_overall["cost_per_decision_p50_ms"],
         "%d" % p2_eval_overall["cost_per_decision_p50_ms"]],
    ]))
    lines += ["",
              "- Số liệu `max` gồm lần tải checkpoint ở request đầu tiên (~15s), bỏ qua khi đọc p50/p95.",
              "- P1 chạy `--batch-size 8`: latency mỗi request lên ~3.2s nhưng **giá mỗi quyết định "
              "chỉ ~404ms** (chia sẻ forward pass); chạy lẻ 1 request thì p50 = %d ms."
              % p1_lat["p50"],
              "- P2 không batch được (mỗi mẫu có bộ cấu phần riêng -> questions khác nhau), "
              "3 câu hỏi chung 1 forward pass nên p50 = %d ms/request." % p2_lat["p50"]]

    lines += ["", "## 4. Token sử dụng", ""]
    lines.append(md_table(["chỉ số", "P1 condition relation", "P2 performer lane"], [
        ["số request", p1_req, p2_req],
        ["tổng input token", p1_tok["total"], p2_tok["total"]],
        ["trung bình/request", "%d" % p1_tok["avg"], "%d" % p2_tok["avg"]],
        ["min / p50 / p95 / max", "%d / %d / %d / %d"
         % (p1_tok["min"], p1_tok["p50"], p1_tok["p95"], p1_tok["max"]),
         "%d / %d / %d / %d"
         % (p2_tok["min"], p2_tok["p50"], p2_tok["p95"], p2_tok["max"])],
        ["trung bình/câu hỏi", "%d" % p1_tok["avg"], "%d" % round(p2_tok["avg"] / 3.0)],
        ["tổng output token", p1_out, p2_out],
    ]))
    lines += ["",
              "- `output_tokens = 0` ở mọi request: Laya là mô hình **System 1 phi tự hồi quy**, "
              "không sinh token văn bản - chỉ đọc input và trả về xác suất.",
              "- P2 tốn nhiều token hơn/request vì 1 state mang 3 câu hỏi + danh sách cấu phần.",
              "- Token được đếm lại bằng đúng pipeline encode của Laya "
              "(`attention_mask` của forward, gồm state + mọi câu hỏi sau khi cắt bớt ngân sách)."]

    lines += ["", "## 5. Nhận xét", ""]
    lines.append(md_table(["tiêu chí", "đánh giá"], [
        ["độ chính xác", "P1 = 0.2800 (thua baseline 0.6350); P2 performer = 0.4750 "
                          "(vượt baseline 0.2450); evidence = 0.6200 (thua baseline 0.9450); "
                          "mixed_lanes = 0.2250 (thua baseline 0.7750)"],
        ["threshold 0.8", "xem dòng `0.8` ở mục 2: coverage giảm mạnh, accuracy trên mẫu "
                          "đã trả lời %s (P1) / %s (P2 gộp)"
         % (F4(next(e["accuracy"] for e in thr[0][1] if e["threshold"] == 0.8)),
            F4(next(e["accuracy"] for e in thr[4][1] if e["threshold"] == 0.8)))],
        ["threshold 0.9", "coverage tiếp tục giảm, accuracy trên mẫu đã trả lời %s (P1) / %s (P2 gộp)"
         % (F4(next(e["accuracy"] for e in thr[0][1] if e["threshold"] == 0.9)),
            F4(next(e["accuracy"] for e in thr[4][1] if e["threshold"] == 0.9)))],
        ["tốc độ", "P1 p50 = %d ms, P2 p50 = %d ms trên CPU 4 luồng" % (p1_lat["p50"], p2_lat["p50"])],
        ["token", "P1 trung bình %d input token/request, P2 %d - output token = 0"
         % (p1_tok["avg"], p2_tok["avg"])],
        ["rủi ro", "model thiên về 1 nhãn (P1->or 194/200, P2 mixed_lanes->true 200/200); "
                   "confidence cao nhưng sai nên threshold không lọc được hết lỗi"],
        ["threshold với P2", "accuracy@t của P2 gộp GIẢM khi tăng threshold vì `mixed_lanes` luôn "
                             "conf ~ 1.0 nhưng sai hết (22.5%) - nhóm này lọt hết vào nhóm trả lời "
                             "tại mọi ngưỡng, kéo accuracy xuống"],
    ]))

    report_path = os.path.join(root, "unified_report.md")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("build_unified_report: %s" % report_path)
    print("threshold_analysis.csv: %d dong" % (len(thr) * len(THRESHOLDS)))


if __name__ == "__main__":
    main()


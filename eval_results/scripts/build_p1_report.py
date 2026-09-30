import csv
import json
import sys
from collections import Counter

LABELS = ["and", "or", "insufficient_evidence"]


def fmt(value):
    if value is None:
        return "-"
    if isinstance(value, float):
        return "%.4f" % value
    return str(value)


def md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def main():
    if len(sys.argv) != 5:
        raise SystemExit("dung: build_p1_report.py <full.csv> <trim.csv> <report.json> <out_dir>")
    full_path, trim_path, report_path, out_dir = sys.argv[1:5]

    with open(trim_path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    with open(full_path, encoding="utf-8-sig", newline="") as fh:
        meta = {r["sample_id"]: r for r in csv.DictReader(fh)}
    with open(report_path, encoding="utf-8") as fh:
        report = json.load(fh)

    cases = report["cases"]
    if len(cases) != len(rows):
        raise SystemExit("so case %d khong khop so dong CSV %d" % (len(cases), len(rows)))

    preds = []
    for row, case in zip(rows, cases):
        answer = case["answer"]
        probs = answer.get("probabilities") or {}
        payload = json.loads(row["input_json"])
        source = meta.get(row["sample_id"]) or {}
        preds.append({
            "sample_id": row["sample_id"],
            "pair_scope": row["pair_scope"],
            "label_status": row["label_status"],
            "split": source.get("split", ""),
            "variant_type": source.get("variant_type", ""),
            "rule_code": source.get("rule_code", ""),
            "rule_name": source.get("rule_name", ""),
            "source_group": source.get("source_group", ""),
            "derived_from": source.get("derived_from", ""),
            "connective_quote": source.get("connective_quote", ""),
            "expected": case["expected"],
            "predicted": answer.get("choice"),
            "correct": 1 if case["correct"] else 0,
            "answer_confidence": round(float(answer.get("answer_confidence") or 0.0), 4),
            "entropy_confidence": round(float(answer.get("confidence") or 0.0), 4),
            "prob_and": round(float(probs.get("and") or 0.0), 4),
            "prob_or": round(float(probs.get("or") or 0.0), 4),
            "prob_insufficient_evidence": round(float(probs.get("insufficient_evidence") or 0.0), 4),
            "checkpoint": case.get("model"),
            "left_condition": payload.get("left_condition") or "",
            "right_condition": payload.get("right_condition") or "",
            "clause_text": payload.get("clause_text") or "",
        })

    with open(out_dir + "/predictions.csv", "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(preds[0].keys()))
        writer.writeheader()
        writer.writerows(preds)

    matrix = {label: Counter() for label in LABELS}
    for pred in preds:
        matrix[pred["expected"]][pred["predicted"] or "(trả lời rỗng)"] += 1

    columns = LABELS + ["(trả lời rỗng)"]
    with open(out_dir + "/confusion_matrix.csv", "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["expected\\predicted"] + columns + ["tong", "dung", "sai"])
        for label in LABELS:
            total = sum(matrix[label].values())
            correct = matrix[label][label]
            writer.writerow([label] + [matrix[label].get(col, 0) for col in columns]
                            + [total, correct, total - correct])

    total = len(preds)
    correct = sum(p["correct"] for p in preds)
    accuracy = correct / total if total else 0.0

    lines = ["# Báo cáo test P1 - condition relation", ""]
    name_of = lambda path: path.replace("\\", "/").split("/")[-1]
    lines.append("- Dữ liệu đầu vào model: `%s`" % name_of(trim_path))
    lines.append("- Dữ liệu nguồn (nối metadata): `%s`" % name_of(full_path))
    lines.append("- Số mẫu: **%d**" % total)
    lines.append("- Checkpoint: %s" % fmt(report["config"].get("model") or "auto-routing"))
    lines.append("- Device: %s" % fmt(report["config"].get("device")))
    lines.append("- Revisions: `%s`" % json.dumps(report["config"].get("revisions") or {}, ensure_ascii=False))
    timing = report["config"].get("timing") or {}
    lines.append("- Batch: batch_size=%s, chunks=%s, max_chunk=%s"
                 % (timing.get("batch_size"), timing.get("chunks"), timing.get("max_chunk")))
    lines += ["", "## 1. Kết quả tổng", "",
              md_table(["metric", "value"],
                       [[k, fmt(v)] for k, v in sorted(report["overall"].items())]),
              "",
              "Accuracy tính lại từ predictions.csv: **%d/%d = %s** (khớp `choice_accuracy`)"
              % (correct, total, "%.4f" % accuracy)]

    lines += ["", "## 2. Ma trận nhầm lẫn (hàng = expected, cột = predicted)", "",
              md_table(["expected"] + columns + ["tổng", "đúng", "sai"],
                       [[label] + [matrix[label].get(col, 0) for col in columns]
                        + [sum(matrix[label].values()), matrix[label][label],
                           sum(matrix[label].values()) - matrix[label][label]]
                        for label in LABELS])]

    for dimension in ("tag", "model", "language"):
        groups = report["slices"].get(dimension) or {}
        if not groups:
            continue
        metrics = sorted({m for group in groups.values() for m in group})
        lines += ["", "## 3. Kết quả theo `--slice %s`" % dimension, "",
                  md_table([dimension] + metrics,
                           [[value] + [fmt(group.get(m)) for m in metrics]
                            for value, group in sorted(groups.items())])]

    wrong = [p for p in preds if not p["correct"]]
    lines += ["", "## 4. Mẫu sai (%d/%d)" % (len(wrong), total), ""]
    if wrong:
        lines.append(md_table(
            ["sample_id", "expected", "predicted", "conf", "pair_scope", "label_status", "left_condition", "right_condition"],
            [[p["sample_id"], p["expected"], p["predicted"], fmt(p["answer_confidence"]),
              p["pair_scope"], p["label_status"], p["left_condition"], p["right_condition"]] for p in wrong]))
        pairs = Counter((p["expected"], p["predicted"]) for p in wrong)
        lines += ["", "Tổng hợp lỗi (expected -> predicted):", ""]
        lines.append(md_table(["expected", "predicted", "so mau"],
                              [[a, b, n] for (a, b), n in pairs.most_common()]))
    else:
        lines.append("Không có mẫu nào sai.")

    lines += ["", "## 5. Phân bố nhãn", ""]
    dist = Counter(p["expected"] for p in preds)
    lines.append(md_table(["expected", "so mau", "ty le"],
                          [[k, n, "%.1f%%" % (100.0 * n / total)] for k, n in
                           sorted(dist.items(), key=lambda kv: -kv[1])]))

    with open(out_dir + "/report.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("build_p1_report: accuracy=%.4f, sai=%d/%d" % (accuracy, len(wrong), total))


if __name__ == "__main__":
    main()


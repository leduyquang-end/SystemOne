import csv
import json
import sys
from collections import Counter

QIDS = ["performer", "evidence", "mixed_lanes"]
EVIDENCE_LABELS = ["verb", "object", "context"]
MIXED_LABELS = ["true", "false"]
FULL_META = ["split", "variant_type", "label_basis", "source_group", "feature",
             "project", "source_ref", "derived_from"]


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


def write_matrix(path, labels, pairs, extra=()):
    counts = {a: Counter() for a in labels}
    for expected, predicted in pairs:
        counts[expected][predicted] += 1
    columns = list(labels) + list(extra)
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["expected\\predicted"] + columns + ["tong", "dung", "sai"])
        for label in labels:
            total = sum(counts[label].values())
            correct = counts[label][label]
            writer.writerow([label] + [counts[label].get(col, 0) for col in columns]
                            + [total, correct, total - correct])
    return counts


def matrix_md(counts, labels, extra=()):
    columns = list(labels) + list(extra)
    rows = []
    for label in labels:
        total = sum(counts[label].values())
        rows.append([label] + [counts[label].get(col, 0) for col in columns]
                    + [total, counts[label][label], total - counts[label][label]])
    return md_table(["expected"] + columns + ["tổng", "đúng", "sai"], rows)


def main():
    if len(sys.argv) != 5:
        raise SystemExit("dung: build_p2_report.py <full.csv> <trim.csv> <report.json> <out_dir>")
    full_path, trim_path, report_path, out_dir = sys.argv[1:5]

    with open(trim_path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    with open(full_path, encoding="utf-8-sig", newline="") as fh:
        meta = {r["sample_id"]: r for r in csv.DictReader(fh)}
    with open(report_path, encoding="utf-8") as fh:
        report = json.load(fh)

    cases = report["cases"]
    if len(cases) != len(rows) * len(QIDS):
        raise SystemExit("so case %d khong bang %d x %d"
                         % (len(cases), len(rows), len(QIDS)))

    performer_labels = sorted({r["expected_performer"] for r in rows}
                              | {c["answer"].get("choice") for c in cases if c["qid"] == "performer"})
    preds = []
    for index, row in enumerate(rows):
        chunk = cases[index * len(QIDS):(index + 1) * len(QIDS)]
        if [c["qid"] for c in chunk] != QIDS:
            raise SystemExit("thu tu qid sai o dong %d" % index)
        perf, evi, mix = chunk
        perf_answer, evi_answer, mix_answer = perf["answer"], evi["answer"], mix["answer"]
        payload = json.loads(row["input_json"])
        substeps = payload.get("substeps") or []
        source = meta.get(row["sample_id"]) or {}
        record = {
            "sample_id": row["sample_id"],
            "split": row["split"],
            "label_status": row["label_status"],
            "variant_type": source.get("variant_type", ""),
            "label_basis": source.get("label_basis", ""),
            "source_group": source.get("source_group", ""),
            "feature": source.get("feature", ""),
            "subject": (payload.get("subject") or {}).get("text", ""),
            "substep_quote": (substeps[0].get("quote") if substeps else "") or "",
            "expected_performer": perf["expected"],
            "predicted_performer": perf_answer.get("choice"),
            "ok_performer": 1 if perf["correct"] else 0,
            "perf_confidence": round(float(perf_answer.get("answer_confidence") or 0.0), 4),
            "expected_evidence": evi["expected"],
            "predicted_evidence": evi_answer.get("choice"),
            "ok_evidence": 1 if evi["correct"] else 0,
            "evi_confidence": round(float(evi_answer.get("answer_confidence") or 0.0), 4),
            "expected_mixed_lanes": str(mix["expected"]).lower(),
            "noul_mixed_lanes": round(float(mix_answer.get("noul") or 0.0), 4),
            "predicted_mixed_lanes": "true" if float(mix_answer.get("noul") or 0.0) >= 0.5 else "false",
            "ok_mixed_lanes": 1 if mix["correct"] else 0,
            "checkpoint": perf_answer.get("type") and (perf.get("model") or ""),
        }
        probs = perf_answer.get("probabilities") or {}
        for label in performer_labels:
            record["prob_" + label] = round(float(probs.get(label) or 0.0), 4)
        preds.append(record)

    with open(out_dir + "/predictions.csv", "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(preds[0].keys()))
        writer.writeheader()
        writer.writerows(preds)

    perf_pairs = [(p["expected_performer"], p["predicted_performer"] or "(trống)") for p in preds]
    evi_pairs = [(p["expected_evidence"], p["predicted_evidence"] or "(trống)") for p in preds]
    mix_pairs = [(p["expected_mixed_lanes"], p["predicted_mixed_lanes"]) for p in preds]

    perf_counts = write_matrix(out_dir + "/confusion_matrix_performer.csv",
                               performer_labels, perf_pairs, extra=["(trống)"])
    evi_counts = write_matrix(out_dir + "/confusion_matrix_evidence.csv",
                              EVIDENCE_LABELS, evi_pairs, extra=["(trống)"])
    mix_counts = write_matrix(out_dir + "/confusion_matrix_mixed_lanes.csv",
                              MIXED_LABELS, mix_pairs)

    total = len(preds)
    n_perf = sum(p["ok_performer"] for p in preds)
    n_evi = sum(p["ok_evidence"] for p in preds)
    n_mix = sum(p["ok_mixed_lanes"] for p in preds)
    timing = report["config"].get("timing") or {}

    lines = ["# Báo cáo test P2 - performer lane", ""]
    name_of = lambda path: path.replace("\\", "/").split("/")[-1]
    lines.append("- Dữ liệu đầu vào model: `%s`" % name_of(trim_path))
    lines.append("- Dữ liệu nguồn (nối metadata): `%s`" % name_of(full_path))
    lines.append("- Số mẫu: **%d** (%d câu hỏi/mẫu = %d case)"
                 % (total, len(QIDS), len(cases)))
    lines.append("- Device: %s" % fmt(report["config"].get("device")))
    lines.append("- Revisions: `%s`" % json.dumps(report["config"].get("revisions") or {},
                                                  ensure_ascii=False))
    lines.append("- Batch: batch_size=%s, chunks=%s, max_chunk=%s"
                 % (timing.get("batch_size"), timing.get("chunks"), timing.get("max_chunk")))

    lines += ["", "## 1. Kết quả tổng (laya-evals)", "",
              md_table(["metric", "value"],
                       [[k, fmt(v)] for k, v in sorted(report["overall"].items())])]
    lines += ["", "## 2. Accuracy theo từng câu hỏi", "",
              md_table(["câu hỏi", "đúng/tổng", "accuracy"], [
                  ["performer (chọn cấu phần)", "%d/%d" % (n_perf, total), "%.4f" % (n_perf / total)],
                  ["evidence (verb/object/context)", "%d/%d" % (n_evi, total), "%.4f" % (n_evi / total)],
                  ["mixed_lanes (noul)", "%d/%d" % (n_mix, total), "%.4f" % (n_mix / total)],
              ])]

    lines += ["", "## 3. Ma trận nhầm lẫn - performer", "", matrix_md(perf_counts, performer_labels,
                                                                      extra=["(trống)"])]
    lines += ["", "## 4. Ma trận nhầm lẫn - evidence", "", matrix_md(evi_counts, EVIDENCE_LABELS,
                                                                     extra=["(trống)"])]
    lines += ["", "## 5. Ma trận nhầm lẫn - mixed_lanes", "", matrix_md(mix_counts, MIXED_LABELS)]

    for dimension in ("qid", "tag", "model", "language"):
        groups = report["slices"].get(dimension) or {}
        if not groups:
            continue
        metrics = sorted({m for group in groups.values() for m in group})
        lines += ["", "## 6. Kết quả theo `--slice %s`" % dimension, "",
                  md_table([dimension] + metrics,
                           [[value] + [fmt(group.get(m)) for m in metrics]
                            for value, group in sorted(groups.items())])]

    wrong_perf = [p for p in preds if not p["ok_performer"]]
    lines += ["", "## 7. Mẫu sai performer (%d/%d)" % (len(wrong_perf), total), ""]
    if wrong_perf:
        lines.append(md_table(
            ["sample_id", "split", "expected", "predicted", "conf", "label_status", "variant_type", "bước con"],
            [[p["sample_id"], p["split"], p["expected_performer"], p["predicted_performer"],
              fmt(p["perf_confidence"]), p["label_status"], p["variant_type"], p["substep_quote"][:70]]
             for p in wrong_perf]))
        pairs = Counter((p["expected_performer"], p["predicted_performer"]) for p in wrong_perf)
        lines += ["", "Tổng hợp lỗi performer (expected -> predicted):", "",
                  md_table(["expected", "predicted", "so mau"],
                           [[a, b, n] for (a, b), n in pairs.most_common()])]
    else:
        lines.append("Không có mẫu nào sai.")

    wrong_evi = [p for p in preds if not p["ok_evidence"]]
    wrong_mix = [p for p in preds if not p["ok_mixed_lanes"]]
    lines += ["", "## 8. Mẫu sai evidence (%d) và mixed_lanes (%d)"
              % (len(wrong_evi), len(wrong_mix)), ""]
    if wrong_evi:
        lines.append(md_table(
            ["sample_id", "expected", "predicted", "conf"],
            [[p["sample_id"], p["expected_evidence"], p["predicted_evidence"],
              fmt(p["evi_confidence"])] for p in wrong_evi]))
    if wrong_mix:
        lines.append("")
        lines.append(md_table(
            ["sample_id", "expected", "noul", "predicted"],
            [[p["sample_id"], p["expected_mixed_lanes"], fmt(p["noul_mixed_lanes"]),
              p["predicted_mixed_lanes"]] for p in wrong_mix]))

    lines += ["", "## 9. Phân bố nhãn", ""]
    dist = Counter(p["expected_performer"] for p in preds)
    lines.append(md_table(["expected_performer", "so mau", "ty le"],
                          [[k, n, "%.1f%%" % (100.0 * n / total)]
                           for k, n in sorted(dist.items(), key=lambda kv: -kv[1])]))
    lines += ["", "Phân bố evidence / mixed_lanes:", ""]
    lines.append(md_table(["nhãn", "so mau"],
                          [[k, n] for k, n in
                           sorted(Counter(p["expected_evidence"] for p in preds).items())]
                          + [[k, n] for k, n in
                             sorted(Counter(p["expected_mixed_lanes"] for p in preds).items())]))

    with open(out_dir + "/report.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("build_p2_report: performer=%.4f evidence=%.4f mixed=%.4f"
          % (n_perf / total, n_evi / total, n_mix / total))


if __name__ == "__main__":
    main()


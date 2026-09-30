import csv
import json
import sys
import time

from laya import Router


def percentile(values, q):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * q))]


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit("dung: collect_usage.py <dataset.jsonl> <usage.csv> [model]")
    dataset_path, out_path = sys.argv[1], sys.argv[2]
    forced_model = sys.argv[3] if len(sys.argv) == 4 else None

    rows = []
    with open(dataset_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                rows.append(json.loads(line))

    router = Router(device="cpu", preload=False)
    latencies = []
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["index", "qid", "checkpoint", "expected", "predicted",
                         "answer_confidence", "correct", "latency_ms",
                         "input_tokens", "output_tokens"])
        for index, row in enumerate(rows):
            started = time.perf_counter()
            result = router.predict(row["state"], row["questions"],
                                    model=forced_model or row.get("model"))
            elapsed = (time.perf_counter() - started) * 1000.0
            latencies.append(elapsed)
            usage = result.get("usage") or {}
            answers = result.get("answers") or {}
            routing = (result.get("routing") or {}).get("model") or result.get("model") or ""
            for qid, expected in (row.get("expected") or {}).items():
                answer = answers.get(qid) or {}
                confidence = answer.get("answer_confidence")
                if answer.get("type") == "noul":
                    predicted = str(bool(float(answer.get("noul") or 0.0) >= 0.5)).lower()
                    expected_text = str(bool(expected)).lower()
                else:
                    predicted = answer.get("choice")
                    expected_text = str(expected)
                writer.writerow([
                    index, qid, routing, expected_text, predicted, confidence,
                    int(str(predicted) == str(expected_text)), round(elapsed, 1),
                    usage.get("input_tokens"), usage.get("output_tokens"),
                ])
            if (index + 1) % 20 == 0:
                print("collect_usage: %d/%d (p50=%d ms)" % (index + 1, len(rows),
                      percentile(latencies, 0.5)), flush=True)
    total = sum(latencies)
    print("collect_usage: %d yeu cau, tong %.1f s, p50=%d ms, p95=%d ms -> %s"
          % (len(rows), total / 1000.0, percentile(latencies, 0.5),
             percentile(latencies, 0.95), out_path))


if __name__ == "__main__":
    main()

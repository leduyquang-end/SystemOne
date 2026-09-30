import csv
import json
import sys

LABELS = ("and", "or", "insufficient_evidence")

QUESTIONS = {
    "relation": {
        "type": "choice",
        "instructions": "Trong câu điều kiện, left_condition và right_condition có quan hệ logic gì với nhau?",
        "criteria": {
            "and": "cả hai điều kiện phải được thỏa đồng thời (và, đồng thời, giao, dấu phẩy liệt kê cùng cấp)",
            "or": "chỉ cần thỏa một trong hai điều kiện (hoặc, HOẶC)",
            "insufficient_evidence": "không đủ căn cứ trong câu để kết luận quan hệ",
        },
    }
}


def state_of(payload):
    return (
        "Câu điều kiện: {clause}\n"
        "Điều kiện 1 (left): {left}\n"
        "Điều kiện 2 (right): {right}"
    ).format(
        clause=payload.get("clause_text") or "",
        left=payload.get("left_condition") or "",
        right=payload.get("right_condition") or "",
    )


def main():
    if len(sys.argv) != 3:
        raise SystemExit("dung: build_p1_dataset.py <input.csv> <output.jsonl>")
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    written = 0
    with open(dst, "w", encoding="utf-8") as out:
        for row in rows:
            payload = json.loads(row["input_json"])
            expected = row["expected_relation"]
            if expected not in LABELS:
                raise SystemExit("label khong hop le o %s: %r" % (row["sample_id"], expected))
            record = {
                "state": state_of(payload),
                "questions": QUESTIONS,
                "expected": {"relation": expected},
                "tags": [row["pair_scope"], row["label_status"]],
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1
    print("build_p1_dataset: %d dong -> %s" % (written, dst))


if __name__ == "__main__":
    main()


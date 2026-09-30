import csv
import json
import sys

EVIDENCE_LABELS = ("verb", "object", "context")

QUESTIONS = {
    "performer": {
        "type": "choice",
        "instructions": (
            "Bước con được xét do cấu phần nào thực hiện? Chỉ chọn một id trong danh sách "
            "các cấu phần; chọn insufficient_evidence nếu câu nghiệp vụ không đủ căn cứ."
        ),
        "criteria": {},
    },
    "evidence": {
        "type": "choice",
        "instructions": "Căn cứ dùng để kết luận performer lấy từ đâu?",
        "criteria": {
            "verb": "verb - việc được làm, đọc từ động từ của bước con",
            "object": "object - dữ liệu được xử lý trong bước con",
            "context": "context - ngữ cảnh, chủ ngữ hoặc từ khóa khác trong câu",
        },
    },
    "mixed_lanes": {
        "type": "noul",
        "instructions": "Bước con có gộp việc của nhiều cấu phần và cần được tách không?",
    },
}


def state_of(payload):
    subject = payload.get("subject") or {}
    steps = payload.get("substeps") or []
    step = steps[0] if steps else {}
    lines = [
        "Câu nghiệp vụ: %s" % (payload.get("row_text") or ""),
        "Chủ ngữ (subject): %s (%s)" % (subject.get("text") or "", subject.get("resolution") or ""),
        "Bước con cần xét [%s]: %s" % (step.get("step_key") or "", step.get("quote") or ""),
        "Các cấu phần được phép chọn:",
    ]
    for member in payload.get("members") or []:
        lines.append("- id=%s | tên=%s | tầng=%s | mô tả=%s"
                     % (member.get("id") or "", member.get("name") or "",
                        member.get("tier") or "", member.get("description") or ""))
    return "\n".join(lines)


def questions_of(payload):
    criteria = {"insufficient_evidence": "không đủ căn cứ trong câu nghiệp vụ để chọn cấu phần"}
    for member in payload.get("members") or []:
        criteria[member.get("id")] = "%s (%s) - %s" % (
            member.get("name") or "", member.get("tier") or "", member.get("description") or "")
    questions = {key: dict(value) for key, value in QUESTIONS.items()}
    questions["performer"]["criteria"] = criteria
    return questions


def main():
    if len(sys.argv) != 3:
        raise SystemExit("dung: build_p2_dataset.py <input.csv> <output.jsonl>")
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    written = 0
    with open(dst, "w", encoding="utf-8") as out:
        for row in rows:
            payload = json.loads(row["input_json"])
            performer = row["expected_performer"]
            member_ids = {m.get("id") for m in payload.get("members") or []}
            if performer != "insufficient_evidence" and performer not in member_ids:
                raise SystemExit("expected_performer khong nam trong members: %s" % row["sample_id"])
            evidence = row["expected_evidence"]
            if evidence not in EVIDENCE_LABELS:
                raise SystemExit("expected_evidence khong hop le: %r" % evidence)
            mixed = row["expected_mixed_lanes"].strip().lower()
            if mixed not in ("true", "false"):
                raise SystemExit("expected_mixed_lanes khong hop le: %r" % mixed)
            record = {
                "state": state_of(payload),
                "questions": questions_of(payload),
                "expected": {
                    "performer": performer,
                    "evidence": evidence,
                    "mixed_lanes": mixed == "true",
                },
                "tags": [row["split"], row["label_status"]],
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1
    print("build_p2_dataset: %d dong -> %s" % (written, dst))


if __name__ == "__main__":
    main()


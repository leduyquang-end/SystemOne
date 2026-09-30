import argparse
import collections
import json
import random

P1_RELABEL = {"and": "requires_both", "or": "requires_either"}

MIXED_CHOICE_QUESTION = {
    "type": "choice",
    "instructions": "Buộc con có gặp việc của nhiều cấu phần không? Chọn nhãn mô tả đúng kết luận.",
    "criteria": {
        "tach_rieng": "tach_rieng - viec gap nhieu cau phan va can duoc tach rieng tung cau phan",
        "khong_can_tach": "khong_can_tach - viec thuoc mot cau phan duy nhat, khong can tach",
    },
}

MIXED_CHOICE_MAP = {
    True: "tach_rieng", False: "khong_can_tach",
    "True": "tach_rieng", "False": "khong_can_tach",
}

P2_QUESTIONS = ("performer", "evidence", "mixed_lanes")


def read_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def tagged(row, extra):
    return dict(row, tags=list(row.get("tags") or []) + list(extra))


def relabel_choice(row, qid, mapping):
    question = dict(row["questions"][qid])
    criteria = question.get("criteria") or {}
    question["criteria"] = {mapping.get(k, k): v for k, v in criteria.items()}
    questions = dict(row["questions"], **{qid: question})
    expected = dict(row["expected"])
    expected[qid] = mapping.get(expected[qid], expected[qid])
    return dict(row, questions=questions, expected=expected)


def pick_question(row, qid, extra_tags=()):
    return tagged({"state": row["state"],
                   "questions": {qid: row["questions"][qid]},
                   "expected": {qid: row["expected"][qid]}}, extra_tags)


def balance(rows, label_of, target, rng, tag):
    buckets = collections.defaultdict(list)
    for index, row in enumerate(rows):
        buckets[str(label_of(row))].append(index)
    kept, stats = [], {}
    for label, indexes in sorted(buckets.items()):
        if len(indexes) >= target:
            pick = rng.sample(indexes, target)
            duplicates = []
        else:
            pick = list(indexes)
            duplicates = rng.choices(indexes, k=target - len(indexes))
        for position, source in enumerate(pick + duplicates):
            row = rows[source]
            extra = [tag]
            if position >= len(pick):
                extra.append("duplicate")
            kept.append(tagged(row, extra))
        stats[label] = {"before": len(indexes), "after": target,
                        "duplicated": max(0, target - len(indexes)),
                        "dropped": max(0, len(indexes) - target)}
    rng.shuffle(kept)
    return kept, stats


def label_distribution(rows, qid):
    return dict(sorted(collections.Counter(str(r["expected"][qid]) for r in rows).items()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--p1", required=True)
    parser.add_argument("--p2", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--target", type=int, default=40)
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    p1 = read_jsonl(args.p1)
    p2 = read_jsonl(args.p2)
    manifest = {"seed": args.seed, "target_per_class": args.target, "files": {}}

    def record(name, rows, qid, note, stats=None):
        write_jsonl("%s/%s.jsonl" % (args.out_dir, name), rows)
        manifest["files"][name] = {"rows": len(rows), "questions": qid, "note": note,
                                   "labels": label_distribution(rows, qid),
                                   "balance": stats}

    p1_full = [relabel_choice(r, "relation", P1_RELABEL) for r in p1]
    record("p1_relabel_full", p1_full, "relation",
           "200 mau goc, chi doi nhan and/or -> requires_both/requires_either")

    p1_bal, p1_stats = balance(p1_full, lambda r: r["expected"]["relation"],
                               args.target, rng, "balanced")
    record("p1_balanced", p1_bal, "relation",
           "nhan moi + can bang lop (moi lop %d mau)" % args.target, p1_stats)

    p2_full = []
    for row in p2:
        row = tagged(row, ["relabeled"])
        questions = dict(row["questions"])
        expected = dict(row["expected"])
        questions["mixed_lanes"] = dict(MIXED_CHOICE_QUESTION)
        expected["mixed_lanes"] = MIXED_CHOICE_MAP[expected["mixed_lanes"]]
        p2_full.append(dict(row, questions=questions, expected=expected))
    record("p2_relabel_full", p2_full, "performer",
           "200 mau goc; mixed_lanes chuyen tu noul true/false sang choice tach_rieng/khong_can_tach; "
           "performance + evidence giu nhan goc")

    performer = [pick_question(r, "performer", ["optimized"]) for r in p2]
    bal, stats = balance(performer, lambda r: r["expected"]["performer"],
                         args.target, rng, "balanced")
    record("p2_performer_balanced", bal, "performer",
           "chi cau hoi performer, can bang %d mau/lop" % args.target, stats)

    evidence = [pick_question(r, "evidence", ["optimized"]) for r in p2]
    bal, stats = balance(evidence, lambda r: r["expected"]["evidence"],
                         args.target, rng, "balanced")
    record("p2_evidence_balanced", bal, "evidence",
           "chi cau hoi evidence, can bang %d mau/lop" % args.target, stats)

    mixed_noul = [pick_question(r, "mixed_lanes", ["optimized"]) for r in p2]
    bal, stats = balance(mixed_noul, lambda r: r["expected"]["mixed_lanes"],
                         args.target, rng, "balanced")
    record("p2_mixed_lanes_balanced", bal, "mixed_lanes",
           "noul true/false goc, can bang %d mau/nhan" % args.target, stats)

    mixed_choice = []
    for row in p2:
        row = pick_question(tagged(row, ["relabeled"]), "mixed_lanes", ["optimized"])
        questions = dict(row["questions"])
        questions["mixed_lanes"] = dict(MIXED_CHOICE_QUESTION)
        expected = dict(row["expected"])
        expected["mixed_lanes"] = MIXED_CHOICE_MAP[expected["mixed_lanes"]]
        mixed_choice.append(dict(row, questions=questions, expected=expected))
    bal, stats = balance(mixed_choice, lambda r: r["expected"]["mixed_lanes"],
                         args.target, rng, "balanced")
    record("p2_mixed_lanes_choice_balanced", bal, "mixed_lanes",
           "noul chuyen choice nhan nghe nghia + can bang %d mau/lop" % args.target, stats)

    manifest["label_mapping_p1"] = P1_RELABEL
    manifest["label_mapping_mixed_lanes"] = {str(k): v for k, v in MIXED_CHOICE_MAP.items()}
    with open("%s/manifest.json" % args.out_dir, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    for name, info in manifest["files"].items():
        print("%-34s %4d rows  %s" % (name, info["rows"], info["labels"]))


if __name__ == "__main__":
    main()

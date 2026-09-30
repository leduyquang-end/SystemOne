import glob
import json
import os
import sys


def main():
    roots = sys.argv[1:] or [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]
    paths = []
    for root in roots:
        paths.extend(glob.glob(os.path.join(root, "optimized", "*.jsonl")))
        paths.extend(glob.glob(os.path.join(root, "standard_benchmarks", "*.jsonl")))
        paths.extend(glob.glob(os.path.join(root, "p1_condition_relation", "dataset.jsonl")))
        paths.extend(glob.glob(os.path.join(root, "p2_performer_lane", "dataset.jsonl")))
    errors = 0
    for path in sorted(set(paths)):
        rows = 0
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            row = json.loads(line)
            if not row.get("state"):
                print("EMPTY state:", path)
                errors += 1
            for qid, expected in row["expected"].items():
                question = row["questions"][qid]
                if question["type"] == "choice":
                    keys = list(question["criteria"].keys())
                    if expected not in keys:
                        print("BAD choice label: %s %s -> %s (keys %s)"
                              % (os.path.basename(path), qid, expected, keys))
                        errors += 1
                elif question["type"] == "noul":
                    if str(expected).lower() not in ("true", "false"):
                        print("BAD noul label: %s %s -> %s"
                              % (os.path.basename(path), qid, expected))
                        errors += 1
                elif question["type"] == "score":
                    float(expected)
            rows += 1
        print("%-40s %4d rows" % (os.path.basename(path), rows))
    print("errors:", errors)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

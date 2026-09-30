import argparse
import collections
import json
import os
import random

from huggingface_hub import hf_hub_download

SPECS = {
    "ag_news": {
        "repo": "fancyzhx/ag_news",
        "filename": "data/test-00000-of-00001.parquet",
        "format": "parquet",
        "text": "text",
        "label": "label",
        "qid": "topic",
        "instructions": "Which topic category does this news article belong to?",
        "criteria": {
            "world": "world - international news, politics, conflict and diplomacy",
            "sports": "sports - matches, athletes, teams and competitions",
            "business": "business - companies, markets, economy and employment",
            "sci_tech": "sci_tech - science, technology, space and computing",
        },
        "labels": {0: "world", 1: "sports", 2: "business", 3: "sci_tech"},
    },
    "emotion": {
        "repo": "dair-ai/emotion",
        "filename": "split/test-00000-of-00001.parquet",
        "format": "parquet",
        "text": "text",
        "label": "label",
        "qid": "emotion",
        "instructions": "Which emotion does this first-person sentence express?",
        "criteria": {
            "sadness": "sadness - feeling down, sorrowful or depressed",
            "joy": "joy - feeling happy, pleased or delighted",
            "love": "love - affection, warmth or attachment toward someone",
            "anger": "anger - feeling annoyed, irritated or furious",
            "fear": "fear - feeling anxious, scared or worried",
            "surprise": "surprise - reacting to something unexpected",
        },
        "labels": {0: "sadness", 1: "joy", 2: "love", 3: "anger", 4: "fear", 5: "surprise"},
    },
    "enron_spam": {
        "repo": "SetFit/enron_spam",
        "filename": "test.jsonl",
        "format": "jsonl",
        "text": "text",
        "label": "label_text",
        "qid": "spam",
        "instructions": "Is this email spam or a legitimate message?",
        "criteria": {
            "spam": "spam - unsolicited advertising, scams or malicious email",
            "ham": "ham - legitimate personal or business email",
        },
        "labels": {"spam": "spam", "ham": "ham"},
    },
}


def load_rows(spec, cache_dir):
    path = hf_hub_download(repo_id=spec["repo"], filename=spec["filename"],
                           repo_type="dataset",
                           local_dir=os.path.join(cache_dir, spec["repo"].replace("/", "__")))
    rows = []
    if spec["format"] == "parquet":
        import pandas as pd
        for record in pd.read_parquet(path).to_dict("records"):
            rows.append(record)
    else:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def stratified_sample(rows, spec, count, rng):
    buckets = collections.defaultdict(list)
    for row in rows:
        buckets[spec["labels"][row[spec["label"]]]].append(row)
    total = len(rows)
    raw = {key: count * len(value) / total for key, value in buckets.items()}
    quota = {key: int(value) for key, value in raw.items()}
    for key in sorted(raw, key=lambda k: raw[k] - quota[k], reverse=True)[:count - sum(quota.values())]:
        quota[key] += 1
    sample = []
    for key, wanted in quota.items():
        pool = buckets[key]
        sample.extend(rng.sample(pool, min(wanted, len(pool))))
    rng.shuffle(sample)
    return sample


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    manifest = {"seed": args.seed, "count_per_dataset": args.count, "datasets": {}}

    for name, spec in SPECS.items():
        rows = load_rows(spec, args.cache_dir)
        sample = stratified_sample(rows, spec, args.count, rng)
        question = {"type": "choice", "instructions": spec["instructions"],
                    "criteria": dict(spec["criteria"])}
        with open("%s/%s.jsonl" % (args.out_dir, name), "w", encoding="utf-8") as fh:
            for row in sample:
                payload = {
                    "state": row[spec["text"]],
                    "questions": {spec["qid"]: question},
                    "expected": {spec["qid"]: spec["labels"][row[spec["label"]]]},
                    "tags": ["benchmark", name],
                    "language": "en",
                }
                fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
        labels = [spec["labels"][row[spec["label"]]] for row in sample]
        manifest["datasets"][name] = {
            "source": "%s/%s" % (spec["repo"], spec["filename"]),
            "rows": len(sample),
            "qid": spec["qid"],
            "labels": dict(sorted(collections.Counter(labels).items())),
            "majority_baseline": round(max(collections.Counter(labels).values()) / len(labels), 4),
            "source_rows": len(rows),
        }
        print("%-12s %4d/%d rows  baseline=%.3f  %s"
              % (name, len(sample), len(rows),
                 manifest["datasets"][name]["majority_baseline"],
                 manifest["datasets"][name]["labels"]))

    with open("%s/manifest.json" % args.out_dir, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

set -e

# 1) Official laya-evals reports for the three public Laya benchmark datasets.
for name in ag_news emotion enron_spam; do
  laya-evals run /out/standard_benchmarks/${name}.jsonl --device cpu --model multilingual --batch-size 8 --on-error fail --json /out/standard_benchmarks/${name}_report.json --markdown /out/standard_benchmarks/${name}_report.md
done

# 2) One inference pass per dataset: predictions, confidence, latency and token counts.
python /out/scripts/collect_usage.py /out/standard_benchmarks/ag_news.jsonl /out/standard_benchmarks/ag_news_usage.csv multilingual
python /out/scripts/collect_usage.py /out/standard_benchmarks/emotion.jsonl /out/standard_benchmarks/emotion_usage.csv multilingual
python /out/scripts/collect_usage.py /out/standard_benchmarks/enron_spam.jsonl /out/standard_benchmarks/enron_spam_usage.csv multilingual
python /out/scripts/collect_usage.py /out/optimized/p1_relabel_full.jsonl /out/optimized/p1_relabel_full_usage.csv multilingual
python /out/scripts/collect_usage.py /out/optimized/p1_balanced.jsonl /out/optimized/p1_balanced_usage.csv multilingual
python /out/scripts/collect_usage.py /out/optimized/p2_relabel_full.jsonl /out/optimized/p2_relabel_full_usage.csv multilingual
python /out/scripts/collect_usage.py /out/optimized/p2_performer_balanced.jsonl /out/optimized/p2_performer_balanced_usage.csv multilingual
python /out/scripts/collect_usage.py /out/optimized/p2_evidence_balanced.jsonl /out/optimized/p2_evidence_balanced_usage.csv multilingual
python /out/scripts/collect_usage.py /out/optimized/p2_mixed_lanes_balanced.jsonl /out/optimized/p2_mixed_lanes_balanced_usage.csv multilingual
python /out/scripts/collect_usage.py /out/optimized/p2_mixed_lanes_choice_balanced.jsonl /out/optimized/p2_mixed_lanes_choice_balanced_usage.csv multilingual

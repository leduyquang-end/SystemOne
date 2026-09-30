set -e
python /out/scripts/collect_usage.py /out/p1_condition_relation/dataset.jsonl /out/p1_condition_relation/usage.csv
python /out/scripts/collect_usage.py /out/p2_performer_lane/dataset.jsonl /out/p2_performer_lane/usage.csv

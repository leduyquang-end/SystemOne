set -e
python /out/scripts/build_p2_dataset.py /data/p2_performer_lane_poc_200_1.csv /out/p2_performer_lane/dataset.jsonl
laya-evals run /out/p2_performer_lane/dataset.jsonl --device cpu --slice qid --slice tag --on-error fail --json /out/p2_performer_lane/laya_evals_report.json --markdown /out/p2_performer_lane/laya_evals_report.md
python /out/scripts/build_p2_report.py /data/p2_performer_lane_poc_200.csv /data/p2_performer_lane_poc_200_1.csv /out/p2_performer_lane/laya_evals_report.json /out/p2_performer_lane

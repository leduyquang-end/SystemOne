set -e
python /out/scripts/build_p1_dataset.py /data/p1_condition_relation_poc_200_1.csv /out/p1_condition_relation/dataset.jsonl
laya-evals run /out/p1_condition_relation/dataset.jsonl --device cpu --batch-size 8 --slice tag --slice model --on-error fail --json /out/p1_condition_relation/laya_evals_report.json --markdown /out/p1_condition_relation/laya_evals_report.md
python /out/scripts/build_p1_report.py /data/p1_condition_relation_poc_200.csv /data/p1_condition_relation_poc_200_1.csv /out/p1_condition_relation/laya_evals_report.json /out/p1_condition_relation

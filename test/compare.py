import csv
import json
import sys

test_file = sys.argv[1]
result_files = sys.argv[2:]

tests = json.load(open(test_file))
results = [
    [json.loads(line) for line in open(result_file)]
    for result_file in result_files
]
results = [
    {x["record_id"]: x for x in records}
    for records in results
]

fields = ["Clean Title", "Top SOC6", "Probability", "SOC6 Match", "SOC3 Match", "SOC2 Match"]
result_names = [chr(i+65) for i in range(len(results))]

writer = csv.writer(sys.stdout)
writer.writerow(
    ["id", "title"] +
    sum(
        [[f"{field} {name}" for name in result_names] for field in fields],
        start=[]
    )
)

for test in tests:
    row = [test["id"], test["title"]]
    result = {result_names[i]: results[i].get(test["id"], {}) for i in range(len(results))}
    top = {name: (result[name]["socs"][0] if len(result[name]["socs"]) else {}) for name in result}
    # Clean Title
    for name in result_names:
        row.append(result[name].get("clean_title", ""))
    # Top SOC6
    for name in result_names:
        row.append(top[name].get("soc", "").replace("-", ""))
    # Probability
    for name in result_names:
        row.append(top[name].get("prob", ""))
    # SOC6 Match
    for name in result_names:
        soc = top[name].get("soc", "")
        row.append(f"{soc[:2]}-{soc[2:]}" in test["SOC6"])
    # SOC3 Match
    for name in result_names:
        row.append(top[name].get("soc", "")[:3] in test["SOC3"])
    # SOC2 Match
    for name in result_names:
        row.append(top[name].get("soc", "")[:2] in test["SOC2"])
    writer.writerow(row)

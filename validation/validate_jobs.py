import os
import pandas as pd
import sockit.parse

socs = pd.read_csv("../sockit/data/socs.csv", dtype=str)

for soc in socs.soc:
    print(soc)
    results = sockit.parse.parse_job_posting(f"jobs/{soc[:2]}-{soc[2:]}.00.txt", "txt")
    print(results["Occupations"][0])

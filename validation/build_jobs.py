import os
import pandas as pd

if not os.path.exists("jobs"):
    os.makedirs("jobs")

socs      = pd.read_csv("../sockit/data/socs.csv", dtype=str)
desc      = pd.read_csv("onet_db_27_0_text/Occupation Data.txt", delimiter="\t", dtype=str, index_col="O*NET-SOC Code")
task      = pd.read_csv("onet_db_27_0_text/Task Statements.txt", delimiter="\t", dtype=str)
activity  = task.merge(
                pd.read_csv("onet_db_27_0_text/Tasks to DWAs.txt", delimiter="\t", dtype=str, usecols=["Task ID", "DWA ID"]),
                how="left",
                on="Task ID"
            ).merge(
                pd.read_csv("onet_db_27_0_text/DWA Reference.txt", delimiter="\t", dtype=str, usecols=["DWA ID", "DWA Title"]),
                how="left",
                on="DWA ID"
            ).dropna()

for soc in socs.soc:
    soc = "{}-{}.00".format(soc[:2], soc[2:])
    print(soc)
    with open(f"jobs/{soc}.txt", "w") as f:
        print(desc.loc[soc, "Title"], file=f)
        print(desc.loc[soc, "Description"], file=f)
        print("\n".join(task.loc[task["O*NET-SOC Code"] == soc, "Task"]), file=f)
        print("\n".join(activity.loc[activity["O*NET-SOC Code"] == soc, "DWA Title"]), file=f)

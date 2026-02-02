import json
import matplotlib.pyplot as plt

with open("charts/data.json") as f:
    data = json.load(f)

orgs = list(data.keys())
merged = [data[o]["MERGED"] for o in orgs]
open_prs = [data[o]["OPEN"] for o in orgs]
closed = [data[o]["CLOSED"] for o in orgs]

plt.figure(figsize=(10, 6))

plt.bar(orgs, merged, label="Merged", color="#2ea44f")
plt.bar(orgs, open_prs, bottom=merged, label="Open", color="#0366d6")
plt.bar(
    orgs,
    closed,
    bottom=[merged[i] + open_prs[i] for i in range(len(orgs))],
    label="Closed",
    color="#d73a49",
)

plt.xticks(rotation=30, ha="right")
plt.ylabel("Pull Requests")
plt.title("Open Source Contributions by Organization")
plt.legend()
plt.tight_layout()

plt.savefig("charts/org_contributions.svg")
plt.close()

print("Chart generated")
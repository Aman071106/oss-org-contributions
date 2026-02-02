import json
import matplotlib.pyplot as plt

# 1. Load Data
with open("charts/data.json") as f:
    data = json.load(f)

# 2. Filter & Sort Data
YOUR_USERNAME = "Aman071106" 
if YOUR_USERNAME in data:
    del data[YOUR_USERNAME]

# Filter: Keep only orgs where you have MERGED or OPEN PRs
# (We ignore 'CLOSED' counts completely for filtering now)
active_orgs = {
    k: v for k, v in data.items() 
    if v["MERGED"] > 0 or v["OPEN"] > 0
}

# Sort: Highest MERGED count first, then OPEN count
sorted_orgs = sorted(
    active_orgs.keys(), 
    key=lambda x: (active_orgs[x]["MERGED"], active_orgs[x]["OPEN"]), 
    reverse=True
)

# Limit to Top 10
sorted_orgs = sorted_orgs[:10]

orgs = sorted_orgs
merged = [active_orgs[o]["MERGED"] for o in orgs]
open_prs = [active_orgs[o]["OPEN"] for o in orgs]

# 3. Theme Settings (GitHub Dark)
plt.style.use('dark_background')
plt.rcParams['text.color'] = '#c9d1d9'
plt.rcParams['axes.labelcolor'] = '#c9d1d9'
plt.rcParams['xtick.color'] = '#8b949e'
plt.rcParams['ytick.color'] = '#8b949e'
plt.rcParams['font.family'] = 'sans-serif'

fig, ax = plt.subplots(figsize=(10, 6))

# Transparent Background
fig.patch.set_alpha(0.0) 
ax.patch.set_alpha(0.0)

# 4. Plotting (Only Merged and Open)
bar_width = 0.6

# Layer 1: Merged (Purple)
p1 = plt.bar(orgs, merged, width=bar_width, label="Merged", color="#8957e5", edgecolor='#8957e5')

# Layer 2: Open (Green) - Stacked on top of Merged
p2 = plt.bar(orgs, open_prs, width=bar_width, bottom=merged, label="Open", color="#238636", edgecolor='#238636')

# 5. Styling
plt.xticks(rotation=45, ha="right", fontsize=10, weight='bold')
plt.yticks(fontsize=10)
plt.ylabel("Pull Requests", fontsize=12, weight='bold')
plt.title("Top External OSS Contributions", fontsize=16, weight='bold', pad=20)

# Clean Borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#30363d')
ax.spines['left'].set_color('#30363d')

# Gridlines
ax.yaxis.grid(True, color='#30363d', linestyle='--', linewidth=0.5, alpha=0.5)
ax.set_axisbelow(True)

# Legend
plt.legend(frameon=False, loc='upper right', fontsize=10)

plt.tight_layout()

# 6. Save
plt.savefig("charts/org_contributions.svg", transparent=True, bbox_inches='tight')
plt.close()

print(f"Chart generated (Closed PRs excluded) for {len(orgs)} organizations.")
import json
import matplotlib.pyplot as plt

# Load Data
with open("charts/data.json") as f:
    data = json.load(f)

orgs = list(data.keys())
merged = [data[o]["MERGED"] for o in orgs]
open_prs = [data[o]["OPEN"] for o in orgs]
closed = [data[o]["CLOSED"] for o in orgs]

# --- THEME SETTINGS (Matches GitHub Dark) ---
plt.style.use('dark_background')
plt.rcParams['text.color'] = '#c9d1d9'       # GitHub Dark Text
plt.rcParams['axes.labelcolor'] = '#c9d1d9'
plt.rcParams['xtick.color'] = '#8b949e'      # GitHub Dim Text
plt.rcParams['ytick.color'] = '#8b949e'
plt.rcParams['font.family'] = 'sans-serif'

fig, ax = plt.subplots(figsize=(10, 6))

# Transparent background for the plot area
fig.patch.set_alpha(0.0) 
ax.patch.set_alpha(0.0)

# Colors matching GitHub PR statuses
# Merged: Purple/Green (Neon style), Open: Green/Blue, Closed: Red
bar_width = 0.6
p1 = plt.bar(orgs, merged, width=bar_width, label="Merged", color="#8957e5", edgecolor='#8957e5') # GitHub Purple
p2 = plt.bar(orgs, open_prs, width=bar_width, bottom=merged, label="Open", color="#238636", edgecolor='#238636') # GitHub Green
p3 = plt.bar(orgs, closed, width=bar_width, bottom=[merged[i] + open_prs[i] for i in range(len(orgs))], label="Closed", color="#da3633", edgecolor='#da3633') # GitHub Red

# Customizing Axes
plt.xticks(rotation=45, ha="right", fontsize=10, weight='bold')
plt.yticks(fontsize=10)
plt.ylabel("Pull Requests", fontsize=12, weight='bold')
plt.title("OSS Contributions by Organization", fontsize=16, weight='bold', pad=20)

# Remove top and right spines for a cleaner look
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#30363d')
ax.spines['left'].set_color('#30363d')

# Legend with transparent background
plt.legend(frameon=False, loc='upper right', fontsize=10)

plt.tight_layout()

# Save with transparent background
plt.savefig("charts/org_contributions.svg", bgcolor='transparent', transparent=True)
plt.close()

print("Dark mode chart generated")
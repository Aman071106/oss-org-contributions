import os
import requests
from collections import defaultdict
import json

USERNAME = "Aman071106"
TOKEN = os.environ["GITHUB_TOKEN"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    pullRequests(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        state
        repository {
          owner {
            login
          }
        }
      }
    }
  }
}
"""

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

response = requests.post(
    "https://api.github.com/graphql",
    json={"query": QUERY, "variables": {"login": USERNAME}},
    headers=headers
)

data = response.json()

org_stats = defaultdict(lambda: {"MERGED": 0, "OPEN": 0, "CLOSED": 0})

for pr in data["data"]["user"]["pullRequests"]["nodes"]:
    org = pr["repository"]["owner"]["login"]
    org_stats[org][pr["state"]] += 1

os.makedirs("charts", exist_ok=True)

with open("charts/data.json", "w") as f:
    json.dump(org_stats, f, indent=2)

print("Fetched stats:", dict(org_stats))
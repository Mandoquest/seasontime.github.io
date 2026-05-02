import requests
import json
import os
from datetime import datetime, timezone

API_KEY = os.environ["BUNGIE_API_KEY"]
HEADERS = {"X-API-Key": API_KEY}

now = datetime.now(timezone.utc)

# Milestones abrufen
ms_url = "https://www.bungie.net/Platform/Destiny2/Milestones/"
ms_response = requests.get(ms_url, headers=HEADERS)
ms_response.raise_for_status()
ms_data = ms_response.json()

# Alle zukünftigen Enddaten sammeln und ausgeben (zum Debuggen)
print("Gefundene Enddaten:")
all_ends = []
for key, value in ms_data["Response"].items():
    end_str = value.get("endDate")
    if end_str:
        end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        diff_days = (end - now).days
        print(f"  Milestone {key}: {end_str} ({diff_days} Tage)")
        if end > now:
            all_ends.append(end)

# Das späteste zukünftige Enddatum nehmen
season_end = None
if all_ends:
    best_end = max(all_ends)
    season_end = best_end.isoformat()
    print(f"Season-Ende gespeichert: {season_end}")
else:
    print("Kein zukünftiges Enddatum gefunden.")

result = {
    "seasonEnd": season_end,
    "updatedAt": now.isoformat()
}

with open("season.json", "w") as f:
    json.dump(result, f, indent=2)

import requests
import json
import os
from datetime import datetime, timezone

API_KEY = os.environ["BUNGIE_API_KEY"]
HEADERS = {"X-API-Key": API_KEY}

# Season-Daten über den Settings-Endpoint holen
# Dieser Endpoint enthält das offizielle Season-Enddatum
url = "https://www.bungie.net/Platform/Settings/"
response = requests.get(url, headers=HEADERS)
response.raise_for_status()
data = response.json()

season_end = None
season_name = "Unbekannte Season"

try:
    destiny = data["Response"]["destiny2CoreSettings"]
    season_end   = destiny.get("currentSeasonalArtifactHash")  # nur als Check
    season_end   = destiny.get("futureSeasonHashes")           # nur als Check

    # Das echte Enddatum steckt in den Milestone-Daten
    ms_url = "https://www.bungie.net/Platform/Destiny2/Milestones/"
    ms_response = requests.get(ms_url, headers=HEADERS)
    ms_response.raise_for_status()
    ms_data = ms_response.json()

    # Season-Milestone hat die längste Laufzeit — wir filtern nach dem
    # Enddatum das am weitesten in der Zukunft liegt und mindestens
    # 14 Tage entfernt ist (um wöchentliche Events auszuschließen)
    now = datetime.now(timezone.utc)
    best_end = None

    for key, value in ms_data["Response"].items():
        end_str = value.get("endDate")
        if not end_str:
            continue
        end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        diff_days = (end - now).days
        if diff_days >= 14:  # Mindestens 2 Wochen entfernt = Season-Level
            if best_end is None or end > best_end:
                best_end = end

    if best_end:
        season_end = best_end.isoformat()
    else:
        season_end = None

except (KeyError, TypeError) as e:
    print(f"Fehler beim Parsen: {e}")
    season_end = None

result = {
    "seasonEnd": season_end,
    "updatedAt": now.isoformat()
}

with open("season.json", "w") as f:
    json.dump(result, f, indent=2)

if season_end:
    print(f"Season-Ende gespeichert: {season_end}")
else:
    print("Kein Season-Enddatum gefunden.")

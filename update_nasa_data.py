
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

api_key = os.environ.get("NASA_API_KEY")

if not api_key:
    raise RuntimeError("NASA_API_KEY secret is missing")

end_date = datetime.now(timezone.utc).date()
start_date = end_date - timedelta(days=7)

params = urllib.parse.urlencode({
    "startDate": start_date.isoformat(),
    "endDate": end_date.isoformat(),
    "api_key": api_key
})

url = "https://ccmc.gsfc.nasa.gov/DONKI-API/get/FLR?" + params

request = urllib.request.Request(
    url,
    headers={"User-Agent": "SolarWatch/1.0"}
)

with urllib.request.urlopen(request, timeout=30) as response:
    flares = json.loads(response.read().decode("utf-8"))

Path("data").mkdir(exist_ok=True)

with open("data/solar_flares.json", "w", encoding="utf-8") as file:
    json.dump({
        "updated": datetime.now(timezone.utc).isoformat(),
        "flares": flares
    }, file, indent=2)

print("NASA data updated successfully!")
print("Solar flares found:", len(flares))

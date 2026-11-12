import json
import threading
import urllib.request


NASA_DATA_URL = (
    "https://raw.githubusercontent.com/"
    "Mikhdad207/Solar-Watch/main/data/solar_flares.json"
)


class NasaFeed:
    """Loads the public NASA observations published by the Solar Watch workflow."""

    def __init__(self):
        self._lock = threading.Lock()
        self._status = "CONNECTING"
        self._flares = []
        self._updated = None

        thread = threading.Thread(target=self._load, daemon=True)
        thread.start()

    def _load(self):
        try:
            request = urllib.request.Request(
                NASA_DATA_URL,
                headers={"User-Agent": "SolarWatch/1.0"}
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))

            flares = payload.get("flares", [])
            if not isinstance(flares, list):
                raise ValueError("NASA data file has an invalid format")

            flares.sort(
                key=lambda item: item.get("beginTime") or "",
                reverse=True
            )

            with self._lock:
                self._flares = flares
                self._updated = payload.get("updated")
                self._status = "LIVE"

        except Exception:
            with self._lock:
                self._status = "OFFLINE"

    def snapshot(self):
        with self._lock:
            return self._status, list(self._flares), self._updated

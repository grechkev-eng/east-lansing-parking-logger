import csv
from datetime import datetime
import os
import sys
from zoneinfo import ZoneInfo
from curl_cffi import requests

API_URL = "https://cms.revize.com/revize/apps/eastlansingparking/"
CSV_FILE = "parking_data.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://cityofeastlansing.com/2186/Live-Parking-Availability",
    "Origin": "https://cityofeastlansing.com",
}


def log_parking_data():
  # Captures local East Lansing time in standard ISO 8601 format
  timestamp = datetime.now(ZoneInfo("America/Detroit")).isoformat()

  file_exists = os.path.exists(CSV_FILE)

  try:
    response = requests.get(
        API_URL, headers=HEADERS, impersonate="chrome", timeout=15
    )
    response.raise_for_status()
    garages = response.json()

    data_rows = []
    for garage in garages:
      data_rows.append([
          timestamp,
          garage.get("id"),
          garage.get("name"),
          garage.get("free"),
          garage.get("capacity"),
          garage.get("active"),
      ])

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
      writer = csv.writer(f)
      if not file_exists:
        writer.writerow([
            "timestamp",
            "facility_id",
            "facility_name",
            "available_spaces",
            "total_capacity",
            "is_active",
        ])
      writer.writerows(data_rows)

    print(f"[{timestamp}] Logged {len(data_rows)} rows to {CSV_FILE}")

  except Exception as e:
    print(f"[{timestamp}] Error logging data: {e}")
    sys.exit(1)


if __name__ == "__main__":
  log_parking_data()    sys.exit(1)


if __name__ == "__main__":
  log_parking_data()

import csv
from datetime import datetime
import os
import sys
from zoneinfo import ZoneInfo
from curl_cffi import requests

API_URL = "https://cms.revize.com/revize/apps/eastlansingparking/"
CSV_FILE = "parking_data.csv"

HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://cityofeastlansing.com/2186/Live-Parking-Availability",
    "Origin": "https://cityofeastlansing.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
}


def log_parking_data():
  eastern_tz = ZoneInfo("America/Detroit")
  timestamp = datetime.now(eastern_tz).strftime("%Y-%m-%d %H:%M:%S")
  file_exists = os.path.exists(CSV_FILE)

  try:
    response = requests.get(
        API_URL, headers=HEADERS, impersonate="chrome120", timeout=20
    )

    # --- Debug Outputs ---
    print(f"[{timestamp}] DEBUG Status Code: {response.status_code}")
    print(f"[{timestamp}] DEBUG Response Body:\n{response.text[:1000]}")
    # ---------------------

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
  log_parking_data()

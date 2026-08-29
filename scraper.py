import csv
from datetime import datetime
import os
import sys
from zoneinfo import ZoneInfo
import requests

APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycby_KvFLxrX07eWeIne7TliC4NQi_g9fdCt-XLN2c76B3VrtADqGw3s2ed-PVp1Yr8AU/exec"
CSV_FILE = "parking_data.csv"


def log_parking_data():
  eastern_tz = ZoneInfo("America/Detroit")
  timestamp = datetime.now(eastern_tz).strftime("%Y-%m-%d %H:%M:%S")
  file_exists = os.path.exists(CSV_FILE)

  try:
    # requests.get follows Google Apps Script's 302 redirects automatically
    response = requests.get(APPS_SCRIPT_URL, timeout=30)
    response.raise_for_status()

    # Verify response is valid JSON
    try:
      garages = response.json()
    except Exception:
      print(f"[{timestamp}] Failed to parse JSON response. Raw output:")
      print(response.text[:500])
      sys.exit(1)

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

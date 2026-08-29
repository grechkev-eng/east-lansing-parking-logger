import csv
from datetime import datetime
import os
import sys
from zoneinfo import ZoneInfo
import requests

WORKER_URL = "https://parking-proxy.grechkev.workers.dev/"
CSV_FILE = "parking_data.csv"


def log_parking_data():
  eastern_tz = ZoneInfo("America/Detroit")
  timestamp = datetime.now(eastern_tz).strftime("%Y-%m-%d %H:%M:%S")
  file_exists = os.path.exists(CSV_FILE)

  try:
    response = requests.get(WORKER_URL, timeout=20)
    response.raise_for_status()

    # Verify JSON structure before parsing
    try:
      garages = response.json()
    except Exception:
      print(f"[{timestamp}] Failed to parse JSON. Raw body:")
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

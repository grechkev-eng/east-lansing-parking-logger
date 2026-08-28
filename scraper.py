import csv
from datetime import datetime
import os
import requests

API_URL = "https://cms.revize.com/revize/apps/eastlansingparking/"
CSV_FILE = "parking_data.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def log_parking_data():
  timestamp = datetime.now().isoformat()
  file_exists = os.path.exists(CSV_FILE)

  try:
    response = requests.get(API_URL, headers=HEADERS, timeout=15)
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


if __name__ == "__main__":
  log_parking_data()

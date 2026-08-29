import csv
from datetime import datetime
import os
import sys
from zoneinfo import ZoneInfo
import requests

API_URL = "https://cms.revize.com/revize/apps/eastlansingparking/"
CSV_FILE = "parking_data.csv"


def log_parking_data():
  eastern_tz = ZoneInfo("America/Detroit")
  timestamp = datetime.now(eastern_tz).strftime("%Y-%m-%d %H:%M:%S")
  file_exists = os.path.exists(CSV_FILE)

  # Check if ScraperAPI key exists in environment variables
  scraper_key = os.getenv("SCRAPER_API_KEY")

  if scraper_key:
    # Route through ScraperAPI to bypass Cloudflare IP blocks
    target_url = "http://api.scraperapi.com"
    params = {
        "api_key": scraper_key,
        "url": API_URL,
    }
    response = requests.get(target_url, params=params, timeout=30)
  else:
    # Fallback for local testing without ScraperAPI
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(API_URL, headers=headers, timeout=20)

  try:
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
    print(f"Response Body: {response.text[:500]}")
    sys.exit(1)


if __name__ == "__main__":
  log_parking_data()

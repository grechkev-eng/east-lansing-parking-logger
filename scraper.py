import csv
from datetime import datetime
import json
import os
import sys
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

API_URL = "https://cms.revize.com/revize/apps/eastlansingparking/"
PAGE_URL = "https://cityofeastlansing.com/2186/Live-Parking-Availability"
CSV_FILE = "parking_data.csv"


def log_parking_data():
  eastern_tz = ZoneInfo("America/Detroit")
  timestamp = datetime.now(eastern_tz).strftime("%Y-%m-%d %H:%M:%S")
  file_exists = os.path.exists(CSV_FILE)

  try:
    with sync_playwright() as p:
      browser = p.chromium.launch(headless=True)
      context = browser.new_context(
          user_agent=(
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
              " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
          ),
          extra_http_headers={"Referer": PAGE_URL},
      )
      page = context.new_page()

      # Navigate directly to the API URL (top-level navigation bypasses CORS)
      page.goto(API_URL, wait_until="networkidle", timeout=30000)

      # Pause briefly for any Cloudflare challenge redirection to settle
      page.wait_for_timeout(3000)

      # Extract the raw JSON text from the browser body
      body_text = page.locator("body").inner_text()
      browser.close()

    garages = json.loads(body_text)

    if not isinstance(garages, list):
      raise ValueError(f"Unexpected response format: {type(garages)}")

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

#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone

import requests

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    "?vs_currency=usd&days=30&interval=daily"
)

OUTPUT_DIR  = "docs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "index.html")


def fetch_bitcoin_data():
    print("Fetching Bitcoin data from CoinGecko...")
    response = requests.get(
        COINGECKO_URL,
        headers={"accept": "application/json"},
        timeout=15,
    )
    response.raise_for_status()

    raw = response.json()
    formatted = []
    for timestamp_ms, price in raw.get("prices", []):
        dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        formatted.append({"date": dt.strftime("%b %d"), "price": round(price, 2)})

    print(f"  Fetched {len(formatted)} data points.")
    return formatted


def build_html(data):
    data_json    = json.dumps(data)
    generated_at = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    # Returns a complete HTML page — see the full version in scripts/generate_static.py
    # The key line is: const BITCOIN_DATA = {data_json};
    # This bakes the fetched data directly into the page so no runtime fetch is needed.
    ...


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)   # creates docs/ if it doesn't exist
    print(f"Output directory ready: {OUTPUT_DIR}/")

    data = fetch_bitcoin_data()
    html = build_html(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        fh.write(html)

    print(f"Written to {OUTPUT_FILE} ({len(html):,} bytes).")


if __name__ == "__main__":
    main()
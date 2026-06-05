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
        data_json = json.dumps(data, ensure_ascii=False)
        # Avoid accidentally terminating the <script> tag if data ever contains '</'.
        data_json = data_json.replace("</", "<\\/")
 
        generated_at = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
 
        return f"""<!DOCTYPE html>
            <html lang=\"en\">
            <head>
                <meta charset=\"utf-8\" />
                <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
                <title>Bitcoin Price Tracker</title>
                <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background: linear-gradient(135deg, #0f172a, #1e293b);
                        color: #f8fafc;
                        text-align: center;
                        padding: 30px;
                    }}
                    h1 {{
                        margin-bottom: 20px;
                    }}
                    .card {{
                        background: #1e293b;
                        border-radius: 16px;
                        padding: 20px;
                        max-width: 900px;
                        margin: auto;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                    }}
                    canvas {{
                        margin-top: 20px;
                    }}
                    .footer {{
                        margin-top: 20px;
                        opacity: 0.7;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <h1>📈 Bitcoin Price (Last 30 Days)</h1>
                <div class=\"card\">
                    <canvas id=\"chart\"></canvas>
                </div>
                <div class=\"footer\">Data from CoinGecko • Generated {generated_at}</div>
            
                <script>
                    const BITCOIN_DATA = {data_json};
            
                    const labels = BITCOIN_DATA.map(p => p.date);
                    const prices = BITCOIN_DATA.map(p => p.price);
            
                    const ctx = document.getElementById('chart').getContext('2d');
                    new Chart(ctx, {{
                        type: 'line',
                        data: {{
                            labels,
                            datasets: [{{
                                label: 'BTC Price (USD)',
                                data: prices,
                                borderColor: '#38bdf8',
                                backgroundColor: 'rgba(56,189,248,0.2)',
                                tension: 0.3,
                                fill: true,
                                pointRadius: 0
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            plugins: {{
                                legend: {{
                                    labels: {{ color: '#f8fafc' }}
                                }}
                            }},
                            scales: {{
                                x: {{ ticks: {{ color: '#cbd5f5' }} }},
                                y: {{ ticks: {{ color: '#cbd5f5' }} }}
                            }}
                        }}
                    }});
                </script>
            </body>
            </html>
            """

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
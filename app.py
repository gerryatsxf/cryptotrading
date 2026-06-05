# app.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import requests
from datetime import datetime

app = FastAPI(title="Bitcoin Price Dashboard")

COINGECKO_API = (
    "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    "?vs_currency=usd&days=30&interval=daily"
)


@app.get("/api/bitcoin")
def bitcoin_data(): 
    try:
        response = requests.get(
            COINGECKO_API,
            headers={"accept": "application/json"},
            timeout=15,
        )
        response.raise_for_status()

        data = response.json()
        prices = data.get("prices", [])

        formatted = []
        for timestamp, price in prices:
            dt = datetime.utcfromtimestamp(timestamp / 1000).strftime("%b %d")
            formatted.append({
                "date": dt,
                "price": round(price, 2),
            })

        return JSONResponse(content=formatted)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Bitcoin 30-Day Price Tracker</title>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Inter, Arial, sans-serif;
            background: linear-gradient(135deg, #0f172a, #111827);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }

        .container {
            width: 100%;
            max-width: 1100px;
        }

        .card {
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 24px;
            padding: 32px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.35);
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 24px;
        }

        .title {
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
        }

        .subtitle {
            color: rgba(255,255,255,0.7);
            margin-top: 8px;
            font-size: 0.95rem;
        }

        .price-box {
            background: linear-gradient(135deg, #f59e0b, #f97316);
            color: white;
            padding: 18px 24px;
            border-radius: 18px;
            min-width: 200px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(249,115,22,0.35);
        }

        .price-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .price {
            font-size: 2rem;
            font-weight: 800;
            margin-top: 6px;
        }

        .chart-wrap {
            position: relative;
            height: 500px;
        }

        .footer {
            margin-top: 18px;
            color: rgba(255,255,255,0.55);
            font-size: 0.9rem;
            text-align: center;
        }

        .loader {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 500px;
            font-size: 1.2rem;
            color: rgba(255,255,255,0.7);
        }

        @media (max-width: 768px) {
            .title {
                font-size: 1.6rem;
            }

            .chart-wrap {
                height: 350px;
            }

            .price {
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="header">
                <div>
                    <h1 class="title">₿ Bitcoin Price Dashboard</h1>
                    <div class="subtitle">
                        Interactive 30-day BTC price chart powered by FastAPI
                    </div>
                </div>

                <div class="price-box">
                    <div class="price-label">Latest BTC Price</div>
                    <div class="price" id="latestPrice">$--</div>
                </div>
            </div>

            <div id="loading" class="loader">
                Loading Bitcoin data...
            </div>

            <div class="chart-wrap">
                <canvas id="btcChart"></canvas>
            </div>

            <div class="footer">
                Data source: CoinGecko API
            </div>
        </div>
    </div>

    <script>
        async function loadChart() {
            const loading = document.getElementById("loading");
            const canvas = document.getElementById("btcChart");

            try {
                const response = await fetch("/api/bitcoin");
                const data = await response.json();

                loading.style.display = "none";

                const labels = data.map(item => item.date);
                const prices = data.map(item => item.price);

                const latest = prices[prices.length - 1];

                document.getElementById("latestPrice").innerText =
                    "$" + latest.toLocaleString();

                const ctx = canvas.getContext("2d");

                const gradient = ctx.createLinearGradient(0, 0, 0, 400);
                gradient.addColorStop(0, "rgba(245, 158, 11, 0.5)");
                gradient.addColorStop(1, "rgba(245, 158, 11, 0.02)");

                new Chart(ctx, {
                    type: "line",
                    data: {
                        labels: labels,
                        datasets: [{
                            label: "BTC Price (USD)",
                            data: prices,
                            borderColor: "#f59e0b",
                            backgroundColor: gradient,
                            fill: true,
                            tension: 0.35,
                            borderWidth: 3,
                            pointRadius: 0,
                            pointHoverRadius: 6,
                            pointHoverBackgroundColor: "#fff",
                            pointHoverBorderColor: "#f59e0b",
                            pointHoverBorderWidth: 3
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {
                            intersect: false,
                            mode: "index"
                        },
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                backgroundColor: "#111827",
                                borderColor: "#374151",
                                borderWidth: 1,
                                padding: 12,
                                titleColor: "#fff",
                                bodyColor: "#fff",
                                displayColors: false,
                                callbacks: {
                                    label: function(context) {
                                        return "$" +
                                            context.parsed.y.toLocaleString();
                                    }
                                }
                            }
                        },
                        scales: {
                            x: {
                                ticks: {
                                    color: "rgba(255,255,255,0.7)"
                                },
                                grid: {
                                    color: "rgba(255,255,255,0.05)"
                                }
                            },
                            y: {
                                ticks: {
                                    color: "rgba(255,255,255,0.7)",
                                    callback: function(value) {
                                        return "$" + value.toLocaleString();
                                    }
                                },
                                grid: {
                                    color: "rgba(255,255,255,0.05)"
                                }
                            }
                        }
                    }
                });

            } catch (err) {
                loading.innerHTML =
                    "Failed to load Bitcoin data.<br><br>" + err;
            }
        }

        loadChart();
    </script>
</body>
</html>
"""


# Run with:
# uvicorn app:app
#
# Install dependencies:
# pip install fastapi uvicorn requests
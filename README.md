
 
# Stock Data API

This API provides access to stock data fetched from Yahoo Finance, along with functionality for generating candlestick charts and calculating Simple Moving Averages (SMA) for stock prices. The API allows users to retrieve stock data, analyze it within a specific date range, and obtain detailed statistics about stock movements.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
  - [1. `/candlestick-chart-tradingview`](#1-candlestick-chart-tradingview)
  - [2. `/sma-report/details`](#2-sma-reportdetails)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Candlestick Chart**: Displays a TradingView candlestick chart for a given stock ticker.
- **Simple Moving Average (SMA)**: Calculates and displays the Simple Moving Average (SMA) for a given stock over a specified period.
- **Statistics**: Provides statistics such as the number of days the stock was above or below the SMA, and how often the stock price crossed the SMA.

---

## Requirements

- Python 3.x
- `Flask`
- `Flask-RESTX`
- `yfinance`
- `pandas`
- `plotly`

Install the required dependencies by running:

```bash
pip install -r requirements.txt
```
**Installation**

# 1.Clone the repository:

```bash
git clone https://github.com/yourusername/stock-data-api.git
cd stock-data-api
```
# Install dependencies:

```bash

pip install -r requirements.txt
```
Run the Flask app:

```bash
python app.py
```
The server will start and be available at http://127.0.0.1:5000/.

**Endpoints**
1. /candlestick-chart-tradingview
Description: This endpoint returns an HTML page with a TradingView candlestick chart for a specific stock ticker.

Method: GET
Query Parameters:
ticker (required): Stock ticker symbol (e.g., "AAPL" for Apple).
Example Request:

```bash
GET http://127.0.0.1:5000/stocks/candlestick-chart-tradingview?ticker=AAPL
```
Example Response:
An HTML page containing a TradingView candlestick chart for the specified stock ticker.

2. /sma-report/details
Description: This endpoint retrieves stock data for a specific ticker and calculates the Simple Moving Average (SMA) for a given period, along with other statistics.

Method: GET
Query Parameters:
ticker (required): Stock ticker symbol (e.g., "AAPL").
sma_period (required): Period for the SMA calculation (e.g., 50 for a 50-day SMA).
start_date (required): Start date for the data range in YYYY-MM-DD format.
end_date (required): End date for the data range in YYYY-MM-DD format.
timeframe (optional): Timeframe for data (default is 1d). Other options include 5d, 1wk, etc.
Example Request:
```bash

GET http://127.0.0.1:5000/stocks/sma-report/details?ticker=AAPL&sma_period=50&start_date=2023-01-01&end_date=2023-12-31
```
Example Response:
json
```bash
{
  "status": "success",
  "details": [
    {
      "date": "2023-01-01",
      "close_price": 150.0,
      "sma": 148.5,
      "difference": 1.5
    },
    ...
  ],
  "statistics": {
    "Above SMA": 120,
    "Below SMA": 80,
    "Crossing Above": 15,
    "Crossing Below": 12
  }
}
```
Contributing
We welcome contributions! If you'd like to contribute, please fork the repository, make your changes, and submit a pull request. Be sure to follow the project's coding style and conventions.

# Steps to contribute:
1.Fork the repository /n
2.Create a new branch for your feature
3.Make your changes
4.Submit a pull request

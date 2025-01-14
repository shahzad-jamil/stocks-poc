import yfinance as yf
from flask_restx import Namespace, Resource, fields,reqparse
import pandas as pd
import logging
import plotly.graph_objects as go
from flask import jsonify,Flask,request

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Define the Namespace
stock_ns = Namespace("stocks", description="Stock Data Operations")

# Service Functions
def get_stock_data(ticker, period="1y", interval="1d"):
    """Fetch historical stock data from Yahoo Finance."""
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
  
    if data.empty:
        raise ValueError("No data found for the given ticker and period.")
    return data.reset_index().to_dict(orient="records")


def generate_candlestick_plot(data):
    """Generate a candlestick plot using Plotly."""
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        increasing_line_color='green', 
        decreasing_line_color='red'
    )])

    # Customize the layout
    fig.update_layout(
        title="Candlestick Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark"
    )
    
    # Convert to HTML to be embedded in the Flask page
    return fig.to_html(full_html=False)

  # Ensure serializable format
def calculate_sma(data, sma_period):
    """Calculate SMA for the given stock data."""
    df = pd.DataFrame(data) 
    df[f"SMA_{sma_period}"] = df["Close"].rolling(window=sma_period).mean()
    return df.reset_index().to_dict(orient="records")

def get_period_details(data, start_date, end_date, sma_period):
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)  
    
    df['SMA'] = df['Close'].rolling(window=sma_period).mean()
    df['Difference'] = df['Close'] - df['SMA']
    
    # Convert start_date and end_date to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Now filter based on the date range
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    print("Filtered Data:", filtered_df)  
    
    if filtered_df.empty:
        raise ValueError("No data found for the given date range.")
    
    return filtered_df[['Date', 'Close', 'SMA', 'Difference']].rename(columns={
        'Date': 'date',
        'Close': 'close_price',
        'SMA': 'sma',
        'Difference': 'difference'
    }).to_dict(orient='records')


def get_period_details(data, start_date, end_date, sma_period):
    df = pd.DataFrame(data)
    
    # Ensure 'Date' column is without timezone
    if 'Date' not in df.columns:
        raise ValueError("Invalid stock data. Missing 'Date' column.")
    
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)  # Remove timezone information
    
    # Calculate SMA and Difference before filtering
    df['SMA'] = df['Close'].rolling(window=sma_period).mean()
    df['Difference'] = df['Close'] - df['SMA']
    
    df = df.dropna(subset=['SMA'])
    # Convert start_date and end_date to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Now filter based on the date range
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    
    # Calculate statistics
    above_sma = sum(filtered_df['Close'] > filtered_df['SMA'])
    below_sma = sum(filtered_df['Close'] < filtered_df['SMA'])
    crossing_above = sum((filtered_df['Close'].shift(1) < filtered_df['SMA'].shift(1)) & (filtered_df['Close'] > filtered_df['SMA']))
    crossing_below = sum((filtered_df['Close'].shift(1) > filtered_df['SMA'].shift(1)) & (filtered_df['Close'] < filtered_df['SMA']))
    
    # Prepare the result
    result = filtered_df[['Date', 'Close', 'SMA', 'Difference']].rename(columns={
        'Date': 'date',
        'Close': 'close_price',
        'SMA': 'sma',
        'Difference': 'difference'
    }).to_dict(orient='records')
    
    # Combine result and statistics into one dictionary
    return {
        "details": result,
        "statistics": {
            "Above SMA": above_sma,
            "Below SMA": below_sma,
            "Crossing Above": crossing_above,
            "Crossing Below": crossing_below
        }
    }


# Define Response Model for SMA Report Details
period_response = stock_ns.model('PeriodDetailsResponse', {
    "status": fields.String(description="Status of the API call"),
    "details": fields.List(fields.Nested(stock_ns.model('PeriodDetail', {
        "date": fields.String(description="Date of the stock data"),
        "close_price": fields.Float(description="Closing price of the stock"),
        "sma": fields.Float(description="Simple Moving Average value"),
        "difference": fields.Float(description="Difference between Close Price and SMA")
    }))),
    "statistics": fields.Nested(stock_ns.model('Statistics', {
        "Above SMA": fields.Integer(description="Count of days above the SMA"),
        "Below SMA": fields.Integer(description="Count of days below the SMA"),
        "Crossing Above": fields.Integer(description="Count of days crossing above the SMA"),
        "Crossing Below": fields.Integer(description="Count of days crossing below the SMA")
    }))
})


@stock_ns.route("/candlestick-chart-tradingview")
class CandlestickChartTradingView(Resource):
    @stock_ns.doc(params={
        "ticker": "Stock ticker symbol",
    })
    def get(self):
        """Return an HTML page with a TradingView candlestick chart."""
        parser = reqparse.RequestParser()
        parser.add_argument('ticker', required=True, type=str)
        args = parser.parse_args()
        ticker = args['ticker']

        # Render an HTML template and pass the ticker
        try:
            return {
                "status": "success",
                "html": f"""
                    <html>
                        <head>
                            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                        </head>
                        <body>
                            <div id="tradingview_chart" style="height: 600px; width: 100%;"></div>
                            <script>
                                new TradingView.widget({{
                                    "symbol": "{ticker}",
                                    "width": "100%",
                                    "height": 600,
                                    "interval": "D",
                                    "timezone": "Etc/UTC",
                                    "theme": "Light",
                                    "style": "1",
                                    "locale": "en",
                                    "toolbar_bg": "#f1f3f6",
                                    "enable_publishing": false,
                                    "withdateranges": true,
                                    "allow_symbol_change": true,
                                    "details": true,
                                    "studies": [],
                                    "container_id": "tradingview_chart"
                                }});
                            </script>
                        </body>
                    </html>
                """
            }, 200
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }, 500


@stock_ns.route("/sma-report/details")
class SMAReportDetails(Resource):
    @stock_ns.doc(params={
        "ticker": "Stock ticker symbol",
        "sma_period": "SMA period",
        "start_date": "Start date of the period (YYYY-MM-DD)",
        "end_date": "End date of the period (YYYY-MM-DD)",
        "timeframe": "Timeframe for data (e.g., 1d, 5d)"
    })
    @stock_ns.marshal_with(period_response)
    def get(self):
        """Get day-by-day stock data for a selected period."""
        parser = reqparse.RequestParser()
        parser.add_argument('ticker', required=True, type=str)
        parser.add_argument('sma_period', required=True, type=int)
        parser.add_argument('start_date', required=True, type=str)
        parser.add_argument('end_date', required=True, type=str)
        parser.add_argument('timeframe', default='1d', type=str)
        
        args = parser.parse_args()
        
        ticker = args['ticker']
        sma_period = args['sma_period']
        start_date = args['start_date']
        end_date = args['end_date']
        timeframe = args['timeframe']
        
        try:
            # Fetch stock data with the correct arguments
            stock_data = get_stock_data(ticker, period="1y", interval=timeframe)
            result = get_period_details(stock_data, start_date, end_date, sma_period)
            
            return {
                "status": "success",
                "details": result['details'],
                "statistics": result['statistics']
            }, 200
        except Exception as e:
            error_message = str(e)
            print(error_message)  
            return {
                "status": "error",
                "message": error_message,
            }, 500



@stock_ns.route("/stocks/Pie-chart")
class StockData(Resource):
    """Get the max and min stock values for the given ticker."""
    
    @stock_ns.doc(params={
        "ticker": "Stock ticker symbol",  
    })
    def get(self):
        """Fetch stock data and return max and min values as JSON."""
        ticker = request.args.get('ticker') 
        if not ticker:
            return {"error": "Ticker symbol is required."}, 400
        
        try:
            # Get today's stock data (list of records)
            stock_data = get_stock_data(ticker, period="1d", interval="1d")
            
            if not stock_data:
                return {"error": "No data available for the provided ticker."}, 404
            
            # Extract max and min values (from the first record)
            today_max = stock_data[0]['High']  
            today_min = stock_data[0]['Low']   
            
            # Return as JSON
            return jsonify({
                'ticker': ticker,
                'max_value': today_max,
                'min_value': today_min
            })
        
        except Exception as e:
            return {"error": str(e)}, 400
        

COMPANIES = [    
        {"name": "Apple Inc.", "ticker": "AAPL"}, 
        {"name": "Microsoft Corp.", "ticker": "MSFT"},
        {"name": "Amazon.com Inc.", "ticker": "AMZN"},
        {"name": "Tesla Inc.", "ticker": "TSLA"},
        {"name": "Alphabet Inc. Class A", "ticker": "GOOGL"},
        {"name": "NVIDIA Corp.", "ticker": "NVDA"},
        {"name": "Meta Platforms Inc.", "ticker": "META"}, 
        {"name": "Johnson & Johnson", "ticker": "JNJ"},
        {"name": "Procter & Gamble Co.", "ticker": "PG"},
    ]

@stock_ns.route("/stocks/market-prices")
class StockMarket(Resource):
    def get(self):
        """
        Fetch market prices and percentage changes for predefined companies.
        """
        stock_data = []
        for company in COMPANIES:
            try:
                ticker = company["ticker"]
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d")  

                if hist.empty:
                    stock_data.append({
                        "name": company["name"],
                        "ticker": ticker,
                        "price": None,
                        "change_percent": None,
                        "error": "No data available"
                    })
                    continue

               
                last_close = hist.iloc[-1]["Close"]
                prev_close = hist.iloc[-2]["Close"] if len(hist) > 1 else last_close
                print(prev_close)
                change_percent = ((last_close - prev_close) / prev_close) * 100

                stock_data.append({
                    "name": company["name"],
                    "ticker": ticker,
                    "price": round(last_close, 2),
                    "change_percent": round(change_percent, 2)
                })
            except Exception as e:
                stock_data.append({
                    "name": company["name"],
                    "ticker": company["ticker"],
                    "error": str(e)
                })

        return {
            "status": "success",
            "data": stock_data
        }, 200
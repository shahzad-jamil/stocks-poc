from flask import Flask, jsonify,render_template
from flask_restx import Api
from app.stocks import stock_ns  # Assuming you have stock_ns defined in app/stocks.py


app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")
api = Api(
    app,
    version="1.0",
    title="Stock SMA API",
    description="API for fetching stock data and calculating SMA reports",
    doc="/docs"  # Swagger UI at `/docs`
)

# Register namespaces
api.add_namespace(stock_ns, path="/stocks")





from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from risk_manager import can_trade, get_trade_size
from bybit_api import place_order

load_dotenv()
app = Flask(__name__)

SECRET_TOKEN = os.getenv("WEBHOOK_SECRET", "supersecreto")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    token = data.get("token")
    if token != SECRET_TOKEN:
        return jsonify({"error": "Token inválido"}), 403

    symbol = data.get("symbol", "BTCUSDT")
    side = data.get("side", "buy")
    leverage = data.get("leverage", 3)

    if not can_trade():
        return jsonify({"error": "Límite de trading alcanzado"}), 403

    qty = get_trade_size(symbol, leverage)

    try:
        order = place_order(symbol, side, qty, leverage)
        return jsonify({"message": "Orden ejecutada", "order": order})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

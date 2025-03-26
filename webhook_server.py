from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from risk_manager import can_trade, get_trade_size
from bybit_api import place_order

load_dotenv()
app = Flask(__name__)

SECRET_TOKEN = os.getenv("WEBHOOK_SECRET", "supersecreto")
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_LEVERAGE = 3

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Intentar interpretar como JSON
        data = request.get_json(silent=True)
        if data and isinstance(data, dict):
            token = data.get("token")
            if token != SECRET_TOKEN:
                return jsonify({"error": "Token inválido"}), 403

            symbol = data.get("symbol", DEFAULT_SYMBOL)
            side = data.get("side", "buy")
            leverage = data.get("leverage", DEFAULT_LEVERAGE)

        else:
            # Interpretar como texto plano
            raw = request.data.decode("utf-8").strip().lower()
            if raw not in ["long", "short"]:
                return jsonify({"error": "Formato de mensaje no válido"}), 400

            print(f"[Webhook plano recibido]: {raw}")
            symbol = DEFAULT_SYMBOL
            side = "buy" if raw == "long" else "sell"
            leverage = DEFAULT_LEVERAGE

        if not can_trade():
            return jsonify({"error": "Límite de trading alcanzado"}), 403

        qty = get_trade_size(symbol, leverage)
        order = place_order(symbol, side, qty, leverage)
        return jsonify({"message": "Orden ejecutada", "order": order})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Validar si se puede tradear
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

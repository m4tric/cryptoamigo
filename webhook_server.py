from flask import Flask, request, jsonify
import os
import traceback
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
        print("📥 Webhook recibido")

        data = request.get_json(silent=True)
        print(f"🧾 JSON parseado: {data}")

        # Intentar interpretar como JSON válido
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
            print(f"📄 Texto plano recibido: {raw}")
            if raw not in ["long", "short"]:
                return jsonify({"error": "Formato de mensaje no válido"}), 400

            symbol = DEFAULT_SYMBOL
            side = "buy" if raw == "long" else "sell"
            leverage = DEFAULT_LEVERAGE

        if not can_trade():
            return jsonify({"error": "Límite de trading alcanzado"}), 403

        qty = get_trade_size(symbol, leverage)
        order = place_order(symbol, side, qty, leverage)
        return jsonify({"message": "Orden ejecutada", "order": order})

    except Exception as e:
        print("❌ Error en ejecución:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

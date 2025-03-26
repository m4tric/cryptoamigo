import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from utils import log_event, validate_payload
from bybit_api import place_order, set_leverage
from risk_manager import load_config, calculate_qty, can_trade, update_state

load_dotenv()
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    log_event("📥 Incoming request")

    if not request.is_json:
        log_event("⚠️ Request is not JSON")
        return jsonify({"error": "Request must be JSON"}), 400

    try:
        raw_data = request.data.decode("utf-8")
        log_event(f"📦 Raw body: {raw_data}")
        data = request.get_json(force=True)
        log_event(f"✅ Parsed JSON: {data}")
    except Exception as e:
        log_event(f"❌ JSON parsing error: {str(e)}")
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400

    log_event(f"🖱️ SIGNAL RECEIVED: {data}")

    missing = validate_payload(data)
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Aquí seguiría la lógica del bot: cálculo de qty, envío de orden, etc.
    # Por ahora solo confirmamos recepción:
    return jsonify({"status": "Webhook received"}), 200

    log_event(f"📡 SIGNAL RECEIVED: {data}")

    missing = validate_payload(data)
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if not can_trade():
        return jsonify({"error": "Daily trading limit reached"}), 403

    try:
        symbol = data["symbol"]
        side = data["side"]
        leverage = data["leverage"]
        sl_percent = 1.0  # Puedes hacerlo variable si lo deseas
        tp = data["tp"]
        sl = data["sl"]
        entry_price = data.get("entry_price")

        if not entry_price:
            return jsonify({"error": "Missing entry_price for risk calculation"}), 400

        config = load_config()
        qty = calculate_qty(entry_price, config["capital_usdt"], config["risk_percent"], sl_percent)

        set_leverage(symbol, leverage)
        result = place_order(symbol, side, qty, sl, tp)

        update_state(profit_loss=0)

        return jsonify(result)
    except Exception as e:
        log_event(f"❌ ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    log_event("🚀 BOT STARTED (Risk Managed Version)")
    app.run(host="0.0.0.0", port=port)

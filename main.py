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
        log_event(f"❗ Missing fields: {missing}")
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if not can_trade():
        log_event("🚫 Daily trading limit reached")
        return jsonify({"error": "Daily trading limit reached"}), 403

    try:
        symbol = data["symbol"]
        side = data["side"]
        leverage = data["leverage"]
        sl = data["sl"]
        tp = data["tp"]
        entry_price = data["entry_price"]

        config = load_config()
        sl_percent = 1.0  # Fijo por ahora, se puede parametrizar
        qty = calculate_qty(entry_price, config["capital_usdt"], config["risk_percent"], sl_percent)

        log_event(f"📐 Calculated qty: {qty}")
        log_event(f"📊 Setting leverage: {leverage}")
        set_leverage(symbol, leverage)

        log_event("🚀 Sending order...")
        result = place_order(symbol, side, qty, sl, tp)
        log_event(f"📥 BYBIT RESPONSE: {result}")

        update_state(profit_loss=0)

        log_event(f"✅ ORDER EXECUTED SUCCESSFULLY")
        return jsonify(result)
    except Exception as e:
        log_event(f"❌ ERROR DURING ORDER EXECUTION: {str(e)}")
        return jsonify({"error": f"Internal bot error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    log_event("🚀 BOT STARTED (Debug Mode)")
    app.run(host="0.0.0.0", port=port)

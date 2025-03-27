import os
import sys
import time
import hmac
import hashlib
import json
import requests
from utils import log_event

# Leer claves API
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")

# Validar claves
if not API_KEY or not API_SECRET:
    log_event("❌ ERROR: API_KEY o API_SECRET no están definidas en las variables de entorno.")
    sys.exit("Faltan las claves API. Verifica tus variables en Render.")

BASE_URL = "https://api.bybit.com"

def _get_headers(query_string="", body_str=""):
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    if body_str:
        sign_payload = timestamp + API_KEY + recv_window + body_str
    else:
        sign_payload = timestamp + API_KEY + recv_window + query_string
    signature = hmac.new(
        bytes(API_SECRET, "utf-8"),
        sign_payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "X-BAPI-SIGN": signature,
        "Content-Type": "application/json"
    }

def set_leverage(symbol, leverage):
    endpoint = "/v5/position/set-leverage"
    url = BASE_URL + endpoint
    body = {
        "category": "linear",
        "symbol": symbol,
        "buyLeverage": str(leverage),
        "sellLeverage": str(leverage)
    }
    body_str = json.dumps(body, separators=(',', ':'))
    headers = _get_headers(body_str=body_str)
    response = requests.post(url, headers=headers, data=body_str)
    log_event(f"📈 set leverage response: {response.text}")
    return response.json()

def place_order(symbol, side, qty, entry_price, sl=None, tp=None):
    # Si la señal incluye qty_override, usar ese valor manualmente
    try:
        qty_override = float(os.getenv("QTY_OVERRIDE", "0"))
        if qty_override > 0:
            log_event(f"🚨 OVERRIDE: usando qty fija: {qty_override}")
            qty = qty_override
    except Exception as e:
        log_event(f"❌ Error al interpretar QTY_OVERRIDE: {str(e)}")

    log_event(f"📊 QTY CALCULADA: {qty}")

    endpoint = "/v5/order/create"
    url = BASE_URL + endpoint

    body = {
        "category": "linear",
        "symbol": symbol,
        "side": side.capitalize(),  # "Buy" o "Sell"
        "orderType": "Market",
        "qty": str(qty),
        "timeInForce": "GTC"
    }

    if tp is not None:
        tp_price = round(entry_price * (1 + tp / 100), 5) if side.lower() == "buy" else round(entry_price * (1 - tp / 100), 5)
        body["takeProfit"] = str(tp_price)
        log_event(f"🎯 Take Profit calculado: {tp_price}")

    if sl is not None:
        sl_price = round(entry_price * (1 - sl / 100), 5) if side.lower() == "buy" else round(entry_price * (1 + sl / 100), 5)
        body["stopLoss"] = str(sl_price)
        log_event(f"🛡️ Stop Loss calculado: {sl_price}")

    body_str = json.dumps(body, separators=(',', ':'))
    headers = _get_headers(body_str=body_str)

    print("📤 Enviando orden a Bybit:")
    print(json.dumps(body, indent=2))

    response = requests.post(url, headers=headers, data=body_str)

    print(f"📥 Código de respuesta: {response.status_code}")
    print("🧾 Respuesta cruda:", response.text)

    try:
        return response.json()
    except ValueError:
        print("❌ Error al parsear respuesta JSON de Bybit.")
        return {
            "error": "Respuesta no válida de Bybit",
            "raw": response.text
        }

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
    log_event(f"📈 SET LEVERAGE RESPONSE: {response.text}")
    return response.json()

def place_order(symbol, side, qty, sl, tp):
    endpoint = "/v5/order/create"
    url = BASE_URL + endpoint
    body = {
        "category": "linear",
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": str(qty),
        "timeInForce": "GoodTillCancel",
        "takeProfit": str(tp),
        "stopLoss": str(sl),
        "positionIdx": 0
    }
    body_str = json.dumps(body, separators=(',', ':'))
    headers = _get_headers(body_str=body_str)
    response = requests.post(url, headers=headers, data=body_str)
    log_event(f"📤 ORDER SENT: {body_str}")
    log_event(f"📥 BYBIT RESPONSE: {response.text}")
    return response.json()

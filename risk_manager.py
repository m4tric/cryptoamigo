import json
import os
import traceback
from utils import log_event

CONFIG_FILE = "config.json"
STATE_FILE = "state.json"

def load_config():
    try:
        print(f"🗂 Ruta actual: {os.getcwd()}")
        print(f"📄 Verificando existencia de config.json: {os.path.isfile(CONFIG_FILE)}")
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        print(f"✅ Config cargado: {config}")
        return config
    except Exception as e:
        print("❌ Error al cargar config.json:")
        traceback.print_exc()
        raise

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"trades_today": 0, "daily_loss": 0}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def calculate_qty(entry_price, capital, risk_percent, sl_percent):
    risk_amount = (risk_percent / 100) * capital
    sl_amount_per_unit = entry_price * (sl_percent / 100)
    qty = risk_amount / sl_amount_per_unit
    return round(qty, 3)

def get_trade_size(symbol, leverage):
    config = load_config()
    capital = config.get("capital_usdt", 20)
    risk_percent = config.get("risk_percent", 5)

    # Precio estimado temporal para simulación (hasta tener price real)
    price = 100

    qty = calculate_qty(entry_price=price, capital=capital, risk_percent=risk_percent, sl_percent=1)
    return round(qty * leverage, 3)

def can_trade():
    config = load_config()
    state = load_state()
    if state["trades_today"] >= config["max_trades_per_day"]:
        log_event("❌ Límite de operaciones diarias alcanzado.")
        return False
    if state["daily_loss"] >= config["max_daily_loss_usdt"]:
        log_event("❌ Límite de pérdida diaria alcanzado.")
        return False
    return True

def update_state(profit_loss):
    state = load_state()
    state["trades_today"] += 1
    if profit_loss < 0:
        state["daily_loss"] += abs(profit_loss)
    save_state(state)

def reset_daily_state():
    save_state({"trades_today": 0, "daily_loss": 0})

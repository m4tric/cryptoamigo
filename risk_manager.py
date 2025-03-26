import json
from utils import log_event

CONFIG_FILE = "config.json"
STATE_FILE = "state.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

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

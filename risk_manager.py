import json
import os

class RiskManager:
    def __init__(self, max_daily_loss, max_trades, state_file='risk_state.json'):
        self.max_daily_loss = max_daily_loss
        self.max_trades = max_trades
        self.state_file = state_file
        self.daily_loss = 0
        self.daily_trades = 0
        self.load_state()

    def can_trade(self):
        return (self.daily_loss < self.max_daily_loss and 
                self.daily_trades < self.max_trades)

    def register_trade(self, profit_loss):
        self.daily_loss += abs(min(0, profit_loss))
        self.daily_trades += 1
        self.save_state()

    def save_state(self):
        state = {
            'daily_loss': self.daily_loss,
            'daily_trades': self.daily_trades
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f)

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                self.daily_loss = state.get('daily_loss', 0)
                self.daily_trades = state.get('daily_trades', 0)
        else:
            self.daily_loss = 0
            self.daily_trades = 0

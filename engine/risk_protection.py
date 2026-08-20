"""
Aegis AI
Module: Risk Protection
Version: 0.2.0

Pre-entry account protection. This module does not close or modify
existing positions; it only decides whether a NEW trade may be opened.
"""

import json
import os
from datetime import datetime, date

import MetaTrader5 as mt5

from engine.config import (
    SYMBOL,
    MAGIC_NUMBER,
    ACCOUNT_BALANCE,
    RISK_PERCENT,
)
from engine.database import Database


class RiskProtection:

    def __init__(self):
        self.db = Database()
        self.state_file = os.path.join("data", "risk_state.json")

        self.max_daily_loss_percent = 3.0
        self.max_drawdown_percent = 5.0
        self.max_open_risk_percent = 2.0
        self.max_open_trades = 1

        self._ensure_state_dir()

    # =====================================================
    # STATE STORAGE
    # =====================================================

    def _ensure_state_dir(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)

    def _load_state(self):
        if not os.path.exists(self.state_file):
            return {}

        try:
            with open(self.state_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _save_state(self, state):
        try:
            with open(self.state_file, "w", encoding="utf-8") as file:
                json.dump(state, file, indent=2)
        except OSError as exc:
            print(f"⚠ Risk state save failed: {exc}")

    def _refresh_day_state(self, account):
        state = self._load_state()
        today = date.today().isoformat()

        if state.get("day") != today:
            state["day"] = today
            state["day_start_balance"] = float(account.balance)
            state["peak_equity"] = float(account.equity)
            self._save_state(state)

        peak_equity = float(state.get("peak_equity", account.equity))
        if account.equity > peak_equity:
            state["peak_equity"] = float(account.equity)
            self._save_state(state)

        return state

    # =====================================================
    # MT5
    # =====================================================

    def _account(self):
        return mt5.account_info()

    def _positions(self):
        positions = mt5.positions_get(symbol=SYMBOL)
        if positions is None:
            return []
        return [p for p in positions if p.magic == MAGIC_NUMBER]

    # =====================================================
    # DAILY REALIZED P/L
    # =====================================================

    def daily_closed_profit(self):
        total = 0.0
        for trade in self.db.get_trades():
            if trade[9] != "CLOSED" or not trade[12]:
                continue

            try:
                closed_at = datetime.fromisoformat(str(trade[12]))
            except ValueError:
                continue

            if closed_at.date() == date.today():
                total += float(trade[10] or 0.0)

        return total

    # =====================================================
    # FLOATING P/L
    # =====================================================

    def floating_profit(self):
        return sum(float(p.profit) for p in self._positions())

    # =====================================================
    # OPEN RISK
    # =====================================================

    def position_risk(self, position):
        entry = float(position.price_open)
        sl = float(position.sl)

        if sl <= 0:
            return 0.0

        info = mt5.symbol_info(position.symbol)
        if info is None:
            return 0.0

        tick_size = float(info.trade_tick_size)
        tick_value = float(info.trade_tick_value)

        if tick_size <= 0 or tick_value <= 0:
            return 0.0

        ticks = abs(entry - sl) / tick_size
        return ticks * tick_value * float(position.volume)

    def total_open_risk(self):
        return sum(self.position_risk(p) for p in self._positions())

    # =====================================================
    # CHECK
    # =====================================================

    def check(self):
        account = self._account()
        if account is None:
            return {
                "approved": False,
                "checks": ["❌ MT5 account information unavailable."],
            }

        state = self._refresh_day_state(account)
        balance = float(account.balance)
        equity = float(account.equity)
        day_start_balance = float(state.get("day_start_balance", balance))
        peak_equity = float(state.get("peak_equity", equity))

        closed_profit = self.daily_closed_profit()
        floating = self.floating_profit()
        daily_pnl = closed_profit + floating

        daily_loss_limit = day_start_balance * (
            self.max_daily_loss_percent / 100.0
        )

        current_drawdown = max(
            0.0,
            peak_equity - equity,
        )
        drawdown_limit = peak_equity * (
            self.max_drawdown_percent / 100.0
        )

        configured_risk_limit = balance * (
            self.max_open_risk_percent / 100.0
        )
        open_risk = self.total_open_risk()
        open_positions = len(self._positions())

        approved = True
        checks = []

        if daily_pnl <= -daily_loss_limit:
            checks.append(
                f"❌ Daily loss limit reached: {daily_pnl:.2f}"
            )
            approved = False
        else:
            checks.append(
                f"✅ Daily P/L within limit: {daily_pnl:.2f}"
            )

        if current_drawdown >= drawdown_limit:
            checks.append(
                f"❌ Maximum drawdown reached: {current_drawdown:.2f}"
            )
            approved = False
        else:
            checks.append(
                f"✅ Drawdown within limit: {current_drawdown:.2f}"
            )

        if open_risk >= configured_risk_limit:
            checks.append(
                f"❌ Open risk limit reached: {open_risk:.2f}"
            )
            approved = False
        else:
            checks.append(
                f"✅ Open risk within limit: {open_risk:.2f}"
            )

        if open_positions >= self.max_open_trades:
            checks.append(
                f"❌ Maximum open positions reached: {open_positions}"
            )
            approved = False
        else:
            checks.append(
                f"✅ Open positions: {open_positions}"
            )

        return {
            "approved": approved,
            "checks": checks,
            "balance": balance,
            "equity": equity,
            "daily_pnl": daily_pnl,
            "daily_loss_limit": daily_loss_limit,
            "drawdown": current_drawdown,
            "drawdown_limit": drawdown_limit,
            "open_risk": open_risk,
            "open_risk_limit": configured_risk_limit,
            "open_positions": open_positions,
        }

    # =====================================================
    # REPORT
    # =====================================================

    def print_report(self):
        result = self.check()

        print("\n========== ACCOUNT PROTECTION ==========")
        for check in result["checks"]:
            print(check)
        print(f"Balance       : {result.get('balance')}")
        print(f"Equity        : {result.get('equity')}")
        print(f"Daily P/L     : {result.get('daily_pnl')}")
        print(f"Open Risk     : {result.get('open_risk')}")
        print(f"Protection    : {'APPROVED' if result['approved'] else 'BLOCKED'}")

        return result
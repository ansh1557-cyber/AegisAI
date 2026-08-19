"""
Aegis AI
Module: Risk & Protection Monitor
Version: 0.1.0
"""

from datetime import datetime

import MetaTrader5 as mt5

from engine.config import (
    SYMBOL,
    MAGIC_NUMBER,
    ACCOUNT_BALANCE,
    RISK_PERCENT,
)


class RiskProtection:

    def __init__(self):
        self.account_balance_config = ACCOUNT_BALANCE
        self.risk_percent = RISK_PERCENT

    # =====================================================
    # OPEN POSITIONS
    # =====================================================

    def get_open_positions(self):

        positions = mt5.positions_get(symbol=SYMBOL)

        if positions is None:
            return []

        return [
            position
            for position in positions
            if position.magic == MAGIC_NUMBER
        ]

    # =====================================================
    # ACCOUNT
    # =====================================================

    def get_account_info(self):

        account = mt5.account_info()

        if account is None:
            return None

        return account

    # =====================================================
    # CURRENT EQUITY
    # =====================================================

    def get_equity(self):

        account = self.get_account_info()

        if account is None:
            return None

        return float(account.equity)

    # =====================================================
    # BALANCE
    # =====================================================

    def get_balance(self):

        account = self.get_account_info()

        if account is None:
            return None

        return float(account.balance)

    # =====================================================
    # FLOATING PROFIT
    # =====================================================

    def get_floating_profit(self):

        positions = self.get_open_positions()

        return sum(
            float(position.profit)
            for position in positions
        )

    # =====================================================
    # OPEN EXPOSURE
    # =====================================================

    def get_open_exposure(self):

        positions = self.get_open_positions()

        exposure = 0.0

        for position in positions:

            tick = mt5.symbol_info_tick(
                position.symbol
            )

            if tick is None:
                continue

            if position.type == mt5.ORDER_TYPE_BUY:
                price = tick.bid
            else:
                price = tick.ask

            exposure += (
                float(position.volume)
                * float(price)
            )

        return exposure

    # =====================================================
    # OPEN TRADE COUNT
    # =====================================================

    def get_open_trade_count(self):

        return len(
            self.get_open_positions()
        )

    # =====================================================
    # RISK PER POSITION
    # =====================================================

    def get_position_risk(self, position):

        entry = float(position.price_open)
        sl = float(position.sl)

        if sl <= 0:
            return 0.0

        price_distance = abs(
            entry - sl
        )

        symbol_info = mt5.symbol_info(
            position.symbol
        )

        if symbol_info is None:
            return 0.0

        tick_size = float(
            symbol_info.trade_tick_size
        )

        tick_value = float(
            symbol_info.trade_tick_value
        )

        if tick_size <= 0 or tick_value <= 0:
            return 0.0

        ticks = (
            price_distance
            / tick_size
        )

        return ticks * tick_value * float(
            position.volume
        )

    # =====================================================
    # TOTAL OPEN RISK
    # =====================================================

    def get_total_open_risk(self):

        positions = self.get_open_positions()

        return sum(
            self.get_position_risk(position)
            for position in positions
        )

    # =====================================================
    # CONFIGURED RISK LIMIT
    # =====================================================

    def get_configured_risk_limit(self):

        return (
            self.account_balance_config
            * (self.risk_percent / 100)
        )

    # =====================================================
    # RISK STATUS
    # =====================================================

    def get_risk_status(self):

        open_positions = self.get_open_positions()

        total_risk = self.get_total_open_risk()
        configured_limit = (
            self.get_configured_risk_limit()
        )

        risk_usage_percent = 0.0

        if configured_limit > 0:
            risk_usage_percent = (
                total_risk
                / configured_limit
            ) * 100

        return {
            "open_trades": len(
                open_positions
            ),
            "total_open_risk": round(
                total_risk,
                2
            ),
            "configured_risk_limit": round(
                configured_limit,
                2
            ),
            "risk_usage_percent": round(
                risk_usage_percent,
                2
            ),
            "risk_limit_exceeded": (
                total_risk
                > configured_limit
            ),
        }

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        balance = self.get_balance()
        equity = self.get_equity()

        return {
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
            "balance": (
                round(balance, 2)
                if balance is not None
                else None
            ),
            "equity": (
                round(equity, 2)
                if equity is not None
                else None
            ),
            "floating_profit": round(
                self.get_floating_profit(),
                2
            ),
            "open_exposure": round(
                self.get_open_exposure(),
                2
            ),
            **self.get_risk_status(),
        }

    # =====================================================
    # PRINT REPORT
    # =====================================================

    def print_report(self):

        data = self.summary()

        print("\n========================================")
        print("         AEGIS AI RISK MONITOR")
        print("========================================")

        print(
            f"Time               : "
            f"{data['timestamp']}"
        )

        print(
            f"Balance            : "
            f"{data['balance']}"
        )

        print(
            f"Equity             : "
            f"{data['equity']}"
        )

        print(
            f"Floating P/L       : "
            f"{data['floating_profit']}"
        )

        print(
            f"Open Exposure      : "
            f"{data['open_exposure']}"
        )

        print(
            f"Open Trades        : "
            f"{data['open_trades']}"
        )

        print(
            f"Open Risk          : "
            f"{data['total_open_risk']}"
        )

        print(
            f"Configured Risk    : "
            f"{data['configured_risk_limit']}"
        )

        print(
            f"Risk Usage         : "
            f"{data['risk_usage_percent']}%"
        )

        print(
            f"Risk Limit Exceeded: "
            f"{data['risk_limit_exceeded']}"
        )

        print("========================================\n")
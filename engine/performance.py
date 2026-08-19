"""
Aegis AI
Module: Performance Analytics
Version: 0.2.0
"""

from dataclasses import dataclass
from statistics import mean

from engine.database import Database


@dataclass
class TradeRecord:
    trade_id: int
    ticket: int
    symbol: str
    signal: str
    volume: float
    entry: float
    stop_loss: float
    take_profit: float
    confidence: int
    status: str
    profit: float
    open_time: str
    close_time: str | None


class PerformanceAnalytics:

    def __init__(self):
        self.db = Database()

    # =====================================================
    # CONVERT DATABASE ROW
    # =====================================================

    @staticmethod
    def _to_trade(row):
        """
        Convert the database tuple into a named TradeRecord.
        """

        if row is None:
            return None

        return TradeRecord(
            trade_id=row[0],
            ticket=row[1],
            symbol=row[2],
            signal=row[3],
            volume=float(row[4] or 0),
            entry=float(row[5] or 0),
            stop_loss=float(row[6] or 0),
            take_profit=float(row[7] or 0),
            confidence=int(row[8] or 0),
            status=row[9],
            profit=float(row[10] or 0),
            open_time=row[11],
            close_time=row[12],
        )

    # =====================================================
    # ALL TRADES
    # =====================================================

    def get_all_trades(self):

        rows = self.db.get_trades()

        return [
            self._to_trade(row)
            for row in rows
        ]

    # =====================================================
    # CLOSED TRADES
    # =====================================================

    def get_closed_trades(self):

        return [
            trade
            for trade in self.get_all_trades()
            if trade.status == "CLOSED"
        ]

    # =====================================================
    # OPEN TRADES
    # =====================================================

    def get_open_trades(self):

        return [
            trade
            for trade in self.get_all_trades()
            if trade.status == "OPEN"
        ]

    # =====================================================
    # BASIC COUNTS
    # =====================================================

    def total_trades(self):
        return len(self.get_all_trades())

    def total_closed(self):
        return len(self.get_closed_trades())

    def total_open(self):
        return len(self.get_open_trades())

    # =====================================================
    # WIN / LOSS
    # =====================================================

    def winning_trades(self):

        return [
            trade
            for trade in self.get_closed_trades()
            if trade.profit > 0
        ]

    def losing_trades(self):

        return [
            trade
            for trade in self.get_closed_trades()
            if trade.profit < 0
        ]

    def breakeven_trades(self):

        return [
            trade
            for trade in self.get_closed_trades()
            if trade.profit == 0
        ]

    # =====================================================
    # WIN RATE
    # =====================================================

    def win_rate(self):

        closed = self.total_closed()

        if closed == 0:
            return 0.0

        return (
            len(self.winning_trades())
            / closed
        ) * 100

    # =====================================================
    # PROFIT
    # =====================================================

    def total_profit(self):

        return sum(
            trade.profit
            for trade in self.get_closed_trades()
        )

    def average_profit(self):

        profits = [
            trade.profit
            for trade in self.get_closed_trades()
        ]

        if not profits:
            return 0.0

        return mean(profits)

    def average_win(self):

        profits = [
            trade.profit
            for trade in self.winning_trades()
        ]

        if not profits:
            return 0.0

        return mean(profits)

    def average_loss(self):

        profits = [
            trade.profit
            for trade in self.losing_trades()
        ]

        if not profits:
            return 0.0

        return mean(profits)

    # =====================================================
    # PROFIT FACTOR
    # =====================================================

    def profit_factor(self):

        gross_profit = sum(
            trade.profit
            for trade in self.winning_trades()
        )

        gross_loss = abs(
            sum(
                trade.profit
                for trade in self.losing_trades()
            )
        )

        if gross_loss == 0:
            if gross_profit > 0:
                return float("inf")

            return 0.0

        return gross_profit / gross_loss

    # =====================================================
    # BEST / WORST
    # =====================================================

    def best_trade(self):

        trades = self.get_closed_trades()

        if not trades:
            return None

        return max(
            trades,
            key=lambda trade: trade.profit
        )

    def worst_trade(self):

        trades = self.get_closed_trades()

        if not trades:
            return None

        return min(
            trades,
            key=lambda trade: trade.profit
        )

    # =====================================================
    # EQUITY CURVE
    # =====================================================

    def get_equity_curve(self):

        """
        Returns cumulative realized profit.

        Example:
        profits = [10, -5, 20]

        result:
        [
            {"trade": 1, "profit": 10, "equity": 10},
            {"trade": 2, "profit": -5, "equity": 5},
            {"trade": 3, "profit": 20, "equity": 25},
        ]
        """

        trades = [
            trade
            for trade in self.get_closed_trades()
            if trade.close_time
        ]

        # Oldest → newest.
        trades.sort(
            key=lambda trade: trade.close_time
        )

        equity = 0.0
        curve = []

        for index, trade in enumerate(
            trades,
            start=1
        ):

            equity += trade.profit

            curve.append(
                {
                    "trade": index,
                    "ticket": trade.ticket,
                    "close_time": trade.close_time,
                    "profit": trade.profit,
                    "equity": round(equity, 2),
                }
            )

        return curve

    # =====================================================
    # DRAWDOWN
    # =====================================================

    def get_drawdown(self):

        curve = self.get_equity_curve()

        peak = 0.0
        result = []

        for point in curve:

            equity = point["equity"]

            peak = max(
                peak,
                equity
            )

            drawdown = equity - peak

            drawdown_percent = (
                (drawdown / peak) * 100
                if peak > 0
                else 0.0
            )

            result.append(
                {
                    **point,
                    "peak": round(peak, 2),
                    "drawdown": round(
                        drawdown,
                        2
                    ),
                    "drawdown_percent": round(
                        drawdown_percent,
                        2
                    ),
                }
            )

        return result

    # =====================================================
    # MAX DRAWDOWN
    # =====================================================

    def max_drawdown(self):

        drawdown = self.get_drawdown()

        if not drawdown:
            return {
                "amount": 0.0,
                "percent": 0.0,
            }

        worst = min(
            drawdown,
            key=lambda item: item["drawdown"]
        )

        return {
            "amount": abs(
                worst["drawdown"]
            ),
            "percent": abs(
                worst["drawdown_percent"]
            ),
        }

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        profit_factor = self.profit_factor()
        max_dd = self.max_drawdown()

        return {
            "total_trades": self.total_trades(),
            "open_trades": self.total_open(),
            "closed_trades": self.total_closed(),
            "winning_trades": len(
                self.winning_trades()
            ),
            "losing_trades": len(
                self.losing_trades()
            ),
            "breakeven_trades": len(
                self.breakeven_trades()
            ),
            "win_rate": round(
                self.win_rate(),
                2
            ),
            "total_profit": round(
                self.total_profit(),
                2
            ),
            "average_profit": round(
                self.average_profit(),
                2
            ),
            "average_win": round(
                self.average_win(),
                2
            ),
            "average_loss": round(
                self.average_loss(),
                2
            ),
            "profit_factor": (
                "INF"
                if profit_factor == float("inf")
                else round(
                    profit_factor,
                    2
                )
            ),
            "max_drawdown": round(
                max_dd["amount"],
                2
            ),
            "max_drawdown_percent": round(
                max_dd["percent"],
                2
            ),
        }

    # =====================================================
    # PRINT REPORT
    # =====================================================

    def print_report(self):

        data = self.summary()

        print(
            "\n========================================"
        )
        print(
            "       AEGIS AI PERFORMANCE REPORT"
        )
        print(
            "========================================"
        )

        print(
            f"Total Trades      : "
            f"{data['total_trades']}"
        )

        print(
            f"Open Trades       : "
            f"{data['open_trades']}"
        )

        print(
            f"Closed Trades     : "
            f"{data['closed_trades']}"
        )

        print(
            f"Winning Trades    : "
            f"{data['winning_trades']}"
        )

        print(
            f"Losing Trades     : "
            f"{data['losing_trades']}"
        )

        print(
            f"Break-even Trades : "
            f"{data['breakeven_trades']}"
        )

        print(
            f"Win Rate          : "
            f"{data['win_rate']}%"
        )

        print(
            f"Total Profit      : "
            f"{data['total_profit']}"
        )

        print(
            f"Average Profit    : "
            f"{data['average_profit']}"
        )

        print(
            f"Average Win       : "
            f"{data['average_win']}"
        )

        print(
            f"Average Loss      : "
            f"{data['average_loss']}"
        )

        print(
            f"Profit Factor     : "
            f"{data['profit_factor']}"
        )

        print(
            f"Max Drawdown      : "
            f"{data['max_drawdown']}"
        )

        print(
            f"Max Drawdown %    : "
            f"{data['max_drawdown_percent']}%"
        )

        print(
            "========================================\n"
        )
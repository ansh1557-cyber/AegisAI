"""
Aegis AI
Dashboard v0.6.2

Read-only local dashboard.
MT5 history is the primary performance source when MT5 is available.
SQLite database is used as a fallback for historical records.
Live open-position P/L is read directly from MT5.
No order placement/modification is exposed by this application.
"""

from __future__ import annotations

import json
import sqlite3
from collections import OrderedDict
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

try:
    import MetaTrader5 as mt5
except Exception:  # pragma: no cover
    mt5 = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "aegis.db"
HOST = "127.0.0.1"
PORT = 8765
REFRESH_SECONDS = 5

try:
    from engine.config import MAGIC_NUMBER, SYMBOL
except Exception:
    MAGIC_NUMBER = 20260726
    SYMBOL = "XAUUSD"


def _connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _query_trades():
    if not DB_PATH.exists():
        return []
    conn = _connect_db()
    try:
        rows = conn.execute(
            """
            SELECT id, ticket, symbol, signal, volume, entry,
                   stop_loss, take_profit, confidence, status,
                   profit, open_time, close_time
            FROM trades
            ORDER BY id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def _mt5_connected():
    if mt5 is None:
        return False
    try:
        return mt5.account_info() is not None
    except Exception:
        return False


def _ensure_mt5():
    if mt5 is None:
        return False
    if _mt5_connected():
        return True
    try:
        return bool(mt5.initialize())
    except Exception:
        return False


def _mt5_history(days=3650):
    """
    Build position-level historical records from MT5 deals.

    MT5 is the primary source here, so the dashboard can show historical
    trades even when the local SQLite DB is empty or incomplete.

    A position can have multiple exit deals (partial close + final close).
    Those exit deals are aggregated by position_id.
    """
    if not _ensure_mt5():
        return []

    date_to = datetime.now()
    date_from = date_to - timedelta(days=days)

    try:
        deals = mt5.history_deals_get(date_from, date_to)
    except Exception:
        return []

    if deals is None:
        return []

    grouped = OrderedDict()

    for deal in deals:
        try:
            magic = int(getattr(deal, "magic", 0))
            position_id = int(getattr(deal, "position_id", 0))
        except Exception:
            continue

        if magic != int(MAGIC_NUMBER) or position_id <= 0:
            continue

        bucket = grouped.setdefault(
            position_id,
            {
                "position_id": position_id,
                "symbol": str(getattr(deal, "symbol", SYMBOL)),
                "type": None,
                "volume_in": 0.0,
                "volume_out": 0.0,
                "entry_price_sum": 0.0,
                "entry_volume_weight": 0.0,
                "first_time": None,
                "last_time": None,
                "profit": 0.0,
                "swap": 0.0,
                "commission": 0.0,
                "closed": False,
            },
        )

        deal_time = int(getattr(deal, "time", 0) or 0)
        if bucket["first_time"] is None or deal_time < bucket["first_time"]:
            bucket["first_time"] = deal_time
        if bucket["last_time"] is None or deal_time > bucket["last_time"]:
            bucket["last_time"] = deal_time

        entry = int(getattr(deal, "entry", -1))

        # IN / INOUT deals establish the position.
        if entry in (
            getattr(mt5, "DEAL_ENTRY_IN", 0),
            getattr(mt5, "DEAL_ENTRY_INOUT", 2),
        ):
            volume = _safe_float(getattr(deal, "volume", 0))
            price = _safe_float(getattr(deal, "price", 0))
            bucket["volume_in"] += volume
            bucket["entry_price_sum"] += price * volume
            bucket["entry_volume_weight"] += volume

            deal_type = int(getattr(deal, "type", -1))
            if deal_type == getattr(mt5, "DEAL_TYPE_BUY", 0):
                bucket["type"] = "BUY"
            elif deal_type == getattr(mt5, "DEAL_TYPE_SELL", 1):
                bucket["type"] = "SELL"

        # OUT / OUT_BY deals close some/all of the position.
        if entry in (
            getattr(mt5, "DEAL_ENTRY_OUT", 1),
            getattr(mt5, "DEAL_ENTRY_OUT_BY", 3),
        ):
            bucket["volume_out"] += _safe_float(
                getattr(deal, "volume", 0)
            )
            bucket["profit"] += _safe_float(
                getattr(deal, "profit", 0)
            )
            bucket["swap"] += _safe_float(
                getattr(deal, "swap", 0)
            )
            bucket["commission"] += _safe_float(
                getattr(deal, "commission", 0)
            )

    result = []

    for position_id, bucket in grouped.items():
        volume_in = bucket["volume_in"]
        volume_out = bucket["volume_out"]

        # A complete historical trade has all opened volume closed.
        # Small floating-point tolerance prevents false "open" states.
        closed = (
            volume_in > 0
            and volume_out >= volume_in - 1e-9
        )

        total_profit = (
            bucket["profit"]
            + bucket["swap"]
            + bucket["commission"]
        )

        entry_price = (
            bucket["entry_price_sum"]
            / bucket["entry_volume_weight"]
            if bucket["entry_volume_weight"] > 0
            else 0.0
        )

        open_time = (
            datetime.fromtimestamp(bucket["first_time"]).isoformat(sep=" ")
            if bucket["first_time"]
            else None
        )
        close_time = (
            datetime.fromtimestamp(bucket["last_time"]).isoformat(sep=" ")
            if bucket["last_time"] and closed
            else None
        )

        result.append(
            {
                "id": position_id,
                "ticket": position_id,
                "symbol": bucket["symbol"],
                "signal": bucket["type"] or "UNKNOWN",
                "volume": round(volume_in, 8),
                "entry": round(entry_price, 5),
                "stop_loss": None,
                "take_profit": None,
                "confidence": None,
                "status": "CLOSED" if closed else "OPEN",
                "profit": round(total_profit, 2),
                "open_time": open_time,
                "close_time": close_time,
                "source": "MT5",
                "partial_close": (
                    closed
                    and volume_out > 0
                    and volume_out < volume_in
                ),
            }
        )

    result.sort(
        key=lambda x: x.get("open_time") or ""
    )
    return result


def _history_source():
    """
    Prefer MT5 history. If unavailable, use the existing SQLite history.
    """
    mt5_history = _mt5_history()
    if mt5_history:
        return mt5_history, "MT5"

    db_trades = _query_trades()
    return db_trades, "SQLite"


def _performance_history(trades):
    closed = [
        t for t in trades
        if t.get("status") == "CLOSED"
    ]

    ordered = sorted(
        closed,
        key=lambda t: (
            t.get("close_time") or "",
            t.get("open_time") or "",
            t.get("id") or 0,
        ),
    )

    equity = 0.0
    peak = 0.0
    result = []

    for index, trade in enumerate(ordered, start=1):
        profit = _safe_float(trade.get("profit"))
        equity += profit
        peak = max(peak, equity)
        drawdown = peak - equity
        drawdown_pct = (
            drawdown / peak * 100.0
            if peak > 0
            else 0.0
        )

        result.append(
            {
                "trade_no": index,
                "id": trade.get("id"),
                "ticket": trade.get("ticket"),
                "symbol": trade.get("symbol"),
                "signal": trade.get("signal"),
                "confidence": trade.get("confidence"),
                "volume": _safe_float(trade.get("volume")),
                "entry": _safe_float(trade.get("entry")),
                "stop_loss": trade.get("stop_loss"),
                "take_profit": trade.get("take_profit"),
                "profit": round(profit, 2),
                "equity": round(equity, 2),
                "peak": round(peak, 2),
                "drawdown": round(drawdown, 2),
                "drawdown_percent": round(drawdown_pct, 2),
                "open_time": trade.get("open_time"),
                "close_time": trade.get("close_time"),
                "source": trade.get("source", "SQLite"),
            }
        )

    return result


def _metrics(trades, history, source):
    closed = [
        t for t in trades
        if t.get("status") == "CLOSED"
    ]
    open_trades = [
        t for t in trades
        if t.get("status") == "OPEN"
    ]

    profits = [
        _safe_float(t.get("profit"))
        for t in closed
    ]
    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p < 0]

    total_profit = sum(profits)
    win_rate = (
        len(wins) / len(closed) * 100
        if closed
        else 0.0
    )

    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else (
            None
            if gross_profit <= 0
            else "INF"
        )
    )

    max_drawdown = max(
        [point["drawdown"] for point in history],
        default=0.0,
    )
    max_drawdown_pct = max(
        [point["drawdown_percent"] for point in history],
        default=0.0,
    )

    return {
        "history_source": source,
        "total_trades": len(trades),
        "open_trades": len(open_trades),
        "closed_trades": len(closed),
        "winning_trades": len(wins),
        "losing_trades": len(losses),
        "breakeven_trades": len(
            [p for p in profits if p == 0]
        ),
        "win_rate": round(win_rate, 2),
        "total_profit": round(total_profit, 2),
        "average_profit": round(
            total_profit / len(profits), 2
        ) if profits else 0.0,
        "average_win": round(
            gross_profit / len(wins), 2
        ) if wins else 0.0,
        "average_loss": round(
            sum(losses) / len(losses), 2
        ) if losses else 0.0,
        "profit_factor": (
            round(profit_factor, 2)
            if isinstance(profit_factor, float)
            else profit_factor
        ),
        "max_drawdown": round(max_drawdown, 2),
        "max_drawdown_percent": round(
            max_drawdown_pct, 2
        ),
        "first_trade_time": (
            history[0]["open_time"]
            if history
            else None
        ),
        "last_closed_time": (
            history[-1]["close_time"]
            if history
            else None
        ),
        "realized_equity": round(
            history[-1]["equity"], 2
        ) if history else 0.0,
    }



def _period_stats(history):
    """Return daily, weekly and monthly realized P/L summaries."""
    now = datetime.now()
    periods = {
        "today": [],
        "7d": [],
        "30d": [],
    }

    for trade in history:
        close_time = trade.get("close_time")
        if not close_time:
            continue
        try:
            dt = datetime.fromisoformat(close_time)
        except (TypeError, ValueError):
            continue

        delta = now - dt
        profit = _safe_float(trade.get("profit"))

        if dt.date() == now.date():
            periods["today"].append(profit)
        if delta <= timedelta(days=7):
            periods["7d"].append(profit)
        if delta <= timedelta(days=30):
            periods["30d"].append(profit)

    result = {}
    for key, values in periods.items():
        wins = [v for v in values if v > 0]
        losses = [v for v in values if v < 0]
        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        result[key] = {
            "trades": len(values),
            "wins": len(wins),
            "losses": len(losses),
            "profit": round(sum(values), 2),
            "win_rate": round(
                len(wins) / len(values) * 100, 2
            ) if values else 0.0,
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2),
            "profit_factor": round(
                gross_profit / gross_loss, 2
            ) if gross_loss > 0 else (
                "INF" if gross_profit > 0 else 0.0
            ),
        }

    return result


def _breakdown_stats(history, key_name):
    """Aggregate realized results by a selected trade attribute."""
    buckets = {}
    for trade in history:
        key = trade.get(key_name)
        if key in (None, ""):
            key = "UNKNOWN"
        key = str(key)

        bucket = buckets.setdefault(
            key,
            {"trades": 0, "wins": 0, "losses": 0, "profit": 0.0}
        )
        p = _safe_float(trade.get("profit"))
        bucket["trades"] += 1
        bucket["profit"] += p
        if p > 0:
            bucket["wins"] += 1
        elif p < 0:
            bucket["losses"] += 1

    rows = []
    for key, bucket in buckets.items():
        rows.append({
            "key": key,
            "trades": bucket["trades"],
            "wins": bucket["wins"],
            "losses": bucket["losses"],
            "profit": round(bucket["profit"], 2),
            "win_rate": round(
                bucket["wins"] / bucket["trades"] * 100, 2
            ) if bucket["trades"] else 0.0,
            "avg_trade": round(
                bucket["profit"] / bucket["trades"], 2
            ) if bucket["trades"] else 0.0,
        })

    rows.sort(key=lambda x: x["profit"], reverse=True)
    return rows


def _advanced_metrics(history):
    """Compute additional portfolio statistics from realized history."""
    profits = [_safe_float(t.get("profit")) for t in history]

    if not profits:
        return {
            "expectancy": 0.0,
            "best_trade": 0.0,
            "worst_trade": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "largest_win": 0.0,
            "largest_loss": 0.0,
            "max_consecutive_wins": 0,
            "max_consecutive_losses": 0,
        }

    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p < 0]

    max_w = max_wins = 0
    max_l = max_losses = 0
    for p in profits:
        if p > 0:
            max_w += 1
            max_l = 0
        elif p < 0:
            max_l += 1
            max_w = 0
        else:
            max_w = 0
            max_l = 0
        max_wins = max(max_wins, max_w)
        max_losses = max(max_losses, max_l)

    return {
        "expectancy": round(sum(profits) / len(profits), 2),
        "best_trade": round(max(profits), 2),
        "worst_trade": round(min(profits), 2),
        "avg_win": round(sum(wins) / len(wins), 2) if wins else 0.0,
        "avg_loss": round(sum(losses) / len(losses), 2) if losses else 0.0,
        "largest_win": round(max(wins), 2) if wins else 0.0,
        "largest_loss": round(min(losses), 2) if losses else 0.0,
        "max_consecutive_wins": max_wins,
        "max_consecutive_losses": max_losses,
    }


def _mt5_snapshot():
    if not _ensure_mt5():
        return {
            "connected": False,
            "error": "MT5 terminal is not connected.",
            "balance": None,
            "equity": None,
            "floating_profit": None,
            "positions": [],
        }

    try:
        account = mt5.account_info()
        positions = mt5.positions_get()

        result = {
            "connected": account is not None,
            "balance": (
                round(float(account.balance), 2)
                if account
                else None
            ),
            "equity": (
                round(float(account.equity), 2)
                if account
                else None
            ),
            "floating_profit": (
                round(float(account.profit), 2)
                if account
                else None
            ),
            "positions": [],
        }

        if positions:
            for position in positions:
                if int(getattr(position, "magic", 0)) != int(MAGIC_NUMBER):
                    continue

                result["positions"].append(
                    {
                        "ticket": int(position.ticket),
                        "symbol": str(position.symbol),
                        "type": (
                            "BUY"
                            if position.type == mt5.ORDER_TYPE_BUY
                            else "SELL"
                        ),
                        "volume": float(position.volume),
                        "entry": float(position.price_open),
                        "sl": float(position.sl),
                        "tp": float(position.tp),
                        "profit": float(position.profit),
                        "open_time": datetime.fromtimestamp(
                            int(position.time)
                        ).isoformat(sep=" "),
                    }
                )

        return result

    except Exception as exc:
        return {
            "connected": False,
            "error": f"MT5 snapshot error: {type(exc).__name__}: {exc}",
            "balance": None,
            "equity": None,
            "floating_profit": None,
            "positions": [],
        }


def build_payload():
    """
    Build dashboard data without allowing a single data-source error
    to take down the API endpoint.
    """
    try:
        trades, source = _history_source()
        history = _performance_history(trades)

        return {
            "ok": True,
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
            "database": str(DB_PATH),
            "magic_number": MAGIC_NUMBER,
            "symbol": SYMBOL,
            "metrics": _metrics(
                trades,
                history,
                source
            ),
            "periods": _period_stats(history),
            "advanced": _advanced_metrics(history),
            "by_signal": _breakdown_stats(history, "signal"),
            "by_symbol": _breakdown_stats(history, "symbol"),
            "by_confidence": _breakdown_stats(
                history,
                "confidence"
            ),
            "mt5": _mt5_snapshot(),
            "recent_trades": trades[-15:][::-1],
            "performance_history": history,
        }

    except Exception as exc:
        return {
            "ok": False,
            "error": (
                f"{type(exc).__name__}: {exc}"
            ),
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
            "database": str(DB_PATH),
            "magic_number": MAGIC_NUMBER,
            "symbol": SYMBOL,
            "metrics": {},
            "periods": {},
            "advanced": {},
            "by_signal": [],
            "by_symbol": [],
            "by_confidence": [],
            "mt5": {
                "connected": False,
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "positions": [],
            },
            "recent_trades": [],
            "performance_history": [],
        }


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Aegis AI Dashboard v0.6.2</title>
<style>
:root{color-scheme:dark;font-family:Inter,Segoe UI,Arial,sans-serif}
body{margin:0;background:#0b1020;color:#edf2f7}
.wrap{max-width:1500px;margin:0 auto;padding:24px}
header{display:flex;justify-content:space-between;align-items:end;gap:16px;margin-bottom:20px}
h1{margin:0;font-size:28px}.muted{color:#94a3b8;font-size:13px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.card{background:#121a2b;border:1px solid #27324a;border-radius:14px;padding:16px;box-shadow:0 8px 24px rgba(0,0,0,.15)}
.label{color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:.08em}.value{font-size:26px;font-weight:700;margin-top:8px}
.section{margin-top:18px}.section h2{font-size:17px;margin:0 0 10px}
.status{display:inline-flex;align-items:center;gap:8px;padding:6px 10px;border-radius:999px;background:#17213a;font-size:12px}
.dot{width:8px;height:8px;border-radius:50%;background:#94a3b8}.ok .dot{background:#22c55e}.bad .dot{background:#ef4444}
.good{color:#22c55e}.badtext{color:#ef4444}.warn{color:#f59e0b}.empty{color:#94a3b8;padding:16px 0}
.table-wrap{overflow:auto;max-height:560px}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:10px;border-bottom:1px solid #27324a;text-align:left;white-space:nowrap}th{color:#94a3b8;font-weight:600;position:sticky;top:0;background:#121a2b}
.chart-card{padding:14px}.chart-head{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:8px}.chart-head strong{font-size:14px}.legend{font-size:12px;color:#94a3b8}
svg{width:100%;height:310px;display:block;background:#0e1526;border:1px solid #27324a;border-radius:10px}
.chart-grid{stroke:#26324a;stroke-width:1}.chart-axis{stroke:#506079;stroke-width:1}.equity-line{fill:none;stroke:#60a5fa;stroke-width:2.5}.dd-area{fill:rgba(239,68,68,.18)}.dd-line{fill:none;stroke:#ef4444;stroke-width:1.8}.bar-pos{fill:#22c55e}.bar-neg{fill:#ef4444}.chart-text{fill:#94a3b8;font-size:11px}.chart-point{fill:#60a5fa}
.live-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:12px}
.live-trade{border-top:1px solid #27324a;padding-top:12px;margin-top:12px}.live-title{display:flex;justify-content:space-between;gap:12px}.live-pnl{font-weight:800;font-size:22px}
.source{margin:10px 0 0;padding:8px 10px;background:#0e1526;border-radius:8px;font-size:12px;color:#cbd5e1}
@media(max-width:1000px){.grid,.live-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.grid,.live-grid{grid-template-columns:1fr}.wrap{padding:14px}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <div><h1>🤖 Aegis AI</h1><div class="muted">Read-only v0.6.2 · MT5 Live P/L + Full Broker History</div></div>
  <div id="status" class="status"><span class="dot"></span><span>Loading…</span></div>
</header>

<div class="grid" id="cards"></div>

<div class="section card">
  <h2>Live Trading</h2>
  <div id="live"></div>
</div>

<div class="section chart-card">
  <div class="chart-head"><strong>Full Performance — Equity Curve & Drawdown</strong><span id="source" class="legend">Loading history…</span></div>
  <div id="equityChart"></div>
</div>

<div class="section chart-card">
  <div class="chart-head"><strong>Trade-by-Trade P/L</strong><span class="legend">Complete closed history</span></div>
  <div id="profitChart"></div>
</div>

<div class="section card">
  <h2>Performance Periods</h2>
  <div class="grid" id="periods"></div>
</div>

<div class="section card">
  <h2>Advanced Statistics</h2>
  <div class="grid" id="advanced"></div>
</div>

<div class="section card">
  <h2>Performance by Direction / Setup</h2>
  <div id="breakdowns"></div>
</div>

<div class="section card">
  <h2>Full Trade History</h2>
  <div id="history"></div>
</div>

<div class="section card">
  <h2>Full Trade History</h2>
  <div id="history"></div>
</div>

<div class="muted" style="margin-top:14px">Auto-refresh: 5 seconds · Read-only dashboard · Live P/L from MT5 · Historical performance from MT5 history with SQLite fallback</div>
</div>
<script>
const fmt=(v)=>v===null||v===undefined?'—':Number(v).toFixed(2);
const money=(v)=>v===null||v===undefined?'—':(Number(v)>=0?'+':'')+Number(v).toFixed(2);
const esc=(s)=>String(s??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
function card(label,value,cls=''){return `<div class="card"><div class="label">${esc(label)}</div><div class="value ${cls}">${esc(value)}</div></div>`}
function niceRange(values){
  if(!values.length)return {min:-1,max:1};
  let min=Math.min(...values),max=Math.max(...values);
  if(min===max){min-=1;max+=1;}
  const pad=(max-min)*0.12;return {min:min-pad,max:max+pad};
}
function equitySvg(history){
  if(!history.length)return '<div class="empty">No closed MT5 positions yet.</div>';
  const W=1100,H=310,L=56,R=20,T=18,B=42,CW=W-L-R,CH=H-T-B;
  const equity=history.map(x=>x.equity), dd=history.map(x=>-x.drawdown);
  const er=niceRange(equity), dr=niceRange(dd);
  const ex=i=>L+(i/(Math.max(history.length-1,1)))*CW;
  const ey=v=>T+(er.max-v)/(er.max-er.min)*CH;
  const dy=v=>T+(dr.max-v)/(dr.max-dr.min||1)*CH;
  const epts=history.map((x,i)=>`${ex(i).toFixed(1)},${ey(x.equity).toFixed(1)}`).join(' ');
  const dpts=history.map((x,i)=>`${ex(i).toFixed(1)},${dy(-x.drawdown).toFixed(1)}`).join(' ');
  const area=`${L},${dy(0)} ${dpts} ${ex(history.length-1)},${dy(0)}`;
  let grid='';
  for(let i=0;i<5;i++){
    const y=T+i*(CH/4),v=er.max-i*(er.max-er.min)/4;
    grid+=`<line x1="${L}" x2="${W-R}" y1="${y}" y2="${y}" class="chart-grid"/><text x="${L-8}" y="${y+4}" text-anchor="end" class="chart-text">${fmt(v)}</text>`;
  }
  const labels=[0,Math.floor((history.length-1)/2),history.length-1];
  labels.forEach(i=>{if(i>=0){grid+=`<text x="${ex(i)}" y="${H-14}" text-anchor="middle" class="chart-text">T${history[i].trade_no}</text>`;}});
  return `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><line x1="${L}" x2="${L}" y1="${T}" y2="${H-B}" class="chart-axis"/><line x1="${L}" x2="${W-R}" y1="${H-B}" y2="${H-B}" class="chart-axis"/>${grid}<polygon points="${area}" class="dd-area"/><polyline points="${dpts}" class="dd-line"/><polyline points="${epts}" class="equity-line"/>${history.map((x,i)=>`<circle cx="${ex(i)}" cy="${ey(x.equity)}" r="2.8" class="chart-point"><title>Trade ${x.trade_no} · Ticket ${esc(x.ticket)} · P/L ${money(x.profit)} · Equity ${fmt(x.equity)} · Close ${esc(x.close_time)}</title></circle>`).join('')}</svg>`;
}
function profitSvg(history){
  if(!history.length)return '<div class="empty">No closed MT5 positions yet.</div>';
  const W=1100,H=300,L=48,R=16,T=20,B=48,CW=W-L-R,CH=H-T-B;
  const vals=history.map(x=>x.profit),range=niceRange(vals),y=v=>T+(range.max-v)/(range.max-range.min)*CH,zero=y(0),barW=Math.max(4,Math.min(30,CW/history.length*.65));
  let svg=`<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><line x1="${L}" x2="${W-R}" y1="${zero}" y2="${zero}" class="chart-axis"/>`;
  history.forEach((x,i)=>{
    const cx=L+((i+.5)/history.length)*CW;
    const top=y(Math.max(x.profit,0)),bottom=y(Math.min(x.profit,0));
    const h=Math.max(1,Math.abs(bottom-top));
    const cls=x.profit>=0?'bar-pos':'bar-neg';
    svg+=`<rect x="${cx-barW/2}" y="${Math.min(top,bottom)}" width="${barW}" height="${h}" class="${cls}"><title>Trade ${x.trade_no} · Ticket ${esc(x.ticket)} · ${esc(x.symbol)} · ${esc(x.signal)} · P/L ${money(x.profit)}</title></rect>`;
    if(history.length<=25||i%Math.ceil(history.length/12)===0){svg+=`<text x="${cx}" y="${H-18}" text-anchor="middle" class="chart-text">${x.trade_no}</text>`;}
  });
  svg+=`<text x="${L-8}" y="${T+4}" text-anchor="end" class="chart-text">${fmt(range.max)}</text><text x="${L-8}" y="${H-B-4}" text-anchor="end" class="chart-text">${fmt(range.min)}</text></svg>`;
  return svg;
}
function renderLive(a){
  const open=a.positions||[];
  const cards=`<div class="live-grid">${card('MT5 Balance',fmt(a.balance))}${card('MT5 Equity',fmt(a.equity))}${card('Aegis Floating P/L',money(a.floating_profit),a.floating_profit>=0?'good':'badtext')}${card('Aegis Live Positions',open.length)}</div>`;
  const positions=open.length?open.map(p=>`<div class="live-trade"><div class="live-title"><div><strong>${esc(p.symbol)} ${esc(p.type)}</strong><div class="muted">Ticket ${esc(p.ticket)} · Volume ${fmt(p.volume)} · Open ${esc(p.open_time)}</div></div><div class="live-pnl ${p.profit>=0?'good':'badtext'}">${money(p.profit)}</div></div><div class="muted" style="margin-top:8px">Entry ${fmt(p.entry)} · SL ${fmt(p.sl)} · TP ${fmt(p.tp)}</div></div>`).join(''):`<div class="empty">No live Aegis positions.</div>`;
  return cards+positions;
}
function renderHistory(history){
  if(!history.length)return '<div class="empty">No closed history returned by MT5.</div>';
  const rows=history.slice().reverse().map(t=>`<tr><td>${t.trade_no}</td><td>${esc(t.ticket)}</td><td>${esc(t.symbol)}</td><td>${esc(t.signal||'—')}</td><td>${esc(t.confidence??'—')}</td><td>${fmt(t.volume)}</td><td>${fmt(t.entry)}</td><td>${fmt(t.stop_loss)}</td><td>${fmt(t.take_profit)}</td><td class="${t.profit>=0?'good':'badtext'}">${money(t.profit)}</td><td>${fmt(t.equity)}</td><td>${fmt(t.drawdown)}</td><td>${esc(t.close_time||'')}</td></tr>`).join('');
  return `<div class="table-wrap"><table><thead><tr><th>#</th><th>Ticket</th><th>Symbol</th><th>Direction</th><th>Conf.</th><th>Vol</th><th>Entry</th><th>SL</th><th>TP</th><th>P/L</th><th>Equity</th><th>Drawdown</th><th>Close Time</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

function renderPeriodCard(title, p){
  const pf = p.profit_factor === "INF" ? "INF" : fmt(p.profit_factor);
  return `<div class="card">
    <div class="label">${esc(title)}</div>
    <div class="value ${p.profit>=0?'good':'badtext'}">${money(p.profit)}</div>
    <div class="muted">${p.trades} trades · ${p.win_rate}% win rate · PF ${pf}</div>
  </div>`;
}

function renderBreakdowns(d){
  const section=(title, rows)=>`<div style="margin-top:12px">
    <div class="muted" style="margin-bottom:6px">${esc(title)}</div>
    <div class="table-wrap">
      <table><thead><tr><th>Group</th><th>Trades</th><th>Wins</th><th>Losses</th><th>Win Rate</th><th>Total P/L</th><th>Avg Trade</th></tr></thead>
      <tbody>${rows.map(r=>`<tr>
        <td>${esc(r.key)}</td>
        <td>${r.trades}</td>
        <td>${r.wins}</td>
        <td>${r.losses}</td>
        <td>${fmt(r.win_rate)}%</td>
        <td class="${r.profit>=0?'good':'badtext'}">${money(r.profit)}</td>
        <td>${money(r.avg_trade)}</td>
      </tr>`).join('')}</tbody></table>
    </div>
  </div>`;
  return section('Direction',d.by_signal||[])+section('Symbol',d.by_symbol||[])+section('Confidence',d.by_confidence||[]);
}

async function refresh(){
  try{
    const r=await fetch('/api/status',{cache:'no-store'}); 
    const d=await r.json();

    if(!r.ok || d.ok===false){
      throw new Error(d.error || `HTTP ${r.status}`);
    }

    const m=d.metrics,a=d.mt5,h=d.performance_history||[];
    document.getElementById('status').className='status '+(a.connected?'ok':'bad');
    document.getElementById('status').innerHTML=`<span class="dot"></span><span>${a.connected?'MT5 Connected':'MT5 Unavailable'} · ${esc(d.timestamp)}</span>`;
    document.getElementById('cards').innerHTML=[
      card('Open Trades',m.open_trades),card('Win Rate',m.win_rate+'%'),
      card('Realized P/L',money(m.total_profit),m.total_profit>=0?'good':'badtext'),card('Profit Factor',m.profit_factor===null?'—':m.profit_factor),
      card('Closed Trades',m.closed_trades),card('Winning Trades',m.winning_trades),
      card('Max Drawdown',fmt(m.max_drawdown),m.max_drawdown>0?'badtext':''),card('Realized Equity',money(m.realized_equity),m.realized_equity>=0?'good':'badtext')
    ].join('');
    document.getElementById('live').innerHTML=renderLive(a);
    document.getElementById('source').innerHTML=`History source: ${esc(m.history_source)} · Magic ${esc(d.magic_number)} · ${esc(d.symbol)}`;
    document.getElementById('equityChart').innerHTML=equitySvg(h);
    document.getElementById('profitChart').innerHTML=profitSvg(h);
    const periods=d.periods||{};
    document.getElementById('periods').innerHTML =
      renderPeriodCard('Today', periods.today||{profit:0,trades:0,win_rate:0,profit_factor:0}) +
      renderPeriodCard('Last 7 Days', periods['7d']||{profit:0,trades:0,win_rate:0,profit_factor:0}) +
      renderPeriodCard('Last 30 Days', periods['30d']||{profit:0,trades:0,win_rate:0,profit_factor:0});

    const a2=d.advanced||{};
    document.getElementById('advanced').innerHTML =
      card('Expectancy / Trade', money(a2.expectancy), a2.expectancy>=0?'good':'badtext') +
      card('Best Trade', money(a2.best_trade), 'good') +
      card('Worst Trade', money(a2.worst_trade), 'badtext') +
      card('Avg Win', money(a2.avg_win), 'good') +
      card('Avg Loss', money(a2.avg_loss), 'badtext') +
      card('Max Consecutive Wins', a2.max_consecutive_wins||0) +
      card('Max Consecutive Losses', a2.max_consecutive_losses||0);

    document.getElementById('breakdowns').innerHTML = renderBreakdowns(d);
    document.getElementById('history').innerHTML=renderHistory(h);
  }catch(e){
    document.getElementById('status').className='status bad';
    document.getElementById('status').innerHTML =
      `<span class="dot"></span><span>Dashboard API error: ${esc(e.message)}</span>`;
  }
}
refresh();setInterval(refresh,5000);
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/status":
            try:
                payload = build_payload()
                body = json.dumps(
                    payload,
                    default=str,
                    allow_nan=False,
                ).encode("utf-8")

                status_code = 200 if payload.get("ok", True) else 500

            except Exception as exc:
                payload = {
                    "ok": False,
                    "error": (
                        f"{type(exc).__name__}: {exc}"
                    ),
                }
                body = json.dumps(
                    payload,
                    default=str,
                ).encode("utf-8")
                status_code = 500

            self.send_response(status_code)
            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )
            self.send_header(
                "Cache-Control",
                "no-store"
            )
            self.send_header(
                "Content-Length",
                str(len(body))
            )
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


def main():
    print("=" * 60)
    print("🤖 AEGIS AI DASHBOARD v0.6.2")
    print("=" * 60)
    print(f"Database      : {DB_PATH}")
    print(f"Magic Number  : {MAGIC_NUMBER}")
    print(f"Symbol        : {SYMBOL}")
    print(f"URL           : http://{HOST}:{PORT}")
    print("Read-only dashboard. No order controls enabled.")
    print("Live P/L from MT5 + historical performance from MT5.")
    print("SQLite is used as fallback if MT5 history is unavailable.")
    print("Press Ctrl+C to stop.")

    server = ThreadingHTTPServer(
        (HOST, PORT),
        Handler
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

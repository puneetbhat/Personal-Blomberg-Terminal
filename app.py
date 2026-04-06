"""
PUNEET TERMINAL – Flask backend
Serves live prices, news, history, commodities and Anthropic AI proxy.
"""
import json
import os
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import anthropic
import feedparser
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

PORTFOLIO_FILE = os.path.join(os.path.dirname(__file__), "portfolio.json")

# ── Thread-safe cache ────────────────────────────────────────────────────────
_cache: dict = {}
_cache_ts: dict = {}
_lock = threading.Lock()


def get_cached(key: str, fetch_fn, ttl: int = 30):
    now = time.time()
    with _lock:
        if key in _cache and now - _cache_ts.get(key, 0) < ttl:
            return _cache[key]
    try:
        data = fetch_fn()
        with _lock:
            _cache[key] = data
            _cache_ts[key] = now
        return data
    except Exception as exc:
        print(f"[cache] {key} fetch failed: {exc}")
        with _lock:
            if key in _cache:
                return _cache[key]          # return stale rather than crash
        return None


# ── Portfolio ────────────────────────────────────────────────────────────────
def load_portfolio() -> dict:
    with open(PORTFOLIO_FILE, encoding="utf-8") as f:
        return json.load(f)


# ── Hardcoded fallbacks so the UI never shows "–" ───────────────────────────
FALLBACK = {
    "^NSEI":    {"p": 24508.65, "c": 100.41,  "cp":  0.41},
    "^NSEBANK": {"p": 52134.20, "c": -94.55,  "cp": -0.18},
    "^BSESN":   {"p": 80780.25, "c": 282.85,  "cp":  0.35},
    "^GSPC":    {"p":  5614.56, "c": -12.35,  "cp": -0.22},
    "^VIX":     {"p":    14.22, "c":  -0.45,  "cp": -3.10},
    "USDINR=X": {"p":    86.48, "c":   0.02,  "cp":  0.02},
    "EURINR=X": {"p":   109.50, "c":   0.12,  "cp":  0.11},
    "GBPINR=X": {"p":   110.50, "c":   0.03,  "cp":  0.03},
    "GC=F":     {"p":  2870.00, "c":  12.50,  "cp":  0.44},
    "SI=F":     {"p":    32.80, "c":   0.25,  "cp":  0.77},
    "CL=F":     {"p":    71.50, "c":  -0.40,  "cp": -0.56},
    "BTC-USD":  {"p": 84000.00, "c": 1200.00, "cp":  1.45},
}


# ── Price fetching via fast_info (live last-traded price, parallelised) ───────
def _build_ticker_list() -> list[str]:
    pf = load_portfolio()
    tickers = []
    for h in pf.get("angel", []) + pf.get("kite", []):
        if h.get("nse"):
            tickers.append(h["nse"])
    for s in pf.get("us", []):
        tickers.append(s["sym"])
    tickers += [
        "^NSEI", "^NSEBANK", "^BSESN", "^GSPC", "^VIX",
        "USDINR=X", "EURINR=X", "GBPINR=X",
        "GC=F", "SI=F", "CL=F", "NG=F", "HG=F",
        "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD",
    ]
    return list(dict.fromkeys(tickers))          # deduplicate, preserve order


def _fetch_one(sym: str) -> tuple[str, dict | None]:
    """Fetch live last_price + previous_close for a single ticker."""
    try:
        fi = yf.Ticker(sym).fast_info
        last  = float(fi.last_price)
        prev  = float(fi.previous_close) if fi.previous_close else last
        chg   = last - prev
        chg_p = (chg / prev * 100) if prev else 0.0
        return sym, {"p": round(last, 4), "c": round(chg, 4), "cp": round(chg_p, 4)}
    except Exception as exc:
        print(f"[prices] {sym}: {exc}")
        return sym, None


def _do_fetch_prices() -> dict:
    tickers = _build_ticker_list()
    result  = {}
    # 12 workers ≈ 5-8 s for 50 tickers
    with ThreadPoolExecutor(max_workers=12) as ex:
        futures = {ex.submit(_fetch_one, sym): sym for sym in tickers}
        for fut in as_completed(futures):
            sym, data = fut.result()
            if data:
                result[sym] = data
    # Fill anything still missing with fallback
    for sym, fb in FALLBACK.items():
        if sym not in result or not result[sym].get("p"):
            result[sym] = fb
    return result


def get_all_prices() -> dict:
    return get_cached("all_prices", _do_fetch_prices, ttl=30) or FALLBACK


# ── News ─────────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    ("ECONOMIC TIMES", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
    ("MONEYCONTROL",   "https://www.moneycontrol.com/rss/MCtopnews.xml"),
    ("LIVEMINT",       "https://www.livemint.com/rss/markets"),
    ("CNBC",           "https://www.cnbctv18.com/rss/market.xml"),
    ("BLOOMBERG",      "https://news.google.com/rss/search?q=bloomberg+india+stocks+market&hl=en-IN&gl=IN&ceid=IN:en"),
]

# Portfolio keywords — only keep news matching these
PORTFOLIO_KEYWORDS = [
    "IRFC", "HDFCBANK", "HAL", "SPICEJET", "NIFTYBEES", "RELIANCE",
    "SUNPHARMA", "OFSS", "LT", "TATASTEEL", "META", "AAPL", "NIFTY",
    "SENSEX", "RBI", "BANKBEES", "ELECON", "ITC", "JSWENERGY", "SILVERBEES",
    "GMRAIRPORT", "INDHOTEL", "ITCHOTELS", "ABCAPITAL", "BAJAJHFL",
    "HDFCBANK", "IDFCFIRSTB", "WAAREEENER", "GEECEE", "JIOFIN",
    "market", "nifty", "sensex", "rate", "rbi", "budget", "inflation",
    "paypal", "apple", "meta", "nasdaq", "dow jones", "s&p",
]

BULL_WORDS = {"rally","surge","gain","rise","high","beat","profit","growth","up","buy","bullish","strong"}
BEAR_WORDS = {"fall","drop","decline","loss","crash","cut","miss","low","sell","bearish","weak","tumble"}


def _time_ago(entry: dict) -> str:
    try:
        import email.utils
        pub = entry.get("published", "")
        if pub:
            ts = email.utils.parsedate_to_datetime(pub)
            diff = datetime.now(ts.tzinfo) - ts
            s = int(diff.total_seconds())
            if s < 60:   return f"{s}s"
            if s < 3600: return f"{s//60}m"
            if s < 86400:return f"{s//3600}h"
            return f"{s//86400}d"
    except Exception:
        pass
    return "?"


def _do_fetch_news() -> list[dict]:
    items = []
    kw_lower = [k.lower() for k in PORTFOLIO_KEYWORDS]
    for src_name, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries[:20]:
                title   = (entry.get("title", "") or "").strip()
                summary = re.sub(r"<[^>]+>", "", (entry.get("summary", "") or "")).strip()
                if not title:
                    continue
                tl = title.lower()
                # Only include if headline matches a portfolio stock or market keyword
                if not any(k in tl for k in kw_lower):
                    continue
                if any(w in tl for w in BULL_WORDS):
                    sent = "bull"
                elif any(w in tl for w in BEAR_WORDS):
                    sent = "bear"
                else:
                    sent = "neu"
                link = entry.get("link", "")
                # For Google News links (Bloomberg feed), try to get the real URL
                if "news.google.com" in link:
                    link = entry.get("source", {}).get("href", link) or link
                items.append({
                    "src":  src_name,
                    "time": _time_ago(entry),
                    "head": title[:130],
                    "body": summary[:220] if summary else "Click to read full article.",
                    "tags": [sent.upper()],
                    "sent": sent,
                    "link": link,
                })
                count += 1
                if count >= 4:
                    break
        except Exception as exc:
            print(f"[news] {src_name}: {exc}")
    return items[:20]


def get_news() -> list:
    return get_cached("news", _do_fetch_news, ttl=60) or []


# ── Commodities + Crypto ─────────────────────────────────────────────────────
COMMODITY_MAP = {
    "GC=F":    ("GOLD",         "Gold Spot",          "commodity", "https://finance.yahoo.com/quote/GC%3DF/"),
    "SI=F":    ("SILVER",       "Silver Spot",        "commodity", "https://finance.yahoo.com/quote/SI%3DF/"),
    "CL=F":    ("CRUDE OIL",    "WTI Crude Oil",      "commodity", "https://finance.yahoo.com/quote/CL%3DF/"),
    "NG=F":    ("NAT GAS",      "Natural Gas",        "commodity", "https://finance.yahoo.com/quote/NG%3DF/"),
    "HG=F":    ("COPPER",       "Copper Futures",     "commodity", "https://finance.yahoo.com/quote/HG%3DF/"),
}
CRYPTO_MAP = {
    "BTC-USD":  ("BTC",  "Bitcoin",   "https://finance.yahoo.com/quote/BTC-USD/"),
    "ETH-USD":  ("ETH",  "Ethereum",  "https://finance.yahoo.com/quote/ETH-USD/"),
    "BNB-USD":  ("BNB",  "BNB Chain", "https://finance.yahoo.com/quote/BNB-USD/"),
    "SOL-USD":  ("SOL",  "Solana",    "https://finance.yahoo.com/quote/SOL-USD/"),
    "XRP-USD":  ("XRP",  "XRP",       "https://finance.yahoo.com/quote/XRP-USD/"),
    "ADA-USD":  ("ADA",  "Cardano",   "https://finance.yahoo.com/quote/ADA-USD/"),
}

# Add crypto to fallback
FALLBACK.update({
    "NG=F":     {"p":   3.20,  "c":  0.05, "cp":  1.59},
    "HG=F":     {"p":   4.85,  "c": -0.02, "cp": -0.41},
    "ETH-USD":  {"p": 2100.00, "c": 25.00, "cp":  1.20},
    "BNB-USD":  {"p":  580.00, "c":  8.00, "cp":  1.40},
    "SOL-USD":  {"p":  130.00, "c":  2.50, "cp":  1.96},
    "XRP-USD":  {"p":    0.55, "c":  0.01, "cp":  1.85},
    "ADA-USD":  {"p":    0.45, "c":  0.01, "cp":  2.27},
})


def _build_float_item(sym: str, name: str, label: str, kind: str, prices: dict, link: str = "") -> dict:
    q  = prices.get(sym, FALLBACK.get(sym, {}))
    p  = q.get("p")
    if p is None:
        return None
    cp    = q.get("cp", 0.0)
    is_up = cp >= 0
    # Format price sensibly
    if p >= 1000:
        p_str = f"${p:,.2f}"
    elif p >= 1:
        p_str = f"${p:,.4f}" if p < 10 else f"${p:,.2f}"
    else:
        p_str = f"${p:.6f}"
    return {
        "sym":    name,
        "label":  label,
        "type":   kind,
        "p":      p_str,
        "c":      f"{'+' if is_up else ''}{cp:.2f}%",
        "up":     is_up,
        "raw_p":  p,
        "raw_cp": cp,
        "link":   link or f"https://finance.yahoo.com/quote/{sym.replace('=', '%3D')}/",
    }


def _do_fetch_commodities() -> dict:
    prices = get_all_prices()
    comms  = []
    crypto = []
    for sym, (name, label, kind, link) in COMMODITY_MAP.items():
        item = _build_float_item(sym, name, label, kind, prices, link)
        if item:
            comms.append(item)
    for sym, (name, label, link) in CRYPTO_MAP.items():
        item = _build_float_item(sym, name, label, "crypto", prices, link)
        if item:
            crypto.append(item)
    # Ticker-bar flat list (commodity only for original ticker)
    ticker_items = [{"sym": i["sym"], "p": i["p"], "c": i["c"], "up": i["up"]} for i in comms]
    return {"commodities": comms, "crypto": crypto, "ticker": ticker_items}


def get_commodities() -> dict:
    return get_cached("commodities", _do_fetch_commodities, ttl=90) or {"commodities": [], "crypto": [], "ticker": []}


# ── Historical benchmark ──────────────────────────────────────────────────────
PERIOD_MAP = {
    "1D": ("1d",  "5m"),
    "1W": ("5d",  "1h"),
    "1M": ("1mo", "1d"),
    "3M": ("3mo", "1d"),
    "6M": ("6mo", "1d"),
    "1Y": ("1y",  "1wk"),
    "3Y": ("3y",  "1mo"),
    "5Y": ("5y",  "1mo"),
}


def _label_fmt(ts, period: str) -> str:
    if period == "1D":
        return ts.strftime("%H:%M")
    if period in ("1W", "1M", "3M"):
        return ts.strftime("%b %d")
    return ts.strftime("%b '%y")


def _do_fetch_history(period: str, is_us: bool) -> dict | None:
    yf_period, interval = PERIOD_MAP.get(period, ("1mo", "1d"))
    bench_sym = "^GSPC" if is_us else "^NSEI"

    # Benchmark
    bench_raw = yf.download(bench_sym, period=yf_period, interval=interval,
                             progress=False, auto_adjust=True)
    if bench_raw.empty:
        return None

    bench_close = bench_raw["Close"].dropna()
    bench_norm  = (bench_close / bench_close.iloc[0] - 1) * 100

    # Portfolio weighted return
    pf = load_portfolio()
    if is_us:
        holdings = pf.get("us", [])
        tickers  = [h["sym"] for h in holdings]
        weights  = [h["inv"] for h in holdings]
    else:
        all_eq  = pf.get("angel", []) + pf.get("kite", [])
        tickers = [h["nse"] for h in all_eq if h.get("nse")]
        weights = [h["inv"] for h in all_eq if h.get("nse")]

    # Use top 15 by weight
    paired   = sorted(zip(weights, tickers), reverse=True)[:15]
    w_top    = [w for w, _ in paired]
    t_top    = [t for _, t in paired]
    total_w  = sum(w_top) or 1

    portfolio_norm = pd.Series(0.0, index=bench_close.index)
    try:
        pf_raw = yf.download(t_top, period=yf_period, interval=interval,
                              progress=False, auto_adjust=True)
        if not pf_raw.empty and "Close" in pf_raw.columns:
            close = pf_raw["Close"]
            if isinstance(close, pd.Series):
                close = close.to_frame(name=t_top[0])
            close = close.reindex(bench_close.index, method="ffill")
            for sym, w in zip(t_top, w_top):
                if sym not in close.columns:
                    continue
                col = close[sym].dropna()
                if len(col) < 2:
                    continue
                pct = (col / col.iloc[0] - 1) * 100
                pct = pct.reindex(bench_close.index, method="ffill").fillna(0)
                portfolio_norm += pct * (w / total_w)
    except Exception as exc:
        print(f"[history] portfolio calc error: {exc}")

    labels     = [_label_fmt(ts, period) for ts in bench_close.index]
    bench_data = [round(float(v), 3) for v in bench_norm.values]
    pf_data    = [round(float(v), 3) for v in portfolio_norm.reindex(bench_close.index, method="ffill").fillna(0).values]

    pf_ret    = pf_data[-1]   if pf_data    else 0.0
    bench_ret = bench_data[-1] if bench_data else 0.0

    return {
        "labels":           labels,
        "portfolio":        pf_data,
        "benchmark":        bench_data,
        "portfolio_return": round(pf_ret, 2),
        "benchmark_return": round(bench_ret, 2),
        "alpha":            round(pf_ret - bench_ret, 2),
        "benchmark_name":   "S&P 500" if is_us else "NIFTY 50",
    }


# ── Flask routes ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/prices")
def api_prices():
    try:
        return jsonify({"ok": True, "data": get_all_prices()})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route("/api/news")
def api_news():
    try:
        return jsonify({"ok": True, "data": get_news()})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route("/api/commodities")
def api_commodities():
    try:
        return jsonify({"ok": True, "data": get_commodities()})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route("/api/history")
def api_history():
    period = request.args.get("period", "1M")
    is_us  = request.args.get("broker", "all") == "ind"
    key    = f"history_{period}_{is_us}"
    try:
        data = get_cached(key, lambda: _do_fetch_history(period, is_us), ttl=300)
        if data is None:
            return jsonify({"ok": False, "error": "No data available"}), 500
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route("/api/stock-chart")
def api_stock_chart():
    ticker = request.args.get("ticker", "").strip()
    period = request.args.get("period", "1M")
    if not ticker:
        return jsonify({"ok": False, "error": "No ticker provided"}), 400
    key = f"chart_{ticker}_{period}"
    def _fetch():
        yf_period, interval = PERIOD_MAP.get(period, ("1mo", "1d"))
        raw = yf.download(ticker, period=yf_period, interval=interval,
                          progress=False, auto_adjust=True)
        if raw.empty:
            return None
        # Handle MultiIndex
        if isinstance(raw.columns, pd.MultiIndex):
            close = raw.xs("Close", axis=1, level=0).iloc[:, 0]
        else:
            close = raw["Close"]
        close = close.dropna()
        if len(close) == 0:
            return None
        labels = [_label_fmt(ts, period) for ts in close.index]
        prices = [round(float(v), 2) for v in close.values]
        first_p = prices[0]
        last_p  = prices[-1]
        chg_pct = round(((last_p - first_p) / first_p * 100) if first_p else 0, 2)
        # Also get live price from fast_info
        try:
            fi      = yf.Ticker(ticker).fast_info
            live_p  = round(float(fi.last_price), 2)
            day_chg = round(float(fi.last_price - fi.previous_close) / fi.previous_close * 100, 2) if fi.previous_close else 0
        except Exception:
            live_p  = last_p
            day_chg = 0
        return {
            "ticker":    ticker,
            "labels":    labels,
            "prices":    prices,
            "period_chg": chg_pct,
            "day_chg":   day_chg,
            "high":      round(float(close.max()), 2),
            "low":       round(float(close.min()), 2),
            "live_p":    live_p,
        }
    try:
        data = get_cached(key, _fetch, ttl=300)
        if data is None:
            return jsonify({"ok": False, "error": "No data for ticker"}), 500
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route("/api/geo-ai", methods=["POST"])
def api_geo_ai():
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return jsonify({"ok": False, "error": "ANTHROPIC_API_KEY not set in .env"}), 400
    try:
        body   = request.get_json(force=True)
        prompt = body.get("prompt", "")
        client = anthropic.Anthropic(api_key=api_key)
        msg    = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return jsonify({"ok": True, "text": msg.content[0].text})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


if __name__ == "__main__":
    print("Starting PUNEET TERMINAL backend on http://localhost:5000")
    app.run(debug=True, port=5000, threaded=True)

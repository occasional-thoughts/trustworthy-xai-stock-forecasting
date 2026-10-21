"""Forecast the NEXT trading day, from data downloaded today.

The walk-forward test in train.py forecasts days whose outcome is already known, because
that is the only way to score a model. This script does the other half: it takes the same
features and the same hyperparameters, retrains on everything up to the most recent close,
and forecasts a day that has not happened yet.

    python src/live.py            # downloads, retrains, forecasts (~10 min the first time)
    python src/live.py --cached   # reuse the downloaded prices

Writes  data/live_panel.pkl       raw prices from Yahoo Finance
        data/live_features.pkl    the same 32 features, through the latest close
        models/rf_reg_live.joblib the retrained model
        results/live_forecast.pkl one row per stock: predicted next-day return

Caveats, which the demo page repeats:
  * 43 of the original 474 tickers no longer trade (acquired, merged or delisted), so the
    live universe is smaller and the market-context features are computed over it.
  * Prices come from Yahoo Finance, not the benchmark panel the study used. Both are
    split- and dividend-adjusted, but they are not the same vendor.
  * Nothing here is scored. The whole point is that the answer is not known yet.
"""
import json
import sys
import time
import warnings

import joblib
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor

from config import DATA, MODELS, PANEL_FILE, RESULTS, SECTOR_FILE, SEED, TRAIN_START
from features import FEATURES, build

warnings.filterwarnings("ignore")
START = "2012-05-14"          # same start as the study's panel
MIN_DAYS = 260                # a stock needs this much history before its features are usable
LIVE_PANEL = DATA / "live_panel.pkl"
LIVE_FEATURES = DATA / "live_features.pkl"
LIVE_MODEL = MODELS / "rf_reg_live.joblib"
LIVE_FORECAST = RESULTS / "live_forecast.pkl"


def download(tickers):
    t0 = time.time()
    raw = yf.download(tickers, start=START, auto_adjust=True, progress=False, threads=True)
    frames = []
    for field, name in (("Open", "open"), ("High", "high"), ("Low", "low"),
                        ("Close", "close"), ("Volume", "volume")):
        frames.append(raw[field].stack(future_stack=True).rename(name))
    panel = pd.concat(frames, axis=1).rename_axis(["date", "ticker"]).reset_index()
    panel = panel.dropna(subset=["open", "high", "low", "close", "volume"])
    keep = panel.groupby("ticker").size()
    panel = panel[panel.ticker.isin(keep[keep >= MIN_DAYS].index)]
    print(f"downloaded {len(panel):,} stock-days for {panel.ticker.nunique()} stocks "
          f"({panel.date.min().date()} -> {panel.date.max().date()}) [{time.time() - t0:.0f}s]", flush=True)
    return panel


def main():
    sectors = pd.read_csv(SECTOR_FILE)
    sector_col = [c for c in sectors.columns if "sector" in c.lower()][0]
    ticker_col = [c for c in sectors.columns if "ticker" in c.lower() or "symbol" in c.lower()][0]
    sector_of = dict(zip(sectors[ticker_col], sectors[sector_col]))
    universe = sorted(pd.read_pickle(PANEL_FILE).ticker.unique())

    if "--cached" in sys.argv and LIVE_PANEL.exists():
        panel = pd.read_pickle(LIVE_PANEL)
        print(f"reusing {len(panel):,} stock-days through {panel.date.max().date()}")
    else:
        panel = download(universe)
        panel.to_pickle(LIVE_PANEL)
    gone = sorted(set(universe) - set(panel.ticker.unique()))
    panel["sector"] = panel.ticker.map(sector_of)
    panel = panel.dropna(subset=["sector"])

    t0 = time.time()
    df = build(panel)
    df = df[df["date"] >= TRAIN_START].replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=FEATURES + ["close"])          # NOT on the target: the last day has none
    for col in FEATURES:
        df[col] = df[col].astype("float32")
    df = df.sort_values(["date", "ticker"]).reset_index(drop=True)
    df.to_pickle(LIVE_FEATURES)
    last_day = df.date.max()
    print(f"features through {last_day.date()} ({len(df):,} stock-days) [{time.time() - t0:.0f}s]", flush=True)

    # Train on every stock-day whose outcome is known; forecast the ones whose outcome is not.
    train = df.dropna(subset=["target_ret"])
    live = df[df.date == last_day].copy()
    assert live.target_ret.isna().all(), "the last day already has a known outcome - rerun after the close"

    t0 = time.time()
    chosen = json.loads((RESULTS / "tuning.json").read_text())["chosen"]
    model = RandomForestRegressor(n_estimators=chosen["n_estimators"],
                                  min_samples_leaf=chosen["min_samples_leaf"],
                                  max_features=chosen["max_features"],
                                  max_samples=chosen["max_samples"],
                                  n_jobs=-1, random_state=SEED)
    model.fit(train[FEATURES].values, train.target_ret.values)
    joblib.dump(model, LIVE_MODEL, compress=3)
    print(f"retrained on {len(train):,} stock-days up to {train.date.max().date()} "
          f"[{time.time() - t0:.0f}s]", flush=True)

    live["pred_ret"] = model.predict(live[FEATURES].values)
    live["pred_close"] = live["close"] * np.exp(live["pred_ret"])
    live["pred_ret_bp"] = 1e4 * live["pred_ret"]
    out = live[["date", "ticker", "sector", "close", "pred_ret", "pred_ret_bp", "pred_close"] + FEATURES]
    out.to_pickle(LIVE_FORECAST)
    (RESULTS / "live_meta.json").write_text(json.dumps({
        "as_of_close": str(last_day.date()),
        "forecast_for": "the next trading session after that close",
        "generated_at": pd.Timestamp.now().isoformat(timespec="seconds"),
        "n_stocks": int(live.ticker.nunique()),
        "n_train_rows": int(len(train)),
        "train_through": str(train.date.max().date()),
        "tickers_no_longer_trading": gone,
        "source": "Yahoo Finance via yfinance, split- and dividend-adjusted",
    }, indent=2))

    print(f"\nforecast for the session after {last_day.date()} - {len(out)} stocks")
    print(f"predicted return: mean {out.pred_ret_bp.mean():+.2f} bp, "
          f"sd {out.pred_ret_bp.std():.2f} bp, "
          f"range {out.pred_ret_bp.min():+.1f} .. {out.pred_ret_bp.max():+.1f}")
    top = out.nlargest(5, "pred_ret_bp")[["ticker", "close", "pred_ret_bp", "pred_close"]]
    bot = out.nsmallest(5, "pred_ret_bp")[["ticker", "close", "pred_ret_bp", "pred_close"]]
    print("\nmost positive:\n", top.to_string(index=False))
    print("\nmost negative:\n", bot.to_string(index=False))


if __name__ == "__main__":
    main()

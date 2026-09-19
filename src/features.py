"""Technical, volatility, volume and market-context features plus next-day targets.

Every feature for (stock, day t) uses only prices and volumes up to and including day t's
close. The targets are the NEXT trading day's log return and close price.

Features are computed on wide (date x ticker) tables, then stacked to one row per
stock-day. Each feature belongs to one family, used to group explanations.

    python src/features.py
"""
import numpy as np
import pandas as pd

from config import FEATURE_FILE, PANEL_FILE, TRAIN_START

FAMILIES = {
    "Past returns": ["ret_1d", "ret_2d", "ret_5d", "ret_10d", "ret_20d", "ret_60d"],
    "Trend": ["dist_sma5", "dist_sma20", "dist_sma50", "dist_sma200", "macd_hist"],
    "Oscillators": ["rsi_14", "stoch_k14", "bb_pctb20"],
    "Volatility": ["vol_5d", "vol_20d", "vol_60d", "atr_14", "range_1d", "bb_width20"],
    "Volume": ["volume_ratio_20d", "volume_trend_5_20", "dollar_volume_log"],
    "Candle": ["gap_open", "body_1d", "close_pos_range"],
    "Market & sector": ["mkt_ret_1d", "mkt_ret_5d", "mkt_vol_20d", "sector_ret_5d", "rel_ret_20d", "beta_60d"],
}
FEATURES = [f for fam in FAMILIES.values() for f in fam]
FAMILY_OF = {f: fam for fam, feats in FAMILIES.items() for f in feats}


def rsi(close, n=14):
    delta = close.diff()
    up = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    down = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    return 100 - 100 / (1 + up / down.replace(0, np.nan))


def build(panel):
    wide = {c: panel.pivot(index="date", columns="ticker", values=c) for c in ("open", "high", "low", "close", "volume")}
    o, h, l, c, v = (wide[k] for k in ("open", "high", "low", "close", "volume"))
    logc = np.log(c)
    r1 = logc.diff()
    f = {}

    for n in (1, 2, 5, 10, 20, 60):
        f[f"ret_{n}d"] = logc.diff(n)
    for n in (5, 20, 50, 200):
        f[f"dist_sma{n}"] = c / c.rolling(n, min_periods=n).mean() - 1
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    f["macd_hist"] = (macd - macd.ewm(span=9, adjust=False).mean()) / c

    f["rsi_14"] = rsi(c)
    low14, high14 = l.rolling(14).min(), h.rolling(14).max()
    f["stoch_k14"] = (c - low14) / (high14 - low14).replace(0, np.nan)
    mid, sd = c.rolling(20).mean(), c.rolling(20).std()
    f["bb_pctb20"] = (c - (mid - 2 * sd)) / (4 * sd).replace(0, np.nan)

    for n in (5, 20, 60):
        f[f"vol_{n}d"] = r1.rolling(n, min_periods=n).std()
    prev_c = c.shift(1)
    tr = pd.concat([h - l, (h - prev_c).abs(), (l - prev_c).abs()]).groupby(level=0).max()
    f["atr_14"] = tr.rolling(14).mean() / c
    f["range_1d"] = np.log(h / l)
    f["bb_width20"] = 4 * sd / mid

    logv = np.log(v.clip(lower=1))
    f["volume_ratio_20d"] = logv - logv.rolling(20).mean()
    f["volume_trend_5_20"] = logv.rolling(5).mean() - logv.rolling(20).mean()
    f["dollar_volume_log"] = np.log((c * v).rolling(20).mean().clip(lower=1))

    f["gap_open"] = np.log(o / prev_c)
    f["body_1d"] = np.log(c / o)
    f["close_pos_range"] = (c - l) / (h - l).replace(0, np.nan)

    mkt = r1.mean(axis=1)                                      # equal-weighted market return
    f["mkt_ret_1d"] = pd.DataFrame(np.repeat(mkt.values[:, None], c.shape[1], 1), index=c.index, columns=c.columns)
    f["mkt_ret_5d"] = f["mkt_ret_1d"].rolling(5).sum()
    f["mkt_vol_20d"] = f["mkt_ret_1d"].rolling(20).std()
    sector = panel.drop_duplicates("ticker").set_index("ticker")["sector"].reindex(c.columns)
    r5 = f["ret_5d"]
    f["sector_ret_5d"] = r5.T.groupby(sector).transform("mean").T
    f["rel_ret_20d"] = f["ret_20d"] - f["mkt_ret_1d"].rolling(20).sum()
    mkt_s = pd.Series(mkt)
    cov = r1.rolling(60, min_periods=60).cov(mkt_s)
    f["beta_60d"] = cov.div(mkt_s.rolling(60, min_periods=60).var(), axis=0)

    # Targets: next trading day's log return and close price.
    next_ret = logc.shift(-1) - logc
    next_close = c.shift(-1)

    stacked = {name: df.stack(future_stack=True) for name, df in f.items()}
    out = pd.DataFrame(stacked)
    out["close"] = c.stack(future_stack=True)
    out["target_ret"] = next_ret.stack(future_stack=True)
    out["target_close"] = next_close.stack(future_stack=True)
    out["target_up"] = (out["target_ret"] > 0).astype("int8")
    out = out.rename_axis(["date", "ticker"]).reset_index()
    out["sector"] = out["ticker"].map(sector)
    return out


def main():
    panel = pd.read_pickle(PANEL_FILE)
    df = build(panel)
    n_all = len(df)
    df = df[df["date"] >= TRAIN_START]
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=FEATURES + ["target_ret", "target_close", "close"])
    for col in FEATURES:
        df[col] = df[col].astype("float32")
    df = df.sort_values(["date", "ticker"]).reset_index(drop=True)
    df.to_pickle(FEATURE_FILE)
    print(f"{len(FEATURES)} features in {len(FAMILIES)} families; {len(df):,} usable stock-days of {n_all:,} "
          f"({df.date.min().date()} -> {df.date.max().date()}, {df.ticker.nunique()} stocks)")
    print(f"share of up days: {df.target_up.mean():.3f}")


if __name__ == "__main__":
    main()

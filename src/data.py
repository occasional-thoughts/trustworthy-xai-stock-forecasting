"""Load the raw S&P 500 panel, fix its known data issues, and save one clean long table.

Issues found in the raw file (see README, "Data cleaning"):
  1. adjclose is NaN before a stock was listed           -> those rows are dropped
  2. 15 tickers store open/high/low already dividend-adjusted but close unadjusted, so
     high/low do not bracket close                        -> put OHLC on one adjusted basis
  3. GOOG before 2014-03-27 is a different, unadjusted share-class series (a -300% jump)
                                                           -> dropped
Output columns: ticker, date, sector, open, high, low, close (all adjusted), volume.

    python src/data.py
"""
import numpy as np
import pandas as pd

from config import PANEL_FILE, RAW_FILE, SECTOR_FILE


def main():
    raw = np.load(RAW_FILE, allow_pickle=True).item()
    sectors = pd.read_csv(SECTOR_FILE).set_index("Symbol")["Sector"]
    frames, fixed = [], []
    for ticker, df in raw.items():
        df = df.copy()
        df.index = pd.to_datetime(df.index)
        df = df[df["adjclose"].notna()]
        if ticker == "GOOG":
            df = df[df.index >= "2014-03-27"]
        factor = df["adjclose"] / df["close"]
        # Which convention are open/high/low stored in? Pick the one under which the adjusted
        # close lies inside the adjusted day range most often.
        ohl_raw = ((df["low"] * factor <= df["adjclose"] * 1.0001) & (df["adjclose"] <= df["high"] * factor * 1.0001)).mean()
        ohl_adj = ((df["low"] <= df["adjclose"] * 1.0001) & (df["adjclose"] <= df["high"] * 1.0001)).mean()
        scale = factor if ohl_raw >= ohl_adj else 1.0
        if ohl_adj > ohl_raw:
            fixed.append(ticker)
        out = pd.DataFrame({
            "open": df["open"] * scale, "high": df["high"] * scale, "low": df["low"] * scale,
            "close": df["adjclose"], "volume": df["volume"],
        }, index=df.index)
        # Guard remaining rounding noise so high >= max(open, close) and low <= min(open, close).
        out["high"] = out[["high", "open", "close"]].max(axis=1)
        out["low"] = out[["low", "open", "close"]].min(axis=1)
        out["ticker"] = ticker
        out["sector"] = sectors.get(ticker, "Unknown")
        frames.append(out)
    panel = pd.concat(frames).rename_axis("date").reset_index()
    panel = panel[["ticker", "date", "sector", "open", "high", "low", "close", "volume"]]
    panel = panel.sort_values(["date", "ticker"]).reset_index(drop=True)
    PANEL_FILE.parent.mkdir(exist_ok=True)
    panel.to_pickle(PANEL_FILE)

    print(f"{panel.ticker.nunique()} tickers, {panel.date.nunique()} dates, {len(panel):,} rows "
          f"({panel.date.min().date()} -> {panel.date.max().date()})")
    print(f"open/high/low already adjusted, re-based: {len(fixed)} tickers {fixed}")
    print("sectors:", panel.groupby("sector").ticker.nunique().to_dict())


if __name__ == "__main__":
    main()

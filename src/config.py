"""Paths, periods, market regimes and feature families shared by every script."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"
MODELS = ROOT / "models"

RAW_FILE = DATA / "baseline_data_sp500.npy"   # 474 S&P 500 stocks, daily OHLCV, 2012-05-14 .. 2022-05-25
SECTOR_FILE = DATA / "sp500_ticker.csv"       # GICS sector per ticker
PANEL_FILE = DATA / "panel_clean.pkl"
FEATURE_FILE = DATA / "features.pkl"

# Chronological design. Hyperparameters are chosen on VALIDATION with a model trained on
# TRAIN; the test period is then forecast walk-forward, retraining at the start of every
# test year on all data before that year.
TRAIN_START = "2013-03-01"     # first date with a full 200-day feature history
VALID_START = "2018-01-01"
TEST_START = "2019-01-01"
TEST_YEARS = [2019, 2020, 2021, 2022]

# Market regimes in the test period, fixed from well-known events before looking at any
# explanation (the S&P 500 peaked on 2020-02-19 and bottomed on 2020-03-23).
REGIMES = {
    "Pre-COVID bull": ("2019-01-01", "2020-02-19"),
    "COVID crash": ("2020-02-20", "2020-03-23"),
    "Recovery": ("2020-03-24", "2021-12-31"),
    "2022 bear": ("2022-01-01", "2022-12-31"),
}

SEED = 42

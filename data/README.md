# Data

The raw dataset is not committed (88 MB). It is the public S&P 500 benchmark released with
ESTIMATE (Huynh et al., WSDM 2023).

**To obtain it**

1. Download `baseline_data_sp500.npy` and `sp500_ticker.csv` from
   https://github.com/thanhtrunghuynh93/estimate (`src/data/US/sp500/`).
2. Place both files in this folder.
3. Rebuild the derived files:

```bash
cd src
../.venv/bin/python data.py      # -> data/panel_clean.pkl
../.venv/bin/python features.py  # -> data/features.pkl
```

**Contents:** daily open, high, low, close, adjusted close and volume for 474 S&P 500
constituents, 14 May 2012 – 25 May 2022, plus each stock's GICS sector.

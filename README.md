# Trustworthy Explanations for Random-Forest Stock Price Forecasting

A Random Forest forecasts the next-day closing price of 474 S&P 500 stocks. SHAP explains
every forecast, and the project then tests whether those explanations can be trusted.
The full write-up (problem statement, tech stack, literature review, research gap, method, results) is in
**[REPORT.md](REPORT.md)**; the 5-paper literature review is also in [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md).

## Pipeline

| Step | Script | Output |
|---|---|---|
| 1. Clean the raw panel | `src/data.py` | `data/panel_clean.pkl` |
| 2. Build 32 features + next-day targets | `src/features.py` | `data/features.pkl` |
| 3. Tune RF on validation years 2017–2018 | `src/tune.py` | `results/tuning.json` |
| 4. Walk-forward training, 2019 → May 2022 | `src/train.py` | `results/predictions.pkl`, `models/` |
| 5. Accuracy vs baselines + significance tests | `src/evaluate.py` | `results/metrics.json` |
| 6. SHAP explanations + reliability checks | `src/explain.py` | `results/xai.json`, `results/importance.csv`, `results/shap_sample.pkl` |
| 7. LIME explanations + SHAP-vs-LIME checks | `src/lime_explain.py` | `results/lime.json`, `results/lime_sample.pkl` |
| 8. Figures | `src/plots.py` | `results/figures/*.png` |

## Setup and run

```bash
python3.11 -m venv .venv
.venv/bin/pip install "numpy<2.2" pandas scikit-learn shap lime matplotlib scipy
```

```bash
cd src
../.venv/bin/python data.py
../.venv/bin/python features.py
../.venv/bin/python tune.py
../.venv/bin/python train.py
../.venv/bin/python evaluate.py
../.venv/bin/python explain.py
../.venv/bin/python lime_explain.py
../.venv/bin/python plots.py
```

On an Apple M3 Pro the whole pipeline takes about 25 minutes (training about 10, tuning
about 5, explanations about 7).

## Data

* **Source:** daily open, high, low, close, adjusted close and volume for 474 S&P 500
  constituents, 14 May 2012 – 25 May 2022, plus each stock's GICS sector. It is the public
  S&P 500 benchmark released with ESTIMATE (Huynh et al., WSDM 2023,
  [github.com/thanhtrunghuynh93/estimate](https://github.com/thanhtrunghuynh93/estimate))
  and reused by StockMixer (AAAI 2024).
* **Files:** `data/baseline_data_sp500.npy` (a pickled dict of per-ticker DataFrames) and
  `data/sp500_ticker.csv`.
* **Coverage:** 11 GICS sectors (21–67 stocks each). The period includes the COVID-19
  crash and the 2022 bear market.

### Data cleaning (`src/data.py`)

| Issue found | Rows affected | Fix |
|---|---|---|
| Adjusted close missing before a stock was listed (e.g. PAYC, HLT) | 3,450 | Rows dropped |
| For 12 tickers, open/high/low are already dividend-adjusted but close is not, so high/low don't bracket the close | ~27,000 | Convention detected per ticker; OHLC put on one adjusted basis |
| GOOG before 2014-03-27 is a different, unadjusted share-class series (a −300% jump) | 470 | Dropped |

Real extreme moves are kept, such as the 9 March 2020 oil crash (APA −54%, OXY −51%).

## Design

* **Target:** the next-day close price. The RF predicts the next-day log return *r̂*, and
  the price forecast is close × exp(*r̂*). Predicting returns rather than price levels
  avoids a tree model's inability to extrapolate to new price highs.
* **Features:** 32, all computed from data up to day *t*'s close, in 7 families:
  * past returns;
  * trend (distance from moving averages, MACD);
  * oscillators (RSI, stochastic, Bollinger %B);
  * volatility (realised volatility, ATR, day range, Bollinger width);
  * volume;
  * candle (overnight gap, day body, close position in the day's range);
  * market & sector (equal-weighted market return and volatility, sector return,
    relative strength, 60-day beta).
* **Splits:**
  * **Tuning:** hyperparameters chosen by validation MSE, averaged over 2017 and 2018,
    each validated with a model trained on earlier data.
  * **Test:** walk-forward over 2019, 2020, 2021 and 2022 (Jan–May), retraining each
    January on all earlier data. The test period is never used for any design choice.
* **Baselines:**
  * naive persistence (tomorrow = today);
  * historical drift;
  * Ridge regression on the same features;
  * a Random Forest on raw price levels (the common approach in the literature);
  * a Random Forest classifier for up/down direction.
* **Regimes (fixed from known market events before the analysis):**
  * Pre-COVID bull: 2019-01-01 → 2020-02-19
  * COVID crash: 2020-02-20 → 2020-03-23
  * Recovery: 2020-03-24 → 2021-12-31
  * 2022 bear: 2022-01-01 → 2022-05-24

## Key results

Test set: 405,545 stock-days, Jan 2019 – May 2022. Details in [REPORT.md](REPORT.md) §6.

| | Result |
|---|---|
| **Price accuracy** (RF) | MAPE 1.56% (98.44% "price accuracy"), RMSE $6.25, R² 0.9994, 75% of forecasts within 2% |
| **Versus naive "tomorrow = today"** | Identical accuracy; difference not significant (Diebold–Mariano p = 0.30) |
| **RF on raw price levels** | R² 0.993 but RMSE $21.56, significantly worse than naive (p < 0.001) |
| **Direction accuracy** | 51.8%, below the "always predict the majority direction" rule (52.8%) |
| **What drives forecasts** (SHAP) | 72% market & sector context (market volatility, 5-day and 1-day market return) |
| **Faithfulness** | Removing the top-SHAP feature moves the forecast 13× more than a random one; fidelity r ≥ 0.98 |
| **Seed stability** | Kendall τ 0.85 |
| **Retraining stability** | τ 0.44–0.77; lowest after COVID was added |
| **Explainer agreement** | SHAP vs MDI τ 0.69; SHAP vs permutation τ 0.03 (only 4 of 32 features improve accuracy) |
| **Regime drift** | Significant, p = 0.003 (volatility share 5% in 2019 → 9% in 2022 bear) |
| **Sector drift** | Significant, p = 0.001 |
| **LIME vs SHAP** | Globally agree (τ 0.73); per forecast LIME is unstable across runs (ρ 0.48), fits poorly (median R² 0.17), matches SHAP's top-5 only 66% |
| **Sanity check** | No-signal model: τ 0.13, 8× weaker explanations. Market-timing-only model: τ 0.56. Explanations are mostly about market-wide timing |

## Figures (`results/figures/`)

| File | Shows |
|---|---|
| `price_accuracy.png` | Error and within-2% rate for every model |
| `price_paths_AAPL.png` | AAPL forecasts vs actual prices |
| `shap_global.png` | Top 15 features by mean \|SHAP\| |
| `explainer_agreement.png` | Feature ranks from TreeSHAP, permutation and MDI |
| `shap_dependence.png` | How the top features move the forecast |
| `local_explanations.png` | Dollar contributions for individual stock-days |
| `regime_family_shares.png` | Feature-family shares across market regimes |
| `sector_family_shares.png` | Feature-family shares across GICS sectors |
| `faithfulness.png` | Deletion curves: top-SHAP vs random |
| `stability_sanity.png` | Seed, retraining and no-signal comparisons |
| `lime_vs_shap_local.png` | SHAP vs LIME explanations for the same forecasts |
| `lime_reliability.png` | LIME stability, faithfulness and fit vs SHAP |

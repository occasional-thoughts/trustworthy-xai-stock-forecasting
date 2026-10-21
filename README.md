# Trustworthy Explanations for Random-Forest Stock Return Forecasting

A Random Forest forecasts the **next-day return** of 474 S&P 500 stocks (the price forecast is
that return applied to today's close). SHAP and LIME explain every forecast, and the project
then tests whether those explanations can be trusted.

The full write-up (problem statement, tech stack, literature review, research gap, method,
results) is in **[REPORT.md](REPORT.md)**; the objective, model specification and system
requirements are in **[OBJECTIVE_MODEL_REQUIREMENTS.md](OBJECTIVE_MODEL_REQUIREMENTS.md)**;
the 5-paper literature review is also in [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md).

**The headline result in one line:** one set of forecasts scores **R² 0.9994 on the price
level and +0.00013 on the return**. Only the second number says anything about the model.

## Pipeline

| Step | Script | Output |
|---|---|---|
| 1. Clean the raw panel | `src/data.py` | `data/panel_clean.pkl` |
| 2. Build 32 features + next-day targets | `src/features.py` | `data/features.pkl` |
| 3. Tune RF on validation years 2017–2018 | `src/tune.py` | `results/tuning.json` |
| 4. Walk-forward training, 2019 → May 2022 | `src/train.py` | `results/predictions.pkl`, `models/` |
| 5. Return-space skill and price-space accuracy vs baselines, with significance tests | `src/evaluate.py` | `results/metrics.json` |
| 6. SHAP explanations + reliability checks | `src/explain.py` | `results/xai.json`, `results/importance.csv`, `results/shap_sample.pkl` |
| 7. LIME explanations + SHAP-vs-LIME checks | `src/lime_explain.py` | `results/lime.json`, `results/lime_sample.pkl` |
| 8. Figures | `src/plots.py` | `results/figures/*.png` |
| 9. Markdown → Word | `src/make_docx.py [file.md]` | `REPORT.docx`, `OBJECTIVE_MODEL_REQUIREMENTS.docx` |
| 10. Slide deck | `src/make_slides.js` | `LIT_REVIEW_SLIDES.pptx` (needs `pptxgenjs`) |
| 11. Next-session forecast | `src/live.py` | `results/live_forecast.pkl`, `models/rf_reg_live.joblib` |
| 12. Interactive demo | `src/app.py` | a local page at `http://127.0.0.1:8000` |

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

## Interactive demo

```bash
.venv/bin/python src/app.py
```

Opens a local page where you pick one stock and one trading day. It then runs the saved model
for that stock-day and shows:

* the forecast next-day return, the price it implies, and what actually happened;
* the TreeSHAP and LIME explanations of that same forecast, side by side on one scale;
* whether the two explanations agree (rank correlation, shared top-5, same top feature,
  sign agreement);
* whether LIME says the same thing twice, by re-running it five times on identical input;
* whether the explanation is faithful, by blanking out the feature SHAP ranked first and
  comparing the effect against blanking out random features.

Everything is computed live from `models/*.joblib` — about 0.7 s per stock-day — so the page
shows what the pipeline produces rather than a cached result. Requires `data/features.pkl` and
`models/`, both of which are rebuilt by steps 1–4 above.

Five preset cases are offered, including `BAC 2019-02-28`, where SHAP and LIME name different
top features. On 28 randomly sampled stock-days they disagreed on the top feature on 11.

### Forecasting a day that has not happened

The walk-forward test scores days whose outcome is already known, because that is the only way
to measure accuracy. `src/live.py` does the other half:

```bash
.venv/bin/python src/live.py          # ~2 min: download, retrain, forecast
```

It downloads the universe from Yahoo Finance, rebuilds the same 32 features, retrains with the
same hyperparameters on everything up to the most recent close, and forecasts the next session.
The demo page then offers it as a second mode, where "what happened" is honestly blank.

Three things to state when showing it:

* **431 of the original 474 stocks still trade.** The other 43 were acquired, merged or
  delisted — survivorship bias made visible rather than described.
* **Prices come from Yahoo Finance**, not the benchmark panel used for the study. Both are
  split- and dividend-adjusted, but they are different vendors.
* **Nothing here is scored, and the backtest says not to expect much.** Across 405,545 scored
  forecasts the model's return R² was +0.00013, so a single live forecast is a demonstration of
  the mechanism, not evidence about tomorrow.

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

* **Target:** the next-day **log return** *r̂*. The price forecast, close × exp(*r̂*), is a
  derived quantity and never the training target. Predicting returns rather than price levels
  keeps every stock on one scale, avoids a tree's inability to extrapolate to new price highs,
  and — most importantly — is the only space in which a score means anything, since price-level
  R² is ≈ 0.999 for any method whatsoever.
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
| **Return skill** (RF, primary) | Out-of-sample R² **+0.00013** vs predicting zero change (DM p = 0.97); daily IC +0.009 (t = 1.39); RMSE 246 bp against a realised 245 bp |
| **Forecast dispersion** | sd 10.8 bp vs realised 245 bp — the model hedges to near-zero, a range 23× narrower than reality |
| **Direction accuracy** | 51.8%, below the "always predict the majority direction" rule (52.8%) |
| **Economic value** | Decile ranking weakly monotone (ρ 0.75); long-short +8.2 bp/day (t = 1.53, Sharpe 0.83); **−1.8 bp/day after a 10 bp cost** |
| **Where the skill lives** | Significant only in the 2020–21 recovery (R² +0.0067, DM p = 0.043); inverted in the COVID crash (IC −0.073, direction 34.7%, −119 bp/day) |
| **Price accuracy** (RF, secondary) | MAPE 1.56% (98.44% "price accuracy"), RMSE $6.25, R² 0.9994, 75% within 2% — matched exactly by naive persistence (DM p = 0.30) |
| **RF on raw price levels** | R² 0.993 but RMSE $21.56, and significantly worse than naive in both spaces (p < 0.001) |
| **What drives forecasts** (SHAP) | 72% market & sector context (market volatility, 5-day and 1-day market return) |
| **Faithfulness** | Removing the top-SHAP feature moves the forecast 13× more than a random one; fidelity r ≥ 0.98 |
| **Seed stability** | Kendall τ 0.85 |
| **Retraining stability** | τ 0.44–0.77; lowest after COVID was added |
| **Explainer agreement** | SHAP vs MDI τ 0.69; SHAP vs permutation τ 0.03 (only 4 of 32 features improve accuracy) |
| **Regime drift** | Significant, p = 0.003 (volatility share 5% in 2019 → 9% in 2022 bear) |
| **Sector drift** | Significant, p = 0.001 |
| **LIME vs SHAP** | Agree only moderately even globally (τ 0.58); per forecast LIME is unstable across runs (ρ 0.45), fits poorly (median R² 0.17), and names a different top feature 41% of the time |
| **Sanity check** | No-signal model: τ 0.13, 8× weaker explanations. Market-timing-only model: τ 0.56. Explanations are mostly about market-wide timing |

## Figures (`results/figures/`)

| File | Shows |
|---|---|
| `return_skill.png` | Return-space R² and direction accuracy for every model |
| `price_vs_return.png` | The same forecasts scored both ways, and how narrowly they move |
| `decile_portfolio.png` | Actual return of each decile of predicted return, gross and net of cost |
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

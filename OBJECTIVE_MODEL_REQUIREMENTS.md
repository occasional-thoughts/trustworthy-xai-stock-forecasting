# Objective, Proposed Model and Requirements

*Trustworthy Explanations for Random-Forest Stock Return Forecasting — 474 S&P 500 stocks, 2013–2022*

---

## 1. Objective

### 1.1 Objective statement

> To build a leakage-free Random Forest that forecasts the **next-day return** of 474 S&P 500
> stocks, to measure its skill in return space against naive and learned baselines with formal
> significance tests, to explain every forecast with SHAP and LIME, and to determine whether
> those explanations are **trustworthy** — that is, faithful to the model, stable across random
> seeds and retraining, consistent with each other and with other importance measures, different
> from the explanations of a model with no real signal, and stable across market regimes and
> sectors.

### 1.2 Specific objectives

| # | Objective | How it is met | Deliverable |
|---|---|---|---|
| **O1** | Build a leakage-free, walk-forward next-day **return** forecaster for 474 stocks | 32 features computed only from data up to day *t*'s close; retrained each January on all prior data; the 2019–2022 test window is never used for any design choice | `src/features.py`, `src/train.py`, `results/predictions.pkl` |
| **O2** | Measure skill in the units the model predicts in, not in price units | Out-of-sample R² against a zero-return and a drift forecast, IC, Rank IC, ICIR, direction accuracy, decile portfolio net of cost; Diebold–Mariano and binomial tests | `src/evaluate.py`, `results/metrics.json` |
| **O3** | Demonstrate why price-level accuracy misleads | The same forecasts scored both ways, plus a Random Forest deliberately trained on raw price levels as a negative control | §7.1.2 of the report, `price_vs_return.png` |
| **O4** | Explain every forecast | TreeSHAP on 38,183 stock-days; LIME on 804 stock-days × 5 seeds; permutation importance and MDI as comparison explainers | `src/explain.py`, `src/lime_explain.py` |
| **O5** | Audit the explanations for reliability | Faithfulness (deletion curves, AOPC, fidelity), stability (5 seeds, yearly retrains), explainer agreement (Kendall τ), sanity (two shuffled-label null models) | `results/xai.json`, `results/lime.json` |
| **O6** | Test explanation drift formally | Permutation tests (1,000 permutations) on feature-family SHAP shares across 4 market regimes and 11 GICS sectors | `results/xai.json`, §7.4 |
| **O7** | Produce a submittable write-up | Report, literature review of 5 recent papers with gaps, 15 figures, slide deck, public repository | `REPORT.docx`, `LIT_REVIEW_HANDOUT.docx`, `LIT_REVIEW_SLIDES.pptx` |
| **O8** | Make the audit inspectable one forecast at a time | A local page that takes a stock and a day, runs the model, TreeSHAP and five LIME re-runs live, and reports agreement, stability and faithfulness for that single forecast | `src/app.py`, `src/static/index.html` |
| **O9** | Forecast a session whose outcome does not exist yet | Download the universe from Yahoo Finance, rebuild the same features, retrain on everything up to the latest close, forecast the next session | `src/live.py`, `results/live_forecast.pkl` |

### 1.3 Why returns and not raw prices

| | Price-level target | Return target (used here) |
|---|---|---|
| What is predicted | *P*ₜ₊₁ in dollars | *r*ₜ₊₁ = ln(*P*ₜ₊₁ / *P*ₜ) |
| Comparable across stocks? | No — a $10 stock and a $3,000 stock are on different scales | Yes — returns are scale-free |
| Can a tree extrapolate? | **No.** A tree can only output values seen in training, so it fails whenever a stock makes a new high | Not required — returns stay in the same range forever |
| Does the score mean anything? | R² ≈ 0.999 for *any* method, because tomorrow's price ≈ today's | R² ≈ 0 unless the model genuinely predicts the change |
| Measured here | RF on price levels: R² 0.993 but RMSE $21.56, **significantly worse than naive** (p < 0.001) | RF on returns: R² +0.00013, RMSE $6.25, tied with naive |

---

## 2. Proposed model

### 2.1 System architecture

```
          ┌────────────────────────────────────────────────────────────┐
          │  STAGE 1 — DATA                                            │
          │  474 S&P 500 stocks · daily OHLCV · 14 May 2012–25 May 2022│
          │  cleaning: adjustment-convention repair, pre-listing NaNs, │
          │  GOOG share-class break            →  data/panel_clean.pkl │
          └───────────────────────────┬────────────────────────────────┘
                                      ▼
          ┌────────────────────────────────────────────────────────────┐
          │  STAGE 2 — FEATURE ENGINEERING                             │
          │  32 features in 7 families, each using only data up to     │
          │  day t's close:  past returns · trend · oscillators ·      │
          │  volatility · volume · candle · market & sector            │
          │  target  r(t+1) = ln(P(t+1)/P(t))   →  data/features.pkl   │
          └───────────────────────────┬────────────────────────────────┘
                                      ▼
          ┌────────────────────────────────────────────────────────────┐
          │  STAGE 3 — MODEL (walk-forward, retrained every January)   │
          │                                                            │
          │   x(i,t) ∈ R³² ──►  Random Forest regressor  ──►  r̂(i,t+1) │
          │                     300 trees · min_samples_leaf 5000      │
          │                     max_features 0.3 · max_samples 0.25    │
          │                                                            │
          │   price reconstruction:  P̂(i,t+1) = P(i,t) · exp(r̂(i,t+1)) │
          │                                                            │
          │   baselines trained alongside: naive · drift · Ridge ·     │
          │   RF-on-price-levels (negative control) · RF classifier    │
          └───────────────────────────┬────────────────────────────────┘
                                      ▼
       ┌──────────────────────────────┴───────────────────────────────┐
       ▼                                                              ▼
┌──────────────────────────────┐              ┌──────────────────────────────────┐
│  STAGE 4a — EVALUATION       │              │  STAGE 4b — EXPLANATION          │
│  return space (primary):     │              │  TreeSHAP  φ(i,t) ∈ R³²          │
│    R² vs zero / vs drift,    │              │    38,183 stock-days, exact      │
│    IC, Rank IC, ICIR,        │              │  LIME  λ(i,t) ∈ R³²              │
│    direction, deciles, cost  │              │    804 stock-days × 5 seeds      │
│  price space (secondary):    │              │  permutation importance, MDI     │
│    MAE, RMSE, MAPE, R²       │              │                                  │
│  tests: Diebold–Mariano,     │              │                                  │
│         binomial             │              │                                  │
└──────────────────────────────┘              └──────────────┬───────────────────┘
                                                             ▼
                              ┌──────────────────────────────────────────────────┐
                              │  STAGE 5 — RELIABILITY AUDIT  (the contribution) │
                              │  R1 Faithfulness — deletion curves, AOPC,        │
                              │     fidelity vs a random-order control           │
                              │  R2 Stability — 5 seeds; consecutive retrains    │
                              │  R3 Agreement — Kendall τ across 4 explainers    │
                              │  R4 Sanity — vs fully-shuffled and               │
                              │     within-day-shuffled label models             │
                              │  R5 Drift — 1,000-permutation tests across       │
                              │     4 regimes and 11 sectors                     │
                              └──────────────────────────┬───────────────────────┘
                                                         ▼
       ┌─────────────────────────────────────────────────────────────────────────┐
       │  STAGE 6 — USE                                                          │
       │                                                                         │
       │  src/app.py     one stock + one day  ──►  forecast, TreeSHAP, 5 LIME    │
       │                 runs, agreement, stability, faithfulness   (~0.7 s)     │
       │                 past day   → outcome known, forecast is scored          │
       │                 next day   → outcome blank, nothing to score            │
       │                                                                         │
       │  src/live.py    Yahoo Finance ──► same 32 features ──► retrain on       │
       │                 everything to the latest close ──► forecast the next    │
       │                 session for the 431 tickers that still trade            │
       └─────────────────────────────────────────────────────────────────────────┘
```

**The two halves of Stage 6 answer different questions.** A forecast of a past day can be
graded, which is how accuracy is measured at all; a forecast of the next session cannot be
graded yet, which is what a deployed model actually does. The same model, features and
explainers serve both.

### 2.2 Formal specification

| Element | Specification |
|---|---|
| **Universe** | *N* = 474 S&P 500 stocks, indexed *i*; trading days indexed *t* |
| **Input** | **x**ᵢ,ₜ ∈ ℝ³², computed only from prices and volumes up to day *t*'s close |
| **Target** | *r*ᵢ,ₜ₊₁ = ln(*P*ᵢ,ₜ₊₁ / *P*ᵢ,ₜ), the next-day log return |
| **Model** | *r̂*ᵢ,ₜ₊₁ = *f*(**x**ᵢ,ₜ), *f* = Random Forest regressor (bagged CART, mean aggregation) |
| **Price output** | *P̂*ᵢ,ₜ₊₁ = *P*ᵢ,ₜ · exp(*r̂*ᵢ,ₜ₊₁) — a derived quantity, never the training target |
| **Explanation** | **φ**ᵢ,ₜ ∈ ℝ³² (TreeSHAP, exact, additive: base + Σφ = *r̂*) and **λ**ᵢ,ₜ ∈ ℝ³² (LIME surrogate weights) |
| **Loss** | Mean squared error on *r* |
| **Selection** | Hyperparameters by validation MSE averaged over 2017 and 2018 only |

### 2.3 Chosen hyperparameters

| Parameter | Value | Chosen how |
|---|---|---|
| `n_estimators` | 300 | fixed |
| `max_samples` | 0.25 | fixed (bootstrap fraction, for runtime) |
| `min_samples_leaf` | **5000** | tuned over {200, 1000, 5000} |
| `max_features` | **0.3** | tuned over {0.3, 0.6} |
| `random_state` | 42 | fixed for reproducibility |

The most heavily regularised option in the grid won on validation. That is itself a result:
it is what a low signal-to-noise problem looks like.

### 2.4 Training and testing protocol

| Phase | Period | Use |
|---|---|---|
| Training pool | 2013-03-01 onwards (first date with a full 200-day feature history) | model fitting |
| Validation | 2017, 2018 | hyperparameter selection only |
| **Walk-forward test** | **2019, 2020, 2021, 2022 (Jan–May)** | retrain each January on everything before it, then forecast every stock-day of that year |
| Test size | **405,545 stock-days over 856 trading days** | never used for any design decision |

### 2.5 Market regimes (fixed in advance from known events)

| Regime | Window |
|---|---|
| Pre-COVID bull | 2019-01-01 → 2020-02-19 |
| COVID crash | 2020-02-20 → 2020-03-23 |
| Recovery | 2020-03-24 → 2021-12-31 |
| 2022 bear | 2022-01-01 → 2022-05-24 |

### 2.6 Evaluation metrics

| Space | Metric | Benchmark it is read against |
|---|---|---|
| **Return (primary)** | RMSE and MAE in basis points | realised return sd, 245 bp |
| | Out-of-sample R² | a zero-return forecast, and the historical drift |
| | Daily IC, Rank IC, ICIR | zero |
| | Direction accuracy | the majority-direction rule, 52.8% |
| | Decile spread, Sharpe, net of 10 bp cost | zero |
| **Price (secondary)** | MAE, RMSE, MAPE, R², within 1% / 2% | naive persistence |
| **Tests** | Diebold–Mariano (Newey–West, 5 lags) | model vs benchmark, both spaces |
| | Binomial test | direction vs majority rule |
| | Permutation test (1,000 draws) | explanation drift across regimes and sectors |

---

## 3. Requirements

### 3.1 Functional requirements

| # | Requirement |
|---|---|
| FR1 | The system shall load daily OHLCV data for 474 S&P 500 stocks and repair the three known data defects (adjustment-convention mismatch, pre-listing NaNs, the GOOG share-class break) before use. |
| FR2 | The system shall compute 32 technical, volatility, volume and market-context features per stock-day, using **only** information available at or before that day's close. |
| FR3 | The system shall train a Random Forest to predict the **next-day log return**, and shall derive price forecasts from it rather than training on price levels. |
| FR4 | The system shall retrain walk-forward at the start of each test year on all prior data, and shall never use test-period data for tuning or design. |
| FR5 | The system shall produce forecasts from five comparison models: naive persistence, historical drift, Ridge regression, a price-level Random Forest and a direction classifier. |
| FR6 | The system shall report return-space skill as the primary result and price-space accuracy as a secondary, comparability result, for the whole test set and broken down by year, market regime and GICS sector. |
| FR7 | The system shall test each model against its benchmark with a Diebold–Mariano test, and direction accuracy against the majority rule with a binomial test. |
| FR8 | The system shall compute exact TreeSHAP attributions for a stratified sample of at least 35,000 stock-days, and verify SHAP additivity. |
| FR9 | The system shall compute LIME explanations for a sample of stock-days with at least 5 random seeds each, to measure run-to-run stability. |
| FR10 | The system shall test explanation **faithfulness** by deleting top-ranked features against a random-order control, reporting deletion curves, AOPC and fidelity. |
| FR11 | The system shall test explanation **stability** across random seeds and across consecutive yearly retrains, using Kendall's τ and Spearman's ρ. |
| FR12 | The system shall compare four explainers (TreeSHAP, LIME, permutation importance, MDI) and report their rank agreement. |
| FR13 | The system shall test explanation **sanity** against two null models trained on shuffled labels (fully shuffled, and shuffled within each day). |
| FR14 | The system shall test explanation **drift** across the four market regimes and the eleven GICS sectors with a 1,000-draw permutation test. |
| FR15 | The system shall emit all results as machine-readable JSON, all figures as PNG, and the write-up as Markdown and Word. |
| FR16 | The system shall provide an interactive page that accepts a stock and a trading day and returns, computed live from the saved model, the forecast, its TreeSHAP and LIME explanations, their agreement, LIME's run-to-run stability over 5 re-runs, and a faithfulness test for that single forecast. |
| FR17 | The system shall additionally forecast the next trading session: retrieving current prices, rebuilding the same features, retraining with the same hyperparameters up to the latest close, and presenting the result with its outcome fields explicitly blank. |
| FR18 | The system shall state, wherever a live forecast is shown, how many of the original 474 tickers still trade, which price vendor was used, and that the backtest found no return skill. |

### 3.2 Non-functional requirements

| # | Requirement |
|---|---|
| NFR1 | **Reproducibility.** Every stochastic component is seeded (`SEED = 42`); a full re-run must reproduce every published number. *Defect found and fixed: `LimeTabularExplainer` binds its `RandomState` into the discretiser and the surrogate solver at construction, so reassigning `.random_state` on a reused explainer left the same seed returning a different explanation on every call (Spearman 0.46–0.53 between repeats that should have been identical). A fresh explainer is now constructed per seed, at a cost of 18 ms, and repeats are bit-identical.* |
| NFR2 | **No look-ahead.** Feature construction, scaling and model selection must be verifiable as using only past information. |
| NFR3 | **Runtime.** The complete pipeline must finish in under one hour on a laptop. *(Measured: ≈ 25 min on an Apple M3 Pro — tuning 5, training 10, explanations 7, figures 1.)* |
| NFR4 | **Memory.** Must run within 16 GB RAM; the feature table is ~1.1 M stock-days × 32 float32 columns. |
| NFR5 | **Transparency of negative results.** Results that undercut the model must be reported, not suppressed. |
| NFR6 | **Auditability.** Each pipeline stage writes its own artefact, so any stage can be re-run or inspected independently. |

### 3.3 Software requirements

| Component | Version used | Purpose |
|---|---|---|
| Python | **3.11.13** | runtime |
| NumPy | 2.1.3 | arrays |
| pandas | 3.0.5 | panel and time-series handling |
| scikit-learn | 1.9.1 | `RandomForestRegressor`, `RandomForestClassifier`, `RidgeCV`, `permutation_importance` |
| SHAP | 0.51.0 | `TreeExplainer` (exact TreeSHAP) |
| LIME | 0.2.0.1 | `LimeTabularExplainer` |
| SciPy | 1.17.1 | Newey–West variance, binomial test, Spearman, Kendall |
| Matplotlib | 3.11.2 | figures |
| joblib | 1.6.0 | model persistence, parallelism |
| pandoc + python-docx | — | report → Word |
| yfinance | 1.7.0 | current prices for the next-session forecast |
| Node.js + pptxgenjs | — | slide deck |
| git + GitHub | — | version control, public release |

### 3.4 Hardware requirements

| Resource | Minimum | Used for this project |
|---|---|---|
| CPU | 4 cores | Apple M3 Pro, 12 cores (`n_jobs = -1`) |
| RAM | 16 GB | 18 GB |
| Disk | 2 GB free | 330 MB data + 4.4 MB models + 53 MB results + 600 MB virtual environment |
| GPU | none | none — Random Forests are CPU-only |
| OS | macOS, Linux or Windows | macOS 14 |

### 3.5 Data requirements

| Requirement | Detail |
|---|---|
| Source | Public S&P 500 benchmark released with ESTIMATE (Huynh et al., WSDM 2023) and reused by StockMixer (AAAI 2024) |
| Fields | Daily open, high, low, close, adjusted close, volume; plus GICS sector per ticker |
| Coverage | 474 stocks, 14 May 2012 – 25 May 2022, 11 sectors (21–67 stocks each) |
| Minimum history | 200 trading days per stock before its first usable feature row |
| Volume after cleaning | ≈ 1.1 M usable stock-days; 405,545 of them in the test window |
| Licence | Public research dataset, redistributed under its original terms |

### 3.6 Acceptance criteria

| # | Criterion | Status |
|---|---|---|
| AC1 | Walk-forward forecasts exist for every test stock-day with no look-ahead | ✅ 405,545 forecasts |
| AC2 | Return-space and price-space results are both reported, with the return space first | ✅ §7.1 |
| AC3 | Every accuracy claim is accompanied by a benchmark and a significance test | ✅ DM and binomial throughout |
| AC4 | SHAP additivity error < 1 × 10⁻¹⁵ | ✅ max 2.6 × 10⁻¹⁷ |
| AC5 | Faithfulness: top-ranked deletion moves the forecast materially more than random deletion | ✅ 13.3× at *k* = 1 |
| AC6 | Stability and sanity are both quantified | ✅ τ 0.85 across seeds; τ 0.13 vs a no-signal model |
| AC7 | Drift is tested statistically, not asserted | ✅ regimes p = 0.003, sectors p = 0.001 |
| AC8 | The pipeline reproduces from a clean checkout | ✅ 12 steps, documented in `README.md` |
| AC9 | Repeating a LIME explanation with the same seed returns identical weights | ✅ after the NFR1 fix; previously ρ 0.46–0.53 |
| AC10 | A single forecast can be explained and audited interactively | ✅ ≈ 0.7 s per stock-day, nothing served from cache |
| AC11 | A forecast exists for a session that has not traded | ✅ 431 stocks, retrained on 1,470,270 stock-days, outcome fields blank |

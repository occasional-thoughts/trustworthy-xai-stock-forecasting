# Trustworthy Explanations for Random-Forest Stock Price Forecasting

*A SHAP and LIME reliability audit on 474 S&P 500 stocks*

---

## Contents

1. Problem statement
2. Tech stack
3. Literature review
4. Research gap
5. Data
6. Methodology
7. Results
8. Discussion
9. Limitations
10. Conclusion
11. References

---

## 1. Problem statement

### 1.1 Background

* **Adoption.** Machine-learning models, Random Forests (RF) especially, are widely used to
  forecast stock prices from historical price and volume data. They are popular because
  they:
  * handle non-linear patterns;
  * need little tuning;
  * resist overfitting better than single trees.
* **Explanations.** Because these models are "black boxes", studies increasingly attach
  explainable-AI (XAI) methods, mainly **SHAP** (Shapley additive explanations) and
  **LIME** (local interpretable model-agnostic explanations). These show which inputs
  drove a forecast.
* **Why it matters.** In finance, explanations are increasingly expected by investment
  committees, risk officers and regulators before a model is allowed to inform decisions.

### 1.2 The problem

Recent studies (Section 3) share two linked weaknesses.

**Problem 1: accuracy is reported without a meaningful benchmark.**
* Price forecasts are often judged by price-level accuracy (R², "accuracy %"). When returns
  are evaluated properly, the signal is weak: Indra et al. (2025) found near-zero R² and 49–54%
  directional accuracy.
* But a stock's price tomorrow is almost the same as today. The naive forecast "tomorrow's
  price = today's price" already scores R² ≈ 0.999.
* Without comparing against that naive forecast and testing the difference, a reader can't
  tell whether a model has any real predictive skill.

**Problem 2: explanations are presented as findings, but never tested.** Studies report
SHAP or LIME outputs ("volume is the most important feature") as insight about the market.
They do not check whether those explanations are:

| Property | Question | If it fails |
|---|---|---|
| **Faithful** | Does removing the features the explanation ranks highest actually change the forecast most? | The explanation describes features the model doesn't really use |
| **Stable** | Do the explanations stay the same when the model is re-seeded or retrained? | The explanation is an artefact of one random seed or one training run |
| **Consistent across explainers** | Do SHAP, LIME and importance measures agree? | Conclusions depend on which XAI tool was picked |
| **Meaningful** | Do they differ from the explanations of a model trained on randomly shuffled labels? | The explanation reflects feature structure, not a learned relationship |
| **Context-dependent** | Do they change across market regimes (e.g. the COVID crash) and sectors? | A single "global" explanation misrepresents specific periods or sectors |

Without these tests, an explanation may describe noise, one random seed or one market
period, and misleading explanations in finance can lead to real financial losses and
misplaced trust.

### 1.3 Formal problem definition

| Element | Definition |
|---|---|
| **Universe** | *N* = 474 S&P 500 stocks, indexed by *i*; trading days indexed by *t* |
| **Input** | A feature vector **x**ᵢ,ₜ ∈ ℝ³² for stock *i* on day *t*, computed only from prices and volumes up to *t*'s close (7 families: past returns, trend, oscillators, volatility, volume, candle, market & sector) |
| **Output** | Forecast of the next-day closing price *P̂*ᵢ,ₜ₊₁ |
| **Model** | Random Forest *f* predicting the next-day log return *r̂* = *f*(**x**ᵢ,ₜ); price forecast *P̂*ᵢ,ₜ₊₁ = *P*ᵢ,ₜ · exp(*r̂*) |
| **Explanations** | A SHAP vector **φ**ᵢ,ₜ ∈ ℝ³² and a LIME weight vector **λ**ᵢ,ₜ ∈ ℝ³² for every explained forecast |
| **Evaluation** | Accuracy vs naive persistence (Diebold–Mariano test), plus a reliability audit of **φ** and **λ**: faithfulness, stability, agreement, sanity, regime and sector drift |

### 1.4 Problem statement

> **Given daily price and volume data for 474 S&P 500 stocks (2012–2022), this project
> builds a Random Forest that forecasts each stock's next-day closing price, measures its
> accuracy against naive and learned baselines with significance tests, and explains every
> forecast with SHAP and LIME. It then determines whether those explanations can be
> trusted, that is, whether they are faithful to the model, stable across random seeds and
> yearly retraining, consistent with each other and with importance-based explainers,
> different from the explanations of a model with no real signal, and consistent across
> market regimes (pre-COVID bull, COVID crash, recovery, 2022 bear) and GICS sectors.**

### 1.5 Research questions

| # | Research question |
|---|---|
| **RQ1** | How accurate is the Random Forest's next-day closing-price forecast (Jan 2019 – May 2022), and how much of that accuracy exceeds naive persistence? |
| **RQ2** | Which features and feature families drive the forecasts, globally and for individual stock-days? |
| **RQ3** | Are the SHAP explanations faithful to the model, and stable across random seeds and yearly retraining? |
| **RQ4** | Do the explanations change significantly across market regimes and GICS sectors? |
| **RQ5** | Do the explanations differ from those of models trained on shuffled (signal-free) labels? |
| **RQ6** | Do SHAP and LIME agree, and which is more stable and faithful for this model? |

### 1.6 Objectives

1. **Forecaster.** Build a leakage-free, walk-forward Random Forest next-day price
   forecaster for 474 stocks.
2. **Honest accuracy.** Benchmark it against naive persistence, historical drift, Ridge
   regression and a price-level Random Forest, with Diebold–Mariano and binomial tests.
3. **Explanations.** Explain every forecast with TreeSHAP and LIME, and compare four
   explainers (TreeSHAP, LIME, permutation importance, MDI).
4. **Reliability audit.** Test the explanations for faithfulness, stability and sanity
   against shuffled-label models.
5. **Drift tests.** Test explanation drift across regimes and sectors with permutation
   tests.

### 1.7 Scope

* **In scope:**
  * daily data;
  * price and volume features only;
  * one-day-ahead forecasts;
  * S&P 500 constituents;
  * post-hoc explanations (SHAP, LIME).
* **Out of scope:**
  * news or sentiment data;
  * fundamentals;
  * intraday data;
  * trading costs;
  * portfolio optimisation;
  * deep-learning models.

### 1.8 Contributions

1. **Benchmarked accuracy.** Shows that a Random Forest's 98.4% price accuracy equals naive
   persistence, and that a price-level Random Forest is significantly *worse* than naive
   despite R² = 0.993.
2. **A five-part reliability audit of SHAP and LIME** for stock forecasting: faithfulness,
   stability, explainer agreement, sanity, and regime and sector drift.
3. **A direct SHAP-vs-LIME comparison** on the same forecasts: agreement, run-to-run
   stability, local fidelity and faithfulness.
4. **Statistical tests** of explanation drift across four market regimes and 11 sectors,
   on a 474-stock universe.

---

## 2. Tech stack

| Layer | Tool (version) | Used for |
|---|---|---|
| Language | Python 3.11.13 | All code (8 scripts in `src/`) |
| Environment | `venv` | Isolated, reproducible dependencies |
| Data handling | pandas 3.0.5, NumPy 2.1.3 | Cleaning the panel, feature engineering (wide date × ticker tables), results |
| Machine learning | scikit-learn 1.9.1 | `RandomForestRegressor` (main model), `RandomForestClassifier` (direction), `RidgeCV` (baseline), `permutation_importance` |
| XAI: SHAP | shap 0.51.0 | `TreeExplainer`: exact TreeSHAP values, local and global explanations |
| XAI: LIME | lime 0.2.0.1 | `LimeTabularExplainer`: local surrogate explanations |
| Statistics | SciPy 1.17.1 | Kendall τ, Spearman ρ, binomial test, normal distribution for the Diebold–Mariano test |
| Visualisation | Matplotlib 3.11.2 | All 12 figures |
| Model storage | joblib 1.6.0 | Saved yearly Random Forest models |
| Supporting | numba 0.67.0 | Required by shap |
| Result formats | JSON, CSV, pickle, PNG | Metrics, importances, explanation samples, figures |
| Hardware | Apple M3 Pro (12 cores), 18 GB RAM, macOS 14.4 | Full pipeline runs in about 30 minutes |
| Data source | ESTIMATE S&P 500 benchmark (Huynh et al., WSDM 2023) | 474 stocks, daily OHLCV and GICS sectors |
| Literature search | OpenAlex API, arXiv, publisher websites | Finding and verifying the 5 reviewed papers (2025–2026) |

**Pipeline.**

| Step | Script | Does | Output |
|---|---|---|---|
| 1 | `data.py` | Clean the raw panel | `data/panel_clean.pkl` |
| 2 | `features.py` | 32 features and next-day targets | `data/features.pkl` |
| 3 | `tune.py` | Hyperparameters on 2017–2018 | `results/tuning.json` |
| 4 | `train.py` | Walk-forward forecasts, 2019–2022 | `results/predictions.pkl`, `models/` |
| 5 | `evaluate.py` | Accuracy and significance tests | `results/metrics.json` |
| 6 | `explain.py` | SHAP explanations and reliability audit | `results/xai.json` |
| 7 | `lime_explain.py` | LIME explanations and SHAP-vs-LIME audit | `results/lime.json` |
| 8 | `plots.py` | All figures | `results/figures/` |

---

## 3. Literature review

Five recent papers (2025–2026) closest to this project: stock prediction with Random Forest
or tree-based models, explained with SHAP or LIME, or tested for explanation stability.

| # | Paper | Authors | Methodology | Research gap |
|---|---|---|---|---|
| 1 | *Stock Return Prediction on the LQ45 Market Index in the Indonesia Stock Exchange Using a Machine Learning Algorithm Based on Technical Indicators*, **Journal of Risk and Financial Management, 2025** | S. Indra, Sudradjat Supian, Sukono, Riaman Riaman, Moch Panji Agung Saputra, Astrid Sulistya Azahra, Dede Irman Pirdaus | Random Forest, XGBoost, Linear and Ridge regression on technical indicators for 6 Indonesian stocks (5- and 21-day returns); SHAP to find the most important features | Only 6 stocks. SHAP results are reported but never checked to see if they are correct or stable. |
| 2 | *Comparing model-specific and model-agnostic features importance methods using machine learning with technical indicators: A NASDAQ sector-based study*, **Machine Learning with Applications, 2025** | Jeonghoe Lee, Lin Cai | Random Forest and neural networks on NASDAQ's 11 sectors; compares different feature-importance methods for choosing technical indicators | Uses importance methods only to pick features. Does not test whether the explanations are trustworthy or change over time. |
| 3 | *An Explainable AI for Stock Market Prediction: A Machine Learning Approach with XAI and Deep Neural Networks*, **Journal of Computational and Cognitive Engineering, 2025** | Kangana Wallapure Manikrao, Shridhar Allagi, Wai Yie Leong, Mahantesh Laddi | LSTM with attention using sentiment and technical indicators; compared with Random Forest and XGBoost; SHAP and LIME for explanations | Uses SHAP and LIME side by side but does not check if they agree, or if LIME gives the same answer when run again. |
| 4 | *Regime-Aware LightGBM for Stock Market Forecasting: A Validated Walk-Forward Framework with Statistical Rigor and Explainable AI Analysis*, **Electronics, 2026** | A. Pagliaro | Tree model (LightGBM) on 51 NASDAQ-100 stocks, adjusted for bull and bear markets; explanations show the model behaves differently in each market phase | Says explanations change across market phases but does not test this statistically, and only covers 51 stocks. |
| 5 | *Attention Integration Strategies in MLP-Based Stock Movement Prediction: Effects on Performance, Stability, and Interpretability*, **Electronics, 2026** | Yoojeong Song, Woojin Cho, Sang Ik Han, Juhan Yoo | Neural network models trained 1,600 times with different random seeds on 20 stocks (10 CSI 300, 10 S&P 500) | Found that explanations change with the random seed, but only tested neural networks, not Random Forest with SHAP or LIME. |

*Methods and gaps are based on each paper's abstract and publicly available details;
confirm them against the full texts before submission.*

---

## 4. Research gap

### 4.1 What is missing

| What is missing | Seen in | How this project addresses it |
|---|---|---|
| **Correctness (faithfulness)**: checking that SHAP or LIME point to features the model really uses | Papers 1, 3 | Deletion tests: removing top-ranked features must change the forecast more than removing random ones |
| **Stability**: same explanation when the model is re-seeded or retrained, or LIME is re-run | Papers 1, 3, 5 | 5 random seeds, yearly retraining, and 5 LIME runs per forecast |
| **Agreement between explainers** | Papers 2, 3 | SHAP vs LIME vs permutation importance vs MDI |
| **Tested changes across market phases and sectors** | Papers 2, 4 | Permutation tests across 4 market regimes and 11 sectors |
| **Broad stock universe** | Papers 1, 4, 5 (6–51 stocks) | 474 S&P 500 stocks |

### 4.2 Overall research gap

> **These papers either use SHAP or LIME without checking whether the explanations can be
> trusted, or check only one aspect on a small number of stocks. No paper tests, for a
> Random Forest stock price model, whether SHAP and LIME explanations are (1) correct
> (faithful to the model), (2) stable when the model or LIME is re-run, (3) in agreement
> with each other, and (4) consistent across market phases such as the COVID crash and
> across sectors. This project fills that gap on 474 S&P 500 stocks, with price accuracy
> benchmarked against a naive forecast.**

---

## 5. Data

| Item | Detail |
|---|---|
| **Source** | Public S&P 500 benchmark released with ESTIMATE (Huynh et al., WSDM 2023), also used by StockMixer (Fan & Shen, AAAI 2024) |
| **Universe** | 474 S&P 500 constituents, 11 GICS sectors (21–67 stocks each) |
| **Fields** | Daily open, high, low, close, adjusted close, volume |
| **Period** | 14 May 2012 – 25 May 2022 (2,526 trading days), including the COVID crash and the 2022 bear market |
| **Usable stock-days** | 1,097,165 (after a 200-day feature warm-up and cleaning) |
| **Test stock-days** | 405,545 (856 trading days, Jan 2019 – May 2022) |

**Cleaning (`data.py`).**

| Issue found | Rows affected | Fix |
|---|---|---|
| Adjusted close missing before a stock was listed (e.g. PAYC, HLT) | 3,450 | Dropped |
| For 12 tickers, open/high/low were already dividend-adjusted while close was not, so high/low didn't bracket the close | ~27,000 | Convention detected per ticker; OHLC put on one adjusted basis |
| GOOG before 27 March 2014: a different, unadjusted share-class series (a −300% jump) | 470 | Dropped |

Real extreme moves are kept, e.g. the 9 March 2020 oil crash (APA −54%).

---

## 6. Methodology

### 6.1 Target and model

**Target.** For stock *i* on day *t*:
* the model predicts the next-day log return *r̂*ᵢ,ₜ₊₁;
* the price forecast is *P̂*ᵢ,ₜ₊₁ = *P*ᵢ,ₜ · exp(*r̂*ᵢ,ₜ₊₁).

Forecasting returns rather than price levels lets one model serve stocks priced from $10
to $3,000, and avoids a tree's inability to predict beyond the price range seen in training
(§7.1).

**Random Forest (scikit-learn `RandomForestRegressor`).**
* **Fixed settings:** 300 trees, each on a 25% bootstrap sample.
* **Tuned settings:** `min_samples_leaf` ∈ {200, 1000, 5000}, `max_features` ∈ {0.3, 0.6}.
* **Tuning:** by validation MSE averaged over 2017 and 2018, each validated with a model
  trained on all earlier data.
* **Selected:** `min_samples_leaf = 5000`, `max_features = 0.3`, the most regularised
  option. That is itself a sign of a low signal-to-noise problem.

### 6.2 Features

32 features, each computed only from data up to day *t*'s close:

| Family | Features |
|---|---|
| Past returns | Log returns over 1, 2, 5, 10, 20, 60 days |
| Trend | Distance from 5/20/50/200-day moving average; MACD histogram |
| Oscillators | RSI(14), stochastic %K(14), Bollinger %B(20) |
| Volatility | Realised volatility (5, 20, 60 days), ATR(14), day range, Bollinger width |
| Volume | Volume vs 20-day average, 5 vs 20-day volume trend, log dollar volume |
| Candle | Overnight gap, open-to-close body, close position in the day range |
| Market & sector | Equal-weighted market return (1 day, 5 days) and 20-day volatility, sector 5-day return, 20-day relative strength, 60-day beta |

### 6.3 Evaluation design

* **Walk-forward test.** At the start of 2019, 2020, 2021 and 2022, the model is retrained
  on all stock-days from March 2013 up to the previous 31 December, then forecasts every
  stock-day of that year. The test period is never used for tuning or design.
* **Baselines:**
  1. naive persistence (*P̂*ₜ₊₁ = *P*ₜ);
  2. historical drift (mean training return);
  3. Ridge regression on the same features;
  4. RF on raw price levels (close, 4 lags, open/high/low, moving averages in $);
  5. RF classifier for next-day direction.
* **Metrics:**
  * price: MAE, RMSE, MAPE, R², share within 1% and 2%;
  * return skill: out-of-sample R² vs a zero forecast, daily IC and Rank IC, directional
    accuracy, AUC;
  * economic: top-minus-bottom decile next-day return.
* **Significance tests:**
  * Diebold–Mariano test (Newey–West, 5 lags) on daily mean squared percentage error vs
    naive;
  * binomial test of directional accuracy vs "always predict the majority direction".

### 6.4 Explanation methods

**TreeSHAP (`shap.TreeExplainer`).**
* **What it computes:** exact Shapley values for tree ensembles. For every forecast,
  *base value* + Σ SHAP = prediction (verified: additivity error < 3×10⁻¹⁷).
* **Sample:** 40 random stocks per test day plus AAPL, MSFT, JPM, XOM and PFE on every
  day, giving **38,183 stock-days**, each explained by its own year's model.

**LIME (`lime.lime_tabular.LimeTabularExplainer`).**
* **How it works:** for one forecast, it samples 5,000 perturbed inputs, weights them by
  proximity, and fits a linear surrogate model whose weights form the explanation.
* **Settings:** default quartile discretisation; 5,000 training rows as the reference
  distribution.
* **Sample:** **804 stock-days** (200 per test year plus the local cases), each explained
  with **5 different random seeds**.

**Comparison explainers.**
* **Permutation importance:** increase in test MSE when a feature is shuffled; 3 repeats.
* **MDI:** the Random Forest's built-in impurity importance.

**Derived explanations.**
* **Global:** mean |SHAP| and mean |LIME weight| per feature.
* **Feature-family shares:** each family's share of total |SHAP|.
* **Local, in dollars:** attribution × close price ≈ each feature's dollar contribution to
  the next-day price forecast.

### 6.5 Reliability audit

| Check | SHAP | LIME |
|---|---|---|
| **Faithfulness** | Replace the top-*k* features (by \|SHAP\|) with values from 32 random training rows, *k* ∈ {1, 2, 4, 8, 16, 32}; compare with random order; AOPC; fidelity = corr(SHAP mass removed, actual change) | Same deletion test, ordered by \|LIME weight\|, on the LIME sample |
| **Stability** | 5 random seeds on identical 2013–2019 data (4,000 stock-days from 2020); consecutive yearly retrains (4,000 stock-days from 2022); global Kendall τ and per-row Spearman ρ | Same stock-day explained with 5 LIME seeds: median ρ, top-5 overlap, identical top feature |
| **Local fit** | Exact by construction (additivity) | R² of LIME's surrogate model |
| **Agreement** | Global Kendall τ among TreeSHAP, LIME, permutation and MDI; per-row SHAP vs LIME: Spearman ρ, top-5 overlap, same top feature, sign agreement | (same) |
| **Sanity (data randomisation)** | RFs trained on fully shuffled labels (no signal) and on labels shuffled within each day (keeps market-wide timing only) | – |
| **Regime and sector drift** | Mean pairwise total-variation distance (TVD) between family-share vectors; null distribution from 1,000 permutations that shuffle whole days (regimes) or whole stocks (sectors) | – |

**Regimes** (fixed in advance from market events):
* **Pre-COVID bull:** 2019-01-01 → 2020-02-19
* **COVID crash:** 2020-02-20 → 2020-03-23
* **Recovery:** 2020-03-24 → 2021-12-31
* **2022 bear:** 2022-01-01 → 2022-05-24

---

## 7. Results

### 7.1 RQ1: price accuracy

**Overall test performance** (405,545 stock-days, Jan 2019 – May 2022):

| Model | MAPE | "Price accuracy" (100 − MAPE) | RMSE | R² (price) | Within 2% | Direction accuracy | DM vs naive (p) |
|---|---|---|---|---|---|---|---|
| Naive (tomorrow = today) | 1.561% | 98.44% | $6.25 | 0.99938 | 75.3% | – | – |
| Historical drift | 1.560% | 98.44% | $6.25 | 0.99938 | 75.4% | 52.8% | 0.25 |
| Ridge regression | 1.567% | 98.43% | $6.27 | 0.99937 | 75.3% | 51.7% | 0.17 |
| RF on price levels | 1.583% | 98.42% | **$21.56** | 0.99261 | 75.0% | 50.8% | **< 0.001 (worse)** |
| **Random Forest (proposed)** | **1.560%** | **98.44%** | **$6.25** | **0.99938** | **75.4%** | **51.8%** | 0.30 |
| RF classifier (direction) | – | – | – | – | – | 51.9% (AUC 0.505) | – |

**What this shows.**
* **Accurate as a price forecast.** The Random Forest is within 1.56% of the actual next-day
  close on average (98.44% price accuracy, R² 0.9994), and within 2% on 75% of stock-days.
* **But no better than naive.** Naive persistence scores the same; the difference is not
  significant (Diebold–Mariano p = 0.30).
* **Almost no skill beyond persistence:**
  * out-of-sample return R² = +0.0001;
  * daily IC = +0.009 (t = 1.39, not significant);
  * direction accuracy 51.8%, below "always predict the majority direction" (52.8%).
* **A small, non-significant economic signal:** the top-minus-bottom decile of predicted
  returns earned +8.0 bp/day (t = 1.50).

**The price-level Random Forest shows why unbenchmarked accuracy misleads.**
* It reports R² 0.993 and 98.4% "accuracy".
* Yet its RMSE is 3.4× naive, and it is significantly *worse* than naive (DM p < 0.001).
* Its RMSE grows from $6 (2019) to $36 (2021) as prices trend to new highs, because trees
  can't predict above the training range.

**By year and regime.**

| Period | RF MAPE | Naive MAPE | RF direction accuracy | Majority-direction rule | RF daily IC |
|---|---|---|---|---|---|
| 2019 | 1.11% | 1.12% | 53.5% | 55.3% | +0.014 |
| 2020 | 2.20% | 2.20% | 51.0% | 51.8% | +0.018 |
| 2021 | 1.29% | 1.29% | 50.4% | 53.2% | −0.008 |
| 2022 (Jan–May) | 1.74% | 1.74% | 52.7% | 51.5% | +0.018 |
| COVID crash | 5.78% | 5.72% | 34.7% | 65.8% (down) | −0.073 |

* **COVID crash:** the RF was significantly worse than naive (DM p = 0.04), because it kept
  forecasting small rebounds while 66% of stock-days fell.
* **By sector:** MAPE ranges from 1.13% (Utilities) to 2.24% (Energy), and the RF equals
  naive within 0.004 percentage points in every sector.

Figures: `price_accuracy.png`, `price_paths_AAPL.png`.

### 7.2 RQ2: what drives the forecasts (SHAP)

**Global importance** (mean |SHAP|, basis points of predicted return):

| Rank | Feature | Family | Mean \|SHAP\| (bp) |
|---|---|---|---|
| 1 | Market 20-day volatility | Market & sector | 5.37 |
| 2 | Market 5-day return | Market & sector | 3.33 |
| 3 | Market 1-day return | Market & sector | 3.28 |
| 4 | Overnight gap | Candle | 0.77 |
| 5 | Own 1-day return | Past returns | 0.57 |
| 6 | Sector 5-day return | Market & sector | 0.53 |
| 7 | ATR(14) | Volatility | 0.43 |

**Family shares.**
* **Market & sector context:** 72.2%.
* **Other families:** volatility 7.6%, past returns 7.0%, candle 5.9%, trend 3.8%,
  oscillators 2.0%, volume 1.5%.

**What the features do** (dependence plots):
* **High market volatility** raises the forecast by +10–15 bp.
* **A falling 5-day market** raises it by up to +25 bp.
* **A strong up-day** for the market lowers it.

The model mainly learned **market-wide short-term reversal after volatile sell-offs**.

**Local example: AAPL on 16 March 2020** (worst day of the COVID crash):
* close $59.64 → forecast $59.82; actual next close $62.27;
* **pushing the forecast up:** market volatility (+$0.08), the −17.8% 5-day market fall
  (+$0.04);
* **pushing it down:** the −13.7% market day (−$0.01) and the overnight gap (−$0.01).

Figures: `shap_global.png`, `shap_dependence.png`, `local_explanations.png`.

### 7.3 RQ3: are the SHAP explanations faithful and stable?

**Faithfulness.**

| Features removed (k) | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| \|Δ forecast\|, top-SHAP first (bp) | 8.70 | 8.39 | 8.36 | 8.47 | 8.56 | 8.59 |
| \|Δ forecast\|, random order (bp) | 0.65 | 1.19 | 2.04 | 3.65 | 5.88 | 8.59 |
| Fidelity: corr(SHAP mass removed, actual Δ) | 0.98 | 0.99 | 0.99 | 1.00 | 1.00 | 1.00 |

* **Faithful.** Removing the single top-SHAP feature changes a forecast **13×** more than
  removing a random one (AOPC 8.51 vs 3.67 bp), and fidelity is ≥ 0.98.
* **One feature does almost all the work:** removing it moves the forecast as much as
  removing all 32.

**Stability.**

| Comparison | Global ranking τ | Top-5 overlap | Per-stock-day ρ |
|---|---|---|---|
| 5 random seeds, same data | 0.85 | 92% | 0.86 |
| 2019 vs 2020 model | 0.75 | 80% | 0.73 |
| **2020 vs 2021 model** | **0.44** | 100% | **0.57** |
| 2021 vs 2022 model | 0.77 | 80% | 0.77 |

* **Stable to the random seed** (forecast correlation between seeds 0.99).
* **Less stable to retraining:** once 2020 (COVID) enters the training data, agreement
  drops to τ = 0.44. The top 5 stay the same, but the other 27 features reorder.

Figures: `faithfulness.png`, `stability_sanity.png`.

### 7.4 RQ4: regime and sector drift

**Regimes: significant drift** (TVD 0.054 vs null 0.017, **p = 0.003**).

| Family | Pre-COVID bull | COVID crash | Recovery | 2022 bear |
|---|---|---|---|---|
| Market & sector | 71.2% | 74.7% | 71.7% | 74.7% |
| Volatility | 5.1% | 5.9% | 8.3% | **9.2%** |
| Past returns | **8.7%** | 7.2% | 6.5% | 6.0% |
| Trend | 4.6% | **5.9%** | 3.7% | 2.3% |
| Candle | 6.3% | 4.1% | 6.2% | 4.9% |
| Oscillators | 2.4% | 1.5% | 2.1% | 1.2% |
| Volume | 1.7% | 0.7% | 1.4% | 1.7% |

* **Volatility nearly doubles** (5.1% → 9.2%); **past returns fade**; **trend peaks in the
  crash**.
* **The feature ranking reorders:** rank correlation falls to 0.46 between the COVID crash
  and the 2022 bear, against 0.84 between the pre-COVID bull and the crash.
* **The top-3 market features never change.**

**Sectors: significant, but a smaller effect** (TVD 0.036 vs null 0.011, **p = 0.001**).
* **Volatile sectors use more volatility features:** Energy 10.4%, Consumer Discretionary
  9.5%, Communication Services 9.4%.
* **Defensive sectors rely more on market context:** Utilities 76.1%, Consumer Staples
  76.4%, against Energy 66.8%.

Figures: `regime_family_shares.png`, `sector_family_shares.png`.

### 7.5 RQ5: sanity check against no-signal models

| Model trained on | Test IC | Total mean \|SHAP\| (bp) | Market & sector share | τ vs real model | Per-row ρ vs real |
|---|---|---|---|---|---|
| **Real labels** | +0.018 | 20.8 | 77.3% | – | – |
| Fully shuffled labels (no signal) | −0.023 | 2.6 | 19.6% | **0.13** | 0.13 |
| Labels shuffled within each day (market timing only) | +0.011 | 19.5 | 84.5% | **0.56** | 0.60 |

* **The explanations pass the sanity check.** A no-signal model gives explanations 8×
  weaker and unrelated to the real ones.
* **But they are mostly about market-wide timing.** A model that can only learn market-wide
  timing reproduces 94% of the explanation magnitude and τ = 0.56 of the ranking.

### 7.6 RQ6: SHAP vs LIME

**Global agreement between four explainers** (Kendall τ; top-5 overlap in brackets):

| | LIME | Permutation | MDI |
|---|---|---|---|
| **TreeSHAP** | **0.73** (4/5) | **0.03** (3/5) | 0.69 (4/5) |
| **LIME** | – | 0.07 (3/5) | 0.69 (4/5) |
| **Permutation** | – | – | 0.15 (4/5) |

* **Globally, SHAP and LIME agree well** (τ = 0.73), and both agree with MDI.
* **All three disagree with permutation importance** (τ ≤ 0.15). Only 4 of 32 features
  measurably improve accuracy (permutation importance > 2 SD): market volatility, sector
  5-day return, Bollinger width and volume trend; 15 have negative permutation importance.
* **Meaning:** SHAP and LIME describe *what the model uses*, not *what improves accuracy*.

**Reliability for individual forecasts** (804 stock-days, 5 LIME seeds each):

| Measure | TreeSHAP | LIME |
|---|---|---|
| Agreement with the other method: median Spearman ρ | – | **0.45** |
| Agreement: top-5 feature overlap | – | 66% |
| Agreement: same top feature | – | 59% |
| Agreement: sign matches SHAP on SHAP's top-5 features | – | 81% |
| Run-to-run stability: median ρ between runs | **1.00** (deterministic) | **0.48** |
| Run-to-run stability: top-5 overlap between runs | 1.00 | 80% |
| Run-to-run stability: same top feature in all 5 runs | 100% | 92% |
| Local fit (surrogate R²) | exact (additive) | **median 0.17**; 67% of explanations below 0.3 |
| Faithfulness AOPC (bp; random order = 3.71) | **8.70** | 8.15 |
| Faithfulness: \|Δ forecast\| after removing top-1 feature (random = 0.56 bp) | **8.89** | 6.50 |
| Time per explanation | ~0.001 s | ~0.08 s |

**What this shows.**
* **LIME is less reliable than SHAP for individual forecasts:**
  * explaining the *same* forecast twice with different seeds gives a feature ranking that
    correlates only 0.48;
  * LIME's linear surrogate explains a median of just **17%** of the model's local
    behaviour;
  * on a typical forecast, LIME and SHAP share only 3 of their top 5 features.
* **Both are faithful, SHAP more so.** Both beat random ordering, but removing LIME's top
  feature changes the forecast 27% less than removing SHAP's.
* **They can contradict each other on the same forecast.**
  * **AAPL, 16 March 2020:** they agree on the two main drivers (market volatility +$0.077
    SHAP vs +$0.074 LIME; 5-day market return +$0.044 vs +$0.041), ρ = 0.53, LIME R² 0.49.
  * **JPM, 18 May 2022:** they disagree on the *direction* of the top feature. Market
    volatility pushes the forecast down by $0.056 per SHAP but up by $0.050 per LIME
    (ρ = 0.19, LIME R² 0.11).
  * **Why:** LIME's discretised bins ("market volatility > 0.01") compare against the whole
    training distribution, while SHAP attributes along the model's own decision paths.

Figures: `lime_vs_shap_local.png`, `lime_reliability.png`, `explainer_agreement.png`.

---

## 8. Discussion

1. **High price accuracy needs a benchmark to mean anything.**
   * The Random Forest's 98.44% price accuracy is real, but naive persistence scores exactly
     the same, and a price-level Random Forest with R² 0.993 is significantly worse than
     naive.
   * Accuracy claims without a persistence baseline cannot be interpreted. This matches
     the weak signal Indra et al. (2025) found once returns were evaluated properly.
2. **Faithful does not mean the market insight is real.**
   * SHAP is faithful (fidelity ≥ 0.98), seed-stable (τ = 0.85) and passes the sanity check.
   * Yet SHAP, LIME and MDI all disagree with permutation importance (τ ≤ 0.15).
   * Explanations describe how the model computes its forecast, not which relationships
     actually predict prices. Presenting SHAP or LIME rankings as market insight, as in
     papers 1 and 3, conflates the two.
3. **For tree models, SHAP should be preferred over LIME for individual explanations.**
   * LIME agrees with SHAP globally (τ 0.73) but is unstable for individual forecasts (ρ
     0.48 between runs), fits poorly (median R² 0.17), and can flip a feature's sign.
   * Studies reporting a single LIME explanation per case (paper 3) risk reporting noise.
     Like Song et al. (2026) for neural networks, this shows explanations must be
     re-run before they are trusted.
4. **Explanations are period- and sector-specific.**
   * Regime drift (p = 0.003), sector drift (p = 0.001) and the drop in agreement after
     retraining on COVID data (τ 0.44) mean an explanation from one period shouldn't be
     generalised.
   * This turns Pagliaro's (2026) qualitative regime observation into formal tests on 474
     stocks.
5. **What the model learned.**
   * Mainly one market-wide rule: expect a small rebound after volatile sell-offs.
   * It failed in the COVID crash (35% direction accuracy), which is exactly when a user
     would most rely on it.

---

## 9. Limitations

* **Data:**
  * price and volume only (no news, fundamentals or macroeconomic data);
  * the data ends May 2022;
  * the 474 stocks were constituents when the dataset was built (survivorship bias).
* **Explanation methods:**
  * TreeSHAP uses the path-dependent algorithm; interventional SHAP could differ when
    features are correlated;
  * LIME uses its default quartile discretisation and 5,000 samples; other settings could
    change its stability.
* **Faithfulness test:** it replaces features with values from random training rows, which
  can create unrealistic feature combinations.
* **Regimes and costs:** regimes are calendar-defined; the COVID crash has only 23 trading
  days. Transaction costs are not modelled.
* **Literature gaps:** stated from abstracts and public details; verify against full
  texts before submission.

---

## 10. Conclusion

* **Accuracy.** A walk-forward Random Forest forecasts next-day closing prices for 474
  S&P 500 stocks with 98.44% price accuracy (MAPE 1.56%, R² 0.9994). That is statistically
  identical to naive persistence, with 51.8% directional accuracy.
* **SHAP explanations** are:
  * faithful and seed-stable;
  * clearly different from a no-signal model;
  * mostly about market-wide timing;
  * significantly different across market regimes and sectors, and after retraining.
* **LIME explanations** agree with SHAP globally, but are unstable between runs, fit the
  model poorly, and can contradict SHAP on individual forecasts.
* **Neither** SHAP nor LIME identifies the features that actually improve accuracy.
* **Recommendations for stock-forecasting studies:**
  1. benchmark accuracy against persistence;
  2. prefer TreeSHAP to single LIME runs for tree models;
  3. test explanations for faithfulness, stability, sanity and regime drift before
     reading them as market insight.

---

## 11. References

**Literature review**

1. Indra, S., Supian, S., Sukono, Riaman, R., Saputra, M. P. A., Azahra, A. S., & Pirdaus, D. I. (2025). Stock Return Prediction on the LQ45 Market Index in the Indonesia Stock Exchange Using a Machine Learning Algorithm Based on Technical Indicators. *Journal of Risk and Financial Management*. https://doi.org/10.3390/jrfm18120714
2. Lee, J., & Cai, L. (2025). Comparing model-specific and model-agnostic features importance methods using machine learning with technical indicators: A NASDAQ sector-based study. *Machine Learning with Applications*. https://doi.org/10.1016/j.mlwa.2025.100799
3. Manikrao, K. W., Allagi, S., Leong, W. Y., & Laddi, M. (2025). An Explainable AI for Stock Market Prediction: A Machine Learning Approach with XAI and Deep Neural Networks. *Journal of Computational and Cognitive Engineering*. https://doi.org/10.47852/bonviewjcce52026428
4. Pagliaro, A. (2026). Regime-Aware LightGBM for Stock Market Forecasting: A Validated Walk-Forward Framework with Statistical Rigor and Explainable AI Analysis. *Electronics*, 15(6), 1334. https://doi.org/10.3390/electronics15061334
5. Song, Y., Cho, W., Han, S. I., & Yoo, J. (2026). Attention Integration Strategies in MLP-Based Stock Movement Prediction: Effects on Performance, Stability, and Interpretability. *Electronics*, 15(17), 3942. https://doi.org/10.3390/electronics15173942

**Methods and data**

6. Breiman, L. (2001). Random Forests. *Machine Learning*, 45, 5–32.
7. Lundberg, S. M., Erion, G., Chen, H., et al. (2020). From local explanations to global understanding with explainable AI for trees. *Nature Machine Intelligence*, 2, 56–67.
8. Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). "Why Should I Trust You?": Explaining the Predictions of Any Classifier. *KDD 2016*.
9. Diebold, F. X., & Mariano, R. S. (1995). Comparing Predictive Accuracy. *Journal of Business & Economic Statistics*, 13(3), 253–263.
10. Adebayo, J., Gilmer, J., Muelly, M., Goodfellow, I., Hardt, M., & Kim, B. (2018). Sanity Checks for Saliency Maps. *NeurIPS 2018*.
11. Huynh, T. T., Nguyen, M. H., Nguyen, T. T., et al. (2023). Efficient Integration of Multi-Order Dynamics and Internal Dynamics in Stock Movement Prediction. *WSDM 2023* (source of the S&P 500 dataset).

# Literature Review and Problem Statement

*Trustworthy Explanations for Random-Forest Stock Price Forecasting — 474 S&P 500 stocks*

---

## 1. Problem statement

### 1.1 The two problems in the literature

**Problem 1: accuracy is reported without a meaningful benchmark.**

- Stock-prediction papers report very high accuracy for price forecasting, such as R² of 0.88–0.99.
- But a share price tomorrow is almost the same as today's. The naive forecast **"tomorrow's price = today's price"** already scores R² ≈ 0.999.
- Unless a paper compares against that naive forecast and tests the difference, the reader cannot tell whether the model has any real skill.

**Problem 2: explanations are presented as findings, but never tested.**

- Papers attach SHAP or LIME to a model, report which features rank highest, and present that as insight about the market.
- They do not check whether those explanations are:

| Property | The question it answers | What it means if it fails |
|---|---|---|
| **Faithful** | Do the features the explanation ranks highest actually drive the prediction? | The explanation names features the model barely uses |
| **Stable** | Does the explanation stay the same after retraining, a new random seed, or re-running LIME? | The "finding" is an accident of one run |
| **In agreement** | Do SHAP and LIME give the same answer for the same forecast? | The conclusion depends on which tool was picked |
| **Meaningful** | Does it differ from the explanation of a model trained on scrambled, meaningless data? | The explanation reflects the data's structure, not anything learned |
| **Consistent** | Does it change between calm markets and crashes, or between sectors? | One "global" explanation misrepresents specific periods |

### 1.2 Problem statement

> **Given daily price and volume data for 474 S&P 500 stocks (2012–2022), this project builds a Random Forest that forecasts each stock's next-day closing price, measures its accuracy against a naive "tomorrow = today" benchmark with a significance test, and then audits its SHAP and LIME explanations: are they faithful to the model, stable across retraining and repeated runs, in agreement with each other, distinguishable from the explanations of a model trained on meaningless labels, and statistically different across market regimes and sectors?**

### 1.3 Research questions

| # | Question |
|---|---|
| RQ1 | How accurate is the next-day price forecast, and how much of that accuracy exceeds naive persistence? |
| RQ2 | Which features drive the forecasts, globally and for individual stock-days? |
| RQ3 | Are the SHAP explanations faithful to the model, and stable across seeds and retraining? |
| RQ4 | Do explanations change significantly across market regimes and sectors? |
| RQ5 | Do they differ from those of a model trained on shuffled, signal-free labels? |
| RQ6 | Do SHAP and LIME agree, and which is more reliable for this model? |

---

## 2. Key terms

### 2.1 Stock market terms

| Term | Meaning |
|---|---|
| **Return** | Percentage change in price. ₹100 → ₹102 is a +2% return |
| **5-day / 21-day return** | Percentage change over the next 5 or 21 *trading* days (about one week, about one month) |
| **Direction accuracy** | How often the model gets "up or down" right. 50% is a coin flip |
| **Buy-and-hold** | Buy once and do nothing. The benchmark every strategy must beat |
| **Naive (persistence) forecast** | "Tomorrow's price = today's price." Simple, and very hard to beat |
| **Basis point (bp)** | One hundredth of a percent. 100 bp = 1% |
| **Sharpe ratio** | Profit per unit of risk. Above 1 is good |
| **Deflated Sharpe ratio** | Sharpe corrected for having tested many strategies, since one of many looks good by luck |

### 2.2 Accuracy measures

| Term | Meaning |
|---|---|
| **MAE** | Average error size, in dollars |
| **RMSE** | Like MAE, but punishes large misses more |
| **MAPE** | Average error as a percentage |
| **R²** | Share of variation explained; 1.0 is perfect, 0 is no better than guessing the average. **Trap:** on price *levels* it is ≈ 0.99 automatically |
| **AUC** | Quality of up/down predictions; 0.5 is random |
| **p-value** | Probability a result this strong arose by luck; below 0.05 is "significant" |
| **Kendall τ / Spearman ρ** | Do two rankings agree? 1 = identical, 0 = unrelated |

### 2.3 The models

| Term | Meaning |
|---|---|
| **Decision tree** | A flowchart of yes/no questions ending in a prediction |
| **Random Forest** | Hundreds of decision trees, each on a random slice of data and features; the answer is their average. Robust and hard to overfit. **The model used in this project** |
| **XGBoost / LightGBM** | Trees built one after another, each correcting the previous one's errors |
| **Linear / Ridge regression** | Straight-line models; Ridge penalises over-reliance on any one input |
| **LSTM** | A neural network for sequences, with memory of earlier days |
| **Attention** | A neural-network component that learns which days or features to focus on |
| **Hidden Markov Model (HMM)** | Labels each period with a hidden state; used to tag markets as bull, bear or sideways |

### 2.4 Technical indicators (the model's inputs)

| Term | Meaning |
|---|---|
| **Moving average (SMA/EMA)** | Average price over the last N days; smooths out noise |
| **RSI** | 0–100 scale of recent gains vs losses; above 70 "overbought", below 30 "oversold" |
| **MACD** | Difference between a fast and a slow moving average; signals trend changes |
| **Bollinger Bands** | A band around the moving average; its width measures volatility |
| **ATR** | Average daily trading range; a volatility measure |
| **Stochastic %K/%D, Williams %R, CCI, ROC** | Momentum gauges: where today's price sits in its recent range, and how fast it is moving |
| **OBV, WAD, EOM** | Volume-based gauges of buying vs selling pressure |
| **Beta** | How strongly a stock moves with the market as a whole |

### 2.5 Testing and explainability

| Term | Meaning |
|---|---|
| **Look-ahead bias (leakage)** | Accidentally letting the model see the future; makes results look great but fake |
| **Walk-forward validation** | Train on the past, predict the next period, roll forward, repeat |
| **Random seed** | The starting point for a model's randomness; a different seed gives a slightly different model |
| **SHAP** | Splits a prediction into each feature's contribution ("market volatility added 8 cents"). Exact for tree models, and identical every run |
| **LIME** | Explains one prediction by nudging inputs thousands of times and fitting a simple local model. Because the nudges are random, **re-running can give a different answer** |
| **Permutation importance** | Scramble one feature and see how much accuracy drops. Measures what helps accuracy |
| **Gini / MDI importance** | A tree's built-in count of how useful each feature was |
| **Faithfulness** | Does the explanation match what the model really does? |
| **Sanity check** | Train a model on scrambled answers; its explanations should look nothing like the real model's |
| **Market regime** | A phase of the market: calm bull market, crash, recovery, bear market |

---

## 3. Literature review: five recent papers (2025–2026)

### 3.1 Indra et al. (2025), *Journal of Risk and Financial Management* 18(12), 714

**Authors:** Indra; Sudradjat Supian; Sukono; Riaman; Moch Panji Agung Saputra; Astrid Sulistya Azahra; Dede Irman Pirdaus (Universitas Padjadjaran, Indonesia).

- **What they did:** tested whether better statistical accuracy actually earns money, by predicting stock returns and then simulating real trading with fees.
- **Dataset:** Yahoo Finance, January 2016 – September 2025. **Six Indonesian LQ45 stocks** (BBCA, BBRI, BMRI, ASII, ICBP, UNVR), about 2,420 trading days each.
- **Method:** Linear regression, Ridge, **Random Forest** and XGBoost; targets were 5-day and 21-day returns; inputs were momentum, volatility, trend and volume indicators; expanding-window walk-forward validation; backtest including transaction costs; **SHAP** for interpretation.
- **Results and conclusion:** R² near zero or negative; **direction accuracy 49–54%**; AUC 0.50–0.53. XGBoost had the lowest errors, but Ridge earned more (Sharpe 0.1232 vs −0.1935), and **every strategy lost to buy-and-hold**. SHAP ranked volatility and volume highest, but all values were below 0.0004, which the authors call negligible. They conclude the market is "semi-efficient": patterns exist but do not survive real-world trading costs.
- **Gap:** only **6 stocks**; SHAP is computed once and reported, never tested for correctness or stability; no LIME; no analysis by market phase or sector.

### 3.2 Lee & Cai (2025), *Machine Learning with Applications* 23, 100799

**Authors:** Jeonghoe Lee, Lin Cai (Department of Statistics, Columbia University).

- **What they did:** compared *methods of ranking features*, to see which one best selects technical indicators for prediction.
- **Dataset:** Yahoo Finance, June 2019 – June 2024. **22 NASDAQ companies**, two from each of the 11 sectors, 26,487 observations, **15 technical indicators**.
- **Method:** 8 models (**Random Forest**, Gradient Boosting, XGBoost, MLP, RNN, LSTM, GRU, TCN) predicting the next closing price; rolling-window forecasting with scaling fitted inside each window to prevent leakage; compared **model-specific** importance (Gini, coefficients, gradient saliency) against **model-agnostic** importance (**SHAP**, **permutation importance**); kept the top-5 features, retrained, and measured R² and MAPE.
- **Results and conclusion:** tree models always selected the same five indicators (Williams %R, ROC, EOM, WAD, SMA), while neural models selected different ones. Best results reached R² ≈ 0.93. Their headline conclusion: **model-specific methods gave the most stable rankings, permutation importance was next, and SHAP was the least stable.**
- **Gap:** they test whether ranking methods **agree with each other**, not whether a ranking is **true to the model** — there is no test that the top-ranked features actually drive predictions. No LIME, no per-prediction explanations, and R² is measured on price levels with no naive benchmark.

### 3.3 Manikrao et al. (2025), *Journal of Computational and Cognitive Engineering* 5(3), 410–424

**Authors:** Kangana Wallapure Manikrao; Shridhar Allagi; Wai Yie Leong; Mahantesh Laddi.

- **What they did:** built an accurate deep-learning price predictor and explained it with **both SHAP and LIME**.
- **Dataset:** Yahoo Finance, **Apple (AAPL) only**, January 2020 – December 2024, daily prices plus a daily sentiment index built from news and Twitter.
- **Method:** LSTM (two layers, 64 and 32 units) with multiplicative attention; a hybrid MAE + MAPE loss; walk-forward validation; 25 independent runs; compared against XGBoost, **Random Forest**, plain LSTM, Temporal Fusion Transformer and Informer.
- **Results and conclusion:** RMSE 1.56, MAE 1.08, **R² 0.88**, beating all baselines. SHAP showed the day's low, high and open prices dominate (a second analysis ranked RSI 0.28 and MACD 0.22 highest, sentiment 0.19); LIME explained individual predictions, for example RSI 67 contributing +0.9.
- **Gap:** **a single stock**, which the authors acknowledge; SHAP and LIME are used side by side but **never compared with each other**; LIME is run once per case, so its instability cannot appear; neither explanation is validated; R² is reported with no naive benchmark.

### 3.4 Pagliaro (2026), *Electronics* 15(6), 1334

**Author:** Antonio Pagliaro (INAF Palermo, Italy).

- **What they did:** built a tree model that changes its behaviour according to the market phase, validated it rigorously, and used SHAP to show how its reasoning shifts.
- **Dataset:** **51 NASDAQ-100 stocks**, January 2015 – February 2026 (about 2,791 days each), plus 10 macroeconomic and cross-asset series (VIX, gold, Bitcoin, high-yield and government bonds, the dollar index).
- **Method:** **LightGBM** predicting whether the 10-day forward return is positive, using 63 normalised features; market regimes (bull, sideways, bear) detected by a **rolling Hidden Markov Model** refitted every 63 days to avoid look-ahead bias; walk-forward validation with 100 folds and a 10-day purge; a trading backtest with costs; **SHAP (TreeExplainer)** for explanations.
- **Results and conclusion:** portfolio Sharpe 1.184 and out-of-fold accuracy 53.8%, with honest negative findings: poor probability calibration, a **Deflated Sharpe of 0.686 (not significant)**, and only **9 of 51 stocks (17.6%) beating buy-and-hold**. Its key XAI finding: the model's **decision logic changes by regime** — distance from the 200-day average dominates in bear markets (mean |SHAP| 0.498), while the yield curve (0.434) and market beta (0.290) dominate in bull markets.
- **Gap:** the regime comparison is **descriptive and based on a single stock (AMD)**, with **no statistical test** that the differences are real; no faithfulness or stability check; no LIME; the author also acknowledges survivorship bias.

### 3.5 Song et al. (2026), *Electronics* 15(17), 3942

**Authors:** Yoojeong Song; Woojin Cho; Sang Ik Han; Juhan Yoo (Republic of Korea).

- **What they did:** tested whether attention actually helps stock prediction, and whether explanations taken from attention weights are reproducible.
- **Dataset:** **10 CSI 300 and 10 S&P 500 stocks**, May 2016 – April 2023, **111 features** (5 raw price/volume series plus 106 technical indicators).
- **Method:** predicting the direction of the 5-day forward return with a strictly forward-looking label, a purged chronological split and early stopping; **16 model configurations × 20 stocks × 5 random seeds = 1,600 runs**.
- **Results and conclusion:** one way of adding attention collapsed to predicting a single class in every run; otherwise no model family was significantly more accurate (about 51–52%). The key finding: **the "most important features" identified by different random seeds shared almost nothing** — pairwise overlap averaged 0.046 and rank correlation was effectively zero (0.006). The explanations were seed noise, because the models reached their best validation loss after a median of one epoch, leaving attention weights near their random starting values.
- **Gap:** this tests **attention weights inside neural networks**, not SHAP or LIME on tree models; 20 stocks; direction classification rather than price prediction.

### 3.6 Summary of the five papers

| # | Authors (year) | Dataset | Models | XAI used | Main conclusion | Gap |
|---|---|---|---|---|---|---|
| 1 | Indra et al. (2025) | 6 Indonesian stocks, 2016–2025 | Linear, Ridge, RF, XGBoost | SHAP | Accuracy 49–54%; all strategies lose to buy-and-hold | 6 stocks; SHAP never validated |
| 2 | Lee & Cai (2025) | 22 NASDAQ stocks, 11 sectors, 2019–2024 | RF, GB, XGBoost, 5 neural models | SHAP, permutation, Gini | SHAP is the least stable ranking method | Tests agreement, not correctness; no LIME |
| 3 | Manikrao et al. (2025) | Apple only, 2020–2024 | LSTM + attention | SHAP and LIME | R² 0.88 with interpretable outputs | 1 stock; SHAP and LIME never compared |
| 4 | Pagliaro (2026) | 51 NASDAQ-100 stocks, 2015–2026 | LightGBM + HMM regimes | SHAP | Model's reasoning changes by market phase | Descriptive, 1 stock, no significance test |
| 5 | Song et al. (2026) | 20 stocks (CSI 300, S&P 500), 2016–2023 | MLP, attention, LSTM, Transformer | Attention weights | Explanations change completely with the random seed | Attention only, not SHAP or LIME on trees |

---

## 4. The research gap

### 4.1 Evidence

The five PDFs were searched directly for the relevant terms:

- **"faithful" — 0 occurrences. "deletion" — 0 occurrences. "sanity" — 0 occurrences**, across all five papers. No paper tests whether removing the features an explanation ranks highest actually changes the prediction.
- **No paper uses a shuffled-label control model.**
- **LIME appears only in paper 3**, where it is never compared with that paper's own SHAP results.

### 4.2 What is already covered, and what is not

| Check | Already done by | Still untested |
|---|---|---|
| Comparing explainers | Paper 2 (model-specific vs SHAP vs permutation) | SHAP vs **LIME** on the same forecasts |
| Stability of explanations | Paper 2 (across stocks, sectors, windows); Paper 5 (across seeds, attention only) | Seeds and retraining for **SHAP on a tree model**; **LIME run-to-run** |
| Explanations by market phase | Paper 4 (descriptive, 1 stock) | **Statistical testing** of the difference |
| **Faithfulness** | nobody | **Fully open** |
| **No-signal control** | nobody | **Fully open** |

### 4.3 Gap statement

> **Recent work has begun to question stock-prediction explanations: Lee and Cai (2025) find SHAP the least stable ranking method, Song et al. (2026) find that neural-network explanations change entirely with the random seed, and Pagliaro (2026) shows a model's reasoning differs across market regimes. All of this measures whether explanations agree with one another. No paper tests whether an explanation is faithful — whether the features it ranks highest are the ones actually driving the prediction — and none compares against a model trained on meaningless labels. No paper compares SHAP against LIME on the same forecasts. This project adds those missing tests, on 474 S&P 500 stocks, with accuracy benchmarked against a naive forecast.**

---

## 5. What this project does

### 5.1 Scale, compared with the reviewed papers

| Paper | Stocks |
|---|---|
| Manikrao et al. (2025) | 1 |
| Indra et al. (2025) | 6 |
| Song et al. (2026) | 20 |
| Lee & Cai (2025) | 22 |
| Pagliaro (2026) | 51 |
| **This project** | **474** |

- **474 S&P 500 stocks**, all 11 GICS sectors (21–67 stocks each), May 2012 – May 2022.
- **1,097,165 stock-days** after cleaning; **405,545 forecasts** in the test period (2019 – May 2022).
- **38,183 forecasts explained with SHAP**; 804 forecasts explained with LIME five times each.

### 5.2 The model

- A **Random Forest** (300 trees) predicts the next-day return; the price forecast is today's close × the predicted change.
- 32 features in 7 families: past returns, trend, oscillators, volatility, volume, candle shape, and market/sector context.
- **Walk-forward testing:** the model is retrained each January on all earlier data, then forecasts that year. The test period is never used for any design decision.
- **Baselines:** naive persistence, historical drift, Ridge regression, a Random Forest trained on raw price levels, and a Random Forest classifier for direction.

### 5.3 How faithfulness is tested (the central new test)

For one forecast:

1. Record the model's prediction.
2. Ask SHAP which features contributed most **to that specific prediction**.
3. Replace the top-ranked feature's value with a value from a random training day, so the model still runs but that feature carries no real information; repeat with 32 different replacement values and average.
4. Re-run the model and measure how far the forecast moved.
5. Repeat for the top 2, 4, 8, 16 and all 32 features.
6. Repeat the whole procedure removing features **in random order** — the control.
7. Average over 2,000 stock-days.

**Result:**

| Features removed | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| SHAP's top features removed first (bp) | **8.70** | 8.39 | 8.36 | 8.47 | 8.56 | 8.59 |
| Random order (bp) | 0.65 | 1.19 | 2.04 | 3.65 | 5.88 | 8.59 |

- Removing **one** SHAP-selected feature moves the forecast **13× more** than removing one random feature.
- Both curves meet at 32 because removing everything gives the same result either way; what matters is how fast each rises.
- **Fidelity:** the SHAP values of removed features predict the actual change with r = 0.98 (at 5% removed) and 0.94 (at 10%).

### 5.4 The other reliability tests

| Test | How it works |
|---|---|
| **Stability across seeds** | Train five Random Forests on identical data with different random seeds; compare their explanations |
| **Stability across retraining** | Compare the 2019, 2020, 2021 and 2022 models explaining the same stock-days |
| **LIME run-to-run** | Explain the same forecast five times with different LIME seeds |
| **Explainer agreement** | Compare SHAP, LIME, permutation importance and the tree's own importance |
| **Sanity check** | Train models on labels shuffled at random (no signal at all) and on labels shuffled within each day (market timing only), then compare their explanations with the real model's |
| **Regime and sector drift** | Compare feature-family attribution across four market phases and 11 sectors, with a 1,000-run permutation test for significance |

### 5.5 Results

| Finding | Result |
|---|---|
| Price accuracy | MAPE 1.56% (98.44% accuracy), RMSE $6.25, R² 0.9994, 75% of forecasts within 2% |
| **Versus the naive forecast** | **Identical; the difference is not significant (p = 0.30)** |
| Direction accuracy | 51.8%, below the "always predict the majority" rule (52.8%) |
| Random Forest on raw price levels | R² 0.993 yet significantly **worse** than naive (p < 0.001), showing why unbenchmarked R² misleads |
| What drives forecasts | 72% of attribution goes to market and sector context |
| **Faithfulness** | Top-SHAP removal moves forecasts 13× more than random; fidelity r ≥ 0.94 |
| **Seed stability** | Kendall τ 0.85 (SHAP is stable) |
| **Retraining stability** | τ 0.44–0.77; weakest after COVID entered the training data |
| **Explainer agreement** | SHAP vs tree importance τ 0.69, but SHAP vs permutation only **τ 0.03** — only 4 of 32 features measurably improve accuracy |
| **SHAP vs LIME** | Agree globally (τ 0.73), but on a single forecast LIME is unstable between runs (ρ 0.48) and fits poorly (median R² 0.17) |
| **Regime drift** | Significant (p = 0.003): volatility's share rises from 5.1% pre-COVID to 9.2% in the 2022 bear market |
| **Sector drift** | Significant (p = 0.001) |
| **Sanity check** | A no-signal model gives explanations 8× weaker and unrelated (τ 0.13) |

**In short:** the explanations are faithful and stable, but they describe *what the model does*, not *what predicts the market* — and they change significantly with the market phase.

---

## 6. Anticipated questions

**"Isn't this already done?"** Partly, and that should be conceded. Papers 2, 4 and 5 each test *one* property, on 6–51 stocks, in different settings. The contribution here is the **validation protocol applied together** — faithfulness, stability, agreement, sanity and drift — on 474 stocks, plus the first SHAP-versus-LIME comparison on the same forecasts. It is a validation contribution, not a new XAI method.

**"Why is 98% accuracy not impressive?"** Because the naive "tomorrow = today" forecast scores the same. That is the point of the project, and it is why every accuracy figure is reported next to a benchmark and a significance test.

**"Isn't replacing a feature with a random value unrealistic?"** Yes, and this is stated as a limitation: it can create feature combinations that never occur in real markets. It is a known weakness of deletion-based faithfulness testing.

**Honest caveats.** Gaps were identified from the papers' full texts plus direct word searches for "faithful", "deletion" and "sanity"; papers 2 and 5 were read in sections rather than cover to cover. The dataset ends in May 2022 and covers only price and volume data, with no news or fundamentals.

---

## 7. References

1. Indra, S., Supian, S., Sukono, Riaman, R., Saputra, M. P. A., Azahra, A. S., & Pirdaus, D. I. (2025). Stock Return Prediction on the LQ45 Market Index in the Indonesia Stock Exchange Using a Machine Learning Algorithm Based on Technical Indicators. *Journal of Risk and Financial Management*, 18(12), 714. https://doi.org/10.3390/jrfm18120714
2. Lee, J., & Cai, L. (2025). Comparing model-specific and model-agnostic features importance methods using machine learning with technical indicators: A NASDAQ sector-based study. *Machine Learning with Applications*, 23, 100799. https://doi.org/10.1016/j.mlwa.2025.100799
3. Manikrao, K. W., Allagi, S., Leong, W. Y., & Laddi, M. (2025). An Explainable AI for Stock Market Prediction: A Machine Learning Approach with XAI and Deep Neural Networks. *Journal of Computational and Cognitive Engineering*, 5(3), 410–424. https://doi.org/10.47852/bonviewjcce52026428
4. Pagliaro, A. (2026). Regime-Aware LightGBM for Stock Market Forecasting: A Validated Walk-Forward Framework with Statistical Rigor and Explainable AI Analysis. *Electronics*, 15(6), 1334. https://doi.org/10.3390/electronics15061334
5. Song, Y., Cho, W., Han, S. I., & Yoo, J. (2026). Attention Integration Strategies in MLP-Based Stock Movement Prediction: Effects on Performance, Stability, and Interpretability. *Electronics*, 15(17), 3942. https://doi.org/10.3390/electronics15173942

**Methods and data**

6. Breiman, L. (2001). Random Forests. *Machine Learning*, 45, 5–32.
7. Lundberg, S. M., Erion, G., Chen, H., et al. (2020). From local explanations to global understanding with explainable AI for trees. *Nature Machine Intelligence*, 2, 56–67.
8. Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). "Why Should I Trust You?": Explaining the Predictions of Any Classifier. *KDD 2016*.
9. Diebold, F. X., & Mariano, R. S. (1995). Comparing Predictive Accuracy. *Journal of Business & Economic Statistics*, 13(3), 253–263.
10. Huynh, T. T., Nguyen, M. H., Nguyen, T. T., et al. (2023). Efficient Integration of Multi-Order Dynamics and Internal Dynamics in Stock Movement Prediction. *WSDM 2023* (source of the S&P 500 dataset).

# How this project works, step by step

*Study notes on the pipeline, the numbers and the explainability architecture*

---

Every number here was read out of the saved result files, not remembered. Jargon is
defined the first time it appears, in plain words.


## 0. The one-paragraph version

We take ten years of daily prices for 474 big American companies. For each company on
each day we compute 32 numbers that describe "what has been happening to this stock
lately" (features). We train a Random Forest to guess one thing: how much will this
stock move tomorrow. Then — and this is the actual project — we ask two different
explanation tools, SHAP and LIME, to tell us why the model guessed what it guessed,
and we run five tests to find out whether those explanations can be believed at all.

The forecast is nearly worthless. The audit of the explanations is the result.

---

## 1. The map

Twelve files. Ten you run, two you only import. They run in this order, and each one
eats what the one before it produced.

| # | You run | It reads | It writes |
|---|---------|----------|-----------|
| 0 | — | `src/config.py` is imported by everything | nothing (just settings) |
| 1 | `src/data.py` | `baseline_data_sp500.npy`, `sp500_ticker.csv` | `data/panel_clean.pkl` |
| 2 | `src/features.py` | `panel_clean.pkl` | `data/features.pkl` |
| 3 | `src/tune.py` | `features.pkl` | `results/tuning.json` |
| 4 | `src/train.py` | `features.pkl`, `panel_clean.pkl`, `tuning.json` | `results/predictions.pkl`, 8 model files, `mdi_importance.json` |
| 5 | `src/evaluate.py` | `predictions.pkl` | `results/metrics.json` |
| 6 | `src/explain.py` | `features.pkl`, the 4 saved models, `tuning.json` | `results/xai.json`, `importance.csv`, `shap_sample.pkl` |
| 7 | `src/lime_explain.py` | `shap_sample.pkl`, `importance.csv`, `features.pkl`, models | `results/lime.json`, `lime_sample.pkl` |
| 8 | `src/plots.py` | `metrics.json`, `xai.json`, `lime.json`, `predictions.pkl` | 15 PNGs in `results/figures/` |
| 9 | `src/live.py` | Yahoo Finance (internet), `tuning.json` | `results/live_forecast.pkl`, `live_meta.json`, `rf_reg_live.joblib` |
| 10 | `src/app.py` | everything above | serves the web page on port 8000 |

Two files are never run on their own:

- `src/config.py` — one place for every path, date and setting. 32 lines.
- `src/features.py` has a `build()` function that two other files import, so it is both
  a step you run and a library.

---

## 2. Stage by stage

### Stage 0 — `config.py`: the settings everyone shares

Not run. Imported by all nine other modules. It holds:

- Where every file lives.
- The three time periods. Train starts 2013-03-01 (the first day on which a 200-day
  moving average exists). Validation is 2018. Test is 2019 to 2022-05.
- The four market regimes (a regime is just a named stretch of time with a particular
  market mood), fixed from public history before anybody looked at a single
  explanation, so they cannot be cherry-picked after the fact:

  | Regime | From | To |
  |---|---|---|
  | Pre-COVID bull | 2019-01-01 | 2020-02-19 |
  | COVID crash | 2020-02-20 | 2020-03-23 |
  | Recovery | 2020-03-24 | 2021-12-31 |
  | 2022 bear | 2022-01-01 | 2022-12-31 |

- `SEED = 42`. A seed is the starting point for the computer's random number generator;
  fixing it means a rerun gives the identical answer.

### Stage 1 — `data.py`: clean the raw prices

Input: `baseline_data_sp500.npy`, an 88 MB file from the ESTIMATE paper's public
repository. Inside it is a Python dictionary: ticker → a table of open, high, low,
close, adjusted close and volume for every day. Plus `sp500_ticker.csv`, which says
which GICS sector each company is in (GICS is the standard industry classification —
Energy, Financials, Health Care and so on; there are 11).

What it does — three real data bugs found and fixed:

1. Before a company was listed, `adjclose` is NaN (not a number, a missing value).
   Those rows are dropped.
2. Fifteen tickers store open/high/low already adjusted for dividends but store close
   unadjusted, so the day's high is lower than its close, which is impossible. The code
   tests both conventions and keeps whichever one puts the close inside the day's range
   more often.
3. GOOG before 2014-03-27 is a different share class spliced in, which shows up as a
   −300% one-day jump. Dropped.

Output: `data/panel_clean.pkl`. One row per stock per day.

```
474 tickers, 2,526 dates, 1,193,405 rows, 2012-05-14 -> 2022-05-25, 11 sectors
```

Run it with `python src/data.py`.

### Stage 2 — `features.py`: turn prices into 32 descriptions

Input: `panel_clean.pkl`.

A feature is one number describing the stock's recent situation. We build 32 of them,
grouped into 7 families:

| Family | Features | What it is in plain words |
|---|---|---|
| Past returns (6) | `ret_1d` `ret_2d` `ret_5d` `ret_10d` `ret_20d` `ret_60d` | how much it has already moved over the last 1, 2, 5, 10, 20, 60 days |
| Trend (5) | `dist_sma5/20/50/200`, `macd_hist` | how far above or below its own moving average it sits (a moving average is the mean price over the last N days) |
| Oscillators (3) | `rsi_14`, `stoch_k14`, `bb_pctb20` | standard chart indicators that say "overbought" or "oversold" |
| Volatility (6) | `vol_5d/20d/60d`, `atr_14`, `range_1d`, `bb_width20` | how jumpy it has been (volatility = the standard deviation of daily moves) |
| Volume (3) | `volume_ratio_20d`, `volume_trend_5_20`, `dollar_volume_log` | how many shares are changing hands versus normal |
| Candle (3) | `gap_open`, `body_1d`, `close_pos_range` | the shape of today's bar: did it gap open, did it close near its high |
| Market & sector (6) | `mkt_ret_1d`, `mkt_ret_5d`, `mkt_vol_20d`, `sector_ret_5d`, `rel_ret_20d`, `beta_60d` | what the whole market and the stock's own sector did, and how strongly this stock normally follows the market (beta) |

The single most important rule in the whole project is on line 1 of this file's
docstring: every feature for (stock, day t) uses only prices up to and including day
t's close. If a feature accidentally peeked at tomorrow, the model would look brilliant
and be useless. That is called leakage.

The targets — the thing we are trying to predict:

- `target_ret` = tomorrow's log return = `log(close_tomorrow / close_today)`. A log
  return is just a percentage change written in a way that adds up neatly over time.
  We report it in basis points (bp); 1 bp = 0.01%, so a 1% move is 100 bp.
- `target_close` = tomorrow's closing price in dollars.
- `target_up` = 1 if tomorrow's return is positive.

Rows with any missing feature or missing target are dropped.

Output: `data/features.pkl`.

```
32 features in 7 families; 1,097,165 usable stock-days
2013-03-01 -> 2022-05-24, 474 stocks, share of up days 0.526
```

A stock-day is one row: one company on one calendar day. 1.1 million of them.

### Stage 3 — `tune.py`: pick the model's settings honestly

Input: `features.pkl`.

A Random Forest has knobs (hyperparameters — settings you choose rather than learn).
We try 6 combinations:

- `min_samples_leaf` ∈ {200, 1000, 5000} — the smallest group of examples a tree is
  allowed to end on. Bigger = smoother, less overfitting.
- `max_features` ∈ {0.3, 0.6} — how many of the 32 features each split may consider.

Each combination is trained twice and scored on a year it never saw: once scored on
2017, once on 2018. The test period (2019 onward) is not touched here at all — that is
what makes the later test numbers honest.

Scoring criterion: mean squared error of the next-day return.

```
leaf   200 mf 0.3: MSE 2.6279e-04   leaf   200 mf 0.6: MSE 2.7131e-04
leaf  1000 mf 0.3: MSE 2.5765e-04   leaf  1000 mf 0.6: MSE 2.5987e-04
leaf  5000 mf 0.3: MSE 2.5641e-04   <-- chosen   leaf  5000 mf 0.6: MSE 2.5780e-04
```

Output: `results/tuning.json`, chosen settings
`{min_samples_leaf: 5000, max_features: 0.3, max_samples: 0.25, n_estimators: 300}`.
300 trees, each tree seeing a random 25% of the rows.

Notice the winner is the most heavily smoothed option on the grid. That is the first
hint that there is almost no signal to find: the data is telling us to barely fit it.

### Stage 4 — `train.py`: walk forward and forecast 405,545 days

Inputs: `features.pkl`, `panel_clean.pkl` (for the price-level features), `tuning.json`.

Walk-forward means: to forecast year Y, train only on data before year Y, then move
forward and retrain. Four passes:

| Test year | Trained on | Forecasts made | Time |
|---|---|---|---|
| 2019 | 691,620 stock-days | 119,340 | 96 s |
| 2020 | 810,960 | 119,919 | 120 s |
| 2021 | 930,879 | 119,448 | 160 s |
| 2022 (to May) | 1,050,327 | 46,838 | 185 s |

Four models are fitted every year:

1. `rf_reg` — Random Forest regressor, 32 features → next-day log return. This is the
   proposed model. A Random Forest is a few hundred decision trees, each trained on a
   random slice of the data, whose answers are averaged.
2. `rf_clf` — Random Forest classifier, same features → probability tomorrow is up.
3. `ridge` — Ridge regression, the simple linear baseline. Ridge is linear regression
   with a penalty that keeps the coefficients small.
4. `rf_level` — Random Forest on raw dollar prices (close, 4 lags, 4 moving averages)
   → tomorrow's dollar close. This is what most published papers do. It is included on
   purpose, to show it breaks.

The price forecast is always `close_today × exp(predicted_return)`. The model never
predicts a dollar price directly; a dollar price is only the return applied to today's
close. That distinction is the spine of the whole evaluation.

Outputs:
- `results/predictions.pkl` — 405,545 rows, one per forecast, with every model's answer
  and the truth beside it.
- `models/rf_reg_2019..2022.joblib` and `rf_clf_2019..2022.joblib` — the 8 saved models.
  These get reloaded by `explain.py`, `lime_explain.py` and `app.py`.
- `results/mdi_importance.json` — the forest's built-in importance scores.

### Stage 5 — `evaluate.py`: how good is it, really

Input: `predictions.pkl`. Output: `results/metrics.json`.

The test set: 405,545 stock-days over 856 trading days. On an average day a stock moves
245.5 bp (about 2.5%). That is the number every forecast has to beat.

Six baselines and models are scored in two different spaces.

Return space — what the model actually predicts:

| Model | RMSE (bp) | R² vs zero | IC | direction | DM p |
|---|---|---|---|---|---|
| Naive (tomorrow = today) | 245.5 | 0.00000 | — | 47.16% | — |
| Historical drift | 245.5 | +0.00043 | — | 52.84% | 0.635 |
| Ridge regression | 246.9 | −0.01076 | +0.0019 | 51.70% | 0.392 |
| RF on price levels | 250.4 | −0.03972 | +0.0063 | 50.85% | 0.000 |
| Random Forest (proposed) | 245.5 | +0.00013 | +0.0090 | 51.77% | 0.968 |
| always guess the majority direction | | | | 52.84% | |

Definitions:

- RMSE — root mean squared error, the typical size of a mistake.
- R² vs zero — out-of-sample R² against the forecast "tomorrow's return will be 0".
  R² of 0 means exactly as good as that do-nothing forecast; 1 would be perfect;
  negative means worse than doing nothing. Ours is +0.00013. That is 0.013% of the
  variation explained.
- IC — information coefficient. Each day, correlate the model's predicted returns
  across all stocks with what actually happened, then average over the 856 days. It
  asks "can it at least rank which stocks will do better than which?" +0.0090, with a
  t-statistic of 1.39 — not statistically distinguishable from zero.
- direction — share of days the sign was right. 51.77%, which is worse than the dumbest
  possible rule (always guess up, 52.84%).
- DM p — Diebold–Mariano test p-value. A formal test of "is this model's error
  genuinely smaller than the baseline's, or is the difference noise?" p = 0.968 means
  no evidence at all. For `rf_level`, p = 0.000 and the statistic is positive, meaning
  it is significantly worse.

Price space — what the literature reports:

| Model | MAPE | RMSE $ | R² price | "accuracy" |
|---|---|---|---|---|
| Naive | 1.561% | $6.25 | 0.99938 | 98.44% |
| Random Forest (proposed) | 1.560% | $6.25 | 0.99938 | 98.44% |
| RF on price levels | 1.583% | $21.56 | 0.99261 | 98.42% |

This is the project's headline finding. The same Random Forest forecasts score R²
0.99938 in price space and +0.00013 in return space. They are not two models — they are
one set of numbers scored two ways. The 99.9% is an artefact: prices barely move
day to day, so "tomorrow ≈ today" is already 98.44% accurate, and copying today's price
gets you the identical score to three decimal places.

Economic view — if you traded it. Sort each day's stocks into 10 buckets by predicted
return (deciles) and look at what each bucket actually did, in bp per day:

```
decile 1 .. 10:  +1.3  +6.2  +3.8  +5.2  +6.2  +4.6  +5.8  +6.4  +6.4  +9.5
long-short (buy decile 10, sell decile 1): +8.17 bp/day, t = 1.54,
annual Sharpe 0.83, net of 10 bp costs: -1.83 bp/day
```

The ranking does slope the right way (Spearman monotonicity 0.745), but t = 1.54 is not
significant, and once you subtract a realistic 10 bp round-trip trading cost it is
negative. A Sharpe ratio is return divided by its own volatility; 0.83 would be decent,
but it does not survive the cost.

Where the little skill lives — by regime:

| Regime | n | R² vs zero | IC | direction | DM p | long-short |
|---|---|---|---|---|---|---|
| Pre-COVID bull | 134,982 | +0.00069 | +0.0148 | 53.03% | 0.865 | +6.9 bp |
| COVID crash | 10,901 | −0.01171 | −0.0732 | 34.68% | 0.127 | −119.0 bp |
| Recovery | 212,824 | +0.00665 | +0.0076 | 51.65% | 0.043 | +16.1 bp |
| 2022 bear | 46,838 | −0.00113 | +0.0180 | 52.68% | 0.913 | +5.6 bp |

Two things only visible here:

- The Recovery is the one period with statistically significant skill, p = 0.043.
- During the COVID crash the model inverted. IC went negative, direction accuracy fell
  to 34.68% (worse than a coin), and the long-short lost 119 bp a day. It had learned a
  relationship that reversed sign exactly when it mattered most.

### Stage 6 — `explain.py`: explain it, then audit the explanation

This is the core of the project. 314 lines, runs in about 5 minutes.

Inputs: `features.pkl`, the four saved `rf_reg_*.joblib` models, `tuning.json`.

It samples 40 stocks per test day plus 5 focus tickers (AAPL, MSFT, JPM, XOM, PFE) on
every single day, giving 38,183 stock-days to explain. Each stock-day is explained by
its own year's model — the 2020 model explains 2020 days.

Four explanation jobs:

X1 — three explainers, do they agree?

- TreeSHAP. SHAP comes from game theory: it splits a prediction into one contribution
  per feature, such that base value + sum of contributions = exactly the prediction.
  TreeSHAP computes this exactly for tree models. The code verifies the adding-up
  property every run — measured error 1e-17, i.e. floating-point dust.
- Permutation importance. Shuffle one feature's column and see how much worse the model
  gets. Measured on up to 60,000 rows per year, 3 repeats.
- MDI (mean decrease in impurity). The forest's own built-in score, free but known to
  be biased toward features with many distinct values.

Agreement measured with Kendall's tau (a rank correlation: 1 = identical ordering,
0 = unrelated) and top-5 overlap:

```
SHAP vs MDI          tau 0.69   top-5 overlap 0.80
SHAP vs permutation  tau 0.03   top-5 overlap 0.60
permutation vs MDI   tau 0.15   top-5 overlap 0.80
only 12.5% of permutation importances exceed 2 standard errors
```

The three "importances" mostly do not agree. But the reason is itself informative: when
a model has essentially no skill, shuffling a feature barely changes its error, so
permutation importance is almost all noise — only 4 of 32 features clear 2 standard
errors. The top 5 still overlap 60–80% because the handful of features that matter are
obvious.

Top features by mean |SHAP|, in bp:

```
mkt_vol_20d     5.37    (how volatile the whole market has been, 20 days)
mkt_ret_5d      3.33    (the market's last week)
mkt_ret_1d      3.28    (the market's yesterday)
gap_open        0.77
ret_1d          0.57
sector_ret_5d   0.53
atr_14          0.43
```

X2 — family shares. Of all the attribution the model hands out, what share goes to each
family:

```
Market & sector  72.2%     Volatility   7.6%     Past returns  7.0%
Candle            5.9%     Trend        3.8%     Oscillators   2.0%     Volume  1.5%
```

Nearly three quarters of the model is about the market, not the individual stock. The
model has essentially learned "tomorrow depends on what the whole market is doing" —
which is true, and also not tradeable, because it says nothing about which stock to
pick.

X3 — local explanations. Four named stock-days broken down feature by feature in bp,
with the dollar equivalent alongside. A local explanation explains one single
prediction, as opposed to a global one which describes the model overall.

X4 — does the explanation drift? Family shares are computed per regime and per sector,
and compared with a permutation test. A permutation test builds the "what would random
look like" distribution by shuffling labels 1,000 times; the p-value is how often random
beat what we actually saw. Shuffling is done by whole day (for regimes) and whole ticker
(for sectors), so that days stay intact.

```
across regimes:  mean pairwise TVD 0.054 vs 0.017 if random, p = 0.003
across sectors:  mean pairwise TVD 0.036,                    p = 0.001
```

TVD is total variation distance, a 0-to-1 measure of how different two share-vectors
are. Both are significant: the explanation genuinely changes with the market regime and
with the sector. `mkt_vol_20d` is still the top feature in all four regimes, so the
headline is stable, but what sits behind it moves.

Then three reliability checks. These are the part a normal XAI project skips.

R1 — faithfulness. Does the explanation describe the model, or is it decoration? Take
the features SHAP called most important, replace them with values from 32 random
background rows, and see how much the forecast moves. Compare against deleting features
in random order. Measured on 2,000 stock-days.

```
features deleted:   1      2      4      8      16     32
by |SHAP| rank:    8.70   8.39   8.36   8.47   8.56   8.59  bp
in random order:   0.65   1.19   2.04   3.65   5.88   8.59  bp

AOPC: 8.51 bp (SHAP order) vs 3.67 bp (random order) = 2.3x
fidelity correlation between SHAP mass removed and actual forecast change:
  0.984 at k=1, rising to 1.000 at k=32
```

AOPC is the area over the deletion curve, i.e. the average displacement. SHAP passes:
deleting the one feature it named moves the forecast 13× more than deleting a random
one, and almost everything is already captured by the first feature (8.70 of the eventual
8.59 bp). Fidelity 0.98+ means the amount SHAP said each feature was worth really does
predict how much the forecast moves when you take it away.

R2 — stability. Same data, 5 different random seeds, then consecutive yearly retrains.

```
across 5 seeds:   Kendall tau 0.85   top-5 overlap 0.92
                  per-row Spearman 0.86   prediction correlation 0.990
across retrains:  2019 vs 2020 tau 0.75    2020 vs 2021 tau 0.44    2021 vs 2022 tau 0.77
```

Reasonably stable across seeds. Much less stable across retrains — the 2020 and 2021
models give noticeably different explanations of the same rows, which is the COVID
regime shift showing up in the explanation.

R3 — the sanity check, and the sharpest test in the project. Train a forest on labels
that have been shuffled, so there is provably nothing to learn, then explain it. If the
nonsense model's explanation looks like the real model's, the explanation was describing
the shape of the features, not anything learned.

Two nulls:

```
                      tau vs real   total |SHAP| (bp)   test IC    pred sd (bp)
real model                  —            20.85          +0.018        9.65
labels fully shuffled      0.13           2.59          -0.023        0.88
returns shuffled within    0.56          19.54          +0.011        9.62
  each day
```

Read it this way. The fully shuffled model is harmless: it knows nothing, it says
nothing (its predictions barely vary, 0.88 bp), and its explanation looks nothing like
the real one (tau 0.13). Good — SHAP is not hallucinating structure out of thin air.

The within-day shuffled model is the uncomfortable one. We kept each day's market-wide
move but scrambled which stock got which return, so all stock-specific information is
destroyed. It still produces 19.54 bp of attribution versus the real model's 20.85, and
its explanation matches the real model's at tau 0.56 with 80% top-5 overlap. That is
direct evidence for the X2 finding: most of what the real model "knows" is the market-
wide component, which survives the shuffle, and only a thin slice is genuine
stock-specific learning.

Outputs: `results/xai.json` (all of the above), `results/importance.csv` (32 rows ×
4 importance measures), `results/shap_sample.pkl` (the 38,183 × 32 SHAP matrix, which
`lime_explain.py` needs).

### Stage 7 — `lime_explain.py`: the second opinion

Inputs: `shap_sample.pkl`, `importance.csv`, `features.pkl`, the saved models.

LIME works completely differently from SHAP. To explain one prediction it generates
5,000 fake nearby inputs, asks the model what it thinks of each, and fits a small
weighted linear model to those answers. The linear model's coefficients are the
explanation. It is model-agnostic (works on anything) but approximate and random.

Run on 804 stock-days (200 per test year plus the 4 named cases), each explained 5
times with 5 different seeds. About 6 minutes.

L2 — global agreement:

```
TreeSHAP vs LIME         tau 0.58   top-5 overlap 0.80
TreeSHAP vs MDI          tau 0.69   top-5 overlap 0.80
LIME vs MDI              tau 0.65   top-5 overlap 0.80
TreeSHAP vs permutation  tau 0.03   top-5 overlap 0.60
LIME vs permutation      tau 0.18   top-5 overlap 0.60
```

L3 — agreement with SHAP on the same individual stock-day:

```
median Spearman 0.44    top-5 overlap 0.65
same single top feature on only 59.1% of stock-days
but when they do share a feature, they agree on its sign 80.7% of the time
```

So on 4 stock-days out of 10, the two standard explanation tools point at a different
most-important feature for the same forecast from the same model. Averaged over
hundreds of rows they look similar; row by row they often disagree. If you were going
to act on a single explanation, that matters a lot.

L4 — LIME's run-to-run stability. TreeSHAP is deterministic: re-run it and you get
bit-identical numbers, so its self-agreement is exactly 1 by construction. LIME:

```
between its own 5 seeds:  median Spearman 0.45   top-5 overlap 0.79
names the same top feature in all 5 runs on 95.8% of stock-days
```

The headline survives re-running, the detailed ranking does not.

A real bug was found and fixed here. `LimeTabularExplainer` binds its random state into
the discretiser and the surrogate solver when you construct it, so setting
`.random_state` afterwards controls only part of the sampling. Measured: a reused
explainer with the same seed gave Spearman 0.46–0.53 between supposedly identical
repeats; a freshly constructed one with the same seed gives exactly 1.000. The fix is
`make_explainer()`, which builds one per seed at a cost of 18 ms. After the fix the
global SHAP-LIME tau moved from 0.73 to 0.58 — the old number was inflated by LIME
quietly not being reproducible.

L5 — local fidelity. LIME reports its own surrogate's R², i.e. how well its little
linear model fitted the 5,000 samples it drew.

```
median R² 0.167    mean 0.223    67.4% of explanations below 0.3
```

Two thirds of LIME's explanations are built on a surrogate that explains less than 30%
of the local behaviour it is trying to approximate. This is the strongest single
argument in the project for preferring SHAP here.

L6 — faithfulness, same deletion test as R1, three orderings:

```
AOPC:  SHAP 8.70 bp    LIME 8.13 bp    Random 3.71 bp
```

Both beat random by more than 2×, so both are genuinely describing the model. SHAP is
somewhat better, and much better at k=1 (8.89 vs 6.53 bp) — SHAP's single top feature is
more often the right one.

Outputs: `results/lime.json`, `results/lime_sample.pkl`.

### Stage 8 — `plots.py`: 15 figures

Reads `metrics.json`, `xai.json`, `lime.json`, `predictions.pkl`, `importance.csv`,
`shap_sample.pkl`, `lime_sample.pkl`. Writes `results/figures/`:

```
return_skill.png          price_vs_return.png        decile_portfolio.png
price_accuracy.png        price_paths_AAPL.png       shap_global.png
explainer_agreement.png   shap_dependence.png        local_explanations.png
regime_family_shares.png  sector_family_shares.png   faithfulness.png
stability_sanity.png      lime_vs_shap_local.png     lime_reliability.png
```

### Stage 9 — `live.py`: forecast a day that has not happened

Everything up to here forecasts the past, because the past is the only thing you can
grade. This file does the other half.

It downloads prices from Yahoo Finance for the same 474 tickers from 2012-05-14 to
today, rebuilds the identical 32 features by importing `build()` from `features.py`,
retrains with the identical hyperparameters from `tuning.json`, and forecasts the next
session.

The one critical difference is a single line. In `features.py` the rows with no
`target_ret` are dropped, which throws away the most recent day. Here they are kept:

```python
df = df.dropna(subset=FEATURES + ["close"])   # NOT on the target: the last day has none
train = df.dropna(subset=["target_ret"])      # train on everything with a known outcome
live  = df[df.date == last_day].copy()        # forecast the one day with no outcome
assert live.target_ret.isna().all(), "the last day already has a known outcome - rerun after the close"
```

That assertion is the honesty guard. If you run it mid-session the last day already has
an outcome and the script refuses rather than quietly "forecasting" something it can
already see.

Current state, from `results/live_meta.json`:

```
as of close           2026-10-29
forecast for          the next trading session
stocks                431
retrained on          1,473,486 stock-days, through 2026-10-28
source                Yahoo Finance via yfinance, split- and dividend-adjusted
no longer trading     43 of the original 474 tickers (ATVI, TWTR, SIVB, FRC, ...)
```

Those 43 missing tickers are survivorship bias (the dataset only contains companies
that are still around, which quietly flatters any backtest) made visible rather than
hidden — the page lists them.

Outputs: `data/live_panel.pkl`, `data/live_features.pkl`, `models/rf_reg_live.joblib`,
`results/live_forecast.pkl`, `results/live_meta.json`.

### Stage 10 — `app.py` + `static/index.html`: the demo

`app.py` is a 299-line server using only the Python standard library — no Flask, no
Django. On startup it loads:

```
features: 405,545 explainable stock-days, 474 stocks
price history: 2,526 days x 474 stocks
live forecast: 431 stocks for the session after 2026-10-29
4 models + 4 TreeSHAP explainers + 4 LIME reference samples (5,000 rows each)
```

Three API endpoints:

| Endpoint | Returns |
|---|---|
| `GET /api/meta` | the ticker list, date range, the 5 suggested cases, live metadata |
| `GET /api/dates?ticker=AAPL` | which dates that stock can be explained on |
| `GET /api/explain?ticker=AAPL&date=2020-03-16` | the whole thing: forecast, SHAP, LIME × 5 seeds, agreement, faithfulness |

Nothing is read back from a cached results file. Every request runs TreeSHAP once and
LIME five times, live, on the saved model. A request takes a few seconds, and a lock
serialises them because LIME needs the model switched to single-threaded.

The key function is `explain(ticker, date, live=False)`. The `live=True` branch swaps in
the retrained live model and the next-session row; everything else — SHAP, the 5 LIME
runs, the agreement maths, the faithfulness probe — is literally the same code. That is
deliberate, so nobody can claim the live demo is a different, friendlier pipeline.

`faithfulness()` is R1 shrunk to one forecast: take SHAP's single top feature, replace
it with the 32 background values and measure the move; do the same for 8 random
features; report the ratio.

---

## 3. Who calls whom

```
config.py  <-- imported by all 9 others (paths, dates, regimes, seed)

features.py --- FEATURES, FAMILIES, build()
     |
     +--> tune.py, train.py, evaluate.py (indirectly), explain.py, app.py
     +--> live.py            calls build() on freshly downloaded prices

explain.py  --- K_STEPS, N_BACKGROUND, rank_agreement()
     |
     +--> lime_explain.py    reuses the deletion-test settings so the two
                             faithfulness numbers are comparable

lime_explain.py --- lime_weights(), make_explainer()
     |
     +--> app.py             the demo runs the same LIME code as the study

evaluate.py --- add_forecasts()
     |
     +--> plots.py

train.py  --> models/*.joblib --> explain.py, lime_explain.py, app.py
live.py   --> rf_reg_live.joblib --> app.py
```

Nothing is duplicated. The demo cannot drift away from the study, because it imports
the study's functions.

---

## 4. Input and output, at every level

At the level of one prediction:

- Input: 32 numbers describing one stock on one day. For AAPL on 2026-10-29 that is
  `mkt_vol_20d` = how jumpy the market has been, `ret_1d` = yesterday's move, and 30
  others.
- Output: one number, the predicted log return for the next session, in bp. AAPL:
  −4.05 bp, which applied to a $348.91 close gives a predicted $348.77.

At the level of the study:

- Input: 474 stocks × 2,526 days of OHLCV, 2012-05-14 to 2022-05-25.
- Output: 405,545 graded forecasts, 15 figures, and a 45 KB report.

At the level of the demo, what you type and what you get back:

You choose two things — a stock (474 of them, or 431 in live mode) and either a date
between 2019-01-02 and 2022-05-24, or "next session".

You get back, on one page:

1. The forecast. Predicted return in bp, predicted close in dollars, the probability
   that tomorrow is up, and in past mode the actual outcome and whether the direction
   was right.
2. A price chart. The last 60 closes, a dashed line to the forecast, and a shaded band
   of one standard deviation of this stock's recent daily moves — so you can see at a
   glance that the forecast is far smaller than a normal day's move.
3. A SHAP waterfall. Starts at the average forecast over all stock-days, adds the top 8
   features one at a time, lumps the other 24 together, and lands exactly on the
   forecast.
4. Two bar charts side by side — SHAP and LIME on the same forecast — plus a table of
   all 32 features with both attributions.
5. Do they agree? Spearman correlation, top-5 overlap, whether they name the same top
   feature, sign agreement.
6. Is each one stable? LIME re-run 5 times with the top feature each run; SHAP marked
   deterministic.
7. Is the explanation faithful? Delete SHAP's top feature, compare the forecast's move
   against deleting 8 random features, report the ratio.

So the input is (stock, date) and the output is a forecast plus a complete audit of the
explanation of that forecast. The audit is the product.

---

## 5. The explainability architecture

This is the bit to be able to draw on a whiteboard.

```
                      32 features for one stock-day
                                  |
                                  v
                    +---------------------------+
                    |  Random Forest regressor  |   300 trees, leaf >= 5000
                    |  predicts next-day return |
                    +---------------------------+
                                  |
                 +----------------+----------------+
                 |                                 |
                 v                                 v
         +---------------+                 +---------------+
         |   TreeSHAP    |                 |     LIME      |
         | exact, additive|                | 5,000 samples |
         | deterministic |                 | linear surrogate|
         +---------------+                 +---------------+
                 |                                 |
                 +----------------+----------------+
                                  |
                                  v
                    +-------------------------------+
                    |      FIVE AUDIT QUESTIONS     |
                    +-------------------------------+
                      |     |      |      |      |
                      v     v      v      v      v
                    agree? faithful? stable? fooled? drifting?
                      |     |      |      |      |
                 tau 0.58  2.3x  tau 0.85  tau   p=0.003
                 rho 0.44  AOPC  (seeds)   0.56   regimes
                 59% same  8.5 vs 0.44    (within- p=0.001
                 top       3.7bp (LIME)    day)   sectors
```

The five questions, and why each one exists:

1. Do two independent explainers agree? If two respected methods explaining the same
   model disagree, at most one of them can be describing the model. Answer: globally
   yes (tau 0.58), per-forecast often no (same top feature 59% of the time).
2. Is the explanation faithful? Delete what it called important; the forecast must move
   more than when you delete something random. Answer: yes, 2.3× by AOPC, with
   fidelity correlation 0.98+. Both methods pass. SHAP passes more cleanly.
3. Is it stable? Re-run it. Answer: SHAP is exactly reproducible by construction; LIME
   agrees with itself at Spearman 0.45 but keeps its top feature 95.8% of the time; the
   model's explanation is stable across seeds (tau 0.85) and shakier across retrains
   (tau 0.44 between the 2020 and 2021 models).
4. Can it be fooled? Explain a model trained on shuffled labels. Answer: a fully
   shuffled model is correctly exposed (tau 0.13, attribution collapses from 20.85 to
   2.59 bp). A within-day-shuffled model is not (tau 0.56, 19.54 bp) — and that is a
   finding about the model, not a failure of SHAP: most of what the model knows is the
   market-wide move, which that shuffle leaves intact.
5. Does it drift? Family shares per regime and per sector against a 1,000-permutation
   null. Answer: yes, significantly (p = 0.003 and p = 0.001). An explanation computed
   in one regime should not be quoted in another.

And the finding that ties the explanation back to the forecast: 72.2% of all
attribution goes to the Market & sector family, with `mkt_vol_20d` the top feature in
every one of the four regimes. The explanation and the performance agree with each
other. The model has learned the market-wide component of tomorrow's return, which is
real but says nothing about which stock to buy — which is exactly why the IC is +0.0090
and the long-short spread dies once you pay for trading. The XAI did not just decorate
the model. It diagnosed it.

---

## 6. Honest summary of the results

What was built: a complete, leakage-free, walk-forward return forecasting pipeline over
1.1 million stock-days with two explainers and a five-part explanation audit.

What it found:

1. Price-space accuracy metrics are an artefact. The same forecasts score R² 0.99938 on
   price and +0.00013 on return. Naive persistence ties them to three decimals at
   98.44% "accuracy". Any paper reporting 98% accuracy on daily closes without a naive
   baseline has reported nothing.
2. Random Forests on raw price levels break. R² $21.56 RMSE versus $6.25 — trees cannot
   extrapolate past the price range they were trained on. DM p = 0.000 worse.
3. Skill in return space is near zero, and that is the honest answer. R² +0.00013,
   IC +0.0090 (t = 1.39), direction 51.77% against a 52.84% majority rule.
4. The small amount of skill is concentrated in one regime (Recovery, p = 0.043) and
   inverts in another (COVID crash, IC −0.073, direction 34.68%).
5. SHAP and LIME both pass faithfulness, but LIME's own surrogate R² is below 0.3 on
   two thirds of explanations, and they name a different top feature on 41% of
   forecasts.
6. Explanations drift significantly across regimes and sectors.
7. The within-day-shuffled sanity null is nearly indistinguishable from the real model,
   which pins down what the model actually learned: the market factor, not stock
   selection.
8. A reproducibility defect in the common LIME usage pattern was found, measured and
   fixed. The inflated agreement number it caused (0.73 vs the correct 0.58) is the
   kind of thing that gets published unnoticed.

What it is not: a trading signal. Do not claim it is. The long-short spread is
+8.17 bp/day before costs, t = 1.54, and −1.83 bp/day after a realistic 10 bp
round-trip. The project's value is the methodology and the audit, and that is a
defensible thing to have built.

---

## 7. Glossary

| Term | Short definition |
|---|---|
| stock-day | one row: one company on one calendar day |
| feature | one number describing a stock's recent situation |
| target | the thing being predicted: tomorrow's log return |
| log return | `log(price_tomorrow / price_today)`, a percentage change that adds up over time |
| basis point (bp) | 0.01%. A 1% move is 100 bp |
| leakage | a feature accidentally containing future information |
| walk-forward | train only on the past, forecast forward, retrain, repeat |
| hyperparameter | a setting you choose rather than learn (e.g. number of trees) |
| Random Forest | hundreds of decision trees on random data slices, averaged |
| Ridge regression | linear regression with a penalty keeping coefficients small |
| RMSE | root mean squared error: the typical size of a mistake |
| MAPE | mean absolute percentage error |
| out-of-sample R² | 1 = perfect, 0 = no better than the baseline, negative = worse |
| IC | information coefficient: daily cross-sectional correlation of forecast with outcome |
| ICIR | IC divided by its own standard deviation across days |
| Diebold–Mariano | formal test of whether one forecast's errors are really smaller |
| p-value | how often pure chance would produce what we saw; small = unlikely to be luck |
| decile | one tenth of the stocks, after sorting them |
| long-short spread | return of buying the top decile and selling the bottom one |
| Sharpe ratio | return divided by its own volatility; higher is better |
| SHAP | splits a prediction into exact per-feature contributions that sum to it |
| TreeSHAP | the exact, fast SHAP algorithm for tree models; deterministic |
| base value | the model's average prediction; SHAP contributions start from here |
| LIME | explains one prediction by fitting a small linear model to 5,000 nearby fakes |
| surrogate R² | how well LIME's little linear model fitted its own samples |
| permutation importance | shuffle a feature's column, see how much worse the model gets |
| MDI | the forest's built-in importance; free but biased |
| Kendall's tau | rank correlation: 1 = same order, 0 = unrelated |
| Spearman rho | correlation of ranks rather than values |
| AOPC | area over the deletion curve: average displacement when features are removed |
| faithfulness | whether the explanation really describes the model's behaviour |
| fidelity | whether the attribution size predicts the actual forecast change |
| sanity check | explaining a model trained on shuffled labels, which knows nothing |
| permutation test | build the random baseline by shuffling labels 1,000 times |
| TVD | total variation distance: 0-to-1 difference between two share-vectors |
| regime | a named stretch of time with a particular market mood |
| GICS sector | the standard 11-way industry classification |
| survivorship bias | dataset only contains companies still around, flattering any backtest |

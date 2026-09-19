"""Walk-forward training and next-day forecasts for the test period (2019 .. 2022-05).

At the start of each test year every model is retrained on all stock-days from TRAIN_START
up to the last day of the previous year, then forecasts every stock-day of that year.

Models
  rf_reg     Random Forest regressor on the 32 features -> next-day log return.
             Price forecast = close_t * exp(predicted return).   (main model)
  rf_clf     Random Forest classifier on the same features -> P(next-day return > 0)
  ridge      Ridge regression on the same (standardised) features -> next-day log return
  rf_level   Random Forest on raw price LEVELS (close, lags, moving averages in $) ->
             next-day close. The common approach in the literature, kept to show its
             extrapolation problem.
Baselines computed in evaluate.py: naive persistence (tomorrow = today) and historical drift.

    python src/train.py
"""
import json
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from config import FEATURE_FILE, MODELS, PANEL_FILE, RESULTS, SEED, TEST_YEARS, TRAIN_START
from features import FEATURES

LEVEL_FEATURES = ["lvl_close", "lvl_close_l1", "lvl_close_l2", "lvl_close_l3", "lvl_close_l4",
                  "lvl_open", "lvl_high", "lvl_low", "lvl_sma5", "lvl_sma20", "lvl_sma50", "lvl_sma200"]


def level_features(panel):
    wide = {k: panel.pivot(index="date", columns="ticker", values=k) for k in ("open", "high", "low", "close")}
    c = wide["close"]
    f = {"lvl_close": c, "lvl_open": wide["open"], "lvl_high": wide["high"], "lvl_low": wide["low"]}
    for lag in range(1, 5):
        f[f"lvl_close_l{lag}"] = c.shift(lag)
    for n in (5, 20, 50, 200):
        f[f"lvl_sma{n}"] = c.rolling(n, min_periods=n).mean()
    out = pd.DataFrame({k: v.stack(future_stack=True) for k, v in f.items()})
    return out.rename_axis(["date", "ticker"]).reset_index()


def rf_params(chosen, **overrides):
    p = dict(n_estimators=chosen["n_estimators"], min_samples_leaf=chosen["min_samples_leaf"],
             max_features=chosen["max_features"], max_samples=chosen["max_samples"],
             n_jobs=-1, random_state=SEED)
    p.update(overrides)
    return p


def main():
    chosen = json.loads((RESULTS / "tuning.json").read_text())["chosen"]
    df = pd.read_pickle(FEATURE_FILE)
    df = df.merge(level_features(pd.read_pickle(PANEL_FILE)), on=["date", "ticker"], how="left")
    MODELS.mkdir(exist_ok=True)
    preds, importances = [], {}
    print("RF hyperparameters (from validation):", chosen)

    for year in TEST_YEARS:
        t0 = time.time()
        train = df[(df.date >= TRAIN_START) & (df.date < f"{year}-01-01")]
        test = df[(df.date >= f"{year}-01-01") & (df.date < f"{year + 1}-01-01")].copy()
        X, Xt = train[FEATURES].values, test[FEATURES].values

        rf_reg = RandomForestRegressor(**rf_params(chosen)).fit(X, train.target_ret.values)
        rf_clf = RandomForestClassifier(**rf_params(chosen)).fit(X, train.target_up.values)
        ridge = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-2, 4, 13))).fit(X, train.target_ret.values)
        lvl_train = train.dropna(subset=LEVEL_FEATURES)
        rf_level = RandomForestRegressor(n_estimators=200, min_samples_leaf=5, max_features=0.6, max_samples=0.25,
                                         n_jobs=-1, random_state=SEED).fit(lvl_train[LEVEL_FEATURES].values,
                                                                           lvl_train.target_close.values)

        test["year"] = year
        test["pred_ret_rf"] = rf_reg.predict(Xt)
        test["prob_up_rf"] = rf_clf.predict_proba(Xt)[:, 1]
        test["pred_ret_ridge"] = ridge.predict(Xt)
        assert not test[LEVEL_FEATURES].isna().any().any(), "level features missing in test rows"
        test["pred_close_rf_level"] = rf_level.predict(test[LEVEL_FEATURES].values)
        test["train_mean_ret"] = train.target_ret.mean()
        preds.append(test[["date", "ticker", "sector", "year", "close", "target_close", "target_ret", "target_up",
                           "pred_ret_rf", "prob_up_rf", "pred_ret_ridge", "pred_close_rf_level", "train_mean_ret"]])

        joblib.dump(rf_reg, MODELS / f"rf_reg_{year}.joblib", compress=3)
        joblib.dump(rf_clf, MODELS / f"rf_clf_{year}.joblib", compress=3)
        importances[year] = dict(zip(FEATURES, rf_reg.feature_importances_.round(6).tolist()))
        print(f"{year}: trained on {len(train):,} stock-days, forecast {len(test):,} "
              f"(ridge alpha {ridge[-1].alpha_:.3g}) in {time.time() - t0:.0f}s", flush=True)

    out = pd.concat(preds, ignore_index=True)
    out.to_pickle(RESULTS / "predictions.pkl")
    (RESULTS / "mdi_importance.json").write_text(json.dumps(importances, indent=2))
    print(f"saved {len(out):,} forecasts to results/predictions.pkl")


if __name__ == "__main__":
    main()

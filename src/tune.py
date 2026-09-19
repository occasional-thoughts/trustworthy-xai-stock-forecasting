"""Choose Random Forest hyperparameters on two validation years (2017 and 2018).

For each fold the model is trained on 2013-03 .. the day before the validation year and
scored on that year. The test period (2019 onward) is never used here. Selection
criterion: mean validation MSE of the next-day log return over both folds.

    python src/tune.py
"""
import itertools
import json
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from config import FEATURE_FILE, RESULTS, SEED, TRAIN_START
from features import FEATURES

FOLDS = [("2017-01-01", "2018-01-01"), ("2018-01-01", "2019-01-01")]
GRID = {"min_samples_leaf": [200, 1000, 5000], "max_features": [0.3, 0.6]}


def daily_ic(pred, y, dates):
    g = pd.DataFrame({"p": pred, "y": y, "d": dates})
    return g.groupby("d").apply(lambda x: x.p.corr(x.y)).mean()


def main():
    df = pd.read_pickle(FEATURE_FILE)
    rows = []
    for leaf, mf in itertools.product(GRID["min_samples_leaf"], GRID["max_features"]):
        scores = []
        for va0, va1 in FOLDS:
            tr = df[(df.date >= TRAIN_START) & (df.date < va0)]
            va = df[(df.date >= va0) & (df.date < va1)]
            t0 = time.time()
            rf = RandomForestRegressor(n_estimators=150, min_samples_leaf=leaf, max_features=mf,
                                       max_samples=0.25, n_jobs=-1, random_state=SEED)
            rf.fit(tr[FEATURES].values, tr.target_ret.values)
            pred = rf.predict(va[FEATURES].values)
            y = va.target_ret.values
            scores.append({"fold": va0[:4], "mse": float(np.mean((y - pred) ** 2)),
                           "mse_zero": float(np.mean(y ** 2)),
                           "ic": float(daily_ic(pred, y, va.date.values)),
                           "dir_acc": float(((pred > 0) == (y > 0)).mean()),
                           "fit_s": round(time.time() - t0, 1)})
        row = {"min_samples_leaf": leaf, "max_features": mf,
               "mean_mse": float(np.mean([s["mse"] for s in scores])),
               "mean_ic": float(np.mean([s["ic"] for s in scores])),
               "mean_dir_acc": float(np.mean([s["dir_acc"] for s in scores])),
               "folds": scores}
        rows.append(row)
        print(f"leaf {leaf:5d} max_features {mf}: MSE {row['mean_mse']:.4e}  IC {row['mean_ic']:+.4f}  "
              f"dir acc {row['mean_dir_acc']:.4f}  ({', '.join(str(s['fit_s']) + 's' for s in scores)})", flush=True)
    best = min(rows, key=lambda r: r["mean_mse"])
    chosen = {"min_samples_leaf": best["min_samples_leaf"], "max_features": best["max_features"],
              "max_samples": 0.25, "n_estimators": 300}
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "tuning.json").write_text(json.dumps({"grid": rows, "chosen": chosen}, indent=2))
    print("chosen:", chosen)


if __name__ == "__main__":
    main()

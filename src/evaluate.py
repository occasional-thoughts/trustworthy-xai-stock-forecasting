"""Forecast accuracy of every model on the test period, with baselines and significance tests.

Price accuracy (next-day close, in $):   MAE, RMSE, MAPE, R^2, share of forecasts within 1% / 2%
Return skill (beyond persistence):       out-of-sample R^2 vs a zero-return forecast, daily IC,
                                         Rank IC, direction accuracy, AUC (classifier)
Tests
  Diebold-Mariano (HAC)  daily cross-sectional mean squared %-error, model vs naive persistence
  Binomial               direction accuracy vs the "always up" rule on the same days
Every metric is reported overall, by test year, by market regime and by GICS sector.

    python src/evaluate.py
"""
import json

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_auc_score

from config import REGIMES, RESULTS

PRICE_MODELS = {
    "Naive (tomorrow = today)": "naive",
    "Historical drift": "drift",
    "Ridge regression": "ridge",
    "Random Forest on price levels": "rf_level",
    "Random Forest (proposed)": "rf",
}


def add_forecasts(p):
    p["price_naive"] = p["close"]
    p["price_drift"] = p["close"] * np.exp(p["train_mean_ret"])
    p["price_ridge"] = p["close"] * np.exp(p["pred_ret_ridge"])
    p["price_rf_level"] = p["pred_close_rf_level"]
    p["price_rf"] = p["close"] * np.exp(p["pred_ret_rf"])
    p["regime"] = "Other"
    for name, (a, b) in REGIMES.items():
        p.loc[(p.date >= a) & (p.date <= b), "regime"] = name
    return p


def dm_test(loss_a, loss_b, dates, lag=5):
    """Diebold-Mariano on the daily mean loss differential with a Newey-West variance.
    Negative statistic = model A has lower loss."""
    d = pd.Series(loss_a - loss_b).groupby(np.asarray(dates)).mean().values
    n, mean = len(d), d.mean()
    dc = d - mean
    var = dc @ dc / n
    for k in range(1, lag + 1):
        var += 2 * (1 - k / (lag + 1)) * (dc[k:] @ dc[:-k]) / n
    stat = mean / np.sqrt(var / n)
    return float(stat), float(2 * stats.norm.sf(abs(stat)))


def daily_corr(pred, y, dates, method="pearson"):
    g = pd.DataFrame({"p": pred, "y": y, "d": dates})
    s = g.groupby("d").apply(lambda x: x.p.corr(x.y, method=method))
    return float(s.mean()), float(s.mean() / s.std() * np.sqrt(len(s)))


def block(g):
    y_close, y_ret = g["target_close"].values, g["target_ret"].values
    out = {"n": int(len(g)), "days": int(g.date.nunique())}
    naive_sq_pct = ((y_close - g["price_naive"]) / y_close) ** 2
    for label, key in PRICE_MODELS.items():
        f = g[f"price_{key}"].values
        err = y_close - f
        pct = np.abs(err) / y_close
        m = {"MAE_$": float(np.abs(err).mean()), "RMSE_$": float(np.sqrt((err ** 2).mean())),
             "MAPE_%": float(100 * pct.mean()), "price_accuracy_%": float(100 * (1 - pct.mean())),
             "R2_price": float(1 - (err ** 2).sum() / ((y_close - y_close.mean()) ** 2).sum()),
             "within_1%": float((pct <= 0.01).mean()), "within_2%": float((pct <= 0.02).mean())}
        if key != "naive":
            stat, pval = dm_test((err / y_close) ** 2, naive_sq_pct, g.date.values)
            m["DM_vs_naive"], m["DM_p"] = stat, pval
        pred_ret = np.log(f / g["close"].values)
        if key not in ("naive",):
            m["R2_return_vs_zero"] = float(1 - ((y_ret - pred_ret) ** 2).sum() / (y_ret ** 2).sum())
            if np.std(pred_ret) > 0 and key != "drift":
                m["IC"], m["IC_t"] = daily_corr(pred_ret, y_ret, g.date.values)
                m["RankIC"], _ = daily_corr(pred_ret, y_ret, g.date.values, "spearman")
            hits = int(((pred_ret > 0) == (y_ret > 0)).sum())
            m["direction_acc"] = hits / len(g)
        out[label] = m

    up = g["target_up"].values
    always_up = float(up.mean())
    clf_pred = (g["prob_up_rf"].values > 0.5)
    hits = int((clf_pred == up).sum())
    out["Random Forest classifier"] = {
        "direction_acc": hits / len(g),
        "AUC": float(roc_auc_score(up, g["prob_up_rf"])) if 0 < up.mean() < 1 else None,
        "balanced_acc": float(0.5 * (clf_pred[up == 1].mean() + (~clf_pred[up == 0]).mean())),
        "binomial_p_vs_always_up": float(stats.binomtest(hits, len(g), max(always_up, 1 - always_up), "greater").pvalue),
    }
    out["always_up_acc"] = max(always_up, 1 - always_up)
    rf_hits = int(((g["pred_ret_rf"] > 0) == (y_ret > 0)).sum())
    out["Random Forest (proposed)"]["binomial_p_vs_always_up"] = float(
        stats.binomtest(rf_hits, len(g), max(always_up, 1 - always_up), "greater").pvalue)

    # Economic view: next-day return of the top decile of predicted returns minus the bottom decile.
    def spread(x):
        q = x["pred_ret_rf"].rank(pct=True)
        return x.loc[q > 0.9, "target_ret"].mean() - x.loc[q <= 0.1, "target_ret"].mean()
    s = g.groupby("date").apply(spread)
    out["long_short_decile_bp_per_day"] = float(1e4 * s.mean())
    out["long_short_t"] = float(s.mean() / s.std() * np.sqrt(len(s)))
    return out


def main():
    p = add_forecasts(pd.read_pickle(RESULTS / "predictions.pkl"))
    res = {"overall": block(p),
           "by_year": {int(y): block(g) for y, g in p.groupby("year")},
           "by_regime": {r: block(g) for r, g in p.groupby("regime") if r in REGIMES},
           "by_sector": {s: block(g) for s, g in p.groupby("sector")}}
    (RESULTS / "metrics.json").write_text(json.dumps(res, indent=2))
    o = res["overall"]
    print(f"test: {o['n']:,} stock-days over {o['days']} days")
    for label in PRICE_MODELS:
        m = o[label]
        extra = "" if "DM_vs_naive" not in m else f"  DM vs naive {m['DM_vs_naive']:+.2f} (p={m['DM_p']:.3f})"
        ic = f"  IC {m['IC']:+.4f} (t={m['IC_t']:+.2f})" if "IC" in m else ""
        acc = f"  dir {m['direction_acc']:.4f}" if "direction_acc" in m else ""
        print(f"{label:32s} MAPE {m['MAPE_%']:.3f}%  RMSE ${m['RMSE_$']:.2f}  R2 {m['R2_price']:.5f}  "
              f"within 2% {m['within_2%']:.3f}{acc}{ic}{extra}")
    c = o["Random Forest classifier"]
    print(f"RF classifier: acc {c['direction_acc']:.4f} AUC {c['AUC']:.4f} balanced {c['balanced_acc']:.4f} "
          f"(always-up {o['always_up_acc']:.4f}, p={c['binomial_p_vs_always_up']:.3f})")
    print(f"long-short decile: {o['long_short_decile_bp_per_day']:+.2f} bp/day (t={o['long_short_t']:+.2f})")
    for r, m in res["by_regime"].items():
        rf = m["Random Forest (proposed)"]
        print(f"  {r:15s} MAPE RF {rf['MAPE_%']:.3f}% vs naive {m['Naive (tomorrow = today)']['MAPE_%']:.3f}%  "
              f"dir {rf['direction_acc']:.4f}  IC {rf.get('IC', float('nan')):+.4f}")


if __name__ == "__main__":
    main()

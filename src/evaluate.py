"""Forecast skill of every model on the test period, with baselines and significance tests.

The target is the next-day LOG RETURN; a price forecast is only that return applied to
today's close. Return space is therefore where skill is measured, and it is reported first.
Price-space numbers are kept because the literature quotes them, and because the contrast
between the two is itself a result: the same forecasts look near-perfect in price space and
near-worthless in return space.

Return skill (primary)       MAE and RMSE in basis points, out-of-sample R^2 against a
                             zero-return and a drift forecast, daily IC, Rank IC, ICIR,
                             direction accuracy, AUC (classifier)
Price accuracy (secondary)   MAE, RMSE, MAPE, R^2, share of forecasts within 1% / 2%
Economic view                next-day return of deciles of the predicted return, the
                             long-short spread, its Sharpe ratio and its net-of-cost value
Tests
  Diebold-Mariano (HAC)  daily mean squared return error, model vs naive zero-return
                         (and, in price space, vs naive persistence)
  Binomial               direction accuracy vs the "always the majority direction" rule
Every metric is reported overall, by test year, by market regime and by GICS sector.

    python src/evaluate.py
"""
import json

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_auc_score

from config import REGIMES, RESULTS

# label -> suffix of the price_<key> / pred_ret_<key> columns built by add_forecasts
PRICE_MODELS = {
    "Naive (tomorrow = today)": "naive",
    "Historical drift": "drift",
    "Ridge regression": "ridge",
    "Random Forest on price levels": "rf_level",
    "Random Forest (proposed)": "rf",
}
MODELS = PRICE_MODELS
# Models whose forecast carries cross-sectional information, so an IC is meaningful.
RANKED = ("ridge", "rf_level", "rf")
COST_BP = 10.0      # assumed round-trip transaction cost for the net long-short figure
N_DECILES = 10


def add_forecasts(p):
    """One price forecast and one return forecast per model, from the same prediction."""
    p["price_naive"] = p["close"]
    p["price_drift"] = p["close"] * np.exp(p["train_mean_ret"])
    p["price_ridge"] = p["close"] * np.exp(p["pred_ret_ridge"])
    p["price_rf_level"] = p["pred_close_rf_level"]
    p["price_rf"] = p["close"] * np.exp(p["pred_ret_rf"])
    for key in PRICE_MODELS.values():
        # The return each model implies: 0 for naive, the model's own prediction otherwise.
        p[f"ret_{key}"] = np.log(p[f"price_{key}"] / p["close"])
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
    """Mean cross-sectional correlation per day, and its t-statistic across days."""
    g = pd.DataFrame({"p": pred, "y": y, "d": dates})
    s = g.groupby("d").apply(lambda x: x.p.corr(x.y, method=method)).dropna()
    return float(s.mean()), float(s.mean() / s.std() * np.sqrt(len(s))), float(s.mean() / s.std())


def return_block(g, key, majority):
    """Skill in the space the model actually predicts in: next-day log return."""
    y = g["target_ret"].values
    f = g[f"ret_{key}"].values
    e = y - f
    zero_sq, drift_sq = y ** 2, (y - g["train_mean_ret"].values) ** 2
    m = {"MAE_bp": float(1e4 * np.abs(e).mean()), "RMSE_bp": float(1e4 * np.sqrt((e ** 2).mean())),
         "R2_oos_vs_zero": float(1 - (e ** 2).sum() / zero_sq.sum()),
         "R2_oos_vs_drift": float(1 - (e ** 2).sum() / drift_sq.sum()),
         "pred_sd_bp": float(1e4 * f.std())}
    if key != "naive":
        stat, pval = dm_test(e ** 2, zero_sq, g.date.values)
        m["DM_ret_vs_zero"], m["DM_ret_p"] = stat, pval
    if key in RANKED:
        m["IC"], m["IC_t"], m["ICIR"] = daily_corr(f, y, g.date.values)
        m["RankIC"], m["RankIC_t"], _ = daily_corr(f, y, g.date.values, "spearman")
    hits = int(((f > 0) == (y > 0)).sum())
    m["direction_acc"] = hits / len(g)
    m["direction_binomial_p_vs_majority"] = float(
        stats.binomtest(hits, len(g), majority, "greater").pvalue)
    return m


def price_block(g, key, naive_sq_pct):
    """The same forecast scored in price space, the way the literature reports it."""
    y = g["target_close"].values
    f = g[f"price_{key}"].values
    err = y - f
    pct = np.abs(err) / y
    m = {"MAE_$": float(np.abs(err).mean()), "RMSE_$": float(np.sqrt((err ** 2).mean())),
         "MAPE_%": float(100 * pct.mean()), "price_accuracy_%": float(100 * (1 - pct.mean())),
         "R2_price": float(1 - (err ** 2).sum() / ((y - y.mean()) ** 2).sum()),
         "within_1%": float((pct <= 0.01).mean()), "within_2%": float((pct <= 0.02).mean())}
    if key != "naive":
        m["DM_vs_naive"], m["DM_p"] = dm_test((err / y) ** 2, naive_sq_pct, g.date.values)
    return m


def economic(g, col="pred_ret_rf"):
    """Sort each day's stocks by predicted return and hold the extremes: the return-space
    question of whether the ranking is worth anything, in basis points per day."""
    d = g[["date", col, "target_ret"]].copy()
    d["decile"] = d.groupby("date")[col].transform(
        lambda x: pd.qcut(x.rank(method="first"), N_DECILES, labels=False, duplicates="drop"))
    per_decile = d.groupby("decile")["target_ret"].mean().mul(1e4)
    daily = d.groupby("date").apply(
        lambda x: x.loc[x.decile == N_DECILES - 1, "target_ret"].mean() - x.loc[x.decile == 0, "target_ret"].mean())
    daily = daily.dropna()
    mean_bp, sd_bp = 1e4 * daily.mean(), 1e4 * daily.std()
    return {"decile_mean_return_bp": {int(k): float(v) for k, v in per_decile.items()},
            "long_short_bp_per_day": float(mean_bp),
            "long_short_t": float(mean_bp / sd_bp * np.sqrt(len(daily))),
            "long_short_sharpe_annual": float(mean_bp / sd_bp * np.sqrt(252)),
            "long_short_net_bp_per_day": float(mean_bp - COST_BP),
            "assumed_round_trip_cost_bp": COST_BP,
            "spearman_decile_monotonicity": float(
                stats.spearmanr(per_decile.index.values, per_decile.values).statistic)}


def block(g):
    y_ret, up = g["target_ret"].values, g["target_up"].values
    majority = float(max(up.mean(), 1 - up.mean()))
    naive_sq_pct = ((g["target_close"].values - g["price_naive"].values) / g["target_close"].values) ** 2
    out = {"n": int(len(g)), "days": int(g.date.nunique()), "majority_direction_acc": majority,
           "realised_return_sd_bp": float(1e4 * y_ret.std())}

    for label, key in PRICE_MODELS.items():
        m = return_block(g, key, majority)
        m.update(price_block(g, key, naive_sq_pct))
        out[label] = m

    clf_pred = g["prob_up_rf"].values > 0.5
    hits = int((clf_pred == up).sum())
    out["Random Forest classifier"] = {
        "direction_acc": hits / len(g),
        "AUC": float(roc_auc_score(up, g["prob_up_rf"])) if 0 < up.mean() < 1 else None,
        "balanced_acc": float(0.5 * (clf_pred[up == 1].mean() + (~clf_pred[up == 0]).mean())),
        "direction_binomial_p_vs_majority": float(
            stats.binomtest(hits, len(g), majority, "greater").pvalue)}
    # Kept under the old key as well, so earlier figures and text still resolve.
    out["always_up_acc"] = majority
    out["economic"] = economic(g)
    out["long_short_decile_bp_per_day"] = out["economic"]["long_short_bp_per_day"]
    out["long_short_t"] = out["economic"]["long_short_t"]
    return out


def main():
    p = add_forecasts(pd.read_pickle(RESULTS / "predictions.pkl"))
    res = {"overall": block(p),
           "by_year": {int(y): block(g) for y, g in p.groupby("year")},
           "by_regime": {r: block(g) for r, g in p.groupby("regime") if r in REGIMES},
           "by_sector": {s: block(g) for s, g in p.groupby("sector")}}
    (RESULTS / "metrics.json").write_text(json.dumps(res, indent=2))

    o = res["overall"]
    print(f"test: {o['n']:,} stock-days over {o['days']} days; "
          f"realised daily return sd {o['realised_return_sd_bp']:.0f} bp\n")
    print("RETURN SPACE (what the model predicts)")
    print(f"{'model':32s} {'RMSE bp':>8s} {'R2 vs 0':>9s} {'R2 vs drift':>12s} {'IC':>8s} "
          f"{'IC t':>6s} {'dir':>7s} {'DM p':>7s}")
    for label in PRICE_MODELS:
        m = o[label]
        print(f"{label:32s} {m['RMSE_bp']:8.1f} {m['R2_oos_vs_zero']:9.5f} {m['R2_oos_vs_drift']:12.5f} "
              f"{m.get('IC', float('nan')):8.4f} {m.get('IC_t', float('nan')):6.2f} "
              f"{m['direction_acc']:7.4f} {m.get('DM_ret_p', float('nan')):7.3f}")
    print(f"{'majority-direction rule':32s} {'':8s} {'':9s} {'':12s} {'':8s} {'':6s} "
          f"{o['majority_direction_acc']:7.4f}")

    print("\nPRICE SPACE (what the literature reports)")
    for label in PRICE_MODELS:
        m = o[label]
        extra = "" if "DM_vs_naive" not in m else f"  DM vs naive {m['DM_vs_naive']:+.2f} (p={m['DM_p']:.3f})"
        print(f"{label:32s} MAPE {m['MAPE_%']:.3f}%  RMSE ${m['RMSE_$']:.2f}  R2 {m['R2_price']:.5f}  "
              f"within 2% {m['within_2%']:.3f}{extra}")
    rf = o["Random Forest (proposed)"]
    print(f"\nsame RF forecasts: R2 {rf['R2_price']:.4f} in price space vs "
          f"{rf['R2_oos_vs_zero']:+.5f} in return space")

    c = o["Random Forest classifier"]
    print(f"RF classifier: acc {c['direction_acc']:.4f} AUC {c['AUC']:.4f} balanced {c['balanced_acc']:.4f} "
          f"(majority rule {o['majority_direction_acc']:.4f}, p={c['direction_binomial_p_vs_majority']:.3f})")
    e = o["economic"]
    print(f"deciles of predicted return (bp/day): "
          f"{', '.join(f'{v:+.1f}' for v in e['decile_mean_return_bp'].values())}")
    print(f"long-short decile: {e['long_short_bp_per_day']:+.2f} bp/day (t={e['long_short_t']:+.2f}, "
          f"Sharpe {e['long_short_sharpe_annual']:+.2f}), net of {e['assumed_round_trip_cost_bp']:.0f} bp cost "
          f"{e['long_short_net_bp_per_day']:+.2f} bp/day")
    print("\nby regime (Random Forest)")
    for r, m in res["by_regime"].items():
        x = m["Random Forest (proposed)"]
        print(f"  {r:15s} RMSE {x['RMSE_bp']:6.1f} bp  R2 vs 0 {x['R2_oos_vs_zero']:+.5f}  "
              f"IC {x.get('IC', float('nan')):+.4f}  dir {x['direction_acc']:.4f}  "
              f"(MAPE {x['MAPE_%']:.3f}% vs naive {m['Naive (tomorrow = today)']['MAPE_%']:.3f}%)")


if __name__ == "__main__":
    main()

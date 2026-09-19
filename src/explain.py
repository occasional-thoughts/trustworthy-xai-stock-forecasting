"""Explanations of the Random Forest and tests of whether those explanations can be trusted.

Explanations
  X1  Global importance from three explainers: TreeSHAP (mean |SHAP|), permutation
      importance on test data, and impurity importance (MDI); agreement via Kendall's tau
  X2  Feature-family shares of SHAP (past returns, trend, oscillators, volatility, ...)
  X3  Local explanations in dollars for chosen stock-days (SHAP x close price)
  X4  Explanation drift across market regimes and across GICS sectors, with permutation tests
Reliability checks
  R1  Faithfulness: removing the top-|SHAP| features must move the forecast more than
      removing random features (deletion curves, AOPC), and the SHAP mass removed should
      predict the actual change (fidelity)
  R2  Stability: same training data, 5 random seeds; and consecutive yearly retrains
  R3  Sanity (data randomisation): a forest trained on labels shuffled within each day has no
      real signal; if its explanations look like the real model's, those explanations
      describe the features' structure rather than learned relationships

    python src/explain.py
"""
import json
import time

import joblib
import numpy as np
import pandas as pd
import shap
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance

from config import FEATURE_FILE, MODELS, REGIMES, RESULTS, SEED, TEST_YEARS, TRAIN_START
from features import FAMILIES, FAMILY_OF, FEATURES

STOCKS_PER_DAY = 40
FOCUS_TICKERS = ["AAPL", "MSFT", "JPM", "XOM", "PFE"]   # explained on every test day
STABILITY_YEAR = 2020
N_STABILITY_ROWS = 4000
N_FAITHFUL_ROWS = 2000
N_BACKGROUND = 32
N_PERM = 1000
K_STEPS = [0, 1, 2, 4, 8, 16, 32]
rng = np.random.default_rng(SEED)
FAM_NAMES = list(FAMILIES)


def regime_of(dates):
    out = np.full(len(dates), "Other", dtype=object)
    for name, (a, b) in REGIMES.items():
        out[(dates >= pd.Timestamp(a)) & (dates <= pd.Timestamp(b))] = name
    return out


def family_shares(abs_shap):
    """Rows of |SHAP| -> share of total attribution per feature family (sums to 1)."""
    per_feat = abs_shap.mean(0)
    fam = np.array([per_feat[[FEATURES.index(f) for f in FAMILIES[name]]].sum() for name in FAM_NAMES])
    return fam / fam.sum()


def tvd(a, b):
    return 0.5 * np.abs(a - b).sum()


def group_drift_test(abs_shap, labels, units):
    """Is the family-share vector different between groups? Statistic: mean total-variation
    distance over group pairs. Null: shuffle group labels across whole units (days for
    regimes, tickers for sectors), so within-unit dependence is kept."""
    groups = sorted(set(labels))
    unit_ids, unit_idx = np.unique(units, return_inverse=True)
    unit_label = pd.Series(labels).groupby(unit_idx).first().values

    def stat(lab_per_unit):
        lab = lab_per_unit[unit_idx]
        shares = [family_shares(abs_shap[lab == g]) for g in groups]
        return np.mean([tvd(shares[i], shares[j]) for i in range(len(groups)) for j in range(i + 1, len(groups))]), shares

    obs, shares = stat(unit_label)
    null = np.array([stat(rng.permutation(unit_label))[0] for _ in range(N_PERM)])
    return {"groups": groups, "family_shares": {g: dict(zip(FAM_NAMES, s.round(4).tolist())) for g, s in zip(groups, shares)},
            "mean_pairwise_TVD": float(obs), "null_mean_TVD": float(null.mean()),
            "p_value": float((1 + (null >= obs).sum()) / (1 + N_PERM))}


def rank_agreement(a, b):
    tau = stats.kendalltau(a, b)[0]
    top5 = len(set(np.argsort(-a)[:5]) & set(np.argsort(-b)[:5])) / 5
    return float(tau), float(top5)


def row_spearman(sa, sb):
    return float(np.median([stats.spearmanr(np.abs(x), np.abs(y))[0] for x, y in zip(sa, sb)]))


def fit_rf(X, y, chosen, seed):
    return RandomForestRegressor(n_estimators=chosen["n_estimators"], min_samples_leaf=chosen["min_samples_leaf"],
                                 max_features=chosen["max_features"], max_samples=chosen["max_samples"],
                                 n_jobs=-1, random_state=seed).fit(X, y)


def deletion_curves(model, X, sv, background):
    """Mean |f(x) - f(x with k features replaced by background values)|, in basis points,
    removing features by |SHAP| rank ('top') or in random order ('random')."""
    n, p = X.shape
    base = model.predict(X)
    order_top = np.argsort(-np.abs(sv), axis=1)
    order_rand = np.array([rng.permutation(p) for _ in range(n)])
    curves = {"top": [], "random": []}
    fidelity = []
    for k in K_STEPS:
        for name, order in (("top", order_top), ("random", order_rand)):
            if k == 0:
                curves[name].append(0.0)
                continue
            Xk = np.repeat(X, len(background), axis=0)
            bg = np.tile(background, (n, 1))
            rows = np.repeat(np.arange(n), len(background))
            cols = order[rows][:, :k]
            Xk[np.arange(len(Xk))[:, None], cols] = bg[np.arange(len(Xk))[:, None], cols]
            removed = model.predict(Xk).reshape(n, len(background)).mean(1)
            change = base - removed
            curves[name].append(float(1e4 * np.abs(change).mean()))
            if name == "top":
                shap_removed = np.take_along_axis(sv, order_top[:, :k], axis=1).sum(1)
                fidelity.append(float(np.corrcoef(shap_removed, change)[0, 1]))
    aopc = {k: float(np.mean(v[1:])) for k, v in curves.items()}
    return {"k": K_STEPS, "abs_change_bp": curves, "AOPC_bp": aopc, "fidelity_corr": dict(zip(K_STEPS[1:], fidelity))}


def main():
    chosen = json.loads((RESULTS / "tuning.json").read_text())["chosen"]
    df = pd.read_pickle(FEATURE_FILE)
    t_start = time.time()

    # ---- SHAP on a sample of test stock-days, each explained by its own year's model ----
    parts, perm, mdi, models = [], {}, {}, {}
    for year in TEST_YEARS:
        model = joblib.load(MODELS / f"rf_reg_{year}.joblib")
        models[year] = model
        test = df[(df.date >= f"{year}-01-01") & (df.date < f"{year + 1}-01-01")]
        pick = test.groupby("date").sample(n=STOCKS_PER_DAY, random_state=SEED)
        focus = test[test.ticker.isin(FOCUS_TICKERS)]
        sample = pd.concat([pick, focus]).drop_duplicates(["date", "ticker"]).sort_values(["date", "ticker"])
        X = sample[FEATURES].values
        expl = shap.TreeExplainer(model)
        sv = expl.shap_values(X, check_additivity=False)
        pred = model.predict(X)
        add_err = np.abs(expl.expected_value + sv.sum(1) - pred).max()
        meta = sample[["date", "ticker", "sector", "close", "target_ret"]].copy()
        meta["year"], meta["pred_ret"], meta["base_value"] = year, pred, float(np.ravel(expl.expected_value)[0])
        parts.append((meta, X, sv))

        sub = test.sample(min(60000, len(test)), random_state=SEED)
        pi = permutation_importance(model, sub[FEATURES].values, sub.target_ret.values, n_repeats=3,
                                    random_state=SEED, scoring="neg_mean_squared_error", n_jobs=1)
        perm[year] = {"mean": pi.importances_mean, "std": pi.importances_std, "n": len(sub)}
        mdi[year] = model.feature_importances_
        print(f"{year}: SHAP on {len(sample):,} stock-days (additivity error {add_err:.1e}), "
              f"permutation on {len(sub):,}  [{time.time() - t_start:.0f}s]", flush=True)

    meta = pd.concat([m for m, _, _ in parts], ignore_index=True)
    X_all = np.vstack([x for _, x, _ in parts])
    S = np.vstack([s for _, _, s in parts])
    A = np.abs(S)
    meta["regime"] = regime_of(meta.date.values)
    pd.to_pickle({"meta": meta, "X": X_all, "shap": S, "features": FEATURES}, RESULTS / "shap_sample.pkl")

    # ---- X1: three explainers ----
    shap_imp = A.mean(0)
    yrs = np.array([sum(meta.year == y) for y in TEST_YEARS], dtype=float)
    perm_imp = np.average([perm[y]["mean"] for y in TEST_YEARS], axis=0, weights=yrs)
    perm_std = np.sqrt(np.average([perm[y]["std"] ** 2 for y in TEST_YEARS], axis=0, weights=yrs))
    mdi_imp = np.average([mdi[y] for y in TEST_YEARS], axis=0, weights=yrs)
    tau_sp, top_sp = rank_agreement(shap_imp, perm_imp)
    tau_sm, top_sm = rank_agreement(shap_imp, mdi_imp)
    tau_pm, top_pm = rank_agreement(perm_imp, mdi_imp)
    importance = pd.DataFrame({"feature": FEATURES, "family": [FAMILY_OF[f] for f in FEATURES],
                               "mean_abs_shap_bp": 1e4 * shap_imp, "permutation_mse_increase": perm_imp,
                               "permutation_std": perm_std, "mdi": mdi_imp}).sort_values("mean_abs_shap_bp", ascending=False)
    importance.to_csv(RESULTS / "importance.csv", index=False)

    # ---- X2 / X4: family shares, regimes, sectors, years ----
    regime_rows = meta.regime.values != "Other"
    regimes = group_drift_test(A[regime_rows], meta.regime.values[regime_rows], meta.date.values[regime_rows])
    sectors = group_drift_test(A, meta.sector.values, meta.ticker.values)
    by_year = {int(y): dict(zip(FAM_NAMES, family_shares(A[meta.year.values == y]).round(4).tolist())) for y in TEST_YEARS}
    reg_names = [r for r in REGIMES if (meta.regime == r).any()]
    regime_rank_corr = {f"{a} vs {b}": float(stats.spearmanr(A[meta.regime.values == a].mean(0), A[meta.regime.values == b].mean(0))[0])
                        for i, a in enumerate(reg_names) for b in reg_names[i + 1:]}
    regime_top5 = {r: [FEATURES[j] for j in np.argsort(-A[meta.regime.values == r].mean(0))[:5]] for r in reg_names}
    print(f"regime drift p={regimes['p_value']:.3f}, sector drift p={sectors['p_value']:.3f}  [{time.time() - t_start:.0f}s]", flush=True)

    # ---- X3: local explanations in dollars ----
    local = {}
    for ticker, day in [("AAPL", "2020-03-16"), ("AAPL", "2019-06-03"), ("XOM", "2020-03-09"), ("JPM", "2022-05-18")]:
        hit = meta.index[(meta.ticker == ticker) & (meta.date == pd.Timestamp(day))]
        if len(hit) == 0:
            continue
        i = hit[0]
        close = float(meta.close[i])
        dollars = S[i] * close
        top = np.argsort(-np.abs(dollars))[:8]
        local[f"{ticker} {day}"] = {
            "close": close, "predicted_close": close * float(np.exp(meta.pred_ret[i])),
            "actual_next_close": close * float(np.exp(meta.target_ret[i])),
            "base_value_ret": float(meta.base_value[i]), "pred_ret": float(meta.pred_ret[i]),
            "top_contributions_$": {FEATURES[j]: {"value": float(X_all[i, j]), "dollars": float(dollars[j])} for j in top},
        }

    # ---- R1: faithfulness ----
    faith_parts = []
    for year in TEST_YEARS:
        rows = np.flatnonzero(meta.year.values == year)
        rows = rng.choice(rows, N_FAITHFUL_ROWS // len(TEST_YEARS), replace=False)
        train = df[(df.date >= TRAIN_START) & (df.date < f"{year}-01-01")]
        background = train[FEATURES].sample(N_BACKGROUND, random_state=SEED).values
        faith_parts.append(deletion_curves(models[year], X_all[rows], S[rows], background))
    faith = {"k": K_STEPS,
             "abs_change_bp": {k: np.mean([f["abs_change_bp"][k] for f in faith_parts], 0).round(4).tolist() for k in ("top", "random")},
             "AOPC_bp": {k: float(np.mean([f["AOPC_bp"][k] for f in faith_parts])) for k in ("top", "random")},
             "fidelity_corr": {k: float(np.mean([f["fidelity_corr"][k] for f in faith_parts])) for k in K_STEPS[1:]}}
    print(f"faithfulness AOPC top {faith['AOPC_bp']['top']:.2f} bp vs random {faith['AOPC_bp']['random']:.2f} bp  "
          f"[{time.time() - t_start:.0f}s]", flush=True)

    # ---- R2 / R3: seeds, retraining, shuffled labels ----
    train = df[(df.date >= TRAIN_START) & (df.date < f"{STABILITY_YEAR}-01-01")]
    test = df[(df.date >= f"{STABILITY_YEAR}-01-01") & (df.date < f"{STABILITY_YEAR + 1}-01-01")]
    rows = test.sample(N_STABILITY_ROWS, random_state=SEED)
    Xs = rows[FEATURES].values
    seed_models = {SEED: models[STABILITY_YEAR]}
    for s in (1, 2, 3, 4):
        seed_models[s] = fit_rf(train[FEATURES].values, train.target_ret.values, chosen, s)
    seed_shap = {s: shap.TreeExplainer(m).shap_values(Xs, check_additivity=False) for s, m in seed_models.items()}
    seed_pred = {s: m.predict(Xs) for s, m in seed_models.items()}
    keys = list(seed_models)
    pairs = [(a, b) for i, a in enumerate(keys) for b in keys[i + 1:]]
    seeds = {
        "global_kendall_tau": float(np.mean([rank_agreement(np.abs(seed_shap[a]).mean(0), np.abs(seed_shap[b]).mean(0))[0] for a, b in pairs])),
        "global_top5_overlap": float(np.mean([rank_agreement(np.abs(seed_shap[a]).mean(0), np.abs(seed_shap[b]).mean(0))[1] for a, b in pairs])),
        "row_spearman_median": float(np.mean([row_spearman(seed_shap[a], seed_shap[b]) for a, b in pairs])),
        "prediction_corr": float(np.mean([np.corrcoef(seed_pred[a], seed_pred[b])[0, 1] for a, b in pairs])),
    }

    retrain = {}
    common = df[(df.date >= "2022-01-01")].sample(N_STABILITY_ROWS, random_state=SEED)[FEATURES].values
    yearly_shap = {y: shap.TreeExplainer(models[y]).shap_values(common, check_additivity=False) for y in TEST_YEARS}
    for a, b in zip(TEST_YEARS[:-1], TEST_YEARS[1:]):
        tau, top = rank_agreement(np.abs(yearly_shap[a]).mean(0), np.abs(yearly_shap[b]).mean(0))
        retrain[f"{a} vs {b} model"] = {"global_kendall_tau": tau, "global_top5_overlap": top,
                                         "row_spearman_median": row_spearman(yearly_shap[a], yearly_shap[b])}

    # Two nulls. "Fully shuffled": labels permuted across all rows, so no feature carries any
    # information. "Shuffled within day": each day's returns permuted across stocks, which keeps
    # the market-wide daily move but removes all stock-specific information.
    y_tr = train.target_ret.values
    nulls = {"fully_shuffled": rng.permutation(y_tr),
             "shuffled_within_day": train.groupby("date").target_ret.transform(
                 lambda s: s.sample(frac=1, random_state=SEED).values).values}
    real_shap = seed_shap[SEED]
    yt, dt = test.target_ret.values, test.date.values

    def test_scores(m):
        pr = m.predict(test[FEATURES].values)
        ic = pd.DataFrame({"p": pr, "y": yt, "d": dt}).groupby("d").apply(lambda g: g.p.corr(g.y)).mean()
        return {"IC": float(ic), "R2_vs_zero": float(1 - ((yt - pr) ** 2).sum() / (yt ** 2).sum()),
                "prediction_sd_bp": float(1e4 * pr.std())}

    sanity = {"real": {"test": test_scores(models[STABILITY_YEAR]),
                       "total_mean_abs_shap_bp": float(1e4 * np.abs(real_shap).sum(1).mean()),
                       "family_shares": dict(zip(FAM_NAMES, family_shares(np.abs(real_shap)).round(4).tolist()))}}
    for name, y_null in nulls.items():
        null_model = fit_rf(train[FEATURES].values, y_null, chosen, SEED)
        null_shap = shap.TreeExplainer(null_model).shap_values(Xs, check_additivity=False)
        tau_null, top_null = rank_agreement(np.abs(real_shap).mean(0), np.abs(null_shap).mean(0))
        sanity[name] = {"global_kendall_tau_vs_real": tau_null, "global_top5_overlap_vs_real": top_null,
                        "row_spearman_median_vs_real": row_spearman(real_shap, null_shap),
                        "total_mean_abs_shap_bp": float(1e4 * np.abs(null_shap).sum(1).mean()),
                        "family_shares": dict(zip(FAM_NAMES, family_shares(np.abs(null_shap)).round(4).tolist())),
                        "test": test_scores(null_model)}
    print(f"seeds tau {seeds['global_kendall_tau']:.2f}; real vs fully shuffled tau "
          f"{sanity['fully_shuffled']['global_kendall_tau_vs_real']:.2f}, vs within-day shuffled "
          f"{sanity['shuffled_within_day']['global_kendall_tau_vs_real']:.2f}  [{time.time() - t_start:.0f}s]", flush=True)

    out = {
        "sample": {"rows": int(len(meta)), "stocks_per_day": STOCKS_PER_DAY, "focus_tickers": FOCUS_TICKERS},
        "X1_explainer_agreement": {"SHAP vs permutation": {"kendall_tau": tau_sp, "top5_overlap": top_sp},
                                   "SHAP vs MDI": {"kendall_tau": tau_sm, "top5_overlap": top_sm},
                                   "permutation vs MDI": {"kendall_tau": tau_pm, "top5_overlap": top_pm},
                                   "permutation_importance_positive_share": float((perm_imp > 2 * perm_std).mean())},
        "X2_family_shares_overall": dict(zip(FAM_NAMES, family_shares(A).round(4).tolist())),
        "X2_family_shares_by_year": by_year,
        "X3_local": local,
        "X4_regimes": regimes | {"feature_rank_corr": regime_rank_corr, "top5": regime_top5},
        "X4_sectors": sectors,
        "R1_faithfulness": faith,
        "R2_seed_stability": seeds,
        "R2_retrain_stability": retrain,
        "R3_sanity_shuffled_labels": sanity,
    }
    (RESULTS / "xai.json").write_text(json.dumps(out, indent=2))
    print(importance.head(10).to_string(index=False))
    print(json.dumps({k: out[k] for k in ("X1_explainer_agreement", "X2_family_shares_overall", "R2_seed_stability",
                                          "R2_retrain_stability")}, indent=2))
    print(json.dumps(out["R3_sanity_shuffled_labels"], indent=2))
    print(json.dumps({k: out[k] for k in ("X4_regimes", "X4_sectors", "R1_faithfulness", "X3_local")}, indent=2, default=str))
    print(f"done in {time.time() - t_start:.0f}s")


if __name__ == "__main__":
    main()

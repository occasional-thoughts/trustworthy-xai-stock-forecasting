"""LIME explanations for the Random Forest, compared against SHAP.

LIME (Ribeiro et al., 2016) explains one forecast by sampling perturbed inputs around it
and fitting a weighted linear surrogate model. Uses `lime.lime_tabular` defaults:
quartile discretisation, 5,000 samples, kernel width 0.75 * sqrt(features).

Explanations
  L1  Local LIME explanations for the same stock-days as the SHAP local explanations
  L2  Global LIME importance (mean |weight|) and its agreement with TreeSHAP,
      permutation importance and MDI
Reliability, measured the same way as for SHAP
  L3  Agreement with SHAP on each stock-day (Spearman rho, top-5 overlap, top-5 sign agreement)
  L4  Run-to-run stability: the same stock-day explained with 5 LIME random seeds
      (TreeSHAP is deterministic, so its run-to-run agreement is exactly 1)
  L5  Local fidelity: R^2 of LIME's surrogate model on its own perturbation samples
  L6  Faithfulness: deletion curves ordered by |LIME weight|, vs |SHAP| and random order

Needs results/shap_sample.pkl and results/importance.csv from explain.py.

    python src/lime_explain.py
"""
import json
import time

import joblib
import numpy as np
import pandas as pd
from lime.lime_tabular import LimeTabularExplainer
from scipy import stats

from config import FEATURE_FILE, MODELS, RESULTS, SEED, TEST_YEARS, TRAIN_START
from explain import K_STEPS, N_BACKGROUND, rank_agreement
from features import FEATURES

ROWS_PER_YEAR = 200
N_SEEDS = 5
N_SAMPLES = 5000
N_LIME_TRAIN = 5000
LOCAL_CASES = [("AAPL", "2020-03-16"), ("AAPL", "2019-06-03"), ("XOM", "2020-03-09"), ("JPM", "2022-05-18")]
rng = np.random.default_rng(SEED)


def lime_weights(explainer, x, predict, seed):
    """One LIME explanation -> (weight per feature in FEATURES order, local surrogate R^2)."""
    explainer.random_state = np.random.RandomState(seed)
    exp = explainer.explain_instance(x, predict, num_features=len(FEATURES), num_samples=N_SAMPLES)
    w = np.zeros(len(FEATURES))
    # In regression mode lime stores the weights under label 1 and a sign-flipped copy under
    # label 0; label 1 is the one that matches exp.as_list().
    for j, weight in exp.as_map()[1]:
        w[j] = weight
    return w, float(exp.score), exp.as_list()


def deletion_curve(model, X, importance, background):
    """Mean |f(x) - f(x with the k most important features replaced by background)| in bp."""
    n = len(X)
    base = model.predict(X)
    order = np.argsort(-np.abs(importance), axis=1)
    out = []
    for k in K_STEPS[1:]:
        Xk = np.repeat(X, len(background), axis=0)
        bg = np.tile(background, (n, 1))
        cols = np.repeat(order[:, :k], len(background), axis=0)
        idx = np.arange(len(Xk))[:, None]
        Xk[idx, cols] = bg[idx, cols]
        out.append(float(1e4 * np.abs(base - model.predict(Xk).reshape(n, -1).mean(1)).mean()))
    return [0.0] + out


def main():
    t0 = time.time()
    d = pd.read_pickle(RESULTS / "shap_sample.pkl")
    meta, X_all, S_all = d["meta"].reset_index(drop=True), d["X"], d["shap"]
    df = pd.read_pickle(FEATURE_FILE)

    rows = []
    for year in TEST_YEARS:
        rows.extend(rng.choice(np.flatnonzero(meta.year.values == year), ROWS_PER_YEAR, replace=False).tolist())
    case_rows = {}
    for ticker, day in LOCAL_CASES:
        hit = meta.index[(meta.ticker == ticker) & (meta.date == pd.Timestamp(day))]
        if len(hit):
            case_rows[f"{ticker} {day}"] = int(hit[0])
    rows = sorted(set(rows) | set(case_rows.values()))

    W = np.zeros((len(rows), N_SEEDS, len(FEATURES)))
    R2 = np.zeros((len(rows), N_SEEDS))
    lime_lists = {}
    faith = {"LIME": [], "SHAP": [], "Random": []}
    for year in TEST_YEARS:
        model = joblib.load(MODELS / f"rf_reg_{year}.joblib")
        model.set_params(n_jobs=1)          # LIME calls predict on 5,000 small batches; threads only add overhead
        train = df[(df.date >= TRAIN_START) & (df.date < f"{year}-01-01")]
        explainer = LimeTabularExplainer(train[FEATURES].sample(N_LIME_TRAIN, random_state=SEED).values,
                                         mode="regression", feature_names=FEATURES, random_state=SEED)
        idx = [i for i, r in enumerate(rows) if meta.year[r] == year]
        for i in idx:
            x = X_all[rows[i]]
            for s in range(N_SEEDS):
                W[i, s], R2[i, s], lst = lime_weights(explainer, x, model.predict, seed=SEED + s)
                if s == 0 and rows[i] in case_rows.values():
                    lime_lists[rows[i]] = lst
        model.set_params(n_jobs=-1)
        background = train[FEATURES].sample(N_BACKGROUND, random_state=SEED).values
        Xy = X_all[[rows[i] for i in idx]]
        faith["LIME"].append(deletion_curve(model, Xy, W[idx, 0], background))
        faith["SHAP"].append(deletion_curve(model, Xy, S_all[[rows[i] for i in idx]], background))
        faith["Random"].append(deletion_curve(model, Xy, rng.random((len(idx), len(FEATURES))), background))
        print(f"{year}: LIME on {len(idx)} stock-days x {N_SEEDS} seeds  [{time.time() - t0:.0f}s]", flush=True)

    S = S_all[rows]
    L = W[:, 0]
    top5 = lambda a: set(np.argsort(-np.abs(a))[:5])

    # L3: agreement with SHAP on each stock-day
    rho_ls = np.array([stats.spearmanr(np.abs(l), np.abs(s))[0] for l, s in zip(L, S)])
    overlap_ls = np.array([len(top5(l) & top5(s)) / 5 for l, s in zip(L, S)])
    sign_ls = np.array([np.mean([np.sign(l[j]) == np.sign(s[j]) for j in top5(s)]) for l, s in zip(L, S)])
    top1_ls = np.array([np.argmax(np.abs(l)) == np.argmax(np.abs(s)) for l, s in zip(L, S)])

    # L4: run-to-run stability over seeds
    pairs = [(a, b) for a in range(N_SEEDS) for b in range(a + 1, N_SEEDS)]
    rho_seed = np.array([[stats.spearmanr(np.abs(W[i, a]), np.abs(W[i, b]))[0] for a, b in pairs] for i in range(len(rows))])
    overlap_seed = np.array([[len(top5(W[i, a]) & top5(W[i, b])) / 5 for a, b in pairs] for i in range(len(rows))])
    top1_same = np.array([len({int(np.argmax(np.abs(W[i, s]))) for s in range(N_SEEDS)}) == 1 for i in range(len(rows))])

    # L2: global agreement between four explainers
    imp = pd.read_csv(RESULTS / "importance.csv").set_index("feature").loc[FEATURES]
    lime_global = np.abs(L).mean(0)
    rankings = {"TreeSHAP": imp.mean_abs_shap_bp.values, "LIME": lime_global,
                "Permutation": imp.permutation_mse_increase.values, "MDI": imp.mdi.values}
    names = list(rankings)
    global_agree = {f"{a} vs {b}": dict(zip(("kendall_tau", "top5_overlap"), rank_agreement(rankings[a], rankings[b])))
                    for i, a in enumerate(names) for b in names[i + 1:]}

    curves = {k: np.mean(v, 0).round(4).tolist() for k, v in faith.items()}
    local = {}
    for name, r in case_rows.items():
        i = rows.index(r)
        order = np.argsort(-np.abs(L[i]))[:8]
        local[name] = {"close": float(meta.close[r]),
                       "lime_top_conditions": [[c, float(w)] for c, w in lime_lists.get(r, [])[:8]],
                       "lime_dollars": {FEATURES[j]: float(L[i, j] * meta.close[r]) for j in order},
                       "shap_dollars": {FEATURES[j]: float(S[i, j] * meta.close[r]) for j in np.argsort(-np.abs(S[i]))[:8]},
                       "lime_local_R2": float(R2[i, 0]),
                       "spearman_vs_shap": float(rho_ls[i]), "top5_overlap_vs_shap": float(overlap_ls[i]),
                       "top5_stability_over_seeds": float(overlap_seed[i].mean())}

    out = {
        "settings": {"stock_days": len(rows), "seeds": N_SEEDS, "num_samples": N_SAMPLES,
                     "discretisation": "quartile (lime default)", "background_rows": N_LIME_TRAIN},
        "L2_global_importance": dict(zip(FEATURES, lime_global.round(8).tolist())),
        "L2_global_agreement": global_agree,
        "L3_agreement_with_SHAP": {"spearman_median": float(np.median(rho_ls)), "top5_overlap_mean": float(overlap_ls.mean()),
                                   "top1_same_share": float(top1_ls.mean()), "top5_sign_agreement": float(sign_ls.mean())},
        "L4_run_to_run_stability": {"spearman_median": float(np.median(rho_seed)), "top5_overlap_mean": float(overlap_seed.mean()),
                                    "top1_identical_all_seeds_share": float(top1_same.mean()),
                                    "SHAP_reference": "TreeSHAP is deterministic: rho = 1, top-5 overlap = 1"},
        "L5_local_fidelity_R2": {"median": float(np.median(R2)), "mean": float(R2.mean()),
                                 "share_below_0.3": float((R2 < 0.3).mean())},
        "L6_faithfulness": {"k": K_STEPS, "abs_change_bp": curves,
                            "AOPC_bp": {k: float(np.mean(v[1:])) for k, v in curves.items()}},
        "L1_local": local,
        "runtime_s": round(time.time() - t0),
    }
    (RESULTS / "lime.json").write_text(json.dumps(out, indent=2))
    pd.to_pickle({"rows": rows, "lime": W, "r2": R2}, RESULTS / "lime_sample.pkl")
    print(json.dumps({k: out[k] for k in ("L2_global_agreement", "L3_agreement_with_SHAP", "L4_run_to_run_stability",
                                          "L5_local_fidelity_R2", "L6_faithfulness")}, indent=2))
    print(json.dumps(local, indent=1))
    print(pd.Series(lime_global, index=FEATURES).sort_values(ascending=False).head(10))


if __name__ == "__main__":
    main()

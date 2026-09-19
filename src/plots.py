"""Report figures -> results/figures/*.png

    python src/plots.py
"""
import json

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

from config import FIGURES, REGIMES, RESULTS  # noqa: E402
from evaluate import PRICE_MODELS, add_forecasts  # noqa: E402
from features import FAMILIES, FAMILY_OF, FEATURES  # noqa: E402

INK, INK2, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7"]
POS, NEG = "#2a78d6", "#e34948"
SEQ = LinearSegmentedColormap.from_list("seq", ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"])
FAM_COLOR = dict(zip(FAMILIES, SERIES))


def style():
    plt.rcParams.update({
        "font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"], "font.size": 9.5,
        "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 10,
        "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "axes.facecolor": SURFACE, "figure.facecolor": SURFACE,
        "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK2, "ytick.labelcolor": INK2,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
        "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False, "savefig.dpi": 200,
        "savefig.bbox": "tight", "text.color": INK})


def save(fig, name):
    fig.savefig(FIGURES / name)
    plt.close(fig)


def fig_price_accuracy(metrics):
    o = metrics["overall"]
    labels = list(PRICE_MODELS)
    mape = [o[l]["MAPE_%"] for l in labels]
    within = [100 * o[l]["within_2%"] for l in labels]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.1), gridspec_kw={"wspace": 0.9})
    for ax, vals, title, fmt in ((axes[0], mape, "Next-day price error (MAPE, lower is better)", "{:.2f}%"),
                                 (axes[1], within, "Forecasts within 2% of the actual close", "{:.1f}%")):
        colors = [SERIES[0] if "proposed" in l else AXIS for l in labels]
        bars = ax.barh(labels, vals, color=colors, height=0.6, edgecolor=SURFACE, linewidth=2)
        ax.invert_yaxis()
        ax.grid(axis="y", visible=False)
        ax.set_title(title)
        for b, v in zip(bars, vals):
            ax.annotate(fmt.format(v), (b.get_width(), b.get_y() + b.get_height() / 2), xytext=(4, 0),
                        textcoords="offset points", va="center", color=INK2, fontsize=9)
        ax.set_xlim(0, max(vals) * 1.22)
    save(fig, "price_accuracy.png")


def fig_price_paths(pred):
    fig, axes = plt.subplots(2, 1, figsize=(10, 5.6), gridspec_kw={"hspace": 0.55})
    for ax, (ticker, a, b) in zip(axes, (("AAPL", "2020-02-01", "2020-05-31"), ("AAPL", "2021-01-01", "2022-05-24"))):
        g = pred[(pred.ticker == ticker) & (pred.date >= a) & (pred.date <= b)].sort_values("date")
        nxt = g.date.shift(-1)
        ax.plot(nxt, g.target_close, color=INK, linewidth=1.6, label="Actual close")
        ax.plot(nxt, g.price_rf, color=SERIES[0], linewidth=1.6, label="Random Forest (proposed)")
        ax.plot(nxt, g.price_rf_level, color=SERIES[1], linewidth=1.6, linestyle="--", label="Random Forest on price levels")
        ax.set_ylabel("price ($)")
        ax.grid(axis="x", visible=False)
        ax.set_title(f"{ticker}, {pd.Timestamp(a):%b %Y} – {pd.Timestamp(b):%b %Y}: one-day-ahead forecasts", pad=24)
        ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncols=3, fontsize=8.5, borderaxespad=0.2)
    save(fig, "price_paths_AAPL.png")


def fig_shap_global():
    imp = pd.read_csv(RESULTS / "importance.csv").head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.barh(imp.feature, imp.mean_abs_shap_bp, color=[FAM_COLOR[f] for f in imp.family], height=0.65,
            edgecolor=SURFACE, linewidth=1.5)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("mean |SHAP| (basis points of predicted next-day return)")
    ax.set_title("What the Random Forest relies on (top 15 features, test period)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=FAM_COLOR[f]) for f in FAMILIES if f in set(imp.family)]
    ax.legend(handles, [f for f in FAMILIES if f in set(imp.family)], loc="lower right", fontsize=8.5)
    save(fig, "shap_global.png")


def fig_explainers():
    imp = pd.read_csv(RESULTS / "importance.csv")
    cols = {"TreeSHAP": imp.mean_abs_shap_bp.rank(ascending=False).values}
    lime_file = RESULTS / "lime.json"
    if lime_file.exists():
        lime_imp = json.loads(lime_file.read_text())["L2_global_importance"]
        cols["LIME"] = pd.Series([lime_imp[f] for f in imp.feature]).rank(ascending=False).values
    cols["Permutation"] = imp.permutation_mse_increase.rank(ascending=False).values
    cols["MDI"] = imp.mdi.rank(ascending=False).values
    ranks = pd.DataFrame(cols, index=imp.feature)
    top = ranks.sort_values("TreeSHAP").head(12)
    styles = {"TreeSHAP": (SERIES[0], "o"), "LIME": (SERIES[3], "^"), "Permutation": (SERIES[1], "s"), "MDI": (SERIES[2], "D")}
    offsets = np.linspace(-0.27, 0.27, len(cols))
    fig, ax = plt.subplots(figsize=(6.6, 4.8))
    for i, (feat, r) in enumerate(top.iterrows()):
        ax.plot([r.min(), r.max()], [i, i], color=AXIS, linewidth=1.2, zorder=1)
    for off, col in zip(offsets, cols):
        color, marker = styles[col]
        ax.scatter(top[col], np.arange(len(top)) + off, color=color, s=34, marker=marker, label=col, zorder=2,
                   edgecolor=SURFACE, linewidth=1.0)
    ax.set_yticks(range(len(top)), top.index)
    ax.invert_yaxis()
    ax.set_xlabel("importance rank among 32 features (1 = most important)")
    ax.set_xlim(0, 33)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=8.5)
    ax.set_title(f"Do {len(cols)} explainers agree? (top 12 by TreeSHAP)")
    save(fig, "explainer_agreement.png")


def fig_lime_vs_shap(lime):
    cases = [c for c in ("AAPL 2020-03-16", "JPM 2022-05-18") if c in lime["L1_local"]]
    fig, axes = plt.subplots(1, len(cases), figsize=(11.5, 3.9), gridspec_kw={"wspace": 0.55})
    for ax, name in zip(np.atleast_1d(axes), cases):
        c = lime["L1_local"][name]
        feats = list(dict.fromkeys(list(c["shap_dollars"])[:6] + list(c["lime_dollars"])[:6]))
        y = np.arange(len(feats))
        sv = [c["shap_dollars"].get(f, np.nan) for f in feats]
        lv = [c["lime_dollars"].get(f, np.nan) for f in feats]
        ax.barh(y - 0.2, np.nan_to_num(sv), 0.38, color=SERIES[0], edgecolor=SURFACE, linewidth=1, label="SHAP")
        ax.barh(y + 0.2, np.nan_to_num(lv), 0.38, color=SERIES[3], edgecolor=SURFACE, linewidth=1, label="LIME")
        ax.set_yticks(y, feats)
        ax.invert_yaxis()
        ax.axvline(0, color=AXIS, linewidth=0.8)
        ax.grid(axis="y", visible=False)
        ax.set_xlabel("contribution × close price ($)")
        ax.set_title(f"{name}: SHAP vs LIME (Spearman ρ = {c['spearman_vs_shap']:.2f}, LIME R² = {c['lime_local_R2']:.2f})",
                     fontsize=9.5)
        ax.legend(loc="lower right", fontsize=8.5)
    save(fig, "lime_vs_shap_local.png")


def fig_lime_reliability(lime):
    st, ag, fi = lime["L4_run_to_run_stability"], lime["L3_agreement_with_SHAP"], lime["L6_faithfulness"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.3), gridspec_kw={"wspace": 0.45})

    ax = axes[0]
    labels = ["Top-5\noverlap", "Rank\ncorr (ρ)", "Same top\nfeature"]
    shap_v = [1, 1, 1]
    lime_v = [st["top5_overlap_mean"], st["spearman_median"], st["top1_identical_all_seeds_share"]]
    x = np.arange(3)
    for off, vals, color, lab in ((-0.19, shap_v, SERIES[0], "SHAP"), (0.19, lime_v, SERIES[3], "LIME")):
        bars = ax.bar(x + off, vals, 0.36, color=color, edgecolor=SURFACE, linewidth=2, label=lab)
        for b in bars:
            ax.annotate(f"{b.get_height():.2f}", (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 3),
                        textcoords="offset points", ha="center", fontsize=8.5, color=INK2)
    ax.set_xticks(x, labels, fontsize=8.5)
    ax.set_ylim(0, 1.3)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper center", ncols=2, fontsize=8.5)
    ax.set_title("Same stock-day, repeated runs")

    ax = axes[1]
    for key, color, label in (("SHAP", SERIES[0], "SHAP order"), ("LIME", SERIES[3], "LIME order"), ("Random", AXIS, "Random order")):
        ax.plot(fi["k"], fi["abs_change_bp"][key], color=color, linewidth=2, marker="o", markersize=5,
                markeredgecolor=SURFACE, markeredgewidth=1.2, label=f"{label} (AOPC {fi['AOPC_bp'][key]:.1f} bp)")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_xscale("symlog", linthresh=1)
    ax.set_xticks(fi["k"], [str(k) for k in fi["k"]])
    ax.set_xlim(0, 40)
    ax.set_ylim(0, None)
    ax.set_xlabel("features removed")
    ax.set_ylabel("mean |Δ forecast| (bp)")
    ax.set_title("Faithfulness: deletion curves")

    ax = axes[2]
    r2 = pd.read_pickle(RESULTS / "lime_sample.pkl")["r2"].ravel()
    ax.hist(r2, bins=30, color=SERIES[3], edgecolor=SURFACE, linewidth=1)
    ax.axvline(np.median(r2), color=INK, linewidth=1.2)
    ax.annotate(f"median {np.median(r2):.2f}", (np.median(r2), ax.get_ylim()[1] * 0.92), xytext=(5, 0),
                textcoords="offset points", fontsize=8.5, color=INK2)
    ax.set_xlim(0, 1)
    ax.set_xlabel("LIME surrogate R² (SHAP is exact: 1.0)")
    ax.set_ylabel("explanations")
    ax.grid(axis="x", visible=False)
    ax.set_title("How well LIME's linear model fits")
    fig.suptitle(f"LIME vs SHAP reliability (LIME agrees with SHAP: median ρ = {ag['spearman_median']:.2f}, "
                 f"top-5 overlap {ag['top5_overlap_mean']:.0%})", x=0.125, ha="left", y=1.07, fontsize=11, fontweight="bold")
    save(fig, "lime_reliability.png")


def stacked_shares(ax, shares, groups):
    left = np.zeros(len(groups))
    for fam in FAMILIES:
        vals = np.array([shares[g][fam] for g in groups])
        ax.barh(groups, vals, left=left, color=FAM_COLOR[fam], edgecolor=SURFACE, linewidth=2, height=0.62, label=fam)
        for i, v in enumerate(vals):
            if v >= 0.07:
                ax.text(left[i] + v / 2, i, f"{v:.0%}", ha="center", va="center", color="white", fontsize=8)
        left += vals
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.grid(axis="y", visible=False)
    ax.invert_yaxis()


def fig_regimes(xai):
    r = xai["X4_regimes"]
    groups = [g for g in REGIMES if g in r["family_shares"]]
    fig, ax = plt.subplots(figsize=(9.5, 2.9))
    stacked_shares(ax, r["family_shares"], groups)
    ax.set_title(f"Share of SHAP attribution by feature family across market regimes "
                 f"(permutation test p = {r['p_value']:.3f})")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncols=7, fontsize=8.2, handlelength=1)
    save(fig, "regime_family_shares.png")


def fig_sectors(xai):
    s = xai["X4_sectors"]
    groups = s["groups"]
    M = np.array([[s["family_shares"][g][f] for f in FAMILIES] for g in groups])
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    im = ax.imshow(M, cmap=SEQ, aspect="auto", vmin=0)
    ax.set_xticks(range(len(FAMILIES)), list(FAMILIES), rotation=30, ha="right")
    ax.set_yticks(range(len(groups)), groups)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, f"{M[i, j]:.0%}", ha="center", va="center", fontsize=7.8,
                    color="white" if M[i, j] > 0.6 * M.max() else INK)
    ax.grid(False)
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cb.outline.set_visible(False)
    cb.ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.set_title(f"SHAP share by feature family and GICS sector (permutation test p = {s['p_value']:.3f})")
    save(fig, "sector_family_shares.png")


def fig_dependence():
    d = pd.read_pickle(RESULTS / "shap_sample.pkl")
    imp = pd.read_csv(RESULTS / "importance.csv")
    top = imp.feature.head(4).tolist()
    fig, axes = plt.subplots(1, 4, figsize=(12, 2.9), gridspec_kw={"wspace": 0.35})
    for ax, feat in zip(axes, top):
        j = FEATURES.index(feat)
        x, y = d["X"][:, j], 1e4 * d["shap"][:, j]
        lo, hi = np.quantile(x, [0.005, 0.995])
        keep = (x >= lo) & (x <= hi)
        ax.hexbin(x[keep], y[keep], gridsize=40, cmap=SEQ, mincnt=1, bins="log", linewidths=0)
        order = np.argsort(x[keep])
        xs, ys = x[keep][order], y[keep][order]
        bins = np.array_split(np.arange(len(xs)), 25)
        ax.plot([xs[b].mean() for b in bins], [ys[b].mean() for b in bins], color=SERIES[1], linewidth=2)
        ax.axhline(0, color=AXIS, linewidth=0.8)
        ax.set_title(feat, fontsize=10)
        ax.set_xlabel(f"{feat} value")
        ax.grid(False)
    axes[0].set_ylabel("SHAP (bp of return)")
    fig.suptitle("How the top features move the forecast (hexbin density; orange = binned mean)", x=0.125, ha="left",
                 y=1.06, fontsize=11, fontweight="bold")
    save(fig, "shap_dependence.png")


def fig_local(xai):
    cases = list(xai["X3_local"].items())[:2]
    fig, axes = plt.subplots(1, len(cases), figsize=(11, 3.4), gridspec_kw={"wspace": 0.75})
    for ax, (name, c) in zip(np.atleast_1d(axes), cases):
        items = list(c["top_contributions_$"].items())[::-1]
        vals = [v["dollars"] for _, v in items]
        labels = [f"{k} = {v['value']:.3g}" for k, v in items]
        ax.barh(labels, vals, color=[POS if v >= 0 else NEG for v in vals], height=0.6, edgecolor=SURFACE, linewidth=1.5)
        ax.axvline(0, color=AXIS, linewidth=0.8)
        ax.grid(axis="y", visible=False)
        ax.set_xlabel("contribution to next-day price forecast ($)")
        ax.set_title(f"{name}: close ${c['close']:.2f} → forecast ${c['predicted_close']:.2f} "
                     f"(actual ${c['actual_next_close']:.2f})", fontsize=9.5)
    save(fig, "local_explanations.png")


def fig_faithfulness(xai):
    f = xai["R1_faithfulness"]
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    for key, color, label in (("top", SERIES[0], "Highest |SHAP| removed first"), ("random", SERIES[1], "Random order")):
        ax.plot(f["k"], f["abs_change_bp"][key], color=color, linewidth=2, marker="o", markersize=5.5,
                markeredgecolor=SURFACE, markeredgewidth=1.5)
        ax.annotate(label, (f["k"][-1], f["abs_change_bp"][key][-1]), xytext=(6, 0), textcoords="offset points",
                    va="center", color=INK2, fontsize=9)
    ax.set_xscale("symlog", linthresh=1)
    ax.set_xticks(f["k"], [str(k) for k in f["k"]])
    ax.set_xlim(0, 110)
    ax.set_xlabel("features replaced by background values")
    ax.set_ylabel("mean |Δ forecast| (bp)")
    ax.set_ylim(0, None)
    ax.set_title("Faithfulness: removing top-SHAP features first")
    save(fig, "faithfulness.png")


def fig_stability(xai):
    seeds, retrain, san = xai["R2_seed_stability"], xai["R2_retrain_stability"], xai["R3_sanity_shuffled_labels"]
    labels = ["Different random seeds\n(same data)"] + [f"Retrain {k.replace(' model', '')}" for k in retrain] + \
             ["vs fully shuffled\nlabels (no signal)", "vs labels shuffled\nwithin each day"]
    nulls = [san["fully_shuffled"], san["shuffled_within_day"]]
    tau = [seeds["global_kendall_tau"]] + [v["global_kendall_tau"] for v in retrain.values()] + \
          [n["global_kendall_tau_vs_real"] for n in nulls]
    rho = [seeds["row_spearman_median"]] + [v["row_spearman_median"] for v in retrain.values()] + \
          [n["row_spearman_median_vs_real"] for n in nulls]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(10.5, 3.3))
    b1 = ax.bar(x - 0.19, tau, 0.36, color=SERIES[0], edgecolor=SURFACE, linewidth=2, label="Global ranking (Kendall τ)")
    b2 = ax.bar(x + 0.19, rho, 0.36, color=SERIES[1], edgecolor=SURFACE, linewidth=2, label="Per-stock-day explanation (median Spearman ρ)")
    for bars in (b1, b2):
        for b in bars:
            ax.annotate(f"{b.get_height():.2f}", (b.get_x() + b.get_width() / 2, max(b.get_height(), 0)), xytext=(0, 3),
                        textcoords="offset points", ha="center", color=INK2, fontsize=8.5)
    ax.set_xticks(x, labels, fontsize=8.5)
    ax.axhline(0, color=AXIS, linewidth=0.8)
    ax.set_ylim(min(0, min(tau + rho) - 0.1), 1.12)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper right", fontsize=8.5, ncols=2, bbox_to_anchor=(1, 1.02))
    ax.set_title("Stability and sanity of the explanations (1 = identical)")
    save(fig, "stability_sanity.png")


def main():
    style()
    FIGURES.mkdir(parents=True, exist_ok=True)
    metrics = json.loads((RESULTS / "metrics.json").read_text())
    xai = json.loads((RESULTS / "xai.json").read_text())
    pred = add_forecasts(pd.read_pickle(RESULTS / "predictions.pkl"))
    fig_price_accuracy(metrics)
    fig_price_paths(pred)
    fig_shap_global()
    fig_explainers()
    fig_regimes(xai)
    fig_sectors(xai)
    fig_dependence()
    fig_local(xai)
    fig_faithfulness(xai)
    fig_stability(xai)
    if (RESULTS / "lime.json").exists():
        lime = json.loads((RESULTS / "lime.json").read_text())
        fig_lime_vs_shap(lime)
        fig_lime_reliability(lime)
    print("figures:", sorted(p.name for p in FIGURES.glob("*.png")))


if __name__ == "__main__":
    main()

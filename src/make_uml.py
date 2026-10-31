"""Design diagrams for chapter 4 of the VIT report -> results/figures/design/*.png

Architecture, data-flow (level 0 and 1), use case, module structure and a sequence
diagram, drawn from the code as it actually is rather than from an idealised plan.
Captions live in the report, so the figures carry no title of their own.

    python src/make_uml.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

from config import FIGURES  # noqa: E402

OUT = FIGURES / "design"
INK, MUTED, LINE, SURFACE = "#0b0b0b", "#52514e", "#898781", "#fcfcfb"
BLUE, ORANGE, GREEN, AMBER, PURPLE = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#4a3aa7"
PALE = {BLUE: "#e3eefc", ORANGE: "#fdeae1", GREEN: "#e0f5ed", AMBER: "#fdf3dd", PURPLE: "#eae7f7",
        MUTED: "#f0efea"}
FONT = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100 * h / w)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, edge=BLUE, size=8.5, weight="normal", radius=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                                facecolor=PALE[edge], edgecolor=edge, linewidth=1.3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=INK,
            fontweight=weight, fontfamily=FONT, linespacing=1.5)


def sq(ax, x, y, w, h, text, size=8.5):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=PALE[MUTED], edgecolor=MUTED, linewidth=1.3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=INK,
            fontfamily=FONT, linespacing=1.5)


def store(ax, x, y, w, h, text, size=7.0):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=PALE[MUTED], edgecolor=MUTED, linewidth=1.2))
    ax.plot([x, x + w], [y + h, y + h], color=MUTED, linewidth=2.4)
    ax.text(x + w / 2, y + h / 2 - 0.3, text, ha="center", va="center", fontsize=size, color=INK,
            fontfamily=FONT)


def ellipse(ax, x, y, w, h, text, size=7.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={h / 2}",
                                facecolor=PALE[GREEN], edgecolor=GREEN, linewidth=1.3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=INK,
            fontfamily=FONT, linespacing=1.45)


def arrow(ax, p, q, text=None, colour=MUTED, dashed=False, offset=(0, 1.6), size=7.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=11, color=colour,
                                 linewidth=1.2, linestyle="--" if dashed else "-", shrinkA=1, shrinkB=1))
    if text:
        ax.text((p[0] + q[0]) / 2 + offset[0], (p[1] + q[1]) / 2 + offset[1], text, ha="center",
                va="center", fontsize=size, color=MUTED, fontfamily=FONT, linespacing=1.35)


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print("wrote", OUT / name)


def architecture():
    fig, ax = canvas(11, 6.0)          # y: 0 .. 54.5
    sq(ax, 2.0, 43, 31, 8.5, "Raw panel  (ESTIMATE S&P 500)\n474 tickers x 2,526 days x OHLCV", size=7.4)
    sq(ax, 49.5, 43, 31, 8.5, "Yahoo Finance via yfinance\nprices to the latest close", size=7.4)

    stages = [("1  Data", "data.py\nclean 474 tickers\nrepair 3 defects", BLUE),
              ("2  Features", "features.py\n32 features\n7 families", BLUE),
              ("3  Tune", "tune.py\nvalidation 2018\nleaf 5000, mtry 0.3", MUTED),
              ("4  Train", "train.py\nwalk-forward RF\n4 yearly models", ORANGE),
              ("5  Evaluate", "evaluate.py\nreturn + price skill\nDM, binomial, deciles", AMBER),
              ("6  Explain", "explain.py\nlime_explain.py\nTreeSHAP + LIME audit", GREEN)]
    w, gap, x0 = 14.2, 2.0, 2.0
    for i, (head, body, edge) in enumerate(stages):
        bx = x0 + i * (w + gap)
        box(ax, bx, 21, w, 16, f"{head}\n\n{body}", edge=edge, size=7.0)
        if i:
            arrow(ax, (bx - gap + 0.2, 29), (bx - 0.2, 29), colour=LINE)
        arrow(ax, (bx + w / 2, 21), (bx + w / 2, 15.2), colour=LINE)

    arrow(ax, (17.5, 43), (9.1, 37.2), colour=LINE)
    arrow(ax, (57.7, 43), (57.7, 37.2), colour=ORANGE)
    ax.text(58.7, 40.0, "live.py", ha="left", va="center", fontsize=7.2, color=ORANGE,
            fontweight="bold", fontfamily=FONT)

    box(ax, 2.0, 3.5, 46.4, 11.5, "Artifacts\nmetrics.json   xai.json   lime.json\n"
                                  "importance.csv   shap_sample.pkl", edge=PURPLE, size=7.4)
    box(ax, 50.8, 3.5, 46.4, 11.5, "Presentation\nplots.py  ->  15 result figures\n"
                                   "app.py  ->  interactive audit page", edge=PURPLE, size=7.4)
    save(fig, "architecture.png")


def dfd_level0():
    fig, ax = canvas(10, 3.8)          # y: 0 .. 38
    sq(ax, 1.5, 12, 19, 13, "Market data\nvendor\n(ESTIMATE / Yahoo)", size=8)
    box(ax, 38.5, 9.5, 23, 18, "0\n\nStock forecasting\nand explanation\naudit system",
        edge=BLUE, size=8.6, weight="bold", radius=2.0)
    sq(ax, 79.5, 12, 19, 13, "Analyst\n(user of the\ndemonstration)", size=8)
    arrow(ax, (20.5, 21), (38.5, 21), "daily OHLCV,\nGICS sectors", offset=(0, 3.6))
    arrow(ax, (38.5, 15), (20.5, 15), "ticker list", offset=(0, -2.6))
    arrow(ax, (79.5, 21), (61.5, 21), "stock +\ntrading day", offset=(0, 3.6))
    arrow(ax, (61.5, 15), (79.5, 15), "forecast, SHAP, LIME,\nagreement, audit", offset=(0, -3.6))
    save(fig, "dfd_level0.png")


def dfd_level1():
    fig, ax = canvas(11, 5.0)          # y: 0 .. 45.5
    sq(ax, 0.5, 27, 14, 9, "Market data\nvendor", size=7.6)
    sq(ax, 0.5, 11, 14, 9, "Analyst", size=7.6)

    procs = [("1.0\nClean panel", 19.5, 27, BLUE), ("2.0\nBuild\nfeatures", 37.0, 27, BLUE),
             ("3.0\nTune and\ntrain", 54.5, 27, ORANGE), ("4.0\nEvaluate", 72.0, 27, AMBER),
             ("5.0\nExplain\n(SHAP, LIME)", 54.5, 10.5, GREEN), ("6.0\nAudit\nexplanations", 72.0, 11, GREEN),
             ("7.0\nServe forecast\nand audit", 19.5, 11, PURPLE)]
    for text, x, y, edge in procs:
        box(ax, x, y, 15.5, 9.5, text, edge=edge, size=7.0, radius=1.8)

    for text, x, y in [("D1  panel_clean.pkl", 19.5, 38.5), ("D2  features.pkl", 37.0, 38.5),
                       ("D3  models/*.joblib", 54.5, 38.5), ("D4  metrics.json", 72.0, 38.5),
                       ("D5  xai.json, lime.json", 72.0, 21.0)]:
        store(ax, x, y, 15.5, 5.2, text)

    arrow(ax, (14.5, 31.5), (19.5, 31.5))
    for a in (35.0, 52.5, 70.0):
        arrow(ax, (a, 31.5), (a + 2.0, 31.5))
    for x in (27.25, 44.75, 62.25, 79.75):
        arrow(ax, (x, 36), (x, 38.5), colour=LINE)
    arrow(ax, (44.75, 27), (58.0, 20.2), colour=LINE)
    arrow(ax, (62.25, 27), (62.25, 20.2), colour=LINE)
    arrow(ax, (70.0, 15.5), (72.0, 15.5))
    arrow(ax, (79.75, 20), (79.75, 21), colour=LINE)

    # 6.0 -> 7.0 routed under the process row so it crosses nothing.
    ax.plot([79.75, 79.75, 27.25], [11, 5.5, 5.5], color=MUTED, linewidth=1.2)
    arrow(ax, (27.25, 5.5), (27.25, 11), colour=MUTED)
    ax.text(53, 3.6, "explanations + audit", ha="center", va="center", fontsize=7.0, color=MUTED,
            fontfamily=FONT)

    arrow(ax, (19.5, 17.5), (14.5, 17.5))
    ax.text(17.0, 19.4, "page", ha="center", va="center", fontsize=7.0, color=MUTED, fontfamily=FONT)
    arrow(ax, (14.5, 13.5), (19.5, 13.5))
    ax.text(17.0, 11.6, "ticker,\ndate", ha="center", va="center", fontsize=7.0, color=MUTED,
            fontfamily=FONT, linespacing=1.3)
    save(fig, "dfd_level1.png")


def use_case():
    fig, ax = canvas(10, 6.6)          # y: 0 .. 66
    ax.add_patch(Rectangle((23, 1.5), 54, 61, facecolor="none", edgecolor=MUTED, linewidth=1.3))
    ax.text(50, 59.5, "Forecast-and-audit system", ha="center", va="center", fontsize=8.6,
            fontweight="bold", color=INK, fontfamily=FONT)

    def stick(x, y, label):
        ax.add_patch(Circle((x, y + 7.0), 1.5, facecolor="none", edgecolor=INK, linewidth=1.3))
        ax.plot([x, x], [y + 2.0, y + 5.5], color=INK, linewidth=1.3)
        ax.plot([x - 2.6, x + 2.6], [y + 4.5, y + 4.5], color=INK, linewidth=1.3)
        ax.plot([x - 2.2, x], [y - 1.4, y + 2.0], color=INK, linewidth=1.3)
        ax.plot([x + 2.2, x], [y - 1.4, y + 2.0], color=INK, linewidth=1.3)
        ax.text(x, y - 3.4, label, ha="center", va="center", fontsize=7.8, color=INK,
                fontfamily=FONT, linespacing=1.4)

    stick(10, 37, "Analyst")
    stick(10, 15, "Researcher")
    stick(90, 6, "Market data\nvendor")

    cases = [("Select a stock and\ntrading day", 50), ("View forecast with\nuncertainty band", 42),
             ("Inspect the SHAP\nexplanation", 34), ("Compare SHAP\nagainst LIME", 26),
             ("Check faithfulness of\nthe explanation", 18), ("Check LIME run-to-run\nstability", 10),
             ("Refresh the next-session\nforecast", 2)]
    for text, y in cases:
        ellipse(ax, 29, y, 30, 7.0, text)
    for _, y in cases[:4]:
        arrow(ax, (14.0, 39.5), (29, y + 3.5), colour=LINE)
    for _, y in cases[4:6]:
        arrow(ax, (14.0, 17.5), (29, y + 3.5), colour=LINE)
    arrow(ax, (14.0, 17.5), (29, 5.5), colour=LINE)
    arrow(ax, (86.5, 7.0), (59, 5.5), colour=LINE)
    ax.text(74, 7.4, "supplies prices", ha="center", fontsize=7.0, color=MUTED, fontfamily=FONT)
    save(fig, "use_case.png")


def class_diagram():
    fig, ax = canvas(11, 7.0)          # y: 0 .. 63.6

    def module(x, top, w, name, members, imports, edge):
        head, mh, ih = 4.6, 3.0 * len(members), 3.4 + 2.7 * len(imports)
        h = head + mh + ih
        ax.add_patch(Rectangle((x, top - h), w, h, facecolor=SURFACE, edgecolor=edge, linewidth=1.3))
        ax.add_patch(Rectangle((x, top - head), w, head, facecolor=PALE[edge], edgecolor=edge, linewidth=1.3))
        ax.text(x + w / 2, top - head / 2, name, ha="center", va="center", fontsize=7.8,
                fontweight="bold", color=INK, fontfamily=FONT)
        for i, m in enumerate(members):
            ax.text(x + 1.1, top - head - 1.7 - 3.0 * i, m, ha="left", va="center", fontsize=6.6,
                    color=INK, fontfamily=FONT)
        ax.plot([x, x + w], [top - head - mh, top - head - mh], color=edge, linewidth=1.0)
        ax.text(x + 1.1, top - head - mh - 1.9, "imports", ha="left", va="center", fontsize=6.2,
                color=MUTED, style="italic", fontfamily=FONT)
        for i, m in enumerate(imports):
            ax.text(x + 1.1, top - head - mh - 4.4 - 2.7 * i, m, ha="left", va="center", fontsize=6.4,
                    color=MUTED, fontfamily=FONT)

    cols = [1.5, 26.1, 50.7, 75.3]
    w = 23.0
    grid = [
        (cols[0], 62, "config", ["+ paths, periods", "+ REGIMES, SEED"], ["(none)"], MUTED),
        (cols[1], 62, "data", ["+ main()"], ["config"], BLUE),
        (cols[2], 62, "features", ["+ FEATURES, FAMILIES", "+ build(panel)"], ["config"], BLUE),
        (cols[3], 62, "tune", ["+ main()"], ["config, features"], MUTED),
        (cols[0], 41, "train", ["+ main()"], ["config, features"], ORANGE),
        (cols[1], 41, "evaluate", ["+ PRICE_MODELS", "+ add_forecasts(df)"], ["config, features"], AMBER),
        (cols[2], 41, "explain", ["+ deletion_curves(...)", "+ group_drift_test(...)"],
         ["config, features"], GREEN),
        (cols[3], 41, "lime_explain", ["+ make_explainer(...)", "+ lime_weights(...)"],
         ["config, features"], GREEN),
        (cols[0], 20, "plots", ["+ fig_* (15)"], ["config, features", "evaluate"], PURPLE),
        (cols[1], 20, "live", ["+ main()"], ["config, features"], ORANGE),
        (cols[2], 20, "app", ["+ explain(tkr, date)", "+ faithfulness(...)"],
         ["config, features", "lime_explain"], PURPLE),
    ]
    for x, top, name, members, imports, edge in grid:
        module(x, top, w, name, members, imports, edge)

    ax.text(cols[3] + 1.0, 14.5, "Every module imports config.\nfeatures.build() is the single\n"
                                 "feature definition, shared by\nthe study and the live path.",
            ha="left", va="top", fontsize=7.0, color=ORANGE, fontweight="bold", fontfamily=FONT,
            linespacing=1.6)
    save(fig, "class_diagram.png")


def sequence():
    fig, ax = canvas(10.5, 5.8)        # y: 0 .. 55.2
    actors = [("Analyst", 8), ("app.py\nHandler", 27), ("RandomForest\n(year model)", 46),
              ("shap.\nTreeExplainer", 64.5), ("lime_explain.\nlime_weights", 84)]
    for name, x in actors:
        box(ax, x - 8.5, 47, 17, 7.0, name, edge=BLUE, size=7.2)
        ax.plot([x, x], [47, 5.0], color=LINE, linewidth=1.0, linestyle=(0, (4, 3)))

    steps = [(8, 27, "GET /api/explain?ticker=AAPL&date=...", 43),
             (27, 46, "predict(x)   ->   forecast in bp", 38.5),
             (27, 64.5, "shap_values(x)   ->   32 attributions", 34),
             (64.5, 27, "base + sum(phi) == forecast   (additivity)", 29.5),
             (27, 84, "lime_weights(x, seed = 0 .. 4)", 25),
             (84, 46, "5,000 perturbed rows -> predict", 20.5),
             (84, 27, "5 weight vectors   ->   rho, top-5 overlap", 16),
             (27, 46, "delete top-SHAP feature x 32 backgrounds", 11.5),
             (46, 27, "mean |change| vs random order   ->   ratio", 7),
             (27, 8, "forecast + SHAP + LIME + agreement + audit", 5.5)]
    for a, b, text, y in steps:
        back = b < a
        arrow(ax, (a, y), (b, y), colour=ORANGE if back else MUTED, dashed=back)
        ax.text((a + b) / 2, y + 1.3, text, ha="center", va="bottom", fontsize=6.9, color=INK,
                fontfamily=FONT)
    save(fig, "sequence.png")


def main():
    architecture()
    dfd_level0()
    dfd_level1()
    use_case()
    class_diagram()
    sequence()


if __name__ == "__main__":
    main()

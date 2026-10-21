"""Local demo server: pick a stock and a date, see the forecast and both explanations.

Everything is computed live from the saved walk-forward models, so what the page shows
is what the pipeline produces - nothing is read back from a cached result file.

    python src/app.py          # then open http://127.0.0.1:8000

Endpoints
  GET /                                   the page
  GET /api/meta                           tickers, date range, suggested cases
  GET /api/dates?ticker=AAPL              the dates that stock can be explained on
  GET /api/explain?ticker=AAPL&date=...   forecast + SHAP + LIME + agreement + audit
"""
import json
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import joblib
import numpy as np
import pandas as pd
import shap
from scipy import stats

from config import DATA, FEATURE_FILE, MODELS, RESULTS, SEED, TEST_YEARS, TRAIN_START
from features import FAMILY_OF, FEATURES
from lime_explain import lime_weights

PORT = 8000
STATIC = Path(__file__).resolve().parent / "static"
N_LIME_TRAIN = 5000       # reference rows LIME samples around, as in lime_explain.py
N_LIME_SEEDS = 5          # re-runs, to show LIME's run-to-run instability
N_BACKGROUND = 32         # replacement rows for the faithfulness test
N_RANDOM_PROBES = 8       # random features averaged in the faithfulness control
# Stock-days worth demonstrating. The first two are cases where the explainers line up; the
# next two are cases where they name a different top feature, which happened on 11 of 28
# randomly sampled stock-days. BAC also has LIME contradicting itself across its own re-runs.
CASES = [
    {"ticker": "AAPL", "date": "2020-03-16", "label": "AAPL, worst day of the COVID crash"},
    {"ticker": "XOM", "date": "2020-03-09", "label": "XOM, the 2020 oil crash"},
    {"ticker": "BAC", "date": "2019-02-28", "label": "BAC \u2014 they disagree, and LIME contradicts itself"},
    {"ticker": "KO", "date": "2021-04-13", "label": "KO \u2014 different top feature"},
    {"ticker": "JPM", "date": "2022-05-18", "label": "JPM, the 2022 bear market"},
]

STATE = {}
# explain() flips the model's n_jobs while LIME runs, so one request at a time.
LOCK = threading.Lock()


def load():
    t0 = time.time()
    df = pd.read_pickle(FEATURE_FILE)
    test = df[df.date >= f"{TEST_YEARS[0]}-01-01"]
    STATE["test"] = test.set_index(["ticker", "date"]).sort_index()
    STATE["tickers"] = sorted(test.ticker.unique())
    STATE["sector"] = test.drop_duplicates("ticker").set_index("ticker")["sector"].to_dict()
    print(f"features: {len(test):,} explainable stock-days, {len(STATE['tickers'])} stocks "
          f"[{time.time() - t0:.0f}s]", flush=True)

    load_live()
    STATE["models"], STATE["clf"], STATE["shap"], STATE["lime"], STATE["bg"] = {}, {}, {}, {}, {}
    for year in TEST_YEARS:
        model = joblib.load(MODELS / f"rf_reg_{year}.joblib")
        STATE["models"][year] = model
        STATE["clf"][year] = joblib.load(MODELS / f"rf_clf_{year}.joblib")
        STATE["shap"][year] = shap.TreeExplainer(model)
        train = df[(df.date >= TRAIN_START) & (df.date < f"{year}-01-01")]
        # The reference rows LIME samples around; a fresh explainer is built per run, because
        # a reused one is not reproducible (see lime_explain.make_explainer).
        STATE["lime"][year] = train[FEATURES].sample(N_LIME_TRAIN, random_state=SEED).values
        STATE["bg"][year] = train[FEATURES].sample(N_BACKGROUND, random_state=SEED).values
        print(f"  {year} model, TreeSHAP and LIME ready [{time.time() - t0:.0f}s]", flush=True)


def load_live():
    """The next-session forecast produced by live.py, if it has been run."""
    if not ((RESULTS / "live_forecast.pkl").exists() and (MODELS / "rf_reg_live.joblib").exists()):
        STATE["live"] = None
        print("no live forecast yet (run src/live.py to add one)", flush=True)
        return
    df = pd.read_pickle(RESULTS / "live_forecast.pkl")
    scored = pd.read_pickle(DATA / "live_features.pkl").dropna(subset=["target_ret"])
    model = joblib.load(MODELS / "rf_reg_live.joblib")
    STATE["live"] = {
        "rows": df.set_index("ticker"),
        "tickers": sorted(df.ticker.unique()),
        "model": model,
        "shap": shap.TreeExplainer(model),
        "lime": scored[FEATURES].sample(N_LIME_TRAIN, random_state=SEED).values,
        "bg": scored[FEATURES].sample(N_BACKGROUND, random_state=SEED).values,
        "meta": json.loads((RESULTS / "live_meta.json").read_text()),
    }
    m = STATE["live"]["meta"]
    print(f"live forecast: {m['n_stocks']} stocks for the session after {m['as_of_close']}, "
          f"model retrained on {m['n_train_rows']:,} stock-days", flush=True)


def delete_feature(model, x, cols, background):
    """Mean |change in forecast| (bp) when `cols` are replaced by background values."""
    base = float(model.predict(x[None])[0])
    X = np.repeat(x[None], len(background), axis=0)
    X[:, cols] = background[:, cols]
    return float(1e4 * abs(base - model.predict(X).mean()))


def faithfulness(model, x, shap_row, background, rng):
    """The project's central test, run on this one forecast: does deleting what the
    explanation called important move the forecast more than deleting something random?"""
    top = int(np.argmax(np.abs(shap_row)))
    others = [j for j in range(len(FEATURES)) if j != top]
    probes = rng.choice(others, N_RANDOM_PROBES, replace=False)
    top_change = delete_feature(model, x, [top], background)
    random_change = float(np.mean([delete_feature(model, x, [j], background) for j in probes]))
    return {"top_feature": FEATURES[top], "top_change_bp": top_change,
            "random_change_bp": random_change,
            "ratio": top_change / random_change if random_change > 1e-9 else None,
            "n_random_probes": N_RANDOM_PROBES}


def top5(a):
    return set(np.argsort(-np.abs(a))[:5])


def explain(ticker, date, live=False):
    """One forecast, explained two ways.

    `live=True` uses the model retrained up to the most recent close and forecasts the next
    session, whose outcome does not exist yet; everything else is identical."""
    clf = None
    if live:
        if not STATE.get("live"):
            return {"error": "No live forecast available. Run `python src/live.py` first."}
        L = STATE["live"]
        if ticker not in L["rows"].index:
            return {"error": f"{ticker} is not in the live universe "
                             f"(43 of the original 474 tickers no longer trade)."}
        row = L["rows"].loc[ticker]
        model, explainer, lime_ref, bg = L["model"], L["shap"], L["lime"], L["bg"]
        as_of, year = L["meta"]["as_of_close"], None
    else:
        try:
            row = STATE["test"].loc[(ticker, pd.Timestamp(date))]
        except KeyError:
            return {"error": f"No data for {ticker} on {date}. Pick a trading day in 2019-01-02 .. 2022-05-24."}
        if isinstance(row, pd.DataFrame):
            row = row.iloc[0]
        year = pd.Timestamp(date).year
        model, clf = STATE["models"][year], STATE["clf"][year]
        explainer, lime_ref, bg = STATE["shap"][year], STATE["lime"][year], STATE["bg"][year]
        as_of = str(pd.Timestamp(date).date())

    x = row[FEATURES].values.astype(np.float64)
    rng = np.random.default_rng(SEED)

    pred_ret = float(model.predict(x[None])[0])
    prob_up = float(clf.predict_proba(x[None])[0, 1]) if clf is not None else None
    close = float(row["close"])
    shap_row = explainer.shap_values(x[None])[0]
    base_value = float(np.ravel(explainer.expected_value)[0])

    model.set_params(n_jobs=1)            # LIME calls predict on many small batches
    lime_runs, lime_r2 = [], []
    for s in range(N_LIME_SEEDS):
        w, r2, _ = lime_weights(lime_ref, x, model.predict, SEED + s)
        lime_runs.append(w)
        lime_r2.append(r2)
    model.set_params(n_jobs=-1)
    lime_row = lime_runs[0]

    order = np.argsort(-np.abs(shap_row))
    features = [{"name": FEATURES[j], "family": FAMILY_OF[FEATURES[j]], "value": float(x[j]),
                 "shap_bp": float(1e4 * shap_row[j]), "lime_bp": float(1e4 * lime_row[j])}
                for j in order]

    s5, l5 = top5(shap_row), top5(lime_row)
    pairs = [(a, b) for a in range(N_LIME_SEEDS) for b in range(a + 1, N_LIME_SEEDS)]
    known = (not live) and pd.notna(row.get("target_ret"))
    return {
        "ticker": ticker, "date": as_of, "live": bool(live),
        "sector": row.get("sector") if live else STATE["sector"].get(ticker, ""), "year": year,
        "live_meta": STATE["live"]["meta"] if live else None,
        "close": close,
        "pred_ret_bp": 1e4 * pred_ret,
        "pred_close": close * float(np.exp(pred_ret)),
        "actual_ret_bp": 1e4 * float(row["target_ret"]) if known else None,
        "actual_close": float(row["target_close"]) if known else None,
        "prob_up": prob_up,
        "direction_correct": bool((pred_ret > 0) == (float(row["target_ret"]) > 0)) if known else None,
        "base_value_bp": 1e4 * base_value,
        "features": features,
        "agreement": {
            "spearman": float(stats.spearmanr(np.abs(shap_row), np.abs(lime_row))[0]),
            "top5_overlap": len(s5 & l5) / 5,
            "same_top": bool(np.argmax(np.abs(shap_row)) == np.argmax(np.abs(lime_row))),
            "sign_agreement": float(np.mean([np.sign(lime_row[j]) == np.sign(shap_row[j]) for j in s5])),
            "shap_top": FEATURES[int(np.argmax(np.abs(shap_row)))],
            "lime_top": FEATURES[int(np.argmax(np.abs(lime_row)))],
        },
        "lime_stability": {
            "n_seeds": N_LIME_SEEDS,
            "spearman_between_runs": float(np.mean([
                stats.spearmanr(np.abs(lime_runs[a]), np.abs(lime_runs[b]))[0] for a, b in pairs])),
            "top5_overlap_between_runs": float(np.mean([
                len(top5(lime_runs[a]) & top5(lime_runs[b])) / 5 for a, b in pairs])),
            "same_top_every_run": len({int(np.argmax(np.abs(w))) for w in lime_runs}) == 1,
            "per_seed_top": [FEATURES[int(np.argmax(np.abs(w)))] for w in lime_runs],
            "surrogate_r2_median": float(np.median(lime_r2)),
        },
        "faithfulness": faithfulness(model, x, shap_row, bg, rng),
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, body, ctype="application/json", code=200):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path in ("/", "/index.html"):
                return self._send((STATIC / "index.html").read_bytes(), "text/html; charset=utf-8")
            if url.path == "/api/meta":
                idx = STATE["test"].index
                return self._send(json.dumps({
                    "tickers": STATE["tickers"], "sector": STATE["sector"], "cases": CASES,
                    "live": STATE["live"]["meta"] if STATE.get("live") else None,
                    "live_tickers": STATE["live"]["tickers"] if STATE.get("live") else [],
                    "date_min": str(idx.get_level_values(1).min().date()),
                    "date_max": str(idx.get_level_values(1).max().date())}))
            if url.path == "/api/dates":
                dates = STATE["test"].loc[q["ticker"]].index
                return self._send(json.dumps([str(d.date()) for d in dates]))
            if url.path == "/api/explain":
                t0 = time.time()
                with LOCK:
                    out = explain(q["ticker"], q.get("date"), live=q.get("live") == "1")
                out["compute_seconds"] = round(time.time() - t0, 2)
                print(f"explained {q['ticker']} {q.get('date') or 'next session'} "
                      f"in {out['compute_seconds']}s", flush=True)
                return self._send(json.dumps(out))
            self._send(json.dumps({"error": "not found"}), code=404)
        except Exception as exc:                        # the page shows this, rather than hanging
            self._send(json.dumps({"error": f"{type(exc).__name__}: {exc}"}), code=500)

    def log_message(self, *args):
        pass


def main():
    print("loading models and explainers ...", flush=True)
    load()
    url = f"http://127.0.0.1:{PORT}"
    print(f"\n  demo ready at {url}   (Ctrl-C to stop)\n", flush=True)
    try:
        webbrowser.open(url)
    except Exception:
        pass
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()

// Final project deck (22 slides). Same visual language as make_slides.js.
// Every number is copied from results/metrics.json, xai.json, lime.json and live_meta.json.
//    node src/make_project_slides.js
const PptxGenJS = require("pptxgenjs");
const path = require("path");

const NAVY = "1E2761";
const INK = "16203F";
const ICE = "CADCFC";
const AMBER = "E8703A";
const GREEN = "2E7D63";
const GREY = "5A6472";
const LIGHT = "F4F7FC";
const WHITE = "FFFFFF";
const TEXT = "26324A";

const HEAD = "Cambria";
const BODY = "Calibri";
const MONO = "Consolas";

const FIG = (name) => path.join(__dirname, "..", "results", "figures", name);

const pres = new PptxGenJS();
pres.layout = "LAYOUT_WIDE";
pres.author = "StockRF-XAI";
pres.title = "Trustworthy Explanations for Random-Forest Stock Price Forecasting";

const W = 13.33, H = 7.5, M = 0.7;

function titleBar(s, kicker, title) {
  s.addText(kicker.toUpperCase(), {
    x: M, y: 0.40, w: 11, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12, bold: true, color: AMBER, charSpacing: 2,
  });
  s.addText(title, {
    x: M, y: 0.70, w: W - 2 * M, h: 0.75, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 30, bold: true, color: NAVY,
  });
}

function card(s, x, y, w, h, fill) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.08, fill: { color: fill || LIGHT },
    line: { color: fill === NAVY || fill === INK ? fill : "DCE4F2", width: 1 },
    shadow: { type: "outer", color: "9AA7BD", blur: 8, offset: 1, angle: 90, opacity: 0.22 },
  });
}

function numberBadge(s, x, y, n, colour) {
  s.addShape(pres.ShapeType.ellipse, {
    x, y, w: 0.42, h: 0.42, fill: { color: colour || NAVY }, line: { color: colour || NAVY },
  });
  s.addText(String(n), {
    x, y, w: 0.42, h: 0.42, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 14, bold: true, color: WHITE, align: "center", valign: "middle",
  });
}

function bullets(s, lines, opts) {
  s.addText(lines.map((t, k) => ({
    text: t, options: { bullet: true, breakLine: k < lines.length - 1 },
  })), Object.assign({
    isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, color: TEXT,
    paraSpaceAfter: 8, lineSpacing: 19,
  }, opts));
}

// One sentence across the bottom. Always the thing to say out loud.
function takeaway(s, text, colour) {
  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 6.28, w: W - 2 * M, h: 0.72, rectRadius: 0.06,
    fill: { color: colour || NAVY }, line: { color: colour || NAVY },
  });
  s.addText(text, {
    x: M + 0.25, y: 6.28, w: W - 2 * M - 0.5, h: 0.72, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 14.5, color: WHITE, valign: "middle",
  });
}

function table(s, rows, opts) {
  return s.addTable(rows, Object.assign({
    x: M, y: 1.7, w: W - 2 * M,
    fontFace: BODY, fontSize: 12.5, color: TEXT, valign: "middle",
    border: { type: "solid", color: "DCE4F2", pt: 1 },
    autoPage: false,
  }, opts));
}

// Header row + body rows, in the house colours.
function dataTable(s, header, body, opts) {
  const head = header.map((h) => ({
    text: h, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 12, align: "center" },
  }));
  const rows = body.map((r, i) => r.map((c, j) => ({
    text: String(c),
    options: Object.assign({
      fill: { color: i % 2 ? WHITE : LIGHT },
      align: ((opts && opts.leftCols) || [0]).includes(j) ? "left" : "center",
      fontFace: (opts && opts.monoCols) ? (opts.monoCols.includes(j) ? MONO : BODY) : (j === 0 ? BODY : MONO),
      fontSize: 12,
    }, (c.highlight || {})),
  })));
  return table(s, [head, ...rows], opts);
}

/* ======================================================= 1. Title */
{
  const s = pres.addSlide();
  s.background = { color: INK };
  s.addShape(pres.ShapeType.ellipse, { x: 10.3, y: -1.5, w: 5.2, h: 5.2, fill: { color: NAVY }, line: { color: NAVY } });
  s.addShape(pres.ShapeType.ellipse, { x: 11.6, y: 4.6, w: 3.0, h: 3.0, fill: { color: "232F63" }, line: { color: "232F63" } });
  s.addText("FINAL PROJECT REVIEW", {
    x: M, y: 1.35, w: 9.4, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, bold: true, color: AMBER, charSpacing: 2,
  });
  s.addText("Trustworthy Explanations for\nRandom-Forest Stock Price Forecasting", {
    x: M, y: 1.8, w: 9.4, h: 1.9, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 38, bold: true, color: WHITE, lineSpacing: 44,
  });
  s.addText("A SHAP and LIME reliability audit on 474 S&P 500 stocks", {
    x: M, y: 3.75, w: 9.4, h: 0.5, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 17, italic: true, color: ICE,
  });
  const stats = [["1,097,165", "stock-days"], ["405,545", "graded forecasts"],
                 ["32", "features"], ["2", "explainers, 5 audits"]];
  stats.forEach(([big, small], i) => {
    const x = M + i * 3.0;
    s.addText(big, { x, y: 4.85, w: 2.9, h: 0.55, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 26, bold: true, color: AMBER });
    s.addText(small, { x, y: 5.4, w: 2.9, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, color: ICE });
  });
  s.addText("Live demo: pick any stock, get tomorrow's forecast with both explanations audited in real time", {
    x: M, y: 6.3, w: 11, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, color: ICE,
  });
  s.addNotes("Two halves. First: does the forecast have any skill, measured honestly. Second, and the real contribution: can the SHAP and LIME explanations of that forecast be trusted. The answer to the first is barely, and the answer to the second is a qualified yes for SHAP and a qualified no for LIME - and we can prove both.");
}

/* ======================================================= 2. The two problems */
{
  const s = pres.addSlide();
  titleBar(s, "Motivation", "Two problems this project attacks");
  const items = [
    ["1", "Accuracy reported without a benchmark",
      ["Published price models report R² of 0.88 to 0.99.",
       "But “tomorrow = today” already scores R² 0.99938 on the same data.",
       "With no naive baseline, a 98% accuracy claim carries no information."]],
    ["2", "Explanations presented, never tested",
      ["SHAP and LIME rankings get reported as market insight.",
       "Nobody checks whether they are faithful, stable, or agree with each other.",
       "An explanation can describe noise, or one random seed, and look convincing."]],
  ];
  items.forEach(([n, head, lines], i) => {
    const x = M + i * 6.15;
    card(s, x, 1.7, 5.75, 3.6);
    numberBadge(s, x + 0.35, 2.0, n, i === 0 ? NAVY : AMBER);
    s.addText(head, { x: x + 0.92, y: 1.98, w: 4.6, h: 0.75, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 17, bold: true, color: NAVY });
    bullets(s, lines, { x: x + 0.4, y: 2.9, w: 5.0, h: 2.3, fontSize: 14 });
  });
  s.addText("In finance both failures cost money: a model with no skill that looks accurate, explained by a method nobody validated.", {
    x: M, y: 5.5, w: W - 2 * M, h: 0.5, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 15, italic: true, color: GREY,
  });
  takeaway(s, "This project builds the forecast honestly, then spends most of its effort auditing the explanation of it.");
  s.addNotes("Keep this slide short. The audience needs to accept that both problems are real before any result lands.");
}

/* ======================================================= 3. Objective & RQs */
{
  const s = pres.addSlide();
  titleBar(s, "Objective", "One objective, six research questions");
  card(s, M, 1.65, W - 2 * M, 1.0, NAVY);
  s.addText("Build a leakage-free next-day return forecaster for 474 S&P 500 stocks, then determine whether its SHAP and LIME explanations are faithful, stable and mutually consistent enough to be reported as findings.", {
    x: M + 0.3, y: 1.65, w: W - 2 * M - 0.6, h: 1.0, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 15.5, color: WHITE, valign: "middle", lineSpacing: 22,
  });
  const rqs = [
    ["RQ1", "Does the model have real forecast skill once it is scored in return space against proper baselines?"],
    ["RQ2", "What does the model actually use, globally and on individual forecasts?"],
    ["RQ3", "Are the SHAP explanations faithful to the model and stable across seeds and retrains?"],
    ["RQ4", "Do the explanations drift across market regimes and GICS sectors?"],
    ["RQ5", "Can the explainer be fooled by a model trained on shuffled labels?"],
    ["RQ6", "Do SHAP and LIME agree, and which should be trusted here?"],
  ];
  rqs.forEach(([tag, text], i) => {
    const col = i % 2, row = (i - col) / 2;
    const x = M + col * 6.15, y = 2.95 + row * 1.08;
    card(s, x, y, 5.75, 0.95, col === 0 ? LIGHT : WHITE);
    s.addText(tag, { x: x + 0.25, y: y + 0.08, w: 0.8, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 15, bold: true, color: AMBER });
    s.addText(text, { x: x + 1.05, y: y + 0.08, w: 4.5, h: 0.8, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, color: TEXT, lineSpacing: 16 });
  });
  takeaway(s, "RQ1 is the sanity floor. RQ2 to RQ6 are the project.", AMBER);
  s.addNotes("If asked which RQ matters most: RQ5, because it is the only one that can expose an explainer as describing nothing.");
}

/* ======================================================= 4. Data */
{
  const s = pres.addSlide();
  titleBar(s, "Data", "474 S&P 500 stocks, ten years, cleaned");
  const stats = [["474", "stocks"], ["2,526", "trading days"], ["1,193,405", "stock-days"], ["11", "GICS sectors"]];
  stats.forEach(([big, small], i) => {
    const x = M + i * 3.07;
    card(s, x, 1.65, 2.85, 1.1);
    s.addText(big, { x: x + 0.2, y: 1.78, w: 2.5, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 24, bold: true, color: NAVY });
    s.addText(small, { x: x + 0.2, y: 2.28, w: 2.5, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, color: GREY });
  });
  card(s, M, 2.95, 6.0, 3.1);
  s.addText("Source", { x: M + 0.3, y: 3.1, w: 5.4, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: NAVY });
  bullets(s, [
    "Public S&P 500 benchmark released with ESTIMATE (Huynh et al., WSDM 2023).",
    "Daily open, high, low, close, adjusted close and volume, 14 May 2012 to 25 May 2022.",
    "Each stock's GICS sector, used to group explanations.",
  ], { x: M + 0.3, y: 3.5, w: 5.5, h: 2.4, fontSize: 13.5 });
  card(s, M + 6.3, 2.95, 6.0, 3.1);
  s.addText("Three real data bugs found and fixed", { x: M + 6.6, y: 3.1, w: 5.4, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: AMBER });
  bullets(s, [
    "Rows before a stock was listed have no adjusted close — dropped.",
    "15 tickers store open/high/low adjusted but close unadjusted, so the day's high sits below its close — put on one basis.",
    "GOOG before 27 Mar 2014 is a different share class, a −300% one-day jump — dropped.",
  ], { x: M + 6.6, y: 3.5, w: 5.5, h: 2.4, fontSize: 13.5 });
  takeaway(s, "Cleaning is reported, not hidden: every fix is a named assertion in src/data.py that reruns on every build.");
  s.addNotes("The 15-ticker fix is worth mentioning if anyone asks how carefully the data was handled. The code tests both adjustment conventions per ticker and keeps whichever puts the close inside the day's range more often.");
}

/* ======================================================= 5. Features */
{
  const s = pres.addSlide();
  titleBar(s, "Features", "32 features in 7 families, none of them peeking");
  const fams = [
    ["Past returns", "6", "moves over 1, 2, 5, 10, 20, 60 days"],
    ["Trend", "5", "distance from 5/20/50/200-day averages, MACD"],
    ["Oscillators", "3", "RSI, stochastic, Bollinger %b"],
    ["Volatility", "6", "5/20/60-day volatility, ATR, range, band width"],
    ["Volume", "3", "volume vs normal, volume trend, dollar volume"],
    ["Candle", "3", "gap at the open, body, close within the range"],
    ["Market & sector", "6", "market return and volatility, sector return, beta"],
  ];
  dataTable(s, ["Family", "n", "What it measures"],
    fams.map((f) => [f[0], f[1], f[2]]),
    { y: 1.65, colW: [2.4, 0.6, 4.6], rowH: 0.42, w: 7.6, leftCols: [0, 2], monoCols: [1] });
  card(s, 8.6, 1.65, 4.05, 4.4, LIGHT);
  s.addText("The rule that makes it valid", { x: 8.9, y: 1.82, w: 3.5, h: 0.6, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: AMBER });
  bullets(s, [
    "Every feature for (stock, day t) uses only prices up to and including day t's close.",
    "Target = next day's log return, log(close_t+1 / close_t), reported in basis points. 1 bp = 0.01%.",
    "A price forecast is only that return applied to today's close — the model never predicts a dollar price directly.",
    "1,097,165 usable stock-days after dropping any row with a missing feature or target.",
  ], { x: 8.9, y: 2.45, w: 3.5, h: 3.5, fontSize: 12.5 });
  takeaway(s, "Leakage is the one bug that cannot be caught by looking at results, so it is prevented by construction instead.");
  s.addNotes("If a feature accidentally contained tomorrow's information the model would look brilliant and be worthless. That is why features are built on wide date-by-ticker tables with explicit shifts, never on per-row loops.");
}

/* ======================================================= 6. Architecture */
{
  const s = pres.addSlide();
  titleBar(s, "Proposed system", "Six stages, each one a file you can run");
  const stages = [
    ["1", "Clean", "data.py", "474 stocks × 2,526 days\n3 data bugs fixed"],
    ["2", "Engineer", "features.py", "32 features, 7 families\n1,097,165 stock-days"],
    ["3", "Tune", "tune.py", "6 settings, validated on\n2017 and 2018 only"],
    ["4", "Train", "train.py", "Walk-forward, 4 retrains\n405,545 forecasts"],
    ["5", "Evaluate", "evaluate.py", "Return space first,\nbaselines + DM tests"],
    ["6", "Explain & audit", "explain.py\nlime_explain.py", "SHAP + LIME,\n5 reliability tests"],
  ];
  stages.forEach(([n, name, file, detail], i) => {
    const x = M + i * 2.07;
    card(s, x, 1.75, 1.92, 3.3, i === 5 ? NAVY : LIGHT);
    numberBadge(s, x + 0.12, 1.88, n, i === 5 ? AMBER : NAVY);
    s.addText(name, { x: x + 0.15, y: 2.42, w: 1.65, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 14.5, bold: true, color: i === 5 ? WHITE : NAVY });
    s.addText(file, { x: x + 0.15, y: 2.82, w: 1.7, h: 0.6, isTextBox: true, margin: 0, fontFace: MONO, fontSize: 10.5, color: i === 5 ? ICE : AMBER });
    s.addText(detail, { x: x + 0.15, y: 3.45, w: 1.65, h: 1.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 11.5, color: i === 5 ? ICE : TEXT, lineSpacing: 15 });
    if (i < 5) {
      s.addText("›", { x: x + 1.88, y: 3.1, w: 0.25, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 22, bold: true, color: AMBER, align: "center" });
    }
  });
  card(s, M, 5.25, 5.9, 0.85, WHITE);
  s.addText("live.py — forecast a day that has not happened", { x: M + 0.25, y: 5.3, w: 5.4, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 13.5, bold: true, color: NAVY });
  s.addText("Same features, same hyperparameters, retrained to the latest close", { x: M + 0.25, y: 5.62, w: 5.4, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, color: GREY });
  card(s, M + 6.1, 5.25, 6.2, 0.85, WHITE);
  s.addText("app.py — interactive demo on localhost:8000", { x: M + 6.35, y: 5.3, w: 5.7, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 13.5, bold: true, color: NAVY });
  s.addText("Imports the study's own SHAP and LIME code, so the demo cannot drift", { x: M + 6.35, y: 5.62, w: 5.7, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, color: GREY });
  takeaway(s, "Nothing is duplicated: live.py imports features.build(), app.py imports lime_weights(), so demo and study are the same pipeline.");
  s.addNotes("The last point matters if someone suspects the demo is a friendlier version of the model. It literally calls the study's functions.");
}

/* ======================================================= 7. Methodology */
{
  const s = pres.addSlide();
  titleBar(s, "Methodology", "Walk-forward, so nothing is scored on data it saw");
  const bands = [
    ["Train", "2013-03 → 2016-12", NAVY],
    ["Validate", "2017 and 2018", AMBER],
    ["Test", "2019 → 2022-05", GREEN],
  ];
  bands.forEach(([name, span, col], i) => {
    const x = M + i * 4.1;
    card(s, x, 1.65, 3.85, 0.95, LIGHT);
    s.addShape(pres.ShapeType.roundRect, { x: x + 0.2, y: 1.83, w: 0.18, h: 0.6, rectRadius: 0.04, fill: { color: col }, line: { color: col } });
    s.addText(name, { x: x + 0.52, y: 1.8, w: 3.1, h: 0.33, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 15, bold: true, color: NAVY });
    s.addText(span, { x: x + 0.52, y: 2.12, w: 3.1, h: 0.33, isTextBox: true, margin: 0, fontFace: MONO, fontSize: 12.5, color: GREY });
  });
  dataTable(s, ["Test year", "Trained on", "Forecasts made", "Fit time"], [
    ["2019", "691,620 stock-days", "119,340", "96 s"],
    ["2020", "810,960", "119,919", "120 s"],
    ["2021", "930,879", "119,448", "160 s"],
    ["2022 (to May)", "1,050,327", "46,838", "185 s"],
    ["Total", "—", "405,545 over 856 days", "9 min"],
  ], { y: 2.85, colW: [1.9, 2.3, 2.3, 1.1], rowH: 0.4, w: 7.6 });
  card(s, 8.6, 2.85, 4.05, 3.2, LIGHT);
  s.addText("The model", { x: 8.9, y: 3.0, w: 3.5, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: NAVY });
  bullets(s, [
    "Random Forest regressor, 300 trees.",
    "min_samples_leaf 5000, max_features 0.3, max_samples 0.25 — chosen on validation MSE.",
    "Baselines: naive persistence, historical drift, Ridge, and a Random Forest on raw price levels.",
  ], { x: 8.9, y: 3.42, w: 3.5, h: 2.5, fontSize: 12.5 });
  takeaway(s, "The chosen settings are the most heavily smoothed on the grid — the data itself is saying there is almost nothing to fit.");
  s.addNotes("Hyperparameters come from 2017 and 2018 only. The test period is never touched during selection, which is what makes the RQ1 numbers quotable.");
}

/* ======================================================= 8. The accuracy trap */
{
  const s = pres.addSlide();
  titleBar(s, "RQ1 — finding 1", "The same forecasts, scored two ways");
  s.addImage({ path: FIG("price_vs_return.png"), x: M, y: 1.6, w: 7.9, h: 2.96 });
  card(s, 8.75, 1.6, 3.9, 4.45, LIGHT);
  s.addText("One model, two verdicts", { x: 9.05, y: 1.78, w: 3.3, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: AMBER });
  bullets(s, [
    "Price space: R² 0.99938, MAPE 1.560%, “98.44% accurate”.",
    "Return space: R² +0.00013. Thirteen thousandths of one percent.",
    "Naive persistence ties it to three decimals, because prices barely move day to day.",
    "A Random Forest on raw price levels scores R² 0.993 and is significantly worse than naive (DM p = 0.000), because trees cannot extrapolate.",
  ], { x: 9.05, y: 2.3, w: 3.3, h: 3.6, fontSize: 12.5 });
  takeaway(s, "Price-level accuracy measures the price, not the forecast. Any paper quoting 98% without a naive baseline has reported nothing.", AMBER);
  s.addNotes("This is the first contribution. It is not a criticism of one paper, it is a measurement artefact that a lot of the literature shares. Our own model is subject to it too, which is why we report return space first.");
}

/* ======================================================= 9. RQ1 table */
{
  const s = pres.addSlide();
  titleBar(s, "RQ1 — finding 2", "Return-space skill, against proper baselines");
  dataTable(s, ["Model", "RMSE (bp)", "R² vs zero", "IC", "Direction", "DM p"], [
    ["Naive (tomorrow = today)", "245.5", "0.00000", "—", "47.16%", "—"],
    ["Historical drift", "245.5", "+0.00043", "—", "52.84%", "0.635"],
    ["Ridge regression", "246.9", "−0.01076", "+0.0019", "51.70%", "0.392"],
    ["Random Forest on price levels", "250.4", "−0.03972", "+0.0063", "50.85%", "0.000"],
    ["Random Forest (proposed)", "245.5", "+0.00013", "+0.0090", "51.77%", "0.968"],
    ["Always the majority direction", "—", "—", "—", "52.84%", "—"],
  ], { y: 1.65, colW: [3.6, 1.5, 1.7, 1.4, 1.5, 1.5], rowH: 0.44, w: 11.2 });
  card(s, M, 4.95, 5.6, 1.15, LIGHT);
  s.addText("What the columns mean", { x: M + 0.25, y: 5.05, w: 5.1, h: 0.3, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 13.5, bold: true, color: NAVY });
  s.addText("R² vs zero: 0 = no better than forecasting no move.  IC: daily cross-sectional correlation with the outcome.  DM p: Diebold–Mariano test of whether the error really is smaller.", {
    x: M + 0.25, y: 5.35, w: 5.1, h: 0.7, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 11.5, color: TEXT, lineSpacing: 15,
  });
  card(s, M + 5.85, 4.95, 5.35, 1.15, WHITE);
  s.addText("Read honestly", { x: M + 6.1, y: 5.05, w: 4.9, h: 0.3, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 13.5, bold: true, color: AMBER });
  s.addText("IC +0.0090 has t = 1.39, so it is not distinguishable from zero. Direction 51.77% is below the 52.84% you get by always guessing the majority. On an average day a stock moves 245.5 bp; our forecasts vary by 9.7 bp.", {
    x: M + 6.1, y: 5.35, w: 4.9, h: 0.7, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 11.5, color: TEXT, lineSpacing: 15,
  });
  takeaway(s, "Near-zero skill is the honest answer, and reporting it is what makes everything after this slide credible.");
  s.addNotes("Do not oversell. The project's value is the audit, not the forecast. If a reviewer pushes, point out that 405,545 out-of-sample forecasts with a proper DM test is a stronger negative result than most positive results in this literature.");
}

/* ======================================================= 10. Regimes */
{
  const s = pres.addSlide();
  titleBar(s, "RQ1 — finding 3", "The little skill there is, is not spread evenly");
  dataTable(s, ["Regime", "Stock-days", "R² vs zero", "IC", "Direction", "DM p", "Long-short"], [
    ["Pre-COVID bull", "134,982", "+0.00069", "+0.0148", "53.03%", "0.865", "+6.9 bp"],
    ["COVID crash", "10,901", "−0.01171", "−0.0732", "34.68%", "0.127", "−119.0 bp"],
    ["Recovery", "212,824", "+0.00665", "+0.0076", "51.65%", "0.043", "+16.1 bp"],
    ["2022 bear", "46,838", "−0.00113", "+0.0180", "52.68%", "0.913", "+5.6 bp"],
  ], { y: 1.65, colW: [2.3, 1.6, 1.7, 1.4, 1.4, 1.2, 1.6], rowH: 0.42, w: 11.2 });
  card(s, M, 3.85, 5.6, 2.25, LIGHT);
  s.addText("One period of real skill", { x: M + 0.3, y: 4.0, w: 5.0, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: GREEN });
  bullets(s, [
    "The Recovery is the only regime where the Diebold–Mariano test is significant, p = 0.043.",
    "R² +0.00665 there, fifty times the overall figure, and +16.1 bp a day long-short.",
  ], { x: M + 0.3, y: 4.45, w: 5.0, h: 1.5, fontSize: 13 });
  card(s, M + 5.85, 3.85, 5.35, 2.25, WHITE);
  s.addText("And one period where it inverted", { x: M + 6.15, y: 4.0, w: 4.8, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: AMBER });
  bullets(s, [
    "In the COVID crash the IC went negative and direction accuracy fell to 34.68% — worse than a coin.",
    "The long-short lost 119 bp a day. The relationship it had learned reversed sign exactly when it mattered most.",
  ], { x: M + 6.15, y: 4.45, w: 4.8, h: 1.5, fontSize: 13 });
  takeaway(s, "An average over a decade hides both of these. Regime-level reporting is not optional in finance.");
  s.addNotes("The four regimes were fixed from public market history before any explanation was computed - the S&P peaked 19 Feb 2020 and bottomed 23 Mar 2020 - so they cannot be accused of being chosen after seeing the results.");
}

/* ======================================================= 11. Economic view */
{
  const s = pres.addSlide();
  titleBar(s, "RQ1 — finding 4", "Would the ranking make money? No.");
  s.addImage({ path: FIG("decile_portfolio.png"), x: M, y: 1.65, w: 6.6, h: 3.98 });
  card(s, 7.9, 1.65, 4.75, 3.98, LIGHT);
  s.addText("The trading test", { x: 8.2, y: 1.82, w: 4.1, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: NAVY });
  bullets(s, [
    "Sort each day's stocks into 10 buckets by predicted return, hold the extremes.",
    "The ranking does slope the right way: +1.3 bp in the bottom bucket to +9.5 bp in the top, Spearman 0.745.",
    "Long-short spread +8.17 bp/day, annual Sharpe 0.83.",
    "But t = 1.54, so not significant — and after a realistic 10 bp round-trip cost it is −1.83 bp/day.",
  ], { x: 8.2, y: 2.35, w: 4.1, h: 3.1, fontSize: 13 });
  takeaway(s, "Monotone, plausible, and still not tradeable once you pay for the trades. This is where most strategy papers stop looking.", AMBER);
  s.addNotes("If asked whether they should trade it: no, and this slide is the reason. The point of including costs is that a Sharpe of 0.83 sounds investable until you subtract them.");
}

/* ======================================================= 12. RQ2 global SHAP */
{
  const s = pres.addSlide();
  titleBar(s, "RQ2", "What the model actually uses");
  s.addImage({ path: FIG("shap_global.png"), x: M, y: 1.6, w: 6.0, h: 4.18 });
  card(s, 7.3, 1.6, 5.35, 2.0, LIGHT);
  s.addText("Top features, mean |SHAP| in bp", { x: 7.6, y: 1.75, w: 4.8, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 15, bold: true, color: NAVY });
  s.addText("mkt_vol_20d  5.37    market volatility, 20 days\nmkt_ret_5d   3.33    the market's last week\nmkt_ret_1d   3.28    the market yesterday\ngap_open     0.77    this stock's gap at the open\nret_1d       0.57    this stock yesterday", {
    x: 7.6, y: 2.18, w: 4.8, h: 1.3, isTextBox: true, margin: 0, fontFace: MONO, fontSize: 11.5, color: TEXT, lineSpacing: 16,
  });
  card(s, 7.3, 3.75, 5.35, 2.03, NAVY);
  s.addText("Attribution by family", { x: 7.6, y: 3.9, w: 4.8, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 15, bold: true, color: WHITE });
  s.addText("Market & sector  72.2%\nVolatility 7.6%   Past returns 7.0%   Candle 5.9%\nTrend 3.8%   Oscillators 2.0%   Volume 1.5%", {
    x: 7.6, y: 4.32, w: 4.8, h: 1.3, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13.5, color: ICE, lineSpacing: 20,
  });
  takeaway(s, "Nearly three quarters of the model is about the market, not the stock — which is true, and says nothing about which stock to buy.");
  s.addNotes("This links straight back to RQ1. A model that has learned the market factor will have a tiny IC, because IC measures cross-sectional ranking and the market factor is identical for every stock on a given day.");
}

/* ======================================================= 13. RQ3 faithfulness */
{
  const s = pres.addSlide();
  titleBar(s, "RQ3 — faithfulness", "Delete what the explanation called important");
  s.addImage({ path: FIG("faithfulness.png"), x: M, y: 1.62, w: 6.75, h: 4.37 });
  card(s, 8.0, 1.62, 4.65, 4.37, LIGHT);
  s.addText("The test", { x: 8.3, y: 1.76, w: 4.1, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: NAVY });
  bullets(s, [
    "Replace the top-|SHAP| features with values from 32 background rows; measure how far the forecast moves.",
    "Compare against deleting features in random order. 2,000 stock-days.",
  ], { x: 8.3, y: 2.18, w: 4.1, h: 1.4, fontSize: 12.5 });
  s.addText("AOPC   8.51 bp  by |SHAP| rank\n       3.67 bp  random order\n       = 2.3x\n\nk = 1  8.70 bp vs 0.65 bp = 13x\n\nfidelity correlation 0.984 → 1.000", {
    x: 8.3, y: 3.75, w: 4.1, h: 2.0, isTextBox: true, margin: 0, fontFace: MONO, fontSize: 11, color: TEXT, lineSpacing: 16,
  });
  takeaway(s, "SHAP passes. The single feature it names moves the forecast 13× more than a random one, and its numbers predict the move almost exactly.", GREEN);
  s.addNotes("Fidelity correlation is the stronger result: the amount of SHAP mass removed predicts the actual change in the forecast with correlation 0.98 at one feature, rising to 1.00 at all 32. That is not a ranking check, it is a quantitative one.");
}

/* ======================================================= 14. RQ3 stability */
{
  const s = pres.addSlide();
  titleBar(s, "RQ3 — stability", "Re-run it, retrain it, does the story hold?");
  s.addImage({ path: FIG("stability_sanity.png"), x: M, y: 1.7, w: 7.4, h: 2.93 });
  card(s, 8.6, 1.7, 4.05, 4.3, LIGHT);
  s.addText("Across 5 random seeds", { x: 8.9, y: 1.85, w: 3.5, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 15, bold: true, color: GREEN });
  s.addText("Kendall τ 0.85    top-5 overlap 0.92\nper-row Spearman 0.86\nprediction correlation 0.990", {
    x: 8.9, y: 2.25, w: 3.5, h: 0.9, isTextBox: true, margin: 0, fontFace: MONO, fontSize: 11, color: TEXT, lineSpacing: 15,
  });
  s.addText("Across yearly retrains", { x: 8.9, y: 3.25, w: 3.5, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 15, bold: true, color: AMBER });
  s.addText("2019 vs 2020   τ 0.75\n2020 vs 2021   τ 0.44\n2021 vs 2022   τ 0.77", {
    x: 8.9, y: 3.65, w: 3.5, h: 0.9, isTextBox: true, margin: 0, fontFace: MONO, fontSize: 11, color: TEXT, lineSpacing: 15,
  });
  s.addText("TreeSHAP itself is deterministic: re-running it on the same model gives bit-identical numbers, so all of this instability belongs to the model, not the explainer.", {
    x: 8.9, y: 4.65, w: 3.5, h: 1.2, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, color: TEXT, lineSpacing: 16,
  });
  takeaway(s, "Stable across seeds, shakier across retrains — and the weakest link, 2020 vs 2021, is exactly the COVID regime shift.");
  s.addNotes("Song et al. (2026) found top-feature overlap of 0.046 across seeds for attention weights. Ours is 0.92 for TreeSHAP on a forest, which is the comparison to make if asked whether this is good.");
}

/* ======================================================= 15. RQ5 sanity */
{
  const s = pres.addSlide();
  titleBar(s, "RQ5 — the sharpest test", "Explain a model that provably knows nothing");
  s.addText("Train a forest on shuffled labels, then explain it. If the nonsense model's explanation resembles the real one, the explanation was describing the shape of the features, not anything learned.", {
    x: M, y: 1.6, w: W - 2 * M, h: 0.5, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14.5, italic: true, color: GREY,
  });
  dataTable(s, ["Model", "τ vs real", "Total |SHAP| (bp)", "Test IC", "Prediction sd (bp)"], [
    ["Real model", "—", "20.85", "+0.018", "9.65"],
    ["Labels fully shuffled", "0.13", "2.59", "−0.023", "0.88"],
    ["Returns shuffled within each day", "0.56", "19.54", "+0.011", "9.62"],
  ], { y: 2.2, colW: [3.9, 1.6, 2.2, 1.7, 2.1], rowH: 0.42, w: 11.5 });
  card(s, M, 3.95, 5.6, 2.15, LIGHT);
  s.addText("The reassuring half", { x: M + 0.3, y: 4.1, w: 5.0, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 15.5, bold: true, color: GREEN });
  bullets(s, [
    "The fully shuffled model is correctly exposed: τ 0.13, and its attribution collapses from 20.85 bp to 2.59 bp.",
    "SHAP is not inventing structure out of noise.",
  ], { x: M + 0.3, y: 4.5, w: 5.0, h: 1.5, fontSize: 13 });
  card(s, M + 5.85, 3.95, 5.35, 2.15, NAVY);
  s.addText("The uncomfortable half", { x: M + 6.15, y: 4.1, w: 4.8, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 15.5, bold: true, color: AMBER });
  s.addText("Shuffling returns within each day keeps the market-wide move and destroys all stock-specific information. That model still produces 19.54 bp of attribution and matches the real explanation at τ 0.56 with 80% top-5 overlap.", {
    x: M + 6.15, y: 4.5, w: 4.8, h: 1.5, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, color: ICE, lineSpacing: 18,
  });
  takeaway(s, "That is not a failure of SHAP — it is proof of what the model learned: the market factor, which the shuffle leaves intact.", AMBER);
  s.addNotes("This is the slide to be proudest of. Two nulls, not one, and the second null is the informative one. It independently confirms the 72.2% market-and-sector finding from RQ2 by a completely different route.");
}

/* ======================================================= 16. RQ4 drift */
{
  const s = pres.addSlide();
  titleBar(s, "RQ4", "The explanation drifts — and we tested it properly");
  s.addImage({ path: FIG("regime_family_shares.png"), x: M, y: 1.65, w: 7.3, h: 2.77 });
  card(s, 8.6, 1.65, 4.05, 4.4, LIGHT);
  s.addText("Permutation test", { x: 8.9, y: 1.8, w: 3.5, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: NAVY });
  bullets(s, [
    "Statistic: mean pairwise total variation distance between family-share vectors.",
    "Null: shuffle group labels 1,000 times by whole day (regimes) or whole ticker (sectors), so dependence inside a day is kept.",
  ], { x: 8.9, y: 2.22, w: 3.5, h: 1.6, fontSize: 12.5 });
  s.addText("regimes  TVD 0.054  p = 0.003\nsectors  TVD 0.036  p = 0.001\n(null TVD 0.017)", {
    x: 8.9, y: 3.92, w: 3.5, h: 0.9, isTextBox: true, margin: 0, fontFace: MONO, fontSize: 10, color: TEXT, lineSpacing: 15,
  });
  s.addText("mkt_vol_20d stays the top feature in all four regimes, so the headline is stable. What sits behind it is not.", {
    x: 8.9, y: 4.85, w: 3.5, h: 1.1, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, color: TEXT, lineSpacing: 17,
  });
  takeaway(s, "Pagliaro (2026) observed this drift descriptively. We put a significance test on it: p = 0.003 for regimes, p = 0.001 for sectors.", GREEN);
  s.addNotes("Why shuffle by whole day rather than by row: returns on the same day are strongly correlated across stocks, so a row-level shuffle would produce a far too narrow null and almost any difference would look significant.");
}

/* ======================================================= 17. RQ6 SHAP vs LIME */
{
  const s = pres.addSlide();
  titleBar(s, "RQ6", "Do SHAP and LIME tell the same story?");
  s.addImage({ path: FIG("lime_vs_shap_local.png"), x: M, y: 1.6, w: 7.5, h: 2.76 });
  card(s, 8.8, 1.6, 3.85, 4.45, LIGHT);
  s.addText("804 stock-days, 5 seeds each", { x: 9.1, y: 1.75, w: 3.3, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 14.5, bold: true, color: NAVY });
  s.addText("GLOBAL RANKING\nKendall τ 0.58   top-5 overlap 0.80\n\nTHE SAME SINGLE FORECAST\nmedian Spearman 0.44\ntop-5 overlap 0.65\nsame top feature 59.1%\nsign agreement 80.7%\n\nLIME AGAINST ITSELF\nSpearman 0.45 between its own runs\nsame top feature in all 5 runs 95.8%\n\nLIME'S OWN SURROGATE R²\nmedian 0.167   below 0.3 on 67.4%", {
    x: 9.1, y: 2.2, w: 3.3, h: 3.7, isTextBox: true, margin: 0, fontFace: MONO, fontSize: 10, color: TEXT, lineSpacing: 14,
  });
  takeaway(s, "Averaged over hundreds of rows they look alike. On 41% of individual forecasts they name a different most-important feature.", AMBER);
  s.addNotes("The surrogate R2 is the strongest argument for preferring SHAP here: two thirds of LIME's explanations are built on a local linear model that explains less than 30% of the behaviour it is approximating. TreeSHAP has no such approximation - it is exact and additive by construction.");
}

/* ======================================================= 18. The LIME bug */
{
  const s = pres.addSlide();
  titleBar(s, "RQ6 — a defect found along the way", "LIME was not reproducible, and nobody would have noticed");
  card(s, M, 1.7, 5.85, 2.45, LIGHT);
  s.addText("What was wrong", { x: M + 0.3, y: 1.85, w: 5.2, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: AMBER });
  bullets(s, [
    "LimeTabularExplainer binds its random state into the discretiser and the surrogate solver at construction.",
    "Setting .random_state afterwards — the obvious thing to do — controls only part of the sampling.",
  ], { x: M + 0.3, y: 2.28, w: 5.2, h: 1.7, fontSize: 13 });
  card(s, M + 6.1, 1.7, 6.2, 2.45, WHITE);
  s.addText("Measured, three ways", { x: M + 6.4, y: 1.85, w: 5.6, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: NAVY });
  s.addText("reused explainer, same seed   ρ 0.46 – 0.53\nfresh explainer, same seed     ρ 1.000  identical\nfresh explainer, different seeds ρ 0.16 – 0.31", {
    x: M + 6.4, y: 2.35, w: 5.6, h: 1.1, isTextBox: true, margin: 0, fontFace: MONO, fontSize: 11.5, color: TEXT, lineSpacing: 19,
  });
  s.addText("Fix: construct one explainer per seed. Costs 18 ms.", {
    x: M + 6.4, y: 3.5, w: 5.6, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, italic: true, color: GREY,
  });
  card(s, M, 4.3, W - 2 * M, 1.75, NAVY);
  s.addText("Why it matters", { x: M + 0.35, y: 4.48, w: 5.0, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: AMBER });
  s.addText("Before the fix, the global SHAP–LIME agreement read τ 0.73. After it, τ 0.58. The higher, friendlier number was an artefact of LIME quietly not being reproducible — averaging over noise that was never meant to be there. A reliability study that does not check its own tooling can publish exactly this kind of number without ever seeing it.", {
    x: M + 0.35, y: 4.88, w: W - 2 * M - 0.7, h: 1.05, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13.5, color: ICE, lineSpacing: 19,
  });
  takeaway(s, "The audit found a bug in the audit tool. That is the clearest possible argument for running one.", AMBER);
  s.addNotes("The docstring in src/lime_explain.py cites the exact line numbers in lime_tabular.py. If asked whether this is a known issue: the behaviour is documented nowhere obvious, and the usage pattern that triggers it is the natural one.");
}

/* ======================================================= 19. Faithfulness head-to-head */
{
  const s = pres.addSlide();
  titleBar(s, "RQ6 — verdict", "Both are faithful. One is exact.");
  s.addImage({ path: FIG("lime_reliability.png"), x: M, y: 1.65, w: 7.6, h: 2.95 });
  card(s, 8.85, 1.65, 3.8, 4.4, LIGHT);
  s.addText("Deletion test, three orderings", { x: 9.15, y: 1.8, w: 3.2, h: 0.55, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 14.5, bold: true, color: NAVY });
  s.addText("AOPC    SHAP   8.70 bp\n        LIME   8.13 bp\n        Random 3.71 bp\nk = 1   SHAP   8.89 bp\n        LIME   6.53 bp", {
    x: 9.15, y: 2.35, w: 3.3, h: 1.3, isTextBox: true, margin: 0, fontFace: MONO, fontSize: 10.5, color: TEXT, lineSpacing: 14,
  });
  bullets(s, [
    "Both beat random by more than 2×, so both genuinely describe the model.",
    "SHAP is better at k = 1: its single top feature is more often the right one.",
    "TreeSHAP is exact, additive and deterministic. LIME is approximate and random.",
    "Use TreeSHAP for trees; keep LIME as a cross-check.",
  ], { x: 9.15, y: 3.8, w: 3.3, h: 2.2, fontSize: 11 });
  takeaway(s, "Where an exact explainer exists, approximating it is a choice — and here it costs reproducibility and two thirds of local fidelity.", GREEN);
  s.addNotes("Be fair to LIME: it is model-agnostic, which is exactly why it exists, and on this model it still passes faithfulness. The recommendation is specific to tree models, where TreeSHAP is available and exact.");
}

/* ======================================================= 20. The demo */
{
  const s = pres.addSlide();
  titleBar(s, "Demonstration", "What you type, and what you get back");
  card(s, M, 1.65, 3.5, 4.4, NAVY);
  s.addText("INPUT", { x: M + 0.3, y: 1.82, w: 2.9, h: 0.3, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 11.5, bold: true, color: AMBER, charSpacing: 2 });
  s.addText("Two choices", { x: M + 0.3, y: 2.12, w: 2.9, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 18, bold: true, color: WHITE });
  s.addText("1.  A stock\n     474 in past mode\n     431 in live mode\n\n2.  A date\n     any trading day from\n     2019-01-02 to 2022-05-24\n\n     or “next session”, whose\n     outcome does not exist yet", {
    x: M + 0.3, y: 2.65, w: 2.9, h: 3.2, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, color: ICE, lineSpacing: 18,
  });
  const outs = [
    ["1", "The forecast", "Predicted return in bp, predicted close in dollars, probability tomorrow is up. In past mode, the actual outcome beside it."],
    ["2", "A price chart", "Last 60 closes, a dashed line to the forecast, and a band of one standard deviation of this stock's recent daily moves."],
    ["3", "A SHAP waterfall", "Average forecast → each top feature → this forecast. Lands on the number exactly."],
    ["4", "SHAP vs LIME", "Both explanations of the same forecast, side by side, plus all 32 features in a table."],
    ["5", "The four audits", "Do they agree, is each stable, is it faithful — computed live, on this forecast."],
  ];
  outs.forEach(([n, head, text], i) => {
    const col = i < 3 ? 0 : 1, row = i < 3 ? i : i - 3;
    const x = 4.5 + col * 4.35, y = 1.65 + row * 1.5;
    card(s, x, y, 4.1, 1.35, i % 2 ? WHITE : LIGHT);
    numberBadge(s, x + 0.2, y + 0.16, n, AMBER);
    s.addText(head, { x: x + 0.75, y: y + 0.14, w: 3.2, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 14, bold: true, color: NAVY });
    s.addText(text, { x: x + 0.25, y: y + 0.55, w: 3.6, h: 0.75, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 11, color: TEXT, lineSpacing: 14 });
  });
  card(s, 8.85, 4.65, 4.1, 1.35, LIGHT);
  s.addText("Live, as of the 29 Oct 2026 close", { x: 9.1, y: 4.78, w: 3.6, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 13, bold: true, color: GREEN });
  s.addText("431 stocks, retrained on 1,473,486 stock-days. 43 of the original 474 tickers no longer trade — the page lists them, so survivorship bias is visible rather than hidden.", {
    x: 9.1, y: 5.12, w: 3.6, h: 0.85, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 10.5, color: TEXT, lineSpacing: 13,
  });
  takeaway(s, "Nothing is read from a cache: every request runs TreeSHAP once and LIME five times, live, on the saved model.");
  s.addNotes("Demo order: live mode first - this is tomorrow, nobody knows the answer. Point at the volatility band: the model predicts a 4 bp move on a stock that normally moves 87, which is the honest response to an unpredictable target. Then the waterfall, then the disagreement card, then switch to a past day to show how any of it was graded.");
}

/* ======================================================= 21. Contributions */
{
  const s = pres.addSlide();
  titleBar(s, "Contributions", "What this project adds");
  const items = [
    ["1", "The price-space artefact, measured", "The same forecasts score R² 0.99938 on price and +0.00013 on return, with naive persistence tied to three decimals."],
    ["2", "A five-part explanation audit", "Faithfulness, stability, agreement, sanity nulls and drift — run together on one model, with significance tests."],
    ["3", "Two sanity nulls, not one", "The within-day shuffle independently confirms what the model learned, by a different route from SHAP."],
    ["4", "Drift tested, not just observed", "Permutation tests over whole days and tickers: p = 0.003 across regimes, p = 0.001 across sectors."],
    ["5", "A reproducibility defect in LIME", "Found, measured, fixed, and shown to have inflated the headline agreement from 0.58 to 0.73."],
    ["6", "A working forecast-and-audit demo", "Next-session forecasts on 431 live stocks, explained and audited in real time by the study's own code."],
  ];
  items.forEach(([n, head, text], i) => {
    const col = i % 2, row = (i - col) / 2;
    const x = M + col * 6.15, y = 1.65 + row * 1.52;
    card(s, x, y, 5.75, 1.38, col === 0 ? LIGHT : WHITE);
    numberBadge(s, x + 0.22, y + 0.18, n, i < 2 ? NAVY : AMBER);
    s.addText(head, { x: x + 0.8, y: y + 0.14, w: 4.7, h: 0.38, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 14.5, bold: true, color: NAVY });
    s.addText(text, { x: x + 0.3, y: y + 0.58, w: 5.2, h: 0.75, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 11.5, color: TEXT, lineSpacing: 15 });
  });
  takeaway(s, "The negative forecast result is reported in full. That is what makes the five positive methodological results worth anything.");
  s.addNotes("If time is short, slides 8, 15 and 18 carry the project: the accuracy artefact, the within-day sanity null, and the LIME defect.");
}

/* ======================================================= 22. Limitations */
{
  const s = pres.addSlide();
  titleBar(s, "Limitations", "Stated plainly, before anyone asks");
  const items = [
    ["Universe", "474 large-cap US stocks that survived to 2022. Survivorship bias flatters any backtest; the live demo makes the 43 lost tickers visible but the study panel cannot fix it."],
    ["Horizon", "One day ahead only. Nothing here says anything about weekly or monthly horizons, where the signal-to-noise ratio is different."],
    ["Features", "Price, volume and market context only. No fundamentals, no news, no sentiment, no order book."],
    ["Model", "One model family. The audit method generalises to any tree ensemble, but the specific findings are about this Random Forest."],
    ["Explainers", "TreeSHAP and LIME. Not counterfactual, anchor or concept-based methods."],
    ["Costs", "A flat 10 bp round-trip assumption. Real costs vary by stock, size and venue."],
  ];
  items.forEach(([head, text], i) => {
    const col = i % 2, row = (i - col) / 2;
    const x = M + col * 6.15, y = 1.7 + row * 1.5;
    card(s, x, y, 5.75, 1.35, col === 0 ? LIGHT : WHITE);
    s.addText(head, { x: x + 0.3, y: y + 0.14, w: 5.1, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 15, bold: true, color: AMBER });
    s.addText(text, { x: x + 0.3, y: y + 0.52, w: 5.2, h: 0.78, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 11.5, color: TEXT, lineSpacing: 15 });
  });
  takeaway(s, "None of these weaken the audit method. They bound what the specific numbers are about.");
  s.addNotes("Have this slide ready rather than being walked into it. The strongest version of the answer is that the contribution is the method, and the method survives every limitation on this list.");
}

/* ======================================================= 23. Conclusion */
{
  const s = pres.addSlide();
  s.background = { color: INK };
  s.addShape(pres.ShapeType.ellipse, { x: 10.8, y: -1.2, w: 4.6, h: 4.6, fill: { color: NAVY }, line: { color: NAVY } });
  s.addText("CONCLUSION", {
    x: M, y: 0.65, w: 9, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, bold: true, color: AMBER, charSpacing: 2,
  });
  s.addText("The forecast is near-worthless.\nThe audit of its explanation is the result.", {
    x: M, y: 1.05, w: 10.5, h: 1.3, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 30, bold: true, color: WHITE, lineSpacing: 38,
  });
  const lines = [
    ["RQ1", "R² +0.00013 in return space, IC +0.0090 (t = 1.39), direction 51.77% against a 52.84% majority rule. Skill exists in one regime (p = 0.043) and inverts in another."],
    ["RQ2", "72.2% of attribution goes to market and sector features. The model learned the market factor, not stock selection."],
    ["RQ3", "SHAP is faithful (2.3× AOPC, fidelity 0.98+) and stable across seeds (τ 0.85), less so across retrains (τ 0.44–0.77)."],
    ["RQ4", "Explanations drift significantly across regimes (p = 0.003) and sectors (p = 0.001)."],
    ["RQ5", "A fully shuffled model is exposed (τ 0.13). A within-day shuffled one is not (τ 0.56) — which pins down exactly what was learned."],
    ["RQ6", "SHAP and LIME agree globally (τ 0.58) and disagree on 41% of individual forecasts. LIME's own surrogate R² is below 0.3 two thirds of the time."],
  ];
  lines.forEach(([tag, text], i) => {
    const y = 2.6 + i * 0.63;
    s.addText(tag, { x: M, y, w: 0.75, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 14, bold: true, color: AMBER });
    s.addText(text, { x: M + 0.8, y, w: 10.9, h: 0.6, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, color: ICE, lineSpacing: 16 });
  });
  s.addText("And the audit found a reproducibility bug in the audit tool itself — the clearest argument there is for running one.", {
    x: M, y: 6.55, w: 11.5, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, italic: true, color: WHITE,
  });
  s.addNotes("Closing line to say out loud: every explainability paper reports what SHAP said. This one reports whether SHAP could be believed, and on one of five tests the answer was not a clean yes.");
}

pres.writeFile({ fileName: path.join(__dirname, "..", "PROJECT_SLIDES.pptx") })
  .then((f) => console.log("wrote", f, "-", pres.slides.length, "slides"));

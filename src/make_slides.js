// Literature review + problem statement deck (10 slides).
const PptxGenJS = require("pptxgenjs");

const NAVY = "1E2761";       // dominant
const INK = "16203F";        // darker navy for dark slides
const ICE = "CADCFC";        // supporting
const AMBER = "E8703A";      // accent
const GREY = "5A6472";
const LIGHT = "F4F7FC";
const WHITE = "FFFFFF";

const HEAD = "Cambria";
const BODY = "Calibri";

const pres = new PptxGenJS();
pres.layout = "LAYOUT_WIDE";            // 13.33 x 7.5 in
pres.author = "StockRF-XAI";
pres.title = "Trustworthy Explanations for Random-Forest Stock Price Forecasting";

const W = 13.33, H = 7.5, M = 0.7;

function titleBar(slide, kicker, title) {
  slide.addText(kicker.toUpperCase(), {
    x: M, y: 0.42, w: 9, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12, bold: true, color: AMBER, charSpacing: 2,
  });
  slide.addText(title, {
    x: M, y: 0.72, w: W - 2 * M, h: 0.8, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 32, bold: true, color: NAVY,
  });
}

function card(slide, x, y, w, h, fill) {
  slide.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.08, fill: { color: fill || LIGHT },
    line: { color: fill === NAVY ? NAVY : "DCE4F2", width: 1 },
    shadow: { type: "outer", color: "9AA7BD", blur: 8, offset: 1, angle: 90, opacity: 0.25 },
  });
}

function numberBadge(slide, x, y, n, colour) {
  slide.addShape(pres.ShapeType.ellipse, {
    x, y, w: 0.44, h: 0.44, fill: { color: colour || NAVY }, line: { color: colour || NAVY },
  });
  slide.addText(String(n), {
    x, y, w: 0.44, h: 0.44, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 15, bold: true, color: WHITE, align: "center", valign: "middle",
  });
}

/* ---------------------------------------------------------------- 1. Title */
{
  const s = pres.addSlide();
  s.background = { color: INK };
  s.addShape(pres.ShapeType.ellipse, { x: 10.3, y: -1.5, w: 5.2, h: 5.2, fill: { color: NAVY }, line: { color: NAVY } });
  s.addShape(pres.ShapeType.ellipse, { x: 11.6, y: 4.6, w: 3.0, h: 3.0, fill: { color: "232F63" }, line: { color: "232F63" } });
  s.addText("LITERATURE REVIEW & PROBLEM STATEMENT", {
    x: M, y: 1.55, w: 9.4, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, bold: true, color: AMBER, charSpacing: 2,
  });
  s.addText("Trustworthy Explanations for\nRandom-Forest Stock Price Forecasting", {
    x: M, y: 2.0, w: 9.4, h: 1.9, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 40, bold: true, color: WHITE, lineSpacing: 46,
  });
  s.addText("Can we trust what SHAP and LIME tell us about a stock model?", {
    x: M, y: 3.95, w: 9.4, h: 0.5, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 17, italic: true, color: ICE,
  });
  const stats = [["474", "S&P 500 stocks"], ["405,545", "test forecasts"], ["5", "papers reviewed"]];
  stats.forEach(([big, small], i) => {
    const x = M + i * 3.1;
    s.addText(big, { x, y: 4.95, w: 2.8, h: 0.6, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 30, bold: true, color: AMBER });
    s.addText(small, { x, y: 5.55, w: 2.8, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, color: ICE });
  });
  s.addNotes("Project: build a Random Forest that predicts next-day closing prices for 474 S&P 500 stocks, then test whether its SHAP and LIME explanations can be trusted.");
}

/* ------------------------------------------------- 2. The two problems */
{
  const s = pres.addSlide();
  titleBar(s, "Motivation", "Two problems in the current literature");
  const items = [
    ["1", "Accuracy is reported without a benchmark",
      ["Papers report R² of 0.88–0.99 for price prediction.",
       "But “tomorrow's price = today's price” already scores R² ≈ 0.999.",
       "Without that comparison, we cannot tell if a model has any real skill."]],
    ["2", "Explanations are presented, never tested",
      ["SHAP or LIME rankings are reported as market insight.",
       "Nobody checks if they are faithful, stable, or agree with each other.",
       "An explanation can describe noise, or one random seed."]],
  ];
  items.forEach(([n, head, lines], i) => {
    const x = M + i * 6.15;
    card(s, x, 1.75, 5.75, 3.55);
    numberBadge(s, x + 0.35, 2.05, n, i === 0 ? NAVY : AMBER);
    s.addText(head, { x: x + 0.95, y: 2.05, w: 4.6, h: 0.75, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 18, bold: true, color: NAVY });
    s.addText(lines.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < lines.length - 1 } })), {
      x: x + 0.4, y: 2.95, w: 5.0, h: 2.2, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 14.5, color: "26324A", paraSpaceAfter: 8, lineSpacing: 20,
    });
  });
  s.addText("Misleading explanations in finance lead to real money decisions made on false reasoning.", {
    x: M, y: 5.6, w: W - 2 * M, h: 0.5, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 15, italic: true, color: GREY,
  });
  s.addNotes("Problem 1 is about accuracy claims; problem 2 is about explanation claims. My project addresses both.");
}

/* ------------------------------------------- 3. Why 98% accuracy misleads */
{
  const s = pres.addSlide();
  titleBar(s, "The accuracy trap", "Why “98% accurate” means nothing on its own");
  s.addChart(pres.ChartType.bar, [{
    name: "Average error (MAPE %)",
    labels: ["Naive: tomorrow = today", "Ridge regression", "RF on price levels", "Random Forest (ours)"],
    values: [1.561, 1.567, 1.583, 1.560],
  }], {
    x: M, y: 1.75, w: 7.3, h: 3.9, barDir: "bar", chartColors: [NAVY, "8FA6CC", "8FA6CC", AMBER],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.000",
    dataLabelFontFace: BODY, dataLabelFontSize: 11, dataLabelColor: "26324A",
    catAxisLabelFontFace: BODY, catAxisLabelFontSize: 12, catAxisLabelColor: "26324A",
    valAxisLabelFontFace: BODY, valAxisLabelFontSize: 10, valAxisLabelColor: GREY,
    valAxisMaxVal: 1.75, valAxisMinVal: 1.5, showLegend: false,
    valGridLine: { color: "E3E9F4", size: 1 }, catGridLine: { style: "none" }, barGapWidthPct: 60,
  });
  card(s, 8.35, 1.75, 4.3, 3.9, LIGHT);
  s.addText("What this shows", { x: 8.7, y: 2.0, w: 3.7, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 17, bold: true, color: NAVY });
  s.addText([
    { text: "Our Random Forest: 1.560% error, i.e. 98.44% “accuracy”.", options: { bullet: true, breakLine: true } },
    { text: "The naive forecast: 1.561%. Identical (p = 0.30).", options: { bullet: true, breakLine: true } },
    { text: "A Random Forest on raw prices has R² 0.993 yet is significantly worse than naive.", options: { bullet: true, breakLine: false } },
  ], { x: 8.65, y: 2.5, w: 3.8, h: 2.9, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, color: "26324A", paraSpaceAfter: 10, lineSpacing: 19 });
  s.addText("Lower is better. All four models land within 0.03% of each other.", {
    x: M, y: 5.75, w: 8, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, italic: true, color: GREY,
  });
  s.addNotes("Direction accuracy is the fairer measure: ours is 51.8%, below the 52.8% you get by always predicting the majority direction.");
}

/* ------------------------------------------------ 4. Papers 1-3 */
{
  const s = pres.addSlide();
  titleBar(s, "Literature review (1 of 2)", "What the recent papers did");
  const rows = [
    ["1", "Indra et al. (2025), J. Risk & Financial Management",
      "6 Indonesian LQ45 stocks, 2016–2025",
      "RF, XGBoost, Ridge + SHAP; backtest with costs",
      "Accuracy 49–54%; all strategies lose to buy-and-hold; SHAP effects negligible",
      "6 stocks; SHAP never validated"],
    ["2", "Lee & Cai (2025), Machine Learning with Applications",
      "22 NASDAQ stocks, 11 sectors, 2019–2024",
      "8 models; compares SHAP vs permutation vs Gini importance",
      "SHAP is the least stable ranking method",
      "Tests agreement, not correctness; no LIME"],
    ["3", "Manikrao et al. (2025), J. Comp. & Cognitive Eng.",
      "Apple (AAPL) only, 2020–2024",
      "LSTM + attention + sentiment; SHAP and LIME",
      "R² 0.88 with interpretable outputs",
      "1 stock; SHAP and LIME never compared"],
  ];
  rows.forEach(([n, who, data, method, finding, gap], i) => {
    const y = 1.7 + i * 1.32;
    card(s, M, y, W - 2 * M, 1.18, i % 2 === 0 ? LIGHT : WHITE);
    numberBadge(s, M + 0.25, y + 0.36, n, NAVY);
    s.addText(who, { x: M + 0.85, y: y + 0.12, w: 4.6, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 13.5, bold: true, color: NAVY });
    s.addText(data, { x: M + 0.85, y: y + 0.45, w: 4.6, h: 0.3, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, color: GREY });
    s.addText(method, { x: M + 0.85, y: y + 0.72, w: 4.6, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, color: "26324A" });
    s.addText(finding, { x: M + 5.6, y: y + 0.18, w: 3.5, h: 0.85, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, color: "26324A" });
    s.addText("GAP", { x: M + 9.3, y: y + 0.14, w: 0.8, h: 0.25, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 10, bold: true, color: AMBER, charSpacing: 1 });
    s.addText(gap, { x: M + 9.3, y: y + 0.38, w: 2.5, h: 0.7, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, color: "26324A" });
  });
  s.addNotes("Papers 1 and 3 report SHAP/LIME outputs as findings without validating them. Paper 2 is the closest on comparing explainers.");
}

/* ------------------------------------------------ 5. Papers 4-5 */
{
  const s = pres.addSlide();
  titleBar(s, "Literature review (2 of 2)", "The two papers that started testing explanations");
  const rows = [
    ["4", "Pagliaro (2026), Electronics",
      "51 NASDAQ-100 stocks, 2015–2026, plus VIX, gold, Bitcoin",
      "LightGBM + Hidden Markov regimes; walk-forward; SHAP",
      "Model's reasoning changes by market phase: 200-day average in bear markets, yield curve and beta in bull markets",
      "Descriptive only, one stock (AMD), no significance test"],
    ["5", "Song et al. (2026), Electronics",
      "20 stocks (CSI 300 + S&P 500), 2016–2023",
      "1,600 runs: 16 setups × 20 stocks × 5 random seeds",
      "Top features from different random seeds shared almost nothing (overlap 0.046) — the explanations were noise",
      "Attention weights in neural nets, not SHAP or LIME on trees"],
  ];
  rows.forEach(([n, who, data, method, finding, gap], i) => {
    const y = 1.7 + i * 2.0;
    card(s, M, y, W - 2 * M, 1.8, i % 2 === 0 ? LIGHT : WHITE);
    numberBadge(s, M + 0.25, y + 0.62, n, AMBER);
    s.addText(who, { x: M + 0.85, y: y + 0.18, w: 4.6, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 15, bold: true, color: NAVY });
    s.addText(data, { x: M + 0.85, y: y + 0.58, w: 4.6, h: 0.5, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, color: GREY });
    s.addText(method, { x: M + 0.85, y: y + 1.1, w: 4.6, h: 0.55, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, color: "26324A" });
    s.addText(finding, { x: M + 5.6, y: y + 0.25, w: 3.6, h: 1.3, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, color: "26324A", lineSpacing: 17 });
    s.addText("GAP", { x: M + 9.4, y: y + 0.25, w: 0.8, h: 0.25, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 10, bold: true, color: AMBER, charSpacing: 1 });
    s.addText(gap, { x: M + 9.4, y: y + 0.5, w: 2.4, h: 1.0, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, color: "26324A", lineSpacing: 17 });
  });
  s.addNotes("These two are the closest work. Paper 4 shows regime differences but does not test them; paper 5 proves explanations can be seed noise, but only for attention.");
}

/* ------------------------------------------------ 6. The gap */
{
  const s = pres.addSlide();
  titleBar(s, "Research gap", "What has been tested, and what has not");
  const headers = ["Check", "Already done by", "Still untested"];
  const rows = [
    ["Comparing explainers", "Paper 2 (SHAP vs permutation)", "SHAP vs LIME on the same forecasts"],
    ["Stability of explanations", "Paper 2, Paper 5 (attention only)", "Seeds & retraining for SHAP on trees; LIME run-to-run"],
    ["Change by market phase", "Paper 4 (descriptive, 1 stock)", "Statistical testing of the difference"],
    ["Faithfulness", "nobody", "Fully open"],
    ["No-signal control", "nobody", "Fully open"],
  ];
  const colX = [M, M + 3.5, M + 7.4], colW = [3.3, 3.7, 4.5];
  headers.forEach((h, c) => s.addText(h.toUpperCase(), {
    x: colX[c], y: 1.72, w: colW[c], h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, bold: true, color: AMBER, charSpacing: 1,
  }));
  rows.forEach((r, i) => {
    const y = 2.1 + i * 0.66;
    if (i % 2 === 0) s.addShape(pres.ShapeType.rect, { x: M - 0.15, y: y - 0.06, w: W - 2 * M + 0.3, h: 0.6, fill: { color: LIGHT }, line: { color: LIGHT } });
    const strong = r[1] === "nobody";
    r.forEach((t, c) => s.addText(t, {
      x: colX[c], y: y + 0.02, w: colW[c], h: 0.5, isTextBox: true, margin: 0, fontFace: BODY,
      fontSize: 13.5, bold: strong && c > 0, color: strong && c > 0 ? AMBER : "26324A", valign: "middle",
    }));
  });
  card(s, M, 5.55, W - 2 * M, 1.05, INK);
  s.addText([
    { text: "Verified by searching all five PDFs:  ", options: { bold: true, color: WHITE } },
    { text: "“faithful”, “deletion” and “sanity” appear 0 times. No paper uses a shuffled-label control. LIME appears in one paper only, never compared with its own SHAP results.", options: { color: ICE } },
  ], { x: M + 0.35, y: 5.75, w: W - 2 * M - 0.7, h: 0.7, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13.5, lineSpacing: 18 });
  s.addNotes("Be honest: papers 2, 4 and 5 each test one property. My contribution is the full validation protocol plus the two tests nobody does.");
}

/* ------------------------------------------------ 7. Problem statement */
{
  const s = pres.addSlide();
  s.background = { color: INK };
  s.addShape(pres.ShapeType.ellipse, { x: -1.6, y: 4.4, w: 4.6, h: 4.6, fill: { color: NAVY }, line: { color: NAVY } });
  s.addText("PROBLEM STATEMENT", { x: M, y: 0.8, w: 9, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, bold: true, color: AMBER, charSpacing: 2 });
  s.addText("Given daily price and volume data for 474 S&P 500 stocks, build a Random Forest that forecasts each stock's next-day closing price, measure its accuracy against a naive “tomorrow = today” benchmark, and determine whether its SHAP and LIME explanations can be trusted.", {
    x: M, y: 1.3, w: 11.4, h: 1.9, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 24, color: WHITE, lineSpacing: 34,
  });
  const qs = [
    ["Faithful?", "Do the features it ranks highest really drive the prediction?"],
    ["Stable?", "Same explanation after retraining, a new seed, or re-running LIME?"],
    ["Agreed?", "Do SHAP and LIME say the same thing about one forecast?"],
    ["Meaningful?", "Different from a model trained on scrambled labels?"],
    ["Consistent?", "Do explanations change across crashes and sectors?"],
  ];
  qs.forEach(([h, t], i) => {
    const x = M + (i % 3) * 3.95, y = 3.55 + Math.floor(i / 3) * 1.55;
    s.addShape(pres.ShapeType.roundRect, { x, y, w: 3.6, h: 1.3, rectRadius: 0.08, fill: { color: "232F63" }, line: { color: "35437A", width: 1 } });
    s.addText(h, { x: x + 0.25, y: y + 0.15, w: 3.1, h: 0.35, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: AMBER });
    s.addText(t, { x: x + 0.25, y: y + 0.52, w: 3.15, h: 0.7, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, color: ICE, lineSpacing: 16 });
  });
  s.addNotes("Five questions = five reliability tests. These map directly onto my results slides.");
}

/* ------------------------------------------------ 8. Project design */
{
  const s = pres.addSlide();
  titleBar(s, "My project", "Design: one model, 474 stocks, 10 years");
  s.addChart(pres.ChartType.bar, [{
    name: "Stocks studied",
    labels: ["Manikrao 2025", "Indra 2025", "Song 2026", "Lee & Cai 2025", "Pagliaro 2026", "This project"],
    values: [1, 6, 20, 22, 51, 474],
  }], {
    x: M, y: 1.8, w: 6.6, h: 3.9, barDir: "bar", chartColors: ["8FA6CC", "8FA6CC", "8FA6CC", "8FA6CC", "8FA6CC", AMBER],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontFace: BODY, dataLabelFontSize: 11, dataLabelColor: "26324A",
    catAxisLabelFontFace: BODY, catAxisLabelFontSize: 12, catAxisLabelColor: "26324A",
    valAxisLabelFontFace: BODY, valAxisLabelFontSize: 10, valAxisLabelColor: GREY, valAxisMaxVal: 560, valAxisMinVal: 0,
    showLegend: false, valGridLine: { color: "E3E9F4", size: 1 }, catGridLine: { style: "none" }, barGapWidthPct: 55,
  });
  card(s, 7.7, 1.8, 4.95, 3.9, LIGHT);
  s.addText("Setup", { x: 8.05, y: 2.0, w: 4.3, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 17, bold: true, color: NAVY });
  s.addText([
    { text: "474 S&P 500 stocks, 11 sectors, 2012–2022", options: { bullet: true, breakLine: true } },
    { text: "1.1 million stock-days; 405,545 test forecasts", options: { bullet: true, breakLine: true } },
    { text: "Random Forest, 300 trees, 32 technical features", options: { bullet: true, breakLine: true } },
    { text: "Retrained every January, tested on the next year", options: { bullet: true, breakLine: true } },
    { text: "38,183 forecasts explained with SHAP; LIME run 5× each", options: { bullet: true, breakLine: false } },
  ], { x: 8.0, y: 2.5, w: 4.45, h: 3.0, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13.5, color: "26324A", paraSpaceAfter: 8, lineSpacing: 18 });
  s.addText("Every reviewed paper used between 1 and 51 stocks.", {
    x: M, y: 5.8, w: 8, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, italic: true, color: GREY,
  });
  s.addNotes("One model predicts every stock every day. Walk-forward testing means the test years are never used for any design choice.");
}

/* ------------------------------------------------ 9. Faithfulness test */
{
  const s = pres.addSlide();
  titleBar(s, "The central new test", "Faithfulness: delete what the explanation calls important");
  s.addChart(pres.ChartType.line, [
    { name: "Remove top-SHAP features first", labels: ["0", "1", "2", "4", "8", "16", "32"], values: [0, 8.70, 8.39, 8.36, 8.47, 8.56, 8.59] },
    { name: "Remove random features", labels: ["0", "1", "2", "4", "8", "16", "32"], values: [0, 0.65, 1.19, 2.04, 3.65, 5.88, 8.59] },
  ], {
    x: M, y: 1.85, w: 7.1, h: 3.7, chartColors: [AMBER, "8FA6CC"], lineDataSymbol: "circle", lineDataSymbolSize: 7, lineSize: 3,
    showLegend: true, legendPos: "b", legendFontFace: BODY, legendFontSize: 12, legendColor: "26324A",
    catAxisTitle: "features removed", showCatAxisTitle: true, catAxisTitleFontSize: 11, catAxisTitleColor: GREY,
    valAxisTitle: "change in forecast (bp)", showValAxisTitle: true, valAxisTitleFontSize: 11, valAxisTitleColor: GREY,
    catAxisLabelFontFace: BODY, catAxisLabelFontSize: 11, catAxisLabelColor: "26324A",
    valAxisLabelFontFace: BODY, valAxisLabelFontSize: 11, valAxisLabelColor: GREY,
    valGridLine: { color: "E3E9F4", size: 1 }, catGridLine: { style: "none" },
  });
  const steps = [
    "Ask SHAP which features drove one forecast.",
    "Replace the top one with a value from a random training day.",
    "Re-run the model: how far did the forecast move?",
    "Repeat in random order as a control, over 2,000 stock-days.",
  ];
  s.addText("How it works", { x: 8.2, y: 1.95, w: 4.4, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 17, bold: true, color: NAVY });
  steps.forEach((t, i) => {
    const y = 2.45 + i * 0.72;
    numberBadge(s, 8.2, y, i + 1, NAVY);
    s.addText(t, { x: 8.78, y: y - 0.02, w: 3.9, h: 0.6, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, color: "26324A", lineSpacing: 16 });
  });
  card(s, 8.2, 5.4, 4.45, 0.85, LIGHT);
  s.addText([
    { text: "13×", options: { fontSize: 22, bold: true, color: AMBER, fontFace: HEAD } },
    { text: "  more movement than deleting random features", options: { fontSize: 13, color: "26324A" } },
  ], { x: 8.45, y: 5.58, w: 4.0, h: 0.5, isTextBox: true, margin: 0, fontFace: BODY, valign: "middle" });
  s.addNotes("If the curves were the same, the explanation would be decoration. Fidelity: the SHAP values of removed features predict the actual change at r = 0.98.");
}

/* ------------------------------------------------ 10. Results */
{
  const s = pres.addSlide();
  titleBar(s, "Results", "What the audit found");
  const cells = [
    ["Accuracy", "98.44%", "price accuracy — but identical to the naive forecast (p = 0.30)", NAVY],
    ["Faithful", "13×", "top-SHAP features move forecasts 13× more than random ones", AMBER],
    ["Stable", "τ 0.85", "SHAP agrees across random seeds; LIME only ρ 0.48 between runs", NAVY],
    ["Agreement", "τ 0.03", "SHAP vs accuracy-based importance: only 4 of 32 features help accuracy", AMBER],
    ["Meaningful", "τ 0.13", "explanations differ sharply from a no-signal model — they pass", NAVY],
    ["Consistent", "p = 0.003", "explanations change significantly across market regimes", AMBER],
  ];
  cells.forEach(([label, big, text, colour], i) => {
    const x = M + (i % 3) * 4.0, y = 1.8 + Math.floor(i / 3) * 2.05;
    card(s, x, y, 3.75, 1.8, WHITE);
    s.addText(label.toUpperCase(), { x: x + 0.3, y: y + 0.18, w: 3.1, h: 0.3, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 10.5, bold: true, color: GREY, charSpacing: 1 });
    s.addText(big, { x: x + 0.3, y: y + 0.45, w: 3.1, h: 0.6, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 28, bold: true, color: colour });
    s.addText(text, { x: x + 0.3, y: y + 1.05, w: 3.2, h: 0.65, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, color: "26324A", lineSpacing: 15 });
  });
  s.addText("The explanations are faithful and stable — but they describe what the model does, not what predicts the market.", {
    x: M, y: 6.0, w: W - 2 * M, h: 0.5, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 15, italic: true, color: NAVY,
  });
  s.addNotes("Key nuance: faithful does not mean the market insight is real. SHAP and permutation importance disagree almost completely.");
}

/* ------------------------------------------------ 11. Contribution */
{
  const s = pres.addSlide();
  s.background = { color: INK };
  s.addShape(pres.ShapeType.ellipse, { x: 10.6, y: 3.9, w: 5.0, h: 5.0, fill: { color: NAVY }, line: { color: NAVY } });
  s.addText("CONTRIBUTION", { x: M, y: 0.9, w: 9, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13, bold: true, color: AMBER, charSpacing: 2 });
  s.addText("A validation protocol, not a new XAI method", {
    x: M, y: 1.35, w: 11, h: 0.9, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 32, bold: true, color: WHITE,
  });
  const points = [
    ["Benchmarked accuracy", "Every figure reported next to naive persistence, with a significance test."],
    ["Two tests nobody runs", "Faithfulness (deletion) and a no-signal control model."],
    ["First SHAP vs LIME comparison", "On the same 804 forecasts, five runs each."],
    ["Drift tested, not described", "Permutation tests across 4 market regimes and 11 sectors."],
  ];
  points.forEach(([h, t], i) => {
    const y = 2.55 + i * 0.95;
    numberBadge(s, M, y, i + 1, AMBER);
    s.addText(h, { x: M + 0.6, y: y - 0.02, w: 4.2, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: WHITE });
    s.addText(t, { x: M + 4.9, y: y - 0.02, w: 5.6, h: 0.6, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 13.5, color: ICE, lineSpacing: 17 });
  });
  s.addText("Scope: 474 S&P 500 stocks · daily price and volume only · 2012–2022 · code and data reproducible end to end.", {
    x: M, y: 6.6, w: 11.4, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12.5, italic: true, color: "9FB2D8",
  });
  s.addNotes("If challenged that this exists already: concede that papers 2, 4 and 5 each test one property, on 6-51 stocks. The contribution is running the full protocol together on 474 stocks.");
}

pres.writeFile({ fileName: process.argv[2] || "deck.pptx" }).then(f => console.log("wrote", f));

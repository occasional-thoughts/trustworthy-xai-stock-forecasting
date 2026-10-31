"""Content of the VIT project report, as structured blocks.

Block forms consumed by make_vit_report.py:
    ("h2", text) / ("h3", text)        numbered section headings
    ("p", text)                        justified body paragraph
    ("bullet", [..]) / ("num", [..])   lists
    ("table", caption, header, rows)   caption is placed above the table
    ("table", caption, header, rows, widths)
    ("figure", path, caption)          caption is placed below the figure
    ("figure", path, caption, width_cm)
    ("code", text)                     monospaced block
    ("quote", text)                    indented italic block

Every figure in results/figures and every number quoted here comes from the committed
result files; nothing is restated from memory.
"""

META = {
    "course": "BCSE418L - Explainable AI",
    "title": "Trustworthy Explanations for Random-Forest Stock Price Forecasting",
    "degree": "Bachelor of Technology",
    "programme": "Computer Science and Engineering",
    "students": [("23BAI0190", "ANTONY ABISHA"),
                 ("23BAI0201", "AKAKSHAR SHARMA"),
                 ("23BAI0213", "ARCHITA KHARE")],
    "guide": "Dr. Abdul Gaffar",
    "designation": "Associate Professor",
    "school": "School of Computer Science and Engineering",
    "place": "Vellore",
    "month": "November 2026",
    "semester": "Fall Semester 2026-2027",
}

ABSTRACT = [
    "Machine-learning models are widely used to forecast stock prices, and because such "
    "models are opaque, studies increasingly attach explainable-AI methods such as SHAP and "
    "LIME to describe what drove each forecast. Two weaknesses run through this literature. "
    "Accuracy is reported on the price level, where the naive forecast that tomorrow equals "
    "today already scores an R-squared above 0.999, so the reported figure describes the "
    "behaviour of daily stock prices rather than the quality of the model. And explanations "
    "are presented as findings without ever being tested, so an explanation that describes "
    "noise, a single random seed or a single market period is indistinguishable from one "
    "that describes a learned relationship.",

    "This project addresses both. A leakage-free Random Forest is trained walk-forward on "
    "474 S&P 500 stocks over 1,097,165 stock-days from March 2013 to May 2022, retrained at "
    "the start of each test year, and used to forecast the next-day log return for 405,545 "
    "out-of-sample stock-days. Skill is measured in return space first and in price space "
    "second. The same set of forecasts scores an R-squared of 0.9994 on the price level and "
    "+0.00013 on the return, a figure a Diebold-Mariano test cannot distinguish from "
    "predicting no change at all. A Random Forest trained directly on price levels reports "
    "an R-squared of 0.993 yet is significantly worse than naive persistence.",

    "Every forecast is then explained with TreeSHAP and LIME, and those explanations are "
    "subjected to a five-part reliability audit: faithfulness by feature-deletion tests "
    "against a random-order control, stability across five random seeds and across "
    "consecutive yearly retrains, agreement among four explainers, sanity against models "
    "trained on shuffled labels, and drift across four market regimes and eleven GICS "
    "sectors tested by permutation. SHAP is found to be faithful, with a fidelity "
    "correlation of at least 0.98 and a 13-fold separation from random deletion, and stable "
    "to the random seed at Kendall tau 0.85. LIME is markedly less reliable for individual "
    "forecasts: run-to-run rank correlation 0.45, a median surrogate fit of 0.17, and a "
    "different top feature from SHAP on 41 per cent of forecasts. Explanations drift "
    "significantly across regimes and sectors, and neither method identifies the features "
    "that actually improve accuracy.",

    "The audit also found a reproducibility defect in the standard LIME usage pattern, "
    "which had inflated the reported SHAP-LIME agreement from tau 0.58 to tau 0.73. The "
    "complete pipeline runs forward: the same features, hyperparameters and explanation code "
    "produce audited next-session forecasts for 431 currently traded stocks, served through "
    "an interactive page that recomputes every explanation at request time.",
]

ABBREVIATIONS = [
    ("AOPC", "Area Over the Perturbation Curve"),
    ("API", "Application Programming Interface"),
    ("ATR", "Average True Range"),
    ("AUC", "Area Under the Receiver Operating Characteristic Curve"),
    ("bp", "Basis Point (one hundredth of one per cent)"),
    ("CSV", "Comma-Separated Values"),
    ("DFD", "Data-Flow Diagram"),
    ("DM", "Diebold-Mariano (test of equal predictive accuracy)"),
    ("GICS", "Global Industry Classification Standard"),
    ("HAC", "Heteroskedasticity and Autocorrelation Consistent"),
    ("IC", "Information Coefficient"),
    ("ICIR", "Information Coefficient Information Ratio"),
    ("JSON", "JavaScript Object Notation"),
    ("LIME", "Local Interpretable Model-agnostic Explanations"),
    ("MACD", "Moving Average Convergence Divergence"),
    ("MAE", "Mean Absolute Error"),
    ("MAPE", "Mean Absolute Percentage Error"),
    ("MDI", "Mean Decrease in Impurity"),
    ("MSE", "Mean Squared Error"),
    ("OHLCV", "Open, High, Low, Close, Volume"),
    ("RF", "Random Forest"),
    ("RMSE", "Root Mean Squared Error"),
    ("RSI", "Relative Strength Index"),
    ("SHAP", "SHapley Additive exPlanations"),
    ("SMA", "Simple Moving Average"),
    ("TVD", "Total Variation Distance"),
    ("UML", "Unified Modeling Language"),
    ("XAI", "Explainable Artificial Intelligence"),
]

SYMBOLS = [
    ("x(i,t)", "Feature vector for stock i on trading day t, 32 dimensions"),
    ("r(i,t+1)", "Realised next-day log return of stock i"),
    ("r-hat", "Forecast next-day log return produced by the Random Forest"),
    ("P(i,t)", "Closing price of stock i on day t"),
    ("f", "The trained Random Forest regressor"),
    ("phi", "SHAP attribution vector for one forecast, 32 dimensions"),
    ("lambda", "LIME weight vector for one forecast, 32 dimensions"),
    ("tau", "Kendall rank correlation coefficient"),
    ("rho", "Spearman rank correlation coefficient"),
    ("k", "Number of features removed in a deletion test"),
    ("R-squared", "Out-of-sample coefficient of determination against a stated benchmark"),
    ("p", "Probability value of a statistical test"),
]


CH1 = [
    ("h2", "Background"),
    ("p",
     "Forecasting the next day's closing price of a listed company is one of the oldest "
     "applications of statistical learning, and tree ensembles have become the default tool "
     "for it. A Random Forest, introduced by Breiman in 2001, averages the predictions of "
     "many decision trees, each grown on a bootstrap sample of the data and a random subset "
     "of the inputs. It handles non-linear relationships without being told where they are, "
     "needs little tuning, and resists overfitting far better than a single deep tree. For "
     "price and volume data, where relationships are weak, noisy and unstable, those "
     "properties make it a sensible default."),
    ("p",
     "A Random Forest with three hundred trees is, however, not something a person can read. "
     "A risk officer asked to approve a model, or an investment committee asked to act on "
     "it, cannot inspect the ensemble and see why a particular stock was forecast to rise. "
     "This is the gap that explainable artificial intelligence is meant to close, and two "
     "methods dominate practice. SHAP, which derives from the Shapley value in cooperative "
     "game theory, divides a single forecast into additive contributions, one per input "
     "feature, so that the contributions and a base value sum exactly to the forecast. LIME "
     "approaches the same problem differently: it samples perturbed versions of one input, "
     "weights them by how close they are to the original, and fits a simple linear model to "
     "the predictions, whose coefficients then serve as the explanation."),
    ("p",
     "Both are now routine in published stock-forecasting work. A typical paper trains a "
     "tree ensemble, reports an accuracy figure, runs SHAP, and presents the resulting "
     "ranking of features as insight into what moves the market. The present project takes "
     "that pattern seriously enough to test it, and finds that both halves of it need "
     "qualification."),

    ("h2", "Motivations"),
    ("p",
     "Two weaknesses recur across recent work in this area, and together they motivate the "
     "whole of this project."),
    ("h3", "Accuracy Reported in the Wrong Units"),
    ("p",
     "Price forecasts are conventionally judged on the price level, using R-squared, mean "
     "absolute percentage error, or a derived figure described as accuracy. The difficulty "
     "is that a stock's price tomorrow is almost exactly its price today. The naive forecast "
     "that tomorrow equals today therefore achieves an R-squared of about 0.999 and a mean "
     "absolute percentage error of about 1.5 per cent on this dataset. A model that reports "
     "98 per cent accuracy has reported a property of daily stock prices, not an achievement "
     "of its own."),
    ("p",
     "What a forecaster actually has to get right is the return, which is the change. "
     "Scored on returns, forecasts that look near-perfect on prices routinely explain less "
     "than a tenth of one per cent of the variance. Without reporting skill in return space, "
     "and without testing it against a naive benchmark, a reader cannot tell whether a model "
     "has any predictive value at all."),
    ("h3", "Explanations Presented as Findings but Never Tested"),
    ("p",
     "The second weakness concerns the explanations themselves. Studies report that volume, "
     "or volatility, or some technical indicator is the most important feature, and read "
     "that as a statement about the market. An explanation method, however, always returns a "
     "ranked list. It returns one whether or not the model uses those features, whether or "
     "not the ranking would survive a change of random seed, and whether or not the model "
     "learned anything at all. Nothing in a bar chart distinguishes a true explanation from "
     "a plausible one."),
    ("table", "Properties an explanation must have, and the consequence of each failing",
     ["Property", "Question it answers", "If it fails"],
     [["Faithful", "Does removing the features the explanation ranks highest actually change "
                   "the forecast most?", "The explanation describes features the model does not use"],
      ["Stable", "Do the explanations survive re-seeding and retraining?",
       "The explanation is an artefact of one random seed or one training run"],
      ["Consistent", "Do SHAP, LIME and importance measures agree?",
       "Conclusions depend on which tool happened to be chosen"],
      ["Meaningful", "Do they differ from the explanations of a model trained on shuffled "
                     "labels?", "The explanation reflects feature structure, not a learned relationship"],
      ["Contextual", "Do they change across market regimes and sectors?",
       "A single global explanation misrepresents specific periods or sectors"]],
     [14, 34, 34]),
    ("p",
     "In finance these are not academic concerns. A misleading explanation can justify a "
     "position, pass a model through a governance process it should not have passed, and "
     "lose money. The motivation for this project is therefore to build a forecaster that is "
     "measured honestly, and then to test its explanations rather than presenting them."),

    ("h2", "Scope of the Project"),
    ("p", "The following are within scope:"),
    ("bullet", [
        "Daily data at one-day-ahead horizon, for constituents of the S&P 500 index.",
        "Features derived from price and volume only, computed from information available "
        "at or before the close of the day on which the forecast is made.",
        "Post-hoc explanation of a trained model using SHAP and LIME, together with "
        "permutation importance and mean decrease in impurity as comparison explainers.",
        "A reliability audit of those explanations covering faithfulness, stability, "
        "explainer agreement, sanity against signal-free models, and drift across market "
        "regimes and sectors.",
        "A working demonstration that applies the identical pipeline to the next trading "
        "session, so that no step can depend on knowing the outcome."]),
    ("p", "The following are outside scope:"),
    ("bullet", [
        "News, sentiment, fundamental and macroeconomic data.",
        "Intraday data and horizons shorter or longer than one trading day.",
        "Realistic execution modelling. A single flat ten basis point round-trip cost is "
        "applied to the decile portfolio as a sanity check, but slippage, market impact, "
        "borrowing costs and capacity are not modelled.",
        "Portfolio construction and optimisation.",
        "Deep-learning architectures. The project concerns the reliability of explanations "
        "for a tree ensemble, and TreeSHAP is exact only for tree models."]),
    ("p",
     "The project is a study of forecasting and of explanation reliability. It is not a "
     "trading system, and the results reported in Chapter 7 are the reason it should not be "
     "used as one."),
]


CH2 = [
    ("h2", "Literature Review"),
    ("p",
     "Five recent papers, published in 2025 and 2026, are closest to this work. Each "
     "predicts stock prices or returns with a tree-based or comparable model, explains the "
     "model with SHAP or LIME, or examines the stability of explanations."),
    ("table", "Recent work on explainable stock prediction, and the gap each leaves",
     ["No.", "Paper and venue", "Methodology", "Gap"],
     [["1", "Indra et al., Stock Return Prediction on the LQ45 Market Index Using a Machine "
            "Learning Algorithm Based on Technical Indicators. Journal of Risk and Financial "
            "Management, 2025",
       "Random Forest, XGBoost, linear and Ridge regression on technical indicators for six "
       "Indonesian stocks at 5- and 21-day horizons; SHAP used to rank features",
       "Only six stocks. SHAP results are reported but never checked for correctness or "
       "stability."],
      ["2", "Lee and Cai, Comparing model-specific and model-agnostic feature importance "
            "methods using machine learning with technical indicators. Machine Learning with "
            "Applications, 2025",
       "Random Forest and neural networks across the eleven NASDAQ sectors; compares feature "
       "importance methods as a tool for selecting indicators",
       "Importance methods are used only to select features. Whether the explanations are "
       "trustworthy, or change over time, is not examined."],
      ["3", "Manikrao et al., An Explainable AI for Stock Market Prediction. Journal of "
            "Computational and Cognitive Engineering, 2025",
       "LSTM with attention over sentiment and technical indicators, compared against Random "
       "Forest and XGBoost; SHAP and LIME used side by side",
       "SHAP and LIME are presented together but never compared, and LIME is never re-run to "
       "see whether it returns the same answer."],
      ["4", "Pagliaro, Regime-Aware LightGBM for Stock Market Forecasting. Electronics, 2026",
       "LightGBM on 51 NASDAQ-100 stocks with a walk-forward design adjusted for bull and "
       "bear phases; explanations shown to differ by phase",
       "The claim that explanations change across phases is asserted qualitatively, not "
       "tested statistically, and covers only 51 stocks."],
      ["5", "Song et al., Attention Integration Strategies in MLP-Based Stock Movement "
            "Prediction. Electronics, 2026",
       "Multi-layer perceptron variants trained 1,600 times with different random seeds on "
       "20 stocks drawn from the CSI 300 and the S&P 500",
       "Establishes that explanations move with the random seed, but only for neural "
       "networks, not for a Random Forest explained by SHAP or LIME."]],
     [5, 27, 34, 30]),
    ("p",
     "Taken together, these papers establish the practice this project examines. Papers 1 "
     "and 3 report explanations as findings. Paper 2 treats importance as a feature-selection "
     "device. Paper 4 observes regime dependence without testing it. Paper 5 demonstrates "
     "seed sensitivity, which is precisely the kind of check the others omit, but does so "
     "for a different model family."),

    ("h2", "Research Gap"),
    ("table", "What is missing from the reviewed work, and how this project supplies it",
     ["Missing element", "Papers affected", "Addressed here by"],
     [["Faithfulness: evidence that the explanation points at features the model really uses",
       "1, 3", "Deletion tests in which removing top-ranked features must change the forecast "
               "more than removing random ones"],
      ["Stability under re-seeding, retraining and repeated explanation",
       "1, 3, 5", "Five random seeds, four consecutive yearly retrains, and five LIME runs "
                  "per forecast"],
      ["Agreement between explainers", "2, 3",
       "TreeSHAP against LIME, permutation importance and mean decrease in impurity"],
      ["Statistical testing of regime and sector dependence", "2, 4",
       "Permutation tests across four market regimes and eleven GICS sectors"],
      ["A broad stock universe", "1, 4, 5 (six to 51 stocks)", "474 S&P 500 constituents"]],
     [34, 16, 40]),
    ("quote",
     "No published study tests, for a Random Forest stock price model, whether SHAP and LIME "
     "explanations are faithful to the model, stable when the model or the explainer is "
     "re-run, in agreement with one another, and consistent across market phases such as the "
     "COVID crash and across sectors. This project supplies that test on 474 S&P 500 stocks, "
     "with forecast accuracy benchmarked against naive persistence throughout."),

    ("h2", "Objectives"),
    ("num", [
        "Build a leakage-free, walk-forward Random Forest that forecasts the next-day "
        "closing price for 474 S&P 500 stocks.",
        "Measure its skill in return space first, using out-of-sample R-squared against both "
        "a zero-return and a drift benchmark, the information coefficient, directional "
        "accuracy and a decile portfolio, with Diebold-Mariano and binomial significance "
        "tests against naive persistence; report price-space accuracy second, for "
        "comparability with the literature.",
        "Explain every sampled forecast with TreeSHAP and LIME, and compare four explainers.",
        "Audit those explanations for faithfulness, stability and sanity against models "
        "trained on shuffled labels.",
        "Test explanation drift across market regimes and GICS sectors with permutation "
        "tests.",
        "Demonstrate the whole pipeline running forward on a trading session that has not "
        "yet happened, with every explanation recomputed at request time."]),

    ("h2", "Problem Statement"),
    ("quote",
     "Given daily price and volume data for 474 S&P 500 stocks from 2012 to 2022, build a "
     "Random Forest that forecasts each stock's next-day closing price, measure its accuracy "
     "against naive and learned baselines with significance tests, and explain every forecast "
     "with SHAP and LIME. Then determine whether those explanations can be trusted: whether "
     "they are faithful to the model, stable across random seeds and yearly retraining, "
     "consistent with each other and with importance-based explainers, different from the "
     "explanations of a model with no real signal, and consistent across market regimes and "
     "GICS sectors."),
    ("h3", "Formal Definition"),
    ("table", "Formal specification of the forecasting and explanation problem",
     ["Element", "Definition"],
     [["Universe", "N = 474 S&P 500 stocks indexed by i, trading days indexed by t"],
      ["Input", "A feature vector x(i,t) in 32 dimensions, computed only from prices and "
                "volumes up to and including the close of day t, in seven families"],
      ["Output", "A forecast of the next-day closing price P-hat(i,t+1)"],
      ["Model", "A Random Forest f predicting the next-day log return, r-hat = f(x(i,t)); "
                "the price forecast is P(i,t) multiplied by exp(r-hat)"],
      ["Explanations", "A SHAP vector phi and a LIME weight vector lambda, each in 32 "
                       "dimensions, for every explained forecast"],
      ["Evaluation", "Primary: return-space skill against zero-return and drift benchmarks, "
                     "tested with Diebold-Mariano. Secondary: price-space accuracy. Plus a "
                     "five-part reliability audit of phi and lambda"]],
     [18, 64]),
    ("h3", "Research Questions"),
    ("table", "Research questions addressed by this project",
     ["No.", "Research question"],
     [["RQ1", "How much skill does the Random Forest have on the quantity it predicts, the "
              "next-day return, and how much of its apparent price-level accuracy survives "
              "once it is scored in return space against naive persistence?"],
      ["RQ2", "Which features and feature families drive the forecasts, globally and for "
              "individual stock-days?"],
      ["RQ3", "Are the SHAP explanations faithful to the model, and stable across random "
              "seeds and yearly retraining?"],
      ["RQ4", "Do the explanations change significantly across market regimes and GICS "
              "sectors?"],
      ["RQ5", "Do the explanations differ from those of models trained on shuffled, "
              "signal-free labels?"],
      ["RQ6", "Do SHAP and LIME agree, and which is more stable and faithful for this "
              "model?"]],
     [8, 74]),

    ("h2", "Project Plan"),
    ("p",
     "The work was organised as six stages, each writing its own artifact to disk so that "
     "any stage can be re-run or inspected without repeating the ones before it. The design "
     "decision that governs the schedule is that the test period is touched only once, at "
     "the end: hyperparameters are chosen on a validation year, and the walk-forward test "
     "runs afterwards."),
    ("table", "Project plan by stage",
     ["Stage", "Activity", "Deliverable"],
     [["1", "Literature survey and gap analysis; selection of the benchmark dataset",
       "Reviewed set of five papers; stated research gap"],
      ["2", "Data acquisition and cleaning; diagnosis of the three defects in the raw panel",
       "panel_clean.pkl"],
      ["3", "Feature engineering, with leakage control verified on wide date-by-ticker tables",
       "features.pkl, 32 features in seven families"],
      ["4", "Hyperparameter tuning on the validation year; walk-forward training",
       "tuning.json, four yearly models, 405,545 forecasts"],
      ["5", "Evaluation in return and price space, with significance tests and a decile "
            "portfolio", "metrics.json and five result figures"],
      ["6", "Explanation with TreeSHAP and LIME, and the five-part reliability audit",
       "xai.json, lime.json and ten further figures"],
      ["7", "Live forecasting and the interactive demonstration",
       "live_forecast.pkl, the served audit page"]],
     [8, 48, 34]),
]


CH3 = [
    ("h2", "Requirements"),
    ("h3", "Functional Requirements"),
    ("table", "Functional requirements",
     ["ID", "Requirement"],
     [["FR1", "The system shall load daily OHLCV data for 474 S&P 500 stocks and repair the "
              "three known data defects before use."],
      ["FR2", "The system shall compute 32 technical, volatility, volume and market-context "
              "features per stock-day, using only information available at or before that "
              "day's close."],
      ["FR3", "The system shall train a Random Forest to predict the next-day log return, "
              "and shall derive price forecasts from it rather than training on price levels."],
      ["FR4", "The system shall retrain walk-forward at the start of each test year on all "
              "prior data, and shall never use test-period data for tuning or design."],
      ["FR5", "The system shall produce forecasts from five comparison models: naive "
              "persistence, historical drift, Ridge regression, a price-level Random Forest "
              "and a direction classifier."],
      ["FR6", "The system shall report return-space skill as the primary result and "
              "price-space accuracy as a secondary result, for the whole test set and broken "
              "down by year, market regime and GICS sector."],
      ["FR7", "The system shall test each model against its benchmark with a "
              "Diebold-Mariano test, and directional accuracy against the majority rule with "
              "a binomial test."],
      ["FR8", "The system shall compute exact TreeSHAP attributions for a stratified sample "
              "of at least 35,000 stock-days, and shall verify SHAP additivity."],
      ["FR9", "The system shall compute LIME explanations for a sample of stock-days with at "
              "least five random seeds each, to measure run-to-run stability."],
      ["FR10", "The system shall test explanation faithfulness by deleting top-ranked "
               "features against a random-order control, reporting deletion curves, AOPC and "
               "fidelity."],
      ["FR11", "The system shall test explanation stability across random seeds and across "
               "consecutive yearly retrains, using Kendall tau and Spearman rho."],
      ["FR12", "The system shall compare four explainers and report their rank agreement."],
      ["FR13", "The system shall test explanation sanity against two null models trained on "
               "shuffled labels."],
      ["FR14", "The system shall test explanation drift across the four market regimes and "
               "the eleven GICS sectors with a 1,000-draw permutation test."],
      ["FR15", "The system shall emit all results as machine-readable JSON, all figures as "
               "PNG, and the write-up as Markdown and Word."],
      ["FR16", "The system shall provide an interactive page that accepts a stock and a "
               "trading day and returns, computed live from the saved model, the forecast, "
               "its TreeSHAP and LIME explanations, their agreement, LIME's run-to-run "
               "stability and a faithfulness test for that single forecast."],
      ["FR17", "The system shall additionally forecast the next trading session, retraining "
               "with the same hyperparameters up to the latest close and presenting the "
               "result with its outcome fields explicitly blank."],
      ["FR18", "The system shall state, wherever a live forecast is shown, how many of the "
               "original 474 tickers still trade, which price vendor was used, and that the "
               "backtest found no return skill."]],
     [8, 74]),
    ("h3", "Non-Functional Requirements"),
    ("table", "Non-functional requirements",
     ["ID", "Requirement"],
     [["NFR1", "Reproducibility. Every stochastic component is seeded, and a full re-run "
               "must reproduce every published number."],
      ["NFR2", "No look-ahead. Feature construction, scaling and model selection must be "
               "verifiable as using only past information."],
      ["NFR3", "Runtime. The complete pipeline must finish in under one hour on a laptop. "
               "Measured: approximately 25 minutes."],
      ["NFR4", "Memory. The system must run within 16 GB of RAM; the feature table holds "
               "about 1.1 million stock-days across 32 float32 columns."],
      ["NFR5", "Transparency of negative results. Results that undercut the model must be "
               "reported, not suppressed."],
      ["NFR6", "Auditability. Each pipeline stage writes its own artifact, so any stage can "
               "be re-run or inspected independently."]],
     [8, 74]),
    ("p",
     "NFR1 proved to be more than a formality. Enforcing it uncovered a defect in the way "
     "LIME is conventionally used, described in Section 5.3.3, which had been inflating one "
     "of the headline results."),

    ("h2", "Feasibility Study"),
    ("h3", "Technical Feasibility"),
    ("p",
     "The project is technically feasible on a single laptop. The dataset is 1.1 million "
     "rows by 32 float32 columns, roughly 140 MB in memory, well within the 18 GB available. "
     "The expensive steps are training four Random Forests of 300 trees each, which takes "
     "between 96 and 185 seconds per test year, and computing TreeSHAP for 38,183 "
     "stock-days. TreeSHAP is polynomial in tree depth rather than exponential in the number "
     "of features, which is what makes exact Shapley values tractable here at all; the same "
     "computation with a model-agnostic Shapley method would be infeasible. The complete "
     "pipeline runs end to end in about 25 minutes, comfortably inside the one-hour budget "
     "set by NFR3. Every library used is open source and actively maintained."),
    ("h3", "Economic Feasibility"),
    ("p",
     "The direct cost of the project is zero. The dataset is a public research benchmark "
     "released with the ESTIMATE paper and carries no licence fee; live prices come from "
     "Yahoo Finance through the open-source yfinance package; all software is open source; "
     "and the computation runs on hardware already owned. No cloud compute, no paid data "
     "subscription and no commercial solver is required. Against this, the economic finding "
     "of the project is negative and is reported as such in Section 7.1.3: the decile "
     "strategy earns 8.2 basis points a day before costs and loses 1.8 basis points a day "
     "after a ten basis point round-trip charge, so the model has no demonstrated commercial "
     "value as a trading signal."),
    ("h3", "Social Feasibility"),
    ("p",
     "The social considerations are about how the output is presented rather than whether it "
     "can be built. A forecasting model with a published explanation invites more confidence "
     "than one without, and that confidence is exactly what this project shows to be "
     "unwarranted when the explanation is untested. Three design decisions follow. Results "
     "are reported in return space first, so that no reader can mistake a property of daily "
     "prices for model skill. Negative findings are reported in full, including the periods "
     "in which the model was actively wrong. And the interactive demonstration states on the "
     "page itself that the backtest found no return skill, lists the delisted tickers rather "
     "than quietly dropping them, and warns when a live forecast has gone stale. The system "
     "is a research instrument, and it is presented as one."),

    ("h2", "System Specification"),
    ("h3", "Hardware Specification"),
    ("table", "Hardware used",
     ["Component", "Specification"],
     [["Processor", "Apple M3 Pro, 12 cores"],
      ["Memory", "18 GB unified"],
      ["Storage", "About 1.3 GB for the raw panel and all derived artifacts"],
      ["Operating system", "macOS 14.4"],
      ["Minimum required", "Any 64-bit machine with 16 GB of RAM; no GPU is used"]],
     [26, 56]),
    ("h3", "Software Specification"),
    ("table", "Software stack",
     ["Layer", "Tool and version", "Used for"],
     [["Language", "Python 3.11.13", "All code, 13 modules in src/"],
      ["Environment", "venv", "Isolated, reproducible dependencies"],
      ["Data handling", "pandas 3.0.5, NumPy 2.1.3",
       "Cleaning the panel, feature engineering on wide tables, results"],
      ["Machine learning", "scikit-learn 1.9.1",
       "RandomForestRegressor, RandomForestClassifier, RidgeCV, permutation_importance"],
      ["Explanation: SHAP", "shap 0.51.0", "TreeExplainer, exact TreeSHAP values"],
      ["Explanation: LIME", "lime 0.2.0.1", "LimeTabularExplainer, local surrogate models"],
      ["Statistics", "SciPy 1.17.1",
       "Kendall tau, Spearman rho, binomial test, normal distribution for Diebold-Mariano"],
      ["Visualisation", "Matplotlib 3.11.2", "All 15 result figures and 6 design diagrams"],
      ["Model storage", "joblib 1.6.0", "Saved yearly Random Forest models"],
      ["Live prices", "yfinance 0.2.x", "Prices for the next-session forecast"],
      ["Demonstration", "Python standard library http.server, inline SVG",
       "The interactive page; no web framework is used"],
      ["Document build", "pandoc, python-docx", "Markdown and Word output"]],
     [20, 28, 44]),
]


CH4 = [
    ("h2", "System Architecture"),
    ("p",
     "The system is a six-stage pipeline. Each stage reads the artifact written by the stage "
     "before it and writes its own, so a change to the explanation code does not require "
     "retraining, and a change to the features does not require re-reviewing the literature. "
     "The arrangement also makes the no-look-ahead property inspectable: the only stage that "
     "sees test-period data is the one that forecasts it."),
    ("figure", "design/architecture.png",
     "System architecture. The six stages, their scripts and the artifacts they write", 15.4),
    ("h3", "Dataset"),
    ("p",
     "The raw dataset is the public S&P 500 benchmark released with the ESTIMATE paper and "
     "also used by StockMixer. It holds daily open, high, low, close, adjusted close and "
     "volume for 474 constituents across eleven GICS sectors, from 14 May 2012 to 25 May "
     "2022, a span of 2,526 trading days that includes both the COVID crash and the 2022 "
     "bear market."),
    ("table", "Dataset summary",
     ["Item", "Detail"],
     [["Source", "ESTIMATE S&P 500 benchmark (Huynh et al., WSDM 2023)"],
      ["Universe", "474 constituents, eleven GICS sectors holding 21 to 67 stocks each"],
      ["Fields", "Daily open, high, low, close, adjusted close and volume"],
      ["Period", "14 May 2012 to 25 May 2022, 2,526 trading days"],
      ["Usable stock-days", "1,097,165, after a 200-day feature warm-up and cleaning"],
      ["Training stock-days", "572,884 to the end of 2017"],
      ["Validation stock-days", "118,736, the calendar year 2018"],
      ["Test stock-days", "405,545 across 856 trading days, January 2019 to May 2022"],
      ["Class balance", "52.64 per cent of stock-days closed higher than the previous day"]],
     [26, 56]),
    ("h3", "Data Cleaning"),
    ("p",
     "The raw panel contains three defects, each of which would corrupt the learned model if "
     "left in place. They were found by checking an invariant that must hold for any "
     "well-formed price series: the day's close must lie between the day's low and high."),
    ("table", "Defects found in the raw panel and their repair",
     ["Defect", "Rows affected", "Repair"],
     [["Adjusted close missing before a stock was listed",
       "3,450", "Rows dropped"],
      ["For twelve tickers, open, high and low were already adjusted for dividends while "
       "close was not, so high and low did not bracket the close",
       "About 27,000",
       "The convention is detected per ticker by testing which basis puts the close inside "
       "the day's range more often, and all four prices are put on one adjusted basis"],
      ["GOOG before 27 March 2014 is a different, unadjusted share-class series, producing a "
       "single return of about minus 300 per cent", "470", "Rows dropped"]],
     [34, 14, 42]),
    ("p",
     "Genuine extreme moves are retained. The oil-price collapse of 9 March 2020, in which "
     "APA fell 54 per cent in one session, is real and stays in the data."),
    ("h3", "Feature Engineering"),
    ("p",
     "Thirty-two features are computed for each stock-day, grouped into seven families. The "
     "grouping is not cosmetic: explanations are reported by family as well as by individual "
     "feature, because a family share is more stable and more interpretable than a ranking "
     "of 32 correlated indicators."),
    ("table", "The 32 features, by family",
     ["Family", "Count", "Features"],
     [["Past returns", "6", "Log returns over 1, 2, 5, 10, 20 and 60 trading days"],
      ["Trend", "5", "Distance from the 5, 20, 50 and 200-day simple moving averages; MACD "
                     "histogram"],
      ["Oscillators", "3", "RSI(14), stochastic %K(14), Bollinger %B(20)"],
      ["Volatility", "6", "Realised volatility over 5, 20 and 60 days; ATR(14); the day's "
                          "log range; Bollinger band width"],
      ["Volume", "3", "Volume against its 20-day average; 5 against 20-day volume trend; log "
                      "dollar volume"],
      ["Candle", "3", "Overnight gap, open-to-close body, close position within the day's "
                      "range"],
      ["Market and sector", "6", "Equal-weighted market return over 1 and 5 days, 20-day "
                                 "market volatility, sector 5-day return, 20-day relative "
                                 "strength, 60-day beta"]],
     [22, 8, 52]),
    ("p",
     "Every feature obeys one rule: the value for stock i on day t uses only prices and "
     "volumes up to and including the close of day t. Features are computed on wide tables "
     "indexed by date and ticker, where every backward shift is explicit, and are then "
     "stacked into one row per stock-day. A row survives only if all 32 features and all "
     "targets are present; no missing value is imputed, because an invented input would "
     "undermine the premise of a study about whether explanations can be trusted."),
    ("p",
     "The prediction target is the next trading day's log return, with the next day's "
     "closing price and an up-or-down indicator carried alongside for the secondary "
     "price-space and directional analyses."),

    ("h2", "Design"),
    ("h3", "Data-Flow Diagram"),
    ("p",
     "The context diagram shows the system as a single process between the market data "
     "vendor, which supplies prices, and the analyst, who supplies a stock and a date and "
     "receives a forecast together with its explanation and audit."),
    ("figure", "design/dfd_level0.png", "Level 0 context data-flow diagram", 14.6),
    ("p",
     "The level 1 diagram decomposes that process into the seven sub-processes that "
     "correspond to the pipeline stages, together with the five data stores they read and "
     "write. The lower path, processes 5.0 to 7.0, is the explanation and serving path; the "
     "upper path, 1.0 to 4.0, is the forecasting path. Process 7.0 reads from both, which is "
     "what allows a single forecast and its audit to be served together."),
    ("figure", "design/dfd_level1.png", "Level 1 data-flow diagram", 15.4),
    ("h3", "Use Case Diagram"),
    ("p",
     "Two human actors use the system. An analyst selects a stock and a day and reads the "
     "forecast and its explanation. A researcher additionally exercises the audit functions, "
     "checking whether the explanation is faithful and whether LIME returns the same answer "
     "when re-run. The market data vendor is an external actor that supplies the prices from "
     "which the next-session forecast is built."),
    ("figure", "design/use_case.png", "Use case diagram", 13.4),
    ("h3", "Class Diagram"),
    ("p",
     "The system is organised as modules of functions rather than as a class hierarchy, "
     "which is the natural structure for a data pipeline; the only class defined is the HTTP "
     "request handler in the serving module. The diagram therefore shows the module "
     "structure, with each module's public functions and the modules it imports."),
    ("figure", "design/class_diagram.png",
     "Module structure, showing public functions and import dependencies", 15.4),
    ("p",
     "Two dependencies carry the design. Every module imports config, so the date ranges, "
     "the regime boundaries and the random seed exist in exactly one place. And the serving "
     "module imports the explanation functions from lime_explain rather than reimplementing "
     "them, which is what prevents the demonstration from drifting into a more flattering "
     "version of the study."),
    ("h3", "Sequence Diagram"),
    ("p",
     "The sequence below traces one request to the explanation endpoint. Nothing is read "
     "from a cached result file: the forecast, the SHAP attribution, the five LIME runs, the "
     "agreement statistics and the faithfulness probe are all computed while the request is "
     "being served, which takes about 0.7 seconds."),
    ("figure", "design/sequence.png",
     "Sequence diagram for a single request to the explanation endpoint", 15.4),
]


CH5 = [
    ("h2", "Module Description"),
    ("p",
     "The system consists of thirteen Python modules. Eleven form the pipeline; two generate "
     "the documents and diagrams. Modules are listed in execution order."),
    ("table", "Modules in execution order",
     ["Step", "Module", "Responsibility", "Output"],
     [["-", "config.py", "Paths, date ranges, regime boundaries, random seed. Imported by "
                         "every other module", "-"],
      ["1", "data.py", "Load the raw panel, repair the three defects, stack to one long table",
       "panel_clean.pkl"],
      ["2", "features.py", "Build the 32 features and the next-day targets; exposes "
                           "build(panel), the single feature definition", "features.pkl"],
      ["3", "tune.py", "Grid search on the validation year only", "tuning.json"],
      ["4", "train.py", "Walk-forward retraining and forecasting for the four test years",
       "predictions.pkl, models/"],
      ["5", "evaluate.py", "Return-space and price-space scoring, significance tests, decile "
                           "portfolio", "metrics.json"],
      ["6", "explain.py", "TreeSHAP attributions and the faithfulness, stability, sanity and "
                          "drift tests", "xai.json, importance.csv, shap_sample.pkl"],
      ["7", "lime_explain.py", "LIME explanations and the SHAP-against-LIME comparison",
       "lime.json"],
      ["8", "plots.py", "All 15 result figures", "results/figures/"],
      ["9", "live.py", "Retrain to the latest close and forecast the next session",
       "live_forecast.pkl, live_meta.json"],
      ["10", "app.py", "Serve the interactive forecast-and-audit page", "HTTP on port 8000"],
      ["-", "make_uml.py", "The six design diagrams of Chapter 4", "figures/design/"],
      ["-", "make_docx.py, make_vit_report.py", "Document generation", "Word output"]],
     [6, 22, 48, 24]),
    ("h3", "Target Formulation and Model"),
    ("p",
     "The model predicts the next-day log return, and the price forecast is that return "
     "applied to the current close. Predicting returns rather than price levels does two "
     "things. It lets one model serve stocks priced from ten dollars to three thousand, "
     "because a return is scale-free. And it avoids a structural failure of tree models on "
     "price levels: a tree predicts by averaging training labels, so it can never forecast "
     "above the highest price it was trained on. Section 7.1.2 quantifies what happens when "
     "that rule is broken."),
    ("p",
     "The regressor is a scikit-learn Random Forest with 300 trees, each grown on a 25 per "
     "cent bootstrap sample. Two hyperparameters were tuned: the minimum number of samples "
     "in a leaf, over 200, 1,000 and 5,000, and the fraction of features considered at each "
     "split, over 0.3 and 0.6. Selection was by validation mean squared error, with the "
     "model trained only on data preceding the validation period. The chosen configuration "
     "is a leaf size of 5,000 and a feature fraction of 0.3, the most heavily regularised "
     "option in the grid. That choice is itself a result: a search that lands on maximum "
     "regularisation is telling you the signal-to-noise ratio is very low."),
    ("h3", "Walk-Forward Protocol"),
    ("p",
     "At the start of each test year the model is retrained on every stock-day from March "
     "2013 up to the preceding 31 December, then forecasts every stock-day of that year. "
     "This mimics what a practitioner would actually do and guarantees that no forecast uses "
     "information from its own future."),
    ("table", "Walk-forward training and forecasting",
     ["Test year", "Training stock-days", "Forecasts produced", "Training time"],
     [["2019", "691,620", "119,340", "96 s"],
      ["2020", "810,960", "119,919", "120 s"],
      ["2021", "930,879", "119,448", "160 s"],
      ["2022 (to May)", "1,050,327", "46,838", "185 s"],
      ["Total", "-", "405,545", "561 s"]],
     [20, 28, 26, 18]),
    ("h3", "Baselines and Metrics"),
    ("p",
     "Five comparison models are scored on exactly the same stock-days: naive persistence, "
     "which forecasts zero return; historical drift, the mean training return; Ridge "
     "regression on the same 32 features; a Random Forest trained on raw price levels; and a "
     "Random Forest classifier for next-day direction. Every model produces one forecast, "
     "which is then scored twice, once on the return and once on the price."),
    ("p",
     "Return-space metrics are the primary result: mean absolute and root mean squared error "
     "in basis points, out-of-sample R-squared against both a zero-return and a drift "
     "benchmark, the daily information coefficient and its rank and ratio variants, "
     "directional accuracy, and the standard deviation of the forecasts themselves against "
     "the realised figure. Price-space metrics follow for comparability. An economic view "
     "sorts each day's stocks into deciles of predicted return and measures what each decile "
     "actually returned, reporting the long-short spread gross and net of an assumed ten "
     "basis point round-trip cost."),
    ("p",
     "Two significance tests are applied throughout. A Diebold-Mariano test with "
     "Newey-West standard errors over five lags compares daily mean squared error against "
     "the relevant benchmark. A binomial test compares directional accuracy against the rule "
     "of always predicting the majority direction, which is the benchmark a directional "
     "claim must actually beat."),
    ("h3", "Explanation Methods"),
    ("p",
     "TreeSHAP is applied through shap.TreeExplainer. For tree ensembles it computes exact "
     "Shapley values in time polynomial in tree depth, and it is additive by construction: "
     "the base value plus the 32 attributions equals the forecast. That additivity is "
     "verified rather than assumed, and the maximum observed error is 2.6 times ten to the "
     "minus seventeen, which is floating-point noise. The sample is 40 random stocks per "
     "test day plus AAPL, MSFT, JPM, XOM and PFE on every day, giving 38,183 stock-days, "
     "each explained by the model belonging to its own year."),
    ("p",
     "LIME is applied through lime.lime_tabular.LimeTabularExplainer with its default "
     "settings: quartile discretisation, 5,000 perturbed samples per explanation, and a "
     "reference distribution of 5,000 training rows. The sample is 804 stock-days, 200 per "
     "test year plus the cases examined individually, and each is explained five times with "
     "five different random seeds so that run-to-run variability can be measured. Two "
     "further explainers are computed for comparison: permutation importance, the increase "
     "in test mean squared error when a feature is shuffled, over three repeats; and mean "
     "decrease in impurity, the forest's own built-in importance."),
    ("h3", "The Reliability Audit"),
    ("table", "The five reliability checks and how each is measured",
     ["Check", "Applied to SHAP", "Applied to LIME"],
     [["Faithfulness",
       "Replace the top k features by absolute SHAP with values from 32 random training "
       "rows, for k in 1, 2, 4, 8, 16, 32; compare against random order; report deletion "
       "curves, AOPC and fidelity",
       "The same deletion test, ordered by absolute LIME weight"],
      ["Stability",
       "Five random seeds on identical data, and four consecutive yearly retrains; global "
       "Kendall tau and per-row Spearman rho",
       "The same stock-day explained with five LIME seeds"],
      ["Local fit", "Exact by construction, through additivity",
       "R-squared of LIME's own linear surrogate on its perturbation sample"],
      ["Agreement",
       "Global Kendall tau among all four explainers; per-row Spearman rho, top-5 overlap, "
       "same top feature and sign agreement", "The same statistics"],
      ["Sanity",
       "Forests trained on fully shuffled labels, and on labels shuffled within each day, "
       "compared against the real model", "Not applicable"],
      ["Drift",
       "Mean pairwise total variation distance between family-share vectors, against a null "
       "from 1,000 permutations of whole days or whole stocks", "Not applicable"]],
     [16, 44, 32]),
    ("p",
     "The four market regimes were fixed in advance from well-known market events, before "
     "any explanation was computed. This ordering matters: boundaries chosen after seeing "
     "which ones produced a significant result would make the drift test meaningless."),
    ("table", "Market regimes, fixed in advance",
     ["Regime", "From", "To", "Character"],
     [["Pre-COVID bull", "1 Jan 2019", "19 Feb 2020", "Steady rise to the pre-pandemic peak"],
      ["COVID crash", "20 Feb 2020", "23 Mar 2020", "23 trading days, index down about a third"],
      ["Recovery", "24 Mar 2020", "31 Dec 2021", "Sustained rally to new highs"],
      ["2022 bear", "1 Jan 2022", "24 May 2022", "Rate-driven decline"]],
     [20, 16, 16, 34]),

    ("h2", "Testing"),
    ("h3", "Acceptance Criteria"),
    ("p",
     "Eleven acceptance criteria were defined before the results were produced. Each is "
     "either met or not, and the evidence is a committed artifact."),
    ("table", "Acceptance criteria and outcomes",
     ["ID", "Criterion", "Outcome"],
     [["AC1", "Walk-forward forecasts exist for every test stock-day with no look-ahead",
       "Met: 405,545 forecasts"],
      ["AC2", "Return-space and price-space results are both reported, return space first",
       "Met: Section 7.1"],
      ["AC3", "Every accuracy claim carries a benchmark and a significance test",
       "Met: Diebold-Mariano and binomial throughout"],
      ["AC4", "SHAP additivity error below 1e-15", "Met: maximum 2.6e-17"],
      ["AC5", "Deletion of top-ranked features moves the forecast materially more than "
              "random deletion", "Met: 13.3 times at k = 1"],
      ["AC6", "Stability and sanity are both quantified",
       "Met: tau 0.85 across seeds; tau 0.13 against a no-signal model"],
      ["AC7", "Drift is tested statistically, not asserted",
       "Met: regimes p = 0.003, sectors p = 0.001"],
      ["AC8", "The pipeline reproduces from a clean checkout", "Met: 12 documented steps"],
      ["AC9", "Repeating a LIME explanation with the same seed returns identical weights",
       "Met after the defect in Section 5.3.3 was fixed; previously rho 0.46 to 0.53"],
      ["AC10", "A single forecast can be explained and audited interactively",
       "Met: about 0.7 s per stock-day, nothing served from cache"],
      ["AC11", "A forecast exists for a session that has not yet traded",
       "Met: 431 stocks, retrained on 1,473,486 stock-days, outcome fields blank"]],
     [8, 46, 38]),
    ("h3", "Correctness Checks Built Into the Pipeline"),
    ("p",
     "Rather than a separate test suite, correctness is enforced by assertions and "
     "invariants at the points where an error would be silent and damaging."),
    ("bullet", [
        "Price integrity. After cleaning, the day's high must be at least the maximum of "
        "open and close, and the low at most the minimum. This invariant is what exposed the "
        "twelve mis-adjusted tickers in the first place.",
        "SHAP additivity. The base value plus the 32 attributions is compared against the "
        "model's own prediction for every explained row, and the maximum deviation is "
        "reported in the run log.",
        "Leakage. Features are built on wide date-by-ticker tables where every shift is "
        "explicit, and the target is constructed by shifting the close backwards by one day, "
        "so a sign error would produce an implausibly high R-squared rather than a silent "
        "bias.",
        "Live forecasting. The live module asserts that the day being forecast has no known "
        "outcome. If the script is run while a session is still in progress the assertion "
        "fails and the run stops, rather than presenting a hindsight value as a forecast.",
        "Deletion control. The faithfulness test is always run against a random-order "
        "control on the same rows, so a result cannot be reported without its own null."]),
    ("h3", "A Defect Found by Testing: LIME Reproducibility"),
    ("p",
     "Enforcing NFR1 uncovered a defect in the conventional way LIME is used. The natural "
     "pattern is to construct one LimeTabularExplainer and reassign its random_state "
     "attribute between runs. The class, however, binds its RandomState into the discretiser "
     "and into the surrogate solver at construction time, so reassignment controls only part "
     "of the sampling. The consequence is that repeats which were intended to be identical "
     "were not: the measured Spearman correlation between two runs with the same seed was "
     "0.46 to 0.53, where it should have been exactly 1.000."),
    ("code",
     "# Wrong: the explainer binds its RandomState at construction, so the same seed\n"
     "# does not reproduce the same explanation.\n"
     "explainer.random_state = seed\n"
     "weights = explainer.explain_instance(x, predict).as_map()\n"
     "\n"
     "# Correct: build a fresh explainer per seed. Costs 18 ms; repeats are bit-identical.\n"
     "explainer = LimeTabularExplainer(reference, random_state=seed, ...)\n"
     "weights = explainer.explain_instance(x, predict).as_map()"),
    ("p",
     "The defect mattered because it inflated a headline result. Before the fix the global "
     "agreement between TreeSHAP and LIME read Kendall tau 0.73; after it, tau 0.58. The "
     "higher figure was partly an artefact of LIME not being reproducible across runs that "
     "were supposed to be identical. A reliability study that does not audit its own tooling "
     "can report the inflated number without ever seeing the problem, which is itself a "
     "finding of this project."),
]


CH6 = [
    ("p",
     "Every number in Chapter 7 comes from forecasting days whose outcome is already known. "
     "That is not a weakness of the design; it is the only way a forecast can be scored. An "
     "out-of-sample R-squared of plus 0.00013 cannot be established unless 405,545 forecasts "
     "have been compared against what actually happened."),
    ("p",
     "It does leave one question open. Does the pipeline work on a day that has not yet "
     "happened? A backtest can be made to look good by construction, through a feature that "
     "leaks, a universe chosen after the fact, or hyperparameters tuned on the test period. "
     "Running the identical code forward on data that did not exist when the code was "
     "written removes all three possibilities at once. This chapter describes that "
     "demonstration."),

    ("h2", "Live Forecasting"),
    ("p",
     "The live module downloads current prices for the study's tickers from Yahoo Finance, "
     "rebuilds the 32 features by calling the same features.build function used in the "
     "study, retrains a Random Forest with the hyperparameters already selected, and "
     "forecasts the next trading session. The only substantive difference from the study "
     "path is one line: the study discards every row with a missing target, which "
     "necessarily throws away the most recent day, whereas the live path keeps it precisely "
     "because its outcome is unknown."),
    ("code",
     'df = df.dropna(subset=FEATURES + ["close"])   # NOT on the target: the last day has none\n'
     'train = df.dropna(subset=["target_ret"])      # train on every day with a known outcome\n'
     'live  = df[df.date == last_day].copy()        # forecast the one day with no outcome\n'
     'assert live.target_ret.isna().all(), "the last day already has a known outcome"'),
    ("p",
     "The assertion guards against the most tempting error in a demonstration of this kind. "
     "If the script is run while a session is still in progress, the last available day "
     "already has an outcome, and the script stops rather than presenting a hindsight value "
     "as a forecast."),
    ("table", "A representative live run, as of the close of 29 October 2026",
     ["Quantity", "Value"],
     [["Stocks forecast", "431"],
      ["Training rows", "1,473,486 stock-days, through 28 October 2026"],
      ["Hyperparameters", "Unchanged from the study: 300 trees, leaf 5,000, feature fraction 0.3"],
      ["Price source", "Yahoo Finance via yfinance, split- and dividend-adjusted"],
      ["Tickers no longer trading", "43 of the original 474"]],
     [26, 56]),
    ("p",
     "Three caveats are reported by the system itself rather than left to the reader. "
     "Forty-three of the original tickers have been acquired, merged or delisted, so the "
     "live universe is smaller than the study universe and the market-context features are "
     "computed over the survivors. That is survivorship bias made visible rather than "
     "hidden. The prices come from a different vendor than the study panel; both are "
     "adjusted, but they are not the same series. And nothing in the live output is scored, "
     "because the outcome does not exist yet: the live mode demonstrates that the mechanism "
     "runs forward, not that it is accurate."),

    ("h2", "The Interactive Demonstration"),
    ("p",
     "The serving module presents a single page from the Python standard library's threading "
     "HTTP server. It loads the four walk-forward models, a TreeSHAP explainer for each, the "
     "LIME reference samples, the cleaned price history and, when present, the live forecast "
     "and its retrained model."),
    ("table", "Endpoints exposed by the demonstration",
     ["Endpoint", "Returns"],
     [["GET /api/meta", "Ticker list, date range, suggested cases, live metadata"],
      ["GET /api/dates?ticker=...", "The dates on which that stock can be explained"],
      ["GET /api/explain?ticker=...&date=...",
       "Forecast, SHAP attributions, five LIME runs, agreement statistics, faithfulness probe"]],
     [34, 48]),
    ("p",
     "Two design decisions carry the credibility of the demonstration. Nothing is served "
     "from a cached result file: each request runs TreeSHAP once and LIME five times, on the "
     "saved model, at request time, so the page shows what the pipeline produces rather than "
     "a transcription of the results chapter. And the live and historical paths share one "
     "function, which differs between the two modes only in which model and which feature "
     "row it selects. The TreeSHAP call, the five LIME runs, the agreement statistics and "
     "the faithfulness probe are the same lines of code in both cases, so the demonstration "
     "cannot drift into being a more flattering version of the study."),

    ("h2", "Input and Output"),
    ("p",
     "The user supplies two values: a stock, from 474 in historical mode or 431 in live "
     "mode, and either a trading day between 2 January 2019 and 24 May 2022 or the next "
     "session. The page returns seven things."),
    ("num", [
        "The forecast. Predicted next-day return in basis points, the implied close in "
        "dollars, and the classifier's probability that the day is up. In historical mode "
        "the realised return and close appear beside it, with the direction marked correct "
        "or incorrect.",
        "The forecast in context. The last 60 closes, a dashed segment to the forecast, and "
        "a shaded band of one standard deviation of that stock's recent daily moves. The "
        "band is the point of the chart: for AAPL on 29 October 2026 the forecast is minus "
        "4.05 basis points against a band of plus or minus 87, so the model predicts a move "
        "about 22 times smaller than a normal day.",
        "A SHAP waterfall. The base value, then the top eight contributions in turn, then "
        "the remaining 24 features as one bar, ending exactly on the forecast. The exactness "
        "is the demonstration of additivity: the bars do not illustrate the forecast, they "
        "sum to it.",
        "Both explanations. SHAP and LIME bar charts of the same forecast side by side, plus "
        "a table of all 32 features with both attributions in basis points.",
        "Agreement. Spearman rho between the two attribution vectors, top-5 overlap, whether "
        "they name the same top feature, and sign agreement on SHAP's top five.",
        "Stability. The top feature from each of five LIME runs with different seeds, the "
        "mean Spearman between runs, and the median surrogate fit. TreeSHAP is labelled "
        "deterministic, because re-running it returns identical values.",
        "Faithfulness. The change in the forecast when SHAP's top feature is deleted, the "
        "mean change for eight random features, and the ratio between them."]),
    ("p",
     "The five preset cases are chosen to show both outcomes of the SHAP-against-LIME "
     "comparison: two stock-days where the explainers agree, and two where they name a "
     "different top feature, which happened on 41 per cent of the sampled stock-days, "
     "including one where LIME contradicts its own re-runs."),

    ("h2", "Guards Against Overclaiming"),
    ("p",
     "The demonstration is the part of this project most likely to be mistaken for a trading "
     "system, so three guards are built into it."),
    ("bullet", [
        "The live forecast carries its age. The server computes how many days have passed "
        "since the close the forecast was made from, and the page displays a warning beyond "
        "three days, because a forecast for a session that has already traded is no longer a "
        "forecast.",
        "The 43 delisted tickers are listed on the page rather than silently dropped.",
        "The page states that the forecast has an out-of-sample R-squared of plus 0.00013 "
        "across 405,545 scored forecasts. The live mode demonstrates that the mechanism "
        "works; Chapter 7 remains the statement of how well it works."]),
]


CH7 = [
    ("h2", "RQ1: Forecast Skill"),
    ("p",
     "The model predicts a next-day log return, and the price forecast is only that return "
     "applied to the current close. Skill is therefore measured on returns first. "
     "Price-space accuracy follows, because that is what the literature quotes, and the "
     "distance between the two verdicts is itself the first result of this project."),
    ("h3", "Return Space"),
    ("p",
     "Across 405,545 stock-days from January 2019 to May 2022, the realised next-day return "
     "has a standard deviation of 245 basis points."),
    ("table", "Return-space skill. One basis point is one hundredth of one per cent",
     ["Model", "RMSE (bp)", "R2 vs zero", "R2 vs drift", "Daily IC (t)", "Direction", "DM p"],
     [["Naive, forecast zero return", "245.5", "0.00000", "-0.00043", "-", "47.2%", "-"],
      ["Historical drift", "245.5", "+0.00043", "0.00000", "-", "52.8%", "0.64"],
      ["Ridge regression", "246.9", "-0.01076", "-0.01120", "+0.0019 (0.30)", "51.7%", "0.39"],
      ["RF on price levels", "250.4", "-0.03972", "-0.04016", "+0.0063 (2.24)", "50.8%",
       "<0.001 worse"],
      ["Random Forest (proposed)", "245.5", "+0.00013", "-0.00030", "+0.0090 (1.39)", "51.8%",
       "0.97"],
      ["Majority-direction rule", "-", "-", "-", "-", "52.8%", "-"]],
     [24, 11, 12, 12, 14, 13, 14]),
    ("p",
     "The proposed model explains 0.013 per cent of next-day return variance, and the "
     "Diebold-Mariano test cannot distinguish it from simply predicting zero, at p = 0.97. "
     "Against the slightly stronger drift benchmark the sign flips. Directional accuracy of "
     "51.8 per cent is below the 52.8 per cent achieved by always predicting the majority "
     "direction, and the binomial test returns p = 1.00."),
    ("p",
     "The model hedges towards zero. Its forecasts have a standard deviation of 10.8 basis "
     "points against a realised 245, a range 23 times narrower than reality. That is the "
     "statistically correct response to a near-unpredictable target, and it is precisely why "
     "the price forecasts in the next section look so good. The price-level Random Forest is "
     "the only model significantly different from the benchmark, and it is worse: training a "
     "tree on raw price levels actively destroys return information."),
    ("figure", "return_skill.png",
     "Return-space skill: out-of-sample R-squared on the next-day return and directional "
     "accuracy, by model"),
    ("h3", "Price Space"),
    ("p", "The same forecasts, scored on the next-day closing price:"),
    ("table", "Price-space accuracy, the quantity usually reported in the literature",
     ["Model", "MAPE", "Accuracy (100 - MAPE)", "RMSE", "R2 (price)", "Within 2%", "DM p"],
     [["Naive, tomorrow equals today", "1.561%", "98.44%", "$6.25", "0.99938", "75.3%", "-"],
      ["Historical drift", "1.560%", "98.44%", "$6.25", "0.99938", "75.4%", "0.25"],
      ["Ridge regression", "1.567%", "98.43%", "$6.27", "0.99937", "75.3%", "0.17"],
      ["RF on price levels", "1.583%", "98.42%", "$21.56", "0.99261", "75.0%", "<0.001 worse"],
      ["Random Forest (proposed)", "1.560%", "98.44%", "$6.25", "0.99938", "75.4%", "0.30"]],
     [28, 11, 18, 11, 13, 12, 14]),
    ("table", "The same model, two verdicts",
     ["Scored on", "R-squared", "Reading"],
     [["The price level", "0.9994", "A near-perfect forecaster"],
      ["The next-day return", "+0.00013", "Indistinguishable from predicting no change"]],
     [26, 18, 48]),
    ("p",
     "Both numbers come from one set of forecasts. Price-space R-squared is high because "
     "tomorrow's price is almost today's price, so the denominator, the variance of the "
     "price level across stocks and months, is enormous compared with the one-day error. It "
     "measures the price level, not the forecast. The figure of 98.44 per cent accuracy is a "
     "property of daily stock prices rather than an achievement of the model, and naive "
     "persistence matches it to three decimal places."),
    ("p",
     "The price-level Random Forest demonstrates the second failure mode. It reports an "
     "R-squared of 0.993 and 98.4 per cent accuracy, yet its root mean squared error is 3.4 "
     "times that of naive persistence and it is significantly worse on the Diebold-Mariano "
     "test. Its error grows from six dollars in 2019 to thirty-six dollars in 2021 as prices "
     "trend to new highs, because a tree cannot predict above the range it was trained on."),
    ("figure", "price_vs_return.png",
     "The same forecasts scored on the price level and on the return, and how narrowly the "
     "forecasts move"),
    ("figure", "price_accuracy.png",
     "Next-day price error and the share of forecasts within two per cent, by model"),
    ("figure", "price_paths_AAPL.png",
     "AAPL one-day-ahead forecasts against actual closing prices"),
    ("h3", "Economic View and Cost Analysis"),
    ("p",
     "Sorting each day's stocks by predicted return and measuring what each decile actually "
     "returned gives the economic reading of the same forecasts."),
    ("table", "Mean actual next-day return by decile of predicted return, in basis points",
     ["Decile", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
     [["Actual return (bp)", "+1.3", "+6.2", "+3.8", "+5.2", "+6.2", "+4.6", "+5.8", "+6.4",
       "+6.4", "+9.5"]],
     [22, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]),
    ("p",
     "The ranking is weakly monotone, with a Spearman correlation of 0.75 across deciles, so "
     "the forecasts do carry a little cross-sectional information even though their level is "
     "uninformative. The long-short spread between the top and bottom deciles is 8.2 basis "
     "points a day, with a t-statistic of 1.53 and an annualised Sharpe ratio of 0.83, which "
     "is not statistically significant."),
    ("p",
     "The cost analysis is decisive. A long-short decile strategy turns over its entire book "
     "daily. At an assumed ten basis point round-trip cost the strategy returns minus 1.8 "
     "basis points a day: it loses money. Because slippage, market impact, borrowing costs "
     "and capacity are not modelled, this figure is an optimistic bound rather than a "
     "backtest. The honest economic conclusion is that the model has no demonstrated "
     "commercial value."),
    ("figure", "decile_portfolio.png",
     "Actual next-day return of each decile of predicted return, with the long-short spread "
     "gross and net of cost"),
    ("h3", "Where the Little Skill There Is Actually Lives"),
    ("table", "Skill by period and market regime",
     ["Period", "RMSE (bp)", "R2 vs zero", "DM p", "Daily IC", "Direction", "Majority rule",
      "Long-short (bp)"],
     [["2019", "164.0", "+0.00212", "0.63", "+0.014", "53.5%", "55.3%", "-"],
      ["2020", "348.0", "-0.00016", "0.98", "+0.018", "51.0%", "51.8%", "-"],
      ["2021", "182.0", "+0.00046", "0.87", "-0.008", "50.4%", "53.2%", "-"],
      ["2022 to May", "242.5", "-0.00113", "0.91", "+0.018", "52.7%", "51.5%", "-"],
      ["Pre-COVID bull", "164.4", "+0.00069", "0.87", "+0.015", "53.0%", "55.2%", "+6.9"],
      ["COVID crash", "766.3", "-0.01171", "0.13", "-0.073", "34.7%", "65.8% down", "-119.0"],
      ["Recovery", "233.9", "+0.00665", "0.043", "+0.008", "51.6%", "53.3%", "+16.1"],
      ["2022 bear", "242.5", "-0.00113", "0.91", "+0.018", "52.7%", "51.5%", "+5.6"]],
     [16, 11, 12, 8, 10, 10, 13, 13]),
    ("p",
     "Two findings here are visible only in return space. The recovery is the one period "
     "with detectable skill: from March 2020 to December 2021 the model beat a zero-return "
     "forecast significantly, with an R-squared of plus 0.0067 at p = 0.043, and its "
     "long-short spread earned 16.1 basis points a day. In price space that period looks no "
     "different from any other. The crash is where the model was actively wrong: directional "
     "accuracy fell to 34.7 per cent, the daily information coefficient turned negative, and "
     "the long-short spread lost 119 basis points a day, because the model kept forecasting "
     "small rebounds while two thirds of stock-days fell. A user would have relied on it most "
     "at exactly the moment it inverted."),
    ("p",
     "By sector, return R-squared runs from plus 0.0028 in Information Technology to minus "
     "0.0009 in Consumer Discretionary, and the daily information coefficient from plus "
     "0.025 in Energy to minus 0.016 in Real Estate. All of this is within noise, but none "
     "of it is visible in price space, where mean absolute percentage error differs by less "
     "than 0.004 percentage points between the model and naive persistence in every sector."),

    ("h2", "RQ2: What Drives the Forecasts"),
    ("table", "Global feature importance, by mean absolute SHAP",
     ["Rank", "Feature", "Family", "Mean |SHAP| (bp)"],
     [["1", "Market 20-day volatility", "Market and sector", "5.37"],
      ["2", "Market 5-day return", "Market and sector", "3.33"],
      ["3", "Market 1-day return", "Market and sector", "3.28"],
      ["4", "Overnight gap", "Candle", "0.77"],
      ["5", "Own 1-day return", "Past returns", "0.57"],
      ["6", "Sector 5-day return", "Market and sector", "0.53"],
      ["7", "ATR(14)", "Volatility", "0.43"]],
     [10, 34, 26, 22]),
    ("p",
     "Market and sector context accounts for 72.2 per cent of total attribution. The "
     "remaining families divide the rest: volatility 7.6 per cent, past returns 7.0 per "
     "cent, candle 5.9 per cent, trend 3.8 per cent, oscillators 2.0 per cent and volume 1.5 "
     "per cent. The dependence plots show what those features do. High market volatility "
     "raises the forecast by 10 to 15 basis points, a falling five-day market raises it by "
     "up to 25, and a strong up-day for the market lowers it. The model has mainly learned "
     "one rule: expect a small market-wide rebound after a volatile sell-off."),
    ("figure", "shap_global.png", "Top 15 features by mean absolute SHAP"),
    ("figure", "shap_dependence.png",
     "How the leading features move the forecast (SHAP dependence)"),
    ("p",
     "A local example makes the scale concrete. For AAPL on 16 March 2020, the worst day of "
     "the COVID crash, the model forecast plus 30 basis points while the stock actually rose "
     "430. The attribution pushing the forecast up was market 20-day volatility at plus 12.9 "
     "basis points, the 17.8 per cent five-day market fall at plus 7.4, and the stock's own "
     "29 per cent 20-day decline at plus 1.9; pushing it down were the 13.7 per cent market "
     "fall that day at minus 2.2 and the overnight gap at minus 1.7. The explanation is "
     "coherent, and the direction is right. But every contribution is an order of magnitude "
     "too small, which is the local view of the same 23-times-too-narrow dispersion found in "
     "Section 7.1.1. Expressed in dollars those contributions would read as eight, four and "
     "one cents and look merely small; in return units it is clear that the whole "
     "explanation accounts for one fourteenth of the move."),
    ("figure", "local_explanations.png",
     "Local SHAP explanations in basis points of forecast return, for individual stock-days"),

    ("h2", "RQ3: Faithfulness and Stability"),
    ("table", "Faithfulness: forecast change when k features are removed",
     ["Features removed (k)", "1", "2", "4", "8", "16", "32"],
     [["Top-SHAP first, |change| in bp", "8.70", "8.39", "8.36", "8.47", "8.56", "8.59"],
      ["Random order, |change| in bp", "0.65", "1.19", "2.04", "3.65", "5.88", "8.59"],
      ["Fidelity: corr(SHAP mass removed, actual change)", "0.98", "0.99", "0.99", "1.00",
       "1.00", "1.00"]],
     [40, 7, 7, 7, 7, 7, 7]),
    ("p",
     "SHAP passes. Removing the single top-ranked feature changes a forecast 13 times more "
     "than removing a random one, with an area over the perturbation curve of 8.51 basis "
     "points against 3.67 for random order, and the fidelity correlation is at least 0.98 "
     "throughout. The two curves necessarily meet at k = 32, because replacing all 32 "
     "features gives the same answer whatever order is used."),
    ("p",
     "A second finding falls out of the same table. The top-SHAP row is almost flat: "
     "removing one feature moves the forecast as much as removing sixteen. One feature does "
     "nearly all the work, which is a fact about the model that the explanation alone would "
     "not have revealed."),
    ("figure", "faithfulness.png",
     "Faithfulness: forecast change when top-SHAP features and random features are removed"),
    ("table", "Stability of the explanations",
     ["Comparison", "Global ranking tau", "Top-5 overlap", "Per-stock-day rho"],
     [["Five random seeds, same data", "0.85", "92%", "0.86"],
      ["2019 against 2020 model", "0.75", "80%", "0.73"],
      ["2020 against 2021 model", "0.44", "100%", "0.57"],
      ["2021 against 2022 model", "0.77", "80%", "0.77"]],
     [34, 20, 16, 22]),
    ("p",
     "The explanations are stable to the random seed, with a forecast correlation between "
     "seeds of 0.99, but noticeably less stable to retraining. Once 2020 enters the training "
     "data, agreement with the previous year's model drops to tau 0.44. The top five "
     "features stay the same; the other 27 reorder. An explanation produced before the "
     "pandemic would not have survived it."),
    ("figure", "stability_sanity.png",
     "Stability across seeds and retraining, and comparison with no-signal models"),

    ("h2", "RQ4: Regime and Sector Drift"),
    ("p",
     "Explanations drift significantly across market regimes: the mean pairwise total "
     "variation distance between family-share vectors is 0.054 against a permutation null of "
     "0.017, giving p = 0.003."),
    ("table", "Share of SHAP attribution by feature family across market regimes",
     ["Family", "Pre-COVID bull", "COVID crash", "Recovery", "2022 bear"],
     [["Market and sector", "71.2%", "74.7%", "71.7%", "74.7%"],
      ["Volatility", "5.1%", "5.9%", "8.3%", "9.2%"],
      ["Past returns", "8.7%", "7.2%", "6.5%", "6.0%"],
      ["Trend", "4.6%", "5.9%", "3.7%", "2.3%"],
      ["Candle", "6.3%", "4.1%", "6.2%", "4.9%"],
      ["Oscillators", "2.4%", "1.5%", "2.1%", "1.2%"],
      ["Volume", "1.7%", "0.7%", "1.4%", "1.7%"]],
     [28, 20, 18, 18, 16]),
    ("p",
     "Volatility's share nearly doubles from the pre-COVID bull to the 2022 bear, past "
     "returns fade, and trend peaks during the crash. The feature ranking reorders with "
     "them: rank correlation falls to 0.46 between the COVID crash and the 2022 bear, "
     "against 0.84 between the pre-COVID bull and the crash. The top three market features "
     "never change."),
    ("figure", "regime_family_shares.png",
     "Share of SHAP attribution by feature family across market regimes"),
    ("p",
     "Sector drift is also significant but smaller, at a total variation distance of 0.036 "
     "against a null of 0.011, giving p = 0.001. Volatile sectors use more volatility "
     "features, with Energy at 10.4 per cent, Consumer Discretionary at 9.5 and "
     "Communication Services at 9.4. Defensive sectors rely more on market context, with "
     "Utilities at 76.1 per cent and Consumer Staples at 76.4, against Energy at 66.8."),
    ("figure", "sector_family_shares.png",
     "Share of SHAP attribution by feature family and GICS sector"),

    ("h2", "RQ5: Sanity Against No-Signal Models"),
    ("table", "Comparison with models trained on shuffled labels",
     ["Model trained on", "Test IC", "Total mean |SHAP| (bp)", "Market share", "tau vs real",
      "Per-row rho"],
     [["Real labels", "+0.018", "20.8", "77.3%", "-", "-"],
      ["Fully shuffled labels", "-0.023", "2.6", "19.6%", "0.13", "0.13"],
      ["Labels shuffled within each day", "+0.011", "19.5", "84.5%", "0.56", "0.60"]],
     [30, 12, 20, 14, 14, 12]),
    ("p",
     "The explanations pass the sanity check. A model trained on fully shuffled labels, "
     "which by construction has no signal to learn, produces explanations eight times weaker "
     "and essentially unrelated to the real model's, at tau 0.13."),
    ("p",
     "The second null is the more interesting one. Shuffling returns within each day "
     "destroys all stock-specific information while preserving the market-wide daily move. A "
     "model trained on that reproduces 94 per cent of the real explanation magnitude and tau "
     "0.56 of its ranking. The real model's explanations are therefore mostly, though not "
     "entirely, about market-wide timing. Without this second null the first would have "
     "supported a stronger claim than the evidence allows."),

    ("h2", "RQ6: SHAP Against LIME"),
    ("table", "Global agreement between four explainers, Kendall tau with top-5 overlap",
     ["", "LIME", "Permutation importance", "MDI"],
     [["TreeSHAP", "0.58 (4/5)", "0.03 (3/5)", "0.69 (4/5)"],
      ["LIME", "-", "0.18 (3/5)", "0.65 (4/5)"],
      ["Permutation importance", "-", "-", "0.15 (4/5)"]],
     [30, 20, 30, 20]),
    ("p",
     "Globally, SHAP and LIME agree moderately, sharing four of their top five features, and "
     "both agree with mean decrease in impurity more closely than with each other. All three "
     "disagree with permutation importance. Only four of the 32 features measurably improve "
     "accuracy, in the sense of a permutation importance more than two standard deviations "
     "above zero: market volatility, sector five-day return, Bollinger width and volume "
     "trend. Fifteen have negative permutation importance. The meaning is that SHAP and LIME "
     "describe what the model uses, not what improves accuracy, and those are different "
     "questions."),
    ("figure", "explainer_agreement.png",
     "Feature importance ranks from TreeSHAP, LIME, permutation importance and MDI"),
    ("table", "Reliability for individual forecasts, over 804 stock-days with five LIME seeds each",
     ["Measure", "TreeSHAP", "LIME"],
     [["Agreement with the other method, median Spearman rho", "-", "0.44"],
      ["Agreement, top-5 feature overlap", "-", "65%"],
      ["Agreement, same top feature", "-", "59%"],
      ["Agreement, sign matches on SHAP's top five", "-", "81%"],
      ["Run-to-run stability, median rho between runs", "1.00 (deterministic)", "0.45"],
      ["Run-to-run stability, top-5 overlap", "1.00", "79%"],
      ["Run-to-run stability, same top feature in all five runs", "100%", "96%"],
      ["Local fit, surrogate R-squared", "Exact by additivity",
       "Median 0.17; 67% below 0.3"],
      ["Faithfulness AOPC in bp, random order being 3.71", "8.70", "8.13"],
      ["Faithfulness, |change| after removing the top feature, random being 0.56 bp",
       "8.89", "6.53"],
      ["Time per explanation", "About 0.001 s", "About 0.08 s"]],
     [46, 20, 24]),
    ("p",
     "LIME is less reliable than SHAP for individual forecasts on three counts. Explaining "
     "the same forecast twice with different seeds gives feature rankings that correlate "
     "only 0.45. Its linear surrogate explains a median of just 17 per cent of the model's "
     "local behaviour, and two thirds of its explanations fall below an R-squared of 0.3. "
     "And on a typical forecast it shares only three of its top five features with SHAP."),
    ("p",
     "Both methods are faithful, SHAP more so: both beat random ordering comfortably, but "
     "removing LIME's top feature changes the forecast 27 per cent less than removing "
     "SHAP's. The two can also contradict each other on the same forecast. For AAPL on 16 "
     "March 2020 they agree on the two main drivers, with a rho of 0.53. For JPM on 18 May "
     "2022 they disagree on the direction of the top feature: market volatility pushes the "
     "forecast down according to SHAP and up according to LIME, with a rho of 0.19 and a "
     "LIME surrogate fit of 0.11. The cause is structural. LIME's discretised bins compare "
     "against the whole training distribution, while SHAP attributes along the model's own "
     "decision paths."),
    ("figure", "lime_vs_shap_local.png", "SHAP against LIME explanations for the same forecasts"),
    ("figure", "lime_reliability.png",
     "LIME against SHAP: run-to-run stability, faithfulness and local fit"),

    ("h2", "Discussion"),
    ("h3", "Score the Change, Not the Level"),
    ("p",
     "One set of forecasts scores an R-squared of 0.9994 on the price and plus 0.00013 on "
     "the return. The first number is a property of daily stock prices, matched exactly by "
     "naive persistence; only the second says anything about the model. The forecasts "
     "themselves vary by 10.8 basis points against a realised 245, which is the model "
     "correctly refusing to commit, and that refusal is what produces the flattering price "
     "figures. A price-level Random Forest with an R-squared of 0.993 is significantly worse "
     "than naive persistence in both spaces. Accuracy claims reported in price units without "
     "a persistence baseline cannot be interpreted at all. Return space also localises what "
     "little skill exists, to the 2020 to 2021 recovery, and reveals that the model inverted "
     "during the crash; neither fact is visible in the price-space numbers."),
    ("h3", "Faithful Does Not Mean the Market Insight Is Real"),
    ("p",
     "SHAP is faithful, seed-stable and passes the sanity check. Yet SHAP, LIME and mean "
     "decrease in impurity all disagree with permutation importance. The resolution is that "
     "explanations describe how the model computes its forecast, not which relationships "
     "actually predict prices. A faithful explanation of a model with no skill is a faithful "
     "explanation of nothing useful. Presenting SHAP or LIME rankings as market insight, as "
     "papers 1 and 3 do, conflates the two."),
    ("h3", "For Tree Models, Prefer SHAP to a Single LIME Run"),
    ("p",
     "LIME agrees with SHAP only moderately even globally, is unstable for individual "
     "forecasts, fits the local behaviour poorly, and can flip a feature's sign. A study "
     "reporting a single LIME explanation per case, as paper 3 does, risks reporting noise. "
     "The practical recommendation is to use TreeSHAP for tree models, which is exact and "
     "deterministic, and to keep LIME as a cross-check that is re-run several times before "
     "anything is concluded from it."),
    ("h3", "Explanations Are Period and Sector Specific"),
    ("p",
     "Regime drift at p = 0.003, sector drift at p = 0.001, and the fall in agreement after "
     "retraining on pandemic data together mean that an explanation from one period should "
     "not be generalised to another. This turns Pagliaro's qualitative regime observation "
     "into a formal test on 474 stocks."),

    ("h2", "Limitations"),
    ("bullet", [
        "Data. Price and volume only, with no news, fundamentals or macroeconomic inputs; "
        "the study panel ends in May 2022; and the 474 stocks were index constituents when "
        "the dataset was built, which is a survivorship bias.",
        "Explanation methods. TreeSHAP uses the path-dependent algorithm, and interventional "
        "SHAP could differ where features are correlated. LIME uses its default quartile "
        "discretisation and 5,000 samples; other settings could change its stability.",
        "The faithfulness test replaces features with values drawn from random training "
        "rows, which can create feature combinations that would not occur in the market.",
        "Regimes are calendar-defined, and the COVID crash contains only 23 trading days, so "
        "that regime's estimates are the least precise.",
        "The decile portfolio charges one flat ten basis point round-trip cost and ignores "
        "slippage, market impact, shorting costs and capacity, so the net figure of minus "
        "1.8 basis points a day is an optimistic bound rather than a backtest.",
        "The live demonstration draws prices from a different vendor, covers the 431 "
        "survivors of the original 474, and scores nothing, because the outcomes do not "
        "exist yet. It evidences that the pipeline runs forward; it is not additional "
        "evidence of accuracy.",
        "Literature gaps are stated from abstracts and publicly available details, and "
        "should be verified against the full texts."]),
]


CH8 = [
    ("h2", "Conclusion"),
    ("p",
     "This project built a walk-forward Random Forest forecaster for 474 S&P 500 stocks, "
     "measured it honestly, explained it with SHAP and LIME, and then tested whether those "
     "explanations could be trusted. The conclusions fall into three groups."),
    ("h3", "On Accuracy"),
    ("p",
     "The model predicts the next-day return with an out-of-sample R-squared of plus "
     "0.00013, statistically indistinguishable from predicting no change at all, and a "
     "directional accuracy of 51.8 per cent, below the 52.8 per cent majority rule. "
     "Converted to prices, the identical forecasts read as 98.44 per cent accuracy with an "
     "R-squared of 0.9994, a figure naive persistence matches exactly. The decile ranking "
     "earns 8.2 basis points a day gross and loses money after a ten basis point trading "
     "cost. The headline accuracy figure quoted throughout this literature is, on this "
     "evidence, a property of daily stock prices rather than a result."),
    ("h3", "On the Explanations"),
    ("bullet", [
        "SHAP explanations are faithful, with a fidelity correlation of at least 0.98 and a "
        "13-fold separation from random deletion, and stable to the random seed at tau 0.85.",
        "They are clearly different from the explanations of a model with no signal, but a "
        "model that can learn only market-wide timing reproduces 94 per cent of their "
        "magnitude, so they are mostly about market context.",
        "They drift significantly across market regimes and sectors, and after retraining on "
        "pandemic data.",
        "LIME agrees with SHAP only moderately even globally, is unstable between runs at "
        "rho 0.45, fits the model poorly at a median surrogate R-squared of 0.17, and names "
        "a different top feature on 41 per cent of forecasts.",
        "Neither method identifies the features that actually improve accuracy, which is a "
        "different question from the one either method answers."]),
    ("h3", "On the Audit Itself"),
    ("p",
     "The audit found a defect in the audit tool. LimeTabularExplainer binds its random "
     "state at construction, so the natural usage pattern of reassigning that attribute "
     "between runs leaves repeats non-identical, at a measured rho of 0.46 to 0.53 where it "
     "should be exactly 1.000. Correcting it moved the headline SHAP-LIME agreement from tau "
     "0.73 down to tau 0.58. A reliability study that does not check its own tooling can "
     "report the inflated figure without ever seeing the problem."),
    ("p",
     "Finally, the pipeline runs forward. The same features, hyperparameters and explanation "
     "code produce next-session forecasts for 431 currently traded stocks, explained and "
     "audited at request time. This demonstrates that no step depends on knowing the "
     "outcome. It does not improve the accuracy reported above, and the system says so on "
     "the page."),

    ("h2", "Recommendations for Stock-Forecasting Studies"),
    ("num", [
        "Benchmark accuracy against naive persistence, and report the benchmark's score "
        "beside the model's.",
        "Report skill in return space, and treat price-level R-squared and accuracy "
        "percentages as descriptive statistics of the price series rather than as results.",
        "Prefer TreeSHAP to single LIME runs for tree models, and re-run LIME several times "
        "before drawing any conclusion from it.",
        "Test explanations for faithfulness, stability, sanity and regime drift before "
        "reading them as market insight.",
        "Seed and verify the explanation tooling itself, because a defect there is "
        "indistinguishable from a finding."]),

    ("h2", "Future Work"),
    ("bullet", [
        "Extend the audit to interventional SHAP, which handles correlated features "
        "differently from the path-dependent algorithm used here, and compare the two "
        "rankings on the same forecasts.",
        "Replace the random-background deletion test with one that samples feature values "
        "conditionally, so that the perturbed inputs remain plausible market states.",
        "Apply the same five-part audit to a gradient-boosted model and to a neural "
        "forecaster, to establish whether the reliability ordering between SHAP and LIME is "
        "a property of the explainers or of the model family.",
        "Define market regimes by a fitted change-point or hidden Markov model rather than "
        "by calendar boundaries, which would remove the dependence on hindsight in regime "
        "selection.",
        "Extend the feature set to news and fundamental data, and test whether explanation "
        "drift across regimes narrows once the model has access to the information that "
        "drives those regimes.",
        "Accumulate the live forecasts over a sustained period so that, in time, the "
        "forward-running pipeline produces a scored out-of-sample record of its own."]),
]


REFERENCES = [
    'S. Indra, S. Supian, Sukono, R. Riaman, M. P. A. Saputra, A. S. Azahra, and D. I. '
    'Pirdaus, "Stock return prediction on the LQ45 market index in the Indonesia Stock '
    'Exchange using a machine learning algorithm based on technical indicators," Journal of '
    'Risk and Financial Management, vol. 18, no. 12, 714, 2025. doi: 10.3390/jrfm18120714.',

    'J. Lee and L. Cai, "Comparing model-specific and model-agnostic feature importance '
    'methods using machine learning with technical indicators: A NASDAQ sector-based study," '
    'Machine Learning with Applications, 2025. doi: 10.1016/j.mlwa.2025.100799.',

    'K. W. Manikrao, S. Allagi, W. Y. Leong, and M. Laddi, "An explainable AI for stock '
    'market prediction: A machine learning approach with XAI and deep neural networks," '
    'Journal of Computational and Cognitive Engineering, 2025. doi: 10.47852/bonviewjcce52026428.',

    'A. Pagliaro, "Regime-aware LightGBM for stock market forecasting: A validated '
    'walk-forward framework with statistical rigor and explainable AI analysis," Electronics, '
    'vol. 15, no. 6, 1334, 2026. doi: 10.3390/electronics15061334.',

    'Y. Song, W. Cho, S. I. Han, and J. Yoo, "Attention integration strategies in MLP-based '
    'stock movement prediction: Effects on performance, stability, and interpretability," '
    'Electronics, vol. 15, no. 17, 3942, 2026. doi: 10.3390/electronics15173942.',

    'L. Breiman, "Random forests," Machine Learning, vol. 45, no. 1, pp. 5-32, 2001. '
    'doi: 10.1023/A:1010933404324.',

    'S. M. Lundberg, G. Erion, H. Chen, A. DeGrave, J. M. Prutkin, B. Nair, R. Katz, '
    'J. Himmelfarb, N. Bansal, and S.-I. Lee, "From local explanations to global '
    'understanding with explainable AI for trees," Nature Machine Intelligence, vol. 2, '
    'pp. 56-67, 2020. doi: 10.1038/s42256-019-0138-9.',

    'M. T. Ribeiro, S. Singh, and C. Guestrin, "Why should I trust you? Explaining the '
    'predictions of any classifier," in Proc. 22nd ACM SIGKDD International Conference on '
    'Knowledge Discovery and Data Mining (KDD), 2016, pp. 1135-1144. '
    'doi: 10.1145/2939672.2939778.',

    'F. X. Diebold and R. S. Mariano, "Comparing predictive accuracy," Journal of Business '
    'and Economic Statistics, vol. 13, no. 3, pp. 253-263, 1995. '
    'doi: 10.1080/07350015.1995.10524599.',

    'J. Adebayo, J. Gilmer, M. Muelly, I. Goodfellow, M. Hardt, and B. Kim, "Sanity checks '
    'for saliency maps," in Advances in Neural Information Processing Systems (NeurIPS), '
    '2018, pp. 9505-9515.',

    'T. T. Huynh, M. H. Nguyen, T. T. Nguyen, P. L. Nguyen, M. Weidlich, Q. V. H. Nguyen, '
    'and K. Aberer, "Efficient integration of multi-order dynamics and internal dynamics in '
    'stock movement prediction," in Proc. 16th ACM International Conference on Web Search '
    'and Data Mining (WSDM), 2023, pp. 850-858. doi: 10.1145/3539597.3570427.',

    'J. Fan and Y. Shen, "StockMixer: A simple yet strong MLP-based architecture for stock '
    'price forecasting," in Proc. AAAI Conference on Artificial Intelligence, vol. 38, 2024, '
    'pp. 8389-8397. doi: 10.1609/aaai.v38i8.28681.',

    'F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, M. Blondel, '
    'P. Prettenhofer, R. Weiss, V. Dubourg, J. Vanderplas, A. Passos, D. Cournapeau, '
    'M. Brucher, M. Perrot, and E. Duchesnay, "Scikit-learn: Machine learning in Python," '
    'Journal of Machine Learning Research, vol. 12, pp. 2825-2830, 2011.',

    'W. K. Newey and K. D. West, "A simple, positive semi-definite, heteroskedasticity and '
    'autocorrelation consistent covariance matrix," Econometrica, vol. 55, no. 3, '
    'pp. 703-708, 1987. doi: 10.2307/1913610.',
]


APPENDIX = [
    ("p",
     "The complete source is 3,249 lines across 13 modules, available in the project "
     "repository. The four excerpts below are the passages on which the project's claims "
     "depend; each is reproduced exactly as it runs."),

    ("h2", "Feature Construction, Showing Leakage Control"),
    ("p",
     "Features are built on wide tables indexed by date and ticker, so every backward shift "
     "is explicit and inspectable. The targets are produced by shifting forward, which is "
     "the only place in the pipeline where a future value is referenced at all. From "
     "features.py."),
    ("code",
     'def build(panel):\n'
     '    wide = {c: panel.pivot(index="date", columns="ticker", values=c)\n'
     '            for c in ("open", "high", "low", "close", "volume")}\n'
     '    o, h, l, c, v = (wide[k] for k in ("open", "high", "low", "close", "volume"))\n'
     '    logc = np.log(c)\n'
     '    r1 = logc.diff()\n'
     '    f = {}\n'
     '\n'
     '    for n in (1, 2, 5, 10, 20, 60):\n'
     '        f[f"ret_{n}d"] = logc.diff(n)\n'
     '    for n in (5, 20, 50, 200):\n'
     '        f[f"dist_sma{n}"] = c / c.rolling(n, min_periods=n).mean() - 1\n'
     '    ...\n'
     '    # Targets: next trading day\'s log return and close price.\n'
     '    next_ret = logc.shift(-1) - logc\n'
     '    next_close = c.shift(-1)'),

    ("h2", "The Faithfulness Test"),
    ("p",
     "This is the function on which the project's central argument rests. It replaces the "
     "top k features by absolute SHAP with values drawn from background rows, measures how "
     "far the forecast moves, and does the same for a random ordering as a control. The "
     "fidelity term additionally checks that the SHAP mass removed predicts the size of the "
     "change. From explain.py."),
    ("code",
     'def deletion_curves(model, X, sv, background):\n'
     '    """Mean |f(x) - f(x with k features replaced by background values)|, in basis\n'
     '    points, removing features by |SHAP| rank (\'top\') or in random order."""\n'
     '    n, p = X.shape\n'
     '    base = model.predict(X)\n'
     '    order_top = np.argsort(-np.abs(sv), axis=1)\n'
     '    order_rand = np.array([rng.permutation(p) for _ in range(n)])\n'
     '    curves = {"top": [], "random": []}\n'
     '    fidelity = []\n'
     '    for k in K_STEPS:\n'
     '        for name, order in (("top", order_top), ("random", order_rand)):\n'
     '            Xk = np.repeat(X, len(background), axis=0)\n'
     '            bg = np.tile(background, (n, 1))\n'
     '            rows = np.repeat(np.arange(n), len(background))\n'
     '            cols = order[rows][:, :k]\n'
     '            Xk[np.arange(len(Xk))[:, None], cols] = bg[np.arange(len(Xk))[:, None], cols]\n'
     '            removed = model.predict(Xk).reshape(n, len(background)).mean(1)\n'
     '            change = base - removed\n'
     '            curves[name].append(float(1e4 * np.abs(change).mean()))\n'
     '            if name == "top":\n'
     '                shap_removed = np.take_along_axis(sv, order_top[:, :k], axis=1).sum(1)\n'
     '                fidelity.append(float(np.corrcoef(shap_removed, change)[0, 1]))\n'
     '    aopc = {k: float(np.mean(v[1:])) for k, v in curves.items()}\n'
     '    return {"k": K_STEPS, "abs_change_bp": curves, "AOPC_bp": aopc,\n'
     '            "fidelity_corr": dict(zip(K_STEPS[1:], fidelity))}'),

    ("h2", "Reproducible LIME"),
    ("p",
     "A fresh explainer is constructed for every seed, which is the fix for the defect "
     "described in Section 5.3.3. From lime_explain.py."),
    ("code",
     'def make_explainer(reference, seed):\n'
     '    """A fresh explainer per seed: LimeTabularExplainer binds its RandomState into\n'
     '    the discretiser and the solver at construction, so reassigning .random_state on\n'
     '    a reused explainer does not make repeats reproducible."""\n'
     '    return LimeTabularExplainer(reference, feature_names=FEATURES, mode="regression",\n'
     '                                discretize_continuous=True, random_state=seed)\n'
     '\n'
     '\n'
     'def lime_weights(reference, x, predict, seed):\n'
     '    exp = make_explainer(reference, seed).explain_instance(\n'
     '        x, predict, num_features=len(FEATURES), num_samples=5000)\n'
     '    w = np.zeros(len(FEATURES))\n'
     '    for j, weight in exp.as_map()[0]:\n'
     '        w[j] = weight\n'
     '    return w, exp.score'),

    ("h2", "The Live Forecasting Guard"),
    ("p",
     "The assertion that prevents a hindsight value from being presented as a forecast. From "
     "live.py."),
    ("code",
     'df = df.dropna(subset=FEATURES + ["close"])   # NOT on the target: the last day has none\n'
     'train = df.dropna(subset=["target_ret"])      # train on every day with a known outcome\n'
     'live  = df[df.date == last_day].copy()        # forecast the one day with no outcome\n'
     'assert live.target_ret.isna().all(), \\\n'
     '    "the last day already has a known outcome - rerun after the close"'),
]


CHAPTERS = [
    (1, "INTRODUCTION", "CH1"),
    (2, "PROJECT DESCRIPTION AND GOALS", "CH2"),
    (3, "TECHNICAL SPECIFICATION", "CH3"),
    (4, "DESIGN APPROACH AND DETAILS", "CH4"),
    (5, "METHODOLOGY AND TESTING", "CH5"),
    (6, "PROJECT DEMONSTRATION", "CH6"),
    (7, "RESULT AND DISCUSSION", "CH7"),
    (8, "CONCLUSION", "CH8"),
]

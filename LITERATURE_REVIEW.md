# Literature Review

Five recent papers (2025–2026) closest to this project: stock prediction with Random Forest
or tree models, explained with SHAP or LIME.

| # | Paper | Authors | Methodology | Research gap |
|---|---|---|---|---|
| 1 | *Stock Return Prediction on the LQ45 Market Index in the Indonesia Stock Exchange Using a Machine Learning Algorithm Based on Technical Indicators*, **Journal of Risk and Financial Management, 2025** | S. Indra, Sudradjat Supian, Sukono, Riaman Riaman, Moch Panji Agung Saputra, Astrid Sulistya Azahra, Dede Irman Pirdaus | Random Forest, XGBoost, Linear and Ridge regression on technical indicators for 6 Indonesian stocks; SHAP to find important features | Only 6 stocks. SHAP results are reported but never checked to see if they are correct or stable. |
| 2 | *Comparing model-specific and model-agnostic features importance methods using machine learning with technical indicators: A NASDAQ sector-based study*, **Machine Learning with Applications, 2025** | Jeonghoe Lee, Lin Cai | Random Forest and neural networks on NASDAQ's 11 sectors; compares different feature-importance methods for choosing technical indicators | Uses importance methods only to pick features. Does not test whether the explanations are trustworthy or change over time. |
| 3 | *An Explainable AI for Stock Market Prediction: A Machine Learning Approach with XAI and Deep Neural Networks*, **Journal of Computational and Cognitive Engineering, 2025** | Kangana Wallapure Manikrao, Shridhar Allagi, Wai Yie Leong, Mahantesh Laddi | LSTM with attention using sentiment and technical indicators; compared with Random Forest and XGBoost; SHAP and LIME for explanations | Uses SHAP and LIME side by side but does not check if they agree, or if LIME gives the same answer when run again. |
| 4 | *Regime-Aware LightGBM for Stock Market Forecasting: A Validated Walk-Forward Framework with Statistical Rigor and Explainable AI Analysis*, **Electronics, 2026** | A. Pagliaro | Tree model (LightGBM) on 51 NASDAQ-100 stocks, adjusted for bull and bear markets; explanations show the model behaves differently in each market phase | Says explanations change across market phases but does not test this statistically, and only covers 51 stocks. |
| 5 | *Attention Integration Strategies in MLP-Based Stock Movement Prediction: Effects on Performance, Stability, and Interpretability*, **Electronics, 2026** | Yoojeong Song, Woojin Cho, Sang Ik Han, Juhan Yoo | Neural network models trained 1,600 times with different random seeds on 20 stocks | Found that explanations change with the random seed, but only tested neural networks, not Random Forest with SHAP or LIME. |

## Our research gap

These papers either use SHAP or LIME without checking whether the explanations can be
trusted, or check only one thing on a small number of stocks. **No paper tests, for a
Random Forest stock price model, whether SHAP and LIME explanations are:**

1. **correct** (faithful to the model);
2. **stable** (same result when the model or LIME is re-run);
3. **in agreement** with each other;
4. **consistent** across market phases (such as the COVID crash) and sectors.

**This project fills that gap on 474 S&P 500 stocks.**

# Asian Market Quant Research Project

This repository provides a complete workflow for building a professional quant-research deck and dashboard for Asian cross-asset markets. The project is structured into six sequential workstreams, each with clear deliverables and recommended tools.

---

## 1. Scoping & Asset-Class Mapping

Map tickers to asset classes, currencies, and comments. Deliver a LaTeX-formatted table and define asset-class buckets for risk budgeting (e.g., 60% equities, 30% rates, 10% FX).

| Ticker Range                 | Asset Class                                                 | Currency     | Comment                           |
| ---------------------------- | ----------------------------------------------------------- | ------------ | --------------------------------- |
| MXAP … NU710465, EPHE        | Emerging-Asia equity indices & ETF                          | Mostly USD   | Regional beta + macro sensitivity |
| GOLDS, CO1, S 1, FMETF       | Commodities (Gold spot, Brent, Softs, Philippines gold ETF) | USD          | Inflation hedge, carry via roll   |
| SPX, NKY                     | Developed-market equity benchmarks                          | USD / JPY    | Stress-test proxies               |
| USDPHP … USDJPY              | EM & DM FX crosses vs USD                                   | USD notional | Carry + momentum rich             |
| USGG5YR, GTPHP5yr, GTUSDPH5Y | Sovereign & quasi-sovereign 5-yr yields                     | USD & PHP    | Duration + EM credit risk         |

---

## 2. Data Engineering Pipeline

- **Ingest & tidy:** Load and clean spreadsheet data, resample to business days, forward-fill holidays.
- **Currency normalization:** Convert all series to USD.
- **Corporate actions & rolls:** Adjust for dividends, roll contracts before expiry.
- **Store snapshots:** Organize raw and processed data in `data/`.

**Deliverable:** Reproducible data module (`data_loader.py`) and a data dictionary.

---

## 3. Exploratory Analysis

- Summary statistics: mean %, vol %, skew, kurtosis.
- Correlations & regime analysis (e.g., 2008, COVID-19, 2022 inflation spike).
- Rolling 12-month Sharpe heatmap.

**Deliverable:** Jupyter notebook with charts and a “Market landscape” section for the deck.

---

## 4. Signal Design & Strategy Prototypes

Design and backtest signals for each asset bucket:

| Bucket      | Classic Signals                   | PM-Wow Factor                     |
| ----------- | --------------------------------- | --------------------------------- |
| Equities    | 12-1M momentum, 63-day breakout   | Volatility-adjusted (risk parity) |
| FX          | Carry, 1-M momentum               | “Dollar smile” overlay            |
| Rates       | 2s5s10s butterfly, mean-reversion | Macro overlay (CPI surprises)     |
| Commodities | 6-/12-M momentum, roll yield      | Seasonality dummies               |

- Write vectorized signal functions.
- Backtest monthly with transaction costs and vol-targeting.
- Report metrics: CAGR, Sharpe, Sortino, max drawdown, turnover, hit-rate, exposure heatmap.
- Robustness: rolling windows, walk-forward OOS, parameter sweeps.

**Deliverable:** `backtest_engine.py` and separate notebooks per prototype.

---

## 5. Portfolio Construction & Risk Budgeting

- Top-down allocation (e.g., 60/30/10 split) via hierarchical risk parity (HRP).
- Signal ensemble: combine best signals per bucket (equal risk or performance-weighted).
- Stress tests: 2008, taper-tantrum, 2020 crash, 2022 inflation.
- Optional: factor exposures (Barra or PCA).

**Deliverable:** Notebook and PDF appendix “Risk & Allocation Methodology”.

---

## 6. Presentation & PM-Facing Assets

| Asset                | Purpose                 | Tips                                        |
| -------------------- | ----------------------- | ------------------------------------------- |
| 10-slide Beamer deck | Executive summary       | <15 min read-time, “Key Takeaways” up front |
| Streamlit dashboard  | Interactive exploration | Tabs: Performance, Positions, Risk          |
| Excel hand-off file  | Quick inspection        | Pivot table of monthly returns + tear-sheet |

---

## Recommended Tool Stack

- **Python**: pandas, numpy, vectorbt/bt, PyPortfolioOpt, quantstats
- **Git**: branch per prototype
- **Environment**: conda env + `requirements.txt`
- **Documentation**: MkDocs or simple `README.md`

---

## Suggested Timeline (Working Days)

```
Day 1   Scope + data ingestion
Day 2   Cleaning + basic EDA
Day 3-5 Prototype 1–3 (momentum, carry, roll)
Day 6   Robustness & risk budgeting
Day 7   Build deck & dashboard
Day 8   Buffer / iteration with PM feedback
```

---

## Final Checks Before Hand-off

1. Re-run all notebooks top-to-bottom on a fresh kernel.
2. Tag the Git release (e.g., v0.9-PMdemo).
3. Export deck to PDF and embed high-resolution figures.
4. Dry-run the Streamlit app locally and on Streamlit Community Cloud.

---

## Next Steps

- Add alternative data (e.g., Alibaba traffic, PMI surprises).
- Explore Bayesian ensemble for signal blending.
- Model execution costs for production deployment.

---

**Tackle one workstream at a time, commit early, and you’ll deliver a professional-grade project ready for PM review and further funding.**

# Energy Capital Discipline Monitor

[![Live Dashboard](https://img.shields.io/badge/Live_Dashboard-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://eganl2024-sudo-post-covid-recovery-in-oil-and-gas-app-lrw3ax.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)](https://python.org)

**A real-time financial intelligence platform tracking capital allocation, solvency, and shareholder yield across the Oil & Gas Super Majors.**

**Live dashboard:** https://eganl2024-sudo-post-covid-recovery-in-oil-and-gas-app-lrw3ax.streamlit.app/

---

### 1. The "Banker's Logic" (Why this exists)
In the modern Energy sector, "Growth at all costs" is dead. The new paradigm is **Capital Discipline**.
This platform replaces static Excel models with a live Python engine to answer three critical questions:
1. **Discipline:** Who is over-spending on drilling vs. returning cash to shareholders?
2. **Solvency:** Who is funding their dividend with debt?
3. **Quality:** Who has "Real" Free Cash Flow vs. "Accounting" Net Income?

---

### 2. Key Intelligence Layers

#### 🧠 The Automated Analyst
A logic gate that scans real-time data to auto-generate a "Sector Insight" banner — identifies the Yield Leader (Best Risk/Reward) and the Quality Laggard (Lowest FCF Conversion) instantly.

#### 📉 The Solvency Stress Test
An interactive OCF Downturn simulator (0–50%). The app recalculates the **Dividend Sustainability Ratio (DSR)** in real-time. Identified that **Shell (SHEL)** is currently more resilient to a commodity shock than peers under current capital structures.

#### 🛡️ The Earnings Quality Sentinel
Tracks **FCF Conversion** (FCF / Net Income). A ratio < 0.8 signals that earnings are driven by non-cash items rather than cash generation.

---

### 3. Tech Stack
- **Frontend:** Streamlit
- **Backend:** Python · Pandas · NumPy
- **Data:** yfinance with LRU cache and CSV backup failover
- **Visualization:** Plotly (Bloomberg dark theme)

---

### 4. How to Run Locally
```bash
git clone https://github.com/eganl2024-sudo/Post-COVID-recovery-in-Oil-and-Gas.git
cd Post-COVID-recovery-in-Oil-and-Gas
pip install -r requirements.txt
streamlit run app.py
```

---

### 5. Streamlit Cloud Deployment

| Setting | Value |
|---|---|
| Repository | `eganl2024-sudo/Post-COVID-recovery-in-Oil-and-Gas` |
| Branch | `main` |
| App entrypoint | `app.py` |
| Python version | 3.11 |
| Valuation Desk tab | Local environment only (requires Private Oil Futures repo) |

---

*Author: Liam Egan | [LinkedIn](https://www.linkedin.com/in/liam-egan-)*

# Energy Capital Discipline Monitor (Live Dashboard)

**A real-time financial intelligence platform tracking capital allocation, solvency, and shareholder yield across the Oil & Gas Super Majors.**
*Built by Liam Egan (Chemical Engineering / MSBA)*

[![Streamlit](https://img.shields.io/badge/Streamlit-Live-ff4b4b)](https://energy-capital-monitor.streamlit.app)
[![Status](https://img.shields.io/badge/Status-Institutional%20Grade-success)]()

---

### 1. The "Banker's Logic" (Why this exists)
In the modern Energy sector, "Growth at all costs" is dead. The new paradigm is **Capital Discipline**.
This platform replaces static Excel models with a live Python engine to answer three critical questions:
1.  **Discipline:** Who is over-spending on drilling vs. returning cash to shareholders?
2.  **Solvency:** Who is funding their dividend with debt?
3.  **Quality:** Who has "Real" Free Cash Flow vs. "Accounting" Net Income?

---

### 2. Key Intelligence Layers

#### 🧠 The Automated Analyst
* **Feature:** A logic gate that scans real-time data to auto-generate a "Sector Insight" banner.
* **Logic:** Identifies the "Yield Leader" (Best Risk/Reward) and the "Quality Laggard" (Lowest FCF Conversion) instantly.

#### 📉 The Solvency Stress Test
* **Feature:** An interactive "Oil Price Shock" simulator.
* **Logic:** Users can slide a "Cash Flow Downturn" bar (0-50%). The app recalculates the **Dividend Sustainability Ratio (DSR)** in real-time.
* **Alpha:** Identified that **Shell (SHEL)** is currently more resilient to a crash than peers, challenging historical sector norms.

#### 🛡️ The Earnings Quality Sentinel
* **Feature:** Tracks **FCF Conversion** ($\frac{FCF}{Net Income}$).
* **Insight:** Filters out "Paper Profits." A ratio < 0.8 signals that earnings are driven by non-cash items (like asset mark-ups) rather than cash generation.

---

### 3. Tech Stack & Architecture
* **Frontend:** Streamlit (Custom CSS "Bloomberg" Theme).
* **Backend:** Python (Pandas, NumPy).
* **Data Ingress:** `yfinance` with a robust **LRU Cache** to handle API rate limits and optimize latency.
* **Visualization:** Plotly Interactive Charts with "Event Overlays" (marking COVID, Energy Crisis, etc.).

---

### 4. How to Run Locally
1.  **Clone the repo:**
    ```bash
    git clone https://github.com/eganl2024-sudo/Energy-Capital-Discipline-Monitor.git
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Launch the dashboard:**
    ```bash
    streamlit run app.py
    ```

---
*Author: Liam Egan | [LinkedIn](https://www.linkedin.com/in/liam-egan-)*

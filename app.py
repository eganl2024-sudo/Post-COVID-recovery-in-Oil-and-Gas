import streamlit as st
import pandas as pd
import os
from datetime import datetime

from src.data import EnergyDataLoader
from src.metrics import calculate_metrics, calculate_sustainability_ratios
from src.plots import (
    plot_capital_discipline,
    plot_cash_flow_mix,
    plot_fcf_yield,
    plot_metric_trend,
    plot_earnings_quality,
    plot_sustainability_risk,
    plot_leverage_sentinel
)

# --- Optional: Intrinsic Valuation Desk (requires Private Oil Futures repo locally) ---
try:
    import sys
    PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FUTURES_PATH = os.path.abspath(os.path.join(PARENT_DIR, "Private Oil Futures"))
    if FUTURES_PATH not in sys.path:
        sys.path.insert(0, FUTURES_PATH)
    from src.bridge import evaluate_corporate_intrinsic_value, simulate_corporate_monte_carlo
    VALUATION_DESK_AVAILABLE = True
except ImportError:
    VALUATION_DESK_AVAILABLE = False

st.set_page_config(page_title="Energy Capital Discipline Platform", layout="wide")

# --- CUSTOM THEME ---
st.markdown("""
<style>
    .main { background-color: #121212; color: #ffffff; }
    .stMetric {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #333;
    }
    .snapshot-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #121212 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ffb900;
        margin-bottom: 20px;
    }
    .audit-log {
        font-family: monospace;
        font-size: 0.8rem;
        color: #888;
    }
    .insight-banner {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ffb900;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# --- CACHED DATA ENGINE ---
@st.cache_data(ttl=3600)
def get_sector_data(tickers):
    loader = EnergyDataLoader(tickers=tickers)

    backup_dir = "data"
    backup_file = os.path.join(backup_dir, "backup_financials.csv")
    os.makedirs(backup_dir, exist_ok=True)

    df = pd.DataFrame()
    try:
        df = loader.fetch_financials()
    except Exception as e:
        print(f"Error fetching live financials: {e}")

    if df is not None and not df.empty:
        try:
            df.to_csv(backup_file, index=False)
        except Exception as e:
            print(f"Error writing backup cache: {e}")
    else:
        if os.path.exists(backup_file):
            try:
                df = pd.read_csv(backup_file)
                df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
                df = df[df["Ticker"].isin(tickers)]
                st.toast("📡 Live API rate-limited. Running in offline backup mode.", icon="⚠️")
            except Exception as e:
                print(f"Error loading backup cache: {e}")

    if df is None or df.empty:
        return None
    return calculate_metrics(df)

# --- UI HEADER ---
st.title("📡 Energy Capital Discipline Monitor")
st.subheader("Institutional Sector Coverage: Advanced Intelligence Feed")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Sector Coverage")
    tickers = st.multiselect(
        "Select Tickers",
        ["XOM", "CVX", "SHEL", "TTE", "BP", "EQNR"],
        default=["XOM", "CVX", "SHEL", "TTE", "BP", "EQNR"]
    )

    st.divider()

    # Build tab list dynamically based on what's available
    tab_options = [
        "Current Snapshot",
        "Historical Trends",
        "Earnings Quality",
        "Dividend Sustainability",
        "Solvency Sentinel"
    ]
    if VALUATION_DESK_AVAILABLE:
        tab_options.append("Intrinsic Valuation Desk")

    active_tab = st.radio("Analysis Mode", tab_options)

    st.header("Risk Stress Test")
    stress_pct = st.slider("Simulate OCF Downturn (%)", 0, 50, 0)
    stress_buffer = 1.0 - (stress_pct / 100.0)

    if st.button("🔄 Clear Cache & Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- MAIN ANALYSIS ENGINE ---
if not tickers:
    st.info("Select tickers in the sidebar to begin analysis.")
else:
    processed_data = get_sector_data(tickers)

    if processed_data is None:
        st.error("📡 Could not retrieve financials. yfinance may be experiencing rate limits. Try refreshing in a few minutes.")
    else:
        required_cols = ['Leverage_Ratio', 'Net_Debt', 'EBITDA']
        if not all(col in processed_data.columns for col in required_cols):
            processed_data = calculate_metrics(processed_data)

        latest_data = processed_data.sort_values('Date').groupby('Ticker').tail(1)
        stressted_data = calculate_sustainability_ratios(latest_data, stress_buffer)

        # --- AUTOMATED ANALYST HEADLINE ---
        if stressted_data.empty:
            st.warning("⚠️ Insight Feed: Insufficient data to generate sector analysis.")
        else:
            safe_firms = stressted_data[stressted_data['DSR'] >= 1.0]
            if not safe_firms.empty:
                leader = safe_firms.loc[safe_firms['FCF_Yield'].idxmax()]
            else:
                leader = stressted_data.loc[stressted_data['DSR'].idxmax()]

            laggard = latest_data.loc[latest_data['FCF_Conversion'].idxmin()]

            st.markdown(f"""
            <div style="background-color: #1e1e1e; padding: 15px; border-radius: 5px; border-left: 5px solid #ffb900; margin-bottom: 25px;">
                <span style="color: #ffb900; font-weight: bold; font-size: 1.1em;">💡 SECTOR INSIGHT:</span>
                <span style="color: #e0e0e0; font-size: 1em; margin-left: 10px;">
                    {leader['Ticker']} is the current <b>Yield Leader</b> (DSR: {leader['DSR']:.2f}x, Yield: {leader['FCF_Yield']:.1%}),
                    while {laggard['Ticker']} shows potential earnings quality friction with an FCF Conversion of <b>{laggard['FCF_Conversion']:.2f}x</b>.
                </span>
            </div>
            """, unsafe_allow_html=True)

        # --- TOP LEVEL KPIs ---
        st.markdown('<div class="snapshot-card">', unsafe_allow_html=True)
        snap_col1, snap_col2, snap_col3, snap_col4 = st.columns(4)

        avg_discipline = latest_data['Capital_Discipline_Ratio'].mean()
        snap_col1.metric("Avg. Capital Discipline", f"{avg_discipline:.1%}")

        yield_leader = latest_data.loc[latest_data['FCF_Yield'].idxmax()]
        snap_col2.metric("Yield Leader", yield_leader['Ticker'], f"{yield_leader['FCF_Yield']:.1%}")

        avg_conv = latest_data['FCF_Conversion'].mean()
        snap_col3.metric("Avg. Cash Conversion", f"{avg_conv:.1f}x")

        total_payout = (latest_data['Dividends'] + latest_data['Buybacks']).sum()
        snap_col4.metric("Total Payout (TTM)", f"${total_payout/1e9:.1f}B")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- VIEW MODES ---
        if active_tab == "Current Snapshot":
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(plot_capital_discipline(latest_data), use_container_width=True)
            with col2:
                st.plotly_chart(plot_fcf_yield(latest_data), use_container_width=True)
            st.plotly_chart(plot_cash_flow_mix(latest_data), use_container_width=True)

        elif active_tab == "Historical Trends":
            st.header("Temporal Trajectories")
            metric_to_plot = st.selectbox(
                "Select Trend Metric",
                ["Capital_Discipline_Ratio", "FCF_Yield", "OCF", "Capex", "FCF", "Leverage_Ratio"]
            )
            st.plotly_chart(plot_metric_trend(processed_data, metric_to_plot, f"Historical Trend: {metric_to_plot}"), use_container_width=True)
            st.info("💡 Note: Vertical dashed lines indicate key sector events (COVID, Energy Crisis, Pivot to Discipline).")

        elif active_tab == "Earnings Quality":
            st.header("Operational Integrity")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.plotly_chart(plot_earnings_quality(latest_data), use_container_width=True)
            with col2:
                st.markdown("""
                **Earnings Quality Audit**:
                - **Goal**: Identify firms where FCF conversion significantly deviates from 1.0.
                - **Red Flags**: Conversion < 0.5 may indicate aggressive accounting or heavy working capital drag.
                - **Leaders**: Conversion > 1.0 suggests highly efficient cash generation.
                """)
                st.dataframe(latest_data[['Ticker', 'Net_Income', 'FCF', 'FCF_Conversion']].sort_values('FCF_Conversion', ascending=False))

        elif active_tab == "Dividend Sustainability":
            st.header("Risk Diagnostics: Sustainability Stress Test")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.plotly_chart(plot_sustainability_risk(stressted_data), use_container_width=True)
            with col2:
                st.markdown(f"### Stress Level: {stress_pct}%")
                avg_dsr = stressted_data['DSR'].mean()
                status = "Sustainable" if avg_dsr >= 1.0 else "High Risk"
                st.metric("Sector Avg. DSR", f"{avg_dsr:.2f}", status)
                st.markdown("""
                **Risk Guide**:
                - **DSR >= 1.0**: (Green) Core OCF covers all hard commitments.
                - **0.8 <= DSR < 1.0**: (Amber) Caution. Funding gap likely bridged by divestments or debt.
                - **DSR < 0.8**: (Red) High Risk. Dividend cut or massive borrowing required.
                """)
            st.divider()
            st.subheader("Residual Cash Flow Feed ($B)")
            stressted_data['Residual_Cash_B'] = stressted_data['Residual_Cash'] / 1e9
            st.table(stressted_data[['Ticker', 'Stressed_OCF', 'Total_Commitments', 'Residual_Cash_B', 'DSR']].sort_values('DSR'))

        elif active_tab == "Solvency Sentinel":
            st.header("Financial Rigor: Leverage & Solvency")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.plotly_chart(plot_leverage_sentinel(latest_data), use_container_width=True)
            with col2:
                st.markdown("""
                **Solvency Audit**:
                - **Ratio**: Net Debt / EBITDA.
                - **Healthy (< 1.0x)**: Strong balance sheet, capable of weathering price volatility.
                - **Moderate (1.0x - 2.0x)**: Balanced approach to leverage.
                - **High (> 2.0x)**: Potential constraint on shareholder returns.
                """)
                st.dataframe(latest_data[['Ticker', 'Total_Debt', 'Cash', 'Net_Debt', 'EBITDA', 'Leverage_Ratio']].sort_values('Leverage_Ratio'))

        elif active_tab == "Intrinsic Valuation Desk":
            if not VALUATION_DESK_AVAILABLE:
                st.info(
                    "⚠️ The Intrinsic Valuation Desk requires the Private Oil Futures valuation engine, "
                    "which is only available in the local development environment.\n\n"
                    "The five core analysis modes above (Current Snapshot, Historical Trends, "
                    "Earnings Quality, Dividend Sustainability, and Solvency Sentinel) are fully "
                    "operational in this deployed version."
                )
            else:
                # Full valuation desk — only reachable locally
                import plotly.graph_objects as go

                v_col1, v_col2 = st.columns(2)
                with v_col1:
                    val_ticker = st.selectbox("Select Target Ticker for Valuation", tickers)

                with st.spinner("Initializing valuation models..."):
                    try:
                        base_eval = evaluate_corporate_intrinsic_value(val_ticker, scenario="base")
                    except Exception as e:
                        st.error(f"Valuation Engine error: {e}")
                        base_eval = {
                            "wacc": 0.08, "terminal_growth": 0.015, "current_price": 100.0,
                            "ebitda_margin": 0.30, "implied_share_price": 100.0, "upside_percent": 0.0,
                            "enterprise_value": 0.0, "net_debt": 0.0, "equity_value": 0.0,
                            "shares_outstanding": 1.0, "projected_fcfs": [0.0]*5,
                            "projected_revenues": [0.0]*5, "percent_value_from_tv": 0.5
                        }

                with v_col2:
                    scenario_sel = st.selectbox(
                        "Active Oil Price Scenario",
                        ["Bear Scenario ($60 Oil)", "Base Scenario ($85 Oil)", "Bull Scenario ($110 Oil)"],
                        index=1
                    )
                    scen_key = "low" if "Bear" in scenario_sel else "base" if "Base" in scenario_sel else "high"

                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    custom_wacc_val = st.slider(
                        "Cost of Capital / WACC Override (%)",
                        min_value=4.0, max_value=16.0,
                        value=float(base_eval["wacc"] * 100.0), step=0.25
                    ) / 100.0
                with p_col2:
                    custom_g_val = st.slider(
                        "Terminal Growth Rate Override (%)",
                        min_value=-3.0, max_value=5.0,
                        value=float(base_eval["terminal_growth"] * 100.0), step=0.25
                    ) / 100.0

                with st.spinner("Computing DCF pathways..."):
                    active_eval = evaluate_corporate_intrinsic_value(val_ticker, scenario=scen_key, custom_wacc=custom_wacc_val, custom_terminal_growth=custom_g_val)
                    bear_eval = evaluate_corporate_intrinsic_value(val_ticker, scenario="low", custom_wacc=custom_wacc_val, custom_terminal_growth=custom_g_val)
                    bull_eval = evaluate_corporate_intrinsic_value(val_ticker, scenario="high", custom_wacc=custom_wacc_val, custom_terminal_growth=custom_g_val)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("DCF Intrinsic Price", f"${active_eval['implied_share_price']:.2f}")
                m2.metric("Current Market Price", f"${active_eval['current_price']:.2f}")
                m3.metric("Implied Upside", f"{active_eval['upside_percent']:+.1%}")
                m4.metric("EBITDA Margin", f"{active_eval['ebitda_margin']:.1%}")

        # --- ADVANCED AUDIT LOG ---
        with st.expander("🛠️ Advanced Architectural Audit"):
            st.markdown('<p class="audit-log">Registry Status: ACTIVE</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="audit-log">Last Ingress Attempt: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>', unsafe_allow_html=True)
            st.markdown('<p class="audit-log">Standardization Mapping: IFRS/GAAP Robust</p>', unsafe_allow_html=True)
            st.write("Raw Standardized Feed (Advanced User Access Only)")
            st.dataframe(processed_data)

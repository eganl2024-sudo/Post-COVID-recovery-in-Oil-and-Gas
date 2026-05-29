import pandas as pd
import numpy as np

def calculate_metrics(df):
    """
    Computes modern energy investment metrics based on standardized financial data.
    
    Metrics:
    - Capital Discipline Ratio: Capex / OCF (Target: < 40%)
    - FCF Yield: (OCF - Capex) / Market Cap
    - Shareholder Payback Ratio: (Dividends + Buybacks) / OCF
    """
    m_df = df.copy()
    
    # ensure numeric types
    numeric_cols = ['OCF', 'Capex', 'Dividends', 'Buybacks', 'Market_Cap', 'Net_Income', 'EBITDA', 'Total_Debt', 'Cash']
    for col in numeric_cols:
        if col in m_df.columns:
            m_df[col] = pd.to_numeric(m_df[col], errors='coerce').fillna(0)
        else:
            m_df[col] = 0.0

    # Safe denominators using epsilon clamping to completely prevent division-by-zero or infinite spikes
    safe_ocf = np.where(m_df['OCF'] == 0, 1e-9, m_df['OCF'])
    safe_mcap = np.where(m_df['Market_Cap'] == 0, 1e-9, m_df['Market_Cap'])
    safe_netinc = np.where(m_df['Net_Income'] == 0, 1e-9, m_df['Net_Income'])
    safe_ebitda = np.where(m_df['EBITDA'] == 0, 1e-9, m_df['EBITDA'])

    # 1. Capital Discipline Ratio
    # We use OCF as the denominator to see how much of core cash flow is reinvested
    m_df['Capital_Discipline_Ratio'] = (m_df['Capex'] / safe_ocf).replace([float('inf'), -float('inf')], 0)
    
    # 2. Free Cash Flow (OCF - Capex)
    m_df['FCF'] = m_df['OCF'] - m_df['Capex']
    
    # 3. FCF Yield
    m_df['FCF_Yield'] = (m_df['FCF'] / safe_mcap).replace([float('inf'), -float('inf')], 0)
    
    # 4. Shareholder Payback Ratio
    m_df['Shareholder_Payback_Ratio'] = ((m_df['Dividends'] + m_df['Buybacks']) / safe_ocf).replace([float('inf'), -float('inf')], 0)
    
    # 5. Earnings Quality (FCF Conversion)
    m_df['FCF_Conversion'] = (m_df['FCF'] / safe_netinc).replace([float('inf'), -float('inf')], 0)
    # Clamp extreme values for visualization stability
    m_df['FCF_Conversion'] = m_df['FCF_Conversion'].clip(lower=-2, upper=5)
    
    # 6. Solvency Sentinel: Leverage Ratio (Net Debt / EBITDA)
    m_df['Net_Debt'] = m_df['Total_Debt'] - m_df['Cash']
    m_df['Leverage_Ratio'] = (m_df['Net_Debt'] / safe_ebitda).replace([float('inf'), -float('inf')], 0)
    
    return m_df

def calculate_sustainability_ratios(df, ocf_stress_buffer=1.0):
    """
    Calculates coverage ratios for dividend and capex sustainability.
    Uses an Arps-style breakeven logic assuming hard commit prioritization:
    DSR = Stressed_OCF / (Maintenance Capex + Dividends)
    """
    m_df = df.copy()
    
    # Apply Stress Test to OCF
    m_df['Stressed_OCF'] = m_df['OCF'] * ocf_stress_buffer
    
    # Total Cash Commitments (Capex + Dividends)
    m_df['Total_Commitments'] = m_df['Capex'] + m_df['Dividends']
    
    # Dividend Sustainability Ratio (DSR) with epsilon safety floor
    safe_commitments = np.where(m_df['Total_Commitments'] == 0, 1e-9, m_df['Total_Commitments'])
    m_df['DSR'] = (m_df['Stressed_OCF'] / safe_commitments).replace([float('inf'), -float('inf')], 0)
    
    # Free Cash Flow Post-Dividend (Residual Cash)
    m_df['Residual_Cash'] = m_df['Stressed_OCF'] - m_df['Total_Commitments']
    
    return m_df

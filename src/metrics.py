import pandas as pd

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

    # 1. Capital Discipline Ratio
    # We use OCF as the denominator to see how much of core cash flow is reinvested
    m_df['Capital_Discipline_Ratio'] = (m_df['Capex'] / m_df['OCF']).replace([float('inf'), -float('inf')], 0)
    
    # 2. Free Cash Flow (OCF - Capex)
    m_df['FCF'] = m_df['OCF'] - m_df['Capex']
    
    # 3. FCF Yield
    # Market Cap is usually current, so this is an approximation if looking at historical years
    m_df['FCF_Yield'] = (m_df['FCF'] / m_df['Market_Cap']).replace([float('inf'), -float('inf')], 0)
    
    # 4. Shareholder Payback Ratio
    m_df['Shareholder_Payback_Ratio'] = ((m_df['Dividends'] + m_df['Buybacks']) / m_df['OCF']).replace([float('inf'), -float('inf')], 0)
    
    # 5. Earnings Quality (FCF Conversion)
    # FCF / Net Income. Measures how much of 'paper' profit is real cash.
    # We use a threshold to avoid massive spikes when Net Income is near zero.
    m_df['FCF_Conversion'] = (m_df['FCF'] / m_df['Net_Income']).replace([float('inf'), -float('inf')], 0)
    # Clamp extreme values for visualization stability
    m_df['FCF_Conversion'] = m_df['FCF_Conversion'].clip(lower=-2, upper=5)
    
    # 6. Solvency Sentinel: Leverage Ratio (Net Debt / EBITDA)
    # This provides context on financial flexibility during downturns.
    m_df['Net_Debt'] = m_df['Total_Debt'] - m_df['Cash']
    m_df['Leverage_Ratio'] = (m_df['Net_Debt'] / m_df['EBITDA']).replace([float('inf'), -float('inf')], 0)
    
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
    # We focus on the 'Hard Outlays' that are usually prioritized in energy banking scenarios
    m_df['Total_Commitments'] = m_df['Capex'] + m_df['Dividends']
    
    # Dividend Sustainability Ratio (DSR)
    # DSR > 1.0 means the dividend + capex are covered by Operating Cash Flow.
    # DSR < 1.0 means they are funding the dividend via debt or cash reserves.
    m_df['DSR'] = (m_df['Stressed_OCF'] / m_df['Total_Commitments']).replace([float('inf'), -float('inf')], 0)
    
    # Free Cash Flow Post-Dividend (Residual Cash)
    m_df['Residual_Cash'] = m_df['Stressed_OCF'] - m_df['Total_Commitments']
    
    return m_df

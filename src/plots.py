import plotly.express as px
import plotly.graph_objects as go

# Bloomberg-esque Color Palette
BBG_AMBER = "#ffb900"
BBG_BLUE = "#00b2ff"
BBG_WHITE = "#ffffff"
BBG_DARK = "#121212"
BBG_GRAY = "#2a2a2a"

def plot_capital_discipline(df):
    """
    Creates a bar chart for Capital Discipline Ratio (Capex/OCF).
    """
    fig = px.bar(
        df, 
        x='Ticker', 
        y='Capital_Discipline_Ratio', 
        color='Ticker',
        title="Capital Discipline Ratio (Capex / OCF)",
        labels={'Capital_Discipline_Ratio': 'Ratio (%)'},
        template="plotly_dark"
    )
    
    # Target line at 40%
    fig.add_hline(y=0.4, line_dash="dash", line_color="red", annotation_text="Target Max (40%)")
    
    fig.update_layout(
        plot_bgcolor=BBG_DARK,
        paper_bgcolor=BBG_DARK,
        font_color=BBG_WHITE,
        title_font_size=20
    )
    return fig

def plot_cash_flow_mix(df):
    """
    Creates a stacked bar chart showing the mix of OCF vs Shareholder returns.
    """
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['Ticker'],
        y=df['OCF'],
        name='Operating Cash Flow',
        marker_color=BBG_BLUE
    ))
    
    fig.add_trace(go.Bar(
        x=df['Ticker'],
        y=-(df['Dividends'] + df['Buybacks']),
        name='Shareholder Returns',
        marker_color=BBG_AMBER
    ))
    
    fig.update_layout(
        barmode='relative',
        title="Cash Flow Mix: OCF vs Returns",
        template="plotly_dark",
        plot_bgcolor=BBG_DARK,
        paper_bgcolor=BBG_DARK,
        font_color=BBG_WHITE
    )
    return fig

def plot_fcf_yield(df):
    """
    Bar chart for Free Cash Flow Yield.
    """
    fig = px.bar(
        df,
        x='Ticker',
        y='FCF_Yield',
        title="Free Cash Flow (FCF) Yield",
        labels={'FCF_Yield': 'Yield (%)'},
        template="plotly_dark",
        color='FCF_Yield',
        color_continuous_scale=[BBG_BLUE, BBG_AMBER]
    )
    
    fig.update_layout(
        plot_bgcolor=BBG_DARK,
        paper_bgcolor=BBG_DARK,
        font_color=BBG_WHITE
    )
    return fig

def plot_metric_trend(df, metric_col, title):
    """
    Line chart showing the trajectory of a metric over time for multiple tickers.
    Features vertical event overlays for storytelling.
    """
    fig = px.line(
        df,
        x='Date',
        y=metric_col,
        color='Ticker',
        title=title,
        template="plotly_dark",
        markers=True
    )
    
    # Event Overlays
    events = [
        {"date": "2020-03-01", "label": "COVID-19 Shock"},
        {"date": "2022-02-24", "label": "Energy Crisis"},
        {"date": "2023-01-01", "label": "Capital Discipline Pivot"}
    ]
    
    for event in events:
        try:
            # Convert string to Timestamp to match date-axis type (prevents Plotly TypeError)
            event_ts = pd.to_datetime(event["date"])
            fig.add_vline(
                x=event_ts.timestamp() * 1000 if df['Date'].dtype == 'datetime64[ns]' else event["date"], 
                line_dash="dash", 
                line_color=BBG_GRAY,
                annotation_text=event["label"],
                annotation_position="top left"
            )
        except:
            continue
    
    fig.update_layout(
        plot_bgcolor=BBG_DARK,
        paper_bgcolor=BBG_DARK,
        font_color=BBG_WHITE,
        xaxis_title="Fiscal Year End",
        yaxis_title="Metric Value"
    )
    return fig

def plot_leverage_sentinel(df):
    """
    Bar chart showing Net Debt / EBITDA leverage ratios with risk threshold colors.
    """
    if 'Leverage_Ratio' not in df.columns:
        return go.Figure().update_layout(title="Leverage Data Missing - Please Refresh Cache")
        
    colors = []
    for val in df['Leverage_Ratio']:
        if val <= 1.0: colors.append('green')
        elif val <= 2.0: colors.append('orange')
        else: colors.append('red')
        
    fig = go.Figure(data=[go.Bar(
        x=df['Ticker'],
        y=df['Leverage_Ratio'],
        marker_color=colors,
        text=df['Leverage_Ratio'].apply(lambda x: f"{x:.2f}x"),
        textposition='auto',
    )])
    
    fig.update_layout(
        title="Solvency Sentinel: Net Debt / EBITDA",
        yaxis_title="Leverage Ratio (x)",
        template="plotly_dark",
        plot_bgcolor=BBG_DARK,
        paper_bgcolor=BBG_DARK,
        font_color=BBG_WHITE
    )
    
    # Threshold lines
    fig.add_hline(y=1.0, line_dash="dot", line_color="green", annotation_text="Healthy (<1.0x)")
    fig.add_hline(y=2.0, line_dash="dot", line_color="red", annotation_text="High Leverage (>2.0x)")
    
    return fig

def plot_earnings_quality(df):
    """
    Scatter plot showing FCF Conversion vs OCF to highlight earnings quality outliers.
    """
    fig = px.scatter(
        df,
        x='FCF_Conversion',
        y='OCF',
        color='Ticker',
        size='FCF',
        hover_data=['Ticker', 'FCF_Yield'],
        title="Earnings Quality: FCF Conversion vs. OCF",
        labels={'FCF_Conversion': 'FCF/Net Income (Conversion Ratio)'},
        template="plotly_dark"
    )
    
    # Add vertical line at 1.0 (100% conversion)
    fig.add_vline(x=1.0, line_dash="dot", line_color="white", annotation_text="100% Cash Conversion")
    
    fig.update_layout(
        plot_bgcolor=BBG_DARK,
        paper_bgcolor=BBG_DARK,
        font_color=BBG_WHITE
    )
    return fig

def plot_sustainability_risk(df):
    """
    Creates a bar chart for Dividend Sustainability Ratio (DSR) with risk-dynamic coloring.
    Green: Safe (>= 1.0)
    Amber: Caution (0.8 - 1.0)
    Red: High Risk (< 0.8)
    """
    # Assign colors based on DSR
    colors = []
    for val in df['DSR']:
        if val >= 1.0:
            colors.append('green')
        elif val >= 0.8:
            colors.append('orange')
        else:
            colors.append('red')

    fig = go.Figure(data=[go.Bar(
        x=df['Ticker'],
        y=df['DSR'],
        marker_color=colors,
        text=df['DSR'].apply(lambda x: f"{x:.2f}"),
        textposition='auto',
    )])

    fig.update_layout(
        title="Dividend Sustainability Ratio (DSR) - Stress Test",
        yaxis_title="DSR (Coverage Ratio)",
        template="plotly_dark",
        plot_bgcolor=BBG_DARK,
        paper_bgcolor=BBG_DARK,
        font_color=BBG_WHITE
    )
    
    # Add target line at 1.0
    fig.add_hline(y=1.0, line_dash="dash", line_color="white", annotation_text="Breakeven (1.0)")
    
    return fig

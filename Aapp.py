import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
from streamlit.components.v1 import html

# Page configuration
st.set_page_config(
    page_title="Forex Trading Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    :root {
        --primary: #2c3e50;
        --secondary: #34495e;
        --accent: #3498db;
        --success: #2ecc71;
        --danger: #e74c3c;
        --warning: #f39c12;
        --light-bg: #f8f9fa;
        --dark-text: #2c3e50;
        --light-text: #ecf0f1;
    }
    
    .stApp {
        background-color: var(--light-bg);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: var(--dark-text);
    }
    
    .navbar {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        padding: 15px 0;
        margin-bottom: 20px;
        border-radius: 0 0 10px 10px;
    }
    
    .navbar-brand {
        color: var(--light-text) !important;
        font-weight: 700;
        font-size: 24px;
        padding-left: 20px;
    }
    
    .card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .card-header {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border-radius: 10px 10px 0 0;
        font-weight: 600;
        padding: 15px 20px;
        margin: -20px -20px 20px -20px;
    }
    
    .suggestion-pill {
        display: inline-block;
        padding: 5px 12px;
        margin: 3px;
        border-radius: 20px;
        background-color: #e3f2fd;
        color: #1976d2;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .suggestion-pill:hover {
        background-color: #bbdefb;
        transform: translateY(-2px);
    }
    
    .win-row {
        background-color: rgba(46, 204, 113, 0.1) !important;
    }
    
    .loss-row {
        background-color: rgba(231, 76, 60, 0.1) !important;
    }
    
    .stats-box {
        text-align: center;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .stats-box h6 {
        font-size: 0.9rem;
        color: #7f8c8d;
    }
    
    .stats-box h3 {
        font-weight: 700;
        color: var(--dark-text);
    }
    
    .positive {
        background-color: rgba(46, 204, 113, 0.15);
    }
    
    .negative {
        background-color: rgba(231, 76, 60, 0.15);
    }
    
    .neutral {
        background-color: rgba(241, 196, 15, 0.15);
    }
    
    .trader-rank {
        display: flex;
        align-items: center;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 8px;
        background-color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .rank-number {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: var(--primary);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 15px;
    }
    
    .rank-1 {
        background-color: #f39c12;
    }
    
    .rank-2 {
        background-color: #7f8c8d;
    }
    
    .rank-3 {
        background-color: #cd7f32;
    }
    
    .performance-bar {
        height: 10px;
        border-radius: 5px;
        background-color: #ecf0f1;
        margin-top: 5px;
        overflow: hidden;
    }
    
    .performance-fill {
        height: 100%;
        border-radius: 5px;
        background: linear-gradient(90deg, var(--accent), var(--success));
    }
    
    .trader-details {
        flex-grow: 1;
    }
    
    .trader-name {
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .section-title {
        border-left: 4px solid var(--accent);
        padding-left: 10px;
        margin: 20px 0 15px;
        font-weight: 600;
    }
    
    .instrument-table {
        font-size: 0.9rem;
    }
    
    .progress {
        height: 10px;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Navigation bar
st.markdown("""
<div class="navbar">
    <div class="navbar-brand">
        <i class="fas fa-chart-line"></i> Forex Trading Analytics
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state for trades if not exists
if 'trades' not in st.session_state:
    st.session_state.trades = [
        {
            'date': '2023-10-08', 'trader': 'Waithaka', 'instrument': 'XAUUSD',
            'entry': 1820.50, 'sl': 1815.00, 'target': 1830.00, 'outcome': 'Target Hit'
        },
        {
            'date': '2023-10-07', 'trader': 'Wallace', 'instrument': 'USOIL',
            'entry': 89.30, 'sl': 88.50, 'target': 91.00, 'outcome': 'SL Hit'
        },
        {
            'date': '2023-10-06', 'trader': 'Max', 'instrument': 'BTCUSD',
            'entry': 27450.00, 'sl': 27200.00, 'target': 27800.00, 'outcome': 'Target Hit'
        },
        {
            'date': '2023-10-05', 'trader': 'Waithaka', 'instrument': 'EURUSD',
            'entry': 1.06250, 'sl': 1.06000, 'target': 1.06700, 'outcome': 'Target Hit'
        }
    ]

# Function to calculate trade metrics
def calculate_trade_metrics(trade):
    risk = abs(trade['entry'] - trade['sl'])
    reward = abs(trade['target'] - trade['entry'])
    rr_ratio = round(reward / risk, 2) if risk > 0 else 0
    result = 'Win' if trade['outcome'] == 'Target Hit' else 'Loss'
    
    return {
        'risk': risk,
        'reward': reward,
        'rr_ratio': rr_ratio,
        'result': result
    }

# Function to calculate trader statistics
def calculate_trader_stats(trades):
    traders = ['Waithaka', 'Wallace', 'Max']
    stats = {}
    
    for trader in traders:
        trader_trades = [t for t in trades if t['trader'] == trader]
        total_trades = len(trader_trades)
        wins = len([t for t in trader_trades if t['outcome'] == 'Target Hit'])
        win_rate = round((wins / total_trades) * 100, 1) if total_trades > 0 else 0
        
        stats[trader] = {
            'total_trades': total_trades,
            'wins': wins,
            'losses': total_trades - wins,
            'win_rate': win_rate
        }
    
    return stats

# Add new trade form
with st.expander("Add New Trade", expanded=True):
    st.markdown('<div class="card-header"><i class="fas fa-plus-circle me-2"></i>Add New Trade</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        trader = st.selectbox("Trader", ["", "Waithaka", "Wallace", "Max"], key="trader_input")
    with col2:
        instrument = st.text_input("Instrument", key="instrument_input")
        st.markdown("""
        <div class="mt-2">
            <small class="text-muted">Suggestions:</small>
            <div>
                <span class="suggestion-pill" onclick="document.querySelector('input[aria-label=\\'Instrument\\']').value='XAUUSD'">XAUUSD</span>
                <span class="suggestion-pill" onclick="document.querySelector('input[aria-label=\\'Instrument\\']').value='USOIL'">USOIL</span>
                <span class="suggestion-pill" onclick="document.querySelector('input[aria-label=\\'Instrument\\']').value='BTCUSD'">BTCUSD</span>
                <span class="suggestion-pill" onclick="document.querySelector('input[aria-label=\\'Instrument\\']').value='USTECH'">USTECH</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        trade_date = st.date_input("Date", value=date.today(), key="date_input")
    with col4:
        outcome = st.selectbox("Outcome", ["", "Target Hit", "SL Hit"], key="outcome_input")
    
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        entry = st.number_input("Entry Price", min_value=0.0, format="%.5f", key="entry_input")
    with col6:
        sl = st.number_input("Stop Loss (SL)", min_value=0.0, format="%.5f", key="sl_input")
    with col7:
        target = st.number_input("Target Price", min_value=0.0, format="%.5f", key="target_input")
    with col8:
        st.write("")  # Spacer
        st.write("")  # Spacer
        if st.button("Add Trade", type="primary", use_container_width=True):
            if trader and instrument and outcome and entry and sl and target:
                new_trade = {
                    'date': trade_date.strftime("%Y-%m-%d"),
                    'trader': trader,
                    'instrument': instrument,
                    'entry': entry,
                    'sl': sl,
                    'target': target,
                    'outcome': outcome
                }
                st.session_state.trades.append(new_trade)
                st.success("Trade successfully added!")
                st.rerun()
            else:
                st.error("Please fill all fields")

# Calculate statistics
trader_stats = calculate_trader_stats(st.session_state.trades)
ranked_traders = sorted(
    [(trader, stats) for trader, stats in trader_stats.items()],
    key=lambda x: x[1]['win_rate'],
    reverse=True
)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<h3 class="section-title">Trader Performance Rankings</h3>', unsafe_allow_html=True)
    
    for i, (trader, stats) in enumerate(ranked_traders):
        rank_class = f"rank-{i+1}" if i < 3 else ""
        st.markdown(f"""
        <div class="trader-rank">
            <div class="rank-number {rank_class}">{i+1}</div>
            <div class="trader-details">
                <div style="display: flex; justify-content: space-between;">
                    <span class="trader-name">{trader}</span>
                    <span class="win-rate">Win Rate: <strong>{stats['win_rate']}%</strong></span>
                </div>
                <div class="performance-bar">
                    <div class="performance-fill" style="width: {stats['win_rate']}%"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                    <small>Total Trades: {stats['total_trades']}</small>
                    <small>Wins: {stats['wins']} | Losses: {stats['losses']}</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Trading history table
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <i class="fas fa-table me-2"></i>Trading History
        </div>
    """, unsafe_allow_html=True)
    
    # Prepare table data
    table_data = []
    for trade in st.session_state.trades:
        metrics = calculate_trade_metrics(trade)
        row = {
            'Date': trade['date'],
            'Trader': trade['trader'],
            'Instrument': trade['instrument'],
            'Entry': f"{trade['entry']:.5f}",
            'SL': f"{trade['sl']:.5f}",
            'Target': f"{trade['target']:.5f}",
            'Risk': f"{metrics['risk']:.5f}",
            'Reward': f"{metrics['reward']:.5f}",
            'R/R Ratio': metrics['rr_ratio'],
            'Outcome': trade['outcome'],
            'Result': metrics['result']
        }
        table_data.append(row)
    
    # Display table with custom styling
    df = pd.DataFrame(table_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Result": st.column_config.TextColumn(
                "Result",
                help="Trade result",
                width="small"
            )
        }
    )

with col2:
    st.markdown('<h3 class="section-title">Performance Metrics</h3>', unsafe_allow_html=True)
    
    # Win rate chart
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <i class="fas fa-chart-pie me-2"></i>Overall Win Rate Distribution
        </div>
    """, unsafe_allow_html=True)
    
    if ranked_traders:
        labels = [f"{trader[0]} ({trader[1]['win_rate']}%)" for trader in ranked_traders]
        values = [trader[1]['win_rate'] for trader in ranked_traders]
        
        colors = ['rgba(243, 156, 18, 0.8)', 'rgba(127, 140, 141, 0.8)', 'rgba(205, 127, 50, 0.8)']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values,
            hole=0.5,
            marker_colors=colors
        )])
        
        fig.update_layout(
            height=300,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Trader of the month
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <i class="fas fa-trophy me-2"></i>Trader of the Month
        </div>
    """, unsafe_allow_html=True)
    
    if ranked_traders:
        best_trader = ranked_traders[0]
        st.markdown(f"""
        <div style="text-align: center;">
            <div class="rounded-circle bg-warning d-inline-flex align-items-center justify-content-center" style="width: 80px; height: 80px;">
                <i class="fas fa-trophy fa-2x text-white"></i>
            </div>
            <h4 class="mt-3">{best_trader[0]}</h4>
            <p class="text-muted">Best performance with {best_trader[1]['win_rate']}% win rate</p>
            <div class="stats-box positive">
                <h6>WIN RATE THIS MONTH</h6>
                <h3>{best_trader[1]['win_rate']}%</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Instrument performance
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <i class="fas fa-chart-bar me-2"></i>Instrument Performance by Trader
        </div>
    """, unsafe_allow_html=True)
    
    # Sample instrument performance data (would need to be calculated from trades in a real app)
    instrument_data = {
        'Instrument': ['XAUUSD', 'USOIL', 'BTCUSD', 'USTECH'],
        'Waithaka': [75, 80, 55, 70],
        'Wallace': [60, 50, 65, 40],
        'Max': [45, 70, 85, 75]
    }
    
    instrument_df = pd.DataFrame(instrument_data)
    st.dataframe(
        instrument_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Waithaka": st.column_config.ProgressColumn(
                "Waithaka",
                help="Win rate percentage",
                format="%d%%",
                min_value=0,
                max_value=100,
            ),
            "Wallace": st.column_config.ProgressColumn(
                "Wallace",
                help="Win rate percentage",
                format="%d%%",
                min_value=0,
                max_value=100,
            ),
            "Max": st.column_config.ProgressColumn(
                "Max",
                help="Win rate percentage",
                format="%d%%",
                min_value=0,
                max_value=100,
            )
        }
    )

# Footer
st.markdown("""
<footer class="bg-dark text-white text-center py-3 mt-4">
    <p class="mb-0">© 2023 Forex Trading Analytics. All rights reserved.</p>
</footer>
""", unsafe_allow_html=True)

# Add Font Awesome
st.markdown("""
<script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
""", unsafe_allow_html=True)
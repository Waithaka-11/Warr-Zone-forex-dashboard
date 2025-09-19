import streamlit as st
import pandas as pd
from datetime import date
import altair as alt
import gspread
from google.oauth2.service_account import Credentials

# =============================
# 🔗 GOOGLE SHEETS SETUP
# =============================

# Add your Google Sheet name here
SHEET_NAME = "ForexTrades"

# Streamlit secrets contain the service account JSON (added in step 2)
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)

# Open or create the sheet
try:
    sheet = client.open(SHEET_NAME).sheet1
except gspread.SpreadsheetNotFound:
    sh = client.create(SHEET_NAME)
    sh.share(None, perm_type="anyone", role="writer")
    sheet = sh.sheet1
    sheet.append_row(
        ["Date", "Trader", "Instrument", "Entry", "SL", "Target", "Outcome"]
    )

# Load data
def load_trades():
    records = sheet.get_all_records()
    return pd.DataFrame(records)

# Save data
def save_trade(row):
    sheet.append_row(row)

# =============================
# 🔵 DASHBOARD UI
# =============================
st.set_page_config(page_title="Forex Trading Analytics Dashboard",
                   page_icon="📈",
                   layout="wide")

st.title("📈 Forex Trading Analytics Dashboard")

trades_df = load_trades()

# Add new trade
with st.expander("➕ Add New Trade", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    trader = col1.selectbox("Trader", ["", "Waithaka", "Wallace", "Max"])
    instrument = col2.text_input("Instrument")
    trade_date = col3.date_input("Date", value=date.today())
    outcome = col4.selectbox("Outcome", ["", "Target Hit", "SL Hit"])

    col5, col6, col7 = st.columns(3)
    entry = col5.number_input("Entry Price", min_value=0.0, format="%.5f")
    sl = col6.number_input("Stop Loss (SL)", min_value=0.0, format="%.5f")
    target = col7.number_input("Target Price", min_value=0.0, format="%.5f")

    if st.button("Save Trade", type="primary"):
        if all([trader, instrument, outcome, entry, sl, target]):
            new_trade = [
                trade_date.strftime("%Y-%m-%d"),
                trader, instrument, entry, sl, target, outcome
            ]
            save_trade(new_trade)
            st.success("✅ Trade saved to Google Sheets!")
            st.experimental_rerun()
        else:
            st.error("⚠️ Please fill in all fields")

# Show trades
st.subheader("Trading History")
if trades_df.empty:
    st.info("No trades yet. Add your first trade above.")
else:
    st.dataframe(trades_df, use_container_width=True)

# Win-rate chart
if not trades_df.empty:
    stats = trades_df.groupby("Trader")["Outcome"].apply(
        lambda x: (x == "Target Hit").mean() * 100
    ).reset_index()
    stats.columns = ["Trader", "Win Rate (%)"]
    chart = alt.Chart(stats).mark_bar().encode(
        x="Trader",
        y="Win Rate (%)",
        color="Trader"
    )
    st.altair_chart(chart, use_container_width=True)

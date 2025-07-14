import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import os, json
from io import StringIO
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.title("Swing Trade Position Sizing & ATR Tool")

capital = st.number_input("Total Capital (₹)", value=100000.0, step=1000.0)
risk_pct = st.number_input("Risk % per Trade", value=1.0, step=0.1)

ticker = st.text_input("Enter NSE Stock Symbol (e.g., RELIANCE.NS)", value="RELIANCE.NS")
atr_multiplier = st.slider("ATR Multiplier", 1.0, 3.0, 1.5, 0.1)

use_auto = st.checkbox("Auto-fill Entry & Stop-Loss from Stock Data", value=True)

if ticker:
    try:
        @st.cache_data(ttl=3600)
        def get_stock_data(symbol):
            data = yf.download(symbol, period="30d", interval="1d")
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            return data.dropna()

        df = get_stock_data(ticker)
        df["ATR_14"] = df.ta.atr(length=14)
        latest_atr = df["ATR_14"].dropna().iloc[-1]

        if use_auto:
            entry = df["Close"].iloc[-1]
            stop_loss = entry - (latest_atr * atr_multiplier)
        else:
            entry = st.number_input("Manual Entry Price (₹)", value=390.0, step=1.0)
            stop_loss = st.number_input("Manual Stop-Loss Price (₹)", value=378.0, step=1.0)

        per_share_risk = abs(entry - stop_loss)
        risk_amount = capital * (risk_pct / 100)
        shares = int(risk_amount // per_share_risk) if per_share_risk > 0 else 0
        capital_used = shares * entry

        st.markdown("### 📊 Position Sizing Result")
        st.write(f"• Entry Price: ₹{entry:.2f}")
        st.write(f"• Stop-Loss Price: ₹{stop_loss:.2f}")
        st.write(f"• Risk per Share: ₹{per_share_risk:.2f}")
        st.write(f"• Shares to Buy: {shares}")
        st.write(f"• Capital Used: ₹{capital_used:,.2f}")
        st.success(f"✅ 14-Day ATR: ₹{latest_atr:.2f}")

        st.markdown("## 🌟 SL/TP Risk-Reward Projections")
        rr_ratios = [1, 1.5, 2, 2.5, 3]
        results = []
        for rr in rr_ratios:
            target = entry + (per_share_risk * rr)
            profit_per_share = target - entry
            total_profit = profit_per_share * shares
            results.append({
                "R:R": f"{rr}:1",
                "Target Price (₹)": f"{target:.2f}",
                "Profit/Share (₹)": f"{profit_per_share:.2f}",
                "Total Profit (₹)": f"{total_profit:.2f}"
            })
        st.dataframe(pd.DataFrame(results))

        def log_to_google_sheet(data_dict):
            try:
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                key_str = os.environ.get("GOOGLE_SHEETS_CRED")
                key_dict = json.loads(key_str)
                creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
                client = gspread.authorize(creds)
                sheet = client.open("Swing Trade Logs").sheet1
                sheet.append_row(list(data_dict.values()))
                return True
            except Exception as error:
                return error

        if st.button("📌 Log Trade to Google Sheets"):
            trade_data = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Stock": ticker,
                "Entry Price": entry,
                "Stop Loss": stop_loss,
                "Risk %": risk_pct,
                "Capital Used": capital_used,
                "Shares": shares,
                "Per Share Risk": per_share_risk,
                "Total Risk": risk_amount,
                "ATR": round(latest_atr, 2),
                "Suggested SL": round(stop_loss, 2)
            }

            result = log_to_google_sheet(trade_data)

            if result == True:
                st.success("✅ Trade logged to Google Sheets!")
            else:
                st.error(f"❌ Logging failed: {result}")

    except Exception as e:
        st.error(f"⚠️ Data fetch failed: {e}")

           

       

        


    

        
        

    




        




      

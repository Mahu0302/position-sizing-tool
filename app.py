import streamlit as st

st.title("Swing Trade Risk & Position Size Calculator")

capital = st.number_input("Total Capital (₹)", value=100000.0, step=1000.0)
risk_pct = st.number_input("Risk % per Trade", value=1.0, step=0.1)
entry = st.number_input("Entry Price (₹)", value=390.0, step=1.0)
stop_loss = st.number_input("Stop-Loss Price (₹)", value=378.0, step=1.0)

risk_amount = capital * (risk_pct / 100)
per_share_risk = abs(entry - stop_loss)
shares = int(risk_amount // per_share_risk)
capital_used = shares * entry

st.markdown("### 📊 Results")
st.write(f"• Max Risk: ₹{risk_amount:,.2f}")
st.write(f"• Risk per Share: ₹{per_share_risk:,.2f}")
st.write(f"• Shares to Buy: {shares}")
st.write(f"• Capital Used: ₹{capital_used:,.2f}")
import yfinance as yf
import pandas as pd
import talib

st.markdown("## 📏 ATR-Based Stop-Loss Suggestion")
ticker = st.text_input("Enter NSE Stock Symbol (e.g., BEL.NS)", value="BEL.NS")
atr_multiplier = st.slider("ATR Multiplier", 1.0, 3.0, 1.5, 0.1)

if ticker:
    try:
        df = yf.download(ticker, period="60d")
        df.dropna(inplace=True)
        atr = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
        latest_atr = atr.iloc[-1]
        suggested_sl = entry - (latest_atr * atr_multiplier)

        st.success(f"✅ 14-Day ATR: ₹{latest_atr:.2f}")
        st.write(f"📍 Suggested Stop-Loss (Entry − {atr_multiplier}×ATR): ₹{suggested_sl:.2f}")
    except Exception as e:
        st.error(f"Data fetch failed: {e}")

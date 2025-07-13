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

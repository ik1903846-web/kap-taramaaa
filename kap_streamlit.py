import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="BIST Finansal Tarama", page_icon="📊", layout="wide")
st.title("📊 BIST Finansal Tarama")

@st.cache_data(ttl=3600, show_spinner="Veriler yükleniyor...")
def fetch_all():
    url = "https://scanner.tradingview.com/turkey/scan"
    payload = {
        "columns": [
            "name","description","sector",
            "close","change","market_cap_basic",
            "price_earnings_ttm","price_book_ratio",
            "gross_margin","net_margin","return_on_equity",
            "revenue_change_ttm","earnings_change_ttm",
            "current_ratio","debt_to_equity",
            "performance_1y","performance_3y","performance_5y",
            "total_revenue","gross_profit","net_income",
            "free_cash_flow","ebitda","52_week_high",
        ],
        "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
        "range": [0, 700],
        "markets": ["turkey"],
        "options": {"lang": "tr"},
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://tr.tradingview.com",
        "Referer": "https://tr.tradingview.com/",
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    raw = resp.json()
    stocks = []
    for item in raw.get("data", []):
        d = item["d"]
        def g(i):
            try: return d[i]
            except: return None
        stocks.append({
            "Hisse": g(0), "Şirket": g(1), "Sektör": g(2) or "Diğer",
            "Fiyat": g(3), "Gün%": round(g(4) or 0,2),
            "Piyasa Değeri(B)": round(g(5)/1e9,2) if g(5) else None,
            "FK": round(g(6),1) if g(6) and g(6)>0 else None,
            "PD/DD": round(g(7),2) if g(7) and g(7)>0 else None,
            "Brüt Marj%": round(g(8) or 0,1),
            "Net Marj%": round(g(9) or 0,1),
            "ROE%": round(g(10) or 0,1),
            "Satış Büy%": round(g(11) or 0,1),
            "Kâr Büy%": round(g(12) or 0,1),
            "Cari Oran": round(g(13) or 0,2),
            "Borç/Özkaynak": round(g(14) or 0,2),
            "1Y Getiri%": round(g(15) or 0,1),
            "3Y Getiri%": round(g(16) or 0,1),
            "5Y Getiri%": round(g(17) or 0,1) if g(17) else None,
            "Hasılat(M)": round(g(18)/1e6,0) if g(18) else None,
            "Net Kâr(M)": round(g(20)/1e6,0) if g(20) else None,
            "FAVÖK(M)": round(g(22)/1e6,0) if g(22) else None,
        })
    return pd.DataFrame(stocks)

try:
    df = fetch_all()
    st.success(f"✅ {len(df)} hisse yüklendi")

    with st.sidebar:
        st.header("⚙️ Filtreler")
        hisse = st.text_input("Hisse Ara", placeholder="THYAO, GARAN")
        sektor = st.selectbox("Sektör", ["Tümü"] + sorted(df["Sektör"].dropna().unique().tolist()))
        min_roe = st.slider("Min ROE%", 0, 100, 0)
        min_marj = st.slider("Min Net Marj%", 0, 100, 0)

    filtered = df.copy()
    if hisse:
        aranan = [h.strip().upper() for h in hisse.split(",")]
        filtered = filtered[filtered["Hisse"].isin(aranan)]
    if sektor != "Tümü":
        filtered = filtered[filtered["Sektör"] == sektor]
    if min_roe > 0:
        filtered = filtered[filtered["ROE%"] >= min_roe]
    if min_marj > 0:
        filtered = filtered[filtered["Net Marj%"] >= min_marj]

    tab1, tab2, tab3 = st.tabs(["📊 Genel", "💰 Finansal", "📈 Getiri"])

    with tab1:
        cols = ["Hisse","Şirket","Sektör","Fiyat","FK","PD/DD","ROE%","Net Marj%"]
        st.dataframe(filtered[cols].reset_index(drop=True), use_container_width=True, height=600)

    with tab2:
        cols = ["Hisse","Şirket","Hasılat(M)","Net Kâr(M)","FAVÖK(M)"]
        st.dataframe(filtered[cols].reset_index(drop=True), use_container_width=True, height=600)

    with tab3:
        cols = ["Hisse","Şirket","1Y Getiri%","3Y Getiri%","5Y Getiri%","Satış Büy%","Kâr Büy%"]
        st.dataframe(filtered[cols].reset_index(drop=True), use_container_width=True, height=600)

    buf = BytesIO()
    filtered.to_excel(buf, index=False)
    st.download_button("📥 Excel İndir", buf.getvalue(), f"bist_{datetime.now().strftime('%Y%m%d')}.xlsx")

except Exception as e:
    st.error(f"Hata: {e}")

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="KAP Finansal Tarama", page_icon="📊", layout="wide")
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
            "revenue_annual_1","revenue_annual_2","revenue_annual_3","revenue_annual_4",
            "net_income_annual_1","net_income_annual_2","net_income_annual_3","net_income_annual_4",
            "ebitda_annual_1","ebitda_annual_2","ebitda_annual_3","ebitda_annual_4",
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

    yil = datetime.now().year
    stocks = []
    for item in raw.get("data", []):
        d = item["d"]
        def g(i):
            try: return d[i]
            except: return None

        stocks.append({
            "Hisse": g(0), "Şirket": g(1), "Sektör": g(2),
            "Fiyat": g(3), "Gün%": round(g(4) or 0, 2),
            "Piyasa Değeri(B)": round(g(5)/1e9, 2) if g(5) else None,
            "FK": round(g(6), 1) if g(6) and g(6)>0 else None,
            "PD/DD": round(g(7), 2) if g(7) and g(7)>0 else None,
            "Brüt Marj%": round(g(8) or 0, 1),
            "Net Marj%": round(g(9) or 0, 1),
            "ROE%": round(g(10) or 0, 1),
            "Satış Büy%": round(g(11) or 0, 1),
            "Kâr Büy%": round(g(12) or 0, 1),
            "Cari Oran": round(g(13) or 0, 2),
            "Borç/Özkaynak": round(g(14) or 0, 2),
            "1Y Getiri%": round(g(15) or 0, 1),
            "3Y Getiri%": round(g(16) or 0, 1),
            "5Y Getiri%": round(g(17) or 0, 1),
            "ATH Düşüş%": round(((g(3)-g(23))/g(23))*100, 1) if g(3) and g(23) else None,
            # Hasılat (5 yıl)
            f"Hasılat {yil}(M)": round(g(18)/1e6, 0) if g(18) else None,
            f"Hasılat {yil-1}(M)": round(g(24)/1e6, 0) if g(24) else None,
            f"Hasılat {yil-2}(M)": round(g(25)/1e6, 0) if g(25) else None,
            f"Hasılat {yil-3}(M)": round(g(26)/1e6, 0) if g(26) else None,
            f"Hasılat {yil-4}(M)": round(g(27)/1e6, 0) if g(27) else None,
            # Net Kâr (5 yıl)
            f"Net Kâr {yil}(M)": round(g(20)/1e6, 0) if g(20) else None,
            f"Net Kâr {yil-1}(M)": round(g(28)/1e6, 0) if g(28) else None,
            f"Net Kâr {yil-2}(M)": round(g(29)/1e6, 0) if g(29) else None,
            f"Net Kâr {yil-3}(M)": round(g(30)/1e6, 0) if g(30) else None,
            f"Net Kâr {yil-4}(M)": round(g(31)/1e6, 0) if g(31) else None,
            # FAVÖK (5 yıl)
            f"FAVÖK {yil}(M)": round(g(22)/1e6, 0) if g(22) else None,
            f"FAVÖK {yil-1}(M)": round(g(32)/1e6, 0) if g(32) else None,
            f"FAVÖK {yil-2}(M)": round(g(33)/1e6, 0) if g(33) else None,
            f"FAVÖK {yil-3}(M)": round(g(34)/1e6, 0) if g(34) else None,
            f"FAVÖK {yil-4}(M)": round(g(35)/1e6, 0) if g(35) else None,
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

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Genel", "💰 Hasılat", "🟢 Net Kâr", "📈 FAVÖK"])

    yil = datetime.now().year

    with tab1:
        goster = ["Hisse","Şirket","Sektör","Fiyat","FK","PD/DD","ROE%","Net Marj%","Satış Büy%","Kâr Büy%","ATH Düşüş%","5Y Getiri%"]
        st.dataframe(filtered[[c for c in goster if c in filtered.columns]].reset_index(drop=True), use_container_width=True, height=600)

    with tab2:
        cols = ["Hisse","Şirket"] + [f"Hasılat {yil-i}(M)" for i in range(5)]
        st.dataframe(filtered[[c for c in cols if c in filtered.columns]].reset_index(drop=True), use_container_width=True, height=600)

    with tab3:
        cols = ["Hisse","Şirket"] + [f"Net Kâr {yil-i}(M)" for i in range(5)]
        st.dataframe(filtered[[c for c in cols if c in filtered.columns]].reset_index(drop=True), use_container_width=True, height=600)

    with tab4:
        cols = ["Hisse","Şirket"] + [f"FAVÖK {yil-i}(M)" for i in range(5)]
        st.dataframe(filtered[[c for c in cols if c in filtered.columns]].reset_index(drop=True), use_container_width=True, height=600)

    buf = BytesIO()
    filtered.to_excel(buf, index=False)
    st.download_button("📥 Excel İndir", buf.getvalue(), f"bist_{datetime.now().strftime('%Y%m%d')}.xlsx")

except Exception as e:
    st.error(f"Hata: {e}")

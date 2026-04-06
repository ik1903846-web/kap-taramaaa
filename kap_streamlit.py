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
            "Borç​​​​​​​​​​​​​​​​

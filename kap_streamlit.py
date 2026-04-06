import streamlit as st
import requests
import pandas as pd
import io

st.set_page_config(page_title="KAP Finansal Tarama", page_icon="📊", layout="wide")
st.title("📊 KAP Finansal Tarama")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://kap.org.tr/tr/kalem-karsilastirma",
    "Accept": "*/*",
}

YILLAR = [2020, 2021, 2022, 2023, 2024]
DONEMLER = {"Yıllık": 4, "9 Aylık": 3, "6 Aylık": 2, "3 Aylık": 1}

with st.sidebar:
    st.header("⚙️ Filtreler")
    secili_yillar = st.multiselect("Yıllar", YILLAR, default=YILLAR)
    donem = st.selectbox("Dönem", list(DONEMLER.keys()))
    hisse_filtre = st.text_input("Hisse Filtrele", placeholder="THYAO, GARAN")

if st.button("🚀 Veriyi Çek", type="primary"):
    url = "https://kap.org.tr/tr/api/kalemKarsilastirma"
    payload = {
        "sirketTipi": "İşlem Gören Şirketler",
        "yillar": secili_yillar,
        "donem": DONEMLER[donem],
        "kalemler": ["Hasılat", "Net Dönem Kârı (Zararı)", "Özkaynaklar", "Toplam Varlıklar", "Toplam Kısa Vadeli Yükümlülükler", "Toplam Uzun Vadeli Yükümlülükler"]
    }
    with st.spinner("KAP'tan veriler çekiliyor..."):
        try:
            resp = requests.post(url, json=payload, headers=HEADERS, timeout=60)
            st.write("Status:", resp.status_code)
            st.write("Content-Type:", resp.headers.get("Content-Type"))
            st.write("İlk 500 karakter:", resp.text[:500])
        except Exception as e:
            st.error(f"Hata: {e}")

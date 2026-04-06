import streamlit as st
import requests
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="KAP Finansal Tarama", page_icon="📊", layout="wide")
st.title("📊 KAP Finansal Tarama")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://kap.org.tr/tr/kalem-karsilastirma",
    "Accept": "application/json, text/plain, */*",
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
            df = pd.read_excel(io.BytesIO(resp.content), skiprows=5)
            df.columns = df.columns.str.strip()
            if hisse_filtre.strip():
                aranan = [h.strip().upper() for h in hisse_filtre.split(",")]
                df = df[df["Şirket"].str.upper().isin(aranan)]
            st.success(f"✅ {len(df)} kayıt bulundu")
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 CSV İndir", csv, "kap.csv", "text/csv")
        except Exception as e:
            st.error(f"Hata: {e}")

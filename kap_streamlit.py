import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="KAP Finansal Tarama", page_icon="📊", layout="wide")
st.title("📊 KAP Finansal Tarama")

st.info("""
**Nasıl Kullanılır:**
1. [KAP kalem-karsilastirma](https://kap.org.tr/tr/kalem-karsilastirma) sayfasına git
2. Yıl, Dönem ve Kalemleri seç
3. **İndir** butonuna bas
4. İndirilen Excel'i aşağıya yükle
""")

dosya = st.file_uploader("KAP Excel Dosyasını Yükle", type=["xlsx"])

if dosya:
    df = pd.read_excel(dosya, skiprows=5)
    df = df.dropna(how="all")
    df.columns = df.columns.str.strip()

    st.success(f"✅ {len(df)} kayıt yüklendi")

    with st.sidebar:
        st.header("⚙️ Filtreler")
        hisse = st.text_input("Hisse/Şirket Ara", placeholder="THYAO")
        if "Yıl" in df.columns:
            yillar = ["Tümü"] + sorted(df["Yıl"].dropna().unique().tolist(), reverse=True)
            secili_yil = st.selectbox("Yıl", yillar)
        if "Periyot" in df.columns:
            donemler = ["Tümü"] + sorted(df["Periyot"].dropna().unique().tolist())
            secili_donem = st.selectbox("Dönem", donemler)

    filtered = df.copy()
    if hisse:
        filtered = filtered[filtered.apply(lambda r: hisse.upper() in str(r.values).upper(), axis=1)]
    if "Yıl" in df.columns and secili_yil != "Tümü":
        filtered = filtered[filtered["Yıl"] == secili_yil]
    if "Periyot" in df.columns and secili_donem != "Tümü":
        filtered = filtered[filtered["Periyot"] == secili_donem]

    st.dataframe(filtered.reset_index(drop=True), use_container_width=True, height=600)

    buf = BytesIO()
    filtered.to_excel(buf, index=False)
    st.download_button("📥 Excel İndir", buf.getvalue(), "kap_analiz.xlsx")

import streamlit as st
import requests
import pandas as pd
import re
import io
import time
from datetime import datetime

st.set_page_config(page_title="KAP Finansal Tarama", page_icon="📊", layout="wide")

BASE_URL = "https://kap.org.tr"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://kap.org.tr/tr/kalem-karsilastirma",
}

KALEMLER = {
    "Hasılat": "kpy41_acc5_hasilat",
    "Net Dönem Kârı": "kpy41_acc5_donem_kari_zarari",
    "Özkaynaklar": "kpy41_acc5_ozkaynaklar",
    "Toplam Varlıklar": "kpy41_acc5_toplam_varliklar",
    "Kısa Vadeli Yük.": "kpy41_acc5_kisa_vadeli_yukumlulukler",
    "Uzun Vadeli Yük.": "kpy41_acc5_uzun_vadeli_yukumlulukler",
}
def kalem_cek(kalem_kodu):
    url = f"{BASE_URL}/tr/tumKalemler/{kalem_kodu}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', resp.text, re.DOTALL)
        buyuk = [s for s in scripts if len(s) > 100_000]
        if not buyuk:
            return {}
        unescaped = buyuk[0].replace('\\"', '"')
        all_ch = re.findall(r'"children":"([^"]+)"', unescaped)
        results = {}
        i = 0
        while i < len(all_ch) - 2:
            val = all_ch[i]
            if re.match(r'^[A-Z]{3,6}$', val) and val not in ('HTML','HEAD','BODY','TR','TD','TH'):
                try:
                    deger = float(all_ch[i+2].replace('.','').replace(',','.'))
                    results[val] = deger
                except:
                    pass
                i += 3
            else:
                i += 1
        return results
    except:
        return {}
st.title("📊 KAP Finansal Tarama")

secili_kalemler = st.multiselect(
    "Kalemler", list(KALEMLER.keys()),
    default=["Hasılat", "Net Dönem Kârı", "Özkaynaklar", "Toplam Varlıklar"]
)

hisse_filtre = st.text_input("Hisse Filtrele (boş=hepsi)", placeholder="THYAO, GARAN")

if st.button("🚀 Veriyi Çek", type="primary"):
    tum = {}
    for kalem in secili_kalemler:
        with st.spinner(f"{kalem} çekiliyor..."):
            veri = kalem_cek(KALEMLER[kalem])
            for ticker, deger in veri.items():
                tum.setdefault(ticker, {})[kalem] = deger
            time.sleep(1)

    df = pd.DataFrame(tum).T.reset_index()
    df.columns = ["Hisse"] + [c for c in df.columns if c != "index"]

    if hisse_filtre.strip():
        aranan = [h.strip().upper() for h in hisse_filtre.split(",")]
        df = df[df["Hisse"].isin(aranan)]

    st.success(f"{len(df)} hisse bulundu")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 CSV İndir", csv, "kap_veri.csv", "text/csv")

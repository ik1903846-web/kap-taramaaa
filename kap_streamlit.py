import streamlit as st
import requests
import pandas as pd
import re
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="KAP Finansal Tarama", page_icon="📊", layout="wide")
st.title("📊 KAP Finansal Tarama")

KALEMLER = {
    "Hasılat": "kpy41_acc5_hasilat",
    "Net Kâr": "kpy41_acc5_donem_kari_zarari",
    "Özkaynaklar": "kpy41_acc5_ozkaynaklar",
    "Toplam Varlıklar": "kpy41_acc5_toplam_varliklar",
    "FDO%": "kpy41_acc5_fiili_dolasimdaki_pay",
}

def kalem_cek(kod):
    url = f"https://kap.org.tr/tr/tumKalemler/{kod}"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', resp.text, re.DOTALL)
    buyuk = [s for s in scripts if len(s) > 100000]
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

if st.button("🚀 Veriyi Çek", type="primary"):
    tum = {}
    for ad, kod in KALEMLER.items():
        with st.spinner(f"{ad} çekiliyor..."):
            veri = kalem_cek(kod)
            for ticker, deger in veri.items():
                tum.setdefault(ticker, {})[ad] = deger

    df = pd.DataFrame(tum).T.reset_index()
    df = df.rename(columns={"index": "Hisse"})
    st.success(f"✅ {len(df)} hisse bulundu")
    st.dataframe(df, use_container_width=True, height=600)

    buf = BytesIO()
    df.to_excel(buf, index=False)
    st.download_button("📥 Excel İndir", buf.getvalue(), "kap.xlsx")

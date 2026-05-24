import streamlit as st
import pandas as pd
import yfinance as yf
import twstock

st.set_page_config(layout="wide")
st.title("🦅 少年操盤手：台股地毯式搜索戰情室")

@st.cache_data
def get_stock_data():
    all_codes = twstock.codes
    # 掃描前 300 檔上市股
    target_stocks = [f"{code}.TW" for code in all_codes if all_codes[code].market == '上市'][:300]
    results = []
    
    for stock_id in target_stocks:
        try:
            ticker = yf.Ticker(stock_id)
            info = ticker.info
            eps = info.get('trailingEps', 0)
            gross_margin = info.get('grossMargins', 0)
            market_cap = info.get('marketCap', 0)
            pe = info.get('trailingPE', 0)
            
            if eps > 0.5 and gross_margin > 0.10:
                results.append({
                    "代碼": stock_id,
                    "中文名稱": info.get('shortName', '未知'),
                    "EPS (元)": round(eps, 2),
                    "毛利率 (%)": round(gross_margin * 100, 1),
                    "本益比": round(pe, 1),
                    "市值 (億)": round(market_cap / 100000000, 1)
                })
        except:
            continue
    return pd.DataFrame(results)

df = get_stock_data()

st.sidebar.header("🔍 戰術篩選器")
min_eps = st.sidebar.slider("最低 EPS", 0.0, 10.0, 0.5)
df_filtered = df[df["EPS (元)"] >= min_eps]

st.dataframe(df_filtered, use_container_width=True)
st.success(f"報告指揮官：已鎖定 {len(df_filtered)} 檔符合條件的黃金標的！")

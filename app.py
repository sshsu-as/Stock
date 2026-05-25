import streamlit as st
import twstock
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# 優化介面設定
st.set_page_config(page_title="專業操盤手戰情室", layout="wide")

# 加入一些簡單的 CSS 讓介面更清爽
st.markdown("""
    <style>
    .stApp { background-color: #f5f7f9; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦅 少年操盤手：全能精算戰情室")
st.subheader("篩選出市場中的潛力鑽石")

@st.cache_data(ttl=3600)
def fetch_stock_data(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.TW")
        info = ticker.info
        return {
            "代號": symbol,
            "名稱": info.get("shortName", "未知"),
            "EPS": info.get("trailingEps", 0),
            "毛利率": info.get("grossMargins", 0) * 100,
            "本益比": info.get("forwardPE", 0),
            "殖利率": info.get("dividendYield", 0) * 100,
            "股價淨值比": info.get("priceToBook", 0),
            "市值(億)": info.get("marketCap", 0) / 100000000,
            "負債比率": info.get("debtToEquity", 0),
            "流動比率": info.get("currentRatio", 0)
        }
    except:
        return None

# 側邊欄優化：分區管理
st.sidebar.header("🔥 貪心篩選參數")
col1, col2 = st.sidebar.columns(2)
with col1:
    min_eps = st.slider("最低 EPS", 0.0, 15.0, 2.0)
    min_margin = st.slider("最低毛利率 (%)", 0, 80, 20)
    max_pe = st.slider("最高本益比", 5, 50, 20)
with col2:
    min_yield = st.slider("最低殖利率 (%)", 0.0, 10.0, 3.0)
    max_pb = st.slider("最高股價淨值比", 0.5, 10.0, 3.0)
    min_current_ratio = st.slider("最低流動比率", 0.0, 5.0, 1.0)

if st.button("🚀 啟動全能掃描"):
    with st.spinner("正在為你挖掘市場中的鑽石..."):
        all_symbols = list(twstock.codes.keys())[:200]
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(fetch_stock_data, all_symbols))
        
        data = [r for r in results if r is not None and r["市值(億)"] > 0]
        df = pd.DataFrame(data)
        
        filtered_df = df[
            (df["EPS"] >= min_eps) & 
            (df["毛利率"] >= min_margin) &
            (df["本益比"] <= max_pe) &
            (df["殖利率"] >= min_yield) &
            (df["股價淨值比"] <= max_pb) &
            (df["流動比率"] >= min_current_ratio)
        ]
        
        if not filtered_df.empty:
            st.success(f"發現 {len(filtered_df)} 檔全能好公司！")
            st.dataframe(filtered_df.sort_values(by="EPS", ascending=False), use_container_width=True)
            
            # --- 一鍵下載功能 ---
            csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 下載篩選結果 CSV",
                data=csv,
                file_name='stock_results.csv',
                mime='text/csv',
            )
        else:
            st.error("找不到符合條件的公司！你的標準可能太嚴格囉！")

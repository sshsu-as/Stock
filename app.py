import streamlit as st
import twstock
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# 設定頁面
st.set_page_config(page_title="專業台股篩選器", layout="wide")
st.title("📈 高效能台股篩選器")

# 1. 優化：使用快取減少重複抓取
@st.cache_data(ttl=3600)
def fetch_stock_data(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.TW")
        info = ticker.info
        return {
            "代號": symbol,
            "本益比": info.get("forwardPE", 0),
            "EPS": info.get("trailingEps", 0),
            "毛利率": info.get("grossMargins", 0) * 100,
            "殖利率": info.get("dividendYield", 0) * 100
        }
    except:
        return None

# 2. 優化：多線程處理，速度提升 5-10 倍
def get_all_stocks_data(stock_list):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_stock_data, stock_list))
    return [r for r in results if r is not None]

# 側邊欄設定
st.sidebar.header("篩選參數")
min_eps = st.sidebar.slider("最低 EPS", 0.0, 10.0, 0.5)
min_margin = st.sidebar.slider("最低毛利率 (%)", 0, 50, 10)

if st.button("開始掃描"):
    with st.spinner("正在高速抓取資料中..."):
        all_symbols = twstock.codes.keys() # 這裡可以縮小範圍到你感興趣的產業
        data = get_all_stocks_data(list(all_symbols)[:100]) # 示範取前100檔
        df = pd.DataFrame(data)
        
        # 篩選邏輯
        filtered_df = df[(df["EPS"] >= min_eps) & (df["毛利率"] >= min_margin)]
        
        st.success(f"篩選完成！共找到 {len(filtered_df)} 檔標的")
        st.dataframe(filtered_df.sort_values(by="EPS", ascending=False), use_container_width=True)

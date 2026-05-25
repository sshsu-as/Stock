import streamlit as st
import twstock
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="專業操盤手戰情室", layout="wide")
st.title("🦅 少年操盤手：全能精算戰情室")

@st.cache_data(ttl=3600)
def fetch_stock_data(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.TW")
        info = ticker.info
        # 使用 .get(key, default) 確保一定有值
        return {
            "代號": symbol,
            "名稱": info.get("shortName", "未知"),
            "EPS": info.get("trailingEps") or 0.0,
            "毛利率": (info.get("grossMargins") or 0.0) * 100,
            "本益比": info.get("forwardPE") or 999.0, # 若無資料設為極高，篩選時自然會被過濾
            "殖利率": (info.get("dividendYield") or 0.0) * 100,
            "股價淨值比": info.get("priceToBook") or 999.0,
            "市值(億)": (info.get("marketCap") or 0.0) / 100000000,
            "負債比率": info.get("debtToEquity") or 999.0,
            "流動比率": info.get("currentRatio") or 0.0
        }
    except:
        return None

st.sidebar.header("🔥 貪心篩選參數")
min_eps = st.sidebar.slider("最低 EPS", 0.0, 15.0, 2.0)
min_margin = st.sidebar.slider("最低毛利率 (%)", 0, 80, 20)
max_pe = st.sidebar.slider("最高本益比", 5, 50, 20)
min_yield = st.sidebar.slider("最低殖利率 (%)", 0.0, 10.0, 3.0)
max_pb = st.sidebar.slider("最高股價淨值比", 0.5, 10.0, 3.0)
max_debt = st.sidebar.slider("最高負債比率", 0.0, 500.0, 100.0)
min_current_ratio = st.sidebar.slider("最低流動比率", 0.0, 5.0, 1.0)

if st.button("🚀 啟動全能掃描"):
    with st.spinner("正在為你挖掘市場中的鑽石..."):
        all_symbols = list(twstock.codes.keys())[:200]
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(fetch_stock_data, all_symbols))
        
        data = [r for r in results if r is not None]
        df = pd.DataFrame(data)
        
        # 篩選前再次確保資料存在
        try:
            filtered_df = df[
                (df["EPS"] >= min_eps) & 
                (df["毛利率"] >= min_margin) &
                (df["本益比"] <= max_pe) &
                (df["殖利率"] >= min_yield) &
                (df["股價淨值比"] <= max_pb) &
                (df["負債比率"] <= max_debt) &
                (df["流動比率"] >= min_current_ratio)
            ]
            
            if not filtered_df.empty:
                st.success(f"發現 {len(filtered_df)} 檔全能好公司！")
                st.dataframe(filtered_df, use_container_width=True)
                csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下載篩選結果 CSV", csv, "stock_results.csv", "text/csv")
            else:
                st.warning("找不到符合這麼嚴苛條件的公司！標準放寬一點吧。")
        except Exception as e:
            st.error(f"資料處理發生錯誤，請稍後再試。錯誤訊息：{e}")

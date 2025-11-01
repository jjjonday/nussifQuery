import streamlit as st
import requests
import pandas as pd

def fetch_polygon_data(api_key, ticker, multiplier, timespan, start_date, end_date):
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}"
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": api_key}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json().get("results", [])
    df = pd.DataFrame(data)
    if not df.empty:
        df["ticker"] = ticker
        df = df.fillna(method="ffill").fillna(method="bfill")
    return df

def main():
    st.title("📊 PolyQuery Data Downloader")

    tab1, tab2, tab3 = st.tabs(["🔍 Download Data", "📂 Saved Files", "📘 Ticker Reference"])

    # === TAB 1: Download Data ===
    with tab1:
        api_key = st.text_input("Enter your Polygon API Key:", type="password")
        tickers = st.text_area("Enter tickers (comma-separated):", "AAPL,MSFT,TSLA")
        asset_class = st.selectbox("Select asset class:", ["stocks", "crypto", "fx"])
        multiplier = st.number_input("Multiplier:", min_value=1, value=1)
        timespan = st.selectbox("Timespan:", ["minute", "hour", "day", "week", "month"])
        start_date = st.date_input("Start date:")
        end_date = st.date_input("End date:")
        combine = st.checkbox("Combine all tickers into one CSV", value=True)

        if st.button("Fetch & Download"):
            all_data = []
            tickers_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
            for ticker in tickers_list:
                df = fetch_polygon_data(api_key, ticker, multiplier, timespan, start_date, end_date)
                if not df.empty:
                    all_data.append(df)
                    if not combine:
                        df.to_csv(f"{ticker}_data.csv", index=False)
                        st.success(f"Saved {ticker}_data.csv")

            if combine and all_data:
                combined_df = pd.concat(all_data)
                combined_df.to_csv("combined_data.csv", index=False)
                st.success("✅ Combined CSV saved as combined_data.csv")

    # === TAB 2: Saved Files ===
    with tab2:
        st.header("💾 Previously Saved Files")
        st.write("This section can later display files you've downloaded or saved locally.")

    # === TAB 3: Ticker Reference ===
    with tab3:
        st.header("📘 Valid Tickers Reference")
        st.markdown("""
        ### 📈 **Stocks**
        AAPL — Apple  
        MSFT — Microsoft  
        TSLA — Tesla  
        NVDA — Nvidia  
        AMZN — Amazon  

        ### 💰 **Crypto**
        X:BTCUSD — Bitcoin  
        X:ETHUSD — Ethereum  
        X:SOLUSD — Solana  

        ### 🌍 **FX**
        C:USDEUR — USD/EUR  
        C:USDJPY — USD/JPY  
        C:USDSGD — USD/SGD  
        
        ---
        📝 *Copy any ticker above into the “Download Data” tab.*
        """)

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import requests
from io import BytesIO


# =======================
# Helper: Fetch data from Polygon API
# =======================
def fetch_polygon_data(api_key, ticker, multiplier, timespan, start_date, end_date):
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}"
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 50000,
        "apiKey": api_key
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        st.error(f"Failed to fetch data for {ticker}: {response.text}")
        return pd.DataFrame()

    data = response.json().get("results", [])
    df = pd.DataFrame(data)

    if not df.empty:
        df["ticker"] = ticker
        # Fill NAs without modifying columns
        df = df.fillna(method="ffill").fillna(method="bfill")

    return df


# =======================
# Streamlit App
# =======================
def main():
    st.set_page_config(page_title="PolyQuery", page_icon="📊", layout="centered")
    st.title("📊 PolyQuery Data Downloader")

    tab1, tab2 = st.tabs(["🔍 Download Data", "📘 Ticker Reference"])

    # === TAB 1: Download Data ===
    with tab1:
        st.subheader("Retrieve data from Polygon.io")

        api_key = st.text_input("Enter your Polygon API Key:", type="password")

        tickers = st.text_area(
            "Enter tickers (comma-separated):",
            "AAPL,MSFT,TSLA",
            help="Example: AAPL,MSFT,TSLA or X:BTCUSD,X:ETHUSD"
        )

        asset_class = st.selectbox("Select asset class:", ["stocks", "crypto", "fx"])
        multiplier = st.number_input("Multiplier:", min_value=1, value=1)
        timespan = st.selectbox(
            "Timespan:",
            ["minute", "hour", "day", "week", "month"],
            index=2
        )
        start_date = st.date_input("Start date:")
        end_date = st.date_input("End date:")
        combine = st.checkbox("Combine all tickers into one CSV", value=True)

        if st.button("📥 Fetch Data"):
            if not api_key:
                st.warning("⚠️ Please enter your Polygon API key.")
                return

            tickers_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
            all_data = []

            st.info("Fetching data... This may take a few seconds ⏳")

            for ticker in tickers_list:
                df = fetch_polygon_data(
                    api_key, ticker, multiplier, timespan, start_date, end_date
                )
                if not df.empty:
                    all_data.append(df)
                    st.success(f"✅ Retrieved data for {ticker} ({len(df)} rows)")
                else:
                    st.warning(f"No data returned for {ticker}.")

            # === Export ===
            if all_data:
                if combine:
                    combined_df = pd.concat(all_data)
                    buffer = BytesIO()
                    combined_df.to_csv(buffer, index=False)
                    buffer.seek(0)
                    st.download_button(
                        label="⬇️ Download Combined CSV",
                        data=buffer,
                        file_name="combined_data.csv",
                        mime="text/csv",
                    )
                else:
                    st.markdown("### 📂 Download Individual Ticker CSVs")
                    for df in all_data:
                        ticker = df["ticker"].iloc[0]
                        buffer = BytesIO()
                        df.to_csv(buffer, index=False)
                        buffer.seek(0)
                        st.download_button(
                            label=f"⬇️ Download {ticker}_data.csv",
                            data=buffer,
                            file_name=f"{ticker}_data.csv",
                            mime="text/csv",
                        )
            else:
                st.error("No valid data fetched. Check your tickers or date range.")

    # === TAB 2: Ticker Reference ===
    with tab2:
        st.header("📘 Valid Tickers Reference")
        st.markdown("""
        Here are some **sample tickers** you can copy directly into the input box.

        ### 📈 **Stocks**
        - AAPL — Apple  
        - MSFT — Microsoft  
        - TSLA — Tesla  
        - NVDA — Nvidia  
        - AMZN — Amazon  

        ### 💰 **Crypto**
        - X:BTCUSD — Bitcoin  
        - X:ETHUSD — Ethereum  
        - X:SOLUSD — Solana  

        ### 🌍 **Forex (FX)**
        - C:USDEUR — USD/EUR  
        - C:USDJPY — USD/JPY  
        - C:USDSGD — USD/SGD  

        ---
        📝 *Polygon uses prefixes:*  
        - Stocks → Plain ticker (e.g., AAPL)  
        - Crypto → `X:` prefix (e.g., X:BTCUSD)  
        - FX → `C:` prefix (e.g., C:USDSGD)
        """)


if __name__ == "__main__":
    main()

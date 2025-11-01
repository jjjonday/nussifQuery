import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

# ---------------------------
# Fetch Data Function
# ---------------------------
def fetch_polygon_data(ticker, multiplier, timespan, from_date, to_date, api_key):
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
    params = {"apiKey": api_key}
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    if "results" not in data or not data["results"]:
        st.warning(f"No data found for {ticker}")
        return None

    df = pd.DataFrame(data["results"])
    df["ticker"] = ticker
    df.dropna(inplace=True)
    df.fillna(method="ffill", inplace=True)
    return df


# ---------------------------
# Streamlit App UI
# ---------------------------
st.set_page_config(page_title="Polygon Data Downloader", layout="wide")
st.title("📊 Polygon Data Downloader")

st.markdown("""
This tool fetches **historical aggregate data** from [Polygon.io](https://polygon.io) for multiple tickers and asset classes.  
You can choose to combine all tickers into one CSV or download each separately.
""")

# Sidebar inputs
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("🔑 Polygon API Key", type="password")
    tickers_input = st.text_area("📈 Enter tickers (comma-separated)", "AAPL, C:EURUSD, X:BTCUSD, I:SPX")
    multiplier = st.number_input("⏱️ Multiplier", min_value=1, max_value=60, value=1)
    timespan = st.selectbox("🕒 Timespan", ["minute", "hour", "day", "week", "month"])
    from_date = st.date_input("📅 From Date", value=datetime(2024, 1, 1))
    to_date = st.date_input("📅 To Date", value=datetime(2024, 12, 31))
    combine = st.checkbox("Combine all tickers into one CSV", value=True)

# Run button
if st.button("🚀 Fetch and Download Data"):
    if not api_key or not tickers_input.strip():
        st.error("Please provide your API key and at least one ticker.")
    else:
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
        all_data = []

        st.info(f"Fetching data for {len(tickers)} tickers...")

        for ticker in tickers:
            with st.spinner(f"Fetching {ticker}..."):
                try:
                    df = fetch_polygon_data(
                        ticker=ticker,
                        multiplier=multiplier,
                        timespan=timespan,
                        from_date=from_date,
                        to_date=to_date,
                        api_key=api_key
                    )
                    if df is not None:
                        if combine:
                            all_data.append(df)
                        else:
                            csv_buffer = io.StringIO()
                            df.to_csv(csv_buffer, index=False)
                            st.download_button(
                                label=f"⬇️ Download {ticker} CSV",
                                data=csv_buffer.getvalue(),
                                file_name=f"{ticker}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                except Exception as e:
                    st.error(f"❌ Failed to fetch {ticker}: {e}")

        # Combine output
        if combine and all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            csv_buffer = io.StringIO()
            combined_df.to_csv(csv_buffer, index=False)
            st.success("✅ Combined data ready!")
            st.dataframe(combined_df.head(20))
            st.download_button(
                label="⬇️ Download Combined CSV",
                data=csv_buffer.getvalue(),
                file_name=f"combined_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

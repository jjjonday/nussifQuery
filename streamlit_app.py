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
# Streamlit App Layout
# ---------------------------
st.set_page_config(page_title="Polygon Data Downloader", layout="wide")
st.title("📊 Polygon Data Downloader")

tabs = st.tabs(["📁 Ticker Library", "⬇️ Data Downloader"])

# ---------------------------
# TAB 1: Ticker Library
# ---------------------------
with tabs[0]:
    st.header("📁 Upload Your Ticker Library")

    st.markdown("""
    Upload a **CSV or Excel file** containing valid tickers to use in your data downloads.  
    The file should have **one column** named `ticker`.
    """)

    uploaded_file = st.file_uploader("Upload Ticker Library", type=["csv", "xlsx"])

    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            ticker_library = pd.read_csv(uploaded_file)
        else:
            ticker_library = pd.read_excel(uploaded_file)

        if "ticker" not in ticker_library.columns:
            st.error("❌ The uploaded file must have a column named 'ticker'.")
        else:
            st.success(f"✅ Loaded {len(ticker_library)} tickers successfully!")
            st.dataframe(ticker_library)

            # Store ticker library in session
            st.session_state["ticker_library"] = ticker_library["ticker"].dropna().tolist()
    else:
        st.info("Please upload a ticker library to begin.")

# ---------------------------
# TAB 2: Data Downloader
# ---------------------------
with tabs[1]:
    st.header("⬇️ Polygon Data Downloader")

    api_key = st.text_input("🔑 Polygon API Key", type="password")

    # Use ticker library if available
    if "ticker_library" in st.session_state:
        st.success("Using tickers from uploaded library.")
        tickers = st.session_state["ticker_library"]
        st.text(f"Loaded {len(tickers)} tickers.")
    else:
        tickers_input = st.text_area("📈 Enter tickers (comma-separated)", "AAPL, C:EURUSD, X:BTCUSD, I:SPX")
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

    multiplier = st.number_input("⏱️ Multiplier", min_value=1, max_value=60, value=1)
    timespan = st.selectbox("🕒 Timespan", ["minute", "hour", "day", "week", "month"])
    from_date = st.date_input("📅 From Date", value=datetime(2024, 1, 1))
    to_date = st.date_input("📅 To Date", value=datetime(2024, 12, 31))
    combine = st.checkbox("Combine all tickers into one CSV", value=True)

    if st.button("🚀 Fetch and Download Data"):
        if not api_key:
            st.error("Please enter your Polygon API key.")
        elif not tickers:
            st.error("No tickers found. Upload a library or enter manually.")
        else:
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

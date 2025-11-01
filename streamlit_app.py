import streamlit as st
import pandas as pd
import requests
from io import BytesIO


# =======================
# Helper: Fetch data from Polygon API
# =======================
def fetch_polygon_data(api_key, ticker, multiplier, timespan, start_date, end_date):
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}"
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": api_key}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        st.error(f"Failed to fetch data for {ticker}: {response.text}")
        return pd.DataFrame()

    data = response.json().get("results", [])
    df = pd.DataFrame(data)

    if not df.empty:
        df["ticker"] = ticker
        # Do not modify or remove columns — only fill NAs
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

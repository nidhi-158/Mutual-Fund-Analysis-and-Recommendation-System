# nav_live_fetcher.py


import requests
import pandas as pd
from io import StringIO
from datetime import datetime


def fetch_latest_nav():
    """
    Fetch the latest NAVs from AMFI's NAVAll.txt file.
    Cleans and returns a usable DataFrame with columns: Scheme, NAV, Date.
    """
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/plain",
        "Cache-Control": "no-cache"
    }


    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"❌ Failed to fetch NAVAll.txt: {e}")


    # Read the raw text lines
    content = response.text
    lines = content.splitlines()


    # Keep only valid lines with 6 columns and skip headers/comments
    valid_lines = []
    for line in lines:
        parts = line.split(';')
        if len(parts) == 6 and not line.startswith(('Scheme Code', ';')) and line.strip():
            valid_lines.append(line)


    # Parse into DataFrame
    df = pd.read_csv(StringIO("\n".join(valid_lines)), sep=';', header=None)
    df.columns = ["SchemeCode", "ISIN_1", "ISIN_2", "Scheme", "NAV", "Date"]


    # Clean and convert types
    df.dropna(subset=["Scheme", "NAV"], inplace=True)
    df["NAV"] = pd.to_numeric(df["NAV"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Scheme"] = df["Scheme"].astype(str).str.strip().str.lower()


    # Drop rows with invalid NAV or Date
    df = df.dropna(subset=["NAV", "Date"])


    # ✅ Optional: print the most recent date to verify freshness
    if not df.empty:
        latest_date = df["Date"].max().strftime("%d-%b-%Y")
        print(f"✅ Live NAVs fetched. Latest NAV date: {latest_date}. Total schemes: {len(df)}")
    else:
        print("⚠️ No valid NAV data found.")


    return df[["Scheme", "NAV", "Date"]]

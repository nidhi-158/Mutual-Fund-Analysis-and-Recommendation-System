# nav_live_merge.py


import pandas as pd


def merge_live_with_features(feature_df, live_nav_df):
    """
    Merges live NAVs (AMFI) with latest schemeID-based features.
    Always replaces NAV and Date with live values where available.
    """


    # 📌 Load scheme name mapping to get SchemeID from live NAV data (AMFI uses SchemeCode)
    try:
        mapping_df = pd.read_csv("AFTER_PHASE_2_with_balance_FINAL.csv", usecols=["SchemeID", "Scheme"])
        mapping_df["Scheme"] = mapping_df["Scheme"].astype(str).str.strip().str.lower()
        mapping_df = mapping_df.drop_duplicates()
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load mapping file: {e}")


    # 📌 Normalize schemes in live data
    live_nav_df = live_nav_df.copy()
    live_nav_df["Scheme"] = live_nav_df["Scheme"].astype(str).str.strip().str.lower()


    # 🔄 Merge live NAVs with mapping file to get SchemeID
    live_with_id = pd.merge(
        live_nav_df,
        mapping_df,
        on="Scheme",
        how="left"
    ).dropna(subset=["SchemeID"])


    live_with_id["SchemeID"] = live_with_id["SchemeID"].astype(int)


    # 🔁 Keep only latest NAV per SchemeID
    latest_live_navs = live_with_id.sort_values("Date").groupby("SchemeID").tail(1)
    latest_live_navs = latest_live_navs[["SchemeID", "NAV", "Date"]].rename(columns={
        "NAV": "Live_NAV",
        "Date": "Live_Date"
    })


    # 📦 Get latest row per SchemeID from historical feature file
    latest_features = feature_df.sort_values("Date").groupby("SchemeID").tail(1)


    # 🔁 Merge on SchemeID now (✅ reliable)
    merged = pd.merge(
        latest_features,
        latest_live_navs,
        on="SchemeID",
        how="left"
    )


    # ✅ Use live NAV if available
    merged["NAV"] = merged["Live_NAV"].combine_first(merged["NAV"])
    merged["Date"] = merged["Live_Date"].combine_first(merged["Date"])


    # Clean up
    merged.drop(columns=["Live_NAV", "Live_Date"], inplace=True)


    # 🧾 Log info
    print(f"✅ Live NAVs merged using SchemeID: {latest_live_navs.shape[0]} unique schemes updated.")


    return merged

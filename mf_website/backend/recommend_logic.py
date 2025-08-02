import pandas as pd

# ------------------------
# Asset Class and Market Cap Maps
# ------------------------
asset_class_map = {
    "debt": 0,
    "equity": 1,
    "gold": 2,
    "hybrid": 3,
    "index/etf": 4,
    "liquid": 5,
    "other": 6,
    "specialized": 7
}

market_cap_map = {
    "focused/value": 0,
    "large cap": 1,
    "mid cap": 2,
    "small cap": 3,
    "mid/small cap": 4,
    "multi cap": 5,
    "other": 6,
    "sectoral/thematic": 7
}

# ------------------------
# For New Investors
# ------------------------
def recommend_for_new_investor(df, budget, risk_level, asset_class=None, market_cap=None, top_n=5):
    df = df.copy()
    df["Risk_Level"] = df["Risk_Level"].astype(str).str.strip().str.lower()

    # Step 1: Risk filter
    filtered = df[df["Risk_Level"] == risk_level.lower()]
    print(f"✅ After risk filter ({risk_level}): {len(filtered)}")

    # Step 2: Asset class filter
    if asset_class:
        ac_code = asset_class_map.get(asset_class.lower())
        if ac_code is not None:
            temp = filtered[filtered["Balanced_AssetClass"] == ac_code]
            print(f"🟨 Asset Class '{asset_class}': {len(temp)}")
            if not temp.empty:
                filtered = temp

    # Step 3: Market cap filter
    if market_cap:
        mc_code = market_cap_map.get(market_cap.lower())
        if mc_code is not None:
            temp = filtered[filtered["Balanced_MarketCap"] == mc_code]
            print(f"🟨 Market Cap '{market_cap}': {len(temp)}")
            if not temp.empty:
                filtered = temp

    # Step 4: Budget filter
    filtered = filtered[filtered["NAV"].notnull() & (filtered["NAV"] > 0)]
    filtered = filtered[filtered["NAV"] <= budget]
    print(f"💰 After budget filter (≤ {budget}): {len(filtered)}")

    # Fallback: Risk + budget only if nothing found
    if filtered.empty:
        fallback = df[(df["Risk_Level"] == risk_level.lower()) & (df["NAV"] <= budget)]
        if not fallback.empty:
            print("🔁 Fallback used (risk + budget only)")
            filtered = fallback
        else:
            return {"message": "❌ No funds match your criteria. Try increasing budget or changing filters."}

    # Step 5: Latest NAV per SchemeID
    filtered = filtered.sort_values("Date").groupby("SchemeID").tail(1).drop_duplicates("SchemeID")

    # Step 6: Score calculation
    filtered["score"] = (
        filtered["Sharpe_Ratio"].fillna(0) * 0.5 +
        filtered["CAGR_1Y_winsorized"].fillna(0) * 0.3 -
        filtered["Max_Drawdown_winsorized"].fillna(0) * 0.2
    )

    # Step 7: Units purchasable
    filtered["Units_Purchasable"] = (budget // filtered["NAV"]).astype(int)

    # Step 8: Add scheme name from mapping
    try:
        name_map = pd.read_csv("AFTER_PHASE_2_with_balance_FINAL.csv", usecols=["SchemeID", "Scheme"])
        name_map["Scheme"] = name_map["Scheme"].astype(str).str.strip()
        filtered = pd.merge(filtered, name_map.drop_duplicates(), on="SchemeID", how="left", suffixes=('', '_Original'))
        filtered["Scheme_Name"] = filtered["Scheme_Original"]
        filtered.drop(columns=["Scheme_Original"], inplace=True)
    except Exception as e:
        print("⚠ Could not map scheme names:", e)
        filtered["Scheme_Name"] = filtered["Scheme"]

    result = filtered.sort_values("score", ascending=False).head(top_n)
    return result[["SchemeID", "Scheme_Name", "NAV", "Units_Purchasable"]].to_dict(orient="records")

# ------------------------
# For Existing Investors
# ------------------------
def recommend_for_existing_investor(df, scheme_id, nav_at_purchase, units_held, purchase_date, threshold_improvement=0.03):
    df = df.copy()
    for col in ["Balanced_AssetClass", "Balanced_MarketCap", "Risk_Level", "Scheme"]:
        df[col] = df[col].astype(str).str.strip().str.lower()

    fund_data = df[df["SchemeID"] == scheme_id]
    if fund_data.empty:
        return {"error": "❌ SchemeID not found."}

    fund_data = fund_data.sort_values("Date")
    latest = fund_data.iloc[-1]
    latest_nav = latest["NAV"]
    latest_date = latest["Date"]

    try:
        purchase_dt = pd.to_datetime(purchase_date, dayfirst=False)
    except:
        return {"error": "❌ Invalid purchase date format."}

    holding_years = (latest_date - purchase_dt).days / 365
    if holding_years <= 0:
        return {"error": "❌ Purchase date must be in the past."}

    user_cagr = ((latest_nav / nav_at_purchase) ** (1 / holding_years)) - 1

    similar = df[
        (df["Balanced_AssetClass"] == latest["Balanced_AssetClass"]) &
        (df["Balanced_MarketCap"] == latest["Balanced_MarketCap"]) &
        (df["Risk_Level"] == latest["Risk_Level"]) &
        (df["SchemeID"] != scheme_id)
    ].drop_duplicates(subset="SchemeID")

    if similar.empty:
        return {
            "Current Fund ID": int(scheme_id),
            "Latest NAV": round(latest_nav, 2),
            "Recommendation": "Hold",
            "Reason": "No similar peer funds found."
        }

    similar["score"] = (
        similar["Sharpe_Ratio"].fillna(0) * 0.5 +
        similar["CAGR_1Y_winsorized"].fillna(0) * 0.3 -
        similar["Max_Drawdown_winsorized"].fillna(0) * 0.2
    )

    best = similar.sort_values("score", ascending=False).iloc[0]

    is_better = (
        pd.notnull(best["CAGR_1Y"]) and
        pd.notnull(latest["Sharpe_Ratio"]) and
        best["CAGR_1Y"] > user_cagr + threshold_improvement and
        best["Sharpe_Ratio"] > latest["Sharpe_Ratio"]
    )

    try:
        name_map = pd.read_csv("AFTER_PHASE_2_with_balance_FINAL.csv", usecols=["SchemeID", "Scheme"])
        name_map = name_map.drop_duplicates().dropna()
        name_map["Scheme"] = name_map["Scheme"].astype(str).str.strip()
        scheme_dict = name_map.set_index("SchemeID")["Scheme"].to_dict()
        your_scheme_name = scheme_dict.get(int(scheme_id), latest["Scheme"])
        recommended_scheme_name = scheme_dict.get(int(best["SchemeID"]), best["Scheme"])
    except:
        your_scheme_name = latest["Scheme"]
        recommended_scheme_name = best["Scheme"]

    return {
        "Your_Fund": {
            "SchemeID": int(scheme_id),
            "Scheme": your_scheme_name,
            "NAV_at_Purchase": nav_at_purchase,
            "Current_NAV": round(latest_nav, 2),
            "Units_Held": units_held,
            "Current_Value": round(latest_nav * units_held, 2),
            "CAGR": round(user_cagr * 100, 2)
        },
        "Suggestion": "Switch" if is_better else "Hold",
        "Reason": "Better fund found." if is_better else "Current fund still performs well.",
        "Recommended_Fund": {
            "Recommended_SchemeID": int(best["SchemeID"]),
            "Recommended_Scheme": recommended_scheme_name,
            "NAV": round(best["NAV"], 2)
        } if is_better else {}
    }

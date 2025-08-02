#%%
import pandas as pd
import numpy as np
from datetime import datetime
#%%
# ✅ Load Phase 5 processed dataset
processed_path = r"C:\Users\nidhi\Desktop\Int project\phase5_processed_funds_data_final.csv"
original_path = r"C:\Users\nidhi\Desktop\Int project\AFTER_PHASE_2_with_balance_FINAL.csv"
#%%
df_processed = pd.read_csv(processed_path, parse_dates=["Date"])
df_original = pd.read_csv(original_path, parse_dates=["Date"])

#%%
df_processed.isnull().sum()
#%%
df_original.isnull().sum()
#%%
# ✅ Merge real scheme names from original dataset (pre-encoding)
scheme_map = df_original[['SchemeID', 'Date', 'Scheme']]
df_clustered = pd.merge(df_processed.drop(columns=["Scheme"]), scheme_map, on=["SchemeID", "Date"], how="left")

# ✅ Label mappings
df_clustered['Balanced_AssetClass'] = df_clustered['Balanced_AssetClass'].map({
    1: "Equity", 0: "Debt", 3: "Hybrid", 6: "Other", 5: "Liquid", 4: "Index/ETF", 7: "Specialized", 2: "Gold"
})

df_clustered['Balanced_MarketCap'] = df_clustered['Balanced_MarketCap'].map({
    0: "Focused/Value", 1: "Large Cap", 7: "Small Cap", 4: "Multi Cap", 6: "Sectoral/Thematic",
    2: "Mid Cap", 5: "Other", 3: "Mid/Small Cap"
})

df_clustered['Risk_Level'] = df_clustered['Risk_Level'].astype(str)
df_clustered['Scheme'] = df_clustered['Scheme'].astype(str)

# 🔁 Recommendation for EXISTING INVESTORS
def recommend_for_existing_investor(df, scheme_id, nav_at_purchase, units_held, purchase_date, threshold_improvement=0.03):
    fund_data = df[df['SchemeID'] == scheme_id]
    if fund_data.empty:
        return "❌ SchemeID not found in dataset."

    latest_nav = fund_data.sort_values('Date').iloc[-1]['NAV']
    latest_date = pd.to_datetime(df['Date'].max())
    purchase_date = pd.to_datetime(purchase_date)
    years_held = (latest_date - purchase_date).days / 365

    if years_held <= 0:
        return "❌ Invalid purchase date."

    cagr_user = ((latest_nav / nav_at_purchase) ** (1 / years_held)) - 1
    current_profile = fund_data.iloc[-1]
    asset_class = current_profile['Balanced_AssetClass']
    market_cap = current_profile['Balanced_MarketCap']
    risk_level = current_profile['Risk_Level']

    similar_funds = df[
        (df['Balanced_AssetClass'] == asset_class) &
        (df['Balanced_MarketCap'] == market_cap) &
        (df['Risk_Level'] == risk_level)
    ].drop_duplicates(subset='SchemeID')

    # Scoring
    similar_funds['score'] = (
        similar_funds['Sharpe_Ratio'] * 0.5 +
        similar_funds['CAGR_1Y_winsorized'] * 0.3 -
        similar_funds['Max_Drawdown_winsorized'] * 0.2
    )

    top_fund = similar_funds.sort_values(by='score', ascending=False).iloc[0]

    better = (
        top_fund['CAGR_1Y'] > cagr_user + threshold_improvement and
        top_fund['Sharpe_Ratio'] > current_profile['Sharpe_Ratio']
    )

    return {
        "Current Fund ID": int(scheme_id),
        "Latest NAV": round(latest_nav, 2),
        "Top Similar Fund ID": int(top_fund['SchemeID']),
        "Scheme Name (Top)": top_fund['Scheme'],
        "Recommendation": "Switch" if better else "Hold",
        "Reason": "Better fund found in same class and risk level." if better else "Current fund is optimal based on profile."
    }

# 🆕 Recommendation for NEW INVESTORS
# 🆕 Recommendation for NEW INVESTORS
def recommend_for_new_investor(df, budget, risk_level, asset_class=None, market_cap=None, top_n=5):
    df['Balanced_AssetClass'] = df['Balanced_AssetClass'].astype(str)
    df['Balanced_MarketCap'] = df['Balanced_MarketCap'].astype(str)
    df['Risk_Level'] = df['Risk_Level'].astype(str)

    filtered = df[df['Risk_Level'].str.lower() == risk_level.lower()]

    if asset_class:
        temp = filtered[filtered['Balanced_AssetClass'].str.lower() == asset_class.lower()]
        if not temp.empty:
            filtered = temp

    if market_cap:
        temp = filtered[filtered['Balanced_MarketCap'].str.lower() == market_cap.lower()]
        if not temp.empty:
            filtered = temp

    # ✅ Filter funds within budget
    filtered = filtered[filtered['NAV'] <= budget]

    if filtered.empty:
        return pd.DataFrame()

    filtered = filtered.drop_duplicates(subset='SchemeID')

    # ✅ Add scoring and units purchasable
    filtered['score'] = (
        filtered['Sharpe_Ratio'] * 0.5 +
        filtered['CAGR_1Y_winsorized'] * 0.3 -
        filtered['Max_Drawdown_winsorized'] * 0.2
    )
    filtered['Units_Purchasable'] = (budget // filtered['NAV']).astype(int)

    ranked = filtered.sort_values(by='score', ascending=False)

    return ranked[['SchemeID', 'Scheme', 'NAV', 'Units_Purchasable']].head(top_n)

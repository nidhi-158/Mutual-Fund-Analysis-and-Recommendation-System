import streamlit as st
import pandas as pd
from new_p6 import recommend_for_existing_investor, recommend_for_new_investor

st.set_page_config(page_title="Mutual Fund Recommender", layout="centered")

@st.cache_data
def load_data():
    path = r"C:\Users\nidhi\Desktop\Int project\phase5_processed_funds_data_final.csv"
    original_path = r"C:\Users\nidhi\Desktop\Int project\AFTER_PHASE_2_with_balance_FINAL.csv"

    df = pd.read_csv(path, parse_dates=["Date"])
    df_original = pd.read_csv(original_path, parse_dates=["Date"])
    scheme_map = df_original[['SchemeID', 'Date', 'Scheme']]
    df = pd.merge(df.drop(columns=["Scheme"]), scheme_map, on=["SchemeID", "Date"], how="left")

    asset_class_map = {
        1: "Equity", 0: "Debt", 3: "Hybrid", 6: "Other", 5: "Liquid", 4: "Index/ETF", 7: "Specialized", 2: "Gold"
    }

    market_cap_map = {
        0: "Focused/Value", 1: "Large Cap", 7: "Small Cap", 4: "Multi Cap", 6: "Sectoral/Thematic",
        2: "Mid Cap", 5: "Other", 3: "Mid/Small Cap"
    }

    df['Balanced_AssetClass'] = df['Balanced_AssetClass'].map(asset_class_map)
    df['Balanced_MarketCap'] = df['Balanced_MarketCap'].map(market_cap_map)
    df['Risk_Level'] = df['Risk_Level'].astype(str)
    df['Scheme'] = df['Scheme'].astype(str)

    return df

# Load dataset
df_clustered = load_data()

st.title("💹 Mutual Fund Recommendation System")

user_type = st.sidebar.radio("Select Investor Type", ["New Investor", "Existing Investor"])

# 🔁 Existing Investor
if user_type == "Existing Investor":
    st.header("🔁 Existing Portfolio Analysis")

    scheme_names = sorted(df_clustered['Scheme'].dropna().unique())
    selected_scheme = st.selectbox("Select your Scheme Name", scheme_names)

    scheme_row = df_clustered[df_clustered['Scheme'] == selected_scheme].sort_values(by="Date").iloc[-1]
    scheme_id = int(scheme_row['SchemeID'])

    nav_at_purchase = st.number_input("NAV at time of purchase", min_value=0.0)
    units_held = st.number_input("Units held", min_value=0.0)
    purchase_date = st.date_input("Purchase date")

    if st.button("Analyze Portfolio"):
        result = recommend_for_existing_investor(
            df=df_clustered,
            scheme_id=scheme_id,
            nav_at_purchase=nav_at_purchase,
            units_held=units_held,
            purchase_date=str(purchase_date)
        )
        if isinstance(result, str):
            st.error(result)
        else:
            st.success(f"✅ Recommendation: {result['Recommendation']}")
            st.markdown(f"Reason: {result['Reason']}")
            st.write("📊 Summary:")
            st.dataframe(pd.DataFrame([result]).T.rename(columns={0: "Value"}))

# 🆕 New Investor
if user_type == "New Investor":
    st.header("🆕 Personalized Fund Recommendations")

    budget = st.number_input("Investment Budget (₹)", min_value=1000)
    risk = st.selectbox("Risk Tolerance", ["Low", "Medium", "High"])

    asset_class_options = sorted(df_clustered['Balanced_AssetClass'].dropna().unique())
    market_cap_options = sorted(df_clustered['Balanced_MarketCap'].dropna().unique())

    asset_class = st.selectbox("Fund Type (Asset Class)", asset_class_options)
    market_cap = st.selectbox("Market Cap Preference", market_cap_options)

    # 🔁 Use a fixed number of recommendations instead of asking the user
    fixed_top_n = 7

    if st.button("Recommend Funds"):
        recommendations = recommend_for_new_investor(
            df=df_clustered,
            budget=budget,
            risk_level=risk,
            asset_class=asset_class,
            market_cap=market_cap,
            top_n=fixed_top_n
        )

        if recommendations.empty:
            st.warning("⚠ No matching funds found within your budget and preferences.")
        else:
            recommendations = recommendations.rename(columns={
                "SchemeID": "Scheme ID",
                "Scheme": "Scheme Name",
                "NAV": "Latest NAV",
                "Units_Purchasable": "Units You Can Buy"
            })
            st.success(f"✅ Top Recommendations for You:")
            st.dataframe(recommendations.reset_index(drop=True))

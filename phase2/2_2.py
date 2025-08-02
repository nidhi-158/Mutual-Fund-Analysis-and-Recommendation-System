# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore
import re
from sklearn.utils import resample

# %% Load Dataset
file_path = r"C:\Users\prana\Downloads\Mutual_funds\after_phase_2_with_categorization.csv"

# Load data with error handling
df = pd.read_csv(file_path, low_memory=False, encoding="utf-8", on_bad_lines='skip')
#%% Final Optimized Distribution
print(" Optimized Market Cap Distribution:\n", df['MarketCap'].value_counts())
print(" Optimized Asset Class Distribution:\n", df['AssetClass'].value_counts())
# %% # Asset Class distribution pie chart
asset_class_counts = df['AssetClass'].value_counts()
asset_class_percentage = asset_class_counts / asset_class_counts.sum() * 100
# %%
plt.figure(figsize=(8, 8))
plt.pie(asset_class_percentage, labels=asset_class_percentage.index, autopct='%1.1f%%', startangle=90,
        colors=plt.cm.Paired.colors)  # Use color palette for better visibility
plt.title('Asset Class Distribution (Percentage)', fontsize=16)
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.show()
# %% # Market Capitalization distribution pie chart
market_cap_counts = df['MarketCap'].value_counts()
market_cap_percentage = market_cap_counts / market_cap_counts.sum() * 100

plt.figure(figsize=(8, 8))
plt.pie(market_cap_percentage, labels=market_cap_percentage.index, autopct='%1.1f%%', startangle=90,
        colors=plt.cm.Paired.colors)  # Use color palette for better visibility
plt.title('Market Capitalization Distribution (Percentage)', fontsize=16)
plt.axis('equal')
plt.show()
# %% Original Market Cap distribution
market_cap = {
    "Small Cap": 1109359, "Multi Cap": 1044708, "Focused/Value": 670099,
    "Sectoral/Thematic": 594415, "Large Cap": 151468, "Mid Cap": 123316,
    "Other": 13901, "Mid/Small Cap": 1832
}

# Original Asset Class distribution
asset_class = {
    "Equity": 1554987, "Liquid": 900299, "Debt": 666268, "Hybrid": 282795,
    "Index/ETF": 257056, "Specialized": 36818, "Gold": 7493, "Other": 3394
}

# Convert to DataFrames
market_cap_df = pd.DataFrame(list(market_cap.items()), columns=["MarketCap", "Count"])
asset_class_df = pd.DataFrame(list(asset_class.items()), columns=["AssetClass", "Count"])

# Compute total counts
total_market_cap = market_cap_df["Count"].sum()
total_asset_class = asset_class_df["Count"].sum()

# Compute percentage distribution
market_cap_df["Percentage"] = (market_cap_df["Count"] / total_market_cap) * 100
asset_class_df["Percentage"] = (asset_class_df["Count"] / total_asset_class) * 100

# 🔹 *Balanced Distribution Logic*
def balance_distribution(df, factor_large=0.85, factor_mid=1.1, factor_small=1.5):
    """
    Adjusts the distribution:
    - Reduces large categories slightly (factor < 1)
    - Increases mid-sized categories slightly (factor > 1)
    - Boosts small categories significantly (factor >> 1)
    """
    sorted_df = df.sort_values(by="Count", ascending=False).reset_index(drop=True)
    
    # Define size categories
    large_threshold = sorted_df["Count"].quantile(0.75)  # Top 25% largest categories
    small_threshold = sorted_df["Count"].quantile(0.25)  # Bottom 25% smallest categories

    # Apply scaling factors
    def adjust_count(row):
        if row["Count"] >= large_threshold:
            return int(row["Count"] * factor_large)
        elif row["Count"] <= small_threshold:
            return int(row["Count"] * factor_small)
        else:
            return int(row["Count"] * factor_mid)

    sorted_df["BalancedCount"] = sorted_df.apply(adjust_count, axis=1)

    # *Ensure total count remains similar*
    correction_factor = df["Count"].sum() / sorted_df["BalancedCount"].sum()
    sorted_df["BalancedCount"] = (sorted_df["BalancedCount"] * correction_factor).astype(int)
    
    return sorted_df

# Apply balancing to Market Cap and Asset Class
market_cap_balanced = balance_distribution(market_cap_df)
asset_class_balanced = balance_distribution(asset_class_df)

# Display results
print(" Balanced Market Cap Distribution:")
print(market_cap_balanced[["MarketCap", "BalancedCount"]])

print("\n Balanced Asset Class Distribution:")
print(asset_class_balanced[["AssetClass", "BalancedCount"]])
# %% # Market Cap Pie Chart
plt.figure(figsize=(7, 7))
plt.pie(market_cap_balanced["BalancedCount"], labels=market_cap_balanced.index, 
        autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor': 'black'})
plt.title("Balanced Market Cap Distribution")
plt.show()
# Asset Class Pie Chart
plt.figure(figsize=(7, 7))
plt.pie(asset_class_balanced["BalancedCount"], labels=asset_class_balanced.index, 
        autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor': 'black'})
plt.title("Balanced Asset Class Distribution")
plt.show()

# %%
# Assign Balanced AssetClass Labels
df['Balanced_AssetClass'] = np.nan
for cls, count in asset_class_balanced[['AssetClass', 'BalancedCount']].values:
    matching_rows = df[df['AssetClass'] == cls]
    sampled_rows = matching_rows.sample(n=min(count, len(matching_rows)), random_state=42)
    df.loc[sampled_rows.index, 'Balanced_AssetClass'] = cls

# Assign Balanced MarketCap Labels
df['Balanced_MarketCap'] = np.nan
for cls, count in market_cap_balanced[['MarketCap', 'BalancedCount']].values:
    matching_rows = df[df['MarketCap'] == cls]
    sampled_rows = matching_rows.sample(n=min(count, len(matching_rows)), random_state=42)
    df.loc[sampled_rows.index, 'Balanced_MarketCap'] = cls

# Optional: Convert to category type
df['Balanced_AssetClass'] = df['Balanced_AssetClass'].astype('category')
df['Balanced_MarketCap'] = df['Balanced_MarketCap'].astype('category')
# %%
df.isnull().sum()
# %%
df.shape
# %%
df['Balanced_AssetClass'].value_counts()
# %%
df['Balanced_MarketCap'].value_counts()
# %%
output_path = r"C:\Users\prana\Downloads\Mutual_funds\after_phase_2_with_balance.csv"
df.to_csv(output_path, index=False)

print(f"✅ Cleaned data saved to: {output_path}")
# %%

#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore
#%% Load Dataset 
file_path = r"C:\Users\prana\Downloads\Mutual_funds\after_phase_2.csv" 
# Load data  with error handling for bad lines 
df = pd.read_csv(file_path, low_memory=False, encoding="utf-8", on_bad_lines='skip') 
# %%
import re
#  Enhanced Asset Class Classification
def classify_asset_class(scheme_name):
    scheme_name = scheme_name.lower().strip()
    #  Liquid Class (Enhanced Patterns)
    if re.search(r'\bovernight\b|\bliquid\b|\bcash\s*management\b|\bmoney\s*market\b|\btreasury\b|\bcall\s*money\b|\bfloater\b|\bshort\s*duration\b|\bsavings\b|\bultra\s*short\b|\barbitrage\b|\breserve\b|\binstant\b|\bliquid\s*fund\b', scheme_name):
        return "Liquid"
    #  Equity Class (Expanded Coverage)
    elif re.search(r'\bequity\b|\bstock\b|\blarge\s*cap\b|\bmid\s*cap\b|\bsmall\s*cap\b|\bflexi\s*cap\b|\bmulti\s*cap\b|\bvalue\b|\bcontra\b|\bthematic\b|\bdiversified\b|\bfocused\b|\bgrowth\b|\bbluechip\b|\btop\s*[0-9]+\b|\balpha\b|\bquant\b|\bstrategy\b|\btheme\b', scheme_name):
        return "Equity"
    #  Debt Class (Additional Cases Handled)
    elif re.search(r'\bdebt\b|\bincome\b|\bfmp\b|\bbond\b|\bgilt\b|\bcorporate\s*bonds\b|\bsovereign\b|\bduration\b|\btarget\s*maturity\b|\bdynamic\s*bond\b|\bfixed\s*maturity\b|\bcredit\s*risk\b|\byield\b|\bbanking\s*bonds\b|\bshort\s*term\b', scheme_name):
        return "Debt"
    #  Hybrid Class (More Conservative Matches)
    elif re.search(r'\bhybrid\b|\bbalanced\b|\basset\s*allocation\b|\bconservative\b|\baggressive\b|\barbitrage\b|\bbalanced\s*advantage\b|\bequity\s*savings\b|\bmip\b|\bcombo\b|\btactical\s*allocation\b|\bsolution\b|\ballocation\b', scheme_name):
        return "Hybrid"
    #  Index/ETF Class (Broader ETF Matches)
    elif re.search(r'\betf\b|\bindex\b|\bnifty\b|\bsensex\b|\bbenchmark\b|\bpassive\b|\btracking\s*fund\b|\bnasdaq\b|\bsp500\b|\bdow\s*jones\b|\bglobal\b|\bintl\b|\bindia\b|\bworld\b', scheme_name):
        return "Index/ETF"
    #  Gold/Commodity Class
    elif re.search(r'\bgold\b|\bsilver\b|\bcommodity\b|\bmetals\b|\bprecious\s*metals\b|\breal\s*assets\b|\bnatural\s*resources\b|\bplatinum\b', scheme_name):
        return "Gold"
    #  Specialized Class (Enhanced Matching)
    elif re.search(r'\bulip\b|\bunit\s*linked\b|\bchild\s*plan\b|\belss\b|\bretirement\b|\bpension\b|\btax\b|\bwealth\b|\binsurance\b|\bgovernment\s*scheme\b|\bsocial\s*impact\b|\bethical\s*investing\b|\binnovation\b', scheme_name):
        return "Specialized"
    #  Reduce "Other" but don't eliminate completely
    if re.search(r'\bplan\b|\bsolution\b|\bcapital\b|\ballocation\b|\bportfolio\b|\bfund\b|\bscheme\b|\bpolicy\b', scheme_name):
        return "Hybrid"
    #  Still allow some fallback to "Other"
    return "Other"
#  Enhanced Market Cap Classification
def classify_market_cap(scheme_name, asset_class):
    scheme_name = scheme_name.lower().strip()
    #  Equity Classification
    if asset_class == "Equity":
        if re.search(r'\blarge\s*cap\b|\bbluechip\b|\bnifty\s*50\b|\bsensex\b|\btop\s*100\b|\bfrontline\b|\bbenchmark\b', scheme_name):
            return "Large Cap"
        elif re.search(r'\bmid\s*cap\b|\bmidcap\b|\bmedium\s*cap\b|\bmid\s*tier\b|\btop\s*150\b', scheme_name):
            return "Mid Cap"
        elif re.search(r'\bsmall\s*cap\b|\bsmallcap\b|\bemerging\b|\btop\s*250\b|\bsmid\b|\bgrowth\b|\bsmall\s*tier\b', scheme_name):
            return "Small Cap"
        elif re.search(r'\bmulti\s*cap\b|\bflexi\s*cap\b|\bdiversified\b|\bbalanced\s*equity\b', scheme_name):
            return "Multi Cap"
        elif re.search(r'\bfocused\b|\bvalue\b|\bcontra\b|\besg\b|\btheme\b|\bstrategy\b', scheme_name):
            return "Focused/Value"
        elif re.search(r'\bsectoral\b|\bthematic\b|\bbanking\b|\bpharma\b|\btechnology\b|\binfrastructure\b|\benergy\b|\bauto\b', scheme_name):
            return "Sectoral/Thematic"
        return "Multi Cap"  # Fallback to Multi Cap for unmatched equity
    #  Debt & Hybrid Schemes
    elif asset_class in ["Debt", "Hybrid"]:
        if re.search(r'\bduration\b|\bgilt\b|\bbond\b|\bcredit\b|\byield\b|\bcorporate\b|\bdynamic\b|\btactical\b|\bsovereign\b', scheme_name):
            return "Sectoral/Thematic"
        elif re.search(r'\bliquid\b|\bovernight\b|\bshort\s*duration\b|\bmoney\s*market\b', scheme_name):
            return "Large Cap"
        return "Focused/Value"
    #  Index/ETF Schemes
    elif asset_class == "Index/ETF":
        if re.search(r'\bnifty\s*50\b|\bsensex\b|\blarge\s*cap\b|\btop\s*50\b', scheme_name):
            return "Large Cap"
        elif re.search(r'\bmid\s*cap\b|\bsmall\s*cap\b|\btop\s*250\b|\bemerging\b', scheme_name):
            return "Mid/Small Cap"
        return "Sectoral/Thematic"
    #  Gold & Specialized
    elif asset_class == "Gold":
        return "Sectoral/Thematic"
    elif asset_class == "Specialized":
        return "Focused/Value"
    #  Keep some "Other" for unknowns
    return "Other" if "fund" not in scheme_name else "Multi Cap"
#  Apply Enhanced Classifications
df['Scheme'] = df['Scheme'].str.strip().str.lower().fillna("")
df['AssetClass'] = df['Scheme'].apply(classify_asset_class)
df['MarketCap'] = df.apply(lambda row: classify_market_cap(row['Scheme'], row['AssetClass']), axis=1)
#  Final Optimized Distribution
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

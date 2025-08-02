#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore
#%% Load Dataset 
file_path = r"C:\Users\prana\Downloads\Mutual_funds\after_phase_1.csv" 
# Load data  with error handling for bad lines 
df = pd.read_csv(file_path, low_memory=False, encoding="utf-8", on_bad_lines='skip') 
# #%% 
df.shape
# %%
print("✅ Initial Data Overview:") 
print(df.info())
print(df.describe())
print(df.isnull().sum())
# %%
# Make sure Date is datetime and sorted
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(['SchemeID', 'Date'])
# %%
# Create period columns
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(['SchemeID', 'Date'])
df['Month'] = df['Date'].dt.to_period('M')
df['Quarter'] = df['Date'].dt.to_period('Q')
df['Year'] = df['Date'].dt.to_period('Y')

# Helper to compute period returns using shift
def add_period_return(df, period_col, return_col_name):
    df_sorted = df.sort_values(['SchemeID', 'Date'])
    grouped = df_sorted.groupby(['SchemeID', period_col])
    
    # Compute return using first and last NAV in each group
    start_nav = grouped['NAV'].transform('first')
    end_nav = grouped['NAV'].transform('last')
    
    df[return_col_name] = (end_nav - start_nav) / start_nav
    return df
df["Daily_Return"] = df.groupby("SchemeID")["NAV"].pct_change()
# Apply faster computation
df = add_period_return(df, 'Month', 'Monthly_Return')
df = add_period_return(df, 'Quarter', 'Quarterly_Return')
df = add_period_return(df, 'Year', 'Yearly_Return')

# Convert periods to timestamps (optional for plotting)
df['Month'] = df['Month'].dt.to_timestamp()
df['Quarter'] = df['Quarter'].dt.to_timestamp()
df['Year'] = df['Year'].dt.to_timestamp()
# %%
df.isnull().sum()
# %%
print(df['Daily_Return'].nunique())
print(df['Monthly_Return'].nunique())
print(df['Quarterly_Return'].nunique())
print(df['Yearly_Return'].nunique())
# %%
df.describe()
# %%Compute STD for Monthly, Quarterly, and Yearly Returns per SchemeID
monthly_std = df.groupby("SchemeID")["Monthly_Return"].std().reset_index()
quarterly_std = df.groupby("SchemeID")["Quarterly_Return"].std().reset_index()
yearly_std = df.groupby("SchemeID")["Yearly_Return"].std().reset_index()

# Rename columns for clarity
monthly_std.columns = ["SchemeID", "Monthly_STD"]
quarterly_std.columns = ["SchemeID", "Quarterly_STD"]
yearly_std.columns = ["SchemeID", "Yearly_STD"]

# Merge all STD columns into a single DataFrame
df = df.merge(monthly_std, on="SchemeID", how="left")
df = df.merge(quarterly_std, on="SchemeID", how="left")
df = df.merge(yearly_std, on="SchemeID", how="left")
#%%
df.duplicated().sum()
# %%
print(df['Monthly_STD'].nunique())
print(df['Quarterly_STD'].nunique())
print(df['Yearly_STD'].nunique())
# %%
df.describe()
# %%
df.isnull().sum()
# %% Compute CAGR for 1 Year and 2 Years (if data permits)
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(['SchemeID', 'Date'])

# Reference latest date in the dataset
latest_date = df['Date'].max()
cutoff_1y = latest_date - pd.DateOffset(years=1)
cutoff_2y = latest_date - pd.DateOffset(years=2)

# Helper to get NAV closest to a date
def get_closest_nav(df_sub, target_date):
    return df_sub.iloc[(df_sub['Date'] - target_date).abs().argsort()[:1]]

# Empty list to store results
cagr_data = []

# Loop through each SchemeID
for scheme_id, group in df.groupby('SchemeID'):
    group = group.sort_values('Date')

    # Get latest NAV
    latest_nav_row = group[group['Date'] == latest_date]
    if latest_nav_row.empty:
        latest_nav_row = group.iloc[[-1]]
    nav_latest = latest_nav_row['NAV'].values[0]

    # Get NAV approx 1 year ago
    nav_1y_row = get_closest_nav(group, cutoff_1y)
    nav_2y_row = get_closest_nav(group, cutoff_2y)

    nav_1y = nav_1y_row['NAV'].values[0] if not nav_1y_row.empty else np.nan
    nav_2y = nav_2y_row['NAV'].values[0] if not nav_2y_row.empty else np.nan

    # Calculate CAGR if NAV is available
    cagr_1y = ((nav_latest / nav_1y) ** (1 / 1) - 1) if pd.notnull(nav_1y) and nav_1y > 0 else np.nan
    cagr_2y = ((nav_latest / nav_2y) ** (1 / 2) - 1) if pd.notnull(nav_2y) and nav_2y > 0 else np.nan

    cagr_data.append({
        'SchemeID': scheme_id,
        'CAGR_1Y': cagr_1y,
        'CAGR_2Y': cagr_2y
    })

# Convert to DataFrame and merge
cagr_df = pd.DataFrame(cagr_data)
df = df.merge(cagr_df, on='SchemeID', how='left')
# %%
df.isnull().sum()
# %%
print(df['CAGR_1Y'].nunique())
print(df['CAGR_2Y'].nunique())
# %%
df.duplicated().sum()
# %%
df[['SchemeID','CAGR_1Y','CAGR_2Y']].duplicated().sum()
# %%
df[['SchemeID','CAGR_1Y','CAGR_2Y']].duplicated().sum()
# %%
df[['SchemeID','CAGR_2Y']].duplicated().sum()
# %%
df.describe()
# %%
# Drop rows where any of the key columns have NaN values
df = df.dropna(subset=['Daily_Return', 'Monthly_STD', 'Quarterly_STD', 'Yearly_STD']).reset_index(drop=True)
# %%
df.isnull().sum()
# %%
df.shape
# %%SHARPE RATIO Calculation
risk_free_rate = 0.065
df['Sharpe_Ratio'] = (df['CAGR_1Y'] - risk_free_rate) / df['Yearly_STD']
df['Sharpe_Ratio'].replace([np.inf, -np.inf], np.nan, inplace=True)
df['Sharpe_Ratio'].fillna(0, inplace=True)
# %%
df.isnull().sum()
# %%
df['Sharpe_Ratio'].nunique()
# %%
df['Sharpe_Ratio'].describe()
# %%
df.duplicated().sum()
# %% Improved Sortino Ratio Calculation
def robust_downside_std(returns):
    negative_returns = returns[returns < 0]
    if len(negative_returns) == 0:
        return np.nan  # or return a small epsilon like 1e-6
    return np.sqrt((negative_returns ** 2).mean())

# Calculate downside std per SchemeID
downside_std_dict = (
    df.groupby("SchemeID")["Daily_Return"]
    .apply(robust_downside_std)
    .replace(0, np.nan)  # prevent division by zero
    .to_dict()
)

# Map downside std back to the DataFrame
df["Downside_STD"] = df["SchemeID"].map(downside_std_dict)

# Calculate Sortino Ratio
df["Sortino_Ratio"] = (df["CAGR_1Y"] - risk_free_rate) / df["Downside_STD"]
# %%
df.isnull().sum()
# %%
df['Sortino_Ratio'].nunique()
# %%
df['Sortino_Ratio'].describe()
# %%
df['Sortino_Ratio'].replace([np.inf, -np.inf], np.nan, inplace=True)
df['Sortino_Ratio'].isnull().sum()
# %% Maximum Drawdown Calculation
def calculate_max_drawdown(nav_series):
    # Running maximum NAV
    running_max = nav_series.cummax()
    
    # Drawdown = percentage drop from peak
    drawdown = (nav_series - running_max) / running_max
    
    # Return max drawdown (i.e., the most negative value)
    return drawdown.min()

# Apply per SchemeID
max_drawdown_dict = df.groupby('SchemeID')['NAV'].apply(calculate_max_drawdown).to_dict()

# Map back to DataFrame
df['Max_Drawdown'] = df['SchemeID'].map(max_drawdown_dict)
# %%
df.isnull().sum()
# %%
df['Max_Drawdown'].nunique()
# %%
df['Max_Drawdown'].describe()
# %%
df.duplicated().sum()
# %%
df = df.sort_values(['SchemeID', 'Date'])
# Use smaller min_periods to reduce NaNs
df['Rolling_Volatility_21D'] = (
    df.groupby('SchemeID')['Daily_Return']
    .transform(lambda x: x.rolling(window=21, min_periods=5).std())
)

df['Rolling_Volatility_Quarter'] = (
    df.groupby('SchemeID')['Daily_Return']
    .transform(lambda x: x.rolling(window=62, min_periods=15).std())
)

df['Rolling_Volatility_Year'] = (
    df.groupby('SchemeID')['Daily_Return']
    .transform(lambda x: x.rolling(window=252, min_periods=50).std())
)
# %%
df.isnull().sum()
# %%
df.duplicated().sum()
# %%
print(df['Rolling_Volatility_21D'].nunique())
print(df['Rolling_Volatility_Quarter'].nunique())
print(df['Rolling_Volatility_Year'].nunique())
# %%
df['Downside_STD'].fillna(1e-6, inplace=True)
# %%
df.isnull().sum()
# %%
df['Sortino_Ratio'] = (df['CAGR_1Y'] - risk_free_rate) / df['Downside_STD']
# %%
df.isnull().sum()
# %%
# Forward fill to preserve time-series structure
df['Rolling_Volatility_21D'] = df.groupby('SchemeID')['Rolling_Volatility_21D'].ffill()
df['Rolling_Volatility_Quarter'] = df.groupby('SchemeID')['Rolling_Volatility_Quarter'].ffill()
df['Rolling_Volatility_Year'] = df.groupby('SchemeID')['Rolling_Volatility_Year'].ffill()

# Fill any leftover NaNs with scheme-level mean
for col in ['Rolling_Volatility_21D', 'Rolling_Volatility_Quarter', 'Rolling_Volatility_Year']:
    df[col] = df[col].fillna(df.groupby('SchemeID')[col].transform('mean'))

# %%
df.isnull().sum()
# %%
for col in ['Rolling_Volatility_21D', 'Rolling_Volatility_Quarter', 'Rolling_Volatility_Year']:
    df[col] = df[col].fillna(df[col].median())
# %%
df.isnull().sum()
# %%
df.duplicated().sum()
# %%
df.describe()
# %%
output_path = r"C:\Users\prana\Downloads\Mutual_funds\after_phase_2.csv"
df.to_csv(output_path, index=False)

print(f"✅ Cleaned data saved to: {output_path}")
# %%

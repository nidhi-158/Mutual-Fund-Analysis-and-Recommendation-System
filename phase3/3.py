#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from scipy.stats.mstats import winsorize
#%%
from sklearn.ensemble import IsolationForest
iso = IsolationForest(contamination=0.01)
#%% Load Dataset 
file_path = r"C:\Users\prana\Downloads\Mutual_funds\after_phase_2_with_balance.csv" 
# Load data  with error handling for bad lines 
df = pd.read_csv(file_path, low_memory=False, encoding="utf-8", on_bad_lines='skip') 
# #%% 
df.shape
# %%
print("✅ Initial Data Overview:") 
print(df.info())
# %%
print(df.describe())
# %%
print(df.isnull().sum())
#%%#  Final Optimized Distribution
print(" Optimized Market Cap Distribution:\n", df['Balanced_AssetClass'].value_counts())
print(" Optimized Asset Class Distribution:\n", df['Balanced_MarketCap'].value_counts())
# %%
df.duplicated().sum()
# %%
categorical_cols = ['Fund House', 'Scheme', 'AssetClass', 'MarketCap', 'Balanced_AssetClass', 'Balanced_MarketCap']
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le  # store encoder for inverse_transform later if needed
# %%
print(df['Balanced_AssetClass'].value_counts())
print(df['Balanced_MarketCap'].value_counts())
print(df['AssetClass'].value_counts())
print(df['MarketCap'].value_counts())
# %%
df.isnull().sum()
# %%
print(df['Fund House'].value_counts())
print(df['Scheme'].value_counts())
# %% Select float64 columns
numerical_cols = df.select_dtypes(include='float64').columns.tolist()
print(numerical_cols)
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['NAV'])
plt.title('Box Plot of NAV')
plt.xlabel('NAV')
plt.show()
#%%
count = (df['NAV'] <= 0).sum()
print(count)
# %%  # Adjust contamination %
outliers_if = iso.fit_predict(df[['NAV']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['NAV_log_normalize'] = np.log1p(df['NAV'])  # log1p handles the case when NAV is 0
#%%
plt.figure(figsize=(10, 6))
sns.boxplot(x=df['NAV_log_normalize'])
plt.title('Box Plot of NAV')
plt.title('Log Transformed NAV Distribution')
plt.show()
#%%
count = (df['NAV_log_normalize'] > 0).sum()
print(count)
# %% Daily_Return
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Daily_Return'])
plt.title('Box Plot of NAV')
plt.xlabel('NAV')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['Daily_Return']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['Daily_Return_winsorized'] = winsorize(df['Daily_Return'], limits=[0.03, 0.03])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Daily_Return_winsorized'])
plt.title('Box Plot of NAV')
plt.xlabel('Daily_Return_winsorized')
plt.grid(True)
plt.show()
# %%Monthly_Return
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Monthly_Return'])
plt.title('Box Plot of NAV')
plt.xlabel('Monthly_Return')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['Monthly_Return']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['Monthly_Return_winsorized'] = winsorize(df['Monthly_Return'], limits=[0.03, 0.03])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Monthly_Return_winsorized'])
plt.title('Box Plot of NAV')
plt.xlabel('Monthly_Return_winsorized')
plt.grid(True)
plt.show()
# %% Quarterly_Return
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Quarterly_Return'])
plt.title('Box Plot of NAV')
plt.xlabel('Quarterly_Return')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['Quarterly_Return']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['Quarterly_Return_winsorized'] = winsorize(df['Quarterly_Return'], limits=[0.03, 0.03])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Quarterly_Return_winsorized'])
plt.title('Box Plot of NAV')
plt.xlabel('Quarterly_Return_winsorized')
plt.grid(True)
plt.show()
# %% Yearly_Return
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Yearly_Return'])
plt.title('Box Plot of NAV')
plt.xlabel('Yearly_Return')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['Yearly_Return']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['Yearly_Return_winsorized'] = winsorize(df['Yearly_Return'], limits=[0.03, 0.03])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Yearly_Return_winsorized'])
plt.title('Box Plot of NAV')
plt.xlabel('Yearly_Return_winsorized')
plt.grid(True)
plt.show()
# %% Monthly_STD
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Monthly_STD'])
plt.xlabel('Monthly_STD')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['Monthly_STD']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['Monthly_STD_winsorized'] = winsorize(df['Monthly_STD'], limits=[0.03, 0.03])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Monthly_STD_winsorized'])
plt.xlabel('Monthly_STD_winsorized')
plt.grid(True)
plt.show()
# %% Quarterly_STD
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Quarterly_STD'])
plt.xlabel('Quarterly_STD')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['Quarterly_STD']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['Quarterly_STD_winsorized'] = winsorize(df['Quarterly_STD'], limits=[0.03, 0.03])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Quarterly_STD_winsorized'])
plt.xlabel('Quarterly_STD_winsorized')
plt.grid(True)
plt.show()
# %%'Yearly_STD', 
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Yearly_STD'])
plt.xlabel('Yearly_STD')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['Yearly_STD']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['Yearly_STD_winsorized'] = winsorize(df['Yearly_STD'], limits=[0.03, 0.03])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Yearly_STD_winsorized'])
plt.xlabel('Yearly_STD_winsorized')
plt.grid(True)
plt.show()
# %% 'CAGR_1Y'
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['CAGR_1Y'])
plt.xlabel('CAGR_1Y')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['CAGR_1Y']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['CAGR_1Y_winsorized'] = winsorize(df['CAGR_1Y'], limits=[0.03, 0.03])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['CAGR_1Y_winsorized'])
plt.xlabel('CAGR_1Y_winsorized')
plt.grid(True)
plt.show()
# %%'CAGR_2Y', 
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['CAGR_2Y'])
plt.xlabel('CAGR_2Y')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['CAGR_2Y']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['CAGR_2Y_winsorized'] = winsorize(df['CAGR_2Y'], limits=[0.03, 0.03])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['CAGR_2Y_winsorized'])
plt.xlabel('CAGR_2Y_winsorized')
plt.grid(True)
plt.show()
# %%'Sharpe_Ratio', 
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Sharpe_Ratio'])
plt.xlabel('Sharpe_Ratio')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['Sharpe_Ratio']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['Sharpe_Ratio_log_normalize'] = np.log1p(df['Sharpe_Ratio'])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Sharpe_Ratio_log_normalize'])
plt.xlabel('Sharpe_Ratio_log_normalize')
plt.grid(True)
plt.show()
# %% 'Sortino_Ratio', 
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Sortino_Ratio'])
plt.xlabel('Sortino_Ratio')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['Sortino_Ratio']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['Sortino_Ratio_log_normalize'] = np.log1p(df['Sortino_Ratio'])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Sortino_Ratio_log_normalize'])
plt.xlabel('Sortino_Ratio_log_normalize')
plt.grid(True)
plt.show()
# %%Max_Drawdown'
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Max_Drawdown'])
plt.xlabel('Max_Drawdown')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['Max_Drawdown']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['Max_Drawdown_winsorized'] = winsorize(df['Max_Drawdown'], limits=[0.03, 0.03])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Max_Drawdown_winsorized'])
plt.xlabel('Max_Drawdown_winsorized')
plt.grid(True)
plt.show()
# %%'Rolling_Volatility_21D'
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Rolling_Volatility_21D'])
plt.xlabel('Rolling_Volatility_21D')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['Rolling_Volatility_21D']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['Rolling_Volatility_21D_winsorized'] = winsorize(df['Rolling_Volatility_21D'], limits=[0.03, 0.03])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Rolling_Volatility_21D_winsorized'])
plt.xlabel('Rolling_Volatility_21D_winsorized')
plt.grid(True)
plt.show()
# %%'Rolling_Volatility_Quarter'
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Rolling_Volatility_Quarter'])
plt.xlabel('Rolling_Volatility_Quarter')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['Rolling_Volatility_Quarter']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['Rolling_Volatility_Quarter_winsorized'] = winsorize(df['Rolling_Volatility_Quarter'], limits=[0.03, 0.03])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Rolling_Volatility_Quarter'])
plt.xlabel('Rolling_Volatility_Quarter')
plt.grid(True)
plt.show()
# %%'Rolling_Volatility_Year'
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Rolling_Volatility_Year'])
plt.xlabel('Rolling_Volatility_Year')
plt.grid(True)
plt.show()
# %%
outliers_if = iso.fit_predict(df[['Rolling_Volatility_Year']])  # returns -1 for outliers
print(f"Number of outliers using Isolation Forest: {(outliers_if == -1).sum()}")
# %%Apply log transformation to 'NAV' column
df['Rolling_Volatility_Year_winsorized'] = winsorize(df['Rolling_Volatility_Year'], limits=[0.03, 0.03])
# %%
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['Rolling_Volatility_Year_winsorized'])
plt.xlabel('Rolling_Volatility_Year_winsorized')
plt.grid(True)
plt.show()
# %%
df.shape
# %%
output_path = r"C:\Users\prana\Downloads\Mutual_funds\after_phase_3(transformation).csv"
df.to_csv(output_path, index=False)
print(f"✅ Cleaned data saved to: {output_path}")

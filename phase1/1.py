#%%
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 
import re 
from scipy.stats import zscore 
#%% Load Dataset 
file_path = r"C:\Users\prana\Downloads\Mutual_funds\all-funds-nav.csv" 
# Load data with error handling for bad lines 
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
# %%
try: 
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce') 
except Exception as e: 
    print(f"⚠️ Date conversion error: {e}")
# %%
#Drop any rows with invalid dates 
df = df[df['Date'].notnull()]
# %%
df.isnull().sum()
# %%  Convert NAV to float (handle errors) 
df['NAV'] = pd.to_numeric(df['NAV'], errors='coerce')
# %%
print(df.isnull().sum())
print(df.info())
# %%
df.dropna(subset=['NAV', 'Scheme', 'Fund House'], inplace=True)
# %%
df.sort_values(by=['SchemeID', 'Date'], inplace=True)
# %%
df.drop_duplicates(inplace=True)
# %%
print(df.isnull().sum())
# %%
# For each SchemeID, check number of dates
date_counts = df.groupby('SchemeID')['Date'].nunique()
total_dates = df['Date'].nunique()

# Schemes with missing dates
incomplete_schemes = date_counts[date_counts < total_dates]
print("Number of schemes with missing dates:", len(incomplete_schemes))
# %%
# Number of total trading days
total_dates = df['Date'].nunique()

# Calculate missing days per scheme
missing_counts = total_dates - date_counts
missing_counts = missing_counts.sort_values(ascending=False)

# Basic stats
print(missing_counts.describe())

# Visualize
import matplotlib.pyplot as plt

missing_counts.plot(kind='hist', bins=50, figsize=(10,5), title="Missing Dates per Scheme")
plt.xlabel("Number of Missing Dates")
plt.ylabel("Number of Schemes")
plt.show()
# %%
allowed_missing = int(0.3 * total_dates)
valid_schemes = missing_counts[missing_counts <= allowed_missing].index
filtered_df = df[df['SchemeID'].isin(valid_schemes)]

# %%
df.shape
# %%
print(df.isnull().sum())
# %%
# Check for negative or zero NAV values
invalid_nav = df[df['NAV'] <= 0]

# Print summary
print(f"Total entries with NAV <= 0: {len(invalid_nav)}")
# %%
# Remove rows where NAV is less than or equal to 0
df_cleaned = df[df['NAV'] > 0].copy()

# Check the shape after cleaning
print(f"Original shape: {df.shape}")
print(f"Cleaned shape: {df_cleaned.shape}")
# %%
import seaborn as sns
import matplotlib.pyplot as plt

sns.boxplot(df_cleaned['NAV'])
plt.title("Boxplot of NAV values")
plt.show()
# %%
# Save the cleaned data to a new CSV file
output_path = r"C:\Users\prana\Downloads\Mutual_funds\after_phase_1.csv"
df_cleaned.to_csv(output_path, index=False)

print(f"✅ Cleaned data saved to: {output_path}")

# %%

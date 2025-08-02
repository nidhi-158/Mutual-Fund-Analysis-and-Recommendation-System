import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 
from sklearn.preprocessing import StandardScaler 
from sklearn.decomposition import PCA 
from sklearn.cluster import KMeans 
from sklearn.metrics import silhouette_score, classification_report, confusion_matrix 
from sklearn.model_selection import train_test_split 
from sklearn.ensemble import RandomForestClassifier 
import joblib 
 
#%% Step 1: Load the already scaled dataset 
file_path = r"/content/drive/Shareddrives/MF_57/Mutual_funds/AFTER_PHASE_3(transformation).csv" 
df = pd.read_csv(file_path, low_memory=False, encoding="utf-8", 
on_bad_lines='skip') 
 
df.shape 
 
df.info() 
 
df.isnull().sum() 
 
df.columns 
 
# Ensure 'Date' is datetime 
df['Date'] = pd.to_datetime(df['Date'], errors='coerce') 
 
#%% Step 3: Handle missing values 
for col in ['Sharpe_Ratio_log_normalize', 'Sortino_Ratio_log_normalize']: 
    df[col] = df[col].fillna(df[col].median()) 
 
# Ensure 'Date' is datetime 
df['Date'] = pd.to_datetime(df['Date'], errors='coerce') 
 
#%% Step 3: Handle missing values 
for col in ['Sharpe_Ratio_log_normalize', 'Sortino_Ratio_log_normalize']: 
    df[col] = df[col].fillna(df[col].median()) 
 
#%% Step 4: Define Set 5 Features (Pure Volatility + Downside) 
set5_features = [ 
    'Yearly_Return_winsorized', 
    'Monthly_Return_winsorized','Yearly_STD_winsorized', 
    'Monthly_STD_winsorized', 
    'Max_Drawdown_winsorized', 
    'Sharpe_Ratio_log_normalize','CAGR_1Y_winsorized' 
] 
 
# Prepare features 
X = df[set5_features].dropna() 
 
#%% Step 5: Standardize 
scaler = StandardScaler() 
X_scaled = scaler.fit_transform(X) 
 
#%% Step 6: Apply PCA 
pca = PCA(n_components=2, random_state=42) 
X_pca = pca.fit_transform(X_scaled) 
 
#%% Step 7: Apply KMeans on PCA-transformed data 
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10) 
cluster_labels = kmeans.fit_predict(X_pca) 
 
#%% Step 8: Print Inertia 
final_inertia = kmeans.inertia_ 
print(f"✅Final KMeans Inertia: {final_inertia:.2f}") 
 
#%% Step 9: Visualize Clusters 
pca_df = pd.DataFrame() 
pca_df['PCA1'] = X_pca[:,0] 
pca_df['PCA2'] = X_pca[:,1] 
pca_df['Cluster'] = cluster_labels 
 
plt.figure(figsize=(10,7)) 
sns.scatterplot(data=pca_df, x='PCA1', y='PCA2', hue='Cluster', 
palette='viridis', s=30,alpha=0.7) 
plt.title('📊2D Visualization of Risk Clusters', fontsize=16) 
plt.xlabel('Principal Component 1') 
plt.ylabel('Principal Component 2') 
plt.legend(title='Cluster') 
plt.grid(True) 
plt.show() 
 
kmeans.inertia_ 
 
#%% Step 10: Attach Cluster Labels to Original Data 
df_clustered = df.copy() 
df_clustered = df_clustered.loc[X.index]  # Ensure same rows as X 
df_clustered['Cluster_Label'] = cluster_labels 
 
# Optional: Map cluster numbers to Risk Levels (based on domain or PCA space) 
risk_map = { 
    0: 'Low',     # You can adjust based on visualization understanding 
    1: 'Medium', 
    2: 'High' 
} 
df_clustered['Risk_Level'] = df_clustered['Cluster_Label'].map(risk_map) 
 
#%% Step 11: Train Random Forest Classifier 
from sklearn.ensemble import RandomForestClassifier 
from sklearn.model_selection import train_test_split 
from sklearn.metrics import classification_report 
 
# Define input and target 
X_rf = df_clustered[set5_features]  # original features, not PCA-transformed 
y_rf = df_clustered['Cluster_Label'] 
 
# Train-Test Split 
X_train, X_test, y_train, y_test = train_test_split(X_rf, y_rf, test_size=0.2, random_state=42, stratify=y_rf) 
 
# Random Forest Model 
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42) 
rf_classifier.fit(X_train, y_train) 
 
# Predict and Evaluate 
y_pred = rf_classifier.predict(X_test) 
 
print("✅Random Forest Classification Report:\n") 
print(classification_report(y_test, y_pred)) 
 
#%% Step 12: Save Models for Later Use 
#import joblib 
 
# Save Random Forest model 
#joblib.dump(rf_classifier, 'random_forest_risk_classifier.pkl') 
 
# Save Scaler used for features 
#joblib.dump(scaler, 'scaler_for_rf_model.pkl') 
 
# Save PCA transformer 
#joblib.dump(pca, 'pca_transformer.pkl') 
 
# Save KMeans model 
#joblib.dump(kmeans, 'kmeans_model.pkl') 
 
#print("✅All models saved successfully!") 
 
#%% Step 13: Optional - Feature Importance Visualization 
importances = rf_classifier.feature_importances_ 
feature_names = set5_features 
 
plt.figure(figsize=(10,6)) 
sns.barplot(x=importances, y=feature_names, palette='coolwarm') 
plt.title('Feature Importance (Random Forest)', fontsize=16) 
plt.xlabel('Importance Score') 
plt.ylabel('Feature') 
plt.grid(True) 
plt.show() 
 
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay 
 
# Step 1: Generate the confusion matrix 
conf_matrix = confusion_matrix(y_test, y_pred) 
 
# Step 2: Display the matrix with labels 
disp = ConfusionMatrixDisplay(confusion_matrix=conf_matrix, 
                              display_labels=['Cluster 0', 'Cluster 1', 
'Cluster 2'])  # adjust if you mapped to risk levels 
 
# Step 3: Plot it 
plt.figure(figsize=(6, 5)) 
disp.plot(cmap='Blues', values_format='d')  # 'd' = integer formatting 
plt.title('📊Confusion Matrix - Random Forest Risk Classifier') 
plt.xlabel('Predicted Cluster') 
plt.ylabel('True Cluster') 
plt.grid(False) 
plt.show() 
 
# If your cluster labels are in 'Cluster_Label' column 
cluster_counts = df_clustered['Cluster_Label'].value_counts().sort_index() 
 
print("📊Number of records in each cluster:") 
print(cluster_counts) 
 
risk_counts = df_clustered['Risk_Level'].value_counts() 
 
print("\n📊Number of records in each Risk Level:") 
print(risk_counts) 
 
import seaborn as sns 
import matplotlib.pyplot as plt 
 
sns.countplot(data=df_clustered, x='Cluster_Label', palette='viridis') 
plt.title("Distribution of Records Across Clusters") 
plt.xlabel("Cluster Label") 
plt.ylabel("Number of Records") 
plt.show() 
 
import joblib 
 
# 1. Save updated clustered DataFrame with new name 
df_clustered.to_csv("/content/drive/Shareddrives/MF_57/Mutual_funds/df_clustered_phase_5_final.csv", index=False) 
print("✅New clustered DataFrame saved as df_clustered_phase_5_final.csv") 
 
# 2. Save new Random Forest model 
joblib.dump(rf_classifier, "/content/drive/Shareddrives/MF_57/Mutual_funds/random_forest_risk_classifier_final.pkl") 
print("✅New Random Forest model saved as random_forest_risk_classifier_final.pkl") 
 
# 3. Save new Scaler 
joblib.dump(scaler, "/content/drive/Shareddrives/MF_57/Mutual_funds/scaler_for_rf_model_final.pkl") 
print("✅New scaler saved as scaler_for_rf_model_final.pkl") 
 
# 4. Save new PCA transformer 
joblib.dump(pca, "/content/drive/Shareddrives/MF_57/Mutual_funds/PCA_transformer_final.pkl") 
print("✅New PCA transformer saved as PCA_transformer_final.pkl") 
 
# 5. Save new KMeans model 
joblib.dump(kmeans, 
"/content/drive/Shareddrives/MF_57/Mutual_funds/KMeans_model_final.pkl") 
print("✅New KMeans model saved as KMeans_model_final.pkl") 
 
# Save the full DataFrame after clustering and risk labeling 
df_clustered.to_csv("/content/drive/Shareddrives/MF_57/Mutual_funds/phase5_processed_funds_data_final.csv", index=False) 
 
print("✅Phase 5 processed data saved as 'phase5_processed_funds_data_final.csv'")

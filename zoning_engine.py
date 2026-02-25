import pandas as pd
from sklearn.cluster import KMeans
import pickle
import os
import glob

# --- CONFIGURATION ---
MODEL_OUTPUT = 'zone_model.pkl'
N_ZONES = 4 

def train_zoning_model():
    print("🛰️  SPECTRE SYSTEM: Initializing Global Dynamic Zoning...")
    
    tracking_files = sorted(glob.glob('mosaic_history_*.csv'))
    
    if not tracking_files:
        print("❌ Error: No 'mosaic_history_*.csv' files found in the directory.")
        return

    print(f"📁 Found {len(tracking_files)} tracking files. Combining data for Global AI Training...")
    
    all_coords = []
    for file in tracking_files:
        try:
            df_part = pd.read_csv(file, usecols=['x', 'y'])
            all_coords.append(df_part)
            print(f"   -> Loaded {len(df_part)} points from {file}")
        except Exception as e:
            print(f"   ❌ Error reading {file}: {e}")
            
    # SAFETY CHECK: Ensure we actually loaded data before concatenating
    if not all_coords:
        print("❌ Error: No valid data could be extracted from the tracking files.")
        return

    df_combined = pd.concat(all_coords, ignore_index=True)
    
    # Clean the data for spatial mapping
    unique_coords = df_combined.drop_duplicates()
    
    print(f"\n🧬 Analyzing {len(unique_coords)} unique density points across the entire week...")

    # Train K-Means
    kmeans = KMeans(n_clusters=N_ZONES, init='k-means++', random_state=42, n_init=10)
    kmeans.fit(unique_coords)

    # Save the model
    kmeans.feature_names_in_ = ['x', 'y'] 
    with open(MODEL_OUTPUT, 'wb') as f:
        pickle.dump(kmeans, f)
    
    print(f"\n✅ Step 1 Complete: Global AI Model saved to {MODEL_OUTPUT}")
    
    centers = kmeans.cluster_centers_
    for i, center in enumerate(centers):
        print(f"📍 Zone {i} Center: X={center[0]:.0f}, Y={center[1]:.0f}")

if __name__ == "__main__":
    train_zoning_model()
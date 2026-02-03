import pandas as pd
from sklearn.cluster import KMeans
import pickle
import os

# --- CONFIGURATION ---
INPUT_FILE = 'mosaic_history_24.csv'
MODEL_OUTPUT = 'zone_model.pkl'
N_ZONES = 4 

def train_zoning_model():
    print("🛰️  SPECTRE SYSTEM: Initializing Dynamic Zoning...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: {INPUT_FILE} not found.")
        return

    # 1. Load coordinates
    # FIX: Using usecols to save memory and ensure we only pull x,y
    df = pd.read_csv(INPUT_FILE, usecols=['x', 'y'])
    
    # FIX: Dropping duplicates for training. 
    # If a person stands still for 1000 frames, we don't want to over-weight 
    # that one spot. We want to find general store "areas".
    unique_coords = df.drop_duplicates()
    
    print(f"🧬 Analyzing {len(unique_coords)} unique density points...")

    # 2. Train K-Means
    # init='k-means++' ensures better initial placement of centers
    kmeans = KMeans(n_clusters=N_ZONES, init='k-means++', random_state=42, n_init=10)
    kmeans.fit(unique_coords)

    # 3. Save the model and the feature names
    # FIX: We save the feature names to prevent "UserWarnings" in future 
    # when predicting coordinates in different scripts.
    kmeans.feature_names_in_ = ['x', 'y'] 

    with open(MODEL_OUTPUT, 'wb') as f:
        pickle.dump(kmeans, f)
    
    print(f"✅ Step 1 Complete: Model saved to {MODEL_OUTPUT}")
    
    # 4. Show discovered centers
    centers = kmeans.cluster_centers_
    for i, center in enumerate(centers):
        print(f"📍 Zone {i} Center: X={center[0]:.0f}, Y={center[1]:.0f}")

if __name__ == "__main__":
    train_zoning_model()
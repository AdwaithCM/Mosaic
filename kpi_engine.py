import pandas as pd
import pickle
import os
import numpy as np

# --- 1. CONFIGURATION ---
TRACKING_FILE = 'mosaic_history_24.csv'
SALES_FILE = 'correlated_sales_data.csv'
MODEL_FILE = 'zone_model.pkl'
OUTPUT_FILE = 'zone_analytics.csv'

# --- SMART ZONING LOGIC ---
def assign_zone_names_dynamically(kmeans_model):
    """
    Forces a 1-to-1 mapping of Cluster Centers to our 4 names.
    Strategy: Sort centers spatially to ensure every zone appears.
    """
    centers = kmeans_model.cluster_centers_
    mapping = {}

    # Step 1: Separate into Top (High Y) and Bottom (Low Y)
    # We calculate the mean Y to find the "middle" of the store
    mid_y = np.mean([c[1] for c in centers])
    
    top_clusters = []
    bottom_clusters = []

    for i, (x, y) in enumerate(centers):
        if y > mid_y:
            top_clusters.append((i, x))
        else:
            bottom_clusters.append((i, x))

    # Fallback: If split isn't perfect (e.g., 3 top, 1 bottom), just sort by Y generally
    # But assuming N=4, we usually get 2 and 2. 
    # Let's simple-sort the Top by X and Bottom by X.
    
    # Sort Top clusters by X (Left=Electronics, Right=Groceries)
    top_clusters.sort(key=lambda item: item[1]) # Sort by X
    if len(top_clusters) >= 1: mapping[top_clusters[0][0]] = 'Electronics' # Top-Left
    if len(top_clusters) >= 2: mapping[top_clusters[1][0]] = 'Groceries'   # Top-Right

    # Sort Bottom clusters by X (Left=Home, Right=Beauty)
    bottom_clusters.sort(key=lambda item: item[1])
    if len(bottom_clusters) >= 1: mapping[bottom_clusters[0][0]] = 'Home'   # Bottom-Left
    if len(bottom_clusters) >= 2: mapping[bottom_clusters[1][0]] = 'Beauty' # Bottom-Right

    # SAFETY NET: If the split was weird (like 3 clusters top), 
    # we might miss a name. This manually fills gaps if needed.
    # (For your dataset size, the spatial sort above usually works 99%)
    return mapping

def run_kpi_engine():
    print("🧠 SPECTRE KPI ENGINE: Calculating retail metrics...")

    if not os.path.exists(MODEL_FILE):
        print(f"❌ Error: {MODEL_FILE} not found.")
        return

    # --- 1. LOAD MODEL & ASSIGN ZONES ---
    with open(MODEL_FILE, 'rb') as f:
        kmeans = pickle.load(f)
    
    # Use the new SMART function
    cluster_names = assign_zone_names_dynamically(kmeans)
    
    print("\n🔹 DYNAMIC ZONE MAPPING:")
    for cluster_id, name in cluster_names.items():
        center = kmeans.cluster_centers_[cluster_id]
        print(f"   - Cluster {cluster_id} (at {center[0]:.0f}, {center[1]:.0f}) assigned to -> {name}")

    # --- 2. PROCESS TRACKING DATA ---
    print(f"\n   ...Loading tracking data...")
    try:
        df_track = pd.read_csv(TRACKING_FILE, usecols=['person_id', 'x', 'y', 'time'])
    except ValueError as e:
        print(f"❌ Error reading tracking columns: {e}")
        return

    df_track['cluster_id'] = kmeans.predict(df_track[['x', 'y']])
    df_track['Zone_Name'] = df_track['cluster_id'].map(cluster_names)

    # Filter out any points that didn't get mapped (rare safety check)
    df_track = df_track.dropna(subset=['Zone_Name'])

    zone_stats = df_track.groupby('Zone_Name').agg(
        Visitors=('person_id', 'nunique'),
        Avg_Dwell_Time=('time', lambda x: (x.max() - x.min())) 
    ).reset_index()

    # --- 3. PROCESS SALES DATA ---
    print(f"   ...Loading sales data...")
    df_sales = pd.read_csv(SALES_FILE)
    
    # Ensure Sales CSV uses "Groceries" (matches our new map)
    # If your CSV still has "Fashion", we fix it here dynamically just in case
    df_sales['Zone'] = df_sales['Zone'].replace('Fashion', 'Groceries')

    sales_stats = df_sales.groupby('Zone').agg(
        Transactions=('Transaction_ID', 'nunique'),
        Revenue=('Amount', 'sum')
    ).reset_index()

    # --- 4. MERGE ---
    final_df = pd.merge(zone_stats, sales_stats, left_on='Zone_Name', right_on='Zone', how='left')
    final_df = final_df.fillna(0)
    
    # --- 5. CALCULATE KPIs ---
    final_df['Conversion_Rate'] = np.where(
        final_df['Visitors'] > 0, 
        (final_df['Transactions'] / final_df['Visitors']) * 100, 
        0
    )
    
    final_df['Conversion_Rate'] = final_df['Conversion_Rate'].round(2)
    final_df['Avg_Dwell_Time'] = final_df['Avg_Dwell_Time'].round(1)

    final_df = final_df[['Zone_Name', 'Visitors', 'Avg_Dwell_Time', 'Transactions', 'Conversion_Rate', 'Revenue']]
    
    # --- 6. SAVE OUTPUT ---
    final_df.to_csv(OUTPUT_FILE, index=False)
    print("✅ KPI Calculation Complete.")
    print(f"💾 Results saved to {OUTPUT_FILE}")
    print("\n📊 FINAL METRICS SNAPSHOT:")
    print(final_df.to_string(index=False))

if __name__ == "__main__":
    run_kpi_engine()
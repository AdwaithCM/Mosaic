import pandas as pd
import pickle
import os
import glob
import numpy as np

# --- 1. CONFIGURATION ---
MODEL_FILE = 'zone_model.pkl'
HISTORICAL_OUTPUT = 'historical_analytics.csv' 
LIVE_OUTPUT = 'zone_analytics.csv'             

# --- SMART ZONING LOGIC (BULLETPROOF FIX) ---
def assign_zone_names_dynamically(kmeans_model):
    centers = kmeans_model.cluster_centers_
    mapping = {}

    # Create a list of (cluster_id, x, y)
    points = [(i, c[0], c[1]) for i, c in enumerate(centers)]
    
    # Sort all 4 centers by Y-coordinate (Highest to Lowest)
    points.sort(key=lambda p: p[2], reverse=True)
    
    # Strictly split into Top 2 and Bottom 2 (No more relying on the mean!)
    top_two = points[:2]
    bottom_two = points[2:]
    
    # Sort Top Two by X (Left to Right)
    top_two.sort(key=lambda p: p[1])
    mapping[top_two[0][0]] = 'Electronics' # Top-Left
    mapping[top_two[1][0]] = 'Groceries'   # Top-Right
    
    # Sort Bottom Two by X (Left to Right)
    bottom_two.sort(key=lambda p: p[1])
    mapping[bottom_two[0][0]] = 'Home'     # Bottom-Left
    mapping[bottom_two[1][0]] = 'Beauty'   # Bottom-Right
    
    return mapping

def run_kpi_engine():
    print("🧠 SPECTRE KPI ENGINE: Initializing Time-Series Compilation...")

    if not os.path.exists(MODEL_FILE):
        print(f"❌ Error: {MODEL_FILE} not found. Run zoning_engine.py first.")
        return

    # --- 1. LOAD AI MODEL ---
    with open(MODEL_FILE, 'rb') as f:
        kmeans = pickle.load(f)
    
    cluster_names = assign_zone_names_dynamically(kmeans)
    
    print("\n🔹 DYNAMIC ZONE MAPPING:")
    for cluster_id, name in cluster_names.items():
        center = kmeans.cluster_centers_[cluster_id]
        print(f"   - Cluster {cluster_id} assigned to -> {name}")

    # --- 2. FIND ALL TRACKING FILES ---
    tracking_files = sorted(glob.glob('mosaic_history_*.csv'))
    if not tracking_files:
        print("❌ Error: No tracking files found.")
        return

    all_historical_data = []
    
    print("\n⏳ Processing Daily Metrics...")

    # --- 3. BATCH PROCESS EACH DAY ---
    for tracking_file in tracking_files:
        file_id = tracking_file.replace('mosaic_history_', '').replace('.csv', '')
        sales_file = f'sales_{file_id}.csv'
        
        if not os.path.exists(sales_file):
            print(f"   ⚠️ Warning: Missing {sales_file}. Skipping {tracking_file}...")
            continue
            
        print(f"   -> Merging {tracking_file} with {sales_file}")
        
        # A. Process Tracking
        df_track = pd.read_csv(tracking_file, usecols=['person_id', 'x', 'y', 'time'])
        df_track['cluster_id'] = kmeans.predict(df_track[['x', 'y']])
        df_track['Zone_Name'] = df_track['cluster_id'].map(cluster_names)
        df_track = df_track.dropna(subset=['Zone_Name'])

        # Calculate dwell time PER PERSON first
        person_dwell = df_track.groupby(['Zone_Name', 'person_id'])['time'].agg(lambda x: x.max() - x.min()).reset_index()
        
        # Then aggregate by zone to get average dwell time and total visitors
        zone_stats = person_dwell.groupby('Zone_Name').agg(
            Visitors=('person_id', 'count'),
            Avg_Dwell_Time=('time', 'mean') 
        ).reset_index()

        # B. Process Sales
        df_sales = pd.read_csv(sales_file)
        current_date = df_sales['Date'].iloc[0] 
        df_sales['Zone'] = df_sales['Zone'].replace('Fashion', 'Groceries')

        sales_stats = df_sales.groupby('Zone').agg(
            Transactions=('Transaction_ID', 'nunique'),
            Revenue=('Amount', 'sum')
        ).reset_index()

        # C. Merge and Calculate
        daily_df = pd.merge(zone_stats, sales_stats, left_on='Zone_Name', right_on='Zone', how='left')
        daily_df = daily_df.fillna(0)
        
        daily_df['Conversion_Rate'] = np.where(
            daily_df['Visitors'] > 0, 
            (daily_df['Transactions'] / daily_df['Visitors']) * 100, 
            0
        )
        
        daily_df['Conversion_Rate'] = daily_df['Conversion_Rate'].round(2)
        daily_df['Avg_Dwell_Time'] = daily_df['Avg_Dwell_Time'].round(1)
        
        daily_df = daily_df[['Zone_Name', 'Visitors', 'Avg_Dwell_Time', 'Transactions', 'Conversion_Rate', 'Revenue']]
        
        # D. Time-Stamp the Data
        daily_df.insert(0, 'Date', current_date)
        all_historical_data.append(daily_df)

    # --- 4. COMPILE MASTER LOG & LIVE CACHE ---
    if not all_historical_data:
        print("❌ Error: No pairs were successfully processed.")
        return

    # Create the Master Data Warehouse
    master_df = pd.concat(all_historical_data, ignore_index=True)
    master_df.to_csv(HISTORICAL_OUTPUT, index=False)
    
    # Create the Live Cache using the LAST processed day
    latest_day_df = all_historical_data[-1].drop(columns=['Date']) 
    latest_day_df.to_csv(LIVE_OUTPUT, index=False)
    
    latest_date_str = all_historical_data[-1]['Date'].iloc[0]

    print(f"\n✅ KPI Compilation Complete!")
    print(f"💾 Master Database saved to: {HISTORICAL_OUTPUT} ({len(master_df)} rows total)")
    print(f"💾 Live Dashboard Cache saved to: {LIVE_OUTPUT} (Updated to {latest_date_str})")

if __name__ == "__main__":
    run_kpi_engine()
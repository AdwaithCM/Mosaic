import pandas as pd
import numpy as np
import random
import os
import glob
import pickle
from datetime import datetime, timedelta

# --- 1. CONFIGURATION ---
BASE_SIMULATION_DATE = datetime(2026, 1, 20, 9, 0, 0) # Starting date for our historical time-series
MODEL_FILE = 'zone_model.pkl'

# Product Catalog
zones_catalog = {
    'Electronics': {'products': ['4K TV', 'Headphones', 'Smart Watch'], 'price': [200, 1500]},
    'Groceries':   {'products': ['Organic Coffee', 'Artisan Bread', 'Fresh Produce'], 'price': [10, 60]},
    'Home':        {'products': ['Lamp', 'Cushion', 'Frame'], 'price': [15, 80]},
    'Beauty':      {'products': ['Perfume', 'Lipstick', 'Skincare Set'], 'price': [30, 150]}
}

# --- 2. LOAD AI MODEL & MAPPING ---
if not os.path.exists(MODEL_FILE):
    print(f"❌ Error: '{MODEL_FILE}' not found. Please run zoning_engine.py first.")
    exit()

with open(MODEL_FILE, 'rb') as f:
    kmeans = pickle.load(f)

# EXACT mapping function from kpi_engine.py to guarantee synchronization
def assign_zone_names_dynamically(kmeans_model):
    centers = kmeans_model.cluster_centers_
    mapping = {}
    points = [(i, c[0], c[1]) for i, c in enumerate(centers)]
    points.sort(key=lambda p: p[2], reverse=True)
    
    top_two = points[:2]
    bottom_two = points[2:]
    
    top_two.sort(key=lambda p: p[1])
    mapping[top_two[0][0]] = 'Electronics' 
    mapping[top_two[1][0]] = 'Groceries'   
    
    bottom_two.sort(key=lambda p: p[1])
    mapping[bottom_two[0][0]] = 'Home'     
    mapping[bottom_two[1][0]] = 'Beauty'   
    
    return mapping

cluster_names = assign_zone_names_dynamically(kmeans)

# --- 3. BATCH PROCESS ALL TRACKER FILES ---
tracking_files = sorted(glob.glob('mosaic_history_*.csv'))

if not tracking_files:
    print("❌ Error: No 'mosaic_history_*.csv' files found in the directory.")
    exit()

print(f"📁 Found {len(tracking_files)} tracking files. Starting Batch Processing...")

for day_index, input_file in enumerate(tracking_files):
    file_id = input_file.replace('mosaic_history_', '').replace('.csv', '')
    output_file = f'sales_{file_id}.csv'
    current_day_start = BASE_SIMULATION_DATE + timedelta(days=day_index)
    
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"❌ Error reading '{input_file}': {e}")
        continue

    unique_visitors = df['person_id'].unique()
    
    # Introduce dynamic daily variance (between 20% and 40% conversion as requested)
    daily_conversion_rate = random.uniform(0.20, 0.40)
    num_sales = int(len(unique_visitors) * daily_conversion_rate) 
    
    print(f"\n🔄 Processing: {input_file} -> {output_file}")
    print(f"   ℹ️ Visitors: {len(unique_visitors)} | Target Conv. Rate: {daily_conversion_rate*100:.1f}% | Sales: {num_sales}")

    # Use random.sample to guarantee NO DUPLICATE buyers
    converting_customers = random.sample(list(unique_visitors), num_sales)
    sales_data = []

    for customer_id in converting_customers:
        customer_track = df[df['person_id'] == customer_id]
        
        last_seen = customer_track.iloc[-1]
        final_x = last_seen['x']
        final_y = last_seen['y']
        exit_time_secs = last_seen['time']
        
        # USE THE AI MODEL TO PREDICT THE ZONE
        # Create a tiny dataframe with feature names matching the trained model
        coord_df = pd.DataFrame({'x': [final_x], 'y': [final_y]})
        cluster_id = kmeans.predict(coord_df)[0]
        zone_name = cluster_names.get(cluster_id, 'Beauty') # Fallback just in case
        
        sale_time = current_day_start + timedelta(seconds=float(exit_time_secs))
        
        product = random.choice(zones_catalog[zone_name]['products'])
        price = random.randint(zones_catalog[zone_name]['price'][0], zones_catalog[zone_name]['price'][1])
        
        sales_data.append({
            "Transaction_ID": f"TXN-{random.randint(10000, 99999)}",
            "Customer_ID": customer_id,
            "Date": sale_time.strftime("%Y-%m-%d"),
            "Time": sale_time.strftime("%H:%M:%S"),
            "Zone": zone_name,
            "Product": product,
            "Amount": price,
            "X_Loc": final_x,
            "Y_Loc": final_y
        })

    # Save daily sales
    sales_df = pd.DataFrame(sales_data)
    sales_df.to_csv(output_file, index=False)
    print(f"   ✅ Saved {len(sales_df)} transactions to '{output_file}'.")

print("\n🎉 All tracking data has been successfully correlated using the AI Zoning Model!")
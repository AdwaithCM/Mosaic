import pandas as pd
import random
from datetime import datetime, timedelta

# --- 1. CONFIGURATION ---
INPUT_FILE = 'mosaic_history_24.csv'  # <--- Updated to your filename
OUTPUT_FILE = 'correlated_sales_data.csv'
SIMULATION_START_DATETIME = datetime(2026, 1, 26, 9, 0, 0) 

# Define Zone Boundaries based on your map size (0-15000)
# This acts as a "Virtual Fence" for your sales logic
def get_zone_from_coords(x, y):
    # Split the 15000x15000 map into 4 quadrants
    if x < 7500 and y > 7500:
        return 'Electronics' # Top-Left
    elif x >= 7500 and y > 7500:
        return 'Fashion'     # Top-Right
    elif x < 7500 and y <= 7500:
        return 'Home'        # Bottom-Left
    else:
        return 'Beauty'      # Bottom-Right (x >= 7500, y <= 7500)

# Product Catalog
zones = {
    'Electronics': {'products': ['4K TV', 'Headphones', 'Smart Watch'], 'price': [200, 1500]},
    'Fashion':     {'products': ['Jeans', 'T-Shirt', 'Sneakers'], 'price': [20, 120]},
    'Home':        {'products': ['Lamp', 'Cushion', 'Frame'], 'price': [15, 80]},
    'Beauty':      {'products': ['Perfume', 'Lipstick'], 'price': [30, 150]}
}

# --- 2. LOAD & PROCESS TRACKER DATA ---
try:
    df = pd.read_csv(INPUT_FILE)
    print(f"✅ Loaded {len(df)} rows from {INPUT_FILE}")
except FileNotFoundError:
    print(f"❌ Error: '{INPUT_FILE}' not found.")
    exit()

# Get list of unique visitors
unique_visitors = df['person_id'].unique()
print(f"ℹ️  Found {len(unique_visitors)} unique visitors.")

# --- 3. GENERATE INTELLIGENT SALES ---
sales_data = []

# We'll simulate a sale for 30% of visitors (increased from 15% to get more data)
num_sales = int(len(unique_visitors) * 0.30) 
print(f"🚀 Generating {num_sales} smart transactions...")

for _ in range(num_sales):
    # A. Pick a Random Customer
    customer_id = random.choice(unique_visitors)
    
    # B. Get their track history
    customer_track = df[df['person_id'] == customer_id]
    
    # C. Find 'Where' and 'When' they stopped (or their last position)
    # We take the last recorded position as the "Checkout" or "Decision" point
    last_seen = customer_track.iloc[-1]
    
    final_x = last_seen['x']
    final_y = last_seen['y']
    exit_time_secs = last_seen['time']
    
    # D. Determine Zone based on Location (NOT RANDOM ANYMORE)
    zone_name = get_zone_from_coords(final_x, final_y)
    
    # E. Create Timestamp
    sale_time = SIMULATION_START_DATETIME + timedelta(seconds=float(exit_time_secs))
    
    # F. Generate Product Details
    product = random.choice(zones[zone_name]['products'])
    price = random.randint(zones[zone_name]['price'][0], zones[zone_name]['price'][1])
    
    sales_data.append({
        "Transaction_ID": f"TXN-{random.randint(10000, 99999)}",
        "Customer_ID": customer_id,
        "Date": sale_time.strftime("%Y-%m-%d"),
        "Time": sale_time.strftime("%H:%M:%S"),
        "Zone": zone_name,
        "Product": product,
        "Amount": price,
        "X_Loc": final_x, # Saving location just in case you need to debug
        "Y_Loc": final_y
    })

# --- 4. SAVE ---
sales_df = pd.DataFrame(sales_data)
sales_df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Saved to '{OUTPUT_FILE}'.")
print(sales_df[['Customer_ID', 'Zone', 'Product', 'Amount']].head())
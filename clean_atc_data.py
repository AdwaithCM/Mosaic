import pandas as pd
import os

# --- CONFIGURATION ---
INPUT_FILE = "atc-20121125.csv"       # The file you renamed
OUTPUT_FILE = "mosaic_history_1125.csv" # The file your Heatmap/Dashboard needs

# 1. STORE BOUNDARIES (Keep data INSIDE this box)
# Coordinates in ATC are usually millimeters.
X_MIN, X_MAX = -6000, 9000
Y_MIN, Y_MAX = -3000, 12000

# 2. OBSTACLES / SHELVES (Remove data INSIDE these boxes)
# These coordinates must be relative to the *normalized* store (0 to 15000).
# You will need to tweak these numbers based on your specific 'store_layout.png'.
# Format: (x_min, x_max, y_min, y_max)
# 2. OBSTACLES / SHELVES (Remove data INSIDE these boxes)
# Coordinates estimated from 'final_heatmap1118.png'
# Format: (x_min, x_max, y_min, y_max)
RESTRICTED_ZONES = [
    # --- BOTTOM LEFT ---
    (2000, 4500, 1500, 3000),    # Checkout & Service Counters
    
    # --- MIDDLE LEFT ---
    (2500, 4000, 5500, 7000),    # 'Promotional' Circular Rack Area
    (3000, 5000, 8000, 10000),   # 'Seasonal' Area Shelves

    # --- TOP LEFT ---
    (2000, 5000, 10000, 13000),  # Drinks & Refrigerated Section Wall
    
    # --- TOP RIGHT ---
    (7000, 9000, 11000, 12000),  # Home Goods Shelves
    (10000, 12500, 12000, 14000),# Electronics Section Wall/Counters
    
    # --- MIDDLE RIGHT ---
    (8500, 10500, 9000, 11000),  # Apparel Racks (Cluster of shelves)

    # --- BOTTOM RIGHT (GROCERY AISLES) ---
    # These are thin long rectangles representing the actual shelves
    (6000, 10000, 2500, 3200),   # Grocery Shelf Row 1 (Bottom)
    (5500, 9500, 4500, 5200),    # Grocery Shelf Row 2 (Middle)
    
    # --- ENTRANCE / EXIT BUFFERS (Optional) ---
    # Sometimes data is messy at the very edges of the map
    (0, 1000, 0, 15000),         # Left Edge Buffer
    (14000, 15000, 0, 15000),    # Right Edge Buffer
]

print(f"⏳ Looking for {INPUT_FILE}...")

if not os.path.exists(INPUT_FILE):
    print(f"❌ Error: Could not find '{INPUT_FILE}'.")
    print("   Please rename your downloaded ATC file to 'atc_raw.csv' and place it here.")
    exit()

# --- STEP 1: LOAD DATA ---
print("   Loading dataset (this might take a moment)...")

column_names = ["time", "person_id", "x", "y", "z", "velocity", "angle", "facing"]

try:
    # Loading 500k rows for demo speed
    df = pd.read_csv(INPUT_FILE, names=column_names, header=None, nrows=500000)
except Exception as e:
    print(f"❌ Error reading CSV: {e}")
    exit()

print(f"   Loaded {len(df)} rows.")

# --- STEP 2: CROP TO STORE BOUNDARIES ---
print("   Cropping to store boundaries...")
df_shop = df[
    (df['x'] >= X_MIN) & (df['x'] <= X_MAX) &
    (df['y'] >= Y_MIN) & (df['y'] <= Y_MAX)
].copy()

if df_shop.empty:
    print("⚠️ Warning: Crop resulted in 0 rows. Check your X/Y MIN/MAX values.")
    exit()

print(f"   Rows inside store: {len(df_shop)}")

# --- STEP 3: NORMALIZE COORDINATES ---
# Shift coordinates so the store starts at (0,0)
df_shop['x'] = df_shop['x'] - X_MIN
df_shop['y'] = df_shop['y'] - Y_MIN

# --- STEP 3.5: REMOVE POINTS INSIDE WALLS/SHELVES ---
print("   Filtering out aisles and shelf boundaries...")
initial_count = len(df_shop)

for (r_xmin, r_xmax, r_ymin, r_ymax) in RESTRICTED_ZONES:
    # We keep only the rows that are NOT inside the restricted rectangle
    df_shop = df_shop[~((df_shop['x'] >= r_xmin) & (df_shop['x'] <= r_xmax) &
                        (df_shop['y'] >= r_ymin) & (df_shop['y'] <= r_ymax))]

removed_count = initial_count - len(df_shop)
print(f"   Removed {removed_count} noise points found inside solid objects.")

# --- STEP 4: CLEANUP ---
final_df = df_shop[['time', 'person_id', 'x', 'y', 'velocity']]

start_time = final_df['time'].min()
final_df['time'] = final_df['time'] - start_time

if final_df['time'].max() > 100000: 
    final_df['time'] = final_df['time'] / 1000

final_df['time'] = final_df['time'].astype(int)

# --- SAVE ---
final_df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Success! Created '{OUTPUT_FILE}' with {len(final_df)} rows.")
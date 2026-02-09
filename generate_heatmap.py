import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg

# --- CONFIGURATION ---
DATA_FILE = "mosaic_history_1121.csv"       # Your cleaned ATC data
MAP_FILE = "store_layout2.png"          # Your cleaned floor plan image
OUTPUT_FILE = "final_heatmap1121.png"         # Result file

# --- MAP SCALING (Crucial Step) ---
# We need to stretch your .png map to match the millimeters of the ATC data.
# Based on your cleaning script:
# Width (X): -6000 to 9000 = 15,000 units (approx 15 meters)
# Height (Y): -3000 to 12000 = 15,000 units (approx 15 meters)
# Format: [Left, Right, Bottom, Top]
MAP_EXTENT = [-5000, 22500, -1000, 15000]

print(f"⏳ Loading data from {DATA_FILE}...")
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    print("❌ Error: Data file not found.")
    exit()

print(f"⏳ Loading map from {MAP_FILE}...")
try:
    map_img = mpimg.imread(MAP_FILE)
except FileNotFoundError:
    print("❌ Error: Map image not found.")
    exit()

# --- PLOTTING ---
print("🎨 Generative AI is rendering the heatmap...")

# 1. Setup the figure size (Make it square to match your 15mx15m crop)
plt.figure(figsize=(10, 10))

# 2. Draw the Map (Background)
# 'extent' stretches the image to fit the coordinate system
plt.imshow(map_img, extent=MAP_EXTENT, cmap='gray', alpha=1, zorder=1)

# 3. Draw the Heatmap (Foreground)
# We use a 'Spectral_r' colormap (Red=Hot, Blue=Cold)
# fill=True creates the solid color blobs
# alpha=0.6 makes it transparent so you can see the shelves underneath
sns.kdeplot(
    x=df['x'], 
    y=df['y'], 
    fill=True, 
    thresh=0.05,           # Removes the lowest 5% of noise (cleans up the blue edges)
    levels=100,            # More levels = smoother gradients
    cmap="Spectral_r",     # The classic heatmap colors
    alpha=0.6,
    zorder=2
)

# 4. Styling
plt.title("Mosaic: Spatial Intelligence Heatmap", fontsize=14, fontweight='bold')
plt.xlabel("Store Width (mm)")
plt.ylabel("Store Depth (mm)")
plt.grid(False) # Turn off grid so it looks like a clean app dashboard

# --- SAVE & SHOW ---
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
print(f"✅ Success! Heatmap saved to '{OUTPUT_FILE}'")
plt.show()
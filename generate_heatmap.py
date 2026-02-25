import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
import os
import glob
import pickle
import numpy as np
from datetime import datetime, timedelta

# --- 1. CONFIGURATION ---
STATIC_FOLDER = 'static'
MAP_FILE = 'store_map.png'  # Your teammate's layout file
MODEL_FILE = 'zone_model.pkl'
BASE_SIMULATION_DATE = datetime(2026, 1, 20)

# --- 2. DYNAMIC ZONING LOGIC ---
def assign_zone_names_dynamically(kmeans_model):
    centers = kmeans_model.cluster_centers_
    points = [(i, c[0], c[1]) for i, c in enumerate(centers)]
    # Sort by Y-coordinate (Highest to Lowest)
    points.sort(key=lambda p: p[2], reverse=True)
    
    top_two = points[:2]
    bottom_two = points[2:]
    
    # Sort each pair by X (Left to Right)
    top_two.sort(key=lambda p: p[1])
    bottom_two.sort(key=lambda p: p[1])
    
    return {
        top_two[0][0]: 'Electronics', top_two[1][0]: 'Groceries',
        bottom_two[0][0]: 'Home', bottom_two[1][0]: 'Beauty'
    }

def generate_all_heatmaps():
    if not os.path.exists(MODEL_FILE):
        print("❌ Error: zone_model.pkl not found.")
        return

    # Load AI Model
    with open(MODEL_FILE, 'rb') as f:
        kmeans = pickle.load(f)
    cluster_names = assign_zone_names_dynamically(kmeans)

    tracking_files = sorted(glob.glob('mosaic_history_*.csv'))
    
    for day_index, input_file in enumerate(tracking_files):
        current_date = (BASE_SIMULATION_DATE + timedelta(days=day_index)).strftime('%Y-%m-%d')
        save_path = os.path.join(STATIC_FOLDER, f'heatmap_{current_date}.png')
        
        df = pd.read_csv(input_file, usecols=['x', 'y'])

        # Create Figure
        fig, ax = plt.subplots(figsize=(12, 12))
        
        # 1. Overlay the Store Layout Background
        if os.path.exists(MAP_FILE):
            map_img = mpimg.imread(MAP_FILE)
            # Extent maps the image pixels to your 15k data coordinates
            ax.imshow(map_img, extent=[0, 15000, 0, 15000], aspect='auto', alpha=0.5, zorder=1)

        # 2. Smooth Density Heatmap (The "Glow" Effect)
        # levels: more levels = smoother gradient
        # thresh: hides low-density "noise"
        sns.kdeplot(
            data=df, x='x', y='y', 
            fill=True, cmap="Spectral_r", 
            alpha=0.6, levels=40, thresh=0.08, 
            ax=ax, zorder=2
        )

        # 3. Label Zones with AI-matched Names
        for cluster_id, name in cluster_names.items():
            center = kmeans.cluster_centers_[cluster_id]
            ax.text(
                center[0], center[1], name, 
                color='white', weight='bold', fontsize=14, 
                ha='center', va='center', zorder=3,
                bbox=dict(facecolor='black', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.5')
            )

        ax.set_xlim(0, 15000)
        ax.set_ylim(0, 15000)
        ax.axis('off')
        
        plt.savefig(save_path, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
        plt.close()
        print(f"✅ Generated: {save_path}")

if __name__ == "__main__":
    generate_all_heatmaps()
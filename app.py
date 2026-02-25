from flask import Flask, render_template, jsonify, session, redirect, url_for, request
from intelligence_engine import generate_insights
import pandas as pd
import json
import os

app = Flask(__name__)

# --- CONFIGURATION ---
ANALYTICS_FILE = 'zone_analytics.csv'
HISTORICAL_FILE = 'historical_analytics.csv' # Added the new Data Warehouse
STRATEGY_FILE = 'strategy_log.json'

# --- DATA LOADERS ---
def load_analytics():
    """Reads the Live Cache (Latest Day) KPI CSV."""
    if not os.path.exists(ANALYTICS_FILE):
        return []
    try:
        df = pd.read_csv(ANALYTICS_FILE)
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Error loading analytics: {e}")
        return []

def load_strategies():
    """Reads the AI Strategy JSON."""
    if not os.path.exists(STRATEGY_FILE):
        return []
    try:
        with open(STRATEGY_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading strategies: {e}")
        return []


def get_latest_zone_data():
    """Reads the live zone_analytics.csv cache and returns it as a dictionary for the dashboard."""
    if not os.path.exists('zone_analytics.csv'):
        print("⚠️ Warning: zone_analytics.csv not found.")
        return []
    
    try:
        df = pd.read_csv('zone_analytics.csv')
        # Converts the dataframe into a list of dictionaries that HTML can read
        return df.to_dict('records') 
    except Exception as e:
        print(f"❌ Error reading zone data: {e}")
        return []



# --- ROUTES ---

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    # 1. Load the latest zone data
    zones = get_latest_zone_data()
    
    # 2. Calculate basic metrics
    total_visitors = sum(z['Visitors'] for z in zones)
    total_revenue = sum(z['Revenue'] for z in zones)
    avg_conversion = 0
    if len(zones) > 0:
        avg_conversion = round(sum(z['Conversion_Rate'] for z in zones) / len(zones), 1)

    # 3. MOCK DATA: Historical Transactions (Keep what you had)
    total_transactions = int(total_visitors * (avg_conversion / 100))

    # --- THE GOLDEN HOUR CALCULATOR ---
    # In a real app, this would read historical time-series data. 
    # For now, we dynamically find the most stressed zone today.
    peak_zone = max(zones, key=lambda x: x['Visitors']) if zones else None
    
    peak_ops = {
        "expected_load": int(total_visitors * 1.5), # Estimate 50% more during peak
        "critical_zone": peak_zone['Zone_Name'].upper() if peak_zone else "SYSTEM_WAIT",
        "critical_issue": "SEVERE LOAD",
        "actions": [
            f"Pause restocking in {peak_zone['Zone_Name']} immediately.",
            "Open overflow registers 3 & 4.",
            f"Re-deploy 1 staff member to {peak_zone['Zone_Name']}."
        ]
    }

    return render_template('dashboard.html', 
                           zones=zones,
                           total_visitors=total_visitors,
                           total_revenue=total_revenue,
                           avg_conversion=avg_conversion,
                           total_transactions=total_transactions,
                           peak_ops=peak_ops) # Inject the new intelligence!

@app.route('/analytics')
def analytics():
    # Load the real current data for the Bar Charts
    current_data = load_analytics()
    zone_names = [item['Zone_Name'] for item in current_data]
    zone_conversions = [item['Conversion_Rate'] for item in current_data]
    
    # --- LOAD REAL HISTORICAL DATA FOR THE LINE CHART ---
    history_dates = []
    history_revenue = []
    
    if os.path.exists(HISTORICAL_FILE):
        try:
            df_hist = pd.read_csv(HISTORICAL_FILE)
            # Group by Date and sum the Revenue across all zones for that day
            daily_revenue = df_hist.groupby('Date')['Revenue'].sum().reset_index()
            
            # Convert to lists for Chart.js
            history_dates = daily_revenue['Date'].tolist()
            history_revenue = daily_revenue['Revenue'].tolist()
        except Exception as e:
            print(f"❌ Error loading historical data: {e}")
    else:
        print(f"⚠️ Warning: {HISTORICAL_FILE} not found. Charts will be empty.")

    return render_template('analytics.html', 
                           analytics_data=current_data,
                           dates=json.dumps(history_dates),
                           revenues=json.dumps(history_revenue),
                           zone_names=json.dumps(zone_names),
                           conversions=json.dumps(zone_conversions))

@app.route('/ai')
def ai_reports():
    strategies = load_strategies()
    return render_template('ai.html', strategies=strategies)

@app.route('/settings')
def settings():
    return render_template('settings.html')
    
# --- NEW ROUTE: TRIGGERS THE AI MANUALLY ---
@app.route('/run_intelligence', methods=['POST'])
def run_intelligence():
    try:
        print("⚡ Manual Trigger: Running Intelligence Engine...")
        generate_insights() 
        return jsonify({'status': 'success', 'message': 'Analysis Complete'})
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})    

if __name__ == '__main__':
    app.run(debug=True, port=5000)
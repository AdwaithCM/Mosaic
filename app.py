from flask import Flask, render_template, jsonify, redirect, url_for, request
from intelligence_engine import generate_insights
import pandas as pd
import json
import os

app = Flask(__name__)


# --- CONFIGURATION ---
# These filenames must match exactly what your Engines generate
ANALYTICS_FILE = 'zone_analytics.csv'
STRATEGY_FILE = 'strategy_log.json'

# --- DATA LOADERS ---
def load_analytics():
    """Reads the KPI CSV and returns a list of dictionaries for the UI."""
    if not os.path.exists(ANALYTICS_FILE):
        return []
    try:
        df = pd.read_csv(ANALYTICS_FILE)
        # Converts DataFrame to: [{'Zone_Name': 'Electronics', 'Visitors': 100}, ...]
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

# --- ROUTES ---

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():

    
    # 1. Load Real Data from the CSV
    data = load_analytics()
    
    # 2. Calculate Total Store Metrics (Server-Side Logic)
    # This prevents the UI from having to do complex math
    total_visitors = sum(item['Visitors'] for item in data) if data else 0
    total_revenue = sum(item['Revenue'] for item in data) if data else 0
    avg_conversion = sum(item['Conversion_Rate'] for item in data) / len(data) if data else 0
    
    return render_template('dashboard.html', 
                           zones=data, 
                           total_visitors=total_visitors, 
                           total_revenue=total_revenue,
                           avg_conversion=round(avg_conversion, 2))

@app.route('/analytics')
def analytics():

    
    # Load the real current data
    current_data = load_analytics()
    
    # --- MOCK HISTORY DATA (For Visualization) ---
    # This simulates the last 7 days of revenue
    # Notice the jump in the last 2 days (The "AI Effect")
    history_dates = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun (Today)']
    history_revenue = [12500, 13200, 11800, 12100, 14500, 16800, 17887] 
    
    # Prepare Zone Names and Conversion Rates for the Bar Chart
    zone_names = [item['Zone_Name'] for item in current_data]
    zone_conversions = [item['Conversion_Rate'] for item in current_data]
    
    return render_template('analytics.html', 
                           analytics_data=current_data,
                           dates=json.dumps(history_dates),
                           revenues=json.dumps(history_revenue),
                           zone_names=json.dumps(zone_names),
                           conversions=json.dumps(zone_conversions))

@app.route('/ai')
def ai_reports():

    
    # Future Feature: We can filter 'strategies' by date here later
    strategies = load_strategies()
    return render_template('ai.html', strategies=strategies)

@app.route('/settings')
def settings():

    # Future Feature: 'Recalibrate' button will POST to a new route here
    return render_template('settings.html')
    
# --- NEW ROUTE: TRIGGERS THE AI MANUALLY ---
@app.route('/run_intelligence', methods=['POST'])
def run_intelligence():
    try:
        print("⚡ Manual Trigger: Running Intelligence Engine...")
        generate_insights() # Calls the function from your other file
        return jsonify({'status': 'success', 'message': 'Analysis Complete'})
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})    

if __name__ == '__main__':
    # Debug=True allows auto-reload when you change code
    app.run(debug=True, port=5000)
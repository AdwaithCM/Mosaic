from flask import Flask, render_template, jsonify, session, redirect, url_for, request
from intelligence_engine import generate_insights
import pandas as pd
import json
import os
from datetime import datetime, timedelta

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
    
    # --- 🕒 DYNAMIC TIME CALCULATOR ---
    now = datetime.now()
    current_hour = now.hour

    # Determine the NEXT historical peak based on the current time
    if current_hour < 13:
        next_peak_hour = 13
        peak_time_window = "13:00 - 15:00 (Lunch Rush)"
    elif current_hour < 18:
        next_peak_hour = 18
        peak_time_window = "18:00 - 20:00 (Evening Rush)"
    else:
        # If it's past 6 PM, the next peak is tomorrow at 1 PM
        next_peak_hour = 13
        peak_time_window = "Tomorrow 13:00 - 15:00"

    # Create exact timestamp for the Javascript countdown
    target_date = now.replace(hour=next_peak_hour, minute=0, second=0, microsecond=0)
    if current_hour >= 18:
        target_date += timedelta(days=1)
    
    target_timestamp_ms = int(target_date.timestamp() * 1000)

    # --- 🧠 DYNAMIC PEAK OPERATIONS ENGINE ---
    # Extract the variables safely so peak_ops can use them
    if peak_zone:
        zone_name = peak_zone['Zone_Name'].upper()
        visitors = int(peak_zone['Visitors'])
        conv_rate = float(peak_zone['Conversion_Rate'])
        dwell_time = float(peak_zone['Avg_Dwell_Time'])
        
        dynamic_actions = []
        
        # TRIGGER 1: Conversion Rate Logic
        if conv_rate < 5.0:
            dynamic_actions.append(f"CRITICAL: {zone_name} conversion is only {conv_rate}%. Deploy 'Flash Sale' signs immediately.")
        elif conv_rate >= 8.0:
            dynamic_actions.append(f"HIGH CONVERSION ({conv_rate}%). Ensure top-shelf margin items are fully stocked.")
        else:
            dynamic_actions.append(f"Stable conversion. Monitor {zone_name} endcaps for visual appeal.")

        # TRIGGER 2: Dwell Time / Staffing Logic
        if dwell_time > 12.0:
            dynamic_actions.append(f"Customers are lingering ({dwell_time}m avg). Shift 1 extra staff member to assist and close sales.")
        else:
            dynamic_actions.append(f"Fast movement detected. Ensure checkout pathways leading from {zone_name} are totally clear.")
            
        # TRIGGER 3: Universal Crowd Control
        dynamic_actions.append(f"Expected surge to {int(visitors * 1.5)} visitors. Halt all inventory restocking in this zone by 16:30.")

        peak_ops = {
            "expected_load": int(visitors * 1.5),
            "critical_zone": zone_name,
            "critical_issue": "BOTTLENECK RISK" if dwell_time > 12.0 else "SEVERE LOAD",
            "actions": dynamic_actions,
            "target_timestamp": target_timestamp_ms, 
            "peak_time_window": peak_time_window     
        }
    else:
        # Fallback if no zone data exists
        peak_ops = {
            "expected_load": 0,
            "critical_zone": "SYSTEM WAIT",
            "critical_issue": "NO DATA",
            "actions": ["> Awaiting tracking data..."],
            "target_timestamp": target_timestamp_ms,
            "peak_time_window": peak_time_window
        }

    return render_template('dashboard.html', 
                           page='dashboard',
                           zones=zones,
                           total_visitors=total_visitors,
                           total_revenue=total_revenue,
                           avg_conversion=avg_conversion,
                           total_transactions=total_transactions,
                           peak_ops=peak_ops)

    

@app.route('/analytics')
def analytics():
    # --- AGGREGATE REAL HISTORICAL DATA FOR ALL 6 DAYS ---
    history_dates = []
    history_revenue = []
    all_data = []
    
    if os.path.exists(HISTORICAL_FILE):
        try:
            df_hist = pd.read_csv(HISTORICAL_FILE)
            
            # 1. Line Chart Data (Group by Date)
            daily_revenue = df_hist.groupby('Date')['Revenue'].sum().reset_index()
            history_dates = daily_revenue['Date'].tolist()
            history_revenue = daily_revenue['Revenue'].tolist()
            
            # 2. THE UPGRADE: 6-Day Data for Bar Chart & Table (Group by Zone)
            # We SUM the volume (Visitors/Revenue) and AVERAGE the performance (Conversion/Dwell)
            if 'Zone_Name' in df_hist.columns:
                agg_df = df_hist.groupby('Zone_Name').agg({
                    'Visitors': 'sum',
                    'Revenue': 'sum',
                    'Conversion_Rate': 'mean',
                    'Avg_Dwell_Time': 'mean'
                }).reset_index()
                
                # Round decimals for a clean UI
                agg_df['Conversion_Rate'] = agg_df['Conversion_Rate'].round(1)
                agg_df['Avg_Dwell_Time'] = agg_df['Avg_Dwell_Time'].round(0).astype(int)
                
                all_data = agg_df.to_dict('records')
        except Exception as e:
            print(f"❌ Error processing historical data: {e}")
            
    # Fallback to today's live data if historical fails
    if not all_data:
        all_data = load_analytics()

    zone_names = [item['Zone_Name'] for item in all_data]
    zone_conversions = [item['Conversion_Rate'] for item in all_data]

    return render_template('analytics.html', 
                           page='analytics',
                           analytics_data=all_data,
                           dates=json.dumps(history_dates),
                           revenues=json.dumps(history_revenue),
                           zone_names=json.dumps(zone_names),
                           conversions=json.dumps(zone_conversions))


# --- NEW ROUTE: SILENT API FOR DASHBOARD HEATMAP ---
@app.route('/api/dashboard/<date>')
def api_dashboard_data(date):
    """Fetches exact metrics for the day selected in the Dashboard dropdown."""
    try:
        if os.path.exists(HISTORICAL_FILE):
            df = pd.read_csv(HISTORICAL_FILE)
            if 'Date' in df.columns:
                day_data = df[df['Date'] == date]
                if not day_data.empty:
                    zones = day_data.to_dict('records')
                    return jsonify({
                        'total_visitors': int(sum(z['Visitors'] for z in zones)),
                        'total_revenue': int(sum(z['Revenue'] for z in zones)),
                        'avg_conversion': round(sum(z['Conversion_Rate'] for z in zones) / len(zones), 1)
                    })
        
        # Fallback to today's live data if the exact date isn't found
        zones = get_latest_zone_data()
        return jsonify({
            'total_visitors': int(sum(z['Visitors'] for z in zones)),
            'total_revenue': int(sum(z['Revenue'] for z in zones)),
            'avg_conversion': round(sum(z['Conversion_Rate'] for z in zones) / len(zones), 1) if zones else 0
        })
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({'total_visitors': 0, 'total_revenue': 0, 'avg_conversion': 0})



@app.route('/ai')
def ai_reports():
    strategies = load_strategies()
    return render_template('ai.html',page='ai', strategies=strategies)

@app.route('/settings')
def settings():
    return render_template('settings.html',page='settings')
    
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
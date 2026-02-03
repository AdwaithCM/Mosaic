import os
import json
import pandas as pd
import uuid
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

INPUT_FILE = 'zone_analytics.csv'
OUTPUT_FILE = 'strategy_log.json'
HISTORY_FILE = 'strategy_history.json'

def get_retail_context_map():
    return {
        'Electronics': 'Context: High-ticket items (TVs, Laptops). High dwell time is good (researching), but needs staff to close sales.',
        'Groceries': 'Context: Fast-moving goods. Long dwell time is BAD (means confusion). High traffic, low margin.',
        'Home': 'Context: Furniture/Decor. Requires visualization. Moderate dwell time expected.',
        'Beauty': 'Context: Impulse buys & testing. Needs high engagement. Staff interaction is key.'
    }

# --- FALLBACK SIMULATION (Updated for Detail) ---
def generate_offline_strategies(df):
    print("\n   ⚠️ API ERROR: Switching to OFFLINE MODE.")
    insights = []
    for index, row in df.iterrows():
        zone = row['Zone_Name']
        conv = row['Conversion_Rate']
        visitors = row['Visitors']
        
        # Default fallback logic
        category, priority = "General", "Medium"
        diagnosis = f"Traffic: {visitors}, Conversion: {conv}%."
        action = "Check zone for bottlenecks."
        detail = "Offline mode active. Detailed analysis unavailable."

        if conv < 5:
            category, priority = "Marketing", "High"
            action = "Launch 'Flash Sale' for impulse buyers."
            detail = f"CRITICAL: Only {conv}% of {visitors} visitors bought items. This indicates high interest but price resistance. Immediate Recommendation: Deploy red '50% OFF' signage at eye level to break hesitation."
        
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "zone": zone,
            "metrics_snapshot": {
                "visitors": int(row['Visitors']),
                "conversion": float(row['Conversion_Rate']),
                "dwell_time": float(row['Avg_Dwell_Time']),
                "revenue": float(row['Revenue'])
            },
            "ai_analysis": {
                "category": category,
                "priority": priority,
                "diagnosis": diagnosis,
                "action_plan": action,
                "expected_outcome": "Projected 10% uplift.",
                "detailed_report": detail # <--- NEW FIELD
            }
        }
        insights.append(entry)
    return insights

def generate_insights():
    print("🔮 SPECTRE INTELLIGENCE: Initializing Llama 3 (Groq)...")

    if not API_KEY or not os.path.exists(INPUT_FILE):
        print("❌ Configuration Error.")
        return
    
    df = pd.read_csv(INPUT_FILE)
    if df.empty: return

    # --- PREPARE DATA ---
    batch_data_str = ""
    context_map = get_retail_context_map()
    
    for index, row in df.iterrows():
        zone = row['Zone_Name']
        context = context_map.get(zone, "General Retail")
        batch_data_str += (
            f"--- ZONE: {zone} ---\n"
            f"{context}\n"
            f"DATA: Visitors={row['Visitors']}, Dwell Time={row['Avg_Dwell_Time']}s, "
            f"Conversion={row['Conversion_Rate']}%, Revenue=${row['Revenue']}\n\n"
        )

    # --- CALL GROQ API ---
    try:
        client = Groq(api_key=API_KEY)
        
        # --- THE SHERLOCK PROMPT ---
        prompt = (
            f"Role: Senior Retail Strategist for a flagship store.\n"
            f"Input Data:\n{batch_data_str}\n"
            f"Task: Analyze the data and generate a JSON response.\n"
            f"Rules for 'detailed_report':\n"
            f"1. Be SPECIFIC. Don't say 'improve layout'. Say 'Move high-margin items to the front'.\n"
            f"2. Cite the numbers. Say 'Since dwell time is {row['Avg_Dwell_Time']}s...'\n"
            f"3. Explain the 'Why'. Connect the metric to the behavior.\n\n"
            f"Output JSON Format:\n"
            f"{{ 'strategies': [ {{ \n"
            f"  'zone_name': '...', \n"
            f"  'category': 'Staffing/Inventory/Marketing/Layout', \n"
            f"  'priority': 'High/Medium/Low', \n"
            f"  'diagnosis': 'Short summary (1 sentence)', \n"
            f"  'action_plan': 'Short tactic (Max 10 words)', \n"
            f"  'detailed_report': 'Long paragraph (50-80 words) explaining the problem and specific solution.', \n"
            f"  'expected_outcome': '...' \n"
            f"}} ] }}"
        )

        print("   ...Sending Data to Llama 3...")
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a JSON-only API. Output strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.6,
            response_format={"type": "json_object"}
        )

        response_text = chat_completion.choices[0].message.content
        master_json = json.loads(response_text)
        
        # Merging Logic
        strategies_list = master_json.get('strategies', [])
        current_insights = []
        for item in strategies_list:
            zone_name = item.get('zone_name')
            matching_rows = df[df['Zone_Name'] == zone_name]
            
            if not matching_rows.empty:
                original_row = matching_rows.iloc[0]
                entry = {
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat(),
                    "zone": zone_name,
                    "metrics_snapshot": {
                        "visitors": int(original_row['Visitors']),
                        "conversion": float(original_row['Conversion_Rate']),
                        "revenue": float(original_row['Revenue'])
                    },
                    "ai_analysis": item # Directly use the AI's rich object
                }
                current_insights.append(entry)
        
        print("   ✅ Llama 3 Analysis Successful!")

    except Exception as e:
        print(f"   ⚠️ Groq API Failed: {e}")
        current_insights = generate_offline_strategies(df)

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(current_insights, f, indent=4)
    print(f"✅ Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_insights()
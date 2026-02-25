import os
import json
import pandas as pd
import uuid
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("API_KEY")

INPUT_FILE = 'zone_analytics.csv'
OUTPUT_FILE = 'strategy_log.json'

def get_retail_context_map():
    return {
        'Electronics': 'High-ticket items. High Dwell + Low Conv = Customers are confused or need staff to close the sale. High Dwell + High Conv = Excellent product engagement.',
        'Groceries': 'Fast-moving goods. Long Dwell Time is BAD (means poor layout or hard-to-find items). Low Conversion means out-of-stock items or pricing resistance.',
        'Home': 'Furniture & Decor. Moderate Dwell Time expected for visualization. Low Conversion means displays are uninspiring.',
        'Beauty': 'Impulse buys & testing. Short Dwell Time means poor display visibility. High Dwell + Low Conv means testers are used but prices are too high.'
    }

def generate_offline_strategies(df):
    print("\n   ⚠️ API ERROR: Switching to OFFLINE MODE.")
    insights = []
    for index, row in df.iterrows():
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "zone": row['Zone_Name'],
            "metrics_snapshot": {
                "visitors": int(row['Visitors']),
                "conversion": float(row['Conversion_Rate']),
                "dwell_time": float(row['Avg_Dwell_Time']),
                "revenue": float(row['Revenue'])
            },
            "ai_analysis": {
                "category": "System", "priority": "Low",
                "diagnosis": "Offline Mode Active.", "action_plan": "Check API Key.",
                "detailed_report": "The AI engine could not connect. Check your internet or Groq API key.",
                "expected_outcome": "N/A"
            }
        }
        insights.append(entry)
    return insights

def generate_insights():
    print("🔮 SPECTRE INTELLIGENCE: Initializing Llama 3.3 (Groq)...")

    if not API_KEY or not os.path.exists(INPUT_FILE):
        print("❌ Configuration Error: Missing API Key or zone_analytics.csv")
        return
    
    df = pd.read_csv(INPUT_FILE)
    if df.empty: return

    # --- 1. COMPILE STRICT DATA CONTEXT ---
    batch_data_str = ""
    context_map = get_retail_context_map()
    
    for index, row in df.iterrows():
        zone = row['Zone_Name']
        context = context_map.get(zone, "General Retail")
        batch_data_str += (
            f"ZONE: [{zone}]\n"
            f" - Rules: {context}\n"
            f" - Metrics Today: {row['Visitors']} Visitors | {row['Avg_Dwell_Time']} min Avg Dwell | {row['Conversion_Rate']}% Conversion | ₹{row['Revenue']} Revenue\n\n"
        )

    # --- 2. THE HIGH-PERFORMANCE PROMPT (MERGED & OPTIMIZED) ---
    system_prompt = (
        "Role: You are SPECTRE, an elite, data-obsessed Senior Retail Strategist for a flagship store. "
        "You analyze physical store metrics and output strict JSON. You NEVER give generic advice."
    )
    
    user_prompt = f"""
    Analyze the following retail zones based on today's tracking data:
    
    {batch_data_str}
    
    RULES FOR ANALYSIS:
    1. BE HYPER-SPECIFIC: Never use generic phrases like "improve layout" or "train staff". Give exact physical commands like "Move high-margin impulse items to the front endcap."
    2. CITE THE NUMBERS: You MUST embed the exact metrics from the input data in your report (e.g., "Since dwell time is 8.5s and conversion is only 4%...").
    3. EXPLAIN THE 'WHY': Connect the metrics to human behavior and consumer psychology. Why are they dwelling but not buying? Why are they buying without dwelling?
    4. ACTIONABLE NOW: The 'action_plan' must be a physical change a store manager can execute in under 2 hours.

    OUTPUT JSON SCHEMA:
    {{
      "strategies": [
        {{
          "zone_name": "exact zone name from data",
          "category": "Staffing" or "Inventory" or "Marketing" or "Layout",
          "priority": "High" or "Medium" or "Low",
          "diagnosis": "Short summary (Max 1 sentence describing the harsh truth of the data).",
          "action_plan": "Short tactic (Max 10 words - e.g., 'Deploy red 50% OFF signage at eye level').",
          "detailed_report": "Long paragraph (50-80 words). Sentence 1: The data reality. Sentence 2: The psychological 'Why'. Sentence 3: The precise physical solution.",
          "expected_outcome": "Specific projected metric improvement (e.g., 'Projected 15% conversion uplift')."
        }}
      ]
    }}
    """

    # --- 3. CALL GROQ API ---
    try:
        client = Groq(api_key=API_KEY)
        print("   ...Transmitting Data to Neural Engine...")
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3, # Low temperature for highly logical, non-hallucinated responses
            response_format={"type": "json_object"}
        )

        response_text = chat_completion.choices[0].message.content
        master_json = json.loads(response_text)
        
        # Merge with original data
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
                        "dwell_time": float(original_row['Avg_Dwell_Time']),
                        "revenue": float(original_row['Revenue'])
                    },
                    "ai_analysis": item 
                }
                current_insights.append(entry)
        
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(current_insights, f, indent=4)
        print(f"   ✅ Llama 3 Analysis Successful! Saved to {OUTPUT_FILE}")

    except Exception as e:
        print(f"   ⚠️ Groq API Failed: {e}")
        current_insights = generate_offline_strategies(df)
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(current_insights, f, indent=4)

if __name__ == "__main__":
    generate_insights()
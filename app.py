from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# --- 1. THE GATEKEEPER (Login) ---
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    # In a real app, check password here. 
    # For now, we just redirect to the dashboard.
    return redirect(url_for('dashboard'))

# --- 2. THE CORE APPLICATION ---
@app.route('/dashboard')
def dashboard():
    # Mock Data for the Dashboard
    stats = {
        "visitors": 142, 
        "conversion": "18%", 
        "avg_time": "4m 12s",
        "hot_zone": "Electronics"
    }

    heatmap_filename = 'final_heatmap1121.png'
    return render_template('dashboard.html', page="dashboard", data=stats, heatmap_image= heatmap_filename)

@app.route('/analytics')
def analytics():
    return render_template('analytics.html', page="analytics")

@app.route('/ai-engine')
def ai_page():
    # Mock Data: Creating fake predictions to display on the UI
    mock_predictions = [
        {"time": "14:00 - 15:00", "count": 45, "confidence": "98%", "trend_icon": "arrow-up", "trend_color": "success"},
        {"time": "15:00 - 16:00", "count": 68, "confidence": "89%", "trend_icon": "arrow-up", "trend_color": "warning"},
        {"time": "16:00 - 17:00", "count": 32, "confidence": "92%", "trend_icon": "arrow-down", "trend_color": "info"},
    ]
    return render_template('ai.html', page="ai", predictions=mock_predictions)
@app.route('/settings')
def settings():
    return render_template('settings.html', page="settings")

if __name__ == '__main__':
    app.run(debug=True)
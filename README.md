# 🗺️ Mosaic

> **High-Precision Retail Analytics Platform**

Mosaic is an advanced, privacy-first retail analytics platform designed to analyze customer flow and behavior in physical store environments. By leveraging state-of-the-art Ultra-Wideband (UWB) technology, it delivers high-precision spatial data and real-time insights without the need for invasive video surveillance.

---

## ✨ Key Features

*   🔥 **Heat Mapping & Dwell Time**: Intelligently analyze customer flow, identifying high-traffic zones and measuring how long customers engage with specific store areas.
*   🛡️ **Privacy-First Design**: Built from the ground up to respect consumer privacy. Mosaic tracks anonymous spatial and motion data exclusively, completely eliminating the need for optical or video-based surveillance.
*   ⚡ **Real-Time Dashboard**: A highly responsive, interactive frontend built on React that visualizes live customer coordinates seamlessly onto a digital store map.

---

## 🛠️ Technical Stack

Mosaic's architecture is engineered for low-latency data processing and high reliability:

*   **Backend**: Python (FastAPI/Flask) - Handles complex spatial computations, data aggregation, and API serving.
*   **Database**: PostgreSQL - Robust spatial-temporal data storage for historical analytics and state management.
*   **Frontend**: React.js - Provides a fluid, real-time data visualization interface for store managers and analysts.
*   **Hardware Integration**: UWB Anchors and Tags - The physical infrastructure delivering centimeter-level positioning accuracy.

---

## 🚀 Setup

Follow these steps to set up the Mosaic environment locally.

### Prerequisites

*   Python 3.8+
*   PostgreSQL
*   Node.js & npm

### Backend Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/AdwaithCM/Mosaic.git
    cd Mosaic
    ```
2.  Set up a virtual environment:
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    *   **Windows:**
        ```cmd
        venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
4.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Frontend Installation

1.  Navigate to the frontend directory (e.g., `cd frontend`):
2.  Install dependencies:
    ```bash
    npm install
    ```

---

## 💻 Usage

To launch the Mosaic platform:

1.  **Start the Backend Server:**
    Ensure your virtual environment is activated and run your application:
    ```bash
    # For FastAPI (using Uvicorn)
    uvicorn app:app --reload
    # OR for Flask
    python app.py
    ```
2.  **Start the Frontend Application:**
    In a new terminal, navigate to the frontend directory and start the React app:
    ```bash
    npm start
    ```
3.  **Access the Dashboard:**
    Open your web browser and navigate to `http://localhost:3000` (or your configured port) to view the live tracking and heat map visualization.

---

*Designed and engineered as a high-end portfolio project showcasing real-time spatial analytics and full-stack development expertise.*

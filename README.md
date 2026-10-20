# 🌊 FloodGuard — Flood Risk Intelligence System

FloodGuard is a Streamlit-based flood-risk awareness dashboard designed to help users explore weather conditions, understand potential flood risks, and access basic flood safety guidance.

## ✨ Features

- 📍 **Location Search:** Search for a city and view its weather information.
- 🌦️ **Weather Forecast:** Explore a 7-day forecast using weather data from Open-Meteo.
- 🚦 **Flood Risk Estimation:** View an illustrative Low, Moderate, or High risk classification based on available inputs.
- 🗺️ **Interactive Map:** View the selected location on a map.
- 🛟 **Safety Center:** Access general flood preparedness and safety tips.
- 🧪 **Demo Risk Inputs:** Test how different rainfall and river-level values affect the risk estimate.

## 🛠️ Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- Folium
- Streamlit-Folium
- Requests
- Open-Meteo API

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/snehakumari1984/FloodGuard.git
cd FloodGuard
```

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 📁 Project Structure

```text
FloodGuard/
├── app.py
├── risk_engine.py
├── requirements.txt
├── README.md
└── .gitignore
```

## ⚠️ Limitations

FloodGuard is an educational prototype for flood-risk awareness. Its risk classifications are illustrative and are not official warnings or validated flood predictions. Live river-gauge readings and official emergency-alert integrations are not currently connected. Always follow local authorities and official emergency services during flood events.

## 🔮 Future Improvements

- Integrate verified river-level and rainfall observations.
- Add official flood alerts and warning sources.
- Improve risk estimation using validated data and models.
- Add more detailed location-based visualizations.
- Deploy the dashboard for public demonstration.

## 👩‍💻 Author

**Sneha Kumari**

GitHub: [@snehakumari1984](https://github.com/snehakumari1984)

---

*Built as a learning project exploring Python, data visualization, weather APIs, and flood-risk awareness.*

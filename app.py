
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="FloodGuard | Risk Intelligence",
    page_icon="🌊",
    layout="wide"
)

# ==================================================
# CUSTOM DESIGN
# ==================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #071426, #102b46);
    color: #f1f5f9;
}
h1, h2, h3 {
    color: #e0f2fe;
}
div[data-testid="stMetric"] {
    background: #142e49;
    border: 1px solid #31516d;
    padding: 16px;
    border-radius: 14px;
}
div[data-testid="stMetricLabel"] {
    color: #cbd5e1;
}
div[data-testid="stMetricValue"] {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# CONSTANTS
# ==================================================
RISK_COLORS = {
    "LOW": "#22c55e",
    "MODERATE": "#f59e0b",
    "HIGH": "#ef4444"
}

# ==================================================
# API FUNCTIONS
# ==================================================
@st.cache_data(ttl=600)
def get_city(city_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    response = requests.get(
        url,
        params={
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        },
        timeout=15
    )
    response.raise_for_status()

    results = response.json().get("results", [])
    return results[0] if results else None


@st.cache_data(ttl=600)
def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m"
        ),
        "hourly": (
            "precipitation,"
            "precipitation_probability"
        ),
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "precipitation_probability_max"
        ),
        "forecast_days": 7,
        "timezone": "auto"
    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )
    response.raise_for_status()
    return response.json()


# ==================================================
# WEATHER-BASED DEMONSTRATION ESTIMATE
# ==================================================
def assess_weather_risk(daily):
    """
    Heuristic weather-risk estimate based on forecast rainfall
    and precipitation probability for the next 3 forecast days.

    This is NOT an official flood prediction.
    """

    rainfall_values = daily.get("precipitation_sum", [])
    probability_values = daily.get(
        "precipitation_probability_max", []
    )

    rainfall_values = [
        float(x) for x in rainfall_values[:3]
        if x is not None
    ]

    probability_values = [
        float(x) for x in probability_values[:3]
        if x is not None
    ]

    if not rainfall_values:
        return None

    # Highest daily forecast rainfall in the next 3 days
    max_rain = max(rainfall_values)

    # Highest daily probability of precipitation
    max_probability = (
        max(probability_values)
        if probability_values
        else None
    )

    score = 0
    factors = []

    if max_rain >= 100:
        score += 3
        factors.append(
            "At least 100 mm forecast for one of the next 3 days"
        )
    elif max_rain >= 50:
        score += 2
        factors.append(
            "At least 50 mm forecast for one of the next 3 days"
        )
    elif max_rain >= 25:
        score += 1
        factors.append(
            "At least 25 mm forecast for one of the next 3 days"
        )

    if (
        max_probability is not None
        and max_probability >= 70
        and max_rain >= 25
    ):
        score += 1
        factors.append(
            "High forecast precipitation probability alongside rainfall"
        )

    if score >= 3:
        category = "HIGH"
    elif score >= 1:
        category = "MODERATE"
    else:
        category = "LOW"

    return {
        "category": category,
        "score": score,
        "max_rain": max_rain,
        "max_probability": max_probability,
        "factors": factors
    }


# ==================================================
# OPTIONAL MANUAL DEMO ESTIMATE
# ==================================================
def assess_manual_risk(rainfall, recent_rainfall, river_level):
    score = 0
    factors = []

    if rainfall >= 100:
        score += 3
        factors.append("Very high manual rainfall input")
    elif rainfall >= 50:
        score += 2
        factors.append("High manual rainfall input")
    elif rainfall >= 25:
        score += 1
        factors.append("Moderate manual rainfall input")

    if recent_rainfall >= 150:
        score += 2
        factors.append("Very high manual recent-rainfall input")
    elif recent_rainfall >= 75:
        score += 1
        factors.append("High manual recent-rainfall input")

    if river_level >= 7:
        score += 3
        factors.append("Very high illustrative river level")
    elif river_level >= 4:
        score += 2
        factors.append("Elevated illustrative river level")

    if score >= 5:
        category = "HIGH"
    elif score >= 2:
        category = "MODERATE"
    else:
        category = "LOW"

    return {
        "category": category,
        "score": score,
        "factors": factors
    }


# ==================================================
# HEADER
# ==================================================
st.title("🌊 FloodGuard")
st.subheader("Flood Risk Intelligence Dashboard")

st.caption(
    "Weather-aware demonstration estimate | "
    "Forecast data by Open-Meteo"
)

st.warning(
    "This student project uses simple rainfall thresholds. "
    "It is not an official flood warning, a validated flood model, "
    "or a guarantee that a location is safe."
)

# ==================================================
# SIDEBAR: CITY SEARCH
# ==================================================
st.sidebar.title("📍 Location")

with st.sidebar.form("city_search_form"):
    city_input = st.text_input(
        "Search a city",
        value=st.session_state.get(
            "selected_city", "Guwahati"
        )
    )
    search_clicked = st.form_submit_button(
        "🔎 Search City",
        use_container_width=True
    )

if "selected_city" not in st.session_state:
    st.session_state.selected_city = "Guwahati"

if search_clicked and city_input.strip():
    st.session_state.selected_city = city_input.strip()

st.sidebar.markdown("### Quick locations")

preset_cities = [
    "Guwahati",
    "Jaipur",
    "Delhi",
    "Mumbai",
    "Chennai",
    "Kolkata"
]

for city in preset_cities:
    if st.sidebar.button(
        city,
        key=f"preset_{city}",
        use_container_width=True
    ):
        st.session_state.selected_city = city
        st.rerun()

# ==================================================
# SIDEBAR: RISK MODE
# ==================================================
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Risk calculation")

risk_mode = st.sidebar.radio(
    "Choose risk mode",
    [
        "Weather-based estimate",
        "Manual demo override"
    ],
    index=0,
    help=(
        "Weather mode uses forecast data. Manual mode uses "
        "your test values instead."
    )
)

# ==================================================
# OPTIONAL MANUAL CONTROLS
# ==================================================
if risk_mode == "Manual demo override":
    st.sidebar.markdown("---")
    st.sidebar.warning("MANUAL DEMO MODE")

    rainfall_input = st.sidebar.slider(
        "Rainfall input (mm)",
        min_value=0,
        max_value=200,
        value=20,
        step=1
    )

    recent_rainfall_input = st.sidebar.slider(
        "Recent rainfall input (mm)",
        min_value=0,
        max_value=250,
        value=20,
        step=1
    )

    river_level_input = st.sidebar.slider(
        "Illustrative river level (m)",
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.5
    )

# ==================================================
# FETCH SELECTED CITY AND FORECAST
# ==================================================
city_name = st.session_state.selected_city

try:
    with st.spinner(f"Loading {city_name} weather..."):
        city_data = get_city(city_name)

        if not city_data:
            st.error(
                f"City '{city_name}' was not found. "
                "Try another city name."
            )
            st.stop()

        latitude = city_data["latitude"]
        longitude = city_data["longitude"]

        weather = get_weather(latitude, longitude)

except requests.RequestException:
    st.error(
        "Weather service could not be reached. "
        "Check your internet connection and try again."
    )
    st.stop()

except (ValueError, KeyError, TypeError):
    st.error("Could not process the location or weather data.")
    st.stop()

official_city_name = city_data["name"]
country = city_data.get("country", "")
region = city_data.get("admin1", "")

current = weather.get("current", {})
daily = weather.get("daily", {})
hourly = weather.get("hourly", {})

# ==================================================
# CALCULATE BOTH ESTIMATES
# ==================================================
weather_result = assess_weather_risk(daily)

if risk_mode == "Manual demo override":
    result = assess_manual_risk(
        rainfall_input,
        recent_rainfall_input,
        river_level_input
    )
    result_source = "MANUAL DEMO"
else:
    result = weather_result
    result_source = "WEATHER-BASED ESTIMATE"

# ==================================================
# CITY INFORMATION
# ==================================================
place_text = ", ".join(
    x for x in [official_city_name, region, country] if x
)

st.markdown(f"## 📌 {place_text}")
st.caption(
    f"Coordinates: {latitude:.4f}, {longitude:.4f}"
)

# ==================================================
# CURRENT WEATHER METRICS
# ==================================================
m1, m2, m3, m4 = st.columns(4)

with m1:
    temperature = current.get("temperature_2m")
    st.metric(
        "🌡️ Temperature",
        f"{temperature} °C"
        if temperature is not None else "N/A"
    )

with m2:
    precipitation = current.get("precipitation")
    st.metric(
        "🌧️ Current precipitation",
        f"{precipitation} mm"
        if precipitation is not None else "N/A"
    )

with m3:
    humidity = current.get("relative_humidity_2m")
    st.metric(
        "💧 Humidity",
        f"{humidity}%"
        if humidity is not None else "N/A"
    )

with m4:
    wind = current.get("wind_speed_10m")
    st.metric(
        "💨 Wind speed",
        f"{wind} km/h"
        if wind is not None else "N/A"
    )

# ==================================================
# RISK SUMMARY
# ==================================================
st.markdown("---")
st.markdown("## ⚠️ Risk estimate")

if result is None:
    st.error(
        "Rainfall forecast data is unavailable. "
        "A weather-based estimate cannot be calculated."
    )

else:
    category = result["category"]
    color = RISK_COLORS[category]

    st.markdown(
        f"""
        <div style="
            background:{color};
            padding:22px;
            border-radius:15px;
            color:white;
            margin-bottom:12px;">
            <h2 style="color:white;margin:0;">
                {category} RISK — {result_source}
            </h2>
            <p style="font-size:16px;margin-top:8px;">
                {'Based on the selected city forecast'
                if result_source == 'WEATHER-BASED ESTIMATE'
                else 'Based only on manual demo inputs'}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if result_source == "WEATHER-BASED ESTIMATE":
        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Highest daily rainfall forecast",
            f"{result['max_rain']:.1f} mm"
        )

        probability = result["max_probability"]
        c2.metric(
            "Highest rain probability",
            f"{probability:.0f}%"
            if probability is not None else "N/A"
        )

        c3.metric(
            "Rule score",
            f"{result['score']}/4"
        )

        st.caption(
            "Uses the highest daily rainfall forecast and highest "
            "daily precipitation probability across the next 3 days. "
            "This is a simple heuristic, not a flood forecast."
        )

    else:
        c1, c2 = st.columns(2)

        c1.metric("Manual demo score", f"{result['score']}/8")
        c2.metric("Selected mode", "Manual override")

        st.write(f"Rainfall input: {rainfall_input} mm")
        st.write(
            f"Recent rainfall input: {recent_rainfall_input} mm"
        )
        st.write(
            f"Illustrative river level: {river_level_input:.1f} m"
        )

    if result["factors"]:
        st.markdown("### Why this category?")
        for factor in result["factors"]:
            st.write(f"• {factor}")
    else:
        st.write(
            "No rainfall thresholds in this simple model were reached."
        )

# ==================================================
# TABS
# ==================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "📅 7-Day Forecast",
    "🗺️ Location Map",
    "🛟 Safety Center"
])

# ==================================================
# TAB 1: OVERVIEW
# ==================================================
with tab1:
    left, right = st.columns(2)

    with left:
        st.markdown("### 🌧️ Daily rainfall forecast")

        if daily.get("time") and daily.get("precipitation_sum"):
            rain_df = pd.DataFrame({
                "Date": daily["time"],
                "Rainfall (mm)": daily["precipitation_sum"]
            })

            fig = px.bar(
                rain_df,
                x="Date",
                y="Rainfall (mm)",
                title="Forecast rainfall by day"
            )

            fig.update_layout(
                paper_bgcolor="#102b46",
                plot_bgcolor="#102b46",
                font_color="white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        else:
            st.info("Daily rainfall data is unavailable.")

    with right:
        st.markdown("### 📈 Hourly precipitation probability")

        times = hourly.get("time", [])
        probabilities = hourly.get(
            "precipitation_probability", []
        )

        if times and probabilities:
            count = min(24, len(times), len(probabilities))

            hourly_df = pd.DataFrame({
                "Time": times[:count],
                "Rain probability (%)": probabilities[:count]
            })

            fig = px.line(
                hourly_df,
                x="Time",
                y="Rain probability (%)",
                markers=True,
                title="Next 24 forecast hours"
            )

            fig.update_layout(
                paper_bgcolor="#102b46",
                plot_bgcolor="#102b46",
                font_color="white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        else:
            st.info("Hourly probability data is unavailable.")

    st.info(
        "The charts show forecast data. The risk category is a "
        "separate threshold-based estimate and does not establish "
        "whether flooding will occur."
    )

# ==================================================
# TAB 2: 7-DAY FORECAST
# ==================================================
with tab2:
    st.markdown("### 📅 Weather forecast")

    if daily.get("time"):
        forecast_df = pd.DataFrame({
            "Date": daily.get("time", []),
            "Min temperature (°C)": daily.get(
                "temperature_2m_min", []
            ),
            "Max temperature (°C)": daily.get(
                "temperature_2m_max", []
            ),
            "Rainfall forecast (mm)": daily.get(
                "precipitation_sum", []
            ),
            "Rain probability (%)": daily.get(
                "precipitation_probability_max", []
            )
        })

        st.dataframe(
            forecast_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("The 7-day forecast is unavailable.")

    st.caption(
        "Forecast values may change. They are not observed rainfall "
        "measurements or official flood alerts."
    )

# ==================================================
# TAB 3: MAP
# ==================================================
with tab3:
    st.markdown("### 🗺️ Selected city")

    map_col, summary_col = st.columns([2, 1])

    with map_col:
        flood_map = folium.Map(
            location=[latitude, longitude],
            zoom_start=10,
            tiles="OpenStreetMap"
        )

        marker_color = (
            "red" if result and result["category"] == "HIGH"
            else "orange" if result and result["category"] == "MODERATE"
            else "green"
        )

        folium.Marker(
            [latitude, longitude],
            tooltip=official_city_name,
            popup=f"Selected city: {official_city_name}",
            icon=folium.Icon(
                color=marker_color,
                icon="info-sign"
            )
        ).add_to(flood_map)

        st_folium(
            flood_map,
            width=None,
            height=450,
            key="floodguard_city_map"
        )

    with summary_col:
        st.markdown("### Location summary")
        st.write(f"**City:** {official_city_name}")
        st.write(f"**Mode:** {result_source}")

        if result:
            st.markdown(
                f"<h2 style='color:{RISK_COLORS[result['category']]};'>"
                f"{result['category']}</h2>",
                unsafe_allow_html=True
            )

        st.warning(
            "The marker shows the city coordinates only. It does "
            "not represent a measured flood zone or flood boundary."
        )

# ==================================================
# TAB 4: SAFETY CENTER
# ==================================================
with tab4:
    st.markdown("### 🛟 Flood safety guidance")

    if result and result["category"] == "HIGH":
        st.error(
            "The selected model has a high estimate. Check official "
            "weather and local administration alerts."
        )

        tips = [
            "Follow official weather alerts and local authority instructions.",
            "Avoid flooded roads, underpasses and fast-flowing water.",
            "Move to higher ground if authorities advise evacuation.",
            "Keep drinking water, medicines, a torch and a charged phone ready.",
            "Never walk or drive through floodwater."
        ]

    elif result and result["category"] == "MODERATE":
        st.warning(
            "The model indicates elevated forecast rainfall conditions. "
            "Stay informed and prepared."
        )

        tips = [
            "Monitor official weather and district administration updates.",
            "Keep your phone charged and prepare essential supplies.",
            "Identify safer routes and nearby higher ground.",
            "Avoid riverbanks during heavy rain."
        ]

    else:
        st.success(
            "The simple model has not reached its higher thresholds. "
            "This does not guarantee safety from flooding."
        )

        tips = [
            "Continue checking official weather updates.",
            "Know your local emergency contacts.",
            "Avoid entering floodwater even if it looks shallow.",
            "Take local warnings seriously regardless of this app's score."
        ]

    for tip in tips:
        st.markdown(f"- {tip}")

    st.markdown("---")
    st.markdown("### 🚨 Emergency checklist")

    st.checkbox("Phone charged and power bank ready")
    st.checkbox("Drinking water and essential medicines packed")
    st.checkbox("Important documents stored safely")
    st.checkbox("Family members know the meeting point")
    st.checkbox("Official local alerts checked")

    st.info(
        "FloodGuard is not an emergency alert service. In an emergency, "
        "follow official local authorities and emergency services."
    )

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.caption(
    "FloodGuard | Student demonstration project | "
    "Weather data: Open-Meteo | Not an official flood warning"
)

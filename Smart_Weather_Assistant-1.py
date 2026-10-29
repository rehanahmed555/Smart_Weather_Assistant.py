import os
import io
import requests
import streamlit as st
from datetime import datetime

try:
    import speech_recognition as sr
except ImportError:
    sr = None

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Smart Weather Assistant",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# DESIGN
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
.stApp {
    background:
        radial-gradient(circle at 5% 0%, #ffe8bd 0, transparent 28%),
        radial-gradient(circle at 95% 5%, #c9f0df 0, transparent 28%),
        #f4f7f3;
    color: #203b38;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #173e37, #26705b);
}
[data-testid="stSidebar"] * { color: #f5fff8 !important; }
[data-testid="stSidebar"] input { color: #203b38 !important; }
h1, h2, h3 { color: #173e37 !important; }
.hero {
    padding: 34px; border-radius: 28px; margin-bottom: 24px;
    background: linear-gradient(115deg, #fff0d0, #fbe5c6 45%, #d6f2e5);
    border: 1px solid #e7e9d9; box-shadow: 0 14px 35px #214c3d12;
}
.hero h1 { font-size: clamp(2rem, 4vw, 3.2rem); margin: 0; color: #173e37 !important; }
.hero p { color: #4f6b60; font-size: 1.05rem; }
.tag {
    display: inline-block; background: white; color: #28745b; padding: 7px 12px;
    border-radius: 999px; font-size: .76rem; font-weight: 800; margin-bottom: 13px;
}
.panel {
    background: white; border: 1px solid #e3ebe5; border-radius: 22px;
    padding: 22px; box-shadow: 0 8px 24px #214c3d0c; margin-bottom: 14px;
}
.panel h3 { margin-top: 0; }
.panel p { line-height: 1.65; color: #405851; }
.winter { background: linear-gradient(135deg, #e7f4ff, #fbfdff); border-color: #cfe5f7; }
.winter h3 { color: #27628c !important; }
.summer { background: linear-gradient(135deg, #fff0d2, #fffaf2); border-color: #f6ddb0; }
.summer h3 { color: #a85b16 !important; }
.rain { background: linear-gradient(135deg, #e0f6e9, #fbfffc); border-color: #c7e9d5; }
.rain h3 { color: #1e7052 !important; }
.food { background: linear-gradient(135deg, #fff0e8, #fffaf7); border-color: #f4d8ca; }
.food h3 { color: #a34e30 !important; }
.health { background: linear-gradient(135deg, #f0edff, #fcfbff); border-color: #ded6ff; }
.health h3 { color: #5f4a9b !important; }
.tip {
    background: #e4f5eb; border-left: 5px solid #32966e; border-radius: 15px;
    padding: 15px 17px; margin: 14px 0; color: #245541;
}
.warn {
    background: #fff0d9; border-left: 5px solid #e99a31; border-radius: 15px;
    padding: 15px 17px; margin: 14px 0; color: #704719;
}
[data-testid="stMetric"] {
    background: white; border: 1px solid #e3ebe5; padding: 16px;
    border-radius: 18px; box-shadow: 0 7px 18px #214c3d0b;
}
[data-testid="stMetricLabel"] { color: #688078 !important; }
[data-testid="stMetricValue"] { color: #173e37 !important; }
.stButton > button {
    border: 0; border-radius: 13px; min-height: 46px; font-weight: 800;
    background: linear-gradient(100deg, #287b62, #1e6657); color: white;
}
.stButton > button:hover { background: #174d43; color: white; }
hr { border-color: #e0e9e1; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# API CONFIGURATION
# ---------------------------------------------------------
API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("""
<div class="hero">
    <span class="tag">YOUR DAILY WEATHER + WELLNESS COMPANION</span>
    <h1>Smart Weather Assistant 🌤️</h1>
    <p>Know the weather. Discover seasonal food.
    Build healthier daily habits — all in one place.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.markdown("## 🌦️ Smart Weather Assistant")
st.sidebar.caption("Your personal seasonal guide")

# Voice city entry: record a short city name and convert it to text.
st.sidebar.markdown("### 🎙️ Voice City Entry")
st.sidebar.caption("Record your city name, then tap Transcribe.")
voice_audio = st.sidebar.audio_input("Speak your city name", key="voice_city_audio")
voice_language = st.sidebar.selectbox(
    "Voice language",
    ["English (US)", "Urdu (Pakistan)"],
    key="voice_city_language",
)
if st.sidebar.button("🎤 Transcribe City", use_container_width=True):
    if voice_audio is None:
        st.sidebar.warning("Please record your city name first.")
    elif sr is None:
        st.sidebar.error(
            "Voice transcription package is missing. Install it with: "
            "pip install SpeechRecognition"
        )
    else:
        try:
            with sr.AudioFile(io.BytesIO(voice_audio.getvalue())) as source:
                recorded_audio = sr.Recognizer().record(source)
            language_code = "en-US" if voice_language == "English (US)" else "ur-PK"
            recognized_city = sr.Recognizer().recognize_google(
                recorded_audio, language=language_code
            ).strip()
            if recognized_city:
                st.session_state["city_input"] = recognized_city
                st.sidebar.success(f"City recognized: {recognized_city}")
                st.rerun()
            else:
                st.sidebar.warning("No city name detected. Please try again.")
        except sr.UnknownValueError:
            st.sidebar.warning("Could not understand the audio. Speak clearly and try again.")
        except sr.RequestError:
            st.sidebar.error("Speech recognition service is unavailable. Check your internet.")
        except Exception as exc:
            st.sidebar.error(f"Could not process the recording: {exc}")

city = st.sidebar.text_input("📍 Enter your city", "Sukkur", key="city_input").strip()
section = st.sidebar.radio(
    "Explore Sections",
    [
        "🏠 Overview",
        "❄️ Winter Care",
        "☀️ Summer Care",
        "🌧️ Rainy Season",
        "🥗 Healthy Food",
        "💊 Pharmacy Safety",
        "📅 5-Day Forecast",
    ],
)
st.sidebar.markdown("---")
st.sidebar.caption("Weather powered by OpenWeather")

if not API_KEY:
    st.sidebar.warning("Weather API key is not set.")
    st.sidebar.caption(
        "Set OPENWEATHER_API_KEY in the same PowerShell terminal "
        "used to launch this app."
    )

# ---------------------------------------------------------
# API FUNCTIONS
# ---------------------------------------------------------
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

@st.cache_data(ttl=600, show_spinner=False)
def get_weather(city_name: str, api_key: str):
    response = requests.get(
        WEATHER_URL,
        params={"q": city_name, "appid": api_key, "units": "metric"},
        timeout=15,
    )
    try:
        data = response.json()
    except ValueError:
        raise ValueError("OpenWeather returned an unreadable response.")

    if response.status_code == 401:
        raise ValueError(
            "Invalid API key (401). Check that the key was copied correctly "
            "and is active in your OpenWeather account."
        )
    if response.status_code == 404:
        raise ValueError(
            f"City '{city_name}' was not found. Check the spelling, e.g. Sukkur."
        )
    if response.status_code == 429:
        raise ValueError("API request limit reached. Please wait and try again.")
    if response.status_code != 200:
        message = data.get("message", "Weather unavailable") if isinstance(data, dict) else "Weather unavailable"
        raise ValueError(f"OpenWeather error: {message}")

    return data

@st.cache_data(ttl=600, show_spinner=False)
def get_forecast(city_name: str, api_key: str):
    response = requests.get(
        FORECAST_URL,
        params={"q": city_name, "appid": api_key, "units": "metric"},
        timeout=15,
    )
    try:
        data = response.json()
    except ValueError:
        raise ValueError("OpenWeather returned an unreadable forecast response.")

    if response.status_code == 401:
        raise ValueError(
            "Invalid API key (401). Check that the key is correct and active."
        )
    if response.status_code == 404:
        raise ValueError(f"City '{city_name}' was not found.")
    if response.status_code == 429:
        raise ValueError("API request limit reached. Please wait and try again.")
    if response.status_code != 200:
        message = data.get("message", "Forecast unavailable") if isinstance(data, dict) else "Forecast unavailable"
        raise ValueError(f"OpenWeather error: {message}")

    return data

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "weather_data" not in st.session_state:
    st.session_state.weather_data = None
if "weather_city" not in st.session_state:
    st.session_state.weather_city = ""
if "last_weather_error" not in st.session_state:
    st.session_state.last_weather_error = ""

# ---------------------------------------------------------
# WEATHER SEARCH / REFRESH
# ---------------------------------------------------------
left, right = st.columns([3, 1])
with left:
    st.markdown("### 🌍 Check your local weather")
    st.caption("Enter a city in the sidebar, then refresh to get current conditions.")
with right:
    refresh = st.button("↻ Refresh Weather", use_container_width=True)

if refresh:
    if not API_KEY:
        st.session_state.last_weather_error = (
            "API key missing. Set OPENWEATHER_API_KEY in PowerShell, then restart the app."
        )
        st.session_state.weather_data = None
    elif not city:
        st.session_state.last_weather_error = "Please enter a city name."
        st.session_state.weather_data = None
    else:
        try:
            with st.spinner("Fetching live weather..."):
                st.session_state.weather_data = get_weather(city, API_KEY)
                st.session_state.weather_city = city
                st.session_state.last_weather_error = ""
        except ValueError as exc:
            st.session_state.weather_data = None
            st.session_state.last_weather_error = str(exc)
        except requests.Timeout:
            st.session_state.last_weather_error = "Weather request timed out. Please try again."
        except requests.ConnectionError:
            st.session_state.last_weather_error = "Internet connection problem. Check your connection."
        except requests.RequestException as exc:
            st.session_state.last_weather_error = f"Request failed: {exc}"

if st.session_state.last_weather_error:
    st.error(f"Weather error: {st.session_state.last_weather_error}")

weather = st.session_state.weather_data

# If the user changes the city after loading weather, don't show old city data as current.
if weather and st.session_state.weather_city.casefold() != city.casefold():
    weather = None

if weather:
    temp = weather["main"]["temp"]
    humidity = weather["main"]["humidity"]
    wind = weather.get("wind", {}).get("speed", 0)
    condition = weather["weather"][0]["description"].lower()
    city_name = weather.get("name", st.session_state.weather_city)
else:
    temp = humidity = wind = None
    condition = ""
    city_name = city or "your city"

# ---------------------------------------------------------
# OVERVIEW
# ---------------------------------------------------------
if section == "🏠 Overview":
    if weather:
        st.markdown(f"### 📍 {city_name} · {datetime.now():%d %B %Y}")
        a, b, c, d = st.columns(4)
        a.metric("🌡️ Temperature", f"{temp:.1f} °C")
        b.metric("💧 Humidity", f"{humidity}%")
        c.metric("💨 Wind", f"{wind:.1f} m/s")
        d.metric("🌤️ Condition", condition.title())

        if temp >= 35:
            st.markdown(
                '<div class="warn"><b>🥵 Heat Alert</b><br>'
                'Stay in shade, drink safe water regularly and reduce '
                'strenuous activity during peak heat.</div>',
                unsafe_allow_html=True,
            )
        elif temp <= 10:
            st.markdown(
                '<div class="tip"><b>🧣 Cold Weather</b><br>'
                'Wear warm layers and keep yourself dry.</div>',
                unsafe_allow_html=True,
            )

        if any(word in condition for word in ["rain", "drizzle", "thunder"]):
            st.markdown(
                '<div class="tip"><b>☔ Rain Alert</b><br>'
                'Carry an umbrella and avoid floodwater.</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown("""
        <div class="panel">
            <h3>✨ Welcome to your wellness dashboard</h3>
            <p>Set your OpenWeather API key in PowerShell, enter a city,
            then press Refresh Weather to load live conditions.</p>
            <p>You can explore all seasonal care sections using the menu on the left.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Explore Your Care Guide")
    a, b, c = st.columns(3)
    with a:
        st.markdown("""
        <div class="panel winter">
            <h3>❄️ Winter Care</h3>
            <p>Warm clothing, comforting meals and cold-weather habits.</p>
        </div>
        """, unsafe_allow_html=True)
    with b:
        st.markdown("""
        <div class="panel summer">
            <h3>☀️ Summer Care</h3>
            <p>Hydration, heat awareness and refreshing food ideas.</p>
        </div>
        """, unsafe_allow_html=True)
    with c:
        st.markdown("""
        <div class="panel rain">
            <h3>🌧️ Rainy Season</h3>
            <p>Travel safety, dry clothing and clean-water reminders.</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# WINTER CARE
# ---------------------------------------------------------
elif section == "❄️ Winter Care":
    st.markdown("## ❄️ Winter Care Center")
    st.caption("Cozy ideas and simple habits for colder days.")
    a, b = st.columns(2)
    with a:
        st.markdown("""
        <div class="panel winter">
            <h3>🧣 Stay Warm</h3>
            <p>🧥 Wear comfortable layers and a warm outer layer.</p>
            <p>🧦 Keep your hands and feet warm.</p>
            <p>🏠 Keep indoor spaces comfortably warm.</p>
            <p>👕 Change out of wet clothes promptly.</p>
        </div>
        """, unsafe_allow_html=True)
    with b:
        st.markdown("""
        <div class="panel winter">
            <h3>🍲 Winter Food Ideas</h3>
            <p>🥣 Vegetable, lentil or chicken soup.</p>
            <p>🫘 Daal, beans, eggs and other protein foods.</p>
            <p>🍊 Seasonal fruits such as oranges and guava.</p>
            <p>🥕 Cooked vegetables and balanced home meals.</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown(
        '<div class="tip"><b>Health fact:</b> Common colds are caused by '
        'respiratory viruses, not cold weather itself.</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# SUMMER CARE
# ---------------------------------------------------------
elif section == "☀️ Summer Care":
    st.markdown("## ☀️ Summer Care Center")
    st.caption("Hydration, heat awareness and fresh meals.")
    a, b = st.columns(2)
    with a:
        st.markdown("""
        <div class="panel summer">
            <h3>💧 Beat the Heat</h3>
            <p>🚰 Drink safe water regularly.</p>
            <p>🧢 Use shade, a hat and breathable clothing.</p>
            <p>🕒 Reduce outdoor exercise during peak heat.</p>
            <p>👥 Check on children and older adults during heatwaves.</p>
        </div>
        """, unsafe_allow_html=True)
    with b:
        st.markdown("""
        <div class="panel summer">
            <h3>🍉 Summer Food</h3>
            <p>🍉 Watermelon, melon and other fresh fruits.</p>
            <p>🥒 Cucumber, tomatoes and other vegetables.</p>
            <p>🥚 Balanced meals with protein and grains.</p>
            <p>🧊 Keep perishable foods stored safely.</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown(
        '<div class="warn"><b>⚠️ Heat Warning:</b> Confusion, fainting or '
        'very hot skin can signal an emergency. Seek urgent medical help.</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# RAINY SEASON
# ---------------------------------------------------------
elif section == "🌧️ Rainy Season":
    st.markdown("## 🌧️ Rainy Season Safety")
    st.caption("Practical reminders for wet days.")
    a, b = st.columns(2)
    with a:
        st.markdown("""
        <div class="panel rain">
            <h3>☔ Before Going Out</h3>
            <p>🌂 Carry an umbrella or raincoat.</p>
            <p>👟 Wear shoes with good grip.</p>
            <p>📢 Check weather and travel alerts.</p>
            <p>🚫 Never walk or drive through floodwater.</p>
        </div>
        """, unsafe_allow_html=True)
    with b:
        st.markdown("""
        <div class="panel rain">
            <h3>🧼 Stay Clean and Dry</h3>
            <p>👕 Change into dry clothes when possible.</p>
            <p>🧽 Wash hands regularly.</p>
            <p>🚰 Drink safe, clean water.</p>
            <p>🦟 Avoid standing water where mosquitoes breed.</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown(
        '<div class="tip"><b>Travel Safety:</b> If floodwater is moving or '
        'its depth is unclear, do not enter it.</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# HEALTHY FOOD
# ---------------------------------------------------------
elif section == "🥗 Healthy Food":
    st.markdown("## 🥗 Everyday Healthy Food Guide")
    st.caption("Simple meal ideas using familiar everyday foods.")
    a, b, c = st.columns(3)
    with a:
        st.markdown("""
        <div class="panel food">
            <h3>🥬 Fruits & Vegetables</h3>
            <p>Guava, oranges, leafy greens, carrots, cucumber and other seasonal produce.</p>
        </div>
        """, unsafe_allow_html=True)
    with b:
        st.markdown("""
        <div class="panel winter">
            <h3>🫘 Protein Foods</h3>
            <p>Daal, beans, chickpeas, eggs, fish, chicken or other suitable protein sources.</p>
        </div>
        """, unsafe_allow_html=True)
    with c:
        st.markdown("""
        <div class="panel summer">
            <h3>🌾 Grains & Energy</h3>
            <p>Roti, rice, oats or other grains paired with vegetables and protein.</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("""
    <div class="panel">
        <h3>🍽️ Build a Balanced Plate</h3>
        <p>🥦 Include vegetables and fruit across your meals.</p>
        <p>🫘 Choose a protein source such as daal, beans or eggs.</p>
        <p>🌾 Include grains or other starchy foods.</p>
        <p>💧 Drink safe water and store food safely.</p>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Food needs differ by age, activity, allergies and health conditions.")

# ---------------------------------------------------------
# PHARMACY SAFETY
# ---------------------------------------------------------
elif section == "💊 Pharmacy Safety":
    st.markdown("## 💊 Pharmacy & Basic Health Guide")
    st.caption("General education only — this app does not diagnose or prescribe.")
    st.markdown("""
    <div class="panel health">
        <h3>🤧 Mild Cold-Like Symptoms</h3>
        <p>🛌 Rest and drink fluids.</p>
        <p>🍵 A warm drink may soothe a sore throat.</p>
        <p>📋 Read medicine labels carefully.</p>
        <p>🧑‍⚕️ Ask a qualified pharmacist or clinician before taking medicines,
        especially for children or people with ongoing health conditions.</p>
        <p>💡 Antibiotics do not treat ordinary viral colds.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="warn">
        <b>⚠️ Medicine Safety</b><br>
        Do not use someone else's prescription or exceed the labelled dose.
        Check active ingredients to avoid accidentally taking the same ingredient twice.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="panel">
        <h3>🚑 When to Get Urgent Help</h3>
        <p>• Trouble breathing or chest pain.</p>
        <p>• Confusion, fainting or severe dehydration.</p>
        <p>• Severe allergic reaction or rapidly worsening symptoms.</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5-DAY FORECAST
# ---------------------------------------------------------
elif section == "📅 5-Day Forecast":
    st.markdown("## 📅 5-Day Forecast")
    forecast_city = city or st.session_state.weather_city or "Sukkur"
    st.caption(f"Upcoming conditions for {forecast_city}. Forecasts can change.")

    if not API_KEY:
        st.warning("Set OPENWEATHER_API_KEY in PowerShell, then restart this app.")
    else:
        try:
            with st.spinner("Loading forecast..."):
                forecast = get_forecast(forecast_city, API_KEY)

            # OpenWeather forecast returns 3-hour intervals. Group by local date
            # supplied by the API and calculate daily min/max/average temperatures.
            daily = {}
            for item in forecast.get("list", []):
                day = item["dt_txt"].split(" ")[0]
                daily.setdefault(day, []).append(item)

            if not daily:
                st.info("No forecast entries were returned.")
            else:
                days = list(daily.items())[:5]
                columns = st.columns(len(days))
                for col, (day, entries) in zip(columns, days):
                    temps = [item["main"]["temp"] for item in entries]
                    middle = entries[len(entries) // 2]
                    description = middle["weather"][0]["description"].title()
                    with col:
                        st.markdown(
                            f'<div class="panel rain">'
                            f'<h3>📅 {day}</h3>'
                            f'<h3 style="font-size:1.6rem">{sum(temps) / len(temps):.1f}°C</h3>'
                            f'<p>High: {max(temps):.1f}°C</p>'
                            f'<p>Low: {min(temps):.1f}°C</p>'
                            f'<p>{description}</p></div>',
                            unsafe_allow_html=True,
                        )
        except ValueError as exc:
            st.warning(f"Forecast error: {exc}")
        except requests.Timeout:
            st.warning("Forecast request timed out. Please try again.")
        except requests.ConnectionError:
            st.warning("Internet connection problem. Check your connection.")
        except requests.RequestException as exc:
            st.warning(f"Forecast request failed: {exc}")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")
st.caption(
    "Smart Weather Assistant • Weather is an estimate. "
    "Health tips are general education, not medical diagnosis."
)

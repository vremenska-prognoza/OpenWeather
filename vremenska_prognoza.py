import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from datetime import datetime

# Učitavanje .env fajla
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Provjera da li je API ključ učitan
if not API_KEY:
    st.error("❌ API ključ nije postavljen! Molimo postavite API_KEY u .env datoteku.")
    st.stop()

# Funkcija za dobijanje trenutnog vremena koristeći lat, lon ili ime grada
def get_weather(lat=None, lon=None, city=None, unit="metric"):
    if city:
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit}'
    elif lat and lon:
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units={unit}'
    else:
        return None
        
    try:
        response = requests.get(url)
        response.raise_for_status()  # Proverava da li je status code uspešan (200)
        data = response.json()
        return {
            'Grad': data['name'],
            'Temperatura (°C)': data['main']['temp'],
            'Vlažnost (%)': data['main']['humidity'],
            'Pritisak (hPa)': data['main']['pressure'],
            'Vetar (m/s)': data['wind']['speed'],
            'Opis': data['weather'][0]['description'].capitalize()
        }
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Greška prilikom povezivanja sa OpenWeather API: {str(e)}")
        return None

# Funkcija za dobijanje prognoze za nekoliko dana
def get_forecast(lat=None, lon=None, city=None, unit="metric"):
    if city:
        url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={unit}'
    elif lat and lon:
        url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units={unit}'
    else:
        return None

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        forecast_data = []
        for entry in data['list']:
            forecast_data.append({
                'Sat': entry['dt_txt'],
                'Temperatura (°C)': entry['main']['temp'],
                'Vlažnost (%)': entry['main']['humidity'],
                'Padavine (%)': entry.get('rain', {}).get('3h', 0),  # Padavine u poslednja 3h
                'Vetar (m/s)': entry['wind']['speed'],
                'Opis': entry['weather'][0]['description'].capitalize()
            })

        return forecast_data
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Greška prilikom povezivanja sa OpenWeather API: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(page_title="Vremenska aplikacija", layout="wide")
st.title("🌤️ Vremenska prognoza u realnom vremenu")

# Unesi grad ili koordinate lat, lon
gradovi_input = st.text_input("Unesi ime grada (npr. Beograd):", "Beograd")
gradovi_input_koordinate = st.text_input("ILI Unesi geografske koordinate lat, lon (npr. 44.8176, 20.4633):", "")

# Odabir vremenskog perioda
period_option = st.radio(
    "Odaberite vremenski period",
    ('Danas', '3 dana', '5 dana', '7 dana')
)

# Ako korisnik unese koordinate
koordinate = [g.strip() for g in gradovi_input_koordinate.split(',') if g.strip()]
if len(koordinate) == 2:
    lat, lon = float(koordinate[0]), float(koordinate[1])
else:
    lat, lon = None, None

# Dugme za prikaz
if st.button("Prikaži podatke"):
    podaci = []

    # Prikazivanje trenutnog vremena za "Danas"
    if period_option == 'Danas':
        if gradovi_input:
            vreme = get_weather(city=gradovi_input)
        elif lat and lon:
            vreme = get_weather(lat=lat, lon=lon)
        else:
            st.error("❌ Unesite ili ime grada ili koordinate!")
            st.stop()

        if vreme:
            podaci.append(vreme)
        else:
            st.warning(f"❌ Nema podataka za unesene vrednosti.")
    
    # Prikazivanje prognoze za 3, 5 ili 7 dana
    elif period_option in ['3 dana', '5 dana', '7 dana']:
        forecast = get_forecast(city=gradovi_input, lat=lat, lon=lon)
        
        if forecast:
            df_forecast = pd.DataFrame(forecast)
            st.dataframe(df_forecast)

            # Bar grafikon za temperaturu
            fig_temp = px.bar(df_forecast, x='Sat', y='Temperatura (°C)', title="🌡️ Prognoza temperature")
            st.plotly_chart(fig_temp, use_container_width=True)

            # Bar grafikon za vlažnost
            fig_humidity = px.bar(df_forecast, x='Sat', y='Vlažnost (%)', title="💧 Prognoza vlažnosti")
            st.plotly_chart(fig_humidity, use_container_width=True)

            # Bar grafikon za padavine
            fig_rain = px.bar(df_forecast, x='Sat', y='Padavine (%)', title="🌧️ Prognoza padavina")
            st.plotly_chart(fig_rain, use_container_width=True)

            # Bar grafikon za vetar
            fig_wind = px.bar(df_forecast, x='Sat', y='Vetar (m/s)', title="💨 Prognoza vetra")
            st.plotly_chart(fig_wind, use_container_width=True)


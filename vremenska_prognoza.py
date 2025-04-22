import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

# Učitavanje .env fajla
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Provjera da li je API ključ učitan
if not API_KEY:
    st.error("❌ API ključ nije postavljen! Molimo postavite API_KEY u .env datoteku.")
    st.stop()

# Funkcija za dobijanje podataka o vremenu koristeći lat, lon ili ime grada
def get_weather(lat=None, lon=None, city=None):
    if city:
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
    elif lat and lon:
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
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

# Streamlit UI
st.set_page_config(page_title="Vremenska aplikacija", layout="wide")
st.title("🌤️ Vremenska prognoza u realnom vremenu")

# Unesi grad ili koordinate lat, lon
gradovi_input = st.text_input("Unesi ime grada (npr. Beograd):", "Beograd")
gradovi_input_koordinate = st.text_input("ILI Unesi geografske koordinate lat, lon (npr. 44.8176, 20.4633):", "")

# Ako korisnik unese koordinate
koordinate = [g.strip() for g in gradovi_input_koordinate.split(',') if g.strip()]
if len(koordinate) == 2:
    lat, lon = float(koordinate[0]), float(koordinate[1])
else:
    lat, lon = None, None

# Dugme za prikaz
if st.button("Prikaži podatke"):
    podaci = []
    
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

    if podaci:
        df = pd.DataFrame(podaci)

        # Prikaz podataka
        st.dataframe(df)

        # Grafikon temperature
        fig_temp = px.bar(df, x="Grad", y="Temperatura (°C)", color="Temperatura (°C)", title="🌡️ Temperature po gradovima")
        st.plotly_chart(fig_temp, use_container_width=True)

        # Grafikon vlažnosti
        fig_humidity = px.bar(df, x="Grad", y="Vlažnost (%)", color="Vlažnost (%)", title="💧 Vlažnost po gradovima")
        st.plotly_chart(fig_humidity, use_container_width=True)

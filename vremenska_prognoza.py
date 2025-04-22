import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

# Učitavanje .env fajla
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Funkcija za dobijanje podataka o vremenu koristeći lat i lon
def get_weather(lat, lon):
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            'Grad': data['name'],
            'Temperatura (°C)': data['main']['temp'],
            'Vlažnost (%)': data['main']['humidity'],
            'Pritisak (hPa)': data['main']['pressure'],
            'Vetar (m/s)': data['wind']['speed'],
            'Opis': data['weather'][0]['description'].capitalize()
        }
    else:
        return None

# Streamlit UI
st.set_page_config(page_title="Vremenska aplikacija", layout="wide")
st.title("🌤️ Vremenska prognoza u realnom vremenu")

# Unesi geografske koordinate lat, lon
gradovi_input = st.text_input("Unesi geografske koordinate (lat, lon) razdvojene zarezom (npr. 44.8176, 20.4633 za Beograd):", "44.8176, 20.4633")
koordinate = [g.strip() for g in gradovi_input.split(',') if g.strip()]

# Dugme za prikaz
if st.button("Prikaži podatke"):
    podaci = []
    if len(koordinate) == 2:
        lat, lon = float(koordinate[0]), float(koordinate[1])
        vreme = get_weather(lat, lon)
        if vreme:
            podaci.append(vreme)
        else:
            st.warning(f"❌ Nema podataka za koordinate: {lat}, {lon}")

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

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

# Učitavanje .env fajla
load_dotenv()  # Ovdje učitavamo .env fajl

# Sada pokušavamo da dohvatimo API_KEY iz .env fajla
API_KEY = os.getenv("API_KEY")

# Provera da li je API_KEY učitan iz .env fajla
if API_KEY is None:
    st.error("API ključ nije definisan u .env fajlu!")
else:
    st.write(f"API_KEY je učitan: {API_KEY[:5]}...")  # Pokazivanje delimičnog API ključa

# Funkcija za dobijanje podataka o vremenu
def get_weather(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
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

# Unos gradova
gradovi_input = st.text_input("Unesi gradove razdvojene zarezom (npr. Belgrade, Paris, New York):", "Belgrade, Paris, New York")
gradovi = [g.strip() for g in gradovi_input.split(',') if g.strip()]

# Dugme za prikaz
if st.button("Prikaži podatke"):
    podaci = []
    for grad in gradovi:
        vreme = get_weather(grad)
        if vreme:
            podaci.append(vreme)
        else:
            st.warning(f"❌ Nema podataka za: {grad}")

    if podaci:
        df = pd.DataFrame(podaci)

        # Pretraga
        search = st.text_input("🔍 Pretraga po gradu:")
        if search:
            df = df[df["Grad"].str.contains(search, case=False)]

        st.dataframe(df)

        # Grafikon temperature
        fig_temp = px.bar(df, x="Grad", y="Temperatura (°C)", color="Temperatura (°C)", title="🌡️ Temperature po gradovima")
        st.plotly_chart(fig_temp, use_container_width=True)

        # Grafikon vlažnosti
        fig_humidity = px.bar(df, x="Grad", y="Vlažnost (%)", color="Vlažnost (%)", title="💧 Vlažnost po gradovima")
        st.plotly_chart(fig_humidity, use_container_width=True)


import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
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
            'Opis': data['weather'][0]['description'].capitalize(),
            'Sunčevo zračenje (W/m²)': data.get('clouds', {}).get('all', 0),  # Procenat oblaka kao proxy za sunčevo zračenje
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
                'Opis': entry['weather'][0]['description'].capitalize(),
                'Sunčevo zračenje (W/m²)': entry.get('clouds', {}).get('all', 0),  # Procenat oblaka kao proxy za sunčevo zračenje
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
        
        # Prikaz trenutnih podataka
        st.dataframe(df)

        # **Trenutni grafikon - Kombinovani grafikon sa stubcima i linijama**
        fig_current = go.Figure()

        # Temperatura - Linija
        fig_current.add_trace(go.Scatter(
            x=df['Grad'],
            y=df['Temperatura (°C)'],
            mode='lines+markers',
            name="Temperatura",
            line=dict(color='orangered', width=4),
            marker=dict(size=8, color='orangered'),
            text=df['Temperatura (°C)'].apply(lambda x: f'{x}°C'),
            hoverinfo='text'
        ))

        # Padavine - Stubci
        if 'Padavine (%)' in df.columns:
            fig_current.add_trace(go.Bar(
                x=df['Grad'],
                y=df['Padavine (%)'],
                name="Padavine (%)",
                marker=dict(color='deepskyblue'),
                text=df['Padavine (%)'].apply(lambda x: f'{x}%'),
                hoverinfo='text'
            ))

        # Vetar - Linija
        fig_current.add_trace(go.Scatter(
            x=df['Grad'],
            y=df['Vetar (m/s)'],
            mode='lines+markers',
            name="Vetar",
            line=dict(color='green', width=4),
            marker=dict(size=8, color='green'),
            text=df['Vetar (m/s)'].apply(lambda x: f'{x} m/s'),
            hoverinfo='text'
        ))

        # Sunčevo zračenje - Stubci (ili možete koristiti kao liniju, zavisno od vaših potreba)
        fig_current.add_trace(go.Bar(
            x=df['Grad'],
            y=df['Sunčevo zračenje (W/m²)'],
            name="Sunčevo zračenje",
            marker=dict(color='gold'),
            text=df['Sunčevo zračenje (W/m²)'].apply(lambda x: f'{x} W/m²'),
            hoverinfo='text'
        ))

        # Raspored grafikona bez duple osovine
        fig_current.update_layout(
            title="🌡️ Trenutno stanje (Temperatura, Padavine, Vetar, Sunčevo Zračenje)",
            xaxis_title="Grad",
            yaxis_title="Vrednosti",
            plot_bgcolor='white',
            template='plotly_dark',
            barmode='group',
            margin=dict(l=40, r=40, t=40, b=40)
        )

        st.plotly_chart(fig_current, use_container_width=True)

        # Prikazivanje prognoze za nekoliko dana
        forecast = get_forecast(city=gradovi_input, lat=lat, lon=lon)

        if forecast:
            df_forecast = pd.DataFrame(forecast)

            # Prikaz prognoze u tabeli
            st.dataframe(df_forecast)

            # **1. Grafikon za temperaturu**
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(
                x=df_forecast['Sat'],
                y=df_forecast['Temperatura (°C)'],
                mode='lines+markers',
                name="Temperatura",
                line=dict(color='orangered', width=2),
                marker=dict(size=6, color='orangered'),
                text=df_forecast['Temperatura (°C)'].apply(lambda x: f'{x}°C'),
                hoverinfo='text'
            ))
            fig_temp.update_layout(
                title="🌡️ Temperatura za naredne dane",
                xaxis_title="Vreme (Sat)",
                yaxis_title="Temperatura (°C)",
                plot_bgcolor='white',
                template='plotly_dark',
                margin=dict(l=40, r=40, t=40, b=40)
            )
            st.plotly_chart(fig_temp, use_container_width=True)

            # **2. Grafikon za padavine**
            fig_rain = go.Figure()
            fig_rain.add_trace(go.Bar(
                x=df_forecast['Sat'],
                y=df_forecast['Padavine (%)'],
                name="Padavine (%)",
                marker=dict(color='deepskyblue'),
                text=df_forecast['Padavine (%)'].apply(lambda x: f'{x}%'),
                hoverinfo='text'
            ))
            fig_rain.update_layout(
                title="💧 Padavine za naredne dane",
                xaxis_title="Vreme (Sat)",
                yaxis_title="Padavine (%)",
                plot_bgcolor='white',
                template='plotly_dark',
                margin=dict(l=40, r=40, t=40, b=40)
            )
            st.plotly_chart(fig_rain, use_container_width=True)

            # **3. Grafikon za vetar**
            fig_wind = go.Figure()
            fig_wind.add_trace(go.Scatter(
                x=df_forecast['Sat'],
                y=df_forecast['Vetar (m/s)'],
                mode='lines+markers',
                name="Vetar",
                line=dict(color='green', width=2),
                marker=dict(size=6, color='green'),
                text=df_forecast['Vetar (m/s)'].apply(lambda x: f'{x} m/s'),
                hoverinfo='text'
            ))
            fig_wind.update_layout(
                title="🌬️ Vetar za naredne dane",
                xaxis_title="Vreme (Sat)",
                yaxis_title="Vetar (m/s)",
                plot_bgcolor='white',
                template='plotly_dark',
                margin=dict(l=40, r=40, t=40, b=40)
            )
            st.plotly_chart(fig_wind, use_container_width=True)

            # **4. Grafikon za sunčevo zračenje**
            fig_sun = go.Figure()
            fig_sun.add_trace(go.Bar(
                x=df_forecast['Sat'],
                y=df_forecast['Sunčevo zračenje (W/m²)'],
                name="Sunčevo zračenje",
                marker=dict(color='gold'),
                text=df_forecast['Sunčevo zračenje (W/m²)'].apply(lambda x: f'{x} W/m²'),
                hoverinfo='text'
            ))
            fig_sun.update_layout(
                title="☀️ Sunčevo zračenje za naredne dane",
                xaxis_title="Vreme (Sat)",
                yaxis_title="Sunčevo zračenje (W/m²)",
                plot_bgcolor='white',
                template='plotly_dark',
                margin=dict(l=40, r=40, t=40, b=40)
            )
            st.plotly_chart(fig_sun, use_container_width=True)

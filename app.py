import streamlit as st
import pandas as pd
from datetime import datetime

# URL exacta de tu hoja (asegúrate de que esté compartida como pública)
URL_SHEET = "https://docs.google.com/spreadsheets/d/17It7DSAbGdglluYHKob_EsDP6ZlFuuTb/edit?usp=sharing"

def get_csv_url(url):
    # Esta función convierte el link normal en un link de descarga directa
    base_url = url.split('/edit')[0]
    return f"{base_url}/export?format=csv"

st.set_page_config(page_title="Sistema de Alquileres", page_icon="🏠")

def cargar_datos():
    csv_url = get_csv_url(URL_SHEET)
    df = pd.read_csv(csv_url)
    df.columns = df.columns.str.strip()
    
    # Renombrar para que coincida con tu imagen image_575d08.png
    nuevas_cols = {
        'Cuarto': 'Cuarto',
        'Nombre': 'Nombre',
        'Fecha_Ultimo_Pago': 'Fecha_Ultimo_Pago'
    }
    return df.rename(columns=nuevas_cols)

st.title("🏠 Sistema de Papá")

try:
    df = cargar_datos()
    # Convertir la columna de tu Excel a formato fecha real
    df['Fecha_Ultimo_Pago'] = pd.to_datetime(df['Fecha_Ultimo_Pago'], errors='coerce')
    
    hoy = datetime.now()
    df['Días Pasados'] = (hoy - df['Fecha_Ultimo_Pago']).dt.days
    df['Estado'] = df['Días Pasados'].apply(lambda x: "⚠️ VENCIDO" if x >= 30 else "✅ Al día")

    # Mostrar la tabla bonita
    st.subheader("Estado de Inquilinos")
    st.dataframe(df[['Cuarto', 'Nombre', 'Estado', 'Días Pasados']])
    
except Exception as e:
    st.error(f"Error al conectar: {e}")
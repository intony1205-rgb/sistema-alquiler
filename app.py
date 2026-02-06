import streamlit as st
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN
URL_SHEET = "https://docs.google.com/spreadsheets/d/17It7DSAbGdglluYHKob_EsDP6ZlFuuTb/edit?gid=1618672023#gid=1618672023"

def get_csv_url(url):
    return url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit#gid=', '/export?format=csv&gid=')

st.set_page_config(page_title="Sistema de Alquileres", page_icon="🏠")

def cargar_datos():
    csv_url = get_csv_url(URL_SHEET)
    # Leemos el CSV y forzamos a que ignore espacios en los nombres de columnas
    df = pd.read_csv(csv_url)
    df.columns = df.columns.str.strip() 
    
    # Diccionario para renombrar cualquier variación a lo que el código necesita
    nuevas_cols = {}
    for col in df.columns:
        low_col = col.lower()
        if 'cuarto' in low_col: nuevas_cols[col] = 'Cuarto'
        if 'nombre' in low_col: nuevas_cols[col] = 'Nombre'
        if 'fecha' in low_col: nuevas_cols[col] = 'Fecha_Ultimo_Pago'
    
    return df.rename(columns=nuevas_cols)

st.title("🏠 Sistema de Papá")

try:
    df = cargar_datos()
    
    # Verificación de seguridad: si no existe la columna tras el renombramiento
    if 'Fecha_Ultimo_Pago' not in df.columns:
        st.error(f"No encontré la columna de Fecha. Columnas detectadas: {list(df.columns)}")
    else:
        # Convertir fecha
        df['Fecha_Ultimo_Pago'] = pd.to_datetime(df['Fecha_Ultimo_Pago'], errors='coerce')
        hoy = datetime.now()

        # Cálculo de días y estados
        df['Días Pasados'] = (hoy - df['Fecha_Ultimo_Pago']).dt.days
        df['Estado'] = df['Días Pasados'].apply(lambda x: "⚠️ VENCIDO" if x >= 30 else "✅ Al día")

        # Mostrar tabla con colores
        st.subheader("Estado de Inquilinos")
        
        def color_estado(val):
            color = 'red' if val == "⚠️ VENCIDO" else 'green'
            return f'color: {color}; font-weight: bold'

        st.dataframe(df[['Cuarto', 'Nombre', 'Estado', 'Días Pasados']].style.applymap(color_estado, subset=['Estado']))

except Exception as e:
    st.error(f"Error crítico: {e}")
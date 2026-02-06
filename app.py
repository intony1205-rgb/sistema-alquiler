import streamlit as st
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN: Pega aquí el enlace de tu Google Sheet
URL_SHEET = "https://docs.google.com/spreadsheets/d/17It7DSAbGdglluYHKob_EsDP6ZlFuuTb/edit?gid=1618672023#gid=1618672023"

# Convertir el enlace para que Streamlit pueda leerlo como CSV
def get_csv_url(url):
    return url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit#gid=', '/export?format=csv&gid=')

st.set_page_config(page_title="Sistema de Alquileres", page_icon="🏠")

def cargar_datos():
    csv_url = get_csv_url(URL_SHEET)
    df = pd.read_csv(csv_url)
    # Estandarizar columnas (tu lógica original)
    df.columns = df.columns.str.strip()
    nuevas_cols = {col: 'Cuarto' for col in df.columns if 'cuarto' in col.lower()}
    nuevas_cols.update({col: 'Nombre' for col in df.columns if 'nombre' in col.lower()})
    nuevas_cols.update({col: 'Fecha_Ultimo_Pago' for col in df.columns if 'fecha' in col.lower()})
    return df.rename(columns=nuevas_cols)

st.title("🏠 Sistema de Papá")

try:
    df = cargar_datos()
    df['Fecha_Ultimo_Pago'] = pd.to_datetime(df['Fecha_Ultimo_Pago'], errors='coerce')
    hoy = datetime.now()

    # Cálculo de estados
    df['Días Pasados'] = (hoy - df['Fecha_Ultimo_Pago']).dt.days
    df['Estado'] = df['Días Pasados'].apply(lambda x: "⚠️ VENCIDO" if x >= 30 else "✅ Al día")

    tab1, tab2 = st.tabs(["📊 Reporte", "💰 Registrar Pago"])

    with tab1:
        st.subheader("Estado de Inquilinos")
        st.dataframe(df[['Cuarto', 'Nombre', 'Estado', 'Días Pasados']])

    with tab2:
        st.subheader("¿Quién pagó hoy?")
        cuarto_sel = st.selectbox("Selecciona Cuarto", df['Cuarto'].unique())
        if st.button("Marcar como Pagado"):
            st.info("Para guardar cambios permanentes, abre el Google Sheet y actualiza la fecha. ¡Pronto lo automatizaremos al 100%!")
            
except Exception as e:
    st.error(f"Error al conectar: {e}")
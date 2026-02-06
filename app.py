import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuración de la página
st.set_page_config(page_title="Sistema de Alquileres", page_icon="🏠")

def preparar_df(archivo_excel):
    df = pd.read_excel(archivo_excel)
    df.columns = df.columns.str.strip()
    nuevas_cols = {col: 'Cuarto' for col in df.columns if 'cuarto' in col.lower()}
    nuevas_cols.update({col: 'Fecha_Ultimo_Pago' for col in df.columns if 'fecha' in col.lower()})
    nuevas_cols.update({col: 'Nombre' for col in df.columns if 'nombre' in col.lower()})
    return df.rename(columns=nuevas_cols)

# Título de la App
st.title("🏠 Registro de Alquiler de Papá")

archivo = 'Dataa.xlsx'

if not os.path.exists(archivo):
    st.error(f"No se encontró el archivo {archivo}")
else:
    df = preparar_df(archivo)
    # Convertir fecha a datetime
    df['Fecha_Ultimo_Pago'] = pd.to_datetime(df['Fecha_Ultimo_Pago'], format='mixed', dayfirst=False)
    hoy = datetime.now()

    # --- LÓGICA DE ESTADOS ---
    def calcular_estado(fecha):
        if pd.isna(fecha): return "❓ Error", 0
        dias = (hoy - fecha).days
        estado = "⚠️ VENCIDO" if dias >= 30 else "✅ Al día"
        return estado, dias

    # Aplicar lógica
    df['Estado'], df['Días Pasados'] = zip(*df['Fecha_Ultimo_Pago'].apply(calcular_estado))

    # --- INTERFAZ ---
    tab1, tab2, tab3 = st.tabs(["📋 Reporte Completo", "💰 Registrar Pago", "📢 Pendientes"])

    with tab1:
        st.subheader("Estado General")
        st.dataframe(df.style.applymap(lambda x: 'color: red' if x == "⚠️ VENCIDO" else ('color: green' if x == "✅ Al día" else ''), subset=['Estado']))

    with tab2:
        st.subheader("Actualizar Pago")
        cuartos_lista = df['Cuarto'].astype(str).unique()
        seleccion = st.selectbox("Selecciona el cuarto que pagó:", cuartos_lista)
        
        if st.button("Registrar Pago Hoy"):
            idx = df.index[df['Cuarto'].astype(str) == seleccion].tolist()[0]
            # Actualizar en el DataFrame y guardar
            df.at[idx, 'Fecha_Ultimo_Pago'] = hoy.strftime('%Y-%m-%d') # Formato estándar para Excel
            df_para_guardar = df.drop(columns=['Estado', 'Días Pasados'])
            df_para_guardar.to_excel(archivo, index=False)
            st.success(f"¡Pago registrado para el cuarto {seleccion}!")
            st.rerun()

    with tab3:
        st.subheader("Inquilinos con más de 30 días")
        deudores = df[df['Días Pasados'] >= 30]
        if deudores.empty:
            st.balloons()
            st.success("¡Todos están al día!")
        else:
            st.table(deudores[['Cuarto', 'Nombre', 'Días Pasados']])
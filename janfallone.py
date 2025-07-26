import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración
st.set_page_config(layout="wide")
st.title("📊 Dashboard para Excel Transpuesto")

# Cargar archivo
uploaded_file = st.file_uploader("Sube tu Excel (filas ↔ columnas)", type="xlsx")
if uploaded_file:
    try:
        # Leer el archivo y transponer
        df = pd.read_excel(uploaded_file, header=None)  # No asumir encabezados
        df_transposed = df.T  # Transponer: filas → columnas
        
        # Convertir la primera fila en encabezados
        df_transposed.columns = df_transposed.iloc[0]  # Usar primera fila como nombres de columnas
        df_clean = df_transposed.drop(df_transposed.index[0])  # Eliminar la primera fila (ahora es el header)
        
        # Mostrar datos limpios (para debug)
        with st.expander("Ver datos transpuestos"):
            st.dataframe(df_clean)

        # --- KPIs ---
        st.header("🔍 KPIs")
        numeric_cols = df_clean.select_dtypes(include=['number']).columns
        
        if not numeric_cols.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Ventas", f"${df_clean['Ventas'].sum():,.0f}")  # Ajusta 'Ventas' a tu columna
            col2.metric("Promedio", f"${df_clean['Ventas'].mean():,.0f}")
            col3.metric("Registros", len(df_clean))
        
        # --- Gráficos ---
        st.header("📈 Gráficos")
        
        # Gráfico de barras (ajusta 'Categoría' y 'Ventas')
        if 'Ventas' in df_clean.columns:
            fig = px.bar(df_clean, x='Categoría', y='Ventas', title="Ventas por Categoría")
            st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de línea para series temporales
        if 'Fecha' in df_clean.columns:
            df_clean['Fecha'] = pd.to_datetime(df_clean['Fecha'])  # Convertir a fecha
            fig2 = px.line(df_clean, x='Fecha', y='Ventas', title="Ventas en el tiempo")
            st.plotly_chart(fig2, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.warning("Por favor, sube un archivo Excel.")

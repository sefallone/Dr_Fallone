import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Excel", layout="wide")

# Título
st.title("📊 Dashboard de Análisis de Excel")

# Carga el archivo
uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type="xlsx")

if uploaded_file:
    # Leer el Excel
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    
    # Mostrar datos en bruto (opcional)
    with st.expander("Ver datos originales"):
        st.dataframe(df)

    # --- KPIs ---
    st.header("🔍 KPIs Principales")
    col1, col2, col3 = st.columns(3)
    
    # Ejemplo de KPIs (ajusta según tus columnas)
    if 'Ventas' in df.columns:
        col1.metric("Ventas Totales", f"${df['Ventas'].sum():,.0f}")
        col2.metric("Promedio Ventas", f"${df['Ventas'].mean():,.0f}")
        col3.metric("Transacciones", df.shape[0])

    # --- Gráficos ---
    st.header("📈 Visualizaciones")
    
    # Gráfico 1: Ventas por categoría (Plotly)
    if 'Ventas' in df.columns and 'Categoría' in df.columns:
        fig1 = px.bar(df, x='Categoría', y='Ventas', title="Ventas por Categoría")
        st.plotly_chart(fig1, use_container_width=True)
    
    # Gráfico 2: Serie temporal (Matplotlib)
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'])  # Convertir a datetime
        fig2, ax = plt.subplots()
        df.groupby(df['Fecha'].dt.to_period('M'))['Ventas'].sum().plot(kind='line', ax=ax)
        ax.set_title("Ventas Mensuales")
        st.pyplot(fig2)

    # Gráfico 3: Pie chart (Plotly)
    if 'Región' in df.columns:
        fig3 = px.pie(df, names='Región', title="Distribución por Región")
        st.plotly_chart(fig3, use_container_width=True)

else:
    st.warning("Por favor, sube un archivo Excel.")

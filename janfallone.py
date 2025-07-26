import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Dashboard para Excel Transpuesto")

uploaded_file = st.file_uploader("Sube tu Excel", type="xlsx")
if uploaded_file:
    try:
        # Leer y transponer
        df = pd.read_excel(uploaded_file, header=None)
        df_clean = df.T.set_index(0).T  # Transpone y usa primera fila como headers
        df_clean.columns = df_clean.iloc[0]
        df_clean = df_clean.drop(0).reset_index(drop=True)
        
        # Convertir columnas numéricas
        numeric_cols = ['Ventas', 'Otra_Columna']  # Ajusta a tus columnas
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Mostrar datos (debug)
        st.dataframe(df_clean)
        
        # KPIs (convertir valores a nativos)
        if 'Ventas' in df_clean.columns:
            col1, col2 = st.columns(2)
            col1.metric("Ventas totales", f"${int(df_clean['Ventas'].sum()):,.0f}")
            col2.metric("Promedio", f"${float(df_clean['Ventas'].mean()):,.2f}")
        
        # Gráficos (asegurar datos serializables)
        if 'Categoría' in df_clean.columns and 'Ventas' in df_clean.columns:
            fig = px.bar(df_clean, x='Categoría', y='Ventas')  # Plotly maneja la conversión
            st.plotly_chart(fig)
    
    except Exception as e:
        st.error(f"Error: {str(e)}")  # Muestra el error como string

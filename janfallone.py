import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Dashboard para Excel Transpuesto")

uploaded_file = st.file_uploader("Sube tu Excel", type="xlsx")
if uploaded_file:
    try:
        # 1. Leer archivo (sin asumir encabezados)
        df = pd.read_excel(uploaded_file, header=None)
        
        # 2. Transponer y limpiar
        df_transposed = df.T
        df_clean = df_transposed.rename(columns=df_transposed.iloc[0]).drop(index=df_transposed.index[0])
        
        # 3. Convertir columnas numéricas
        numeric_cols = ['Ventas', 'Cantidad']  # Ajusta a tus columnas
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # 4. Mostrar datos para debug
        st.write("Datos procesados:", df_clean)
        
        # 5. KPIs y gráficos (ejemplo)
        if 'Ventas' in df_clean.columns:
            st.metric("Ventas totales", f"${int(df_clean['Ventas'].sum()):,.0f}")
            fig = px.bar(df_clean, x=df_clean.columns[1], y='Ventas')  # Ajusta ejes
            st.plotly_chart(fig)
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

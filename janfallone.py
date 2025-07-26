import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Comparativo VITHAS-OSA", layout="wide")

# Título
st.title("🏥 Dashboard Comparativo VITHAS vs OSA")
st.markdown("### Análisis de Diferencias Porcentuales")

# Carga y procesamiento de datos
def load_data(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Proyeccion 2026")
        
        # Limpieza de nombres de columnas
        df.columns = df.columns.str.strip()
        
        # Columnas requeridas (ajustadas a tu archivo)
        required_columns = {
            'Fecha': 'Fecha',
            'Total Facturación': 'Total Facturación',
            'Facturación CCEE VITHAS': 'Facturación CCEE VITHAS',
            'Facturación CCEE OSA (80%)': 'Facturación CCEE OSA (80%)',
            'Facturación Quirúrgico VITHAS': 'Facturación Quirúrgico VITHAS',
            'Facturación Quirúrgico OSA (90%)': 'Facturación Quirúrgico OSA (90%)',
            'Facturación Urgencias VITHAS': 'Facturación Urgencias VITHAS',
            'Facturación Urgencias OSA (50%)': 'Facturación Urgencias OSA (50%)'
        }
        
        # Verificar columnas
        missing = [k for k, v in required_columns.items() if v not in df.columns]
        if missing:
            st.error(f"Columnas faltantes: {missing}")
            st.write("Columnas disponibles:", df.columns.tolist())
            return None
            
        # Convertir tipos de datos
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        for col in required_columns.values():
            if col != 'Fecha':
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return None

# Cálculo de KPIs comparativos
def calculate_kpis(df):
    # Totales por categoría
    resultados = {
        'Total VITHAS': df['Facturación CCEE VITHAS'].sum() + 
                       df['Facturación Quirúrgico VITHAS'].sum() + 
                       df['Facturación Urgencias VITHAS'].sum(),
        
        'Total OSA': df['Facturación CCEE OSA (80%)'].sum() + 
                    df['Facturación Quirúrgico OSA (90%)'].sum() + 
                    df['Facturación Urgencias OSA (50%)'].sum(),
        
        'CCEE VITHAS': df['Facturación CCEE VITHAS'].sum(),
        'CCEE OSA': df['Facturación CCEE OSA (80%)'].sum(),
        
        'Quirúrgico VITHAS': df['Facturación Quirúrgico VITHAS'].sum(),
        'Quirúrgico OSA': df['Facturación Quirúrgico OSA (90%)'].sum(),
        
        'Urgencias VITHAS': df['Facturación Urgencias VITHAS'].sum(),
        'Urgencias OSA': df['Facturación Urgencias OSA (50%)'].sum()
    }
    
    # Cálculo de diferencias porcentuales
    resultados['Diferencia % Total'] = ((resultados['Total VITHAS'] / resultados['Total OSA'] - 1) * 100
    resultados['Diferencia % CCEE'] = ((resultados['CCEE VITHAS'] / resultados['CCEE OSA'] - 1) * 100
    resultados['Diferencia % Quirúrgico'] = ((resultados['Quirúrgico VITHAS'] / resultados['Quirúrgico OSA'] - 1) * 100
    resultados['Diferencia % Urgencias'] = ((resultados['Urgencias VITHAS'] / resultados['Urgencias OSA'] - 1) * 100
    
    return resultados

# Interfaz principal
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        # Calcular KPIs
        kpis = calculate_kpis(df)
        
        # ==============================================
        # SECCIÓN DE KPIs COMPARATIVOS
        # ==============================================
        st.header("📊 KPIs Comparativos")
        
        # Fila 1 - Totales
        col1, col2, col3 = st.columns(3)
        col1.metric("Facturación Total VITHAS", f"€{kpis['Total VITHAS']:,.0f}")
        col2.metric("Facturación Total OSA", f"€{kpis['Total OSA']:,.0f}")
        col3.metric("Diferencia % Total", 
                   f"{kpis['Diferencia % Total']:.1f}%",
                   delta=f"{kpis['Diferencia % Total']:.1f}%")
        
        # Fila 2 - Por categoría
        st.subheader("Diferencias por Categoría")
        
        col4, col5, col6 = st.columns(3)
        col4.metric("Consultas Externas", 
                   f"{kpis['Diferencia % CCEE']:.1f}%",
                   help="VITHAS vs OSA (80%)")
        col5.metric("Quirúrgico", 
                   f"{kpis['Diferencia % Quirúrgico']:.1f}%",
                   help="VITHAS vs OSA (90%)")
        col6.metric("Urgencias", 
                   f"{kpis['Diferencia % Urgencias']:.1f}%",
                   help="VITHAS vs OSA (50%)")
        
        # ==============================================
        # GRÁFICOS COMPARATIVOS
        # ==============================================
        st.header("📈 Análisis Visual")
        
        # Gráfico 1: Diferencias porcentuales
        diff_df = pd.DataFrame({
            'Categoría': ['Total', 'Consultas', 'Quirúrgico', 'Urgencias'],
            'Diferencia %': [
                kpis['Diferencia % Total'],
                kpis['Diferencia % CCEE'],
                kpis['Diferencia % Quirúrgico'],
                kpis['Diferencia % Urgencias']
            ]
        })
        
        fig1 = px.bar(diff_df, x='Categoría', y='Diferencia %',
                     title="Diferencias Porcentuales VITHAS vs OSA",
                     text_auto='.1f%',
                     color='Categoría')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico 2: Evolución mensual de diferencias
        df['Diferencia % CCEE'] = (df['Facturación CCEE VITHAS'] / df['Facturación CCEE OSA (80%)'] - 1) * 100
        df['Diferencia % Quirúrgico'] = (df['Facturación Quirúrgico VITHAS'] / df['Facturación Quirúrgico OSA (90%)'] - 1) * 100
        df['Diferencia % Urgencias'] = (df['Facturación Urgencias VITHAS'] / df['Facturación Urgencias OSA (50%)'] - 1) * 100
        
        fig2 = px.line(df, x='Fecha', 
                      y=['Diferencia % CCEE', 'Diferencia % Quirúrgico', 'Diferencia % Urgencias'],
                      title="Evolución Mensual de Diferencias Porcentuales",
                      labels={'value': 'Diferencia %', 'variable': 'Categoría'})
        st.plotly_chart(fig2, use_container_width=True)
        
        # ==============================================
        # TABLA RESUMEN
        # ==============================================
        st.header("📋 Resumen Comparativo")
        
        summary_data = [
            ["Total", kpis['Total VITHAS'], kpis['Total OSA'], kpis['Diferencia % Total']],
            ["Consultas Externas", kpis['CCEE VITHAS'], kpis['CCEE OSA'], kpis['Diferencia % CCEE']],
            ["Quirúrgico", kpis['Quirúrgico VITHAS'], kpis['Quirúrgico OSA'], kpis['Diferencia % Quirúrgico']],
            ["Urgencias", kpis['Urgencias VITHAS'], kpis['Urgencias OSA'], kpis['Diferencia % Urgencias']]
        ]
        
        summary_df = pd.DataFrame(
            summary_data,
            columns=["Categoría", "VITHAS (€)", "OSA (€)", "Diferencia %"]
        )
        
        # Formatear valores
        summary_df["VITHAS (€)"] = summary_df["VITHAS (€)"].apply(lambda x: f"€{x:,.0f}")
        summary_df["OSA (€)"] = summary_df["OSA (€)"].apply(lambda x: f"€{x:,.0f}")
        summary_df["Diferencia %"] = summary_df["Diferencia %"].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(summary_df, hide_index=True, use_container_width=True)

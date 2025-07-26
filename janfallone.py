import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def clean_column_name(name):
    """Estandariza nombres de columnas eliminando espacios y caracteres especiales"""
    return (name.strip()
            .replace(" ", "_")
            .replace("(", "")
            .replace(")", "")
            .replace("%", "porc")
            .replace("ó", "o")
            .replace("í", "i")
            .lower())

def load_and_process_data(uploaded_file):
    try:
        # Leer el archivo Excel
        df = pd.read_excel(uploaded_file, sheet_name="Proyeccion 2026")
        
        # Verificar si el DataFrame está vacío
        if df.empty:
            raise ValueError("El archivo no contiene datos o la hoja está vacía")
        
        # Estandarizar nombres de columnas
        df.columns = [clean_column_name(col) for col in df.columns]
        
        # Mapeo de columnas esperadas
        expected_columns = {
            'fecha': 'Fecha',
            'total_facturacion': 'Total Facturación',
            'facturacion_ccee_vithas': 'Facturación CCEE VITHAS',
            'facturacion_ccee_osa_80porc': 'Facturación CCEE OSA (80%)',
            'no_de_pacientes_ccee': 'No. De Pacientes CCEE',
            'facturacion_quirurgico_vithas': 'Facturación Quirúrgico VITHAS',
            'facturacion_quirurgico_osa_90porc': 'Facturación Quirúrgico OSA (90%)',
            'facturacion_urgencias_osa_50porc': 'Facturación Urgencias OSA (50%)',
            'facturacion_urgencias_vithas': 'Facturación Urgencias VITHAS'
        }
        
        # Verificar columnas faltantes
        missing_columns = [original for clean, original in expected_columns.items() 
                          if clean not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Columnas requeridas no encontradas: {missing_columns}\n"
                           f"Columnas disponibles: {list(df.columns)}")
        
        # Renombrar columnas a nombres estandarizados
        df.rename(columns={clean: original for clean, original in expected_columns.items()}, 
                 inplace=True)
        
        # Limpieza de datos
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        
        # Convertir columnas numéricas
        numeric_cols = ['Total Facturación', 'Facturación CCEE VITHAS', 
                       'Facturación CCEE OSA (80%)', 'No. De Pacientes CCEE',
                       'Facturación Quirúrgico VITHAS', 'Facturación Quirúrgico OSA (90%)',
                       'Facturación Urgencias OSA (50%)', 'Facturación Urgencias VITHAS']
        
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].isnull().any():
                raise ValueError(f"La columna {col} contiene valores no numéricos")
        
        return df
    
    except Exception as e:
        st.error("❌ Error crítico durante la carga de datos")
        st.error(str(e))
        st.warning("ℹ️ Posibles soluciones:")
        st.write("- Verifica que el archivo sea la versión correcta de 'Proyeccion 3.xlsx'")
        st.write("- Asegúrate que la hoja se llame exactamente 'Proyeccion 2026'")
        st.write("- Revisa que las columnas coincidan con los nombres esperados")
        
        # Mostrar columnas disponibles para ayudar en la depuración
        try:
            if 'df' in locals():
                st.write("🔍 Columnas encontradas en el archivo:")
                st.write(df.columns.tolist())
                
                st.write("📊 Primeras filas de datos:")
                st.dataframe(df.head())
        except:
            pass
        
        return None

# Interfaz de usuario
st.title("🏥 Dashboard de Proyecciones Médicas")

uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:
    df = load_and_process_data(uploaded_file)
    
    if df is not None:
        try:
            # ==============================================
            # ANÁLISIS Y VISUALIZACIONES
            # ==============================================
            
            # 1. Cálculo de métricas comparativas
            total_vithas = df['Facturación CCEE VITHAS'].sum() + df['Facturación Quirúrgico VITHAS'].sum() + df['Facturación Urgencias VITHAS'].sum()
            total_osa = df['Facturación CCEE OSA (80%)'].sum() + df['Facturación Quirúrgico OSA (90%)'].sum() + df['Facturación Urgencias OSA (50%)'].sum()
            
            # 2. KPIs comparativos
            st.header("📊 KPIs Comparativos VITHAS vs OSA")
            col1, col2, col3 = st.columns(3)
            col1.metric("Facturación Total VITHAS", f"€{total_vithas:,.0f}")
            col2.metric("Facturación Total OSA", f"€{total_osa:,.0f}")
            col3.metric("Diferencia", f"€{total_vithas-total_osa:,.0f}", 
                       delta=f"{(total_vithas/total_osa-1)*100:.1f}%" if total_osa > 0 else "N/A")
            
            # 3. Gráfico de evolución comparativa
            st.header("📈 Evolución Mensual")
            fig = px.line(df, x='Fecha', 
                         y=['Facturación CCEE VITHAS', 'Facturación CCEE OSA (80%)',
                            'Facturación Quirúrgico VITHAS', 'Facturación Quirúrgico OSA (90%)',
                            'Facturación Urgencias VITHAS', 'Facturación Urgencias OSA (50%)'],
                         title="Comparación por Categoría",
                         labels={'value': 'Facturación (€)', 'variable': 'Categoría'})
            st.plotly_chart(fig, use_container_width=True)
            
            # 4. Gráfico de composición
            st.header("🧩 Composición de Facturación")
            fig2 = px.pie(
                names=['VITHAS CCEE', 'VITHAS Quirúrgico', 'VITHAS Urgencias',
                      'OSA CCEE', 'OSA Quirúrgico', 'OSA Urgencias'],
                values=[
                    df['Facturación CCEE VITHAS'].sum(),
                    df['Facturación Quirúrgico VITHAS'].sum(),
                    df['Facturación Urgencias VITHAS'].sum(),
                    df['Facturación CCEE OSA (80%)'].sum(),
                    df['Facturación Quirúrgico OSA (90%)'].sum(),
                    df['Facturación Urgencias OSA (50%)'].sum()
                ],
                title="Distribución de Facturación"
            )
            st.plotly_chart(fig2, use_container_width=True)
            
        except Exception as analysis_error:
            st.error("❌ Error durante el análisis de datos")
            st.error(str(analysis_error))
            st.write("⚠️ Por favor reporta este error al administrador del sistema")

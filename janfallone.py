import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def load_and_process_data(uploaded_file):
    try:
        # Leer el archivo Excel manteniendo los espacios en nombres de columnas
        df = pd.read_excel(uploaded_file, sheet_name="Proyeccion 2026")
        
        # Mostrar columnas exactas para diagnóstico
        st.write("🔍 Columnas encontradas (exactas con espacios):")
        st.write([f"'{col}'" for col in df.columns.tolist()])
        
        # Mapeo completo con todas las variantes posibles
        column_mapping = {
            'Fecha': ['Fecha'],
            'Total Facturación': ['Total Facturación', 'total_facturacion'],
            'Facturación CCEE VITHAS': ['Facturación CCEE VITHAS', 'facturacion_ccee_vithas'],
            'Facturación CCEE OSA (80%)': ['Facturación CCEE OSA (80%)', 'facturacion_ccee_osa_80porc'],
            'No. De Pacientes CCEE': ['No. De Pacientes CCEE', 'no._de_pacientes_ccee'],
            'Facturación Quirúrgico VITHAS': ['Facturación Quirúrgico VITHAS', 'facturacion_quirúrgico_vithas'],
            'Facturación Quirúrgico OSA (90%)': ['Facturación Quirúrgico OSA (90%)', 'facturacion_quirúrgico_osa_90porc'],
            'Facturación Urgencias OSA (50%)': [
                'Facturación Urgencias OSA (50%)', 
                'facturacion_urgencias_osa_50porc',
                'facturacion_urgencias_osa_50porc ',  # Con espacio al final
                'Facturación Urgencias OSA (50% )'   # Con espacio antes del paréntesis
            ],
            'Facturación Urgencias VITHAS': ['Facturación Urgencias VITHAS', 'facturacion_urgencias_vithas']
        }
        
        # Encontrar coincidencias exactas
        actual_columns = {}
        for standard_name, possible_names in column_mapping.items():
            found = False
            for name in possible_names:
                # Buscar coincidencia exacta incluyendo espacios
                if name in df.columns:
                    actual_columns[standard_name] = name
                    found = True
                    break
            
            if not found:
                # Intentar coincidencia insensible a espacios y mayúsculas
                for col in df.columns:
                    if col.strip().lower() in [n.strip().lower() for n in possible_names]:
                        actual_columns[standard_name] = col
                        found = True
                        break
            
            if not found:
                st.error(f"❌ No se encontró: {standard_name}")
                st.error(f"Variantes probadas: {possible_names}")
                st.error(f"Columnas disponibles: {list(df.columns)}")
                return None
        
        # Renombrar columnas
        df.rename(columns={v: k for k, v in actual_columns.items()}, inplace=True)
        
        # Verificación final
        required_columns = list(column_mapping.keys())
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error(f"❌ Columnas faltantes: {missing}")
            return None
        
        # Limpieza de datos
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        for col in required_columns:
            if col != 'Fecha':
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

# Interfaz
st.title("🏥 Dashboard de Proyecciones Médicas")

uploaded_file = st.file_uploader("Sube 'Proyeccion 3.xlsx'", type=["xlsx"])

if uploaded_file:
    df = load_and_process_data(uploaded_file)
    
    if df is not None:
        st.success("✅ Datos cargados correctamente!")
        st.write(df.head())
        
        
        # ==============================================
        # ANÁLISIS Y VISUALIZACIONES
        # ==============================================
        
        st.header("📊 KPIs Clave")
        
        # 1. Cálculo de totales
        total_vithas = df['Facturación CCEE VITHAS'].sum() + \
                      df['Facturación Quirúrgico VITHAS'].sum() + \
                      df['Facturación Urgencias VITHAS'].sum()
        
        total_osa = df['Facturación CCEE OSA (80%)'].sum() + \
                   df['Facturación Quirúrgico OSA (90%)'].sum() + \
                   df['Facturación Urgencias OSA (50%)'].sum()
        
        # 2. Mostrar KPIs
        col1, col2 = st.columns(2)
        col1.metric("Facturación Total VITHAS", f"€{total_vithas:,.0f}")
        col2.metric("Facturación Total OSA", f"€{total_osa:,.0f}")
        
        # 3. Gráfico comparativo
        st.header("📈 Comparativo Mensual")
        fig = px.line(df, x='Fecha', 
                     y=['Facturación CCEE VITHAS', 'Facturación CCEE OSA (80%)',
                        'Facturación Quirúrgico VITHAS', 'Facturación Quirúrgico OSA (90%)',
                        'Facturación Urgencias VITHAS', 'Facturación Urgencias OSA (50%)'],
                     title="Evolución de Facturación",
                     labels={'value': 'Euros (€)', 'variable': 'Categoría'})
        st.plotly_chart(fig, use_container_width=True)
        
        # 4. Gráfico de composición
        st.header("🧩 Composición de Facturación")
        fig2 = px.pie(
            names=['CCEE VITHAS', 'Quirúrgico VITHAS', 'Urgencias VITHAS',
                  'CCEE OSA', 'Quirúrgico OSA', 'Urgencias OSA'],
            values=[
                df['Facturación CCEE VITHAS'].sum(),
                df['Facturación Quirúrgico VITHAS'].sum(),
                df['Facturación Urgencias VITHAS'].sum(),
                df['Facturación CCEE OSA (80%)'].sum(),
                df['Facturación Quirúrgico OSA (90%)'].sum(),
                df['Facturación Urgencias OSA (50%)'].sum()
            ],
            hole=0.3
        )
        st.plotly_chart(fig2, use_container_width=True)

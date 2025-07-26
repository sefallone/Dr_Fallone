import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def load_data(uploaded_file):
    try:
        # Leer el archivo Excel
        df = pd.read_excel(uploaded_file, sheet_name="Proyeccion 2026")
        
        # Mostrar columnas exactas para diagnóstico
        st.write("🔍 Columnas encontradas en el archivo:")
        st.write([f"'{col}'" for col in df.columns.tolist()])
        
        # Mapeo flexible de columnas con todas las variantes posibles
        column_mapping = {
            'Fecha': ['Fecha'],
            'Total Facturación': ['Total Facturación', 'total_facturacion'],
            'Facturación CCEE VITHAS': ['Facturación CCEE VITHAS', 'facturacion_ccee_vithas'],
            'Facturación CCEE OSA (80%)': ['Facturación CCEE OSA (80%)', 'facturacion_ccee_osa_80porc'],
            'No. De Pacientes CCEE': ['No. De Pacientes CCEE', 'no._de_pacientes_ccee'],
            'Facturación Quirúrgico VITHAS': ['Facturación Quirúrgico VITHAS', 'facturacion_quirúrgico_vithas'],
            'Facturación Quirúrgico OSA (90%)': ['Facturación Quirúrgico OSA (90%)', 'facturacion_quirúrgico_osa_90porc'],
            'Facturación Urgencias VITHAS': ['Facturación Urgencias VITHAS', 'facturacion_urgencias_vithas'],
            'Facturación Urgencias OSA (50%)': [
                'Facturación Urgencias OSA (50%)',
                'facturacion_urgencias_osa_50porc',
                'facturacion_urgencias_osa_50porc ',  # Con espacio al final
                'Facturación Urgencias OSA (50% )',   # Con espacio antes del paréntesis
                'facturacion_urgencias_osa_50%',      # Sin 'porc'
                'Facturación Urgencias OSA 50%'       # Sin paréntesis
            ]
        }
        
        # Encontrar los nombres reales de las columnas
        actual_columns = {}
        for standard_name, possible_names in column_mapping.items():
            found = False
            for name in possible_names:
                if name in df.columns:
                    actual_columns[standard_name] = name
                    found = True
                    break
            
            if not found:
                # Búsqueda flexible (ignorando mayúsculas, espacios y caracteres especiales)
                for col in df.columns:
                    clean_col = col.strip().lower().replace(" ", "").replace("_", "").replace("ó", "o").replace("(", "").replace(")", "").replace("%", "")
                    clean_possible = [n.strip().lower().replace(" ", "").replace("_", "").replace("ó", "o").replace("(", "").replace(")", "").replace("%", "") for n in possible_names]
                    
                    if clean_col in clean_possible:
                        actual_columns[standard_name] = col
                        found = True
                        break
            
            if not found:
                st.error(f"❌ No se encontró ninguna variante de: {standard_name}")
                st.error(f"Variantes probadas: {possible_names}")
                return None
        
        # Renombrar columnas a nombres estándar
        df.rename(columns={v: k for k, v in actual_columns.items()}, inplace=True)
        
        # Verificación final
        required_columns = list(column_mapping.keys())
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error(f"❌ Columnas faltantes después del mapeo: {missing}")
            return None
        
        # Limpieza de datos
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        for col in required_columns:
            if col != 'Fecha':
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        return None

# Interfaz principal
st.title("🏥 Dashboard Comparativo VITHAS vs OSA")

uploaded_file = st.file_uploader("Sube tu archivo 'Proyeccion 3.xlsx'", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        st.success("✅ Datos cargados correctamente!")
        
        # ==============================================
        # CÁLCULO DE KPIs COMPARATIVOS
        # ==============================================
        
        # 1. Totales por categoría
        total_vithas = df['Facturación CCEE VITHAS'].sum() + \
                      df['Facturación Quirúrgico VITHAS'].sum() + \
                      df['Facturación Urgencias VITHAS'].sum()
        
        total_osa = df['Facturación CCEE OSA (80%)'].sum() + \
                   df['Facturación Quirúrgico OSA (90%)'].sum() + \
                   df['Facturación Urgencias OSA (50%)'].sum()
        
        # 2. Diferencias porcentuales
        diff_total = (total_vithas / total_osa - 1) * 100 if total_osa != 0 else 0
        diff_ccee = (df['Facturación CCEE VITHAS'].sum() / df['Facturación CCEE OSA (80%)'].sum() - 1) * 100
        diff_quir = (df['Facturación Quirúrgico VITHAS'].sum() / df['Facturación Quirúrgico OSA (90%)'].sum() - 1) * 100
        diff_urg = (df['Facturación Urgencias VITHAS'].sum() / df['Facturación Urgencias OSA (50%)'].sum() - 1) * 100
        
        # ==============================================
        # VISUALIZACIÓN DE KPIs
        # ==============================================
        
        st.header("📊 KPIs Comparativos")
        
        # Fila 1 - Totales
        col1, col2, col3 = st.columns(3)
        col1.metric("Facturación Total VITHAS", f"€{total_vithas:,.0f}")
        col2.metric("Facturación Total OSA", f"€{total_osa:,.0f}")
        col3.metric("Diferencia % Total", f"{diff_total:.1f}%", 
                   delta=f"{diff_total:.1f}%")
        
        # Fila 2 - Por categoría
        st.subheader("Diferencias por Categoría")
        col4, col5, col6 = st.columns(3)
        col4.metric("Consultas Externas", f"{diff_ccee:.1f}%",
                   help="VITHAS vs OSA (80%)")
        col5.metric("Quirúrgico", f"{diff_quir:.1f}%",
                   help="VITHAS vs OSA (90%)")
        col6.metric("Urgencias", f"{diff_urg:.1f}%",
                   help="VITHAS vs OSA (50%)")
        
        # ==============================================
        # GRÁFICOS COMPARATIVOS
        # ==============================================
        
        st.header("📈 Análisis Visual")
        
        # Gráfico 1: Diferencias porcentuales
        diff_df = pd.DataFrame({
            'Categoría': ['Total', 'Consultas', 'Quirúrgico', 'Urgencias'],
            'Diferencia %': [diff_total, diff_ccee, diff_quir, diff_urg]
        })
        
        fig1 = px.bar(diff_df, x='Categoría', y='Diferencia %',
                     title="Diferencias Porcentuales VITHAS vs OSA",
                     text_auto='.1f%',
                     color='Categoría')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico 2: Evolución mensual
        df['Diferencia % CCEE'] = (df['Facturación CCEE VITHAS'] / df['Facturación CCEE OSA (80%)'] - 1) * 100
        df['Diferencia % Quirúrgico'] = (df['Facturación Quirúrgico VITHAS'] / df['Facturación Quirúrgico OSA (90%)'] - 1) * 100
        df['Diferencia % Urgencias'] = (df['Facturación Urgencias VITHAS'] / df['Facturación Urgencias OSA (50%)'] - 1) * 100
        
        fig2 = px.line(df, x='Fecha', 
                      y=['Diferencia % CCEE', 'Diferencia % Quirúrgico', 'Diferencia % Urgencias'],
                      title="Evolución Mensual de Diferencias",
                      labels={'value': 'Diferencia %', 'variable': 'Categoría'})
        st.plotly_chart(fig2, use_container_width=True)

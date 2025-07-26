import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def load_and_process_data(uploaded_file):
    try:
        # Leer el archivo Excel
        df = pd.read_excel(uploaded_file, sheet_name="Proyeccion 2026")
        
        # Verificar si el DataFrame está vacío
        if df.empty:
            raise ValueError("El archivo no contiene datos o la hoja está vacía")
        
        # Lista de columnas disponibles para depuración
        st.session_state.available_columns = df.columns.tolist()
        
        # Mapeo exacto de columnas basado en tu archivo
        column_mapping = {
            'Fecha': 'Fecha',
            'Total Facturación': 'Total Facturación',
            'Facturación CCEE VITHAS': 'Facturación CCEE VITHAS',
            'Facturación CCEE OSA (80%)': 'Facturación CCEE OSA (80%)',
            'No. De Pacientes CCEE': 'No. De Pacientes CCEE',
            'Facturación Quirúrgico VITHAS': 'Facturación Quirúrgico VITHAS',
            'Facturación Quirúrgico OSA (90%)': 'Facturación Quirúrgico OSA (90%)',
            'Facturación Urgencias OSA (50%)': 'Facturación Urgencias OSA (50%)',
            'Facturación Urgencias VITHAS': 'Facturación Urgencias VITHAS'
        }
        
        # Verificar y ajustar nombres de columnas
        for expected_col, actual_col in column_mapping.items():
            if actual_col not in df.columns:
                # Intentar variaciones comunes
                variations = [
                    actual_col,
                    actual_col.replace("(", " (").replace("  ", " "),
                    actual_col.replace("ó", "o").replace("í", "i"),
                    actual_col.replace(" ", "_"),
                    actual_col.lower()
                ]
                
                for variation in variations:
                    if variation in df.columns:
                        column_mapping[expected_col] = variation
                        break
                else:
                    raise ValueError(f"Columna requerida no encontrada: '{actual_col}'")
        
        # Renombrar columnas a nombres estandarizados
        df.rename(columns={v: k for k, v in column_mapping.items()}, inplace=True)
        
        # Verificar que todas las columnas requeridas estén presentes
        required_columns = list(column_mapping.keys())
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Columnas requeridas no encontradas: {missing_columns}\n"
                          f"Columnas disponibles: {st.session_state.available_columns}")
        
        # Limpieza de datos
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        
        # Convertir columnas numéricas
        numeric_cols = [col for col in required_columns if col != 'Fecha']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].isnull().any():
                st.warning(f"Advertencia: La columna {col} contiene valores no numéricos")
        
        return df
    
    except Exception as e:
        st.error("❌ Error durante la carga de datos")
        st.error(str(e))
        if 'available_columns' in st.session_state:
            st.write("ℹ️ Columnas disponibles en tu archivo:")
            st.write(st.session_state.available_columns)
        return None

# Interfaz de usuario
st.title("🏥 Dashboard de Proyecciones Médicas 2026")

uploaded_file = st.file_uploader("Sube tu archivo 'Proyeccion 3.xlsx'", type=["xlsx"])

if uploaded_file:
    df = load_and_process_data(uploaded_file)
    
    if df is not None:
        try:
            # ==============================================
            # ANÁLISIS Y VISUALIZACIONES
            # ==============================================
            
            st.header("📊 Datos Cargados Correctamente")
            st.dataframe(df.head())
            
            # 1. Cálculo de métricas comparativas
            total_vithas = df['Facturación CCEE VITHAS'].sum() + \
                          df['Facturación Quirúrgico VITHAS'].sum() + \
                          df['Facturación Urgencias VITHAS'].sum()
            
            total_osa = df['Facturación CCEE OSA (80%)'].sum() + \
                        df['Facturación Quirúrgico OSA (90%)'].sum() + \
                        df['Facturación Urgencias OSA (50%)'].sum()
            
            # 2. KPIs comparativos
            st.header("📈 KPIs Comparativos VITHAS vs OSA")
            col1, col2, col3 = st.columns(3)
            col1.metric("Facturación Total VITHAS", f"€{total_vithas:,.0f}")
            col2.metric("Facturación Total OSA", f"€{total_osa:,.0f}")
            col3.metric("Diferencia", f"€{total_vithas-total_osa:,.0f}", 
                       delta=f"{(total_vithas/total_osa-1)*100:.1f}%" if total_osa > 0 else "N/A")
            
            # 3. Gráfico de evolución comparativa
            st.header("📅 Evolución Mensual por Categoría")
            fig = px.line(df, x='Fecha', 
                         y=['Facturación CCEE VITHAS', 'Facturación CCEE OSA (80%)',
                            'Facturación Quirúrgico VITHAS', 'Facturación Quirúrgico OSA (90%)',
                            'Facturación Urgencias VITHAS', 'Facturación Urgencias OSA (50%)'],
                         title="Comparación Mensual",
                         labels={'value': 'Facturación (€)', 'variable': 'Categoría'},
                         height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # 4. Gráfico de composición porcentual
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
                title="Distribución Porcentual",
                hole=0.3
            )
            st.plotly_chart(fig2, use_container_width=True)
            
        except Exception as analysis_error:
            st.error("❌ Error durante el análisis de datos")
            st.error(str(analysis_error))

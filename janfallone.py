import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Proyección VITHAS-OSA 2026", layout="wide", page_icon="🏥")

# Título
st.title("🏥 Dashboard de Proyección Médica 2026")
st.markdown("### Análisis de Facturación, Pacientes y Procedimientos")

# Carga de archivo
uploaded_file = st.file_uploader("Sube tu archivo 'Proyeccion 3.xlsx'", type="xlsx")

if uploaded_file:
    try:
        # 1. Leer datos
        df = pd.read_excel(uploaded_file, sheet_name="Proyeccion 2026")
        
        # Limpieza de datos
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Mostrar datos procesados (opcional)
        with st.expander("🔍 Ver datos procesados", expanded=False):
            st.dataframe(df)
            st.write(f"📝 Forma del dataset: {df.shape}")
            st.write("📌 Tipos de datos:", df.dtypes)
        
        # ==============================================
        # SECCIÓN DE KPIs (8 métricas clave)
        # ==============================================
        st.markdown("---")
        st.header("📈 KPIs Principales")
        
        # Fila 1 de KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_fact = df['Total Facturación'].sum()/1000
            st.metric("1. Facturación Total (M€)", f"{total_fact:,.1f}M€")
        with col2:
            avg_fact = df['Total Facturación'].mean()/1000
            st.metric("2. Facturación Mensual Promedio", f"{avg_fact:,.1f}K€")
        with col3:
            total_pacientes = df['No. De Pacientes CCEE'].sum()
            st.metric("3. Total Pacientes CCEE", f"{total_pacientes:,}")
        with col4:
            total_cirugias = df['No. De Intervenciones Quirúrgicas'].sum()
            st.metric("4. Total Intervenciones Quirúrgicas", f"{total_cirugias:,}")
        
        # Fila 2 de KPIs
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            total_urgencias = df['No. Urgencias Mes'].sum()
            st.metric("5. Total Urgencias", f"{total_urgencias:,}")
        with col6:
            modulos_dia = df['Módulos Totales x día'].mean()
            st.metric("6. Módulos Diarios Promedio", f"{modulos_dia:.1f}")
        with col7:
            precio_medio_consulta = df['Precio Medio Consultas CCEE'].mean()
            st.metric("7. Precio Medio Consulta (€)", f"{precio_medio_consulta:.2f}€")
        with col8:
            precio_medio_cirugia = df['Precio Medio HHMM Quirúrgicas'].mean()
            st.metric("8. Precio Medio Cirugía (€)", f"{precio_medio_cirugia:,.0f}€")
        
        # ==============================================
        # SECCIÓN DE GRÁFICOS (8 visualizaciones)
        # ==============================================
        st.markdown("---")
        st.header("📊 Visualizaciones")
        
        # Gráfico 1: Evolución mensual de facturación
        fig1 = px.line(df, x='Fecha', y=['Total Facturación', 'Facturación CCEE VITHAS', 
                                       'Facturación Quirúrgico VITHAS', 'Facturación Urgencias VITHAS'],
                     title="1. Evolución Mensual de Facturación (€)",
                     labels={'value': 'Facturación (€)', 'variable': 'Tipo'},
                     height=500)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico 2: Comparación VITHAS vs OSA
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df['Fecha'], y=df['Facturación CCEE VITHAS'], name='CCEE VITHAS'))
        fig2.add_trace(go.Bar(x=df['Fecha'], y=df['Facturación CCEE OSA (80%)'], name='CCEE OSA (80%)'))
        fig2.add_trace(go.Bar(x=df['Fecha'], y=df['Facturación Quirúrgico VITHAS'], name='Quirúrgico VITHAS'))
        fig2.add_trace(go.Bar(x=df['Fecha'], y=df['Facturación Quirúrgico OSA (90%)'], name='Quirúrgico OSA (90%)'))
        fig2.update_layout(barmode='group', title='2. Comparación Facturación VITHAS vs OSA',
                          yaxis_title='Facturación (€)')
        st.plotly_chart(fig2, use_container_width=True)
        
        # Gráfico 3: Pacientes vs Módulos
        fig3 = px.scatter(df, x='No. De Pacientes CCEE', y='Módulos Totales x día',
                         size='Pacientes x Módulo (Cada 15 min)', color='Módulos Totales x día',
                         title="3. Relación Pacientes vs Módulos Diarios",
                         labels={'No. De Pacientes CCEE': 'N° Pacientes', 'Módulos Totales x día': 'Módulos/Día'})
        st.plotly_chart(fig3, use_container_width=True)
        
        # Gráfico 4: Distribución de urgencias
        fig4 = px.bar(df, x='Fecha', y=['Urgencias días Trauma (15%)', 'Urgencias días totales Vitha'],
                     title="4. Distribución de Urgencias por Tipo",
                     labels={'value': 'N° Urgencias', 'variable': 'Tipo'})
        st.plotly_chart(fig4, use_container_width=True)
        
        # Gráfico 5: Composición de facturación
        fact_composicion = df[['Facturación CCEE VITHAS', 'Facturación Quirúrgico VITHAS', 
                             'Facturación Urgencias VITHAS']].sum()
        fig5 = px.pie(values=fact_composicion, names=fact_composicion.index,
                     title="5. Composición de Facturación VITHAS",
                     hole=0.4)
        st.plotly_chart(fig5, use_container_width=True)
        
        # Gráfico 6: Correlaciones entre variables
        numeric_df = df.select_dtypes(include=['number'])
        corr = numeric_df.corr()
        fig6 = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale='Blues',
            zmin=-1,
            zmax=1
        ))
        fig6.update_layout(title="6. Correlación entre Variables Numéricas",
                          height=600)
        st.plotly_chart(fig6, use_container_width=True)
        
        # Gráfico 7: Precios medios comparativos
        fig7 = go.Figure()
        fig7.add_trace(go.Scatter(x=df['Fecha'], y=df['Precio Medio Consultas CCEE'], 
                                name='Consulta', line=dict(color='green')))
        fig7.add_trace(go.Scatter(x=df['Fecha'], y=df['Precio Medio HHMM Quirúrgicas'], 
                                name='Cirugía', line=dict(color='blue')))
        fig7.add_trace(go.Scatter(x=df['Fecha'], y=df['Precio Medio Urgencias'], 
                                name='Urgencia', line=dict(color='red')))
        fig7.update_layout(title="7. Evolución de Precios Medios (€)",
                         yaxis_title="Precio (€)")
        st.plotly_chart(fig7, use_container_width=True)
        
        # Gráfico 8: Módulos por turno
        fig8 = px.area(df, x='Fecha', y=['Módulos Mañana', 'Módulos Tarde'],
                      title="8. Distribución de Módulos por Turno",
                      labels={'value': 'N° Módulos', 'variable': 'Turno'})
        st.plotly_chart(fig8, use_container_width=True)
        
        # ==============================================
        # SECCIÓN DE ANÁLISIS ADICIONAL
        # ==============================================
        st.markdown("---")
        st.header("📌 Resumen Ejecutivo")
        
        with st.expander("🔎 Conclusiones Clave"):
            st.write(f"""
            - **Facturación Total Proyectada**: {total_fact:,.1f} millones de euros
            - **Promedio Mensual**: {avg_fact:,.1f} mil euros
            - **Capacidad de Atención**: 
                - {total_pacientes:,} pacientes en consultas externas
                - {total_cirugias:,} intervenciones quirúrgicas
                - {total_urgencias:,} atenciones de urgencia
            - **Distribución Facturación**:
                - Consultas: {(fact_composicion[0]/total_fact/1000)*100:.1f}%
                - Quirúrgico: {(fact_composicion[1]/total_fact/1000)*100:.1f}%
                - Urgencias: {(fact_composicion[2]/total_fact/1000)*100:.1f}%
            """)
    
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
        st.write("ℹ️ Posibles soluciones:")
        st.write("- Verifica que el archivo tenga la hoja 'Proyeccion 2026'")
        st.write("- Asegúrate de que las fórmulas de Excel se hayan calculado")
        st.write("- Revisa que no haya celdas con errores en los datos numéricos")

else:
    st.info("ℹ️ Por favor, sube el archivo 'Proyeccion 3.xlsx' para comenzar el análisis.")

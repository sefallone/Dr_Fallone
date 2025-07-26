import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Comparativo VITHAS-OSA 2026", layout="wide", page_icon="🏥")

# Título
st.title("🏥 Dashboard Comparativo VITHAS vs OSA 2026")
st.markdown("### Análisis de Facturación y Procedimientos")

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
        
        # Cálculo de totales por entidad
        df['Total VITHAS'] = df['Facturación CCEE VITHAS'] + df['Facturación Quirúrgico VITHAS'] + df['Facturación Urgencias VITHAS']
        df['Total OSA'] = df['Facturación CCEE OSA (80%)'] + df['Facturación Quirúrgico OSA (90%)'] + df['Facturación Urgencias OSA (50%)']
        df['Diferencia'] = df['Total VITHAS'] - df['Total OSA']
        
        # Totales anuales
        total_vithas = df['Total VITHAS'].sum()
        total_osa = df['Total OSA'].sum()
        diferencia_total = total_vithas - total_osa
        proporcion = (total_vithas / total_osa) if total_osa != 0 else 0
        
        # ==============================================
        # SECCIÓN DE KPIs COMPARATIVOS
        # ==============================================
        st.markdown("---")
        st.header("📊 KPIs Comparativos VITHAS vs OSA")
        
        # Fila 1 - Totales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("1. Facturación Total VITHAS", f"€{total_vithas/1000:,.1f}K", 
                     help="Suma de CCEE + Quirúrgico + Urgencias VITHAS")
        with col2:
            st.metric("2. Facturación Total OSA", f"€{total_osa/1000:,.1f}K", 
                     help="Suma de CCEE (80%) + Quirúrgico (90%) + Urgencias (50%) OSA")
        with col3:
            st.metric("3. Diferencia Total", f"€{diferencia_total/1000:,.1f}K", 
                     delta=f"{proporcion-1:.1%}" if proporcion != 0 else None,
                     delta_color="inverse" if diferencia_total < 0 else "normal")
        
        # Fila 2 - Por categoría
        col4, col5, col6 = st.columns(3)
        with col4:
            ccee_vithas = df['Facturación CCEE VITHAS'].sum()
            ccee_osa = df['Facturación CCEE OSA (80%)'].sum()
            st.metric("4. Consultas Externas", 
                     f"VITHAS: €{ccee_vithas/1000:,.1f}K | OSA: €{ccee_osa/1000:,.1f}K",
                     delta=f"{(ccee_vithas/ccee_osa-1):.1%}" if ccee_osa != 0 else None)
        with col5:
            quir_vithas = df['Facturación Quirúrgico VITHAS'].sum()
            quir_osa = df['Facturación Quirúrgico OSA (90%)'].sum()
            st.metric("5. Quirúrgico", 
                     f"VITHAS: €{quir_vithas/1000:,.1f}K | OSA: €{quir_osa/1000:,.1f}K",
                     delta=f"{(quir_vithas/quir_osa-1):.1%}" if quir_osa != 0 else None)
        with col6:
            urg_vithas = df['Facturación Urgencias VITHAS'].sum()
            urg_osa = df['Facturación Urgencias OSA (50%)'].sum()
            st.metric("6. Urgencias", 
                     f"VITHAS: €{urg_vithas/1000:,.1f}K | OSA: €{urg_osa/1000:,.1f}K",
                     delta=f"{(urg_vithas/urg_osa-1):.1%}" if urg_osa != 0 else None)
        
        # ==============================================
        # SECCIÓN DE GRÁFICOS COMPARATIVOS
        # ==============================================
        st.markdown("---")
        st.header("📈 Análisis Visual Comparativo")
        
        # Gráfico 1: Comparación mensual total
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df['Fecha'], y=df['Total VITHAS'], name='VITHAS'))
        fig1.add_trace(go.Bar(x=df['Fecha'], y=df['Total OSA'], name='OSA'))
        fig1.add_trace(go.Scatter(x=df['Fecha'], y=df['Diferencia'], name='Diferencia', 
                                mode='lines+markers', line=dict(color='red')))
        fig1.update_layout(barmode='group', title='1. Comparación Mensual VITHAS vs OSA',
                         yaxis_title='Facturación (€)')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico 2: Composición por entidad
        fig2 = px.sunburst(
            pd.DataFrame({
                'Entidad': ['VITHAS', 'VITHAS', 'VITHAS', 'OSA', 'OSA', 'OSA'],
                'Categoría': ['Consultas', 'Quirúrgico', 'Urgencias']*2,
                'Valor': [ccee_vithas, quir_vithas, urg_vithas, ccee_osa, quir_osa, urg_osa]
            }),
            path=['Entidad', 'Categoría'],
            values='Valor',
            title='2. Composición de Facturación por Entidad'
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Gráfico 3: Evolución de la diferencia
        fig3 = px.area(df, x='Fecha', y='Diferencia',
                      title="3. Evolución de la Diferencia (VITHAS - OSA)",
                      labels={'Diferencia': 'Diferencia (€)'})
        fig3.add_hline(y=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig3, use_container_width=True)
        
        # Gráfico 4: Porcentaje por categoría
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=['Consultas', 'Quirúrgico', 'Urgencias'],
            y=[ccee_vithas/ccee_osa*100 if ccee_osa !=0 else 0, 
               quir_vithas/quir_osa*100 if quir_osa !=0 else 0, 
               urg_vithas/urg_osa*100 if urg_osa !=0 else 0],
            name='VITHAS como % de OSA'
        ))
        fig4.update_layout(
            title='4. VITHAS como Porcentaje de OSA por Categoría',
            yaxis_title='Porcentaje (%)',
            annotations=[
                dict(x=xi, y=yi+5, text=f"{yi:.1f}%", showarrow=False)
                for xi, yi in zip(['Consultas', 'Quirúrgico', 'Urgencias'],
                                [ccee_vithas/ccee_osa*100 if ccee_osa !=0 else 0, 
                                 quir_vithas/quir_osa*100 if quir_osa !=0 else 0, 
                                 urg_vithas/urg_osa*100 if urg_osa !=0 else 0])
            ]
        )
        st.plotly_chart(fig4, use_container_width=True)
        
        # ==============================================
        # TABLA RESUMEN COMPARATIVO
        # ==============================================
        st.markdown("---")
        st.header("📋 Resumen Comparativo Anual")
        
        summary_df = pd.DataFrame({
            'Categoría': ['Consultas Externas', 'Quirúrgico', 'Urgencias', 'TOTAL'],
            'VITHAS (€)': [ccee_vithas, quir_vithas, urg_vithas, total_vithas],
            'OSA (€)': [ccee_osa, quir_osa, urg_osa, total_osa],
            'Diferencia (€)': [ccee_vithas-ccee_osa, quir_vithas-quir_osa, urg_vithas-urg_osa, diferencia_total],
            'VITHAS/OSA': [f"{ccee_vithas/ccee_osa:.1%}" if ccee_osa !=0 else 'N/A',
                          f"{quir_vithas/quir_osa:.1%}" if quir_osa !=0 else 'N/A',
                          f"{urg_vithas/urg_osa:.1%}" if urg_osa !=0 else 'N/A',
                          f"{proporcion:.1%}" if proporcion !=0 else 'N/A']
        })
        
        # Formatear números
        for col in ['VITHAS (€)', 'OSA (€)', 'Diferencia (€)']:
            summary_df[col] = summary_df[col].apply(lambda x: f"€{x:,.0f}")
        
        st.dataframe(summary_df, hide_index=True, use_container_width=True)
        
        # ==============================================
        # ANÁLISIS COMPARATIVO
        # ==============================================
        st.markdown("---")
        st.header("📌 Conclusiones Clave")
        
        with st.expander("🔎 Ver análisis detallado", expanded=True):
            st.write(f"""
            **1. Balance Total:**
            - VITHAS factura €{total_vithas/1000:,.1f}K vs €{total_osa/1000:,.1f}K de OSA
            - Diferencia a favor de VITHAS: €{diferencia_total/1000:,.1f}K ({proporcion:.1%} del total OSA)
            
            **2. Por Categoría:**
            - **Consultas:** VITHAS ({ccee_vithas/1000:,.1f}K) vs OSA ({ccee_osa/1000:,.1f}K) | Relación 80% esperada
            - **Quirúrgico:** VITHAS ({quir_vithas/1000:,.1f}K) vs OSA ({quir_osa/1000:,.1f}K) | Relación 90% esperada
            - **Urgencias:** VITHAS ({urg_vithas/1000:,.1f}K) vs OSA ({urg_osa/1000:,.1f}K) | Relación 50% esperada
            
            **3. Tendencia Mensual:**
            - La diferencia es más pronunciada en {df.loc[df['Diferencia'].idxmax(), 'Fecha'].strftime('%B')} (€{df['Diferencia'].max()/1000:,.1f}K)
            - Menor diferencia en {df.loc[df['Diferencia'].idxmin(), 'Fecha'].strftime('%B')} (€{df['Diferencia'].min()/1000:,.1f}K)
            """)
    
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
        st.write("ℹ️ Posibles soluciones:")
        st.write("- Verifica que el archivo tenga la hoja 'Proyeccion 2026'")
        st.write("- Asegúrate de que las fórmulas de Excel se hayan calculado")
        st.write("- Revisa que no haya celdas con errores en los datos numéricos")

else:
    st.info("ℹ️ Por favor, sube el archivo 'Proyeccion 3.xlsx' para comenzar el análisis.")

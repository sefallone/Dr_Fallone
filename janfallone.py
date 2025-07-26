import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Dashboard Avanzado", layout="wide", page_icon="📊")

# Título
st.title("📊 Dashboard Analítico Avanzado")

# Carga de archivo
uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type="xlsx")

if uploaded_file:
    try:
        # 1. Leer y transponer datos
        df = pd.read_excel(uploaded_file, header=None)
        df_transposed = df.T
        df_clean = df_transposed.rename(columns=df_transposed.iloc[0]).drop(index=df_transposed.index[0])
        
        # 2. Limpieza y conversión de datos
        # Convertir posibles columnas numéricas
        for col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='ignore')
        
        # Convertir fechas si existen
        date_cols = [col for col in df_clean.columns if 'fecha' in col.lower() or 'date' in col.lower()]
        for col in date_cols:
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
        
        # 3. Mostrar datos procesados (opcional)
        with st.expander("🔍 Ver datos procesados", expanded=False):
            st.dataframe(df_clean)
            st.write(f"📝 Forma del dataset: {df_clean.shape}")
            st.write("📌 Tipos de datos:", df_clean.dtypes)
        
        # ==============================================
        # SECCIÓN DE KPIs (8 métricas)
        # ==============================================
        st.markdown("---")
        st.header("📈 KPIs Principales")
        
        # Crear 4 filas con 2 KPIs cada una (total 8)
        for i in range(4):
            cols = st.columns(2)
            with cols[0]:
                if i == 0 and 'Ventas' in df_clean.columns:
                    ventas_totales = df_clean['Ventas'].sum()
                    st.metric("1. Ventas Totales", f"${ventas_totales:,.0f}", 
                             help="Suma acumulada de todas las ventas")
                
                elif i == 1 and 'Ganancia' in df_clean.columns:
                    ganancia_total = df_clean['Ganancia'].sum()
                    st.metric("3. Ganancia Total", f"${ganancia_total:,.0f}", 
                             delta=f"{ganancia_total/ventas_totales:.1%} margen" if 'ventas_totales' in locals() else None)
                
                elif i == 2 and 'Clientes' in df_clean.columns:
                    clientes_unicos = df_clean['Clientes'].nunique()
                    st.metric("5. Clientes Únicos", f"{clientes_unicos:,}")
                
                elif i == 3 and 'Costo' in df_clean.columns:
                    costo_promedio = df_clean['Costo'].mean()
                    st.metric("7. Costo Promedio", f"${costo_promedio:,.2f}")
            
            with cols[1]:
                if i == 0 and 'Ventas' in df_clean.columns:
                    ventas_promedio = df_clean['Ventas'].mean()
                    st.metric("2. Ventas Promedio", f"${ventas_promedio:,.2f}")
                
                elif i == 1 and 'Unidades' in df_clean.columns:
                    unidades_vendidas = df_clean['Unidades'].sum()
                    st.metric("4. Unidades Vendidas", f"{unidades_vendidas:,}")
                
                elif i == 2 and 'Ventas' in df_clean.columns and len(df_clean) > 1:
                    crecimiento = (df_clean['Ventas'].iloc[-1] - df_clean['Ventas'].iloc[0]) / df_clean['Ventas'].iloc[0]
                    st.metric("6. Crecimiento Ventas", f"{crecimiento:.1%}")
                
                elif i == 3 and 'Rating' in df_clean.columns:
                    rating_promedio = df_clean['Rating'].mean()
                    st.metric("8. Satisfacción Cliente", f"{rating_promedio:.1f}/5")
        
        # ==============================================
        # SECCIÓN DE GRÁFICOS (8 visualizaciones)
        # ==============================================
        st.markdown("---")
        st.header("📊 Visualizaciones")
        
        # Gráfico 1: Ventas por categoría (Barras)
        if 'Categoría' in df_clean.columns and 'Ventas' in df_clean.columns:
            fig1 = px.bar(df_clean, x='Categoría', y='Ventas', 
                         title="1. Ventas por Categoría", color='Categoría')
            st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico 2: Serie temporal de ventas (Línea)
        if 'Fecha' in df_clean.columns and 'Ventas' in df_clean.columns:
            fig2 = px.line(df_clean, x='Fecha', y='Ventas', 
                          title="2. Tendencia de Ventas",
                          markers=True)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Gráfico 3: Distribución de ventas (Histograma)
        if 'Ventas' in df_clean.columns:
            fig3 = px.histogram(df_clean, x='Ventas', 
                              title="3. Distribución de Ventas",
                              nbins=20)
            st.plotly_chart(fig3, use_container_width=True)
        
        # Gráfico 4: Relación ventas vs. ganancia (Dispersión)
        if 'Ventas' in df_clean.columns and 'Ganancia' in df_clean.columns:
            fig4 = px.scatter(df_clean, x='Ventas', y='Ganancia',
                            title="4. Ventas vs. Ganancia",
                            trendline="ols")
            st.plotly_chart(fig4, use_container_width=True)
        
        # Gráfico 5: Composición de ventas (Pie)
        if 'Categoría' in df_clean.columns and 'Ventas' in df_clean.columns:
            fig5 = px.pie(df_clean, names='Categoría', values='Ventas',
                         title="5. Composición de Ventas por Categoría")
            st.plotly_chart(fig5, use_container_width=True)
        
        # Gráfico 6: Mapa de calor de correlaciones
        numeric_df = df_clean.select_dtypes(include=['number'])
        if len(numeric_df.columns) > 1:
            corr = numeric_df.corr()
            fig6 = go.Figure(data=go.Heatmap(
                z=corr.values,
                x=corr.columns,
                y=corr.columns,
                colorscale='Blues',
                zmin=-1,
                zmax=1
            ))
            fig6.update_layout(title="6. Correlación entre Variables Numéricas")
            st.plotly_chart(fig6, use_container_width=True)
        
        # Gráfico 7: Boxplot de ventas por categoría
        if 'Categoría' in df_clean.columns and 'Ventas' in df_clean.columns:
            fig7 = px.box(df_clean, x='Categoría', y='Ventas',
                         title="7. Distribución de Ventas por Categoría")
            st.plotly_chart(fig7, use_container_width=True)
        
        # Gráfico 8: Gráfico de áreas apiladas
        if 'Fecha' in df_clean.columns and 'Categoría' in df_clean.columns and 'Ventas' in df_clean.columns:
            pivot_df = df_clean.pivot_table(index='Fecha', columns='Categoría', values='Ventas', aggfunc='sum').fillna(0)
            fig8 = px.area(pivot_df, 
                          title="8. Ventas Acumuladas por Categoría")
            st.plotly_chart(fig8, use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
        st.write("ℹ️ Posibles soluciones:")
        st.write("- Verifica que el archivo tenga la estructura correcta")
        st.write("- Asegúrate de que los nombres de columnas coincidan exactamente")
        st.write("- Revisa que los datos numéricos no contengan caracteres no válidos")

else:
    st.info("ℹ️ Por favor, sube un archivo Excel para comenzar el análisis.")
    st.markdown("### 📌 Estructura recomendada:")
    st.write("- Los encabezados deben estar en la primera fila")
    st.write("- Los datos deben estar organizados en columnas")
    st.write("- Las fechas deben estar en formato reconocible (YYYY-MM-DD)")

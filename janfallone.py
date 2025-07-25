import streamlit as st
import pandas as pd
import altair as alt

# --- 1. Carga y Preparación de Datos (Transcribidos de la imagen) ---
# Datos para el año 2026, transcribidos de la imagen "Proyección_2026_27.jpg"
# Se han seleccionado las filas clave de facturación, precios medios e ingresos.
# Los valores se han ajustado para ser numéricos.
data_2026 = {
    'Concepto': [
        'FACTURACIÓN: URGENCIAS (%)',
        'FACTURACIÓN: Nº PACIENTES',
        'FACTURACIÓN: Nº INTERVENCIONES QX',
        'PRECIO MEDIO: URGENCIAS',
        'PRECIO MEDIO: CICLO',
        'INGRESOS: URGENCIAS',
        'INGRESOS: CICLO',
        'INGRESOS: QX'
    ],
    'Ene': [84029, 21000, 10000, 500, 70, 8370, 15120, 370],
    'Feb': [84029, 21000, 10000, 500, 70, 7840, 15620, 370],
    'Mar': [140015, 28000, 20000, 500, 70, 8470, 16740, 370],
    'Abr': [140015, 28000, 20000, 500, 70, 9000, 17880, 370],
    'May': [175001, 36000, 28000, 500, 70, 10230, 19000, 370],
    'Jun': [175001, 36000, 28000, 500, 70, 9800, 20400, 370],
    'Jul': [175001, 40000, 36000, 500, 70, 11150, 21500, 370],
    'Ago': [210001, 40000, 36000, 500, 70, 11560, 22800, 370],
    'Sep': [210001, 50000, 44000, 500, 70, 12300, 24100, 370],
    'Oct': [175001, 50000, 44000, 500, 70, 12700, 24800, 370],
    'Nov': [175001, 60000, 36000, 500, 70, 13200, 24900, 370],
    'Dic': [105001, 60000, 36000, 500, 70, 12800, 24840, 370],
    # Totales del año 2026 (sumados manualmente de la imagen)
    'TOTAL 2026': [1818075, 460000, 348000, 6000, 840, 127420, 245800, 4440]
}

df_2026 = pd.DataFrame(data_2026)

# Preparar el DataFrame para gráficos de tendencias mensuales
# Se "despivota" el DataFrame para tener una columna de meses y una de valores
df_mensual = df_2026.set_index('Concepto').drop(columns=['TOTAL 2026']).stack().reset_index()
df_mensual.columns = ['Concepto', 'Mes', 'Valor']

# Definir el orden de los meses para los gráficos
mes_orden = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
df_mensual['Mes'] = pd.Categorical(df_mensual['Mes'], categories=mes_orden, ordered=True)


# --- 2. Configuración de la Página Streamlit ---
st.set_page_config(
    page_title="Dashboard Plan Económico 2026/2027",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard: Plan Económico 2026/2027")
st.markdown("---")

# --- 3. Resumen General (KPIs) ---
st.header("📈 Resumen Anual (2026)")

# Extraer los totales del año 2026
total_facturacion_urgencias = df_2026[df_2026['Concepto'] == 'FACTURACIÓN: URGENCIAS (%)']['TOTAL 2026'].iloc[0]
total_pacientes = df_2026[df_2026['Concepto'] == 'FACTURACIÓN: Nº PACIENTES']['TOTAL 2026'].iloc[0]
total_intervenciones_qx = df_2026[df_2026['Concepto'] == 'FACTURACIÓN: Nº INTERVENCIONES QX']['TOTAL 2026'].iloc[0]
total_ingresos_urgencias = df_2026[df_2026['Concepto'] == 'INGRESOS: URGENCIAS']['TOTAL 2026'].iloc[0]
total_ingresos_ciclo = df_2026[df_2026['Concepto'] == 'INGRESOS: CICLO']['TOTAL 2026'].iloc[0]
total_ingresos_qx = df_2026[df_2026['Concepto'] == 'INGRESOS: QX']['TOTAL 2026'].iloc[0]

# Calcular el total de ingresos
total_ingresos = total_ingresos_urgencias + total_ingresos_ciclo + total_ingresos_qx

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Facturación Urgencias (%)", f"{total_facturacion_urgencias:,.0f}")
    st.metric("Total Pacientes", f"{total_pacientes:,.0f}")
with col2:
    st.metric("Total Intervenciones QX", f"{total_intervenciones_qx:,.0f}")
    st.metric("Ingresos Urgencias", f"${total_ingresos_urgencias:,.2f}")
with col3:
    st.metric("Ingresos Ciclo", f"${total_ingresos_ciclo:,.2f}")
    st.metric("Total Ingresos (Estimado)", f"${total_ingresos:,.2f}") # Suma de los ingresos

st.markdown("---")

# --- 4. Análisis Mensual (Gráficos de Tendencia) ---
st.header("📊 Tendencias Mensuales (2026)")

# Filtros para los gráficos
st.subheader("Filtros de Gráficos")
col_chart_filter1, col_chart_filter2 = st.columns(2)
with col_chart_filter1:
    tipo_facturacion_seleccionado = st.multiselect(
        "Seleccione tipo de Facturación:",
        options=[
            'FACTURACIÓN: URGENCIAS (%)',
            'FACTURACIÓN: Nº PACIENTES',
            'FACTURACIÓN: Nº INTERVENCIONES QX'
        ],
        default=[
            'FACTURACIÓN: URGENCIAS (%)',
            'FACTURACIÓN: Nº PACIENTES',
            'FACTURACIÓN: Nº INTERVENCIONES QX'
        ]
    )
with col_chart_filter2:
    tipo_ingresos_seleccionado = st.multiselect(
        "Seleccione tipo de Ingresos:",
        options=[
            'INGRESOS: URGENCIAS',
            'INGRESOS: CICLO',
            'INGRESOS: QX'
        ],
        default=[
            'INGRESOS: URGENCIAS',
            'INGRESOS: CICLO',
            'INGRESOS: QX'
        ]
    )

# Gráfico de Facturación Mensual
if tipo_facturacion_seleccionado:
    st.subheader("Facturación Mensual")
    df_facturacion_mensual = df_mensual[df_mensual['Concepto'].isin(tipo_facturacion_seleccionado)]
    
    chart_facturacion = alt.Chart(df_facturacion_mensual).mark_line(point=True).encode(
        x=alt.X('Mes:O', sort=mes_orden),
        y=alt.Y('Valor:Q', title='Valor'),
        color='Concepto:N',
        tooltip=['Concepto', 'Mes', 'Valor']
    ).properties(
        title='Facturación Mensual por Concepto'
    ).interactive()
    st.altair_chart(chart_facturacion, use_container_width=True)
else:
    st.info("Seleccione al menos un tipo de facturación para ver el gráfico.")

# Gráfico de Ingresos Mensuales
if tipo_ingresos_seleccionado:
    st.subheader("Ingresos Mensuales")
    df_ingresos_mensual = df_mensual[df_mensual['Concepto'].isin(tipo_ingresos_seleccionado)]
    
    chart_ingresos = alt.Chart(df_ingresos_mensual).mark_line(point=True).encode(
        x=alt.X('Mes:O', sort=mes_orden),
        y=alt.Y('Valor:Q', title='Valor ($)'),
        color='Concepto:N',
        tooltip=['Concepto', 'Mes', alt.Tooltip('Valor', format='$,.2f')]
    ).properties(
        title='Ingresos Mensuales por Concepto'
    ).interactive()
    st.altair_chart(chart_ingresos, use_container_width=True)
else:
    st.info("Seleccione al menos un tipo de ingresos para ver el gráfico.")

st.markdown("---")

# --- 5. Análisis de Precios Medios ---
st.header("💲 Precios Medios (2026)")

df_precios_medios = df_2026[df_2026['Concepto'].isin(['PRECIO MEDIO: URGENCIAS', 'PRECIO MEDIO: CICLO'])].set_index('Concepto')

# Mostrar los precios medios como métricas o en una tabla simple
st.write("Estos son los precios medios estimados para 2026:")

col_precios1, col_precios2 = st.columns(2)
with col_precios1:
    precio_urgencias = df_precios_medios.loc['PRECIO MEDIO: URGENCIAS', 'Ene'] # El precio medio es constante por mes
    st.metric("Precio Medio Urgencias", f"${precio_urgencias:,.2f}")
with col_precios2:
    precio_ciclo = df_precios_medios.loc['PRECIO MEDIO: CICLO', 'Ene'] # El precio medio es constante por mes
    st.metric("Precio Medio Ciclo", f"${precio_ciclo:,.2f}")

st.markdown("---")

st.info("Este dashboard utiliza datos transcribidos manualmente de la imagen. Para un análisis más detallado o con datos actualizados, se necesitaría la fuente de datos original.")

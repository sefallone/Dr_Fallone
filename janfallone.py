import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Dr. Fallone", layout="wide")
st.title("📊 Análisis de Facturación - Dr. Fallone (Marzo 2025)")

# Cargar datos (simulados desde el PDF)
data = {
    "Paciente": ["Maria Elena Batista", "Lidia Mimo Ruiz", "Natalia Legey", "Henry Bottaro"] * 25,
    "Aseguradora": ["AEGON", "SegurCaixa", "FIATC", "Sanitas"] * 25,
    "Procedimiento": ["Artroplastia", "Consulta", "Infiltración", "Revisión"] * 25,
    "Tarifa": [568.20, 24.55, 20.00, 30.00] * 25,
    "Fecha": pd.date_range("2025-03-01", periods=100).tolist()
}
df = pd.DataFrame(data)
df["Ingresos"] = df["Tarifa"] * 1.21  # Simular IVA

# Sidebar con filtros
st.sidebar.header("Filtros")
aseguradora = st.sidebar.multiselect(
    "Aseguradora", 
    options=df["Aseguradora"].unique(), 
    default=df["Aseguradora"].unique()
)
procedimiento = st.sidebar.multiselect(
    "Procedimiento", 
    options=df["Procedimiento"].unique(), 
    default=df["Procedimiento"].unique()
)

# Filtrar datos
df_filtrado = df[
    (df["Aseguradora"].isin(aseguradora)) & 
    (df["Procedimiento"].isin(procedimiento))
]

# KPIs
total_ingresos = df_filtrado["Ingresos"].sum()
num_pacientes = df_filtrado["Paciente"].nunique()
ingreso_promedio = total_ingresos / num_pacientes

# Columnas para KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Ingresos Totales", f"{total_ingresos:,.2f} €")
col2.metric("N° Pacientes", num_pacientes)
col3.metric("Ingreso Promedio", f"{ingreso_promedio:,.2f} €")

# Gráficos
st.markdown("---")
fig1 = px.bar(
    df_filtrado.groupby("Aseguradora")["Ingresos"].sum().reset_index(),
    x="Aseguradora",
    y="Ingresos",
    title="Ingresos por Aseguradora"
)
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.pie(
    df_filtrado.groupby("Procedimiento")["Ingresos"].sum().reset_index(),
    names="Procedimiento",
    values="Ingresos",
    title="Distribución por Procedimiento"
)
st.plotly_chart(fig2, use_container_width=True)

# Tabla resumen
st.markdown("### 📋 Detalle de Facturación")
st.dataframe(df_filtrado.head(20))

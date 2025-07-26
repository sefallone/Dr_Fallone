import streamlit as st

st.set_page_config(page_title="Distribución de Facturación", layout="centered")

# Título
st.title("💰 Dashboard de Distribución de Facturación")
st.markdown("Ingrese los valores de facturación para calcular la distribución entre **VITHAS** y **OSA**.")

# Inputs del usuario
facturacion_ccee = st.number_input("Total Facturación CCEE (€)", min_value=0.0, step=100.0, format="%.2f")
facturacion_quirurgico = st.number_input("Total Facturación Quirúrgico (€)", min_value=0.0, step=100.0, format="%.2f")
facturacion_urgencias = st.number_input("Total Facturación Urgencias (€)", min_value=0.0, step=100.0, format="%.2f")

# Cálculos
vithas_ccee = facturacion_ccee * 0.20
vithas_quirurgico = facturacion_quirurgico * 0.10
vithas_urgencias = facturacion_urgencias * 0.50

vithas_total = vithas_ccee + vithas_quirurgico + vithas_urgencias
total_facturacion = facturacion_ccee + facturacion_quirurgico + facturacion_urgencias
osa_total = total_facturacion - vithas_total

# Resultados
st.subheader("📊 Distribución")

col1, col2 = st.columns(2)
with col1:
    st.metric("💙 VITHAS", f"{vithas_total:,.2f} €")
    st.text(f"CCEE: {vithas_ccee:,.2f} €")
    st.text(f"Quirúrgico: {vithas_quirurgico:,.2f} €")
    st.text(f"Urgencias: {vithas_urgencias:,.2f} €")

with col2:
    st.metric("🟦 OSA", f"{osa_total:,.2f} €")
    st.text(f"Diferencia respecto a VITHAS")

# Pie chart
import plotly.express as px

fig = px.pie(
    names=["VITHAS", "OSA"],
    values=[vithas_total, osa_total],
    title="Distribución Total entre VITHAS y OSA",
    color_discrete_sequence=["#2980b9", "#27ae60"]
)
st.plotly_chart(fig)

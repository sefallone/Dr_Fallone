import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Distribución de Facturación", layout="centered")

# --- ENTRADA DE DATOS ---
st.title("💰 Dashboard de Distribución de Facturación")
st.markdown("Distribuye la facturación entre **VITHAS**, **OSA** y sus socios.")

facturacion_ccee = st.number_input("Total Facturación CCEE (€)", min_value=0.0, step=100.0, format="%.2f")
facturacion_quirurgico = st.number_input("Total Facturación Quirúrgico (€)", min_value=0.0, step=100.0, format="%.2f")
facturacion_urgencias = st.number_input("Total Facturación Urgencias (€)", min_value=0.0, step=100.0, format="%.2f")

# --- CÁLCULOS VITHAS ---
vithas_ccee = facturacion_ccee * 0.20
vithas_quirurgico = facturacion_quirurgico * 0.10
vithas_urgencias = facturacion_urgencias * 0.50
vithas_total = vithas_ccee + vithas_quirurgico + vithas_urgencias

# --- TOTAL FACTURACIÓN ---
total_facturacion = facturacion_ccee + facturacion_quirurgico + facturacion_urgencias
osa_total = total_facturacion - vithas_total

# --- CONTROL SOBRE PORCENTAJE PERSONAL EN OSA ---
st.subheader("⚙️ Reparto Interno en OSA")
mi_porcentaje = st.slider("¿Qué porcentaje de OSA te quieres quedar tú?", min_value=0, max_value=100, value=50, step=1)

# Cálculo de reparto
mi_parte_osa = osa_total * (mi_porcentaje / 100)
resto_osa = osa_total - mi_parte_osa
osb = smob = jpp = resto_osa / 3

# --- RESULTADOS ---
st.subheader("📊 Resultados de Distribución")

col1, col2 = st.columns(2)
with col1:
    st.metric("💙 VITHAS", f"{vithas_total:,.2f} €")
    st.text(f"CCEE: {vithas_ccee:,.2f} €")
    st.text(f"Quirúrgico: {vithas_quirurgico:,.2f} €")
    st.text(f"Urgencias: {vithas_urgencias:,.2f} €")

with col2:
    st.metric("🟦 OSA", f"{osa_total:,.2f} €")
    st.text(f"Tú: {mi_parte_osa:,.2f} € ({mi_porcentaje}%)")
    st.text(f"OSB: {osb:,.2f} €")
    st.text(f"SMOB: {smob:,.2f} €")
    st.text(f"JPP: {jpp:,.2f} €")

# --- GRÁFICO GLOBAL ---
st.subheader("📉 Distribución Global")
fig = px.pie(
    names=["VITHAS", "Tú", "OSB", "SMOB", "JPP"],
    values=[vithas_total, mi_parte_osa, osb, smob, jpp],
    title="Distribución General de Facturación",
    color_discrete_sequence=["#3498db", "#2ecc71", "#e67e22", "#9b59b6", "#f39c12"]
)
st.plotly_chart(fig)


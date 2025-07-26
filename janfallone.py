import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Distribución de Facturación", layout="centered")

# --- ENTRADA DE DATOS ---
st.title("💰 Dashboard de Distribución de Facturación")
st.markdown("Distribuye la facturación entre **VITHAS**, **OSA** y sus socios.")

# CCEE
st.subheader("📋 Facturación CCEE")
ccee_hombro = st.number_input("🦴 Hombro y Codo - CCEE (€)", min_value=0.0, step=100.0)
ccee_rodilla = st.number_input("🦵 Rodilla - CCEE (€)", min_value=0.0, step=100.0)
ccee_pie = st.number_input("🦶 Pie - CCEE (€)", min_value=0.0, step=100.0)
facturacion_ccee = ccee_hombro + ccee_rodilla + ccee_pie

# Quirúrgico
st.subheader("🔪 Facturación Quirúrgica")
q_hombro = st.number_input("🦴 Hombro y Codo - Quirúrgico (€)", min_value=0.0, step=100.0)
q_rodilla = st.number_input("🦵 Rodilla - Quirúrgico (€)", min_value=0.0, step=100.0)
q_pie = st.number_input("🦶 Pie - Quirúrgico (€)", min_value=0.0, step=100.0)
facturacion_quirurgico = q_hombro + q_rodilla + q_pie

# Urgencias
st.subheader("🚨 Facturación Urgencias")
u_hombro = st.number_input("🦴 Hombro y Codo - Urgencias (€)", min_value=0.0, step=100.0)
u_rodilla = st.number_input("🦵 Rodilla - Urgencias (€)", min_value=0.0, step=100.0)
u_pie = st.number_input("🦶 Pie - Urgencias (€)", min_value=0.0, step=100.0)
facturacion_urgencias = u_hombro + u_rodilla + u_pie


# --- CÁLCULOS VITHAS ---
vithas_ccee = facturacion_ccee * 0.20
vithas_quirurgico = facturacion_quirurgico * 0.10
vithas_urgencias = facturacion_urgencias * 0.50
vithas_total = vithas_ccee + vithas_quirurgico + vithas_urgencias

# --- TOTAL FACTURACIÓN ---
total_facturacion = facturacion_ccee + facturacion_quirurgico + facturacion_urgencias
osa_total = total_facturacion - vithas_total

# --- CONTROL SOBRE PORCENTAJE PERSONAL EN OSA ---
# --- CONTROL SOBRE PORCENTAJE PERSONAL EN OSA ---
st.subheader("⚙️ Reparto Interno en OSA")
mi_porcentaje = st.slider("¿Qué porcentaje de OSA te quieres quedar tú?", min_value=0, max_value=100, value=50, step=1)
mi_ratio = mi_porcentaje / 100

# --- CÁLCULOS DE OSA POR ESPECIALIDAD ---
osa_total = facturacion_ccee * 0.80 + facturacion_quirurgico * 0.90 + facturacion_urgencias * 0.50

# Especialidad dentro de OSA
osa_hombro = (ccee_hombro * 0.80) + (q_hombro * 0.90) + (u_hombro * 0.50)
osa_rodilla = (ccee_rodilla * 0.80) + (q_rodilla * 0.90) + (u_rodilla * 0.50)
osa_pie = (ccee_pie * 0.80) + (q_pie * 0.90) + (u_pie * 0.50)

# Tu parte
yo_hombro = osa_hombro * mi_ratio
yo_rodilla = osa_rodilla * mi_ratio
yo_pie = osa_pie * mi_ratio

yo_total = yo_hombro + yo_rodilla + yo_pie

# Reparto restante
osb = osa_hombro - yo_hombro
smob = osa_rodilla - yo_rodilla
jpp = osa_pie - yo_pie


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


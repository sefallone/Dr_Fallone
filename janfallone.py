import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Distribución de Facturación", layout="centered")

st.title("💰 Dashboard de Distribución de Facturación")
st.markdown("Distribuye la facturación entre **VITHAS**, **OSA** y sus socios por especialidad.")

# --- ENTRADA DE DATOS POR ESPECIALIDAD Y TIPO ---
st.header("📋 Facturación por Especialidad")

# CCEE
st.subheader("🧾 Facturación CCEE")
ccee_hombro = st.number_input("🦴 Hombro y Codo - CCEE (€)", min_value=0.0, step=100.0)
ccee_rodilla = st.number_input("🦵 Rodilla - CCEE (€)", min_value=0.0, step=100.0)
ccee_pie = st.number_input("🦶 Pie - CCEE (€)", min_value=0.0, step=100.0)
facturacion_ccee = ccee_hombro + ccee_rodilla + ccee_pie

# Quirúrgico
st.subheader("🔪 Facturación Quirúrgico")
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

# --- CÁLCULO OSA ---
osa_total = facturacion_ccee * 0.80 + facturacion_quirurgico * 0.90 + facturacion_urgencias * 0.50

# Especialidad dentro de OSA
osa_hombro = (ccee_hombro * 0.80) + (q_hombro * 0.90) + (u_hombro * 0.50)
osa_rodilla = (ccee_rodilla * 0.80) + (q_rodilla * 0.90) + (u_rodilla * 0.50)
osa_pie = (ccee_pie * 0.80) + (q_pie * 0.90) + (u_pie * 0.50)

# --- REPARTO PERSONAL OSA ---
st.header("⚙️ Tu Participación en OSA")
mi_porcentaje = st.slider("¿Qué porcentaje de OSA te quieres quedar tú?", min_value=0, max_value=100, value=50, step=1)
mi_ratio = mi_porcentaje / 100

# Tu parte de OSA por especialidad
yo_hombro = osa_hombro * mi_ratio
yo_rodilla = osa_rodilla * mi_ratio
yo_pie = osa_pie * mi_ratio
yo_total = yo_hombro + yo_rodilla + yo_pie

# Reparto restante de OSA
osb = osa_hombro - yo_hombro
smob = osa_rodilla - yo_rodilla
jpp = osa_pie - yo_pie

# --- RESULTADOS VITHAS ---
st.header("📊 Resultados de Distribución")
st.subheader("💙 VITHAS")
st.metric("Total VITHAS", f"{vithas_total:,.2f} €")
st.text(f"CCEE: {vithas_ccee:,.2f} €")
st.text(f"Quirúrgico: {vithas_quirurgico:,.2f} €")
st.text(f"Urgencias: {vithas_urgencias:,.2f} €")

# --- RESULTADOS OSA DESGLOSADOS ---
st.subheader("🟦 OSA (Distribución Interna)")
col1, col2 = st.columns(2)
with col1:
    st.metric("Tú (OSA)", f"{yo_total:,.2f} € ({mi_porcentaje}%)")
    st.text(f"Hombro y Codo: {yo_hombro:,.2f} €")
    st.text(f"Rodilla: {yo_rodilla:,.2f} €")
    st.text(f"Pie y Tobillo: {yo_pie:,.2f} €")
with col2:
    st.metric("Resto distribuido", f"{osa_total - yo_total:,.2f} €")
    st.text(f"OSB (Hombro): {osb:,.2f} €")
    st.text(f"SMOB (Rodilla): {smob:,.2f} €")
    st.text(f"JPP (Pie): {jpp:,.2f} €")

# --- GRÁFICO GLOBAL ---
st.subheader("📉 Distribución Global")
fig = px.pie(
    names=["VITHAS", "Tú (OSA)", "OSB", "SMOB", "JPP"],
    values=[vithas_total, yo_total, osb, smob, jpp],
    title="Distribución General de Facturación",
    color_discrete_sequence=["#3498db", "#2ecc71", "#e67e22", "#9b59b6", "#f39c12"]
)
st.plotly_chart(fig)



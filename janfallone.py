import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Distribución de Facturación", layout="wide")

st.title("💼 Distribución de Facturación | VITHAS - OSA")

# --- INPUT DE FACTURACIÓN ---
with st.expander("📋 Ingresar Facturación por Especialidad"):
    st.subheader("💳 Facturación CCEE")
    ccee_hombro = st.number_input("Hombro y Codo (CCEE)", min_value=0.0, step=100.0)
    ccee_rodilla = st.number_input("Rodilla (CCEE)", min_value=0.0, step=100.0)
    ccee_pie = st.number_input("Pie y Tobillo (CCEE)", min_value=0.0, step=100.0)
    facturacion_ccee = ccee_hombro + ccee_rodilla + ccee_pie

    st.subheader("🔪 Facturación Quirúrgica")
    q_hombro = st.number_input("Hombro y Codo (Q)", min_value=0.0, step=100.0)
    q_rodilla = st.number_input("Rodilla (Q)", min_value=0.0, step=100.0)
    q_pie = st.number_input("Pie y Tobillo (Q)", min_value=0.0, step=100.0)
    facturacion_quirurgico = q_hombro + q_rodilla + q_pie

    st.subheader("🚨 Facturación Urgencias")
    u_hombro = st.number_input("Hombro y Codo (U)", min_value=0.0, step=100.0)
    u_rodilla = st.number_input("Rodilla (U)", min_value=0.0, step=100.0)
    u_pie = st.number_input("Pie y Tobillo (U)", min_value=0.0, step=100.0)
    facturacion_urgencias = u_hombro + u_rodilla + u_pie

# --- DISTRIBUCIONES ---
vithas_total = facturacion_ccee * 0.20 + facturacion_quirurgico * 0.10 + facturacion_urgencias * 0.50
osa_total = facturacion_ccee * 0.80 + facturacion_quirurgico * 0.90 + facturacion_urgencias * 0.50

osa_hombro = (ccee_hombro * 0.80) + (q_hombro * 0.90) + (u_hombro * 0.50)
osa_rodilla = (ccee_rodilla * 0.80) + (q_rodilla * 0.90) + (u_rodilla * 0.50)
osa_pie = (ccee_pie * 0.80) + (q_pie * 0.90) + (u_pie * 0.50)

# --- INPUT: % QUE ME QUEDO DE OSA ---
mi_porcentaje = st.slider("Selecciona tu porcentaje dentro de OSA (%)", 0, 100, 30)
mi_porcentaje_decimal = mi_porcentaje / 100

yo_hombro = osa_hombro * mi_porcentaje_decimal
yo_rodilla = osa_rodilla * mi_porcentaje_decimal
yo_pie = osa_pie * mi_porcentaje_decimal
yo_total = yo_hombro + yo_rodilla + yo_pie

# El resto de OSA se divide:
osb = osa_hombro - yo_hombro
smob = osa_rodilla - yo_rodilla
jpp = osa_pie - yo_pie

# --- PARTICION INTERNA OSA ---
osa_part1 = osa_total * 0.55
osa_part2 = osa_total * 0.225
osa_part3 = osa_total * 0.225

# --- TOTALES ---
total_facturacion = facturacion_ccee + facturacion_quirurgico + facturacion_urgencias

total_distribuciones = {
    "VITHAS": vithas_total,
    "Tú (OSA)": yo_total,
    "OSB (Hombro)": osb,
    "SMOB (Rodilla)": smob,
    "JPP (Pie)": jpp,
    "OSA Parte 1 (55%)": osa_part1,
    "OSA Parte 2 (22.5%)": osa_part2,
    "OSA Parte 3 (22.5%)": osa_part3
}

st.markdown("---")
st.header("📊 Totales de Distribución")
for k, v in total_distribuciones.items():
    st.write(f"{k}: {v:,.2f} €")

# --- GRÁFICO ---
st.markdown("---")
st.subheader("📈 Distribución Global")
fig = px.pie(
    names=list(total_distribuciones.keys()),
    values=list(total_distribuciones.values()),
    title="Distribución Total de Facturación",
    color_discrete_sequence=["#003A6F", "#2E8B57", "#1E8449", "#117A65", "#0E6655", "#566573", "#5D6D7E", "#85929E"]
)
fig.update_traces(textposition="inside", textinfo="percent+label")
st.plotly_chart(fig, use_container_width=True)





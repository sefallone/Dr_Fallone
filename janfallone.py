import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Distribución de Facturación", layout="wide")

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
    }
    .metric-container {
        background-color: #325EB8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }
    .stMetric {
        font-weight: bold;
        color: #2E4053;
    }
    .stExpander {
        background-color: #325EB8;
        border: 1px solid #E0E0E0;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("💼 Distribución de Facturación | VITHAS - OSA")

# --- INPUT DE FACTURACIÓN ---
with st.expander("📋 Ingresar Facturación por Especialidad"):
    st.subheader("💳 Facturación CCEE")
    ccee_OSB = st.number_input("Hombro y Codo (CCEE)", min_value=0.0, step=100.0)
    ccee_SMOB = st.number_input("Rodilla (CCEE)", min_value=0.0, step=100.0)
    ccee_JPP = st.number_input("Pie y Tobillo (CCEE)", min_value=0.0, step=100.0)
    facturacion_ccee = ccee_OSB + ccee_SMOB + ccee_JPP

    st.subheader("🔪 Facturación Quirúrgica")
    q_OSB = st.number_input("Hombro y Codo (Q)", min_value=0.0, step=100.0)
    q_SMOB = st.number_input("Rodilla (Q)", min_value=0.0, step=100.0)
    q_JPP = st.number_input("Pie y Tobillo (Q)", min_value=0.0, step=100.0)
    facturacion_quirurgico = q_OSB + q_SMOB + q_JPP

    st.subheader("🚨 Facturación Urgencias")
    u_OSB = st.number_input("Hombro y Codo (U)", min_value=0.0, step=100.0)
    u_SMOB = st.number_input("Rodilla (U)", min_value=0.0, step=100.0)
    u_JPP = st.number_input("Pie y Tobillo (U)", min_value=0.0, step=100.0)
    facturacion_urgencias = u_OSB + u_SMOB + u_JPP

# --- DISTRIBUCIONES ---
vithas_total = facturacion_ccee * 0.20 + facturacion_quirurgico * 0.10 + facturacion_urgencias * 0.50  # Vithas Total
osa_total = facturacion_ccee * 0.80 + facturacion_quirurgico * 0.90 + facturacion_urgencias * 0.50     # OSA Total Recibido

# --- INPUT: % QUE ME QUEDO DE OSA ---
mi_porcentaje = st.slider("Selecciona tu porcentaje dentro de OSA (%)", 0, 100, 30)
mi_porcentaje_decimal = mi_porcentaje / 100

osa_beneficios = osa_total * mi_porcentaje_decimal   # OSA Total Beneficios

osa_OSB = [(ccee_OSB * 0.80) + (q_OSB * 0.90) + (u_OSB * 0.50)] * (100 - mi_porcentaje_decimal)
osa_SMOB = [(ccee_SMOB * 0.80) + (q_SMOB * 0.90) + (u_SMOB * 0.50)] * (100 - mi_porcentaje_decimal)
osa_JPP = [(ccee_JPP * 0.80) + (q_JPP * 0.90) + (u_JPP * 0.50)] * (100 - mi_porcentaje_decimal)


# --- DISTRIBUCIÓN INTERNA DEL % PERSONAL ---
gf = osa_beneficios * 0.55
jp = osa_beneficios * 0.225
jpp_p = osa_beneficios * 0.225

# --- TOTALES ---
total_facturacion = facturacion_ccee + facturacion_quirurgico + facturacion_urgencias

total_distribuciones = {
    "VITHAS": vithas_total,
    "OSA": osa_total,
    "GF (55% de tu OSA)": gf,
    "JP (22.5% de tu OSA)": jp,
    "JPP Pers. (22.5% de tu OSA)": jpp_p,
    "OSB (Hombro)": osa_OSB,
    "SMOB (Rodilla)": osa_SMOB,
    "JPP (Pie)": osa_JPP,
    "Total CCEE": facturacion_ccee,
    "Total Quirúrgico": facturacion_quirurgico,
    "Total Urgencias": facturacion_urgencias
}

st.markdown("---")
st.header("📊 Totales de Distribución")
with st.container():
    k0, k1, k2, k3 = st.columns(4)
    with k0:
        st.metric("💰 Total Facturación", f"{total_facturacion:,.2f} €")
    with k1:
        st.metric("💙 Total VITHAS", f"{vithas_total:,.2f} €")
    with k2:
        st.metric("🟩  OSA", f"{osa_total:,.2f} €")
    with k3:
        st.metric("🔺 Total OSA BENEFICIOS", f"{osa_beneficios:,.2f} €")

with st.container():
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("CCEE", f"{facturacion_ccee:,.2f} €")
    with m2:
        st.metric("Quirúrgico", f"{facturacion_quirurgico:,.2f} €")
    with m3:
        st.metric("Urgencias", f"{facturacion_urgencias:,.2f} €")

with st.container():
    d1, d2, d3 = st.columns(3)
    with d1:
        st.success(f"OSB (Hombro): {osa_OSB:,.2f} €")
    with d2:
        st.info(f"SMOB (Rodilla): {osa_SMOB:,.2f} €")
    with d3:
        st.warning(f"JPP (Pie y Tobillo): {osa_JPP:,.2f} €")

for k, v in total_distribuciones.items():
    st.write(f"{k}: {v:,.2f} €")

# --- GRÁFICO ---
st.markdown("---")
st.subheader("📈 Distribución Global")
fig = px.pie(
    names=list(total_distribuciones.keys()),
    values=list(total_distribuciones.values()),
    title="Distribución Total de Facturación",
    color_discrete_sequence=["#003A6F", "#2E8B57", "#1ABC9C", "#F4D03F", "#E67E22", "#1E8449", "#117A65", "#0E6655", "#566573", "#5D6D7E", "#85929E"]
)
fig.update_traces(textposition="inside", textinfo="percent+label")
st.plotly_chart(fig, use_container_width=True)


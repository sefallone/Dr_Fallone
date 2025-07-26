import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Distribución de Facturación", layout="wide")

st.title("💼 Distribución de Facturación | VITHAS - OSA")

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #0E68C2;
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- INPUT DE FACTURACIÓN ---
with st.expander("📋 Ingresar Facturación por Especialidad"):
    st.subheader("💳 Facturación CCEE")
    ccee_col1, ccee_col2, ccee_col3 = st.columns(3)
    with ccee_col1:
        ccee_hombro = st.number_input("Hombro y Codo", key="ccee_h", min_value=0.0, step=100.0)
    with ccee_col2:
        ccee_rodilla = st.number_input("Rodilla", key="ccee_r", min_value=0.0, step=100.0)
    with ccee_col3:
        ccee_pie = st.number_input("Pie y Tobillo", key="ccee_p", min_value=0.0, step=100.0)
    facturacion_ccee = ccee_hombro + ccee_rodilla + ccee_pie

    st.subheader("🔪 Facturación Quirúrgica")
    q1, q2, q3 = st.columns(3)
    with q1:
        q_hombro = st.number_input("Hombro y Codo", key="q_h", min_value=0.0, step=100.0)
    with q2:
        q_rodilla = st.number_input("Rodilla", key="q_r", min_value=0.0, step=100.0)
    with q3:
        q_pie = st.number_input("Pie y Tobillo", key="q_p", min_value=0.0, step=100.0)
    facturacion_quirurgico = q_hombro + q_rodilla + q_pie

    st.subheader("🚨 Facturación Urgencias")
    u1, u2, u3 = st.columns(3)
    with u1:
        u_hombro = st.number_input("Hombro y Codo", key="u_h", min_value=0.0, step=100.0)
    with u2:
        u_rodilla = st.number_input("Rodilla", key="u_r", min_value=0.0, step=100.0)
    with u3:
        u_pie = st.number_input("Pie y Tobillo", key="u_p", min_value=0.0, step=100.0)
    facturacion_urgencias = u_hombro + u_rodilla + u_pie

# --- CÁLCULOS DE DISTRIBUCIÓN ---
vithas_ccee = facturacion_ccee * 0.20
vithas_quirurgico = facturacion_quirurgico * 0.10
vithas_urgencias = facturacion_urgencias * 0.50
vithas_total = vithas_ccee + vithas_quirurgico + vithas_urgencias

osa_total = facturacion_ccee * 0.80 + facturacion_quirurgico * 0.90 + facturacion_urgencias * 0.50

osa_hombro = (ccee_hombro * 0.80) + (q_hombro * 0.90) + (u_hombro * 0.50)
osa_rodilla = (ccee_rodilla * 0.80) + (q_rodilla * 0.90) + (u_rodilla * 0.50)
osa_pie = (ccee_pie * 0.80) + (q_pie * 0.90) + (u_pie * 0.50)

st.markdown("---")
st.header("⚙️ Distribución OSA")

mi_porcentaje = st.slider("Selecciona tu participación personal en OSA", 0, 100, 50, step=1)
mi_ratio = mi_porcentaje / 100

yo_hombro = osa_hombro * mi_ratio
yo_rodilla = osa_rodilla * mi_ratio
yo_pie = osa_pie * mi_ratio
yo_total = yo_hombro + yo_rodilla + yo_pie

osb = osa_hombro - yo_hombro
smob = osa_rodilla - yo_rodilla
jpp = osa_pie - yo_pie

# --- KPIs DE RESULTADOS ---
st.markdown("---")
st.header("📊 Resumen de Distribución")

k1, k2, k3 = st.columns(3)
with k1:
    st.metric("💙 Total VITHAS", f"{vithas_total:,.2f} €")
with k2:
    st.metric("🟩 Tú (OSA)", f"{yo_total:,.2f} €")
with k3:
    st.metric("🟫 Total OSA Repartido", f"{osa_total - yo_total:,.2f} €")

d1, d2, d3 = st.columns(3)
with d1:
    st.success(f"OSB (Hombro): {osb:,.2f} €")
with d2:
    st.info(f"SMOB (Rodilla): {smob:,.2f} €")
with d3:
    st.warning(f"JPP (Pie y Tobillo): {jpp:,.2f} €")

# --- GRÁFICO PIE ---
st.markdown("---")
st.subheader("📈 Distribución Visual")

fig = px.pie(
    names=["VITHAS", "Tú (OSA)", "OSB", "SMOB", "JPP"],
    values=[vithas_total, yo_total, osb, smob, jpp],
    title="Distribución Global de Facturación",
    color_discrete_map={
        "VITHAS": "#003A6F",
        "Tú (OSA)": "#2E8B57",
        "OSB": "#4B0082",
        "SMOB": "#1F618D",
        "JPP": "#B9770E"
    }
)
fig.update_traces(textposition="inside", textinfo="percent+label")
st.plotly_chart(fig, use_container_width=True)




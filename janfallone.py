import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Distribución VITHAS - OSA (Reestructurado)", layout="wide")

# -------------------- Estilos --------------------
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("💼 Distribución de Facturación | VITHAS - OSA (Reestructurado)")

# -------------------- Definiciones: niveles y servicios --------------------
niveles = {
    "General": ["Fallone", "Puigdellívol", "Ortega", "Aguilar", "Casaccia", "Pons", "Esteban"],
    "Especialista": ["ME1", "ME2", "ME3", "ME4", "ME5", "ME6"],
    "Consultor": ["MC1", "MC2", "MC3", "MC4", "MC5", "MC6"]
}

servicios = {
    "Consultas": {"VITHAS": 0.30, "OSA": 0.70},
    "Quirúrgicas": {"VITHAS": 0.10, "OSA": 0.90},
    "Urgencias": {"VITHAS": 0.50, "OSA": 0.50},
    "Ecografías": {"VITHAS": 0.60, "OSA": 0.40},
    "Prótesis y MQX": {"VITHAS": 0.00, "OSA": 1.00},
    "Pacientes INTL": {"VITHAS": 0.40, "OSA": 0.60},
    "Rehabilitación": {"VITHAS": 0.40, "OSA": 0.60},
    "Podología": {"VITHAS": 0.30, "OSA": 0.70}
}

# Lista plana de médicos
medicos = []
for nivel, lista in niveles.items():
    medicos.extend([(m, nivel) for m in lista])

# -------------------- DataFrame base para st.data_editor --------------------
cols = ["Médico", "Nivel"] + list(servicios.keys())
rows = []
for medico, nivel in medicos:
    fila = {"Médico": medico, "Nivel": nivel}
    for s in servicios.keys():
        fila[s] = 0.0
    rows.append(fila)

df_base = pd.DataFrame(rows, columns=cols)

st.subheader("📋 Ingresar facturación por médico y servicio")
df_edit = st.data_editor(df_base, num_rows="dynamic", use_container_width=True)

# Asegurar columnas numéricas
for s in servicios.keys():
    df_edit[s] = pd.to_numeric(df_edit[s], errors='coerce').fillna(0.0)

# -------------------- Cálculos --------------------
# Totales brutos por médico (suma de todos los servicios, siempre visible)
df_edit['Total_Bruto'] = df_edit[list(servicios.keys())].sum(axis=1)

# Totales por servicio (suma columnas)
totales_por_servicio = {s: df_edit[s].sum() for s in servicios.keys()}

# Totales VITHAS y OSA por servicio
totales_vithas_por_servicio = {s: totales_por_servicio[s] * servicios[s]['VITHAS'] for s in servicios.keys()}
totales_osa_por_servicio = {s: totales_por_servicio[s] * servicios[s]['OSA'] for s in servicios.keys()}

# Totales generales
total_bruto = df_edit['Total_Bruto'].sum()
total_vithas = sum(totales_vithas_por_servicio.values())
total_osa = sum(totales_osa_por_servicio.values())

# -------------------- Cálculo OSA disponible por médico --------------------
osa_por_medico = []
total_vithas_por_medico = []
for _, row in df_edit.iterrows():
    total_osa_med = 0.0
    total_vithas_med = 0.0
    for s in servicios.keys():
        total_osa_med += row[s] * servicios[s]['OSA']
        total_vithas_med += row[s] * servicios[s]['VITHAS']
    osa_por_medico.append(total_osa_med)
    total_vithas_por_medico.append(total_vithas_med)

df_edit['Total_OSA_Disponible'] = osa_por_medico
df_edit['Total_VITHAS'] = total_vithas_por_medico

# Totales por nivel (bruto)
totales_por_nivel = df_edit.groupby('Nivel')['Total_Bruto'].sum().to_dict()

# Promedios por grupo (Especialistas y Consultores)
promedio_especialistas = df_edit[df_edit['Nivel'] == 'Especialista']['Total_Bruto'].mean() if not df_edit[df_edit['Nivel'] == 'Especialista'].empty else 0.0
promedio_consultores = df_edit[df_edit['Nivel'] == 'Consultor']['Total_Bruto'].mean() if not df_edit[df_edit['Nivel'] == 'Consultor'].empty else 0.0

# -------------------- Aplicación reglas abono --------------------
pct_aplicado = []
abonado = []
por_osa_queda = []

for _, row in df_edit.iterrows():
    nivel = row['Nivel']
    total_bruto = row['Total_Bruto']
    total_osa_med = row['Total_OSA_Disponible']

    if nivel == 'General':
        pct = 0.95
    elif nivel == 'Especialista':
        pct = 0.90 if total_bruto > promedio_especialistas else 0.85
    elif nivel == 'Consultor':
        pct = 0.92 if total_bruto > promedio_consultores else 0.88
    else:
        pct = 0.0

    pagado = total_osa_med * pct
    queda_osa = total_osa_med - pagado

    pct_aplicado.append(pct)
    abonado.append(pagado)
    por_osa_queda.append(queda_osa)

df_edit['Pct_Abono'] = pct_aplicado
df_edit['Abonado_a_Medico'] = abonado
df_edit['Queda_en_OSA_por_medico'] = por_osa_queda

# Diferencia porcentual entre lo facturado bruto y lo recibido
df_edit['Diferencia_%'] = (df_edit['Abonado_a_Medico'] / df_edit['Total_Bruto'] - 1).replace([float('inf'), -float('inf')], 0.0).fillna(0.0)

# Totales de abono y saldo OSA
total_abonado_a_medicos = sum(abonado)
osa_saldo_final = total_osa - total_abonado_a_medicos

# -------------------- Resultados en pantalla --------------------
st.markdown("---")
st.header("📊 Resumen General de Facturación")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("💰 Total Facturación Bruta", f"{total_bruto:,.2f} €")
with c2:
    st.metric("🏥 Total VITHAS", f"{total_vithas:,.2f} €")
with c3:
    st.metric("🟩 Total OSA (pool inicial)", f"{total_osa:,.2f} €")
with c4:
    st.metric("⚖️ Saldo OSA después de abonos", f"{osa_saldo_final:,.2f} €")

st.markdown("---")
st.subheader("📌 Totales por Servicio")
serv_df = pd.DataFrame({
    'Servicio': list(totales_por_servicio.keys()),
    'Facturación_Total': list(totales_por_servicio.values()),
    'VITHAS': [totales_vithas_por_servicio[s] for s in totales_por_servicio.keys()],
    'OSA': [totales_osa_por_servicio[s] for s in totales_por_servicio.keys()]
})
st.dataframe(serv_df.style.format({"Facturación_Total": "{:.2f}", "VITHAS": "{:.2f}", "OSA": "{:.2f}"}))
fig_serv = px.pie(serv_df, names='Servicio', values='Facturación_Total', title='Distribución de Facturación por Servicio')
st.plotly_chart(fig_serv, use_container_width=True)

st.markdown("---")
st.subheader("📌 Totales por Nivel Jerárquico (Bruto)")
nivel_df = pd.DataFrame({'Nivel': list(totales_por_nivel.keys()), 'Total_Bruto': list(totales_por_nivel.values())})
st.dataframe(nivel_df.style.format({"Total_Bruto": "{:.2f}"}))
fig_niv = px.bar(nivel_df, x='Nivel', y='Total_Bruto', title='Total Bruto por Nivel Jerárquico')
st.plotly_chart(fig_niv, use_container_width=True)

st.markdown("---")
st.subheader("📋 Detalle por Médico")
cols_to_show = ['Médico', 'Nivel'] + list(servicios.keys()) + ['Total_Bruto', 'Total_VITHAS', 'Total_OSA_Disponible', 'Pct



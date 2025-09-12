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

# data_editor permite edición tipo hoja de cálculo
df_edit = st.data_editor(df_base, num_rows="dynamic", use_container_width=True)

# Asegurarnos de que las columnas de servicios sean numéricas
for s in servicios.keys():
    df_edit[s] = pd.to_numeric(df_edit[s], errors='coerce').fillna(0.0)

# -------------------- Cálculos: totales por médico, por servicio y por nivel --------------------
# Total bruto por médico (antes de separar VITHAS / OSA)
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

# -------------------- Cálculo de OSA disponible por médico --------------------
osa_por_medico = []
for _, row in df_edit.iterrows():
    total_osa_med = 0.0
    for s in servicios.keys():
        total_osa_med += row[s] * servicios[s]['OSA']
    osa_por_medico.append(total_osa_med)

df_edit['Total_OSA_Disponible'] = osa_por_medico

# Totales por nivel (brutos)
totales_por_nivel = df_edit.groupby('Nivel')['Total_Bruto'].sum().to_dict()

# Promedios por grupo (Especialistas y Consultores, usando bruto)
promedio_especialistas = df_edit[df_edit['Nivel'] == 'Especialista']['Total_Bruto'].mean() if not df_edit[df_edit['Nivel'] == 'Especialista'].empty else 0.0
promedio_consultores = df_edit[df_edit['Nivel'] == 'Consultor']['Total_Bruto'].mean() if not df_edit[df_edit['Nivel'] == 'Consultor'].empty else 0.0

# -------------------- Aplicación de reglas de abono (sobre OSA disponible) --------------------
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
        if total_bruto > promedio_especialistas:
            pct = 0.90
        else:
            pct = 0.85
    elif nivel == 'Consultor':
        if total_bruto > promedio_consultores:
            pct = 0.92
        else:
            pct = 0.88
    else:
        pct = 0.0

    pagado = total_osa_med * pct
    queda_osa = total_osa_med - pagado

    pct_aplicado.append(pct)
    abonado.append(pagado)
    por_osa_queda.append(queda_osa)

# Añadir columnas al DataFrame
df_edit['Pct_Abono'] = pct_aplicado
df_edit['Abonado_a_Medico'] = abonado
df_edit['Queda_en_OSA_por_medico'] = por_osa_queda

# Diferencia porcentual entre lo que facturó bruto y lo que recibió
df_edit['Diferencia_%'] = (df_edit['Abonado_a_Medico'] / df_edit['Total_Bruto'] - 1).replace([float('inf'), -float('inf')], 0.0).fillna(0.0)

# Totales resultantes de los abonos
total_abonado_a_medicos = sum(abonado)
osa_saldo_final = total_osa - total_abonado_a_medicos

# -------------------- Resultados en pantalla --------------------
st.markdown("---")
st.header("📊 Resumen General de Facturación")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("💰 Total Facturación Bruta", f"{total_bruto:,.2f} €")
with c2:
    st.metric("🏥 Total VITHAS (según %)", f"{total_vithas:,.2f} €")
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

nivel_df = pd.DataFrame({
    'Nivel': list(totales_por_nivel.keys()),
    'Total_Bruto': list(totales_por_nivel.values())
})
st.dataframe(nivel_df.style.format({"Total_Bruto": "{:.2f}"}))

fig_niv = px.bar(nivel_df, x='Nivel', y='Total_Bruto', title='Total Bruto por Nivel Jerárquico')
st.plotly_chart(fig_niv, use_container_width=True)

st.markdown("---")
st.subheader("📋 Detalle por Médico")

cols_to_show = ['Médico', 'Nivel'] + list(servicios.keys()) + ['Total_Bruto', 'Total_OSA_Disponible', 'Pct_Abono', 'Abonado_a_Medico', 'Queda_en_OSA_por_medico', 'Diferencia_%']
st.dataframe(df_edit[cols_to_show].sort_values(['Nivel', 'Médico']).reset_index(drop=True).style.format({
    **{s: "{:.2f}" for s in servicios.keys()},
    'Total_Bruto': "{:.2f}",
    'Total_OSA_Disponible': "{:.2f}",
    'Pct_Abono': "{:.2%}",
    'Abonado_a_Medico': "{:.2f}",
    'Queda_en_OSA_por_medico': "{:.2f}",
    'Diferencia_%': "{:.2%}"
}))

st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    st.metric("Promedio Especialistas (Bruto)", f"{promedio_especialistas:,.2f} €")
with c2:
    st.metric("Promedio Consultores (Bruto)", f"{promedio_consultores:,.2f} €")

if total_abonado_a_medicos > total_osa:
    st.error("⚠️ Atención: El total abonado supera el pool OSA. Revisa los datos.")

# -------------------- Exportar Excel con varias hojas --------------------
st.markdown("---")
st.subheader("⬇️ Descargar Datos en Excel")

hoja_totales_globales = pd.DataFrame({
    'Concepto': ['Total Bruto', 'Total VITHAS', 'Total OSA (pool inicial)', 'Total abonado a médicos', 'Saldo OSA final'],
    'Valor (€)': [total_bruto, total_vithas, total_osa, total_abonado_a_medicos, osa_saldo_final]
})

hoja_por_servicio = serv_df.copy()
hoja_por_nivel = nivel_df.copy()
hoja_detalle_medicos = df_edit[cols_to_show].copy()

def to_excel_multi(h_tot, h_serv, h_niv, h_med):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        h_tot.to_excel(writer, index=False, sheet_name='Totales_Globales')
        h_serv.to_excel(writer, index=False, sheet_name='Por_Servicio')
        h_niv.to_excel(writer, index=False, sheet_name='Por_Nivel')
        h_med.to_excel(writer, index=False, sheet_name='Detalle_Medicos')
    return output.getvalue()

excel_bytes = to_excel_multi(hoja_totales_globales, hoja_por_servicio, hoja_por_nivel, hoja_detalle_medicos)

st.download_button(
    label="📅 Descargar Excel Completo",
    data=excel_bytes,
    file_name="vithas_osa_reestructurado.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("---")
st.write("Hecho ✅ — Ahora los pagos a médicos salen del pool OSA, el saldo se calcula correctamente y se muestra la diferencia porcentual entre lo facturado bruto y lo recibido.")


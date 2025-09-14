import streamlit as st
import pandas as pd
import plotly.express as px
import math

st.set_page_config(page_title="Escalabilidad", layout="wide", page_icon="📊")
st.title("📊 Escalabilidad del Pago a Médicos")

# -------------------- Definición de niveles y servicios --------------------
niveles = {
    "Especialista": ["Pons", "Sugrañes", "Mayo", "ME3", "ME4", "ME5", "ME6"],
    "Consultor": ["Fallone", "Puigdellívol", "Aguilar", "Casaccia", "De Retana", "Ortega", "Barro", "Esteban", "MC4", "MC5", "MC6"]
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

# -------------------- Crear DataFrame base --------------------
medicos = []
for nivel, lista in niveles.items():
    medicos.extend([(m, nivel) for m in lista])

cols = ["Médico", "Nivel"] + list(servicios.keys())
rows = []
for medico, nivel in medicos:
    fila = {"Médico": medico, "Nivel": nivel}
    for s in servicios.keys():
        fila[s] = 0.0
    rows.append(fila)

df_edit = pd.DataFrame(rows, columns=cols)

# -------------------- Entrada de montos interactiva --------------------
st.markdown("### 📋 Ingreso de Montos de Facturación")
df_edit = st.data_editor(df_edit, num_rows="fixed", use_container_width=True, height=400)

for s in servicios.keys():
    df_edit[s] = pd.to_numeric(df_edit[s], errors='coerce').fillna(0.0)

# -------------------- Cálculos --------------------
df_edit["Total_Bruto"] = df_edit[list(servicios.keys())].sum(axis=1)
df_edit["Total_OSA_Disponible"] = df_edit.apply(lambda row: sum(row[s]*servicios[s]["OSA"] for s in servicios), axis=1)
df_edit["Total_VITHAS"] = df_edit.apply(lambda row: sum(row[s]*servicios[s]["VITHAS"] for s in servicios), axis=1)

promedios_nivel = df_edit.groupby("Nivel")["Total_Bruto"].mean().to_dict()

def calcular_abono(row):
    nivel = row["Nivel"]
    total_bruto = row["Total_Bruto"]
    total_osa = row["Total_OSA_Disponible"]
    if nivel == "Especialista":
        pct = 0.90 if total_bruto > promedios_nivel[nivel] else 0.85
    elif nivel == "Consultor":
        pct = 0.92 if total_bruto > promedios_nivel[nivel] else 0.88
    else:
        pct = 0.0
    return total_osa * pct

df_edit["Abonado_a_Medico"] = df_edit.apply(calcular_abono, axis=1)

# -------------------- KPI tipo tarjeta promedios por nivel --------------------
st.markdown("### 📈 Promedio de facturación por nivel jerárquico")
c1, c2 = st.columns(2)
c1.markdown(f"""
<div style="background: linear-gradient(135deg, #3498db, #2980b9); padding: 20px; border-radius: 15px; text-align: center; color: white;">
    <h4>Promedio Especialistas</h4>
    <h2>{promedios_nivel.get('Especialista',0):,.2f} €</h2>
</div>
""", unsafe_allow_html=True)

c2.markdown(f"""
<div style="background: linear-gradient(135deg, #27ae60, #2ecc71); padding: 20px; border-radius: 15px; text-align: center; color: white;">
    <h4>Promedio Consultores</h4>
    <h2>{promedios_nivel.get('Consultor',0):,.2f} €</h2>
</div>
""", unsafe_allow_html=True)

# -------------------- Selección de médico --------------------
st.markdown("### 👨‍⚕️ Reporte Interactivo del Médico")
medico_sel = st.selectbox("Seleccione un médico", df_edit["Médico"].unique())
row = df_edit[df_edit["Médico"]==medico_sel].iloc[0]

# -------------------- Mini-dashboard de reporte del médico --------------------
st.markdown("### 📝 Mini-Reporte del Médico")

# Filtrar servicios con facturación > 0
serv_no_cero = {s: row[s] for s in servicios.keys() if row[s] > 0}
serv_cero = [s for s in servicios.keys() if row[s] == 0]

num_cols = 3
num_filas = math.ceil(len(serv_no_cero)/num_cols)

for i in range(num_filas):
    cols_kpi = st.columns(num_cols)
    for j in range(num_cols):
        idx = i*num_cols + j
        if idx < len(serv_no_cero):
            s = list(serv_no_cero.keys())[idx]
            fact = row[s]
            vithas = fact*servicios[s]["VITHAS"]
            osa = fact*servicios[s]["OSA"]
            if row["Nivel"]=="Especialista":
                pct = 0.90 if row["Total_Bruto"]>promedios_nivel["Especialista"] else 0.85
            else:
                pct = 0.92 if row["Total_Bruto"]>promedios_nivel["Consultor"] else 0.88
            abon = osa * pct
            cols_kpi[j].markdown(f"""
            <div style="background-color:#2e7d32; border-radius:10px; padding:15px; color:white; text-align:center;">
                <h5>{s}</h5>
                <p>Fact: {fact:,.2f} €</p>
                <p>VITHAS: {vithas:,.2f} €</p>
                <p>Abono: {abon:,.2f} €</p>
            </div>
            """, unsafe_allow_html=True)

# Tarjetas resumen generales del médico
osa_total = row["Total_OSA_Disponible"]
osa_final = osa_total - row["Abonado_a_Medico"]
porc_abonado = row["Abonado_a_Medico"]/row["Total_Bruto"]*100 if row["Total_Bruto"]>0 else 0

rep_cols = st.columns(4)
rep_cols[0].markdown(f"""
<div style="background-color:#1b5e20; border-radius:10px; padding:20px; color:white; text-align:center;">
<h4>Total Facturación</h4>
<p>{row['Total_Bruto']:,.2f} €</p>
</div>
""", unsafe_allow_html=True)

rep_cols[1].markdown(f"""
<div style="background-color:#00695c; border-radius:10px; padding:20px; color:white; text-align:center;">
<h4>Total VITHAS</h4>
<p>{row['Total_VITHAS']:,.2f} €</p>
</div>
""", unsafe_allow_html=True)

rep_cols[2].markdown(f"""
<div style="background-color:#2e7d32; border-radius:10px; padding:20px; color:white; text-align:center;">
<h4>Abonado al Médico</h4>
<p>{row['Abonado_a_Medico']:,.2f} €</p>
</div>
""", unsafe_allow_html=True)

rep_cols[3].markdown(f"""
<div style="background-color:#558b2f; border-radius:10px; padding:20px; color:white; text-align:center;">
<h4>OSA Final</h4>
<p>{osa_final:,.2f} €</p>
<p>{porc_abonado:.1f}% recibido</p>
</div>
""", unsafe_allow_html=True)

# Nota servicios sin facturación
if serv_cero:
    st.info(f"Usted no facturó nada en: {', '.join(serv_cero)}")

# -------------------- Gráfico comparativo por nivel jerárquico --------------------
st.markdown("### 📊 Comparación de abonos por nivel jerárquico")
nivel_sel = st.selectbox("Seleccione nivel jerárquico para gráfico", list(niveles.keys()), key="nivel_grafico")
df_nivel = df_edit[df_edit["Nivel"]==nivel_sel].copy()
df_melt = df_nivel.melt(id_vars=["Médico"], value_vars=["Total_Bruto","Total_VITHAS","Total_OSA_Disponible","Abonado_a_Medico"],
                        var_name="Concepto", value_name="Valor (€)")

fig = px.bar(df_melt, x="Médico", y="Valor (€)", color="Concepto", barmode="group",
             title=f"Comparación de abonos de médicos del nivel {nivel_sel}")
st.plotly_chart(fig, use_container_width=True)

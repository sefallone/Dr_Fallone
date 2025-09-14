import streamlit as st
import pandas as pd
import math

# Configuración de la página
st.set_page_config(page_title="Escalabilidad", layout="wide", page_icon="📊")
st.title("📊 Escalabilidad del Pago a Médicos")

# -------------------- Niveles y servicios --------------------
niveles = {
    "Especialista": ["ME1","ME2","ME3","ME4","ME5","ME6"],
    "Consultor": ["C1","C2","C3"]
}

servicios = {
    "Consultas": {"VITHAS": 0.30, "OSA": 0.70},
    "Quirúrgicas": {"VITHAS": 0.10, "OSA": 0.90},
    "Urgencias": {"VITHAS": 0.50, "OSA": 0.50}
}

# -------------------- Crear DataFrame editable --------------------
medicos = []
for nivel, lista in niveles.items():
    medicos.extend([(m,nivel) for m in lista])

cols = ["Médico","Nivel"] + list(servicios.keys())
rows = []
for medico, nivel in medicos:
    fila = {"Médico":medico,"Nivel":nivel}
    for s in servicios.keys():
        fila[s]=0.0
    rows.append(fila)

df_edit = pd.DataFrame(rows, columns=cols)

# Editor interactivo para ingresar montos
st.markdown("### Ingrese los importes de facturación por médico y servicio")
df_edit = st.data_editor(df_edit, num_rows="fixed", use_container_width=True, height=400)

# -------------------- Cálculos básicos --------------------
for s in servicios.keys():
    df_edit[s] = pd.to_numeric(df_edit[s], errors='coerce').fillna(0.0)

df_edit["Total_Bruto"] = df_edit[list(servicios.keys())].sum(axis=1)
df_edit["Total_OSA"] = df_edit.apply(lambda row: sum(row[s]*servicios[s]["OSA"] for s in servicios), axis=1)

# Promedio por nivel jerárquico
promedios_nivel = df_edit.groupby("Nivel")["Total_Bruto"].mean().to_dict()

def calcular_abono(row):
    nivel = row["Nivel"]
    bruto = row["Total_Bruto"]
    osa = row["Total_OSA"]
    if nivel=="Especialista":
        pct = 0.90 if bruto>promedios_nivel[nivel] else 0.85
    else:
        pct = 0.92 if bruto>promedios_nivel[nivel] else 0.88
    abonado = osa*pct
    return abonado, osa-(osa*pct), pct

df_edit[["Abonado","OSA_Resto","Pct_Abono"]] = df_edit.apply(lambda row: pd.Series(calcular_abono(row)), axis=1)
df_edit["Proy_Si_Supera"] = df_edit.apply(lambda row: row["Total_OSA"]*0.90 if row["Nivel"]=="Especialista" else row["Total_OSA"]*0.92, axis=1)

# -------------------- Selección de médico --------------------
medico_sel = st.selectbox("Seleccione un médico", df_edit["Médico"].unique())
row = df_edit[df_edit["Médico"]==medico_sel].iloc[0]

# -------------------- Mensaje de rendimiento --------------------
if row["Total_Bruto"]>promedios_nivel[row["Nivel"]]:
    st.success(f"Doctor {medico_sel} está por ARRIBA del promedio de facturación de su grupo")
else:
    st.warning(f"Doctor {medico_sel} está por ABAJO del promedio de facturación de su grupo")

# -------------------- KPI por servicio --------------------
serv_no_cero = {s:row[s] for s in servicios.keys() if row[s]>0}
serv_cero = [s for s in servicios.keys() if row[s]==0]

num_cols = 3
num_filas = math.ceil(len(serv_no_cero)/num_cols)
colores = ["#1b5e20","#2e7d32","#388e3c","#43a047","#4caf50"]

st.markdown("### Facturación por servicio")
for i in range(num_filas):
    cols_kpi = st.columns(num_cols)
    for j in range(num_cols):
        idx = i*num_cols+j
        if idx<len(serv_no_cero):
            s = list(serv_no_cero.keys())[idx]
            valor = row[s]
            vithas = valor*servicios[s]["VITHAS"]
            abon = valor*servicios[s]["OSA"]*row["Pct_Abono"]
            color = colores[idx%len(colores)]
            cols_kpi[j].markdown(f"""
            <div style="background-color:{color}; border-radius:10px; padding:15px; color:white; text-align:center;">
            <h5>{s}</h5>
            <p>Facturación: {valor:,.2f} €</p>
            <p>VITHAS: {vithas:,.2f} €</p>
            <p>Abono: {abon:,.2f} €</p>
            </div>
            """, unsafe_allow_html=True)

# -------------------- KPI generales del médico --------------------
st.markdown("### Resumen general del médico")
kpi_cols = st.columns(6)
kpi_cols[0].markdown(f"""
<div style="background-color:#0d47a1; border-radius:10px; padding:15px; color:white; text-align:center;">
<h5>Total Facturado</h5>
<p>{row['Total_Bruto']:,.2f} €</p>
</div>
""", unsafe_allow_html=True)

kpi_cols[1].markdown(f"""
<div style="background-color:#1976d2; border-radius:10px; padding:15px; color:white; text-align:center;">
<h5>Abonado al Médico</h5>
<p>{row['Abonado']:,.2f} €</p>
</div>
""", unsafe_allow_html=True)

kpi_cols[2].markdown(f"""
<div style="background-color:#1565c0; border-radius:10px; padding:15px; color:white; text-align:center;">
<h5>% Abonado</h5>
<p>{row['Pct_Abono']*100:.1f}%</p>
</div>
""", unsafe_allow_html=True)

kpi_cols[3].markdown(f"""
<div style="background-color:#00695c; border-radius:10px; padding:15px; color:white; text-align:center;">
<h5>Se deja de abonar</h5>
<p>{row['OSA_Resto']:,.2f} €</p>
</div>
""", unsafe_allow_html=True)

kpi_cols[4].markdown(f"""
<div style="background-color:#2e7d32; border-radius:10px; padding:15px; color:white; text-align:center;">
<h5>OSA Final</h5>
<p>{row['Total_OSA']-row['Abonado']:,.2f} €</p>
</div>
""", unsafe_allow_html=True)

kpi_cols[5].markdown(f"""
<div style="background-color:#43a047; border-radius:10px; padding:15px; color:white; text-align:center;">
<h5>Proyección si supera promedio</h5>
<p>{row['Proy_Si_Supera']:,.2f} €</p>
</div>
""", unsafe_allow_html=True)

# -------------------- Nota servicios sin facturación --------------------
if serv_cero:
    st.info(f"Usted no facturó nada en: {', '.join(serv_cero)}")


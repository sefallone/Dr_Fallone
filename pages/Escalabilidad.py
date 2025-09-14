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

# -------------------- Mensaje personalizado sobre el promedio --------------------
nivel_medico = row["Nivel"]
promedio_nivel = promedios_nivel[nivel_medico]
if row["Total_Bruto"] > promedio_nivel:
    mensaje = f"Doctor {medico_sel}, usted está por ARRIBA del promedio de facturación de su grupo."
    color_mensaje = "success"
else:
    mensaje = f"Doctor {medico_sel}, usted está por ABAJO del promedio de facturación de su grupo."
    color_mensaje = "warning"

st.success(mensaje) if color_mensaje == "success" else st.warning(mensaje)

# -------------------- Cálculos para el potencial de ganancia --------------------
# Determinar porcentajes actuales y potenciales
if nivel_medico == "Especialista":
    pct_actual = 0.85 if row["Total_Bruto"] <= promedios_nivel[nivel_medico] else 0.90
    pct_potencial = 0.90 if pct_actual == 0.85 else pct_actual
else:  # Consultor
    pct_actual = 0.88 if row["Total_Bruto"] <= promedios_nivel[nivel_medico] else 0.92
    pct_potencial = 0.92 if pct_actual == 0.88 else pct_actual

abono_actual = row["Total_OSA_Disponible"] * pct_actual
abono_potencial = row["Total_OSA_Disponible"] * pct_potencial
diferencia_abono = abono_potencial - abono_actual
porcentaje_actual = (abono_actual / row["Total_Bruto"] * 100) if row["Total_Bruto"] > 0 else 0
porcentaje_potencial = (abono_potencial / row["Total_Bruto"] * 100) if row["Total_Bruto"] > 0 else 0

osa_final_actual = row["Total_OSA_Disponible"] - abono_actual
osa_final_potencial = row["Total_OSA_Disponible"] - abono_potencial

# -------------------- Nuevo diseño de KPIs para el médico --------------------
st.markdown("### 📝 Reporte de Rendimiento del Médico")

# Primera fila de KPIs principales
kpi_cols1 = st.columns(4)

kpi_cols1[0].markdown(f"""
<div style="background: linear-gradient(135deg, #1b5e20, #2e7d32); padding: 15px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h4 style="margin: 0; font-size: 1rem;">Facturación Total</h4>
    <h2 style="margin: 5px 0; font-size: 1.8rem;">{row['Total_Bruto']:,.2f} €</h2>
</div>
""", unsafe_allow_html=True)

kpi_cols1[1].markdown(f"""
<div style="background: linear-gradient(135deg, #00695c, #00897b); padding: 15px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h4 style="margin: 0; font-size: 1rem;">Parte VITHAS</h4>
    <h2 style="margin: 5px 0; font-size: 1.8rem;">{row['Total_VITHAS']:,.2f} €</h2>
</div>
""", unsafe_allow_html=True)

kpi_cols1[2].markdown(f"""
<div style="background: linear-gradient(135deg, #2e7d32, #43a047); padding: 15px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h4 style="margin: 0; font-size: 1rem;">Abonado al Médico</h4>
    <h2 style="margin: 5px 0; font-size: 1.8rem;">{abono_actual:,.2f} €</h2>
    <p style="margin: 0; font-size: 0.9rem;">({porcentaje_actual:.1f}% de la facturación)</p>
</div>
""", unsafe_allow_html=True)

kpi_cols1[3].markdown(f"""
<div style="background: linear-gradient(135deg, #558b2f, #689f38); padding: 15px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h4 style="margin: 0; font-size: 1rem;">OSA Final</h4>
    <h2 style="margin: 5px 0; font-size: 1.8rem;">{osa_final_actual:,.2f} €</h2>
</div>
""", unsafe_allow_html=True)

# Segunda fila de KPIs de potencial
st.markdown("---")
st.subheader("📈 Potencial de Ingresos")

kpi_cols2 = st.columns(2)

if diferencia_abono > 0:
    kpi_cols2[0].markdown(f"""
    <div style="background: linear-gradient(135deg, #e65100, #ef6c00); padding: 20px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h4 style="margin: 0; font-size: 1.1rem;">Potencial no alcanzado</h4>
        <h2 style="margin: 10px 0; font-size: 2rem;">{diferencia_abono:,.2f} €</h2>
        <p style="margin: 0; font-size: 1rem;">Por no superar el promedio de su nivel</p>
    </div>
    """, unsafe_allow_html=True)
else:
    kpi_cols2[0].markdown(f"""
    <div style="background: linear-gradient(135deg, #2e7d32, #43a047); padding: 20px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h4 style="margin: 0; font-size: 1.1rem;">¡Meta alcanzada!</h4>
        <h2 style="margin: 10px 0; font-size: 2rem;">+{abono_potencial:,.2f} €</h2>
        <p style="margin: 0; font-size: 1rem;">Ha superado el promedio de su nivel</p>
    </div>
    """, unsafe_allow_html=True)

kpi_cols2[1].markdown(f"""
<div style="background: linear-gradient(135deg, #1565c0, #1976d2); padding: 20px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h4 style="margin: 0; font-size: 1.1rem;">Abono potencial máximo</h4>
    <h2 style="margin: 10px 0; font-size: 2rem;">{abono_potencial:,.2f} €</h2>
    <p style="margin: 0; font-size: 1rem;">({porcentaje_potencial:.1f}% de la facturación)</p>
</div>
""", unsafe_allow_html=True)

# -------------------- Facturación por servicio --------------------
st.markdown("---")
st.subheader("🧾 Desglose por Servicios")

servicios_con_facturacion = {s: row[s] for s in servicios.keys() if row[s] > 0}
servicios_sin_facturacion = [s for s in servicios.keys() if row[s] == 0]

if servicios_con_facturacion:
    num_cols = min(4, len(servicios_con_facturacion))
    cols_servicios = st.columns(num_cols)
    
    colores_servicios = ["#2e7d32", "#388e3c", "#43a047", "#4caf50", "#66bb6a", "#81c784", "#a5d6a7", "#c8e6c9"]
    
    for i, (servicio, monto) in enumerate(servicios_con_facturacion.items()):
        col_idx = i % num_cols
        color_idx = i % len(colores_servicios)
        
        cols_servicios[col_idx].markdown(f"""
        <div style="background-color: {colores_servicios[color_idx]}; border-radius: 8px; padding: 12px; color: white; text-align: center; margin-bottom: 10px;">
            <h5 style="margin: 0 0 8px 0; font-size: 0.9rem;">{servicio}</h5>
            <p style="margin: 0; font-size: 1.1rem; font-weight: bold;">{monto:,.2f} €</p>
        </div>
        """, unsafe_allow_html=True)

# Servicios sin facturación
if servicios_sin_facturacion:
    st.info(f"**Servicios sin facturación:** {', '.join(servicios_sin_facturacion)}")

# -------------------- Gráfico comparativo por nivel jerárquico --------------------
st.markdown("---")
st.markdown("### 📊 Comparación de abonos por nivel jerárquico")
nivel_sel = st.selectbox("Seleccione nivel jerárquico para gráfico", list(niveles.keys()), key="nivel_grafico")
df_nivel = df_edit[df_edit["Nivel"]==nivel_sel].copy()
df_melt = df_nivel.melt(id_vars=["Médico"], value_vars=["Total_Bruto","Total_VITHAS","Total_OSA_Disponible","Abonado_a_Medico"],
                        var_name="Concepto", value_name="Valor (€)")

fig = px.bar(df_melt, x="Médico", y="Valor (€)", color="Concepto", barmode="group",
             title=f"Comparación de abonos de médicos del nivel {nivel_sel}", text="Valor (€)")
fig.update_traces(texttemplate='%{text:,.0f} €', textposition='outside')
st.plotly_chart(fig, use_container_width=True)


import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Escalabilidad", layout="wide", page_icon="📊")
st.title("📊 Escalabilidad del Pago a Médicos")

st.markdown("""
El sistema de pago funciona en **tres pasos**:

1. Cada médico genera una **facturación bruta total** por servicio.
2. Esa facturación se reparte entre **VITHAS** y **OSA**, según porcentajes.
3. Del pool OSA, se calcula cuánto se le **abona al médico** según su nivel.
""")

# -------------------- Definición de médicos y servicios --------------------
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

# Lista plana de médicos
medicos = []
for nivel, lista in niveles.items():
    medicos.extend([(m, nivel) for m in lista])

# -------------------- Entrada de datos interactiva --------------------
st.markdown("### 📋 Ingrese los montos por médico y servicio")
cols = ["Médico", "Nivel"] + list(servicios.keys())
rows = []
for medico, nivel in medicos:
    fila = {"Médico": medico, "Nivel": nivel}
    for s in servicios.keys():
        fila[s] = 0.0
    rows.append(fila)

df_edit = pd.DataFrame(rows, columns=cols)

df_edit = st.data_editor(df_edit, num_rows="fixed", use_container_width=True, height=400)

# Asegurarnos de que las columnas de servicios sean numéricas
for s in servicios.keys():
    df_edit[s] = pd.to_numeric(df_edit[s], errors='coerce').fillna(0.0)

# -------------------- Cálculos --------------------
df_edit["Total_Bruto"] = df_edit[list(servicios.keys())].sum(axis=1)

# Totales VITHAS y OSA por médico
osa_por_medico = []
abonado = []
for _, row in df_edit.iterrows():
    total_osa_med = sum(row[s]*servicios[s]["OSA"] for s in servicios)
    osa_por_medico.append(total_osa_med)
    # regla simple de ejemplo
    pct = 0.9 if row["Nivel"]=="Especialista" else 0.88
    abonado.append(total_osa_med*pct)

df_edit["Total_OSA_Disponible"] = osa_por_medico
df_edit["Abonado_a_Medico"] = abonado

# -------------------- Selección para detalle --------------------
st.markdown("### 👨‍⚕️ Detalle por servicio")
medico_sel = st.selectbox("Seleccione un médico", df_edit["Médico"].unique())
row = df_edit[df_edit["Médico"]==medico_sel].iloc[0]

detalle_servicios = []
for s in servicios.keys():
    fact = row[s]
    vithas = fact * servicios[s]["VITHAS"]
    osa = fact * servicios[s]["OSA"]
    abon = osa * (0.9 if row["Nivel"]=="Especialista" else 0.88)
    detalle_servicios.append({
        "Servicio": s,
        "Facturación": fact,
        "VITHAS": vithas,
        "OSA": osa,
        "Abonado al Médico": abon
    })

df_detalle = pd.DataFrame(detalle_servicios)
df_detalle.loc["TOTAL"] = df_detalle[["Facturación","VITHAS","OSA","Abonado al Médico"]].sum()
df_detalle.loc["TOTAL","Servicio"] = "TOTAL"

st.dataframe(df_detalle.style.format({
    "Facturación":"{:,.2f} €",
    "VITHAS":"{:,.2f} €",
    "OSA":"{:,.2f} €",
    "Abonado al Médico":"{:,.2f} €"
}), use_container_width=True)

st.markdown(f"**Resumen:** {medico_sel} facturó {row['Total_Bruto']:.2f} €, se abonará {row['Abonado_a_Medico']:.2f} € según su nivel ({row['Nivel']}).")

# -------------------- Gráfico comparativo por nivel --------------------
st.markdown("### 📊 Comparación de abonos por nivel jerárquico")
nivel_sel = st.selectbox("Seleccione nivel jerárquico", list(niveles.keys()))
df_nivel = df_edit[df_edit["Nivel"]==nivel_sel].copy()

df_melt = df_nivel.melt(id_vars=["Médico"], value_vars=["Total_Bruto","Total_OSA_Disponible","Abonado_a_Medico"],
                        var_name="Concepto", value_name="Valor (€)")

fig = px.bar(df_melt, x="Médico", y="Valor (€)", color="Concepto", barmode="group",
             title=f"Comparación de abonos de médicos del nivel {nivel_sel}")
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
### 🔹 Conclusión
- Se parte de la facturación total por servicio.
- Se aplica la distribución VITHAS/OSA.
- Del pool OSA se calcula el abono final al médico.
- Tabla y gráfico permiten ver claramente la deducción y lo que finalmente cobra cada médico.
""")

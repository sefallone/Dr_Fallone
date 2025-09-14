import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="Escalabilidad", layout="wide", page_icon="📊")
st.title("📊 Escalabilidad del Pago a Médicos - Gradientes por Columna")

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

# -------------------- Entrada de datos --------------------
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
df_edit = st.data_editor(df_edit, num_rows="fixed", use_container_width=True, height=400)

# Asegurar que columnas de servicios sean numéricas
for s in servicios.keys():
    df_edit[s] = pd.to_numeric(df_edit[s], errors='coerce').fillna(0.0)

# -------------------- Cálculos --------------------
df_edit["Total_Bruto"] = df_edit[list(servicios.keys())].sum(axis=1)
df_edit["Total_OSA_Disponible"] = df_edit.apply(lambda row: sum(row[s]*servicios[s]["OSA"] for s in servicios), axis=1)
df_edit["Total_VITHAS"] = df_edit.apply(lambda row: sum(row[s]*servicios[s]["VITHAS"] for s in servicios), axis=1)

promedios_nivel = df_edit.groupby("Nivel")["Total_Bruto"].mean().to_dict()

# Abono final según reglas de promedio
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

# -------------------- Tabla interactiva con gradientes por columna --------------------
st.markdown("### 👨‍⚕️ Detalle por servicio de un médico (Colores por columna)")

medico_sel = st.selectbox("Seleccione un médico", df_edit["Médico"].unique())
row = df_edit[df_edit["Médico"]==medico_sel].iloc[0]

detalle_servicios = []
for s in servicios.keys():
    fact = row[s]
    vithas = fact * servicios[s]["VITHAS"]
    osa = fact * servicios[s]["OSA"]
    abon = osa * (0.90 if row["Nivel"]=="Especialista" and row["Total_Bruto"]>promedios_nivel["Especialista"]
                  else 0.85 if row["Nivel"]=="Especialista"
                  else 0.92 if row["Nivel"]=="Consultor" and row["Total_Bruto"]>promedios_nivel["Consultor"]
                  else 0.88)
    detalle_servicios.append({
        "Servicio": s,
        "Facturación": fact,
        "VITHAS": vithas,
        "OSA": osa,
        "Abonado al Médico": abon
    })

df_detalle = pd.DataFrame(detalle_servicios)

# Fila TOTAL
totales = df_detalle[["Facturación","VITHAS","OSA","Abonado al Médico"]].sum()
fila_total = {"Servicio":"TOTAL"}
fila_total.update(totales)
df_detalle = pd.concat([df_detalle, pd.DataFrame([fila_total])], ignore_index=True)

# -------------------- Configuración AgGrid --------------------
df_aggrid = df_detalle.copy()
gb = GridOptionsBuilder.from_dataframe(df_aggrid)
gb.configure_default_column(editable=False, resizable=True)
gb.configure_column("Servicio", pinned="left", width=150)

# Gradientes distintos por columna
colores = {
    "Facturación": "rgba(52, 152, 219, {intensity})",      # azul
    "VITHAS": "rgba(52, 152, 219, {intensity})",          # celeste
    "OSA": "rgba(46, 204, 113, {intensity})",             # verde
    "Abonado al Médico": "rgba(243, 156, 18, {intensity})" # naranja
}

for col, color in colores.items():
    max_val = df_aggrid[col].max() if df_aggrid[col].max() > 0 else 1
    def gradient(params, col_max=max_val, col_color=color):
        intensity = (params.value / col_max) if params.value>0 else 0
        return {'backgroundColor': col_color.format(intensity=intensity)}
    gb.configure_column(col, cellStyle=gradient)

gridOptions = gb.build()
AgGrid(df_aggrid, gridOptions=gridOptions, update_mode=GridUpdateMode.NO_UPDATE, fit_columns_on_grid_load=True, height=400)

st.markdown(f"**Resumen:** {medico_sel} facturó {row['Total_Bruto']:.2f} €, se abonará {row['Abonado_a_Medico']:.2f} € según su nivel ({row['Nivel']}).")

# -------------------- Gráfico comparativo por nivel --------------------
st.markdown("### 📊 Comparación de abonos por nivel jerárquico")
nivel_sel = st.selectbox("Seleccione nivel jerárquico para gráfico", list(niveles.keys()))
df_nivel = df_edit[df_edit["Nivel"]==nivel_sel].copy()

df_melt = df_nivel.melt(id_vars=["Médico"], value_vars=["Total_Bruto","Total_VITHAS","Total_OSA_Disponible","Abonado_a_Medico"],
                        var_name="Concepto", value_name="Valor (€)")

fig = px.bar(df_melt, x="Médico", y="Valor (€)", color="Concepto", barmode="group",
             title=f"Comparación de abonos de médicos del nivel {nivel_sel}")
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
### 🔹 Conclusión del proceso
- Los **colores por columna** permiten identificar fácilmente Facturación, VITHAS, OSA y Abono.
- La **intensidad del color** muestra proporcionalmente cuánto aporta cada celda respecto al total de la columna.
- La tabla y gráficos permiten entender claramente **qué servicios generan más facturación y abonos**.
""")


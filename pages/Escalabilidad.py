import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Escalabilidad", layout="wide", page_icon="📊")
st.title("📊 Escalabilidad del Pago a Médicos")

st.markdown("""
El sistema de pago funciona en **tres pasos**:

1. Cada médico genera una **facturación bruta total** por servicio.
2. Esa facturación se reparte entre **VITHAS** y **OSA**, según porcentajes.
3. Del pool OSA, se calcula cuánto se le **abona al médico** según su nivel y comparación con el promedio de su grupo.
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

# Asegurar que columnas de servicios sean numéricas
for s in servicios.keys():
    df_edit[s] = pd.to_numeric(df_edit[s], errors='coerce').fillna(0.0)

# -------------------- Cálculos --------------------
df_edit["Total_Bruto"] = df_edit[list(servicios.keys())].sum(axis=1)
df_edit["Total_OSA_Disponible"] = df_edit.apply(lambda row: sum(row[s]*servicios[s]["OSA"] for s in servicios), axis=1)
df_edit["Total_VITHAS"] = df_edit.apply(lambda row: sum(row[s]*servicios[s]["VITHAS"] for s in servicios), axis=1)

# Calcular promedio por nivel
promedios_nivel = df_edit.groupby("Nivel")["Total_Bruto"].mean().to_dict()

# Mostrar métricas de promedio por nivel jerárquico
st.markdown("### 📈 Promedio de facturación por nivel jerárquico")
c1, c2 = st.columns(2)
with c1:
    st.metric("Promedio Especialistas", f"{promedios_nivel.get('Especialista',0):,.2f} €")
with c2:
    st.metric("Promedio Consultores", f"{promedios_nivel.get('Consultor',0):,.2f} €")

# Calcular abono final según reglas de promedio
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

# -------------------- Tabla detalle por servicio --------------------
st.markdown("### 👨‍⚕️ Detalle por servicio de un médico")
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

# Fila TOTAL numérica
totales = df_detalle[["Facturación","VITHAS","OSA","Abonado al Médico"]].sum()
fila_total = {"Servicio":"TOTAL"}
fila_total.update(totales)
df_detalle = pd.concat([df_detalle, pd.DataFrame([fila_total])], ignore_index=True)

# Fila % sobre Facturación total
fila_pct = {"Servicio":"% del Total"}
for col in ["Facturación","VITHAS","OSA","Abonado al Médico"]:
    fila_pct[col] = totales[col]/totales["Facturación"]*100
df_detalle = pd.concat([df_detalle, pd.DataFrame([fila_pct])], ignore_index=True)

# -------------------- Colores para destacar deducciones y abonos --------------------
def color_fila(val):
    if isinstance(val, str):
        return ""
    return "background-color: #D5F5E3; color: black"  # verde claro con texto negro

st.dataframe(
    df_detalle.style.format({
        "Facturación":"{:,.2f} €",
        "VITHAS":"{:,.2f} €",
        "OSA":"{:,.2f} €",
        "Abonado al Médico":"{:,.2f} €"
    }).applymap(color_fila, subset=["Facturación","VITHAS","OSA","Abonado al Médico"]),
    use_container_width=True
)

st.markdown(f"**Resumen:** {medico_sel} facturó {row['Total_Bruto']:.2f} €, se abonará {row['Abonado_a_Medico']:.2f} € según su nivel ({row['Nivel']}).")

# -------------------- Gráfico comparativo por nivel --------------------
st.markdown("### 📊 Comparación de abonos por nivel jerárquico")
nivel_sel = st.selectbox("Seleccione nivel jerárquico", list(niveles.keys()))
df_nivel = df_edit[df_edit["Nivel"]==nivel_sel].copy()

df_melt = df_nivel.melt(id_vars=["Médico"], value_vars=["Total_Bruto","Total_VITHAS","Total_OSA_Disponible","Abonado_a_Medico"],
                        var_name="Concepto", value_name="Valor (€)")

fig = px.bar(df_melt, x="Médico", y="Valor (€)", color="Concepto", barmode="group",
             title=f"Comparación de abonos de médicos del nivel {nivel_sel}")
st.plotly_chart(fig, use_container_width=True)

# -------------------- Explicación final --------------------
st.markdown("""
### 🔹 Conclusión del proceso
- Se parte de la **facturación total por servicio**.
- Se aplica la distribución **VITHAS/OSA**.
- Del **pool OSA**, se calcula el **abono final** según el promedio del nivel jerárquico.
- La tabla muestra detalle por servicio, fila TOTAL y fila % sobre facturación total.
- El gráfico permite comparar fácilmente **Facturación → OSA → Abonado** para todos los médicos de un nivel.
""")


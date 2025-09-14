import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Escalabilidad", layout="wide", page_icon="📊")

st.markdown("## 📊 Escalabilidad del Sistema de Pago")
st.write("""
El sistema de pago funciona en **tres pasos muy simples**:

1. Cada médico genera una **facturación bruta total** (lo que entra por consultas, cirugías, urgencias, etc.).
2. Esa facturación se reparte automáticamente entre **VITHAS** y **OSA**, según los porcentajes definidos para cada servicio.
3. Del pool OSA, se calcula cuánto se le abona al médico según su nivel (**Especialista o Consultor**) y su posición respecto al promedio del grupo.
""")

# -------------------- Cargar DataFrame --------------------
if "df_edit" not in st.session_state:
    st.error("❌ No se han cargado datos aún. Por favor, primero use la página 'Distribución VITHAS-OSA'.")
    st.stop()

df_edit = st.session_state["df_edit"].copy()
servicios = st.session_state["servicios"]

# -------------------- Selección de médicos --------------------
st.markdown("### 👨‍⚕️ Seleccione médicos para ver el detalle")
medicos_sel = st.multiselect(
    "Médicos:",
    df_edit["Médico"].unique(),
    default=[df_edit["Médico"].iloc[0]]
)

if not medicos_sel:
    st.warning("⚠️ Selecciona al menos un médico para mostrar datos.")
    st.stop()

# -------------------- Construcción de datos --------------------
comparacion_data = []

for medico_sel in medicos_sel:
    row = df_edit[df_edit["Médico"] == medico_sel].iloc[0]

    for s in servicios.keys():
        fact = row[s]
        vithas = fact * servicios[s]["VITHAS"]
        osa = fact * servicios[s]["OSA"]
        abonado = osa * row["Pct_Abono"]
        comparacion_data.append({
            "Médico": medico_sel,
            "Servicio": s,
            "Facturación": fact,
            "VITHAS": vithas,
            "OSA": osa,
            "Abonado al Médico": abonado
        })

df_comp = pd.DataFrame(comparacion_data)

# -------------------- Mostrar detalle por médico --------------------
st.markdown("### 📋 Detalle por Médico")
for medico_sel in medicos_sel:
    df_medico = df_comp[df_comp["Médico"] == medico_sel].copy()
    df_medico.loc["TOTAL"] = df_medico[["Facturación", "VITHAS", "OSA", "Abonado al Médico"]].sum()
    df_medico.loc["TOTAL", "Médico"] = medico_sel
    df_medico.loc["TOTAL", "Servicio"] = "TOTAL"

    st.subheader(f"👨‍⚕️ {medico_sel}")
    st.dataframe(
        df_medico.style.format({
            "Facturación": "{:,.2f} €",
            "VITHAS": "{:,.2f} €",
            "OSA": "{:,.2f} €",
            "Abonado al Médico": "{:,.2f} €"
        }),
        use_container_width=True
    )

# -------------------- Gráfico comparativo --------------------
st.markdown("### 📊 Comparación entre médicos")

df_melt = df_comp.melt(
    id_vars=["Médico", "Servicio"],
    value_vars=["Facturación", "VITHAS", "OSA", "Abonado al Médico"],
    var_name="Concepto",
    value_name="Valor (€)"
)

fig = px.bar(
    df_melt,
    x="Servicio",
    y="Valor (€)",
    color="Concepto",
    barmode="group",
    facet_col="Médico",
    text_auto=".2s",
    title="Comparación de distribución por servicio y médico"
)
fig.update_layout(yaxis_title="€", xaxis_title="Servicio")
st.plotly_chart(fig, use_container_width=True)

# -------------------- Conclusión --------------------
for medico_sel in medicos_sel:
    row = df_edit[df_edit["Médico"] == medico_sel].iloc[0]
    st.success(f"""
    👉 **{medico_sel}** facturó un total bruto de **{row['Total_Bruto']:,.2f} €**.  
    - VITHAS se queda con su parte según servicio.  
    - El pool OSA suma lo correspondiente.  
    - Finalmente, al médico se le abonó **{row['Abonado_a_Medico']:,.2f} €**  
      (**{row['Pct_Abono']:.0%}** de su OSA disponible).
    """)

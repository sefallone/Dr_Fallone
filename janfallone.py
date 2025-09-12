import streamlit as st
import plotly.express as px
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Distribución de Facturación", layout="wide")

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
    }
    .metric-container {
        background-color: #325EB8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }
    .stMetric {
        font-weight: bold;
        color: #2E4053;
    }
    .stExpander {
        background-color: #325EB8;
        border: 1px solid #E0E0E0;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("💼 Distribución de Facturación | VITHAS - OSA")

menu = st.sidebar.radio("Selecciona una sección", ["Dashboard Actual", "Proyección 2026-2032"]) 

# -------------------- METAS (CONFIGURABLES) --------------------
st.sidebar.header("⚙️ Metas y Umbrales de Distribución")
meta_junior = st.sidebar.number_input("Meta Junior (€/año)", min_value=0.0, step=1000.0, value=150000.0, key="meta_junior")
meta_senior = st.sidebar.number_input("Meta Senior (€/año)", min_value=0.0, step=1000.0, value=250000.0, key="meta_senior")
meta_general = st.sidebar.number_input("Meta General (€/año)", min_value=0.0, step=1000.0, value=350000.0, key="meta_general")

metas = {
    "junior": meta_junior,
    "senior": meta_senior,
    "general": meta_general
}

# -------------------- FUNCIONES --------------------
def porcentaje_por_facturacion(bruto, metas):
    """Devuelve el porcentaje a aplicar según los umbrales (metas).
    Reglas:
      - Hasta meta_junior: 70%
      - Hasta meta_senior: 80%
      
    """
    if bruto <= metas["junior"]:
        return 0.85
    elif bruto <= metas["senior"]:
        return 0.92
    else:
        return 1.00


def aplicar_porcentaje_personal(bruto, neto_osa, metas):
    pct = porcentaje_por_facturacion(bruto, metas)
    neto_final = neto_osa * pct
    return neto_final, pct


def mostrar_metrica_medico(nombre, bruto, neto_osa, nivel, metas):
    neto_final, pct = aplicar_porcentaje_personal(bruto, neto_osa, metas)
    if bruto == 0:
        delta = "0%"
    else:
        diferencia = (neto_final - bruto) / bruto * 100
        delta = f"{diferencia:+.1f}%"
    etiqueta = f"{nombre} | Nivel: {nivel} | {int(pct*100)}%"
    st.metric(label=etiqueta, value=f"{neto_final:,.2f} €", delta=delta, help=f"Facturado bruto: {bruto:,.2f} € \nNeto OSA asignado (antes de nivel): {neto_osa:,.2f} €")
    return neto_final


# -------------------- DASHBOARD --------------------
if menu == "Dashboard Actual":

    # --- INPUT DE FACTURACIÓN ---
    with st.expander("📋 Ingresar Facturación por Especialidad"):
        st.subheader("💳 Facturación CCEE")
    
        # OSB - 3 médicos
        st.markdown("**💼 OSB (Hombro y Codo)**")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            ccee_OSB_1 = st.number_input("Médico 1 (CCEE)", key="ccee_osb_1", min_value=0.0, step=10.0)
            nivel_osb_1 = st.selectbox("Nivel Médico 1", ["Junior", "Senior", "General"], key="nivel_osb_1")
        with c2:
            ccee_OSB_2 = st.number_input("Médico 2 (CCEE)", key="ccee_osb_2", min_value=0.0, step=10.0)
            nivel_osb_2 = st.selectbox("Nivel Médico 2", ["Junior", "Senior", "General"], key="nivel_osb_2")
        with c3:
            ccee_OSB_3 = st.number_input("Médico 3 (CCEE)", key="ccee_osb_3", min_value=0.0, step=10.0)
            nivel_osb_3 = st.selectbox("Nivel Médico 3", ["Junior", "Senior", "General"], key="nivel_osb_3")
        with c4:
            ccee_OSB = ccee_OSB_1 + ccee_OSB_2 + ccee_OSB_3
            st.metric("Total OSB", f"{ccee_OSB:,.2f} €")
    
        # SMOB - 4 médicos
        st.markdown("**💼 SMOB (Rodilla)**")
        s1, s2, s3, s4, s5 = st.columns(5)
        with s1:
            ccee_SMOB_1 = st.number_input("Médico 1 (CCEE)", key="ccee_smob_1", min_value=0.0, step=10.0)
            nivel_smob_1 = st.selectbox("Nivel SMOB 1", ["Junior", "Senior", "General"], key="nivel_smob_1")
        with s2:
            ccee_SMOB_2 = st.number_input("Médico 2 (CCEE)", key="ccee_smob_2", min_value=0.0, step=10.0)
            nivel_smob_2 = st.selectbox("Nivel SMOB 2", ["Junior", "Senior", "General"], key="nivel_smob_2")
        with s3:
            ccee_SMOB_3 = st.number_input("Médico 3 (CCEE)", key="ccee_smob_3", min_value=0.0, step=10.0)
            nivel_smob_3 = st.selectbox("Nivel SMOB 3", ["Junior", "Senior", "General"], key="nivel_smob_3")
        with s4:
            ccee_SMOB_4 = st.number_input("Médico 4 (CCEE)", key="ccee_smob_4", min_value=0.0, step=10.0)
            nivel_smob_4 = st.selectbox("Nivel SMOB 4", ["Junior", "Senior", "General"], key="nivel_smob_4")
        with s5:
            ccee_SMOB = ccee_SMOB_1 + ccee_SMOB_2 + ccee_SMOB_3 + ccee_SMOB_4
            st.metric("Total SMOB", f"{ccee_SMOB:,.2f} €")
    
        # JPP - 2 médicos
        st.markdown("**💼 JPP (Pie y Tobillo)**")
        j1, j2, j3 = st.columns(3)
        with j1:
            ccee_JPP_1 = st.number_input("Médico 1 (CCEE)", key="ccee_jpp_1", min_value=0.0, step=10.0)
            nivel_jpp_1 = st.selectbox("Nivel JPP 1", ["Junior", "Senior", "General"], key="nivel_jpp_1")
        with j2:
            ccee_JPP_2 = st.number_input("Médico 2 (CCEE)", key="ccee_jpp_2", min_value=0.0, step=10.0)
            nivel_jpp_2 = st.selectbox("Nivel JPP 2", ["Junior", "Senior", "General"], key="nivel_jpp_2")
        with j3:
            ccee_JPP = ccee_JPP_1 + ccee_JPP_2
            st.metric("Total JPP", f"{ccee_JPP:,.2f} €")
    
        facturacion_ccee = ccee_OSB + ccee_SMOB + ccee_JPP
    
        st.subheader("🔪 Facturación Quirúrgica")
    
        # OSB
        st.markdown("**🔧 OSB (Hombro y Codo)**")
        q1, q2, q3, q4 = st.columns(4)
        with q1:
            q_OSB_1 = st.number_input("Médico 1 (Q)", key="q_osb_1", min_value=0.0, step=100.0)
        with q2:
            q_OSB_2 = st.number_input("Médico 2 (Q)", key="q_osb_2", min_value=0.0, step=100.0)
        with q3:
            q_OSB_3 = st.number_input("Médico 3 (Q)", key="q_osb_3", min_value=0.0, step=100.0)
        with q4:
            q_OSB = q_OSB_1 + q_OSB_2 + q_OSB_3
            st.metric("Total OSB", f"{q_OSB:,.2f} €")
    
        # SMOB
        st.markdown("**🔧 SMOB (Rodilla)**")
        q5, q6, q7, q8, q9 = st.columns(5)
        with q5:
            q_SMOB_1 = st.number_input("Médico 1 (Q)", key="q_smob_1", min_value=0.0, step=100.0)
        with q6:
            q_SMOB_2 = st.number_input("Médico 2 (Q)", key="q_smob_2", min_value=0.0, step=100.0)
        with q7:
            q_SMOB_3 = st.number_input("Médico 3 (Q)", key="q_smob_3", min_value=0.0, step=100.0)
        with q8:
            q_SMOB_4 = st.number_input("Médico 4 (Q)", key="q_smob_4", min_value=0.0, step=15000.0)
        with q9:
            q_SMOB = q_SMOB_1 + q_SMOB_2 + q_SMOB_3 + q_SMOB_4
            st.metric("Total SMOB", f"{q_SMOB:,.2f} €")
    
        # JPP
        st.markdown("**🔧 JPP (Pie y Tobillo)**")
        q10, q11, q12 = st.columns(3)
        with q10:
            q_JPP_1 = st.number_input("Médico 1 (Q)", key="q_jpp_1", min_value=0.0, step=100.0)
        with q11:
            q_JPP_2 = st.number_input("Médico 2 (Q)", key="q_jpp_2", min_value=0.0, step=100.0)
        with q12:
            q_JPP = q_JPP_1 + q_JPP_2
            st.metric("Total JPP", f"{q_JPP:,.2f} €")
    
        facturacion_quirurgico = q_OSB + q_SMOB + q_JPP
    
        st.subheader("🚨 Facturación Urgencias")
    
        # OSB
        st.markdown("**🚑 OSB (Hombro y Codo)**")
        u1, u2, u3, u4 = st.columns(4)
        with u1:
            u_OSB_1 = st.number_input("Médico 1 (U)", key="u_osb_1", min_value=0.0, step=100.0)
        with u2:
            u_OSB_2 = st.number_input("Médico 2 (U)", key="u_osb_2", min_value=0.0, step=100.0)
        with u3:
            u_OSB_3 = st.number_input("Médico 3 (U)", key="u_osb_3", min_value=0.0, step=100.0)
        with u4:
            u_OSB = u_OSB_1 + u_OSB_2 + u_OSB_3
            st.metric("Total OSB", f"{u_OSB:,.2f} €")
    
        # SMOB
        st.markdown("**🚑 SMOB (Rodilla)**")
        u5, u6, u7, u8, u9 = st.columns(5)
        with u5:
            u_SMOB_1 = st.number_input("Médico 1 (U)", key="u_smob_1", min_value=0.0, step=100.0)
        with u6:
            u_SMOB_2 = st.number_input("Médico 2 (U)", key="u_smob_2", min_value=0.0, step=100.0)
        with u7:
            u_SMOB_3 = st.number_input("Médico 3 (U)", key="u_smob_3", min_value=0.0, step=100.0)
        with u8:
            u_SMOB_4 = st.number_input("Médico 4 (U)", key="u_smob_4", min_value=0.0, step=100.0)
        with u9:
            u_SMOB = u_SMOB_1 + u_SMOB_2 + u_SMOB_3 + u_SMOB_4
            st.metric("Total SMOB", f"{u_SMOB:,.2f} €")
    
        # JPP
        st.markdown("**🚑 JPP (Pie y Tobillo)**")
        u10, u11, u12 = st.columns(3)
        with u10:
            u_JPP_1 = st.number_input("Médico 1 (U)", key="u_jpp_1", min_value=0.0, step=100.0)
        with u11:
            u_JPP_2 = st.number_input("Médico 2 (U)", key="u_jpp_2", min_value=0.0, step=100.0)
        with u12:
            u_JPP = u_JPP_1 + u_JPP_2
            st.metric("Total JPP", f"{u_JPP:,.2f} €")
    
        facturacion_urgencias = u_OSB + u_SMOB + u_JPP

    # --- DISTRIBUCIONES ---
    vithas_total = facturacion_ccee * 0.30 + facturacion_quirurgico * 0.10 + facturacion_urgencias * 0.50
    osa_total = facturacion_ccee * 0.70 + facturacion_quirurgico * 0.90 + facturacion_urgencias * 0.50
    
    # --- INPUT: % QUE ME QUEDO DE OSA ---
    mi_porcentaje = st.slider("Selecciona tu porcentaje dentro de OSA (%)", 0, 100, 30)
    mi_porcentaje_decimal = mi_porcentaje / 100
    
    osa_beneficios = osa_total * mi_porcentaje_decimal
    osa_restante = osa_total - osa_beneficios
    
    osa_OSB = ((ccee_OSB * 0.70) + (q_OSB * 0.90) + (u_OSB * 0.50)) * (1 - mi_porcentaje_decimal)
    osa_SMOB = ((ccee_SMOB * 0.70) + (q_SMOB * 0.90) + (u_SMOB * 0.50)) * (1 - mi_porcentaje_decimal)
    osa_JPP = ((ccee_JPP * 0.70) + (q_JPP * 0.90) + (u_JPP * 0.50)) * (1 - mi_porcentaje_decimal)
    
    # --- DISTRIBUCIÓN INTERNA DEL % PERSONAL ---
    gf = osa_beneficios * 0.60
    jp = osa_beneficios * 0.225
    jpp_p = osa_beneficios * 0.075
    gf2 = osa_beneficios * 0.05
    
    # --- TOTALES ---
    total_facturacion = facturacion_ccee + facturacion_quirurgico + facturacion_urgencias
    total_distribuciones = {
        "OSA": osa_beneficios,
        "OSB (Hombro)": osa_OSB,
        "SMOB (Rodilla)": osa_SMOB,
        "JPP (Pie)": osa_JPP
    }
    
    st.markdown("---")
    st.header("📊 Totales de Facturación")
    with st.container():
        k0, k1, k2, k3, = st.columns(4)
        with k0:
            st.metric("💰 Total Facturación", f"{total_facturacion:,.2f} €")
        with k1:
            st.metric("CCEE", f"{facturacion_ccee:,.2f} €")
        with k2:
            st.metric("Quirúrgico", f"{facturacion_quirurgico:,.2f} €")
        with k3:
            st.metric("Urgencias", f"{facturacion_urgencias:,.2f} €")
    
    st.markdown("---")
    st.header("📊 Totales Hospital / Servicio de Traumatología")
    with st.container():
        m1, m2 = st.columns(2)
        with m1:
            st.metric("💙 Total VITHAS", f"{vithas_total:,.2f} €")
        with m2:
            st.metric("🟩 Total OSA", f"{osa_total:,.2f} €")
    
    st.markdown("---")
    st.header("📊 OSA Beneficios ")
    with st.container():
        z1, z2, z3, z4, z5, z6 = st.columns(6)
        with z1:
            st.metric("🔺 Total OSA BENEFICIOS", f"{osa_beneficios:,.2f} €")
        with z2:
            st.metric("🔺 Giancarlo Fallone", f"{gf:,.2f} €")
        with z3:
            st.metric("🔺 Jordi Puigdellívol", f"{jp:,.2f} €")
        with z4:
            st.metric("🔺 Juan Pablo Ortega", f"{jpp_p:,.2f} €")
        with z5:
            st.metric("🔺 Resto a repartir", f"{gf2:,.2f} €")
        with z6:
            st.metric("🔺 Total OSA DISTRIBUIR", f"{osa_restante:,.2f} €")
    
    # --- DISTRIBUCIÓN POR MÉDICO ---
    st.markdown("---")
    st.header("📊 OSA Distribución por Médico")

    resultados_por_medico = {}  # para exportar

    # --- OSB ---
    st.subheader("🔹 OSB (Hombro y Codo)")
    total_OSB_input = {
        "Médico 1": ccee_OSB_1 + q_OSB_1 + u_OSB_1,
        "Médico 2": ccee_OSB_2 + q_OSB_2 + u_OSB_2,
        "Médico 3": ccee_OSB_3 + q_OSB_3 + u_OSB_3,
    }
    niveles_OSB = {
        "Médico 1": nivel_osb_1,
        "Médico 2": nivel_osb_2,
        "Médico 3": nivel_osb_3,
    }
    total_OSB_suma = sum(total_OSB_input.values())
    if total_OSB_suma > 0:
        dist_OSB = {nombre: (valor / total_OSB_suma) * osa_OSB for nombre, valor in total_OSB_input.items()}
    else:
        dist_OSB = {nombre: 0 for nombre in total_OSB_input}
    
    cols = st.columns(len(dist_OSB))
    for idx, (nombre, bruto) in enumerate(total_OSB_input.items()):
        neto_osa = dist_OSB[nombre]
        nivel = niveles_OSB[nombre]
        with cols[idx]:
            neto_final = mostrar_metrica_medico(nombre, bruto, neto_osa, nivel, metas)
        resultados_por_medico[nombre + " (OSB)"] = {"bruto": bruto, "neto": neto_final, "nivel": nivel}

    # --- SMOB ---
    st.subheader("🔹 SMOB (Rodilla)")
    total_SMOB_input = {
        "Médico 1": ccee_SMOB_1 + q_SMOB_1 + u_SMOB_1,
        "Médico 2": ccee_SMOB_2 + q_SMOB_2 + u_SMOB_2,
        "Médico 3": ccee_SMOB_3 + q_SMOB_3 + u_SMOB_3,
        "Médico 4": ccee_SMOB_4 + q_SMOB_4 + u_SMOB_4,
    }
    niveles_SMOB = {
        "Médico 1": nivel_smob_1,
        "Médico 2": nivel_smob_2,
        "Médico 3": nivel_smob_3,
        "Médico 4": nivel_smob_4,
    }
    total_SMOB_suma = sum(total_SMOB_input.values())
    if total_SMOB_suma > 0:
        dist_SMOB = {nombre: (valor / total_SMOB_suma) * osa_SMOB for nombre, valor in total_SMOB_input.items()}
    else:
        dist_SMOB = {nombre: 0 for nombre in total_SMOB_input}
    
    cols = st.columns(len(dist_SMOB))
    for idx, (nombre, bruto) in enumerate(total_SMOB_input.items()):
        neto_osa = dist_SMOB[nombre]
        nivel = niveles_SMOB[nombre]
        with cols[idx]:
            neto_final = mostrar_metrica_medico(nombre, bruto, neto_osa, nivel, metas)
        resultados_por_medico[nombre + " (SMOB)"] = {"bruto": bruto, "neto": neto_final, "nivel": nivel}

    # --- JPP ---
    st.subheader("🔹 JPP (Pie y Tobillo)")
    total_JPP_input = {
        "Médico 1": ccee_JPP_1 + q_JPP_1 + u_JPP_1,
        "Médico 2": ccee_JPP_2 + q_JPP_2 + u_JPP_2,
    }
    niveles_JPP = {
        "Médico 1": nivel_jpp_1,
        "Médico 2": nivel_jpp_2,
    }
    total_JPP_suma = sum(total_JPP_input.values())
    if total_JPP_suma > 0:
        dist_JPP = {nombre: (valor / total_JPP_suma) * osa_JPP for nombre, valor in total_JPP_input.items()}
    else:
        dist_JPP = {nombre: 0 for nombre in total_JPP_input}
    
    cols = st.columns(len(dist_JPP))
    for idx, (nombre, bruto) in enumerate(total_JPP_input.items()):
        neto_osa = dist_JPP[nombre]
        nivel = niveles_JPP[nombre]
        with cols[idx]:
            neto_final = mostrar_metrica_medico(nombre, bruto, neto_osa, nivel, metas)
        resultados_por_medico[nombre + " (JPP)"] = {"bruto": bruto, "neto": neto_final, "nivel": nivel}

    # --- GRÁFICO ---
    st.markdown("---")
    st.subheader("📈 Distribución OSA")
    fig = px.pie(
        names=list(total_distribuciones.keys()),
        values=list(total_distribuciones.values()),
        title="Distribución Total de Facturación",
        color_discrete_sequence=["#003A6F", "#2E8B57", "#1ABC9C", "#F4D03F"]
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

    # --- DESCARGA EXCEL DASHBOARD ---
    st.markdown("---")
    st.subheader("⬇️ Descargar Datos del Dashboard en Excel")

    # DataFrame resumen
    df_dashboard = pd.DataFrame({
        "Concepto": [
            "Total Facturación", "Facturación CCEE", "Facturación Quirúrgico", "Facturación Urgencias",
            "Total VITHAS", "Total OSA"
        ],
        "Valor (€)": [
            total_facturacion, facturacion_ccee, facturacion_quirurgico, facturacion_urgencias,
            vithas_total, osa_total
        ]
    })

    # Añadir detalle por médico al Excel
    df_medicos = pd.DataFrame.from_dict(resultados_por_medico, orient='index')
    df_medicos.index.name = 'Médico (Servicio)'

    def to_excel_dashboard(df1, df2):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df1.to_excel(writer, index=False, sheet_name='Dashboard')
            df2.to_excel(writer, sheet_name='Detalle_Medicos')
        processed_data = output.getvalue()
        return processed_data

    excel_dashboard = to_excel_dashboard(df_dashboard, df_medicos)
    st.download_button(
        label="📅 Descargar Excel del Dashboard",
        data=excel_dashboard,
        file_name="dashboard_facturacion_actual_completo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


elif menu == "Proyección 2026-2032":
    st.header("📈 Proyección de Facturación (2026-2032)")
    base = st.number_input("💼 Ingresa la facturación base (año 2026)", min_value=0.0, step=100.0, value=100000.0)

    st.subheader("🔄 Porcentaje de crecimiento por año")
    crecimiento_por_año = {}
    años = list(range(2026, 2033))
    for anio in años:
        crecimiento_por_año[anio] = st.slider(f"Crecimiento {anio} (%)", 0, 100, 30, key=f"crec_{anio}")

    proyecciones = []
    valor_actual = base
    for anio in años:
        crecimiento = crecimiento_por_año[anio] / 100
        valor_actual *= (1 + crecimiento)
        proyecciones.append(valor_actual)

    df_proj = pd.DataFrame({"Año": años, "Proyección Total (€)": proyecciones})

    st.subheader("📊 Proyección Anual")
    st.line_chart(df_proj.set_index("Año"))
    st.dataframe(df_proj.style.format({"Proyección Total (€)": "{:.2f}"}))

    st.markdown("---")
    st.subheader("📌 Desglose por Tipo de Facturación")
    ccee_pct = 0.3
    quir_pct = 0.4
    urg_pct = 0.3

    df_proj["CCEE (€)"] = df_proj["Proyección Total (€)"] * ccee_pct
    df_proj["Quirúrgico (€)"] = df_proj["Proyección Total (€)"] * quir_pct
    df_proj["Urgencias (€)"] = df_proj["Proyección Total (€)"] * urg_pct

    fig_tipo = px.area(
        df_proj,
        x="Año",
        y=["CCEE (€)", "Quirúrgico (€)", "Urgencias (€)"],
        title="Proyección por Tipo de Facturación (2026-2032)",
        labels={"value": "Facturación (€)", "variable": "Tipo"},
        color_discrete_sequence=["#1f77b4", "#2ca02c", "#ff7f0e"]
    )
    st.plotly_chart(fig_tipo, use_container_width=True)
    st.dataframe(df_proj.style.format("{:.2f}"))

    st.markdown("---")
    st.subheader("⬇️ Descargar Datos en Excel")
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Proyeccion')
        processed_data = output.getvalue()
        return processed_data

    excel_data = to_excel(df_proj)
    st.download_button(
        label="📅 Descargar Excel Proyección",
        data=excel_data,
        file_name="proyeccion_facturacion_2026_2032.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

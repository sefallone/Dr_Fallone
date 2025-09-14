import streamlit as st
import pandas as pd
import plotly.express as px
import math

st.set_page_config(page_title="Escalabilidad", layout="wide", page_icon="📊")
st.markdown("""
<div style="background: linear-gradient(135deg, #122E13, #0D2B0F); 
            padding: 20px; 
            border-radius: 15px; 
            text-align: center; 
            color: yellow;
            margin-bottom: 20px;">
    <h1 style="margin: 0; font-size: 2.5rem;"> ORTHOPAEDIC SPECIALIST ALLIANCE </h1>
    <p style="margin: 5px 0 0 0; font-size: 1.2rem;">📊 Sistema de Escalabilidad de Pagos a Médicos</p>
</div>
""", unsafe_allow_html=True)


# -------------------- Definición de niveles y servicios --------------------
niveles = {
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

# Usamos markdown en lugar de st.success/st.warning para evitar problemas con DeltaGenerator
if row["Total_Bruto"] > promedio_nivel:
    mensaje_html = f"""
    <div style="background-color: #d4edda; color: #155724; padding: 12px; border-radius: 5px; border-left: 4px solid #28a745; margin: 10px 0;">
        <strong>¡EXCELENTE RENDIMIENTO!</strong> Doctor {medico_sel}, usted está por <strong>ENCIMA</strong> del promedio de facturación de su grupo.
    </div>
    """
else:
    mensaje_html = f"""
    <div style="background-color: #fff3cd; color: #856404; padding: 12px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 10px 0;">
        <strong>ATENCIÓN:</strong> Doctor {medico_sel}, usted está por <strong>DEBAJO</strong> del promedio de facturación de su grupo.
    </div>
    """

st.markdown(mensaje_html, unsafe_allow_html=True)

# -------------------- Cálculos para el potencial de ganancia --------------------
# Determinar porcentajes actuales y potenciales
if nivel_medico == "Especialista":
    pct_actual = 0.85 if row["Total_Bruto"] <= promedios_nivel[nivel_medico] else 0.90
    pct_potencial = 0.90
else:  # Consultor
    pct_actual = 0.88 if row["Total_Bruto"] <= promedios_nivel[nivel_medico] else 0.92
    pct_potencial = 0.92

abono_actual = row["Total_OSA_Disponible"] * pct_actual
abono_potencial = row["Total_OSA_Disponible"] * pct_potencial
diferencia_abono = abono_potencial - abono_actual
porcentaje_actual = (abono_actual / row["Total_Bruto"] * 100) if row["Total_Bruto"] > 0 else 0
porcentaje_potencial = (abono_potencial / row["Total_Bruto"] * 100) if row["Total_Bruto"] > 0 else 0

osa_final_actual = row["Total_OSA_Disponible"] - abono_actual
osa_final_potencial = row["Total_OSA_Disponible"] - abono_potencial

# -------------------- Nuevo diseño de KPIs para el médico --------------------

# Título con nombre del médico
st.markdown(f"### 📝 Reporte de Rendimiento del Médico - <span style='font-size:1.3em; color:#2e7d32;'>Dr. {medico_sel}</span>", unsafe_allow_html=True)

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

# -------------------- POTENCIAL DE INGRESOS --------------------
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
        <h2 style="margin: 10px 0; font-size: 2rem;">{abono_potencial:,.2f} €</h2>
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

# -------------------- POTENCIAL DE ESCALABILIDAD --------------------
st.markdown("---")
st.subheader("🚀 Potencial de Escalabilidad")

kpi_cols3 = st.columns(2)

if diferencia_abono > 0:
    # Caso: No superó el promedio
    kpi_cols3[0].markdown(f"""
    <div style="background: linear-gradient(135deg, #d32f2f, #f44336); padding: 20px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h4 style="margin: 0; font-size: 1.1rem;">Pérdida Estimada</h4>
        <h2 style="margin: 10px 0; font-size: 2rem;">{diferencia_abono:,.2f} €</h2>
        <p style="margin: 0; font-size: 1rem;">Por no alcanzar tu potencial máximo</p>
    </div>
    """, unsafe_allow_html=True)
    
    kpi_cols3[1].markdown(f"""
    <div style="background-color: #ffebee; color: #c62828; padding: 20px; border-radius: 10px; border-left: 4px solid #f44336;">
        <h4 style="margin: 0 0 15px 0; font-size: 1.1rem;">⚠️ Oportunidad de mejora</h4>
        <p style="margin: 0; font-size: 1rem;">
            <strong>Esta es la cantidad que estás dejando de percibir por no alcanzar el promedio de tu nivel.</strong> 
            Superar el promedio es el primer paso para convertirte en socio de OSA y acceder a mayores beneficios.
            Recuerda que depende solo de ti, OSA te abona tu esfuerzo!!.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
else:
    # Caso: Superó el promedio
    kpi_cols3[0].markdown(f"""
    <div style="background: linear-gradient(135deg, #2e7d32, #43a047); padding: 20px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h4 style="margin: 0; font-size: 1.1rem;">Potencial Alcanzado</h4>
        <h2 style="margin: 10px 0; font-size: 2rem;">{abono_potencial:,.2f} €</h2>
        <p style="margin: 0; font-size: 1rem;">Máximo rendimiento obtenido</p>
    </div>
    """, unsafe_allow_html=True)
    
    kpi_cols3[1].markdown(f"""
    <div style="background-color: #e8f5e9; color: #2e7d32; padding: 20px; border-radius: 10px; border-left: 4px solid #4caf50;">
        <h4 style="margin: 0 0 15px 0; font-size: 1.1rem;">🎯 Excelente rendimiento</h4>
        <p style="margin: 0; font-size: 1rem;">
            <strong>Este es el camino para convertirte en socio de OSA.</strong> 
            Mantén este nivel de desempeño para acceder a beneficios exclusivos y mayores porcentajes de retribución.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Gráfico de comparación
st.markdown("#### 📊 Comparativa de Potencial")
comparativa_data = {
    'Escenario': ['Actual', 'Potencial'],
    'Ingresos (€)': [abono_actual, abono_potencial]
}
df_comparativa = pd.DataFrame(comparativa_data)

fig_comparativa = px.bar(df_comparativa, x='Escenario', y='Ingresos (€)', 
                         color='Escenario',
                         color_discrete_map={'Actual': '#43a047', 'Potencial': '#1976d2'},
                         text_auto='.2s',
                         title=f"Comparativa de Potencial - Dr. {medico_sel}")

fig_comparativa.update_traces(texttemplate='%{y:,.0f} €', textposition='outside')
fig_comparativa.update_layout(showlegend=False)
st.plotly_chart(fig_comparativa, use_container_width=True)

# -------------------- DESGLOSE POR SERVICIO --------------------
st.markdown("---")
st.subheader("🧮 Desglose por Servicio")

# Calcular abono por servicio
servicios_con_facturacion = {}
for servicio in servicios.keys():
    if row[servicio] > 0:
        facturado = row[servicio]
        osa_disponible = facturado * servicios[servicio]["OSA"]
        abono_servicio = osa_disponible * (pct_potencial if row["Total_Bruto"] > promedio_nivel else pct_actual)
        servicios_con_facturacion[servicio] = {
            'facturado': facturado,
            'abonado': abono_servicio,
            'porcentaje_abono': (abono_servicio / facturado * 100) if facturado > 0 else 0
        }

# Mostrar KPIs por servicio
if servicios_con_facturacion:
    num_cols = 3  # 3 columnas para mejor visualización
    num_filas = math.ceil(len(servicios_con_facturacion) / num_cols)
    
    colores_servicios = ["#2e7d32", "#388e3c", "#43a047", "#4caf50", "#66bb6a", "#81c784", "#a5d6a7", "#c8e6c9"]
    
    for i in range(num_filas):
        cols_servicio = st.columns(num_cols)
        for j in range(num_cols):
            idx = i * num_cols + j
            if idx < len(servicios_con_facturacion):
                servicio = list(servicios_con_facturacion.keys())[idx]
                datos = servicios_con_facturacion[servicio]
                color_idx = idx % len(colores_servicios)
                
                cols_servicio[j].markdown(f"""
                <div style="background-color: {colores_servicios[color_idx]}; border-radius: 10px; padding: 15px; color: white; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h5 style="margin: 0 0 10px 0; font-size: 1rem; font-weight: bold;">{servicio}</h5>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-size: 0.85rem;">Facturado:</span>
                        <span style="font-size: 0.85rem; font-weight: bold;">{datos['facturado']:,.2f} €</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-size: 0.85rem;">Abonado:</span>
                        <span style="font-size: 0.85rem; font-weight: bold;">{datos['abonado']:,.2f} €</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size: 0.85rem;">% Abono:</span>
                        <span style="font-size: 0.85rem; font-weight: bold;">{datos['porcentaje_abono']:.1f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Servicios sin facturación
servicios_sin_facturacion = [s for s in servicios.keys() if row[s] == 0]
if servicios_sin_facturacion:
    st.info(f"**Servicios sin facturación:** {', '.join(servicios_sin_facturacion)}")

# -------------------- RESUMEN TOTAL POR SERVICIOS --------------------
st.markdown("---")
st.subheader("📊 Resumen de Rendimiento por Servicios")

# Crear DataFrame para el resumen
resumen_data = []
for servicio, datos in servicios_con_facturacion.items():
    resumen_data.append({
        'Servicio': servicio,
        'Facturado (€)': datos['facturado'],
        'Abonado (€)': datos['abonado'],
        '% Abono': datos['porcentaje_abono']
    })

if resumen_data:
    df_resumen = pd.DataFrame(resumen_data)
    
    # Formatear números para mejor visualización
    df_resumen_display = df_resumen.copy()
    df_resumen_display['Facturado (€)'] = df_resumen_display['Facturado (€)'].apply(lambda x: f"{x:,.2f} €")
    df_resumen_display['Abonado (€)'] = df_resumen_display['Abonado (€)'].apply(lambda x: f"{x:,.2f} €")
    df_resumen_display['% Abono'] = df_resumen_display['% Abono'].apply(lambda x: f"{x:.1f}%")
    
    # Mostrar tabla de resumen
    st.dataframe(df_resumen_display, use_container_width=True, hide_index=True)
    
    # Gráfico de rendimiento por servicio
    fig_servicios = px.bar(df_resumen, x='Servicio', y='Facturado (€)', 
                          title=f"Facturación por Servicio - Dr. {medico_sel}",
                          text='Facturado (€)',
                          color='Servicio')
    fig_servicios.update_traces(texttemplate='%{text:,.0f} €', textposition='outside')
    fig_servicios.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig_servicios, use_container_width=True)

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

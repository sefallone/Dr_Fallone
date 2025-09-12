import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Distribución VITHAS - OSA (Reestructurado)", layout="wide")

# -------------------- Estilos Mejorados --------------------
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .main-header { font-size: 2.5rem; color: #1f77b4; margin-bottom: 1rem; }
    .section-header { font-size: 1.8rem; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 0.3rem; margin-top: 2rem; }
    .metric-card { background-color: #f8f9fa; border-radius: 0.5rem; padding: 1rem; border-left: 4px solid #3498db; }
    .positive-metric { border-left: 4px solid #27ae60; }
    .negative-metric { border-left: 4px solid #e74c3c; }
    .dataframe { border-radius: 0.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">💼 Distribución de Facturación | VITHAS - OSA</h1>', unsafe_allow_html=True)
st.markdown("**Sistema de cálculo y distribución de ingresos**")

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

st.markdown('<h2 class="section-header">📋 Ingresar facturación por médico y servicio</h2>', unsafe_allow_html=True)
st.info("Introduce los importes de facturación para cada médico y servicio. El total bruto se calculará automáticamente.")

# data_editor permite edición tipo hoja de cálculo
df_edit = st.data_editor(df_base, num_rows="dynamic", use_container_width=True)

# Asegurarnos de que las columnas de servicios sean numéricas
for s in servicios.keys():
    df_edit[s] = pd.to_numeric(df_edit[s], errors='coerce').fillna(0.0)

# -------------------- Cálculos: totales por médico, por servicio y por nivel --------------------
# Total bruto por médico (antes de separar VITHAS / OSA) - SIN DEDUCCIONES
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
st.markdown('<h2 class="section-header">📊 Resumen General de Facturación</h2>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💰 Total Facturación Bruta", f"{total_bruto:,.2f} €", help="Suma total de todos los servicios sin deducciones")
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🏥 Total VITHAS", f"{total_vithas:,.2f} €", help="Porción que corresponde a VITHAS según los porcentajes establecidos")
    st.markdown('</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🟩 Total OSA (Pool)", f"{total_osa:,.2f} €", help="Pool total de OSA disponible para distribución")
    st.markdown('</div>', unsafe_allow_html=True)
with c4:
    card_class = "metric-card positive-metric" if osa_saldo_final >= 0 else "metric-card negative-metric"
    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
    st.metric("⚖️ Saldo OSA Final", f"{osa_saldo_final:,.2f} €", help="Saldo remanente en OSA después de todos los abonos")
    st.markdown('</div>', unsafe_allow_html=True)

# Info adicional
st.info(f"""
**Detalles del cálculo:**
- Facturación Bruta Total: {total_bruto:,.2f} € (100%)
- Porción VITHAS: {total_vithas:,.2f} € ({total_vithas/total_bruto*100:.1f}%)
- Pool OSA: {total_osa:,.2f} € ({total_osa/total_bruto*100:.1f}%)
- Total abonado a médicos: {total_abonado_a_medicos:,.2f} € ({total_abonado_a_medicos/total_osa*100:.1f}% del pool OSA)
""")

st.markdown("---")
st.markdown('<h2 class="section-header">📌 Distribución por Servicio</h2>', unsafe_allow_html=True)

serv_df = pd.DataFrame({
    'Servicio': list(totales_por_servicio.keys()),
    'Facturación_Total': list(totales_por_servicio.values()),
    'VITHAS': [totales_vithas_por_servicio[s] for s in totales_por_servicio.keys()],
    'OSA': [totales_osa_por_servicio[s] for s in totales_por_servicio.keys()],
    '% VITHAS': [servicios[s]['VITHAS'] * 100 for s in totales_por_servicio.keys()],
    '% OSA': [servicios[s]['OSA'] * 100 for s in totales_por_servicio.keys()]
})

col1, col2 = st.columns([1, 1])
with col1:
    st.dataframe(serv_df.style.format({
        "Facturación_Total": "{:,.2f} €", 
        "VITHAS": "{:,.2f} €", 
        "OSA": "{:,.2f} €",
        "% VITHAS": "{:.1f}%",
        "% OSA": "{:.1f}%"
    }), use_container_width=True)

with col2:
    fig_serv = px.pie(serv_df, names='Servicio', values='Facturación_Total', 
                     title='Distribución de Facturación por Servicio',
                     hole=0.4)
    fig_serv.update_traces(textposition='inside', textinfo='percent+label')
    fig_serv.update_layout(showlegend=False)
    st.plotly_chart(fig_serv, use_container_width=True)

st.markdown("---")
st.markdown('<h2 class="section-header">📊 Distribución por Nivel Jerárquico</h2>', unsafe_allow_html=True)

nivel_df = pd.DataFrame({
    'Nivel': list(totales_por_nivel.keys()),
    'Total_Bruto': list(totales_por_nivel.values()),
    'Número de Médicos': [df_edit[df_edit['Nivel'] == nivel].shape[0] for nivel in totales_por_nivel.keys()],
    'Promedio por Médico': [totales_por_nivel[nivel] / df_edit[df_edit['Nivel'] == nivel].shape[0] for nivel in totales_por_nivel.keys()]
})

col1, col2 = st.columns([1, 1])
with col1:
    st.dataframe(nivel_df.style.format({
        "Total_Bruto": "{:,.2f} €", 
        "Promedio por Médico": "{:,.2f} €"
    }), use_container_width=True)

with col2:
    fig_niv = px.bar(nivel_df, x='Nivel', y='Total_Bruto', 
                    title='Total Bruto por Nivel Jerárquico',
                    color='Nivel',
                    text_auto='.2s')
    fig_niv.update_layout(yaxis_title="Facturación Total (€)")
    st.plotly_chart(fig_niv, use_container_width=True)

st.markdown("---")
st.markdown('<h2 class="section-header">👨‍⚕️ Detalle por Médico</h2>', unsafe_allow_html=True)

cols_to_show = ['Médico', 'Nivel'] + list(servicios.keys()) + ['Total_Bruto', 'Total_OSA_Disponible', 'Pct_Abono', 'Abonado_a_Medico', 'Queda_en_OSA_por_medico', 'Diferencia_%']

# Añadir estilo condicional para la diferencia %
def color_diferencia(val):
    color = 'green' if val > 0 else 'red' if val < 0 else 'gray'
    return f'color: {color}; font-weight: bold;'

st.dataframe(df_edit[cols_to_show].sort_values(['Nivel', 'Médico']).reset_index(drop=True).style.format({
    **{s: "{:,.2f} €" for s in servicios.keys()},
    'Total_Bruto': "{:,.2f} €",
    'Total_OSA_Disponible': "{:,.2f} €",
    'Pct_Abono': "{:.1%}",
    'Abonado_a_Medico': "{:,.2f} €",
    'Queda_en_OSA_por_medico': "{:,.2f} €",
    'Diferencia_%': "{:+.2%}"
}).applymap(color_diferencia, subset=['Diferencia_%']), use_container_width=True, height=400)

st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Promedio Especialistas (Bruto)", f"{promedio_especialistas:,.2f} €")
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Promedio Consultores (Bruto)", f"{promedio_consultores:,.2f} €")
    st.markdown('</div>', unsafe_allow_html=True)

if total_abonado_a_medicos > total_osa:
    st.error("⚠️ Atención: El total abonado supera el pool OSA. Revisa los datos.")

# -------------------- Exportar Excel con varias hojas --------------------
st.markdown("---")
st.markdown('<h2 class="section-header">📥 Exportar Resultados</h2>', unsafe_allow_html=True)

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
    label="📊 Descargar Excel Completo",
    data=excel_bytes,
    file_name="vithas_osa_reestructurado.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
    type="primary"
)

# Notas finales
st.markdown("---")
st.markdown("**Notas:**")
st.markdown("""
- **Facturación Bruta**: Total de ingresos sin deducciones
- **Pool OSA**: Porción de la facturación destinada a distribución entre médicos
- **% Abono**: Porcentaje aplicado según nivel y rendimiento
- **Diferencia %**: Variación entre lo facturado y lo recibido por el médico
""")


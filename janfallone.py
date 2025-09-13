import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(page_title="Sistema de Distribución VITHAS-OSA", layout="wide", page_icon="💼")

# 2c3e50

# -------------------- Estilos Profesionales --------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #DAEDD5;  
        font-weight: 700;
        margin-bottom: 0.5rem;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #E9EFF5;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-left: 0.5rem;
        border-left: 4px solid #3498db;
    }
    .metric-card {
        background: linear-gradient(135deg, #2B4225 0%, #2B4225 100%);
        border-radius: 10px;
        padding: 1.5rem;
        border: 1px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        height: 100%;
    }
    .metric-title {
        font-size: 1rem;
        color: #E9EFF5;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.8rem;
        color: #E9EFF5;
        font-weight: 700;
    }
    .positive-value { color: #27ae60 !important; }
    .negative-value { color: #e74c3c !important; }
    .dataframe {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stDataFrame { 
        border: 1px solid #dee2e6;
        border-radius: 8px;
    }
    .download-btn {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 600;
    }
    .info-box {
        background-color: #E9EFF5;
        border-left: 4px solid #3498db;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- Header --------------------
st.markdown('<div class="main-header">💼 Sistema de Distribución de Facturación VITHAS-OSA</div>', unsafe_allow_html=True)
st.markdown("**Plataforma de gestión y análisis de distribución de ingresos médicos**")

# -------------------- Definiciones: niveles y servicios --------------------
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

# -------------------- DataFrame base para st.data_editor --------------------
cols = ["Médico", "Nivel"] + list(servicios.keys())
rows = []
for medico, nivel in medicos:
    fila = {"Médico": medico, "Nivel": nivel}
    for s in servicios.keys():
        fila[s] = 0.0
    rows.append(fila)

df_base = pd.DataFrame(rows, columns=cols)

# -------------------- Entrada de Datos --------------------
st.markdown('<div class="section-header">📋 Ingreso de Datos de Facturación</div>', unsafe_allow_html=True)
st.info("Introduzca los importes de facturación para cada médico y servicio. Los cálculos se actualizarán automáticamente.")

df_edit = st.data_editor(df_base, num_rows="fixed", use_container_width=True, height=400)

# Asegurarnos de que las columnas de servicios sean numéricas
for s in servicios.keys():
    df_edit[s] = pd.to_numeric(df_edit[s], errors='coerce').fillna(0.0)

# -------------------- Cálculos: totales por médico, por servicio y por nivel --------------------
# Total bruto por médico (antes de separar VITHAS / OSA)
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
    total_bruto_med = row['Total_Bruto']
    total_osa_med = row['Total_OSA_Disponible']

    if nivel == 'Especialista':
        if total_bruto_med > promedio_especialistas:
            pct = 0.90
        else:
            pct = 0.85
    elif nivel == 'Consultor':
        if total_bruto_med > promedio_consultores:
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

# -------------------- Resumen General --------------------
st.markdown('<div class="section-header">📊 Resumen General</div>', unsafe_allow_html=True)

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Facturación Bruta Total</div>
        <div class="metric-value">{:,.2f} €</div>
        <div style='font-size: 0.9rem; color: #E9EFF5;'>Suma total sin deducciones</div>
    </div>
    """.format(total_bruto), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Porción VITHAS</div>
        <div class="metric-value">{:,.2f} €</div>
        <div style='font-size: 0.9rem; color: #E9EFF5;'>{:.1f}% del total</div>
    </div>
    """.format(total_vithas, (total_vithas/total_bruto)*100 if total_bruto > 0 else 0), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Pool OSA</div>
        <div class="metric-value">{:,.2f} €</div>
        <div style='font-size: 0.9rem; color: #E9EFF5;'>{:.1f}% del total</div>
    </div>
    """.format(total_osa, (total_osa/total_bruto)*100 if total_bruto > 0 else 0), unsafe_allow_html=True)

with col4:
    saldo_class = "positive-value" if osa_saldo_final >= 0 else "negative-value"
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Saldo OSA Final</div>
        <div class="metric-value {}">{:,.2f} €</div>
        <div style='font-size: 0.9rem; color: #E9EFF5;'>Después de distribución</div>
    </div>
    """.format(saldo_class, osa_saldo_final), unsafe_allow_html=True)

# -------------------- Distribución por Servicio --------------------
st.markdown('<div class="section-header">📈 Distribución por Servicio</div>', unsafe_allow_html=True)

serv_df = pd.DataFrame({
    'Servicio': list(servicios.keys()),
    'Facturación_Total': list(totales_por_servicio.values()),
    'VITHAS': [totales_vithas_por_servicio[s] for s in servicios.keys()],
    'OSA': [totales_osa_por_servicio[s] for s in servicios.keys()],
    '% VITHAS': [servicios[s]['VITHAS'] * 100 for s in servicios.keys()],
    '% OSA': [servicios[s]['OSA'] * 100 for s in servicios.keys()]
})

tab1, tab2 = st.tabs(["📋 Tabla de Datos", "📊 Visualización"])

with tab1:
    st.dataframe(
        serv_df.style.format({
            "Facturación_Total": "{:,.2f} €",
            "VITHAS": "{:,.2f} €", 
            "OSA": "{:,.2f} €",
            "% VITHAS": "{:.1f}%",
            "% OSA": "{:.1f}%"
        }),
        use_container_width=True
    )

with tab2:
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        name='VITHAS',
        x=serv_df['Servicio'],
        y=serv_df['VITHAS'],
        marker_color='#3498db',
        text=serv_df['VITHAS'].apply(lambda x: f'{x:,.0f} €'),
        textposition='auto'
    ))
    fig1.add_trace(go.Bar(
        name='OSA',
        x=serv_df['Servicio'],
        y=serv_df['OSA'],
        marker_color='#27ae60',
        text=serv_df['OSA'].apply(lambda x: f'{x:,.0f} €'),
        textposition='auto'
    ))
    fig1.update_layout(
        title='Distribución VITHAS vs OSA por Servicio',
        barmode='stack',
        xaxis_tickangle=-45,
        yaxis_title="Importe (€)"
    )
    st.plotly_chart(fig1, use_container_width=True)

# -------------------- Totales por Nivel Jerárquico --------------------
st.markdown('<div class="section-header">🏢 Totales por Nivel Jerárquico</div>', unsafe_allow_html=True)

nivel_df = pd.DataFrame({
    'Nivel': list(totales_por_nivel.keys()),
    'Total_Bruto': list(totales_por_nivel.values()),
    'Número de Médicos': [df_edit[df_edit['Nivel'] == nivel].shape[0] for nivel in totales_por_nivel.keys()],
    'Promedio por Médico': [totales_por_nivel[nivel] / df_edit[df_edit['Nivel'] == nivel].shape[0] if df_edit[df_edit['Nivel'] == nivel].shape[0] > 0 else 0 for nivel in totales_por_nivel.keys()]
})

col1, col2 = st.columns([1, 1])

with col1:
    st.dataframe(
        nivel_df.style.format({
            "Total_Bruto": "{:,.2f} €",
            "Promedio por Médico": "{:,.2f} €"
        }),
        use_container_width=True
    )

with col2:
    fig_niv = px.bar(nivel_df, x='Nivel', y='Total_Bruto', 
                    title='Total Bruto por Nivel Jerárquico',
                    color='Nivel',
                    text_auto='.2s')
    fig_niv.update_layout(
        yaxis_title="Facturación Total (€)",
        showlegend=False
    )
    fig_niv.update_traces(texttemplate='%{text:.2s} €', textposition='outside')
    st.plotly_chart(fig_niv, use_container_width=True)

# -------------------- Detalle por Médico --------------------
st.markdown('<div class="section-header">👨‍⚕️ Detalle por Médico</div>', unsafe_allow_html=True)

cols_to_show = ['Médico', 'Nivel'] + list(servicios.keys()) + ['Total_Bruto', 'Total_OSA_Disponible', 'Pct_Abono', 'Abonado_a_Medico', 'Queda_en_OSA_por_medico', 'Diferencia_%']

# Función para color condicional
def color_diferencia(val):
    if val > 0:
        return 'color: #27ae60; font-weight: bold;'
    elif val < 0:
        return 'color: #e74c3c; font-weight: bold;'
    else:
        return 'color: #7f8c8d;'

st.dataframe(
    df_edit[cols_to_show].sort_values(['Nivel', 'Médico']).reset_index(drop=True).style.format({
        **{s: "{:,.2f} €" for s in servicios.keys()},
        'Total_Bruto': "{:,.2f} €",
        'Total_OSA_Disponible': "{:,.2f} €",
        'Pct_Abono': "{:.1%}",
        'Abonado_a_Medico': "{:,.2f} €",
        'Queda_en_OSA_por_medico': "{:,.2f} €",
        'Diferencia_%': "{:+.2%}"
    }).applymap(color_diferencia, subset=['Diferencia_%']),
    use_container_width=True,
    height=400
)

# -------------------- Promedios por Grupo --------------------
st.markdown('<div class="section-header">📊 Promedios por Grupo</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Promedio Especialistas (Bruto)</div>
        <div class="metric-value">{:,.2f} €</div>
        <div style='font-size: 0.9rem; color: #E9EFF5;'>Base para cálculo de porcentajes</div>
    </div>
    """.format(promedio_especialistas), unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Promedio Consultores (Bruto)</div>
        <div class="metric-value">{:,.2f} €</div>
        <div style='font-size: 0.9rem; color: #E9EFF5;'>Base para cálculo de porcentajes</div>
    </div>
    """.format(promedio_consultores), unsafe_allow_html=True)

# Validación final
if total_abonado_a_medicos > total_osa:
    st.error("⚠️ Atención: El total abonado supera el pool OSA. Revisa los datos.")

# -------------------- Exportación --------------------
st.markdown('<div class="section-header">💾 Exportar Resultados</div>', unsafe_allow_html=True)

def generar_excel():
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Hoja de resumen global
        hoja_totales_globales = pd.DataFrame({
            'Concepto': ['Total Bruto', 'Total VITHAS', 'Total OSA (pool inicial)', 'Total abonado a médicos', 'Saldo OSA final'],
            'Valor (€)': [total_bruto, total_vithas, total_osa, total_abonado_a_medicos, osa_saldo_final]
        })
        hoja_totales_globales.to_excel(writer, sheet_name='Totales_Globales', index=False)
        
        # Hoja por servicio
        hoja_por_servicio = serv_df.copy()
        hoja_por_servicio.to_excel(writer, sheet_name='Por_Servicio', index=False)
        
        # Hoja por nivel
        hoja_por_nivel = nivel_df.copy()
        hoja_por_nivel.to_excel(writer, sheet_name='Por_Nivel', index=False)
        
        # Hoja detalle médicos
        hoja_detalle_medicos = df_edit[cols_to_show].copy()
        hoja_detalle_medicos.to_excel(writer, sheet_name='Detalle_Medicos', index=False)
    
    return output.getvalue()

excel_data = generar_excel()

#col1 = st.columns([1])
#with col1:
st.download_button(
    label="📥 Descargar Excel Completo",
    data=excel_data,
    file_name="distribucion_vithas_osa.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

#with col2:
   # st.markdown("""
  #  <div class="info-box">
    #    <strong>Información del Reporte:</strong> El archivo Excel contiene cuatro hojas: 
    #    Totales globales, distribución por servicio, totales por nivel jerárquico, 
    #    y detalle completo por médico con todos los cálculos aplicados.
   # </div>
   # """, unsafe_allow_html=True)

# -------------------- Footer --------------------

#st.markdown("---")
#st.markdown("""
#<div style='text-align: center; color: #6c757d; font-size: 0.9rem;'>
 #   <strong>Sistema de Distribución VITHAS-OSA</strong> | 
  #  Plataforma de gestión de facturación médica | 
   # © 2024
#</div>
#""", unsafe_allow_html=True)

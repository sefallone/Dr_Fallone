import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(page_title="Sistema de Distribución VITHAS-OSA", layout="wide", page_icon="💼")

# -------------------- Estilos Profesionales --------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #2c3e50;
        font-weight: 700;
        margin-bottom: 0.5rem;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-left: 0.5rem;
        border-left: 4px solid #3498db;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        padding: 1.5rem;
        border: 1px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        height: 100%;
    }
    .metric-title {
        font-size: 1rem;
        color: #6c757d;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.8rem;
        color: #2c3e50;
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
        background-color: #e8f4fd;
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

# -------------------- Entrada de Datos --------------------
st.markdown('<div class="section-header">📋 Ingreso de Datos de Facturación</div>', unsafe_allow_html=True)

# Crear DataFrame base para edición
medicos_lista = []
for nivel, medicos_nivel in niveles.items():
    for medico in medicos_nivel:
        medicos_lista.append({"Médico": medico, "Nivel": nivel})

df_base = pd.DataFrame(medicos_lista)

# Añadir columnas de servicios con valores iniciales en 0
for servicio in servicios.keys():
    df_base[servicio] = 0.0

# Widget para editar datos
with st.expander("📊 Editor de Facturación por Médico", expanded=True):
    st.info("Introduzca los importes de facturación para cada médico y servicio. Los cálculos se actualizarán automáticamente.")
    df_edit = st.data_editor(df_base, num_rows="fixed", use_container_width=True, height=400)

# Convertir todas las columnas numéricas y asegurar que son float
for col in df_edit.columns:
    if col not in ['Médico', 'Nivel']:
        df_edit[col] = pd.to_numeric(df_edit[col], errors='coerce').fillna(0.0)

# -------------------- Cálculos --------------------
# Calcular total bruto por médico
servicios_cols = list(servicios.keys())
df_edit['Total_Bruto'] = df_edit[servicios_cols].sum(axis=1)

# Verificar que hay datos ingresados
if df_edit[servicios_cols].sum().sum() == 0:
    st.warning("⚠️ Por favor, ingrese los datos de facturación en la tabla superior.")
    st.stop()

# Totales por servicio
totales_por_servicio = {servicio: df_edit[servicio].sum() for servicio in servicios_cols}

# Distribución VITHAS/OSA por servicio
totales_vithas_por_servicio = {}
totales_osa_por_servicio = {}
for servicio, porcentajes in servicios.items():
    totales_vithas_por_servicio[servicio] = totales_por_servicio[servicio] * porcentajes['VITHAS']
    totales_osa_por_servicio[servicio] = totales_por_servicio[servicio] * porcentajes['OSA']

# Totales generales
total_bruto = df_edit['Total_Bruto'].sum()
total_vithas = sum(totales_vithas_por_servicio.values())
total_osa = sum(totales_osa_por_servicio.values())

# -------------------- Cálculo de OSA disponible por médico --------------------
df_edit['Total_OSA_Disponible'] = 0.0
for servicio, porcentajes in servicios.items():
    df_edit['Total_OSA_Disponible'] += df_edit[servicio] * porcentajes['OSA']

# -------------------- Resumen General --------------------
st.markdown('<div class="section-header">📊 Resumen General</div>', unsafe_allow_html=True)

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Facturación Bruta Total</div>
        <div class="metric-value">{:,.2f} €</div>
        <div style='font-size: 0.9rem; color: #6c757d;'>Suma total sin deducciones</div>
    </div>
    """.format(total_bruto), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Porción VITHAS</div>
        <div class="metric-value">{:,.2f} €</div>
        <div style='font-size: 0.9rem; color: #6c757d;'>{:.1f}% del total</div>
    </div>
    """.format(total_vithas, (total_vithas/total_bruto)*100 if total_bruto > 0 else 0), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Pool OSA</div>
        <div class="metric-value">{:,.2f} €</div>
        <div style='font-size: 0.9rem; color: #6c757d;'>{:.1f}% del total</div>
    </div>
    """.format(total_osa, (total_osa/total_bruto)*100 if total_bruto > 0 else 0), unsafe_allow_html=True)

with col4:
    saldo_class = "positive-value" if total_osa >= 0 else "negative-value"
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Saldo OSA Final</div>
        <div class="metric-value {}">{:,.2f} €</div>
        <div style='font-size: 0.9rem; color: #6c757d;'>Después de distribución</div>
    </div>
    """.format(saldo_class, total_osa), unsafe_allow_html=True)

# -------------------- Distribución por Servicio --------------------
st.markdown('<div class="section-header">📈 Distribución por Servicio</div>', unsafe_allow_html=True)

serv_df = pd.DataFrame({
    'Servicio': list(servicios.keys()),
    'Facturación Total': [totales_por_servicio[s] for s in servicios.keys()],
    'VITHAS': [totales_vithas_por_servicio[s] for s in servicios.keys()],
    'OSA': [totales_osa_por_servicio[s] for s in servicios.keys()],
    '% VITHAS': [servicios[s]['VITHAS'] * 100 for s in servicios.keys()],
    '% OSA': [servicios[s]['OSA'] * 100 for s in servicios.keys()]
})

tab1, tab2 = st.tabs(["📋 Tabla de Datos", "📊 Visualización"])

with tab1:
    st.dataframe(
        serv_df.style.format({
            "Facturación Total": "{:,.2f} €",
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
        marker_color='#3498db'
    ))
    fig1.add_trace(go.Bar(
        name='OSA',
        x=serv_df['Servicio'],
        y=serv_df['OSA'],
        marker_color='#27ae60'
    ))
    fig1.update_layout(
        title='Distribución VITHAS vs OSA por Servicio',
        barmode='stack',
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig1, use_container_width=True)

# -------------------- Detalle por Médico --------------------
st.markdown('<div class="section-header">👨‍⚕️ Detalle por Médico</div>', unsafe_allow_html=True)

# Calcular promedios por nivel para las reglas de distribución
promedio_especialistas = df_edit[df_edit['Nivel'] == 'Especialista']['Total_Bruto'].mean() if not df_edit[df_edit['Nivel'] == 'Especialista'].empty else 0
promedio_consultores = df_edit[df_edit['Nivel'] == 'Consultor']['Total_Bruto'].mean() if not df_edit[df_edit['Nivel'] == 'Consultor'].empty else 0

# Aplicar reglas de distribución
def calcular_abono(nivel, total_bruto, total_osa):
    if nivel == 'General':
        return total_osa * 0.95
    elif nivel == 'Especialista':
        return total_osa * (0.90 if total_bruto > promedio_especialistas else 0.85)
    elif nivel == 'Consultor':
        return total_osa * (0.92 if total_bruto > promedio_consultores else 0.88)
    return 0

df_edit['Abonado'] = df_edit.apply(
    lambda row: calcular_abono(row['Nivel'], row['Total_Bruto'], row['Total_OSA_Disponible']), axis=1
)
df_edit['% Abono'] = df_edit.apply(
    lambda row: row['Abonado'] / row['Total_OSA_Disponible'] if row['Total_OSA_Disponible'] > 0 else 0, axis=1
)
df_edit['Diferencia %'] = df_edit.apply(
    lambda row: (row['Abonado'] / row['Total_Bruto'] - 1) if row['Total_Bruto'] > 0 else 0, axis=1
)

# Mostrar tabla de médicos
cols_mostrar = ['Médico', 'Nivel', 'Total_Bruto', 'Total_OSA_Disponible', '% Abono', 'Abonado', 'Diferencia %']
st.dataframe(
    df_edit[cols_mostrar].sort_values(['Nivel', 'Médico']).style.format({
        'Total_Bruto': '{:,.2f} €',
        'Total_OSA_Disponible': '{:,.2f} €',
        '% Abono': '{:.1%}',
        'Abonado': '{:,.2f} €',
        'Diferencia %': '{:+.2%}'
    }),
    use_container_width=True,
    height=400
)

# -------------------- Exportación --------------------
st.markdown('<div class="section-header">💾 Exportar Resultados</div>', unsafe_allow_html=True)

def generar_excel():
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Hoja de resumen
        resumen_df = pd.DataFrame({
            'Concepto': ['Facturación Bruta Total', 'Porción VITHAS', 'Pool OSA', 'Total Abonado a Médicos'],
            'Valor (€)': [total_bruto, total_vithas, total_osa, df_edit['Abonado'].sum()],
            'Porcentaje': [
                '100%',
                f'{(total_vithas/total_bruto*100):.1f}%' if total_bruto > 0 else '0%',
                f'{(total_osa/total_bruto*100):.1f}%' if total_bruto > 0 else '0%',
                f'{(df_edit["Abonado"].sum()/total_osa*100):.1f}%' if total_osa > 0 else '0%'
            ]
        })
        resumen_df.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Hoja de servicios
        serv_df.to_excel(writer, sheet_name='Por Servicio', index=False)
        
        # Hoja de médicos
        df_edit.to_excel(writer, sheet_name='Detalle Médicos', index=False)
    
    return output.getvalue()

excel_data = generar_excel()

col1, col2 = st.columns([1, 3])
with col1:
    st.download_button(
        label="📥 Descargar Excel Completo",
        data=excel_data,
        file_name="distribucion_vithas_osa.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with col2:
    st.markdown("""
    <div class="info-box">
        <strong>Información del Reporte:</strong> El archivo Excel contiene tres hojas: Resumen general, 
        distribución por servicio, y detalle completo por médico con todos los cálculos aplicados.
    </div>
    """, unsafe_allow_html=True)

# -------------------- Footer --------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d; font-size: 0.9rem;'>
    <strong>Sistema de Distribución VITHAS-OSA</strong> | 
    Plataforma de gestión de facturación médica | 
    © 2024
</div>
""", unsafe_allow_html=True)

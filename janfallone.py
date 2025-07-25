import streamlit as st
import pandas as pd
import PyPDF2
import re
from datetime import datetime
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Dr. Fallone", layout="wide")
st.title("📊 Dashboard Dr. Fallone - Análisis de PDF")

# --- Función mejorada para extraer datos del PDF ---
def extract_data_from_pdf(uploaded_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    
    # Expresiones regulares para extraer datos clave
    pattern = r"([A-ZÁ-Ú\s\-]+,[A-ZÁ-Ú\s\-]+)\s+([A-Z]+)\s+(.*?)\s+(\d+,\d+|\d+\.\d+)\s+(\d+,\d+|\d+\.\d+)\s+(\d+,\d+|\d+\.\d+)\s+(\d{2}/\d{2}/\d{4})"
    matches = re.finditer(pattern, text)
    
    data = []
    for match in matches:
        paciente = match.group(1).strip()
        aseguradora = match.group(3).strip()
        procedimiento = match.group(3).strip()  # Ajustar según necesidad
        tarifa = float(match.group(4).replace(",", "."))
        fecha = datetime.strptime(match.group(7), "%d/%m/%Y")
        data.append([paciente, aseguradora, procedimiento, tarifa, fecha])
    
    return pd.DataFrame(data, columns=["Paciente", "Aseguradora", "Procedimiento", "Tarifa", "Fecha"])

# --- Interfaz para cargar PDF ---
uploaded_file = st.file_uploader("Sube el archivo PDF del Dr. Fallone", type="pdf")

if uploaded_file is not None:
    try:
        # Extraer datos
        df = extract_data_from_pdf(uploaded_file)
        if df.empty:
            st.error("No se encontraron datos en el PDF. Verifica el formato.")
            st.stop()
        
        df["Ingresos"] = df["Tarifa"]

        # Sidebar con filtros
        st.sidebar.header("Filtros")
        aseguradoras = df["Aseguradora"].unique()
        procedimientos = df["Procedimiento"].unique()
        
        aseguradora_seleccionada = st.sidebar.multiselect(
            "Aseguradora", 
            options=aseguradoras, 
            default=aseguradoras
        )
        procedimiento_seleccionado = st.sidebar.multiselect(
            "Procedimiento", 
            options=procedimientos, 
            default=procedimientos
        )

        # Filtrar datos
        df_filtrado = df[
            (df["Aseguradora"].isin(aseguradora_seleccionada)) & 
            (df["Procedimiento"].isin(procedimiento_seleccionado))
        ]

        # KPIs
        total_ingresos = df_filtrado["Ingresos"].sum()
        num_pacientes = df_filtrado["Paciente"].nunique()
        ingreso_promedio = total_ingresos / num_pacientes if num_pacientes > 0 else 0

        # Mostrar KPIs
        col1, col2, col3 = st.columns(3)
        col1.metric("Ingresos Totales", f"€ {total_ingresos:,.2f}")
        col2.metric("N° Pacientes", num_pacientes)
        col3.metric("Ingreso Promedio", f"€ {ingreso_promedio:,.2f}")

        # Gráficos
        st.markdown("---")
        if not df_filtrado.empty:
            fig1 = px.bar(
                df_filtrado.groupby("Aseguradora")["Ingresos"].sum().reset_index(),
                x="Aseguradora",
                y="Ingresos",
                title="Ingresos por Aseguradora",
                color="Aseguradora"
            )
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.pie(
                df_filtrado.groupby("Procedimiento")["Ingresos"].sum().reset_index(),
                names="Procedimiento",
                values="Ingresos",
                title="Distribución por Procedimiento"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No hay datos para mostrar con los filtros seleccionados.")

        # Tabla de datos
        st.markdown("### 📋 Datos Extraídos")
        st.dataframe(df_filtrado)

    except Exception as e:
        st.error(f"Error al procesar el PDF: {str(e)}")
        st.text("Vista previa del texto extraído (para diagnóstico):")
        st.text(PyPDF2.PdfReader(uploaded_file).pages[0].extract_text()[:500])

else:
    st.info("Por favor, sube un archivo PDF para comenzar.")

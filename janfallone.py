import streamlit as st
import pandas as pd
import PyPDF2
import re
from io import BytesIO
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Dr. Fallone", layout="wide")
st.title("📊 Dashboard Dr. Fallone - Análisis Directo de PDF")

# --- Función mejorada para extraer datos del PDF ---
def extract_data_from_pdf(uploaded_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    
    # Procesamiento específico para el formato del Dr. Fallone
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    data = []
    
    for line in lines:
        # Expresión regular ajustada para el formato específico
        match = re.search(
            r"^([A-ZÁ-Ú\s\-,]+)\s+([A-Z]+)\s+(.*?)\s+(\d+[\.,]\d+)\s+(\d+[\.,]\d+)\s+(\d+[\.,]\d+)\s+(\d{2}/\d{2}/\d{4})",
            line
        )
        if match:
            try:
                paciente = match.group(1).strip()
                aseguradora = match.group(3).strip()
                procedimiento = " ".join(line.split()[3:-5])  # Ajuste para capturar el procedimiento completo
                tarifa = float(match.group(4).replace(",", "."))
                fecha = match.group(7)
                data.append([paciente, aseguradora, procedimiento, tarifa, fecha])
            except Exception as e:
                st.warning(f"Error procesando línea: {line}\nError: {str(e)}")
                continue
    
    return pd.DataFrame(data, columns=["Paciente", "Aseguradora", "Procedimiento", "Tarifa", "Fecha"])

# --- Interfaz principal ---
uploaded_file = st.file_uploader("Sube el archivo PDF del Dr. Fallone", type="pdf")

if uploaded_file is not None:
    with st.spinner("Procesando PDF..."):
        try:
            # Paso 1: Extraer datos del PDF
            df = extract_data_from_pdf(uploaded_file)
            
            if df.empty:
                st.error("No se encontraron datos en el formato esperado.")
                st.stop()
            
            # Paso 2: Mostrar opción para descargar Excel
            excel_buffer = BytesIO()
            df.to_excel(excel_buffer, index=False)
            st.download_button(
                label="⬇️ Descargar Datos en Excel",
                data=excel_buffer.getvalue(),
                file_name="datos_fallone.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Paso 3: Generar dashboard
            st.success(f"Datos cargados correctamente ({len(df)} registros)")
            
            # Filtros
            st.sidebar.header("Filtros")
            aseguradoras = st.sidebar.multiselect(
                "Aseguradoras",
                options=df["Aseguradora"].unique(),
                default=df["Aseguradora"].unique()
            )
            
            procedimientos = st.sidebar.multiselect(
                "Procedimientos",
                options=df["Procedimiento"].unique(),
                default=df["Procedimiento"].unique()
            )
            
            # Aplicar filtros
            df_filtrado = df[
                (df["Aseguradora"].isin(aseguradoras)) & 
                (df["Procedimiento"].isin(procedimientos))
            ]
            
            # KPIs
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Facturado", f"€{df_filtrado['Tarifa'].sum():,.2f}")
            col2.metric("Pacientes Únicos", df_filtrado["Paciente"].nunique())
            col3.metric("Promedio por Procedimiento", f"€{df_filtrado['Tarifa'].mean():,.2f}")
            
            # Gráficos
            st.subheader("Análisis Visual")
            
            fig1 = px.bar(
                df_filtrado.groupby("Aseguradora")["Tarifa"].sum().reset_index(),
                x="Aseguradora",
                y="Tarifa",
                title="Ingresos por Aseguradora",
                color="Aseguradora"
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            fig2 = px.pie(
                df_filtrado.groupby("Procedimiento")["Tarifa"].sum().reset_index(),
                names="Procedimiento",
                values="Tarifa",
                title="Distribución por Procedimiento"
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Datos crudos
            st.subheader("Datos Extraídos")
            st.dataframe(df_filtrado)
            
        except Exception as e:
            st.error(f"Error crítico: {str(e)}")
            st.text("Primeras 500 líneas del texto extraído para diagnóstico:")
            pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
            preview_text = "\n".join([page.extract_text() for page in pdf_reader.pages[:2]])
            st.text(preview_text[:1000])
else:
    st.info("Por favor, sube un archivo PDF para comenzar el análisis.")



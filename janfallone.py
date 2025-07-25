import streamlit as st
import pandas as pd
import PyPDF2
import io
import plotly.express as px
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Dashboard Dr. Fallone", layout="wide")
st.title("📊 Dashboard Dr. Fallone - Cargar PDF")

# --- Función para extraer datos del PDF ---
def extract_data_from_pdf(uploaded_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    
    # Procesamiento básico (adaptar según la estructura real del PDF)
    lines = text.split('\n')
    data = []
    for line in lines:
        if "€" in line and "TRAUMATOLOGÍA" in line:
            parts = line.split()
            try:
                paciente = parts[0] + " " + parts[1]
                aseguradora = " ".join(parts[2:5])
                procedimiento = " ".join(parts[5:-5])
                tarifa = float(parts[-5].replace(",", "."))
                fecha = datetime.strptime(parts[-3], "%d/%m/%Y")
                data.append([paciente, aseguradora, procedimiento, tarifa, fecha])
            except:
                continue
    return pd.DataFrame(data, columns=["Paciente", "Aseguradora", "Procedimiento", "Tarifa", "Fecha"])

# --- Interfaz para cargar PDF ---
uploaded_file = st.file_uploader("Sube el archivo PDF del Dr. Fallone", type="pdf")

if uploaded_file is not None:
    # Extraer datos
    df = extract_data_from_pdf(uploaded_file)
    df["Ingresos"] = df["Tarifa"] * 1.21  # Añadir IVA (opcional)

    # Sidebar con filtros
    st.sidebar.header("Filtros")
    aseguradora = st.sidebar.multiselect(
        "Aseguradora", 
        options=df["Aseguradora"].unique(), 
        default=df["Aseguradora"].unique()
    )
    procedimiento = st.sidebar.multiselect(
        "Procedimiento", 
        options=df["Procedimiento"].unique(), 
        default=df["Procedimiento"].unique()
    )

    # Filtrar datos
    df_filtrado = df[
        (df["Aseguradora"].isin(aseguradora)) & 
        (df["Procedimiento"].isin(procedimiento))
    ]

    # KPIs
    total_ingresos = df_filtrado["Ingresos"].sum()
    num_pacientes = df_filtrado["Paciente"].nunique()
    ingreso_promedio = total_ingresos / num_pacientes if num_pacientes > 0 else 0

    # Mostrar KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Ingresos Totales", f"{total_ingresos:,.2f} €")
    col2.metric("N° Pacientes", num_pacientes)
    col3.metric("Ingreso Promedio", f"{ingreso_promedio:,.2f} €")

    # Gráficos
    st.markdown("---")
    fig1 = px.bar(
        df_filtrado.groupby("Aseguradora")["Ingresos"].sum().reset_index(),
        x="Aseguradora",
        y="Ingresos",
        title="Ingresos por Aseguradora"
    )
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.pie(
        df_filtrado.groupby("Procedimiento")["Ingresos"].sum().reset_index(),
        names="Procedimiento",
        values="Ingresos",
        title="Distribución por Procedimiento"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Tabla de datos
    st.markdown("### 📋 Datos Extraídos del PDF")
    st.dataframe(df_filtrado)

else:
    st.warning("Por favor, sube un archivo PDF para comenzar.")

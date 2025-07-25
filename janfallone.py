import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Dr. Fallone - Excel", layout="wide")
st.title("📊 Dashboard Dr. Fallone - Cargar Excel")

# --- Interfaz para cargar Excel ---
uploaded_file = st.file_uploader("Sube el archivo Excel (XLSX)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Leer el archivo Excel
        df = pd.read_excel(uploaded_file)
        
        # Validar columnas mínimas requeridas
        required_columns = ["Paciente", "Aseguradora", "Procedimiento", "Tarifa", "Fecha"]
        if not all(col in df.columns for col in required_columns):
            st.error(f"El archivo debe contener las columnas: {', '.join(required_columns)}")
            st.stop()
        
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
        total_ingresos = df_filtrado["Tarifa"].sum()
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
        else:
            st.warning("No hay datos para mostrar con los filtros seleccionados.")

        # Tabla de datos
        st.markdown("### 📋 Datos del Excel")
        st.dataframe(df_filtrado)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")

else:
    st.info("Por favor, sube un archivo Excel (XLSX) para comenzar.")

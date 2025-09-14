import streamlit as st

st.set_page_config(
    page_title="Sistema de Distribución VITHAS-OSA",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Sistema de Distribución VITHAS-OSA")

st.markdown("""
Bienvenido a la herramienta interactiva de **análisis y escalabilidad**.

### 📌 Cómo usar la app:
- En la barra lateral (menú de páginas), selecciona la sección que quieras explorar.
- La app tiene **dos páginas principales**:
    1. **Distribución VITHAS-OSA** → Para cargar datos, editar y visualizar la distribución.
    2. **Escalabilidad** → Para entender y comparar de forma sencilla cuánto se abona a los médicos.

👉 Empieza entrando en **Distribución VITHAS-OSA** para cargar los datos.
""")

st.info("Usa el menú de la izquierda para navegar entre páginas.")


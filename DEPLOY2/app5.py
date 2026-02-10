import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# Para asegurar la ruta del archivo CSV, se utiliza Path para obtener la ubicación relativa al script
from pathlib import Path

# 1. Configuración de la página (Ancho completo)
st.set_page_config(page_title="Dashboard Población 2020", layout="wide")

# 2. Estilo personalizado para las tarjetas KPI mediante HTML/CSS
st.markdown("""
    <style>
    .kpi-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        text-align: center;
        color: #000000;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Carga y Limpieza de Datos
@st.cache_data
def load_and_clean_data():
    # Asegúra que el archivo CSV esté en la misma carpeta del Script
    file_path = Path(__file__).parent / "C01_population_by_country_2020.csv"
    df = pd.read_csv(file_path)
    # Limpieza: Convertir porcentajes de texto a números
    df['Urban Pop %'] = df['Urban Pop %'].str.replace('%', '').replace('N.A.', '0').astype(float)
    df['World Share'] = df['World Share'].str.replace('%', '').astype(float)
    # Limpieza de Edad Mediana (N.A. por la media)
    df['Med. Age'] = pd.to_numeric(df['Med. Age'], errors='coerce')
    df['Med. Age'] = df['Med. Age'].fillna(df['Med. Age'].mean())
    
    return df

df = load_and_clean_data()

# 4. Menú Lateral (Sidebar)
with st.sidebar:
    st.title("📌 Navegación")
    opcion = st.radio("Seleccione una vista:", ["📊 Dashboard Principal", "💾 Descarga de Datos"])
    st.divider()
    st.info("Este dashboard analiza la demografía mundial del año 2020.")

# --- VISTA 1: DASHBOARD ---
if opcion == "📊 Dashboard Principal":
    st.title("🌍 Análisis de Población Mundial 2020")

    # KPIs en Tarjetas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_pop = df['Population (2020)'].sum() / 1e9
        st.markdown(f"<div class='kpi-card'><h3>Población Total</h3><h2>{total_pop:.2f} Billones</h2></div>", unsafe_allow_html=True)
    
    with col2:
        avg_age = df['Med. Age'].mean()
        st.markdown(f"<div class='kpi-card' style='border-left-color: #1c83e1;'><h3>Edad Mediana</h3><h2>{avg_age:.1f} Años</h2></div>", unsafe_allow_html=True)
        
    with col3:
        avg_urban = df['Urban Pop %'].mean()
        st.markdown(f"<div class='kpi-card' style='border-left-color: #29b09d;'><h3>% Urbanización</h3><h2>{avg_urban:.1f}%</h2></div>", unsafe_allow_html=True)

    st.write("---")

    # Visualizaciones
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Top 10 Países más Poblados")
        df_top10 = df.nlargest(10, 'Population (2020)')
        fig1, ax1 = plt.subplots()
        sns.barplot(data=df_top10, x='Population (2020)', y='Country (or dependency)', palette='viridis', ax=ax1)
        st.pyplot(fig1)

    with c2:
        st.subheader("Fertilidad vs Edad Mediana")
        fig2, ax2 = plt.subplots()
        sns.scatterplot(data=df, x='Med. Age', y='Fert. Rate', size='Population (2020)', alpha=0.5, ax=ax2)
        st.pyplot(fig2)

# --- VISTA 2: REPORTE Y DESCARGA ---
else:
    st.title("📂 Reporte de Datos Procesados")
    st.write("A continuación puede previsualizar los datos limpios y descargarlos en formato CSV.")
    
    # Filtro dinámico opcional
    busqueda = st.text_input("Filtrar por país:", "")
    df_filtrado = df[df['Country (or dependency)'].str.contains(busqueda, case=False)]
    
    st.dataframe(df_filtrado, use_container_width=True)

    # Botón de Descarga
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte CSV",
        data=csv,
        file_name='reporte_poblacion_2020.csv',
        mime='text/csv',
    )
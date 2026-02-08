# Requiere Instalar: pip install folium streamlit-folium
#
# 1. Importación de librerías
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import folium
from streamlit_folium import st_folium
import json
import requests

# 2. Configuración de la página
st.set_page_config(page_title="Dashboard Población 2020", layout="wide")

# 3. Función con Caché para cargar datos
@st.cache_data
def cargar_datos(archivo):
    df = pd.read_csv(archivo)
    # Limpieza rápida: convertir porcentajes de texto a números si es necesario
    if 'Urban Pop %' in df.columns:
       df['Urban Pop %'] = df['Urban Pop %'].str.replace('%', '').str.replace('N.A.', '0').astype(float)
    return df

@st.cache_data
def obtener_geojson(): # Fuente de GeoJSON para países del mundo
    url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
    response = requests.get(url)
    return response.json()

# 4. Título Principal
st.title("🌏 Análisis Demográfico Global 2020")
st.markdown("---")

# 5. Carga de Archivo
uploaded_file = st.file_uploader("Cargar C01_population_by_country_2020.csv", type=["csv"])

if uploaded_file is not None:
    df_base = cargar_datos(uploaded_file)

    # --- SECCIÓN DE FILTROS (Sidebar) ---
    st.sidebar.header("Filtros de Visualización")
    lista_continentes = ["Todos"] + sorted(df_base['Continent'].unique().tolist())
    seleccion_continente = st.sidebar.selectbox("Selecciona un Continente:", lista_continentes)

    # Aplicar filtro
    if seleccion_continente != "Todos":
       df = df_base[df_base['Continent'] == seleccion_continente]
    else:
       df = df_base

    # 6. MÉTRICAS CLAVE (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Países", len(df))
    col2.metric("Población Total", f"{df['Population (2020)'].sum():,}")
    col3.metric("Edad Media Promedio", f"{round(df['Med. Age'].replace('N.A.', 0).astype(float).mean(), 1)} años")
    col4.metric("% Urbano Promedio", f"{round(df['Urban Pop %'].mean(), 1)}%")

    st.markdown("---")

    # 7. BLOQUE DE GRÁFICOS 1 (Mapa y Barras)
    fila1_col1, fila1_col2 = st.columns([1.5, 1])

    with fila1_col1:
       st.subheader("🗺️ Mapa Global de Densidad")
       
       # Obtener GeoJSON y mapear datos
       world_geojson = obtener_geojson()
       density_dict = df.set_index('Country (or dependency)')['Density (P/Km²)'].to_dict()
       
       for feature in world_geojson['features']:
           country_name = feature['properties']['name']
           feature['properties']['density_val'] = density_dict.get(country_name, None)

       # Crear mapa con Folium
       m = folium.Map(location=[20, 0], zoom_start=2)
       choropleth = folium.Choropleth(
           geo_data=world_geojson,
           name='Densidad',
           data=df,
           columns=['Country (or dependency)', 'Density (P/Km²)'],
           key_on='feature.properties.name',
           fill_color='YlOrRd',
           fill_opacity=0.7,
           line_opacity=0.2,
           legend_name='Densidad de Población (P/Km²)'
       ).add_to(m)

       # Tooltip dinámico
       folium.features.GeoJsonTooltip(
           fields=['name', 'density_val'],
           aliases=['País', 'Densidad (P/Km²)'],
           localize=True,
           sticky=False,
           labels=True,
           style="background-color: white; border: 1px solid black; border-radius: 3px;"
       ).add_to(choropleth.geojson)

       # Renderizar en Streamlit
       st_folium(m, height=450, use_container_width=True)

    with fila1_col2:
       st.subheader("📊 Top 20 Población")
       top10 = df.nlargest(20, 'Population (2020)')
       #fig_bar, ax_bar = plt.subplots()
       fig_bar, ax_bar = plt.subplots(figsize=(5, 8))
       sns.barplot(data=top10, x='Population (2020)', y='Country (or dependency)', ax=ax_bar, palette="viridis")
       st.pyplot(fig_bar)

    st.markdown("---")

    # 8. BLOQUE DE GRÁFICOS 2 (Línea/Dispersión y Pie)
    fila2_col1, fila2_col2 = st.columns(2)

    with fila2_col1:
       st.subheader("📈 Fertilidad vs Edad Media")
       df_clean = df[df['Fert. Rate'] != 'N.A.'].copy()
       df_clean['Fert. Rate'] = df_clean['Fert. Rate'].astype(float)
       fig_scatter = px.scatter(df_clean, x="Med. Age", y="Fert. Rate", size="Population (2020)", color="Country (or dependency)", hover_name="Country (or dependency)")
       st.plotly_chart(fig_scatter, use_container_width=True)

    with fila2_col2:
       st.subheader("🥧 Distribución de Población Mundial")
       top5_share = df.nlargest(5, 'Population (2020)')
       fig_pie, ax_pie = plt.subplots()
       #ax_pie.pie(top5_share['Population (2020)'], labels=top5_share['Country (or dependency)'], autopct='%1.1f%%', startangle=140)
       ax_pie.pie(top5_share['Population (2020)'], labels=top5_share['Country (or dependency)'], autopct='%1.1f%%', startangle=140, pctdistance=0.85, wedgeprops=dict(width=0.3, edgecolor='w'))
       st.pyplot(fig_pie)

    # 9. TABLA DE DATOS
    st.header("📋 Explorador de Datos")
    st.dataframe(df, use_container_width=True)

else:
    st.warning("Por favor, sube el archivo CSV para comenzar el análisis.")
import streamlit as st
import pandas as pd
import openrouteservice
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import folium
from streamlit_folium import st_folium

# ===============================
# CONFIGURACIÓN
# ===============================
st.set_page_config(page_title="ChivoFast Rutas", layout="wide")
st.title("🚚 Optimización de Rutas - ChivoFast")

# API de OpenRouteService (usa tu propia API Key)
API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjkzOTM1M2FmZGEyODQ4MjQ4MjQ1ZDQ2NTg4YmRiODhhIiwiaCI6Im11cm11cjY0In0="
client = openrouteservice.Client(key=API_KEY)

# ===============================
# CARGA DE DATOS DESDE GITHUB
# ===============================
url = "https://raw.githubusercontent.com/Medb935/ChivoFast-website/main/dataset_entregas_coords.csv"
df = pd.read_csv(url)

st.subheader("📊 Dataset cargado")
st.dataframe(df.head())

# Validación de columnas
if not {'id_entrega', 'lat', 'lng'}.issubset(df.columns):
    st.error("El CSV debe tener las columnas: id_entrega, lat, lng")
    st.stop()

# Eliminar registros sin coordenadas
df = df.dropna(subset=['lat', 'lng'])

# ===============================
# PARÁMETROS DE LA APP
# ===============================
st.sidebar.header("⚙️ Parámetros")
depot = st.sidebar.text_input("Coordenadas del almacén (lat,lng)", "13.6929,-89.2182")
num_repartidores = st.sidebar.slider("Número de repartidores", 1, 5, 2)

# ===============================
# CÁLCULO DE RUTAS
# ===============================
if st.button("Calcular rutas óptimas"):
    depot_lat, depot_lng = map(float, depot.split(","))
    coords = [(depot_lng, depot_lat)] + [(lng, lat) for _, lat, lng in df[['lat','lng']].itertuples()]

    # Matriz de distancias
    matriz = client.distance_matrix(
        locations=coords,
        profile="driving-car",
        metrics=["distance"]
    )["distances"]

    # OR-Tools
    manager = pywrapcp.RoutingIndexManager(len(matriz), num_repartidores, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        node_from = manager.IndexToNode(from_index)
        node_to = manager.IndexToNode(to_index)
        return int(matriz[node_from][node_to])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_parameters)

    # ===============================
    # RESULTADOS
    # ===============================
    if solution:
        rutas = []
        for i in range(num_repartidores):
            index = routing.Start(i)
            ruta = []
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                if node == 0:
                    ruta.append({"id": "Depot", "coords": coords[0]})
                else:
                    cliente_idx = node - 1
                    ruta.append({"id": int(df.iloc[cliente_idx]['id_entrega']), "coords": coords[node]})
                index = solution.Value(routing.NextVar(index))
            rutas.append(ruta)

        st.subheader("📌 Rutas calculadas")
        for i, ruta in enumerate(rutas):
            texto = " → ".join([str(p['id']) for p in ruta])
            st.write(f"🛵 Repartidor {i+1}: {texto}")

        # Mapa
        mapa = folium.Map(location=[depot_lat, depot_lng], zoom_start=10)
        colores = ["blue", "green", "red", "purple", "orange"]

        for i, ruta in enumerate(rutas):
            color = colores[i % len(colores)]
            puntos = [p['coords'][::-1] for p in ruta]

            folium.PolyLine(puntos, color=color, weight=5, opacity=0.7, popup=f"Ruta {i+1}").add_to(mapa)

            for p in ruta:
                lat, lng = p['coords'][1], p['coords'][0]
                icono = folium.Icon(color=color if p['id'] != "Depot" else "black",
                                    icon="truck" if p['id'] != "Depot" else "home")
                folium.Marker([lat, lng], popup=str(p['id']), icon=icono).add_to(mapa)

        st.subheader("🗺️ Visualización en mapa")
        st_folium(mapa, width=700, height=500)

    else:
        st.error("No se encontró solución óptima.")


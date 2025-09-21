# ChivoFast-website

# 🚚 ChivoFast - Optimización de Rutas

Aplicación en **Streamlit** para optimizar rutas de entrega utilizando:
- [OpenRouteService](https://openrouteservice.org) (cálculo de distancias y rutas con OpenStreetMap)
- [Google OR-Tools](https://developers.google.com/optimization) (algoritmos de optimización de rutas de vehículos, VRP)
- Mapas interactivos con [Folium](https://python-visualization.github.io/folium/)

---

## 🔹 Características
✅ Carga de dataset de entregas desde CSV  
✅ Definición de punto de partida (almacén/depot)  
✅ Asignación de múltiples repartidores  
✅ Optimización de rutas con **Vehicle Routing Problem (VRP)**  
✅ Visualización de rutas en mapa interactivo  

---

## 🔹 Dataset de ejemplo
El dataset se encuentra en este repositorio:  
[`dataset_entregas.csv`](https://github.com/Medb935/ChivoFast-website/blob/main/dataset_entregas.csv)

Debe contener al menos estas columnas:

| cliente_id | lat     | lng     |
|------------|---------|---------|
| 1          | 13.6929 | -89.2182 |
| 2          | 13.9942 | -89.5597 |
| ...        | ...     | ...      |

---

## 🔹 Requisitos
Instalar dependencias con:

```bash
pip install -r requirements.txt

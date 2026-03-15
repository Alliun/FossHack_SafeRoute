from flask import Flask, request, jsonify
from flask_cors import CORS
import geopandas as gpd
import networkx as nx
import math

print("Loading road dataset...")

roads = gpd.read_file("geo/bangalore_roads_with_safety.geojson")

print("Dataset loaded")

app = Flask(__name__)
CORS(app)

# --------------------------------------------------
# Haversine distance (real km distance)
# --------------------------------------------------

def haversine(a, b):

    lon1, lat1 = a
    lon2, lat2 = b

    R = 6371  # earth radius km

    dlon = math.radians(lon2 - lon1)
    dlat = math.radians(lat2 - lat1)

    x = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)

    c = 2 * math.atan2(math.sqrt(x), math.sqrt(1-x))

    return R * c


# --------------------------------------------------
# Build Graph
# --------------------------------------------------

print("Building graph...")

G = nx.Graph()

for _, row in roads.iterrows():

    geom = row.geometry

    if geom.geom_type == "LineString":
        coords = list(geom.coords)

    elif geom.geom_type == "MultiLineString":
        coords = []
        for part in geom.geoms:
            coords += list(part.coords)

    else:
        continue

    safety = row.get("safety_score", 0.5)

    for i in range(len(coords)-1):

        p1 = coords[i]
        p2 = coords[i+1]

        dist = haversine(p1, p2)

        weight = dist * (1.5 - safety)

        G.add_edge(
            p1,
            p2,
            weight=weight,
            distance=dist,
            safety=safety
        )

print("Graph nodes:", len(G.nodes))
print("Graph edges:", len(G.edges))

# --------------------------------------------------
# Keep Largest Connected Component
# --------------------------------------------------

print("Cleaning disconnected roads...")

largest_component = max(nx.connected_components(G), key=len)

G = G.subgraph(largest_component).copy()

nodes = list(G.nodes)

print("Nodes after cleaning:", len(nodes))


# --------------------------------------------------
# Nearest node
# --------------------------------------------------

def nearest_node(point):

    px, py = point

    best = None
    best_dist = float("inf")

    for node in nodes:

        d = (node[0]-px)**2 + (node[1]-py)**2

        if d < best_dist:
            best_dist = d
            best = node

    return best


# --------------------------------------------------
# Route metrics
# --------------------------------------------------

def route_metrics(path):

    distance = 0
    safety_vals = []

    for i in range(len(path)-1):

        edge = G[path[i]][path[i+1]]

        distance += edge["distance"]
        safety_vals.append(edge["safety"])

    safety = sum(safety_vals)/len(safety_vals)

    return round(safety,2), round(distance,2)


# --------------------------------------------------
# API
# --------------------------------------------------

@app.route("/route", methods=["POST"])
def route():

    data = request.json

    start = tuple(data["start"])
    end = tuple(data["end"])

    print("Start:", start)
    print("End:", end)

    start_node = nearest_node(start)
    end_node = nearest_node(end)

    print("Nearest start:", start_node)
    print("Nearest end:", end_node)

    routes = []

    try:

        generator = nx.shortest_simple_paths(
            G,
            start_node,
            end_node,
            weight="weight"
        )

        for i, path in enumerate(generator):

            if i == 3:
                break

            coords = [[lat, lon] for lon, lat in path]

            safety, distance = route_metrics(path)

            routes.append({
                "coords": coords,
                "safety": safety,
                "distance": distance
            })

    except Exception as e:

        print("Routing error:", e)
        return jsonify([])

    print("Routes returned:", len(routes))

    return jsonify(routes)


if __name__ == "__main__":

    print("Starting routing server...")

    app.run(debug=True)
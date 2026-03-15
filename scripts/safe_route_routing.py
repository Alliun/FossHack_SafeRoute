import geopandas as gpd
import networkx as nx

print("Starting SafeRoute routing...")

# Load safety-aware road dataset
roads = gpd.read_file("geo/bangalore_roads_with_safety.geojson")

print("Road dataset loaded:", len(roads))

# Create graph
G = nx.Graph()

print("Building graph...")

for idx, row in roads.iterrows():

    geom = row.geometry
    safety = row["safety_score"]
    length = row["segment_length"]

    # Handle different geometry types
    if geom.geom_type == "LineString":
        coords = list(geom.coords)

    elif geom.geom_type == "MultiLineString":
        coords = list(list(geom.geoms)[0].coords)

    else:
        continue

    start = coords[0]
    end = coords[-1]

    # Calculate safety-aware cost
    if safety > 0:
        cost = length / safety
    else:
        cost = length * 10

    # Add edge to graph
    G.add_edge(start, end, weight=cost, length=length, safety=safety)

print("Graph built successfully!")
print("Total nodes:", len(G.nodes))
print("Total edges:", len(G.edges))

# Example start and destination coordinates
start_point = (77.5946, 12.9716)   # MG Road area
end_point = (77.5800, 12.9352)     # Jayanagar area

print("Finding safest route...")

# Find nearest graph nodes
start_node = min(
    G.nodes,
    key=lambda node: (node[0] - start_point[0])**2 + (node[1] - start_point[1])**2
)

end_node = min(
    G.nodes,
    key=lambda node: (node[0] - end_point[0])**2 + (node[1] - end_point[1])**2
)

# Compute safest path
route = nx.shortest_path(
    G,
    source=start_node,
    target=end_node,
    weight="weight"
)

print("Safest route found!")
print("Route node count:", len(route))
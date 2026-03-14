import geopandas as gpd
import osmnx as ox

print("Starting SafeRoute road segmentation...")

# Load ward boundaries
wards = gpd.read_file("geo/bangalore_wards.geojson")

print("Total wards:", len(wards))

# Create ward ID
wards = wards.reset_index().rename(columns={"index": "Ward_ID"})

# Keep ward id and geometry
wards = wards[["Ward_ID", "geometry"]]

print("Ward polygons ready")

# Download road network from OpenStreetMap
print("Downloading Bangalore road network...")

G = ox.graph_from_place("Bangalore, India", network_type="drive")

nodes, edges = ox.graph_to_gdfs(G)

roads = edges.reset_index()

roads = roads[["geometry", "length"]]

print("Total road segments:", len(roads))

# Match coordinate systems
roads = roads.to_crs(wards.crs)

print("CRS matched")

# Segment roads by wards
print("Splitting roads by ward boundaries...")

road_segments = gpd.overlay(
    roads,
    wards,
    how="intersection"
)

print("Segments created:", len(road_segments))

# Calculate segment length
road_segments["segment_length"] = road_segments.geometry.length

# Save output
output_path = "geo/bangalore_segmented_roads.geojson"

road_segments.to_file(output_path, driver="GeoJSON")

print("Segmented roads saved to:", output_path)

print("Road segmentation completed successfully.")
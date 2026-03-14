import geopandas as gpd
import pandas as pd

print("Starting safety score assignment...")

# Load segmented roads
roads = gpd.read_file("geo/bangalore_segmented_roads.geojson")

print("Segmented roads loaded:", len(roads))

# Load safety dataset
safety = pd.read_csv("data/bangalore_safe_route_ml_ready.csv")

print("Safety dataset loaded:", len(safety))

# Inspect columns (first run only)
print("Road columns:", roads.columns)
print("Safety columns:", safety.columns)

# ---- Match column names ----
# Adjust these if needed after checking printed columns

roads = roads.rename(columns={"ward_id": "Ward_ID"})

# Merge safety scores with road segments
roads_with_safety = roads.merge(
    safety,
    on="Ward_ID",
    how="left"
)

print("Safety merged")

# Example safety column (change if needed)
if "Norm_Safety_Score_V2" in roads_with_safety.columns:
    roads_with_safety["safety_score"] = roads_with_safety["Norm_Safety_Score_V2"]
else:
    print("Safety score column not found!")

# Keep only useful columns
roads_with_safety = roads_with_safety[[
    "geometry",
    "segment_length",
    "safety_score"
]]

# Save result
output_path = "geo/bangalore_roads_with_safety.geojson"

roads_with_safety.to_file(output_path, driver="GeoJSON")

print("Roads with safety scores saved to:", output_path)
print("Safety assignment complete.")
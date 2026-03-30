# 🚦 SafeRoute — AI-Assisted Safety-Aware Navigation System

## 🌍 Overview

**SafeRoute** is an intelligent navigation system that prioritizes **safety over shortest distance**. Unlike traditional navigation tools that optimize for speed or distance, SafeRoute integrates **urban infrastructure data** (like street lighting) to recommend routes that are **safer for real-world travel**, especially in sensitive scenarios like:

* 🌙 Night-time travel
* 👩 Women's safety navigation
* 🧭 Travel through unfamiliar areas
* 🚨 Emergency or risk-aware routing

The system computes a **Safety Score** for each road segment and uses it to generate:

* 🟢 **1 Safest Route**
* 🔴 **2 Alternative Routes**

All routes are visualized interactively on a map.

---

## 🎯 Objectives

* Build a **safety-first navigation system**
* Integrate **real-world urban datasets**
* Enable **multi-route comparison based on safety**
* Provide **visual and explainable safety insights**
* Lay foundation for **AI-driven real-time routing**

---

## 🧠 Core Concept

### 🔐 Safety Score

Each road segment is assigned a **Safety Score (0 → 1)**:

| Score | Meaning   |
| ----- | --------- |
| 0.9+  | Very Safe |
| ~0.5  | Moderate  |
| <0.2  | Unsafe    |

Currently derived from:

* 💡 Streetlight density

Future enhancements:

* 🚔 Crime data
* 👥 Crowd density
* 📹 CCTV presence
* 🚦 Traffic data

---

## 🏗️ System Architecture

```
Frontend (Leaflet + JS)
        ↓
Flask API (/route)
        ↓
NetworkX Graph Routing
        ↓
GeoSpatial Data (GeoJSON)
```

---

## 📁 Project Structure

```
SafeRoute/
│
├── geo/
│   └── bangalore_roads_with_safety.geojson
│
├── scripts/
│   ├── server.py                # Flask backend (routing engine)
│   └── visualize_route.py      # Map generation (frontend)
│
├── safe_route_map.html         # Generated interactive map
│
├── requirements.txt            # Python dependencies
│
└── README.md                   # Project documentation
```

---

## 📊 Datasets Used

### 1️⃣ Bangalore Road Network Dataset

**File:**

```
geo/bangalore_roads_with_safety.geojson
```

**Description:**
Contains the road network of Bangalore with precomputed safety scores.

**Structure:**

```json
{
  "type": "Feature",
  "geometry": {
    "type": "LineString",
    "coordinates": [[lon, lat], ...]
  },
  "properties": {
    "safety_score": 0.35
  }
}
```

**Usage:**

* Converted into a **graph structure**
* Each road segment → **edge**
* Used for **routing + visualization**

---

### 2️⃣ Streetlight Dataset

**Description:**
Contains streetlight locations and ward-level infrastructure data.

**Used for:**

* Estimating **lighting density**
* Contributing to **safety score**

**Insight:**

```
More streetlights → higher safety
Fewer lights → lower safety
```

---

## 🧮 Graph Construction

Built using:

* `NetworkX`
* `GeoPandas`
* `Shapely`

### Representation:

| Element | Meaning           |
| ------- | ----------------- |
| Node    | Road intersection |
| Edge    | Road segment      |

### Edge Attributes:

```python
distance      # km
safety_score  # 0–1
weight        # routing cost
```

---

## ⚙️ Routing Algorithm

### Algorithm Used:

```
NetworkX: shortest_simple_paths
```

### Cost Function:

```python
weight = distance * (1.5 - safety_score)
```

### Interpretation:

* Safer roads → lower cost
* Unsafe roads → penalized
* Slightly longer but safer routes preferred

---

## ⚡ Performance Optimization

### KDTree Spatial Indexing

Used for fast nearest-node lookup:

```python
from scipy.spatial import KDTree
```

### Improvement:

| Method      | Time     |
| ----------- | -------- |
| Brute force | O(n)     |
| KDTree      | O(log n) |

👉 ~200x faster node lookup

---

## 🌐 Backend (Flask API)

### Endpoint

```
POST /route
```

### Input

```json
{
  "start": [lng, lat],
  "end": [lng, lat]
}
```

### Output

```json
[
  {
    "coords": [...],
    "safety": 0.37,
    "distance": 12.3
  }
]
```

---

## 🗺️ Frontend Features

Built using:

* **Leaflet.js**
* **Folium**

### Features:

* 🖱 Click to select start & destination
* 🟢 Safest route (highlighted)
* 🔴 Alternate routes (dashed)
* 🏷 Safety score labels on routes
* 📊 Route comparison panel
* 🎨 Road-based safety visualization

---

## 🧪 Current Capabilities

✔ Safety-aware routing
✔ Multi-route comparison
✔ Interactive map UI
✔ Distance + safety metrics
✔ Fast node lookup (KDTree)
✔ Clean visualization

---

## ⚠️ Limitations

* Static safety model (no real-time data)
* Limited datasets (currently lighting-based)
* No user interaction with routes (yet)
* No dynamic rerouting

---

## 🚀 Future Improvements

### 🔥 High Priority

* [ ] Route selection (clickable routes)
* [ ] Expandable route explanation panel
* [ ] Layer toggle system

### 🧠 AI Enhancements

* [ ] ML-based safety prediction
* [ ] Multi-factor safety scoring
* [ ] Real-time data integration

### 📊 Additional Layers

* Crime hotspots
* Police stations
* Hospitals
* CCTV cameras

### 📱 Navigation Mode

* Real-time safe navigation
* Dynamic rerouting
* Hazard alerts

---

## 💡 Unique Value Proposition

SafeRoute is not just a map — it is an:

```
AI-powered Safety Navigation System
```

Key differentiators:

* Safety-first routing
* Explainable decision-making
* Real-world data integration
* Multi-route safety comparison

---

## 🛠️ Tech Stack

### Backend

* Python
* Flask
* NetworkX
* GeoPandas
* Shapely
* SciPy (KDTree)

### Frontend

* Leaflet.js
* Folium
* JavaScript
* HTML/CSS

### Data

* GeoJSON
* Urban infrastructure datasets

---

## ▶️ How to Run

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2️⃣ Start backend

```bash
python scripts/server.py
```

---

### 3️⃣ Generate map

```bash
python scripts/visualize_route.py
```

---

### 4️⃣ Open map

```
safe_route_map.html
```

or

```bash
python -m http.server 8000
```

---

## 🏁 Conclusion

SafeRoute demonstrates how **geospatial data + graph algorithms + real-world context** can transform navigation into a **safer and smarter experience**.

This project lays the foundation for:

* Smart city applications
* Safety-first urban mobility
* AI-powered navigation systems

---

## 👨‍💻 Contributors

* Sounava Banerjee
* (Add team members here)

---

## 📌 License

MIT License

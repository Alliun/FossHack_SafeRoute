import folium
import geopandas as gpd
import random
import math
import branca.colormap as cm

print("Loading dataset...")

roads = gpd.read_file("geo/bangalore_roads_with_safety.geojson")

# OPTIONAL CLEAN (recommended)
roads = roads.dropna(subset=["safety_score"])

print("Creating map...")

m = folium.Map(
    location=[12.97, 77.59],
    zoom_start=13,
    tiles="CartoDB positron"   # LIGHT THEME
)

# --------------------------------------------------
# ROAD SAFETY VISUALIZATION (STABLE)
# --------------------------------------------------

print("Rendering road safety layer...")

min_safety = roads["safety_score"].min()
max_safety = roads["safety_score"].max()

colormap = cm.LinearColormap(
    colors=["red", "yellow", "green"],
    vmin=min_safety,
    vmax=max_safety
)

colormap.caption = "Road Safety Score"
colormap.add_to(m)

# sample roads for performance
sample_roads = roads.sample(frac=0.15)

def style_function(feature):

    safety = feature["properties"].get("safety_score", 0.5)

    # FIX: handle invalid values
    if safety is None:
        safety = 0.5

    try:
        if math.isnan(safety):
            safety = 0.5
    except:
        pass

    return {
        "color": colormap(safety),
        "weight": 2,
        "opacity": 0.7
    }

folium.GeoJson(
    sample_roads,
    style_function=style_function
).add_to(m)

# --------------------------------------------------
# ROUTING SCRIPT
# --------------------------------------------------

click_script = """
<script>

document.addEventListener("DOMContentLoaded", function(){

var map = Object.values(window).find(obj => obj instanceof L.Map);

var startMarker = null;
var endMarker = null;

var routeLines = [];
var safetyMarkers = [];

var clickCount = 0;

var startPoint = null;
var endPoint = null;

map.on("click", function(e){

    clickCount++;

    if(clickCount === 1){

        if(startMarker) map.removeLayer(startMarker);

        startMarker = L.marker(e.latlng)
        .addTo(map)
        .bindPopup("Start")
        .openPopup();

        startPoint = e.latlng;

    }

    else if(clickCount === 2){

        if(endMarker) map.removeLayer(endMarker);

        endMarker = L.marker(e.latlng)
        .addTo(map)
        .bindPopup("Destination")
        .openPopup();

        endPoint = e.latlng;

        clickCount = 0;

        fetch("http://127.0.0.1:5000/route",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                start:[startPoint.lng,startPoint.lat],
                end:[endPoint.lng,endPoint.lat]
            })

        })
        .then(res=>res.json())
        .then(routes=>{

            if(!routes || routes.length === 0){
                alert("No route found");
                return;
            }

            routeLines.forEach(r=>map.removeLayer(r));
            safetyMarkers.forEach(m=>map.removeLayer(m));

            routeLines=[];
            safetyMarkers=[];

            // ALT ROUTES
            routes.slice(1).forEach(function(route,index){

                var poly=L.polyline(route.coords,{
                    color:'#ff4d4d',
                    weight:5,
                    opacity:0.7,
                    dashArray:'6,8'
                }).addTo(map);

                routeLines.push(poly);

                addSafetyMarker(route,"#ff4d4d",index+1);

            });

            // SAFEST ROUTE
            var safest=routes[0];

            var safestLine=L.polyline(safest.coords,{
                color:'#00cc66',
                weight:8,
                opacity:1
            }).addTo(map);

            routeLines.push(safestLine);

            addSafetyMarker(safest,"#00994d",0);

            var group = new L.featureGroup(routeLines);
            map.fitBounds(group.getBounds());

            updatePanel(routes);

        })
        .catch(err=>{
            console.log("Route error:",err);
        });

    }

});


function addSafetyMarker(route,color,index){

    if(!route.coords || route.coords.length === 0){
        return;
    }

    let position = (index === 0) ? 0.5 : (index === 1 ? 0.35 : 0.65);

    var pointIndex = Math.floor(route.coords.length * position);

    var mid = route.coords[pointIndex];

    var html =
        '<div style="\
        background:'+color+';\
        color:white;\
        padding:6px 10px;\
        border-radius:8px;\
        font-weight:600;\
        font-size:12px;\
        text-align:center;\
        box-shadow:0 2px 8px rgba(0,0,0,0.3);\
        min-width:70px;\
        ">\
        Safety '+route.safety+'\
        </div>';

    var icon = L.divIcon({
        className:'',
        html:html
    });

    var marker = L.marker(mid,{icon:icon}).addTo(map);

    safetyMarkers.push(marker);
}


function updatePanel(routes){

let html = `
<div style="
position:fixed;
top:20px;
left:20px;
background:white;
padding:15px;
border-radius:10px;
box-shadow:0 0 12px rgba(0,0,0,0.25);
z-index:9999;
width:230px;
font-family:sans-serif;
">

<b>SafeRoute Results</b><br><br>

<span style="color:#00cc66">● Safest Route</span><br>
Safety: ${routes[0].safety}<br>
Distance: ${routes[0].distance} km<br><br>
`;

if(routes.length>1){
html+=`
<span style="color:#ff4d4d">● Alt Route 1</span><br>
Safety: ${routes[1].safety}<br>
Distance: ${routes[1].distance} km<br><br>
`;
}

if(routes.length>2){
html+=`
<span style="color:#ff4d4d">● Alt Route 2</span><br>
Safety: ${routes[2].safety}<br>
Distance: ${routes[2].distance} km
`;
}

html+="</div>";

document.getElementById("result-panel")?.remove();

let panel=document.createElement("div");
panel.id="result-panel";
panel.innerHTML=html;
document.body.appendChild(panel);
}

});
</script>
"""

m.get_root().html.add_child(folium.Element(click_script))

# --------------------------------------------------
# INSTRUCTION PANEL
# --------------------------------------------------

panel="""
<div style="
position:fixed;
bottom:20px;
left:20px;
background:white;
padding:10px;
border-radius:8px;
box-shadow:0 0 8px rgba(0,0,0,0.25);
z-index:9999;
font-size:13px;
">
Click map to select start and destination
</div>
"""

m.get_root().html.add_child(folium.Element(panel))

m.save("safe_route_map.html")

print("Map generated successfully") 
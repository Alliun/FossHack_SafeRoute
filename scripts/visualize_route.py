import folium
import geopandas as gpd
import branca.colormap as cm

print("Loading safety dataset...")

roads = gpd.read_file("geo/bangalore_roads_with_safety.geojson")

# --------------------------------------------------
# DATASET OPTIMIZATION
# --------------------------------------------------

print("Optimizing dataset...")

# simplify geometry (reduces coordinate complexity)
roads["geometry"] = roads.geometry.simplify(0.0002, preserve_topology=True)

# sample only 30% of roads to reduce rendering load
roads = roads.sample(frac=0.3)

print("Creating SafeRoute map...")

m = folium.Map(
    location=[12.97, 77.59],
    zoom_start=13,
    tiles="CartoDB positron"
)

# --------------------------------------------------
# FAST SAFETY HEATMAP
# --------------------------------------------------

print("Rendering safety heatmap...")

colormap = cm.LinearColormap(
    colors=["#ff0000", "#ffff00", "#00ff00"],
    index=[0, 0.5, 1],
    vmin=0,
    vmax=1
)

def style_function(feature):

    safety = feature["properties"].get("safety_score", 0.5)

    if safety is None:
        safety = 0.5

    safety = max(0, min(1, safety))

    return {
        "color": colormap(safety),
        "weight": 2,
        "opacity": 0.8
    }

folium.GeoJson(
    roads,
    style_function=style_function,
    name="Safety Heatmap"
).add_to(m)

colormap.caption = "Road Safety Score"
colormap.add_to(m)

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

            routes.slice(1).forEach(function(route,index){

                var poly=L.polyline(route.coords,{
                    color:'red',
                    weight:6,
                    opacity:0.7,
                    dashArray:'6,8'
                }).addTo(map);

                routeLines.push(poly);

                addSafetyMarker(route,"red",index+1);

            });

            var safest=routes[0];

            var safestLine=L.polyline(safest.coords,{
                color:'green',
                weight:10,
                opacity:1
            }).addTo(map);

            routeLines.push(safestLine);

            addSafetyMarker(safest,"green",0);

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

    let position;

    if(index === 0){
        position = 0.5;
    }
    else if(index === 1){
        position = 0.35;
    }
    else{
        position = 0.65;
    }

    var pointIndex = Math.floor(route.coords.length * position);

    var mid = route.coords[pointIndex];

    var html =
        '<div style="\
        background:'+color+';\
        color:white;\
        padding:12px 20px;\
        border-radius:12px;\
        font-weight:bold;\
        font-size:15px;\
        min-width:95px;\
        text-align:center;\
        box-shadow:0 4px 12px rgba(0,0,0,0.45);\
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
box-shadow:0 0 15px rgba(0,0,0,0.3);
z-index:9999;
width:220px;
font-family:sans-serif;
">

<b>SafeRoute Results</b><br><br>

<span style="color:green">● Safest Route</span><br>
Safety Score: ${routes[0].safety}<br>
Distance: ${routes[0].distance} km<br><br>
`;

if(routes.length>1){

html+=`
<span style="color:red">● Alt Route 1</span><br>
Safety Score: ${routes[1].safety}<br>
Distance: ${routes[1].distance} km<br><br>
`;

}

if(routes.length>2){

html+=`
<span style="color:red">● Alt Route 2</span><br>
Safety Score: ${routes[2].safety}<br>
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
padding:12px;
border-radius:8px;
box-shadow:0 0 10px rgba(0,0,0,0.4);
z-index:9999;
font-size:14px;
">
Click map to select start and destination
</div>
"""

m.get_root().html.add_child(folium.Element(panel))

m.save("safe_route_map.html")

print("Map generated successfully")
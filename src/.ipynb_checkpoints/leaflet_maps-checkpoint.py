from ipyleaflet import Map, Marker, Popup, MarkerCluster, GeoJSON, DrawControl
from ipywidgets import HTML
import numpy as np
from datetime import datetime
from shapely.geometry import Polygon, Point
from tqdm import tqdm

def filter_markers(gdf, feature_collection,size=None):
    
    # Extract coordinates and create Polygon objects
    polygons = []
    for feature in feature_collection['features']:
        polygons.append(Polygon(feature['geometry']['coordinates'][0]))

    filtered_markers = []
    for idx, row in gdf.iterrows():
        if size and row.BRGARE < size: continue
        point = Point(row.geometry.x, row.geometry.y)
        for polygon in polygons:
            if polygon.contains(point):
                filtered_markers.append((idx,point))

    return(filtered_markers)

def markers_from_geojson(feature,popup=None):
    markers=[]
    for idx, marker in enumerate(feature):
        if popup:
            popup_content = f"<b>Iceberg {marker[0]}</b><br>"
            # Create a popup with the HTML widget
            popup = Popup(location=(marker[1].x, marker[1].y), child=HTML(popup_content), close_button=False)
        markers.append(Marker(location=(marker[1].y,marker[1].x), draggable=False, title=str(idx), popup=popup))
    return(markers)

def get_center(filtered_feature):
    points=[f for f in zip(*filtered_feature)][1]
    x,y=([point.x for point in points],[point.y for point in points])
    return(sum(y)/len(y),sum(x)/len(x))

def get_ids(filtered_feature):
    ids=[f for f in zip(*filtered_feature)][0]
    return([id for id in ids])

def mymap(gdf,subsample=4, markers=None,zoom=3,center=None, cluster=True):
    """
    Displays a map with markers for each geometry in the GeoDataFrame.

    Args:
        gdf (GeoDataFrame): Input GeoDataFrame with geometries.
        subsample (int): Subsampling factor for display.
        markers (list): Optional list of markers.
        zoom (int): Zoom level.
        center (tuple): Center of the map.
        cluster (bool): If True, markers are clustered. If False, markers are added individually.
    """
    # Create a base map centered around the mean of the geometries
    if center : m = Map(center=center, zoom=zoom)
    else : m = Map(center=(gdf.geometry.y.mean(), gdf.geometry.x.mean()), zoom=zoom)
    
    # Add markers with popups to the map
    if markers is None:
        markers = []
        for idx, row in tqdm(gdf.iterrows(),total=len(gdf)):
            
            if idx % subsample < (subsample -1): continue #subsampling for display
            # Create a popup string with all the information
            popup_content = f"<b>Iceberg {idx}</b><br>"
        
            # Create a popup with the HTML widget
            popup = Popup(location=(row.geometry.y, row.geometry.x), child=HTML(popup_content), close_button=False)
            
            # Create a marker with the popup
            markers.append(Marker(location=(row.geometry.y, row.geometry.x), draggable=False, title=str(idx), popup=popup))
                
    # Add markers to the map, clustered or not
    if cluster:
        marker_cluster = MarkerCluster(markers=markers)
        m.add_layer(marker_cluster)
    else:
        for marker in markers:
            m.add_layer(marker)
    
    # Add DrawControl to the map
    draw_control = DrawControl(
        polyline={},
        rectangle={},
        circle={},
        marker={},
        circlemarker={}
    )
    
    feature_collection = {
        'type': 'FeatureCollection',
        'features': []
    }
    
    def handle_draw(self, action, geo_json):
    
        #Do something with the GeoJSON when it's drawn on the map
        if action in ['created', 'edited']:
            feature_collection['features'].append(geo_json)
    
        #Clear when a feature is deleted
        elif action == 'deleted':
            feature_collection['features'].remove(geo_json)
        
    draw_control.on_draw(handle_draw)
    
    m.add_control(draw_control)
    
    m.layout.height="550px"
    
    # Display the map
    display(m)
    return(feature_collection)


def seed_from_geopandas(o,gdf,time=datetime.now(),minsize=4):

    parts=[]
    for idx, row in tqdm(gdf.iterrows(),total=len(gdf),desc=f"Seeding virtual particles on {len(gdf)} icebergs"):
        
        n=int(np.ceil(row.BRGARE/(50**2))) # we seed 1 particle per 50m^2 - with a minimum of 4
        if n < minsize: n = minsize
        
        lengths=int(np.ceil(row.IA_BLN))
        widths=int(np.ceil(row.BRGARE/row.IA_BLN))
        sails = np.linspace(5, 50, n)
        drafts = np.linspace(2, 120, n)
        
        lengths, widths, sails, drafts = np.meshgrid(lengths, widths, sails, drafts)
        lengths, widths, sails, drafts  = lengths.ravel(),widths.ravel(), sails.ravel(), drafts.ravel() 
        
        parts+=[lengths.size]
    
        #print(lengths.shape, widths.shape, sails.shape, drafts.shape)
        icebergs = {'lon': row.lon, 'lat': row.lat, 'time': time,
            'number': lengths.size, 'radius': 500,
            'sail': sails, 'draft': drafts, 'length': lengths, 'width': widths}
        o.seed_elements(**icebergs)
        
    print(f"Seeded {sum(parts)} virtual particles on {len(parts)} selected icebergs.\n"
          f"Minimal seeding size: {min(parts)} particles per iceberg\n"
          f"Maximal seeding size: {max(parts)} particles per iceberg")
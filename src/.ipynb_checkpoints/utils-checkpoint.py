import copernicusmarine
from datetime import datetime,timedelta, timezone
from src.copernicusmarine_Parser import BucketParser
from src.leaflet_maps import mymap, markers_from_geojson, get_ids, filter_markers, seed_from_geopandas
from ipywidgets import HTML
from IPython.display import Image
import geopandas as gpd
import logging
import numpy as np
import matplotlib.pyplot as plt
import requests
import json
import xarray as xr
from shapely.geometry import LineString



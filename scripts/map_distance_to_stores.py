#!/usr/bin/env python

from __future__ import division, print_function
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import folium
from math import cos, asin, sqrt
import json
import branca.colormap as cm

# ------------------- #
# Variables to define #
# ------------------- #

# Lat/lng of city center
city_center = [39.8289, -84.8902]

# Latitude to add/subtract to city center lat
offset_lat_top = 0.055
offset_lat_bottom = 0.035

# Longitude to add/subtract to city center lng
offset_lng_left = 0.075
offset_lng_right = 0.075

# Minimum/maximum values in color scale (units of miles)
minval = 0.0
maxval = 3.0

# Number of grids to use in each direction
ngrid = 50

# Colors in colormap
ncolor = 12

# ----------------------- #
# Done defining variables #
# ----------------------- #


def get_df(name):
    '''Return a dataframe'''
    return pd.read_csv(os.path.join('data', name + '_with_latlng.csv'))


def get_distance_between_lat_lng(lat1, lng1, lat2, lng2):
    '''Get the distance between two lat/lng points in miles'''
    p = 0.017453292519943295  # pi/180
    a = 0.5-cos((lat2-lat1)*p)/2+cos(lat1*p)*cos(lat2*p)*(1-cos((lng2-lng1)*p))/2
    return 0.6213*12742*asin(sqrt(a))  # 2*R*asin...


def get_distance_to_closest_store(lat, lng, df):
    '''
    Get distance to closest grocery store in miles
    and the name of that store
    '''
    min_distance = 1e12
    store = ''
    for index, row in df.iterrows():
        distance = get_distance_between_lat_lng(lat, lng, row.lat, row.lng)
        if distance < min_distance:
            min_distance = distance
            store = row.store_name
    return min_distance, store


def get_geojson_grid(upper_right, lower_left, n=ngrid):
    '''Returns a grid of geojson rectangles
       and computes the distance between the center of each rectangle
       and the closest grocery store.
    '''
    df = get_df('grocery_stores')
    grid = []
    distances_to_store = pd.DataFrame(columns=['id', 'distance', 'store'])
    lat_steps = np.linspace(lower_left[0], upper_right[0], n+1)
    lng_steps = np.linspace(lower_left[1], upper_right[1], n+1)
    lat_stride = lat_steps[1] - lat_steps[0]
    lng_stride = lng_steps[1] - lng_steps[0]
    geo_json = {'type': 'FeatureCollection', 'features': []}
    index = 1
    for lat in lat_steps[:-1]:
        for lng in lng_steps[:-1]:
            # Get distance to closest grocery store
            distance, closest_store = get_distance_to_closest_store(lat, lng, df)
            distances_to_store = distances_to_store.append({
                'id': index,
                'distance': distance,
                'store': closest_store
                }, ignore_index=True)
            # Define dimensions of box in grid
            upper_left = [lng, lat + lat_stride]
            upper_right = [lng + lng_stride, lat + lat_stride]
            lower_right = [lng + lng_stride, lat]
            lower_left = [lng, lat]
            # Define json coordinates for polygon
            coordinates = [
                upper_left,
                upper_right,
                lower_right,
                lower_left,
                upper_left]
            grid_json = {
                'type': 'Feature',
                'id': index,
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [coordinates]
                }
            }
            geo_json['features'].append(grid_json)
            index += 1
    return geo_json, distances_to_store


def get_richmond_boundaries():
    '''
    Return the boundaries of Richmond, IN as a geojson
    The boundaries were obtained here:
    http://polygons.openstreetmap.fr/index.py?id=127380
    '''
    with open('./data/richmond.geojson') as f:
        geojson = json.load(f)
    return geojson


def get_color(value, minval, maxval, cmap):
    '''Get the color bounded between the minimum and maximum value'''
    if value != value:
        return '#ffffff'
    else:
        value_bounded = max(minval, min(value, maxval))
        return cmap(value_bounded)


def initialize_map(city_center, zoom=13):
    '''Initialize the map'''
    lower_left = [city_center[0]-offset_lat_bottom, city_center[1]-offset_lng_left]
    upper_right = [city_center[0]+offset_lat_top, city_center[1]+offset_lng_right]
    m = folium.Map(zoom_start=zoom, location=city_center, tiles=None)
    folium.TileLayer('Stamen Toner', name='Available Layers').add_to(m)
    return m


def add_distances_to_map(m, colormap, city_center, offset_lat_bottom,
                         offset_lat_top, offset_lng_left, offset_lng_right):
    '''Add grid of distances to map'''
    lower_left = [city_center[0]-offset_lat_bottom, city_center[1]-offset_lng_left]
    upper_right = [city_center[0]+offset_lat_top, city_center[1]+offset_lng_right]
    geo_json, distances = get_geojson_grid(upper_right, lower_left)
    distances_dict = distances.set_index('id')['distance']
    folium.GeoJson(
        geo_json,
        name='Distance to closest grocery store',
        style_function=lambda feature: {
            'fillColor': get_color(distances_dict[feature['id']], minval, maxval, colormap),
            'fillOpacity': 0.7,
            'color': 'black',
            'weight': 0,
            'dashArray': '5, 5'
            }
        ).add_to(m)
    return m


def add_richmond_boundaries_to_map(m):
    '''Add the boundaries of Richmond to the map'''
    folium.GeoJson(
        get_richmond_boundaries(),
        name='Richmond boundaries',
        style_function=lambda feature: {
            'fillColor': 'white',
            'fillOpacity': 0,
            'color': 'black',
            'weight': 5,
            'dashArray': '10, 10'
            }
        ).add_to(m)
    return m


def add_grocery_stores_to_map(m):
    '''Add labels for grocery store locations'''
    feature_group = folium.map.FeatureGroup(name='Grocery stores')
    for i, row in get_df('grocery_stores').iterrows():
        logo_address = './data/' + row.store_name + '.png'
        icon = folium.features.CustomIcon(logo_address, icon_size=(row.img_width, row.img_height))
        feature_group.add_child(
            folium.Marker(
                [row.lat, row.lng],
                tooltip=row.store_name,
                icon=icon,
                img_size=(row.img_width, row.img_height)
                )
            )
    m.add_child(feature_group)
    return m


def get_colormap():
    '''Add a colorbar for the distance to grocery stores'''
    colormap = cm.LinearColormap(colors=['g', 'y', 'r'], vmin=minval, vmax=maxval).to_step(ncolor)
    colormap.caption = 'Distance to nearest grocery store (miles)'
    return colormap


def add_layer_control_to_map(m):
    '''Add layer control to the map'''
    folium.map.LayerControl('topleft', collapsed=False).add_to(m)
    return m


if __name__ == '__main__':
    m = initialize_map(city_center)
    m = add_distances_to_map(m, get_colormap(), city_center, offset_lat_bottom,
                             offset_lat_top, offset_lng_left, offset_lng_right)
    m = add_richmond_boundaries_to_map(m)
    m = add_grocery_stores_to_map(m)
    m.add_child(get_colormap())
    m = add_layer_control_to_map(m)
    if not os.path.isdir('results'):
        os.mkdir('results')
    m.save('./results/distance_to_stores.html')

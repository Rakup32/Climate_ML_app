import folium
from folium import plugins
import branca.colormap as cm
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
import os
import requests
from io import BytesIO
from folium.plugins import MarkerCluster
import json

class NepalMapVisualizer:
    def __init__(self):
        self.nepal_bounds = {
            'north': 30.45,
            'south': 26.35,
            'east': 88.20,
            'west': 80.06
        }
        self.elevation_data = None
        self.temperature_data = None
        
        # Define major geographical regions
        self.regions = {
            'terai': {
                'bounds': {'south': 26.35, 'north': 27.0},
                'base_elevation': 100,
                'variation': 200
            },
            'siwalik': {
                'bounds': {'south': 27.0, 'north': 27.5},
                'base_elevation': 500,
                'variation': 300
            },
            'mahabharat': {
                'bounds': {'south': 27.5, 'north': 28.0},
                'base_elevation': 1500,
                'variation': 500
            },
            'himal': {
                'bounds': {'south': 28.0, 'north': 30.45},
                'base_elevation': 3000,
                'variation': 2000
            }
        }
        
        # Define major river valleys
        self.river_valleys = [
            {
                'name': 'Koshi',
                'path': [(27.0, 87.0), (27.5, 86.5), (28.0, 86.0)],
                'width': 0.3,
                'depth': 500
            },
            {
                'name': 'Gandaki',
                'path': [(27.0, 84.5), (27.5, 84.0), (28.0, 83.5)],
                'width': 0.3,
                'depth': 500
            },
            {
                'name': 'Karnali',
                'path': [(27.0, 82.0), (27.5, 81.5), (28.0, 81.0)],
                'width': 0.3,
                'depth': 500
            }
        ]
        
        # Initialize elevation data
        self.elevation_data = self.generate_elevation_data()
        
    def generate_elevation_data(self):
        """Generate realistic elevation data for Nepal"""
        resolution = 0.01
        lats = np.arange(self.nepal_bounds['south'], self.nepal_bounds['north'], resolution)
        lons = np.arange(self.nepal_bounds['west'], self.nepal_bounds['east'], resolution)
        elevation = np.zeros((len(lats), len(lons)))
        
        # Generate base elevation for each region
        for i, lat in enumerate(lats):
            for j, lon in enumerate(lons):
                # Determine region
                region = None
                for reg_name, reg_data in self.regions.items():
                    if reg_data['bounds']['south'] <= lat < reg_data['bounds']['north']:
                        region = reg_data
                        break
                
                if region:
                    # Base elevation for the region
                    base_elev = region['base_elevation']
                    
                    # Add regional variation
                    variation = np.random.normal(0, region['variation'])
                    
                    # Add east-west variation (higher in the middle)
                    ew_factor = 1 - abs(lon - 84.0) / 4.0  # Center at 84°E
                    ew_variation = 500 * ew_factor
                    
                    elevation[i, j] = base_elev + variation + ew_variation
        
        # Add river valleys
        for valley in self.river_valleys:
            for i, lat in enumerate(lats):
                for j, lon in enumerate(lons):
                    # Check distance from river path
                    min_dist = float('inf')
                    for path_lat, path_lon in valley['path']:
                        dist = np.sqrt((lat - path_lat)**2 + (lon - path_lon)**2)
                        min_dist = min(min_dist, dist)
                    
                    if min_dist < valley['width']:
                        # Create valley effect
                        valley_factor = np.exp(-(min_dist / valley['width'])**2)
                        elevation[i, j] -= valley['depth'] * valley_factor
        
        # Add some noise for natural terrain
        noise = np.random.normal(0, 100, elevation.shape)
        elevation += noise
        
        # Ensure elevation stays within reasonable bounds
        elevation = np.clip(elevation, 50, 8848)  # Mount Everest height
        
        return elevation
        
    def create_base_map(self, center_lat=28.3949, center_lon=84.1240, zoom_start=7):
        """Create a base map centered on Nepal"""
        return folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles='CartoDB positron'
        )
        
    def add_elevation_layer(self, m, elevation_data):
        """Add elevation raster layer to the map"""
        if elevation_data is not None:
            # Create elevation colormap with more realistic colors
            elevation_colormap = cm.LinearColormap(
                colors=['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c'],
                vmin=elevation_data.min(),
                vmax=elevation_data.max(),
                caption='Elevation (m)'
            )
            
            # Add elevation layer
            folium.raster_layers.ImageOverlay(
                elevation_data,
                bounds=[[self.nepal_bounds['south'], self.nepal_bounds['west']],
                       [self.nepal_bounds['north'], self.nepal_bounds['east']]],
                colormap=elevation_colormap,
                opacity=0.7
            ).add_to(m)
            
            elevation_colormap.add_to(m)
            
    def add_temperature_layer(self, m, temperature_data, year):
        """Add temperature prediction layer to the map"""
        if temperature_data is not None:
            # Create temperature colormap with more realistic colors
            temp_colormap = cm.LinearColormap(
                colors=['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', 
                       '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027'],
                vmin=temperature_data.min(),
                vmax=temperature_data.max(),
                caption=f'Temperature (°C) - {year}'
            )
            
            # Add temperature layer
            folium.raster_layers.ImageOverlay(
                temperature_data,
                bounds=[[self.nepal_bounds['south'], self.nepal_bounds['west']],
                       [self.nepal_bounds['north'], self.nepal_bounds['east']]],
                colormap=temp_colormap,
                opacity=0.7
            ).add_to(m)
            
            temp_colormap.add_to(m)
            
    def add_city_markers(self, m, cities_data):
        """Add city markers with temperature predictions"""
        for city, data in cities_data.items():
            folium.CircleMarker(
                location=[data['lat'], data['lon']],
                radius=8,
                popup=f"{city}<br>Temperature: {data['temperature']:.1f}°C<br>Elevation: {data['elevation']}m",
                color='red',
                fill=True,
                fill_color='red'
            ).add_to(m)
            
    def create_interactive_map(self, cities_data, elevation_data=None, temperature_data=None, year=None):
        """Create an interactive map with all layers"""
        m = self.create_base_map()
        
        # Add base layers
        folium.TileLayer('CartoDB positron', name='Base Map').add_to(m)
        folium.TileLayer('CartoDB dark_matter', name='Dark Mode').add_to(m)
        folium.TileLayer('Stamen Terrain', name='Terrain').add_to(m)
        
        # Add elevation layer with enhanced visualization
        if elevation_data is not None:
            elevation_colormap = cm.LinearColormap(
                colors=['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c'],
                vmin=elevation_data.min(),
                vmax=elevation_data.max(),
                caption='Elevation (m)'
            )
            
            folium.raster_layers.ImageOverlay(
                elevation_data,
                bounds=[[self.nepal_bounds['south'], self.nepal_bounds['west']],
                       [self.nepal_bounds['north'], self.nepal_bounds['east']]],
                colormap=elevation_colormap,
                opacity=0.7,
                name='Elevation'
            ).add_to(m)
            
            elevation_colormap.add_to(m)
            
        # Add temperature layer with enhanced visualization
        if temperature_data is not None:
            temp_colormap = cm.LinearColormap(
                colors=['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', 
                       '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027'],
                vmin=temperature_data.min(),
                vmax=temperature_data.max(),
                caption=f'Temperature (°C) - {year}'
            )
            
            folium.raster_layers.ImageOverlay(
                temperature_data,
                bounds=[[self.nepal_bounds['south'], self.nepal_bounds['west']],
                       [self.nepal_bounds['north'], self.nepal_bounds['east']]],
                colormap=temp_colormap,
                opacity=0.7,
                name='Temperature'
            ).add_to(m)
            
            temp_colormap.add_to(m)
            
        # Add city markers with enhanced visualization
        marker_cluster = MarkerCluster(name='Cities').add_to(m)
        
        for city, data in cities_data.items():
            # Create custom popup with more information
            popup_html = f"""
            <div style='width: 200px'>
                <h4 style='margin-bottom: 5px'>{city}</h4>
                <p style='margin: 2px 0'><b>Temperature:</b> {data['temperature']:.1f}°C</p>
                <p style='margin: 2px 0'><b>Elevation:</b> {data['elevation']}m</p>
                <p style='margin: 2px 0'><b>Coordinates:</b> {data['lat']:.2f}°N, {data['lon']:.2f}°E</p>
            </div>
            """
            
            # Create circle marker with size based on temperature
            radius = 8 + (data['temperature'] - temperature_data.min()) / 2
            
            folium.CircleMarker(
                location=[data['lat'], data['lon']],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=300),
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.7,
                tooltip=f"{city}: {data['temperature']:.1f}°C"
            ).add_to(marker_cluster)
            
        # Add layer control with collapsed option
        folium.LayerControl(collapsed=True).add_to(m)
        
        # Add minimap
        minimap = plugins.MiniMap()
        m.add_child(minimap)
        
        # Add fullscreen option
        plugins.Fullscreen().add_to(m)
        
        # Add mouse position
        fmtr = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
        plugins.MousePosition(
            position='bottomleft',
            separator=' | ',
            prefix="Mouse:",
            lat_formatter=fmtr,
            lng_formatter=fmtr
        ).add_to(m)
        
        return m
        
    def generate_temperature_raster(self, base_temp, elevation_data):
        """Generate temperature raster data based on elevation and latitude"""
        # Create temperature grid
        resolution = 0.01
        lats = np.arange(self.nepal_bounds['south'], self.nepal_bounds['north'], resolution)
        lons = np.arange(self.nepal_bounds['west'], self.nepal_bounds['east'], resolution)
        temperature = np.zeros((len(lats), len(lons)))
        
        # Calculate temperature based on elevation and latitude
        for i, lat in enumerate(lats):
            for j, lon in enumerate(lons):
                # Base temperature adjusted for latitude
                lat_factor = 1 - abs(lat - 28.3949) / 10  # Center at Nepal's latitude
                
                # Elevation effect (temperature decreases with height)
                elevation = elevation_data[i, j]
                lapse_rate = 6.5  # °C per 1000m
                elevation_effect = -lapse_rate * elevation / 1000
                
                # Combine effects
                temperature[i, j] = base_temp * lat_factor + elevation_effect
                
        return temperature 
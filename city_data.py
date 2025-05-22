import pandas as pd
import numpy as np

# City coordinates and elevation data
CITY_DATA = {
    'Kathmandu': {
        'lat': 27.7172,
        'lon': 85.3240,
        'elevation': 1400,  # meters
        'region': 'Central'
    },
    'Pokhara': {
        'lat': 28.2096,
        'lon': 83.9856,
        'elevation': 822,
        'region': 'Western'
    },
    'Bharatpur': {
        'lat': 27.6833,
        'lon': 84.4333,
        'elevation': 208,
        'region': 'Central'
    },
    'Biratnagar': {
        'lat': 26.4525,
        'lon': 87.2718,
        'elevation': 72,
        'region': 'Eastern'
    },
    'Dharan': {
        'lat': 26.8147,
        'lon': 87.2677,
        'elevation': 371,
        'region': 'Eastern'
    }
}

def get_city_coordinates():
    """Returns a DataFrame with city coordinates"""
    cities_df = pd.DataFrame.from_dict(CITY_DATA, orient='index')
    cities_df.index.name = 'city'
    return cities_df

def adjust_temperature_by_elevation(base_temp, elevation):
    """Adjust temperature based on elevation (lapse rate of 6.5°C per 1000m)"""
    lapse_rate = 6.5  # °C per 1000m
    elevation_diff = elevation / 1000  # convert to km
    return base_temp - (lapse_rate * elevation_diff)

def generate_city_temperatures(base_data, city_name):
    """Generate temperature data for a specific city based on base data and elevation"""
    city_info = CITY_DATA[city_name]
    city_data = base_data.copy()
    
    # Adjust temperatures based on elevation
    city_data['temperature'] = city_data['temperature'].apply(
        lambda x: adjust_temperature_by_elevation(x, city_info['elevation'])
    )
    
    # Add city information
    city_data['city'] = city_name
    city_data['lat'] = city_info['lat']
    city_data['lon'] = city_info['lon']
    city_data['elevation'] = city_info['elevation']
    city_data['region'] = city_info['region']
    
    return city_data 
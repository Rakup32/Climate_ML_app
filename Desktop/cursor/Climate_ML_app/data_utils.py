import pandas as pd
import requests
import json
from datetime import datetime
import os
import time

def load_nepal_climate_data():
    """
    Loads climate data for Nepal from the World Bank Climate Data API
    Returns a pandas DataFrame with climate data
    """
    try:
        # World Bank Climate Data API endpoint for Nepal
        base_url = "https://api.worldbank.org/v2/country/NPL/indicator"
        
        # Temperature data (average annual temperature)
        temp_params = {
            'format': 'json',
            'date': '1990:2023',  # Get data from 1990 to 2023
            'per_page': 1000,
            'indicator': 'AG.TMP.AVG'  # Average temperature indicator
        }
        
        # Precipitation data (average annual precipitation)
        precip_params = {
            'format': 'json',
            'date': '1990:2023',
            'per_page': 1000,
            'indicator': 'AG.PCP.AVG'  # Average precipitation indicator
        }
        
        # Make API requests with retry logic
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                temp_response = requests.get(base_url, params=temp_params)
                precip_response = requests.get(base_url, params=precip_params)
                
                # Check if requests were successful
                if temp_response.status_code == 200 and precip_response.status_code == 200:
                    break
                elif attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(f"API request failed after {max_retries} attempts. Status codes: Temperature={temp_response.status_code}, Precipitation={precip_response.status_code}")
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(f"API request failed: {str(e)}")
        
        # Parse JSON responses
        temp_data = json.loads(temp_response.text)
        precip_data = json.loads(precip_response.text)
        
        # Check if we have valid data in the response
        if not temp_data or len(temp_data) < 2 or not temp_data[1]:
            raise Exception("No temperature data found in API response")
        if not precip_data or len(precip_data) < 2 or not precip_data[1]:
            raise Exception("No precipitation data found in API response")
        
        # Extract data from responses
        temp_records = []
        for record in temp_data[1]:
            if record.get('value') is not None:
                temp_records.append({
                    'year': int(record['date']),
                    'temperature': float(record['value'])
                })
        
        precip_records = []
        for record in precip_data[1]:
            if record.get('value') is not None:
                precip_records.append({
                    'year': int(record['date']),
                    'precipitation': float(record['value'])
                })
        
        # Convert to DataFrames
        temp_df = pd.DataFrame(temp_records)
        precip_df = pd.DataFrame(precip_records)
        
        # Merge temperature and precipitation data
        climate_data = pd.merge(temp_df, precip_df, on='year', how='outer')
        
        # Basic data cleaning
        climate_data = climate_data.dropna()
        climate_data = climate_data.sort_values('year')
        
        return climate_data
        
    except Exception as e:
        print(f"Error loading climate data from API: {e}")
        # Fallback to local data if API fails
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_file = os.path.join(current_dir, 'nepal_climate_data.csv')
            climate_data = pd.read_csv(data_file)
            print("Using local data as fallback")
            return climate_data
        except Exception as local_error:
            print(f"Error loading local data: {local_error}")
            return None

def extract_features(climate_data):
    """
    Extracts relevant features from climate data including daily and monthly time features
    Returns a DataFrame with engineered features
    """
    if climate_data is None or climate_data.empty:
        return None
        
    try:
        features = climate_data.copy()
        
        # Convert year to datetime to extract month and day
        features['date'] = pd.to_datetime(features['year'].astype(str), format='%Y')
        features['month'] = features['date'].dt.month
        features['day'] = features['date'].dt.day
        
        # Monthly aggregations
        features['monthly_temp_mean'] = features.groupby('month')['temperature'].transform('mean')
        features['monthly_precip_mean'] = features.groupby('month')['precipitation'].transform('mean')
        
        # Daily features
        features['day_of_year'] = features['date'].dt.dayofyear
        features['is_winter'] = ((features['month'] >= 12) | (features['month'] <= 2)).astype(int)
        features['is_monsoon'] = ((features['month'] >= 6) & (features['month'] <= 9)).astype(int)
        
        # Seasonal calculations
        features['temp_seasonal'] = features.groupby(['month'])['temperature'].transform(lambda x: x - x.mean())
        features['precip_seasonal'] = features.groupby(['month'])['precipitation'].transform(lambda x: x - x.mean())
        
        # Monthly trends
        features['monthly_temp_std'] = features.groupby('month')['temperature'].transform('std')
        features['monthly_precip_std'] = features.groupby('month')['precipitation'].transform('std')
        
        # Drop intermediate columns and NaN values
        features = features.drop('date', axis=1)
        features = features.dropna()
        
        return features
        
    except Exception as e:
        print(f"Error extracting features: {e}")
        return None

def prepare_features_for_model(features_df):
    """
    Prepares features for model training by separating target and feature columns
    Returns X (features) and y (target) DataFrames
    """
    if features_df is None or features_df.empty:
        return None, None
        
    try:
        # Define target columns including year and month
        target_cols = ['temperature', 'precipitation', 'year', 'month']
        
        # Separate features and target
        y = features_df[target_cols]
        X = features_df.drop(target_cols, axis=1)
        
        return X, y
        
    except Exception as e:
        print(f"Error preparing features for model: {e}")
        return None, None





import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

class ClimatePredictor:
    def __init__(self):
        self.city_models = {}
        self.scaler = StandardScaler()
        self.feature_importance = {}
        
    def prepare_data(self, climate_data):
        """Prepare data for time series prediction with advanced features"""
        df = climate_data.copy()
        df['year'] = pd.to_datetime(df['year'].astype(str))
        df.set_index('year', inplace=True)
        
        # Add advanced features
        df['year_sin'] = np.sin(2 * np.pi * df.index.year / 100)
        df['year_cos'] = np.cos(2 * np.pi * df.index.year / 100)
        
        # Add rolling statistics
        df['temp_rolling_mean'] = df['temperature'].rolling(window=5).mean()
        df['temp_rolling_std'] = df['temperature'].rolling(window=5).std()
        
        # Add temperature differences
        df['temp_diff'] = df['temperature'].diff()
        df['temp_diff2'] = df['temp_diff'].diff()
        
        # Fill NaN values
        df = df.fillna(method='bfill')
        
        return df
        
    def train(self, climate_data, city_name=None):
        """Train the temperature prediction model with multiple models"""
        try:
            # Prepare data
            df = self.prepare_data(climate_data)
            
            # Train multiple models
            models = {}
            
            # 1. SARIMA model for seasonal patterns
            sarima_model = SARIMAX(
                df['temperature'],
                order=(2,1,2),
                seasonal_order=(1,1,1,12)
            )
            models['sarima'] = sarima_model.fit(disp=False)
            
            # 2. Random Forest for non-linear patterns
            rf_features = ['year_sin', 'year_cos', 'temp_rolling_mean', 
                          'temp_rolling_std', 'temp_diff', 'temp_diff2']
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rf_model.fit(df[rf_features], df['temperature'])
            models['rf'] = rf_model
            
            # Store feature importance
            if city_name:
                self.feature_importance[city_name] = dict(zip(rf_features, 
                    rf_model.feature_importances_))
            
            # Store models
            if city_name:
                self.city_models[city_name] = models
            else:
                self.temp_model = models
            
            return True
        except Exception as e:
            print(f"Error training model for {city_name if city_name else 'base'}: {e}")
            return False
            
    def predict(self, years_to_predict, city_name=None):
        """Make temperature predictions using ensemble of models"""
        try:
            models = self.city_models.get(city_name) if city_name else self.temp_model
            if models is None:
                raise Exception(f"Model not trained for {city_name if city_name else 'base'}")
            
            # Generate predictions from each model
            predictions = {}
            
            # SARIMA predictions
            sarima_forecast = models['sarima'].forecast(steps=years_to_predict)
            predictions['sarima'] = sarima_forecast
            
            # Random Forest predictions
            last_year = pd.Timestamp.now().year
            future_years = pd.date_range(start=str(last_year + 1), 
                                       periods=years_to_predict, 
                                       freq='Y')
            
            # Prepare features for RF prediction
            future_features = pd.DataFrame({
                'year_sin': np.sin(2 * np.pi * future_years.year / 100),
                'year_cos': np.cos(2 * np.pi * future_years.year / 100),
                'temp_rolling_mean': sarima_forecast.mean(),
                'temp_rolling_std': sarima_forecast.std(),
                'temp_diff': 0,
                'temp_diff2': 0
            })
            
            rf_forecast = models['rf'].predict(future_features)
            predictions['rf'] = rf_forecast
            
            # Ensemble predictions (weighted average)
            ensemble_forecast = 0.6 * sarima_forecast + 0.4 * rf_forecast
            
            # Create prediction DataFrame
            predictions_df = pd.DataFrame({
                'year': future_years.year,
                'temperature': ensemble_forecast,
                'sarima_pred': sarima_forecast,
                'rf_pred': rf_forecast
            })
            
            if city_name:
                predictions_df['city'] = city_name
            
            return predictions_df
            
        except Exception as e:
            print(f"Error making predictions for {city_name if city_name else 'base'}: {e}")
            return None
            
    def get_feature_importance(self, city_name=None):
        """Get feature importance for a specific city"""
        if city_name:
            return self.feature_importance.get(city_name)
        return None

    def predict_all_cities(self, years_to_predict, base_predictions):
        """Make predictions for all cities based on base predictions"""
        all_predictions = []
        
        for city_name in self.city_models.keys():
            city_predictions = base_predictions.copy()
            city_predictions['city'] = city_name
            all_predictions.append(city_predictions)
            
        return pd.concat(all_predictions, ignore_index=True) 
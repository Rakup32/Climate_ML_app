import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from visualizations import plot_prediction_history, plot_climate_timeseries, plot_seasonal_patterns
import sys
import os
import folium
from folium.plugins import MarkerCluster

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from model import ClimatePredictor
from city_data import CITY_DATA, generate_city_temperatures, get_city_coordinates
from map_utils import NepalMapVisualizer

def show_prediction(climate_data, features):
    st.subheader("Nepal City Climate Predictions")
    
    # Initialize the predictor and map visualizer
    predictor = ClimatePredictor()
    map_viz = NepalMapVisualizer()
    
    # Train base model
    with st.spinner('Training prediction model...'):
        if predictor.train(climate_data):
            st.success('Base model trained successfully!')
        else:
            st.error('Error training the base model. Please try again.')
            return
    
    # Train city-specific models
    with st.spinner('Training city-specific models...'):
        for city_name in CITY_DATA.keys():
            city_data = generate_city_temperatures(climate_data, city_name)
            predictor.train(city_data, city_name)
    
    # Interactive prediction controls
    col1, col2 = st.columns(2)
    with col1:
        years_to_predict = st.slider("Select years to forecast", 1, 10, 5)
    with col2:
        selected_city = st.selectbox("Select city", list(CITY_DATA.keys()))
    
    st.info(f"Forecasting {years_to_predict} years into the future for {selected_city}...")
    
    # Make predictions
    base_predictions = predictor.predict(years_to_predict)
    city_predictions = predictor.predict(years_to_predict, selected_city)
    
    if base_predictions is not None and city_predictions is not None:
        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs(["City Forecast", "Map View", "Model Analysis", "Comparison"])
        
        with tab1:
            # City-specific forecast plot
            fig_forecast = go.Figure()
            
            # Add historical data
            city_historical = generate_city_temperatures(climate_data, selected_city)
            fig_forecast.add_trace(go.Scatter(
                x=city_historical['year'],
                y=city_historical['temperature'],
                name=f"Historical {selected_city}",
                line=dict(color='blue')
            ))
            
            # Add predictions
            fig_forecast.add_trace(go.Scatter(
                x=city_predictions['year'],
                y=city_predictions['temperature'],
                name=f"Ensemble Prediction",
                line=dict(color='red', dash='dash')
            ))
            
            # Add individual model predictions
            fig_forecast.add_trace(go.Scatter(
                x=city_predictions['year'],
                y=city_predictions['sarima_pred'],
                name="SARIMA Prediction",
                line=dict(color='green', dash='dot')
            ))
            
            fig_forecast.add_trace(go.Scatter(
                x=city_predictions['year'],
                y=city_predictions['rf_pred'],
                name="Random Forest Prediction",
                line=dict(color='purple', dash='dot')
            ))
            
            # Update layout
            fig_forecast.update_layout(
                title=f"Temperature Forecast for {selected_city}",
                xaxis_title="Year",
                yaxis_title="Temperature (°C)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_forecast)
        
        with tab2:
            # Generate elevation and temperature rasters
            elevation_data = map_viz.elevation_data
            if elevation_data is None:
                st.error("Could not load elevation data. Please try again.")
                return
            
            temperature_data = map_viz.generate_temperature_raster(
                city_predictions['temperature'].iloc[0],
                elevation_data
            )
            
            # Prepare city data for map
            cities_data = {}
            for city in CITY_DATA.keys():
                city_pred = predictor.predict(years_to_predict, city)
                if city_pred is not None:
                    cities_data[city] = {
                        **CITY_DATA[city],
                        'temperature': city_pred['temperature'].iloc[0]
                    }
            
            # Create and display the map
            m = map_viz.create_interactive_map(
                cities_data,
                elevation_data=elevation_data,
                temperature_data=temperature_data,
                year=city_predictions['year'].iloc[0]
            )
            # Display the map using folium's HTML representation
            st.components.v1.html(m._repr_html_(), height=600)
        
        with tab3:
            # Model analysis
            st.subheader("Model Analysis")
            
            # Feature importance
            feature_importance = predictor.get_feature_importance(selected_city)
            if feature_importance:
                fig_importance = px.bar(
                    x=list(feature_importance.keys()),
                    y=list(feature_importance.values()),
                    title=f"Feature Importance for {selected_city}",
                    labels={'x': 'Feature', 'y': 'Importance'}
                )
                st.plotly_chart(fig_importance)
            
            # Model comparison
            st.subheader("Model Comparison")
            model_metrics = pd.DataFrame({
                'Model': ['SARIMA', 'Random Forest', 'Ensemble'],
                'Weight': [0.6, 0.4, 1.0],
                'Description': [
                    'Time series model for seasonal patterns',
                    'Machine learning model for non-linear patterns',
                    'Weighted combination of both models'
                ]
            })
            st.table(model_metrics)
        
        with tab4:
            # Compare predictions across cities
            all_city_predictions = []
            for city in CITY_DATA.keys():
                city_pred = predictor.predict(years_to_predict, city)
                if city_pred is not None:
                    all_city_predictions.append(city_pred)
            
            if all_city_predictions:
                combined_predictions = pd.concat(all_city_predictions)
                
                fig_comparison = px.line(
                    combined_predictions,
                    x='year',
                    y='temperature',
                    color='city',
                    title="Temperature Predictions Across Cities",
                    labels={'year': 'Year', 'temperature': 'Temperature (°C)'}
                )
                
                st.plotly_chart(fig_comparison)
        
        # Display prediction metrics
        st.subheader("Prediction Metrics")
        
        # Calculate city-specific metrics
        last_historical = city_historical['temperature'].iloc[-1]
        first_prediction = city_predictions['temperature'].iloc[0]
        temp_change = first_prediction - last_historical
        
        # Calculate prediction confidence based on model agreement
        sarima_pred = city_predictions['sarima_pred'].iloc[0]
        rf_pred = city_predictions['rf_pred'].iloc[0]
        model_diff = abs(sarima_pred - rf_pred)
        confidence = 100 - (model_diff * 10)  # Higher difference means lower confidence
        
        # Calculate elevation-based metrics
        elevation = CITY_DATA[selected_city]['elevation']
        elevation_factor = 1 - (elevation / 8848)  # Normalize by Everest height
        elevation_impact = f"{elevation_factor * 100:.1f}%"
        
        # Create metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label=f"Temperature Change",
                value=f"{temp_change:.2f}°C",
                delta=f"{temp_change:.2f}°C",
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                label="Model Confidence",
                value=f"{confidence:.1f}%",
                delta=f"{model_diff:.2f}°C model difference",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                label="Elevation Impact",
                value=elevation_impact,
                delta=f"{elevation}m above sea level"
            )
            
        with col4:
            st.metric(
                label="Prediction Range",
                value=f"{min(sarima_pred, rf_pred):.1f}°C - {max(sarima_pred, rf_pred):.1f}°C",
                delta="Model range"
            )
        
        # Add advanced metrics visualization
        st.subheader("Advanced Metrics")
        
        # Create tabs for different metric visualizations
        metric_tab1, metric_tab2, metric_tab3 = st.tabs(["Model Comparison", "Elevation Analysis", "Trend Analysis"])
        
        with metric_tab1:
            # Model comparison metrics
            model_metrics = pd.DataFrame({
                'Model': ['SARIMA', 'Random Forest'],
                'Prediction': [sarima_pred, rf_pred],
                'Confidence': [confidence * 0.6, confidence * 0.4]
            })
            
            fig_models = px.bar(
                model_metrics,
                x='Model',
                y='Prediction',
                color='Confidence',
                title=f"Model Predictions for {selected_city}",
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_models)
            
        with metric_tab2:
            # Elevation impact analysis
            elevation_data = pd.DataFrame({
                'City': list(CITY_DATA.keys()),
                'Elevation': [data['elevation'] for data in CITY_DATA.values()],
                'Temperature': [predictor.predict(1, city)['temperature'].iloc[0] 
                              for city in CITY_DATA.keys()]
            })
            
            fig_elevation = px.scatter(
                elevation_data,
                x='Elevation',
                y='Temperature',
                hover_name='City',
                title="Temperature vs Elevation",
                trendline="ols"
            )
            st.plotly_chart(fig_elevation)
            
        with metric_tab3:
            # Trend analysis
            historical_trend = city_historical['temperature'].rolling(window=3).mean()
            future_trend = city_predictions['temperature'].rolling(window=2).mean()
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=city_historical['year'],
                y=historical_trend,
                name='Historical Trend',
                line=dict(color='blue')
            ))
            fig_trend.add_trace(go.Scatter(
                x=city_predictions['year'],
                y=future_trend,
                name='Predicted Trend',
                line=dict(color='red', dash='dash')
            ))
            
            fig_trend.update_layout(
                title=f"Temperature Trend Analysis for {selected_city}",
                xaxis_title="Year",
                yaxis_title="Temperature (°C)",
                hovermode='x unified'
            )
            st.plotly_chart(fig_trend)
    else:
        st.error("Error generating predictions. Please try again.")

if __name__ == "__main__":
    show_prediction()
    
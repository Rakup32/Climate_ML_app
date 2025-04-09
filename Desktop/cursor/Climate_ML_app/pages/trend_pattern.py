import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def show_trend_pattern(climate_data, features):
    """
    Display climate trends and patterns visualization.
    
    Args:
        climate_data (pd.DataFrame): Climate data containing year, temperature, and precipitation
        features (pd.DataFrame): Processed features containing month and other derived features
    """
    st.subheader("Climate Trends and Patterns")
    
    # Display climate time series plots
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature trend
        fig_temp = px.line(climate_data, x='year', y='temperature',
                          title='Temperature Trend Over Time')
        fig_temp.update_layout(yaxis_title='Temperature (°C)')
        st.plotly_chart(fig_temp)
        
    with col2:
        # Precipitation trend 
        fig_precip = px.line(climate_data, x='year', y='precipitation',
                            title='Precipitation Trend Over Time')
        fig_precip.update_layout(yaxis_title='Precipitation (mm)')
        st.plotly_chart(fig_precip)

    # Display seasonal patterns
    st.subheader("Seasonal Patterns")
    
    try:
        # Calculate monthly averages
        monthly_temp = features.groupby('month')['temperature'].mean()
        monthly_precip = features.groupby('month')['precipitation'].mean()
        
        # Combined seasonal plot
        fig_seasonal = go.Figure()
        fig_seasonal.add_trace(go.Scatter(x=monthly_temp.index, y=monthly_temp,
                                        name="Temperature", yaxis="y1"))
        fig_seasonal.add_trace(go.Bar(x=monthly_precip.index, y=monthly_precip,
                                    name="Precipitation", yaxis="y2"))
        
        fig_seasonal.update_layout(
            title="Monthly Temperature and Precipitation Patterns",
            yaxis=dict(title="Temperature (°C)"),
            yaxis2=dict(title="Precipitation (mm)", overlaying="y", side="right")
        )
        st.plotly_chart(fig_seasonal)
        
    except Exception as e:
        st.error(f"Error displaying seasonal patterns: {e}")
        st.warning("Could not generate seasonal pattern visualization")
            
    # Box plot by season
    features['season'] = pd.cut(features['month'], 
                              bins=[0,3,6,9,12], 
                              labels=['Winter', 'Spring', 'Summer', 'Fall'])
    
    col3, col4 = st.columns(2)
    
    with col3:
        fig_temp_box = px.box(features, x='season', y='temperature',
                            title="Temperature Distribution by Season")
        st.plotly_chart(fig_temp_box)
        
    with col4:
        fig_precip_box = px.box(features, x='season', y='precipitation',
                               title="Precipitation Distribution by Season") 
        st.plotly_chart(fig_precip_box)
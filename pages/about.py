"""
About page module for the Climate ML application.
"""

import streamlit as st
import sys
import os

def show_about():
    """
    Display the About page content.
    """
    st.markdown("""
    ### About This Application
    This application serves as a comprehensive climate analysis tool focused on Nepal's historical weather patterns. 
    It processes and analyzes data to provide insights into:
    - Temperature variations (daily, monthly, and yearly trends)
    - Precipitation patterns and rainfall distribution
    - Seasonal changes and their impacts
    - Climate predictions using machine learning models
    - Extreme weather event analysis
    
    The data is sourced from the World Bank Climate Data API and updated daily to ensure accuracy and relevance.
    """)

    # Detailed features section
    st.markdown("""
    ### Key Features
    
    #### 1. Interactive Data Visualization
    - Dynamic time series plots
    - Customizable date ranges
    - Multiple visualization options (line charts, bar graphs, heatmaps)
    - Downloadable graph data
    
    #### 2. Advanced Trend Analysis
    - Long-term climate pattern detection
    - Year-over-year comparisons
    - Moving averages and trend lines
    - Anomaly detection
    
    #### 3. Machine Learning Predictions
    - Temperature forecasting using SARIMA and Random Forest models
    - City-specific climate predictions
    - Elevation-based impact analysis
    - Model confidence metrics
    
    #### 4. Interactive Map Features
    - Real-time temperature visualization
    - Elevation data overlay
    - City-specific markers with detailed information
    - Customizable map layers
    """)
    
    # Technical details section
    st.markdown("""
    ### Technical Details
    
    #### Data Sources
    - World Bank Climate Data API
    - Historical weather records
    - Elevation data from NASA SRTM
    
    #### Models Used
    - SARIMA for time series analysis
    - Random Forest for non-linear patterns
    - Ensemble methods for improved accuracy
    
    #### Technologies
    - Python 3.8+
    - Streamlit for web interface
    - Pandas for data manipulation
    - Plotly for interactive visualizations
    - Folium for map rendering
    """)
    
    # Contact section
    st.markdown("""
    ### Contact
    For any questions or feedback, please contact the development team.
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("Version 1.0.0 | Last updated: 2025")
    


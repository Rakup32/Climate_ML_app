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
    
    ### Contact
    For any questions or feedback, please contact the development team.
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("Created with ❤️ for Nepal Climate Analysis")
    


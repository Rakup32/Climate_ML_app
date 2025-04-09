import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

def main():
    # Set page config must be the first Streamlit command
    st.set_page_config(
        page_title="Nepal Climate Analysis",
        page_icon="🌡️",
        layout="wide"
    )

    # Add the current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)

    # Import local modules after path setup
    from data_utils import load_nepal_climate_data, extract_features, prepare_features_for_model
    from visualizations import plot_prediction_history, plot_climate_timeseries, plot_yearly_trend, plot_seasonal_patterns

    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select a Page",
        ["Overview", "Data Analysis", "Trends & Patterns", "Predictions", "About"]
    )

    # Title and description
    st.title(" Nepal Climate Analysis")

    # Load data
    with st.spinner('Loading climate data...'):
        climate_data = load_nepal_climate_data()
        
        if climate_data is not None:
            # Process features
            features = extract_features(climate_data)
            X, y = prepare_features_for_model(features)
            
            if page == "Overview":
                from pages.overview import show_overview
                show_overview(climate_data)
                
            elif page == "Data Analysis":
                from pages.data_analysis import show_data_analysis
                show_data_analysis(climate_data, features)
           
            elif page == "Trends & Patterns":
                try:
                    from pages.trend_pattern import show_trend_pattern
                    show_trend_pattern(climate_data, features)
                except ImportError as e:
                    st.error(f"Error importing trend pattern module: {str(e)}")
                    st.info("Current Python path: " + str(sys.path))
                    
            elif page == "Predictions":
                from pages.prediction import show_prediction
                show_prediction(climate_data, features)
                
            elif page == "About":
                from pages.about import show_about
                show_about()

    # Footer
    st.markdown("---")
    st.markdown("Created with ❤️ for Nepal Climate Analysis")

if __name__ == "__main__":
    main()



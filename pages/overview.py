import streamlit as st
import plotly.express as px
import pandas as pd

def show_overview(climate_data):
    st.write("## Climate Data Overview")
    st.markdown("""
            Welcome to Nepal Climate Analysis.This application analyzes historical climate data for Nepal from 1990-2023, focusing on temperature and precipitation patterns.
            The data is sourced from the World Bank Climate Data API.
            """)
    
    # Key metrics display
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_temp = climate_data['temperature'].mean()
        temp_change = climate_data['temperature'].iloc[-1] - climate_data['temperature'].iloc[0]
        st.metric(
            label="Current Average Temperature",
            value=f"{avg_temp:.1f}°C",
            delta=f"{temp_change:+.1f}°C since 1990"
        )
    with col2:
        avg_precip = climate_data['precipitation'].mean()
        precip_change = climate_data['precipitation'].iloc[-1] - climate_data['precipitation'].iloc[0]
        st.metric(
            label="Annual Precipitation",
            value=f"{avg_precip:.0f}mm",
            delta=f"{precip_change:+.0f}mm since 1990"
        )
    with col3:
        data_years = len(climate_data['year'].unique())
        st.metric(
            label="Data Coverage",
            value=f"{data_years} years",
            delta=f"1990-{climate_data['year'].max()}"
        )

    # Temperature trend analysis
    st.subheader("Temperature Distribution Analysis")
    
    # Create temperature histogram with improved styling
    temp_fig = px.histogram(
        climate_data, 
        x="temperature",
        nbins=15,  # Increased bins for more granular view
        title="Temperature Distribution Over Time (1990-2023)",
        labels={
            'temperature': 'Temperature (°C)',
            'count': 'Number of Observations'
        },
        color_discrete_sequence=['#4B8BBE']  # Changed to blue
    )

    # Enhance the layout
    temp_fig.update_layout(
        bargap=0.1,  # Add space between bars
        plot_bgcolor='white',  # Clean white background
        title_x=0.5,  # Center the title
        title_font_size=20
    )

    # Add mean line with clear annotation
    temp_fig.add_vline(
        x=avg_temp,
        line_dash="dash",
        line_color="red",
        line_width=2,
        annotation_text=f"Average Temperature: {avg_temp:.1f}°C",
        annotation_position="top right"
    )

    # Display the plot
    st.plotly_chart(temp_fig, use_container_width=True)

    # Precipitation analysis
    st.subheader("Annual Precipitation Pattern")
    precip_fig = px.line(climate_data, x='year', y='precipitation',
                        title='Annual Precipitation Trend (1990-2023)',
                        labels={'year': 'Year', 'precipitation': 'Precipitation (mm)'},
                        color_discrete_sequence=['#4B8BBE'])
    precip_fig.add_hline(y=avg_precip, line_dash="dash", line_color="blue",
                        annotation_text=f"Mean: {avg_precip:.0f}mm")
    st.plotly_chart(precip_fig)

    # Climate correlation
    st.subheader("Temperature-Precipitation Relationship")
    corr = climate_data['temperature'].corr(climate_data['precipitation'])
    scatter_fig = px.scatter(climate_data, x='temperature', y='precipitation',
                           title=f'Temperature vs Precipitation (Correlation: {corr:.2f})',
                           labels={'temperature': 'Temperature (°C)', 
                                  'precipitation': 'Precipitation (mm)'},
                           trendline='ols',
                           color_discrete_sequence=['#2E8B57'])
    st.plotly_chart(scatter_fig)

    # Statistical summary
    st.subheader("Statistical Summary")
    summary_df = climate_data.describe()
    summary_df.index = ['Count', 'Mean', 'Std Dev', 'Min', '25th Percentile', 
                       'Median', '75th Percentile', 'Max']
    st.dataframe(summary_df.round(2), use_container_width=True)
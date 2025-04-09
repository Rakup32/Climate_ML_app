import streamlit as st
import plotly.express as px
import plotly.graph_objects as go   
from visualizations import plot_climate_timeseries

def show_data_analysis(climate_data, features):
   
    
    st.subheader("Climate Data Analysis")
    
    # Interactive data viewer
    st.write("### Raw Data Explorer")
    st.dataframe(climate_data)
     
    # Climate time series plot call from visualizations.py
    fig = plot_climate_timeseries(climate_data)
    st.pyplot(fig)
    

    
    # Correlation heatmap
    st.subheader("Feature Correlations")
    corr = features.corr()
    fig_corr = px.imshow(corr, 
                        title="Correlation Matrix",
                        color_continuous_scale='RdBu')
    st.plotly_chart(fig_corr)
    
    # Seasonal patterns
    st.subheader("Seasonal Patterns")
    seasonal_temp = features.groupby('month')['temperature'].mean()
    seasonal_precip = features.groupby('month')['precipitation'].mean()
    
    fig_seasonal = go.Figure()
    fig_seasonal.add_trace(go.Scatter(x=seasonal_temp.index, y=seasonal_temp,
                                    name="Temperature", yaxis="y1"))
    fig_seasonal.add_trace(go.Bar(x=seasonal_precip.index, y=seasonal_precip,
                                name="Precipitation", yaxis="y2"))
    
    fig_seasonal.update_layout(
        title="Monthly Temperature and Precipitation Patterns",
        yaxis=dict(title="Temperature (°C)"),
        yaxis2=dict(title="Precipitation (mm)", overlaying="y", side="right")
    )
    st.plotly_chart(fig_seasonal)
    
    # Temperature distribution plot
    st.subheader("Temperature Distribution Over Time")
    fig_temp = px.histogram(climate_data, x="temperature", 
                          nbins=30, 
                          title="Temperature Distribution",
                          color_discrete_sequence=['#FF9B9B'])
    st.plotly_chart(fig_temp)
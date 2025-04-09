import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_climate_timeseries(climate_data):
    """
    Creates time series plots for temperature and precipitation data
    
    Args:
        climate_data (pd.DataFrame): DataFrame containing climate data with 'year', 
                                   'temperature' and 'precipitation' columns
    """
    if climate_data is None or climate_data.empty:
        print("No data available to plot")
        return
        
    try:
        # Set up the figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle('Nepal Climate Trends Over Time', fontsize=16)

        # Temperature plot
        sns.lineplot(data=climate_data, x='year', y='temperature', ax=ax1)
        ax1.set_title('Temperature Trends')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Temperature (°C)')
        
        # Precipitation plot
        sns.lineplot(data=climate_data, x='year', y='precipitation', ax=ax2)
        ax2.set_title('Precipitation Trends') 
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Precipitation (mm)')

        plt.tight_layout()
        return fig
        
    except Exception as e:
        print(f"Error creating climate plots: {e}")
        return None

def plot_seasonal_patterns(climate_data):
    """
    Creates seasonal pattern plots showing monthly distributions of temperature and precipitation
    
    Args:
        climate_data (pd.DataFrame): DataFrame containing climate data with 'month',
                                   'temperature' and 'precipitation' columns
    """
    if climate_data is None or climate_data.empty:
        print("No data available to plot")
        return
        
    try:
        # Set up the figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle('Nepal Seasonal Climate Patterns', fontsize=16)

        # Monthly temperature patterns
        sns.boxplot(data=climate_data, x='month', y='temperature', ax=ax1)
        ax1.set_title('Monthly Temperature Distribution')
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Temperature (°C)')
        
        # Monthly precipitation patterns
        sns.boxplot(data=climate_data, x='month', y='precipitation', ax=ax2)
        ax2.set_title('Monthly Precipitation Distribution')
        ax2.set_xlabel('Month') 
        ax2.set_ylabel('Precipitation (mm)')

        plt.tight_layout()
        return fig
        
    except Exception as e:
        print(f"Error creating seasonal plots: {e}")
        return None
def plot_yearly_trend(climate_data):
    """
    Creates a plot showing the yearly trend of temperature and precipitation
    
    Args:
        climate_data (pd.DataFrame): DataFrame containing climate data with 'year',
                                   'temperature' and 'precipitation' columns
    """
    if climate_data is None or climate_data.empty:
        print("No data available to plot")
        return
        
    try:
        # Calculate yearly averages
        yearly_data = climate_data.groupby('year').agg({
            'temperature': 'mean',
            'precipitation': 'mean'
        }).reset_index()
        
        # Create figure with two y-axes
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()
        
        # Plot temperature
        sns.regplot(data=yearly_data, x='year', y='temperature', ax=ax1, 
                   scatter_kws={'alpha':0.5}, line_kws={'color': 'red'})
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Temperature (°C)', color='red')
        ax1.tick_params(axis='y', labelcolor='red')
        
        # Plot precipitation
        sns.regplot(data=yearly_data, x='year', y='precipitation', ax=ax2,
                   scatter_kws={'alpha':0.5}, line_kws={'color': 'blue'})
        ax2.set_ylabel('Precipitation (mm)', color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')
        
        plt.title('Nepal Yearly Climate Trends')
        plt.tight_layout()
        return fig
        
    except Exception as e:
        print(f"Error creating yearly trend plot: {e}")
        return None

def plot_actual_vs_predicted(y_true, y_pred):
    """
    Creates scatter plots comparing actual vs predicted values for temperature and precipitation
    
    Args:
        y_true (pd.DataFrame): DataFrame containing actual values with 'temperature' and 'precipitation' columns
        y_pred (pd.DataFrame): DataFrame containing predicted values with 'temperature' and 'precipitation' columns
    
    Returns:
        matplotlib.figure.Figure: The generated figure object, or None if error occurs
    """
    if y_true is None or y_pred is None or y_true.empty or y_pred.empty:
        print("No data available to plot")
        return None
        
    try:
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Temperature subplot
        ax1.scatter(y_true['temperature'], y_pred['temperature'], alpha=0.5)
        ax1.plot([y_true['temperature'].min(), y_true['temperature'].max()], 
                 [y_true['temperature'].min(), y_true['temperature'].max()], 
                 'r--', lw=2)
        ax1.set_xlabel('Actual Temperature (°C)')
        ax1.set_ylabel('Predicted Temperature (°C)')
        ax1.set_title('Temperature: Actual vs Predicted')
        
        # Precipitation subplot
        ax2.scatter(y_true['precipitation'], y_pred['precipitation'], alpha=0.5)
        ax2.plot([y_true['precipitation'].min(), y_true['precipitation'].max()],
                 [y_true['precipitation'].min(), y_true['precipitation'].max()],
                 'b--', lw=2)
        ax2.set_xlabel('Actual Precipitation (mm)')
        ax2.set_ylabel('Predicted Precipitation (mm)')
        ax2.set_title('Precipitation: Actual vs Predicted')
        
        plt.tight_layout()
        return fig
        
    except Exception as e:
        print(f"Error creating actual vs predicted plot: {e}")
        return None
def plot_prediction_history(history_temps, predicted_temps, history_precip, predicted_precip,
                          historical_monthly_temps=None, historical_monthly_precip=None,
                          dates=None, rolling_window=12, show_metrics=True):
    """
    Creates plots comparing historical and predicted climate data with historical monthly averages
    
    Args:
        history_temps (array-like): Historical temperature measurements
        predicted_temps (array-like): Predicted temperature values
        history_precip (array-like): Historical precipitation measurements 
        predicted_precip (array-like): Predicted precipitation values
        historical_monthly_temps (array-like, optional): Historical temperature averages by month
        historical_monthly_precip (array-like, optional): Historical precipitation averages by month
        dates (array-like, optional): Dates/timestamps for x-axis
        rolling_window (int): Window size for rolling average, default 12 months
        show_metrics (bool): Whether to display error metrics
        
    Returns:
        matplotlib.figure.Figure: The generated figure object, or None if error occurs
    """
    try:
        # Convert inputs to numpy arrays
        hist_temp = np.array(history_temps)
        pred_temp = np.array(predicted_temps)
        hist_precip = np.array(history_precip)
        pred_precip = np.array(predicted_precip)
            
        # Create x-axis values if dates not provided
        if dates is None:
            dates = np.arange(len(hist_temp))
            
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
        # Temperature plot
        ax1.plot(dates, hist_temp, 'b-', label='Historical Temperature', alpha=0.7)
        ax1.plot(dates, pred_temp, 'r-', label='Predicted Temperature', alpha=0.7)
        
        # Add historical monthly temperature averages if provided
        if historical_monthly_temps is not None:
            months = pd.DatetimeIndex(dates).month if isinstance(dates, pd.DatetimeIndex) else np.ones(len(dates))
            monthly_avg = np.array(historical_monthly_temps)[months - 1]
            ax1.plot(dates, monthly_avg, 'g--', label='Historical Monthly Average', alpha=0.5)
        
        # Add rolling averages for temperature
        if rolling_window:
            hist_rolling = pd.Series(hist_temp).rolling(window=rolling_window).mean()
            pred_rolling = pd.Series(pred_temp).rolling(window=rolling_window).mean()
            ax1.plot(dates, hist_rolling, 'b--', 
                    label=f'{rolling_window}-Period Rolling Avg (Historical)', alpha=0.5)
            ax1.plot(dates, pred_rolling, 'r--', 
                    label=f'{rolling_window}-Period Rolling Avg (Predicted)', alpha=0.5)
        
        ax1.set_xlabel('Time Period')
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title('Historical vs Predicted Temperature')
        ax1.legend()
        ax1.grid(True)
        
        # Add error metrics for temperature
        if show_metrics:
            mse = np.mean((hist_temp - pred_temp)**2)
            mae = np.mean(np.abs(hist_temp - pred_temp))
            metric_text = f'Temperature Metrics:\nMSE: {mse:.2f}\nMAE: {mae:.2f}'
            ax1.text(0.02, 0.98, metric_text, transform=ax1.transAxes,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Precipitation plot
        ax2.plot(dates, hist_precip, 'b-', label='Historical Precipitation', alpha=0.7)
        ax2.plot(dates, pred_precip, 'r-', label='Predicted Precipitation', alpha=0.7)
        
        # Add historical monthly precipitation averages if provided
        if historical_monthly_precip is not None:
            months = pd.DatetimeIndex(dates).month if isinstance(dates, pd.DatetimeIndex) else np.ones(len(dates))
            monthly_avg = np.array(historical_monthly_precip)[months - 1]
            ax2.plot(dates, monthly_avg, 'g--', label='Historical Monthly Average', alpha=0.5)
        
        # Add rolling averages for precipitation
        if rolling_window:
            hist_rolling = pd.Series(hist_precip).rolling(window=rolling_window).mean()
            pred_rolling = pd.Series(pred_precip).rolling(window=rolling_window).mean()
            ax2.plot(dates, hist_rolling, 'b--',
                    label=f'{rolling_window}-Period Rolling Avg (Historical)', alpha=0.5)
            ax2.plot(dates, pred_rolling, 'r--',
                    label=f'{rolling_window}-Period Rolling Avg (Predicted)', alpha=0.5)
        
        ax2.set_xlabel('Time Period')
        ax2.set_ylabel('Precipitation (mm)')
        ax2.set_title('Historical vs Predicted Precipitation')
        ax2.legend()
        ax2.grid(True)
        
        # Add error metrics for precipitation
        if show_metrics:
            mse = np.mean((hist_precip - pred_precip)**2)
            mae = np.mean(np.abs(hist_precip - pred_precip))
            metric_text = f'Precipitation Metrics:\nMSE: {mse:.2f}\nMAE: {mae:.2f}'
            ax2.text(0.02, 0.98, metric_text, transform=ax2.transAxes,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        return fig
        
    except Exception as e:
        print(f"Error creating prediction history plot: {e}")
        return None






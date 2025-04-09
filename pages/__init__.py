"""
This file makes the pages directory a Python package.
"""

# Import all page modules
from .trend_pattern import show_trend_pattern
from .overview import show_overview
from .data_analysis import show_data_analysis
from .prediction import show_prediction
from .about import show_about

# Define what should be imported when using 'from pages import *'
__all__ = [
    'show_trend_pattern',
    'show_overview',
    'show_data_analysis',
    'show_prediction',
    'show_about'
] 
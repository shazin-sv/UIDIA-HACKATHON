import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def fit_holt_winters(series, seasonal_periods=52):
    """
    Fits a Holt-Winters Exponential Smoothing model to the time series.
    Assumes weekly data for seasonal_periods=52 by default.
    """
    # Ensure series is numeric and handle missing values if any (though aggregation should handle it)
    series = series.astype(float)
    
    model = ExponentialSmoothing(
        series,
        trend='add',
        seasonal='add',
        seasonal_periods=seasonal_periods,
        initialization_method="estimated"
    )
    fitted_model = model.fit()
    return fitted_model

def forecast_demand(fitted_model, steps=12):
    """
    Forecasts demand for the specified number of steps.
    """
    forecast = fitted_model.forecast(steps)
    return forecast

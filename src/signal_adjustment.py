import pandas as pd
import numpy as np

def load_simulated_signals(path):
    """
    Loads simulated signals from a CSV file.
    """
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        return pd.DataFrame()

def adjust_forecast_with_signals(forecast_series, signals_df, date_col='date', factor_col='impact_factor'):
    """
    Adjusts a forecast series based on contextual signals.
    
    Args:
        forecast_series (pd.Series): The baseline forecast with DatetimeIndex.
        signals_df (pd.DataFrame): DataFrame containing signal data with dates and impact factors.
        date_col (str): Column name for dates in signals_df.
        factor_col (str): Column name for the adjustment factor in signals_df (e.g., 1.1 for 10% increase).
        
    Returns:
        pd.Series: Adjusted forecast.
    """
    if signals_df.empty:
        return forecast_series
        
    # Ensure dates are datetime
    signals_df[date_col] = pd.to_datetime(signals_df[date_col])
    
    # Create a compatible series from signals aligned with forecast index
    # We allow exact match or nearest match depending on logic. Here we assume monthly/weekly alignment.
    # For simplicity, we'll try to merge on index.
    
    adjustment_factor = pd.Series(1.0, index=forecast_series.index)
    
    # Iterate signals and apply factors to matching periods
    # This is a simplified approach. In production, we'd do a proper merge/resample.
    for _, row in signals_df.iterrows():
        signal_date = row[date_col]
        factor = row.get(factor_col, 1.0)
        
        # Find closest date in forecast index or exact match
        if signal_date in adjustment_factor.index:
            adjustment_factor.loc[signal_date] *= factor
    
    adjusted_forecast = forecast_series * adjustment_factor
    return adjusted_forecast

def get_festival_impact(date):
    """
    Returns a multiplier based on known festival dates (placeholder logic).
    """
    # Placeholder: Simple heuristic for typical high-demand months
    # e.g., Post-harvest or vacation periods might have higher demand.
    month = date.month
    if month in [5, 6]: # Summer vacation
        return 1.1
    elif month in [10, 11]: # Festival season
        return 0.9 # Maybe lower updates due to holidays? Or higher? Let's assume lower.
    return 1.0

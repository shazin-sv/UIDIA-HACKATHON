import pandas as pd
import numpy as np

def calculate_update_rates(df_risk):
    """
    Calculates update rates based on biometric/demographic updates and population.
    """
    df = df_risk.copy()
    
    # Calculate rates (Updates per 1000 enrolled children)
    if 'bio_age_5_17' in df.columns and 'age_5_17' in df.columns:
        df['mbu_rate'] = (df['bio_age_5_17'] / df['age_5_17']).replace([np.inf, -np.inf], 0).fillna(0)
    
    if 'demo_age_5_17' in df.columns and 'age_5_17' in df.columns:
        df['demo_rate'] = (df['demo_age_5_17'] / df['age_5_17']).replace([np.inf, -np.inf], 0).fillna(0)
        
    return df

def categorize_risk(df_risk):
    """
    Categorizes pincodes into High, Medium, and Low load/risk based on MBU rates.
    Uses quantile-based thresholds: Top 25% High, Bottom 25% Low.
    """
    df = df_risk.copy()
    
    if 'mbu_rate' not in df.columns:
        return df
        
    q75 = df['mbu_rate'].quantile(0.75)
    q25 = df['mbu_rate'].quantile(0.25)
    
    def get_risk_label(rate):
        if rate >= q75:
            return 'High Load'
        elif rate >= q25:
            return 'Medium Load'
        else:
            return 'Low Load'
            
    df['risk_category'] = df['mbu_rate'].apply(get_risk_label)
    
    return df

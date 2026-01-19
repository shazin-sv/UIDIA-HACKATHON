import numpy as np
import pandas as pd

def calculate_ihs(mbu_rate, demo_rate):
    """
    Calculates Identity Health Score (IHS) based on update rates.
    Logic from 03_identity_health_score.ipynb
    """
    # Base score
    base = 600
    
    # Bonus for biometric updates (MBU compliance)
    # Assuming rates are fractions, if they are per 1000 or similar, scaling might need adjustment.
    # Notebook logic: bio_bonus = np.clip(mbu_rate * 200, 0, 200)
    # If mbu_rate is like 33.8 (from notebook output example), then 33.8 * 200 is huge.
    # Wait, the notebook output showed 'mbu_rate' as ~33.8 for 1321 bio updates / 39 age_5_17 ?? 
    # 1321 / 39 is ~33.8. That means multiple updates per person or something? Or maybe 1321 is total cumulative?
    # Ah, the notebook logic: 
    # df_ihs['mbu_rate'] = (df_ihs['bio_age_5_17'] / df_ihs['age_5_17'])
    # And then: bio_bonus = np.clip(mbu_rate * 200, 0, 200)
    # If the rate is > 1 for some reason (e.g. data anomaly or cumulative over many years vs current population), it gets clipped.
    # 33.8 * 200 = 6760, clipped to 200.
    # So essentially any significant activity maxes out the bonus?
    # I will follow logic exactly as in notebook.
    
    bio_bonus = np.clip(mbu_rate * 200, 0, 200)
    
    # Bonus for demographic updates
    demo_bonus = np.clip(demo_rate * 100, 0, 100)
    
    return base + bio_bonus + demo_bonus

def assign_ihs_strategy(score):
    """
    Assigns intervention strategy based on IHS.
    """
    if score > 800:
        return 'Maintain (Digital Nudges)'
    elif score > 700:
        return 'Awareness (SMS Campaigns)'
    else:
        return 'Intervention (Mobile Vans/Camps)'

def calculate_pincode_ihs(df):
    """
    Applies IHS calculation to a dataframe.
    """
    if 'mbu_rate' not in df.columns or 'demo_rate' not in df.columns:
        return df
        
    df['ihs_score'] = df.apply(lambda x: calculate_ihs(x['mbu_rate'], x['demo_rate']), axis=1)
    df['strategy'] = df['ihs_score'].apply(assign_ihs_strategy)
    return df

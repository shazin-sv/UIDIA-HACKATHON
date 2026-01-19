import pandas as pd
import glob
import os
import numpy as np

def load_and_concat(pattern):
    """
    Loads all CSV files matching the pattern and concatenates them into a single DataFrame.
    """
    files = glob.glob(pattern)
    if not files:
        print(f"No files found for pattern: {pattern}")
        return pd.DataFrame()
        
    df_list = [pd.read_csv(f) for f in files]
    return pd.concat(df_list, ignore_index=True)

def load_data(base_path):
    """
    Loads biometric, demographic, and enrollment data from the given base path.
    """
    df_bio = load_and_concat(os.path.join(base_path, 'biometric/*.csv'))
    df_demo = load_and_concat(os.path.join(base_path, 'demographic/*.csv'))
    df_enrol = load_and_concat(os.path.join(base_path, 'enrollment/*.csv'))
    
    return df_bio, df_demo, df_enrol

def aggregate_time_series(df_bio, df_demo):
    """
    Aggregates data by date to create a master timeline dataframe.
    """
    # Convert dates
    if not df_bio.empty:
        df_bio['date'] = pd.to_datetime(df_bio['date'], dayfirst=True, errors='coerce')
    if not df_demo.empty:
        df_demo['date'] = pd.to_datetime(df_demo['date'], dayfirst=True, errors='coerce')
    
    # Aggregate biometric updates by date
    bio_agg = pd.DataFrame()
    if not df_bio.empty:
        bio_agg = df_bio.groupby('date')[['bio_age_0_4', 'bio_age_5_17', 'bio_age_18_above']].sum().reset_index()
        bio_agg['total_bio'] = bio_agg['bio_age_0_4'] + bio_agg['bio_age_5_17'] + bio_agg['bio_age_18_above']

    # Aggregate demographic updates by date
    demo_agg = pd.DataFrame()
    if not df_demo.empty:
        demo_agg = df_demo.groupby('date')[['demo_age_0_4', 'demo_age_5_17', 'demo_age_18_above']].sum().reset_index()
        demo_agg['total_demo'] = demo_agg['demo_age_0_4'] + demo_agg['demo_age_5_17'] + demo_agg['demo_age_18_above']
        
    # Merge
    if not bio_agg.empty and not demo_agg.empty:
        df_master = pd.merge(bio_agg, demo_agg, on='date', how='outer').fillna(0)
    elif not bio_agg.empty:
        df_master = bio_agg
        df_master['total_demo'] = 0
    elif not demo_agg.empty:
        df_master = demo_agg
        df_master['total_bio'] = 0
    else:
        return pd.DataFrame()

    df_master['total_updates'] = df_master.get('total_bio', 0) + df_master.get('total_demo', 0)
    df_master = df_master.sort_values('date').set_index('date')
    
    # Resample to weekly
    df_weekly = df_master.resample('W').sum()
    
    return df_weekly

def aggregate_by_pincode(df_bio, df_demo, df_enrol):
    """
    Aggregates data by pincode for risk profiling.
    """
    pincode_stats = pd.DataFrame()
    pincode_demo = pd.DataFrame()
    pincode_pop = pd.DataFrame()

    if not df_bio.empty:
        cols = [c for c in ['bio_age_5_17', 'bio_age_18_above'] if c in df_bio.columns]
        if cols:
             pincode_stats = df_bio.groupby('pincode')[cols].sum().reset_index()
    
    if not df_demo.empty:
        cols = [c for c in ['demo_age_5_17', 'demo_age_18_above'] if c in df_demo.columns]
        if cols:
            pincode_demo = df_demo.groupby('pincode')[cols].sum().reset_index()
    
    if not df_enrol.empty:
        cols = [c for c in ['age_5_17', 'age_18_above'] if c in df_enrol.columns]
        if cols:
            pincode_pop = df_enrol.groupby('pincode')[cols].sum().reset_index()
    
    # Merge all
    # Collect all unique pincodes
    pincodes = set()
    if not pincode_stats.empty: pincodes.update(pincode_stats['pincode'])
    if not pincode_demo.empty: pincodes.update(pincode_demo['pincode'])
    if not pincode_pop.empty: pincodes.update(pincode_pop['pincode'])
    
    df_risk = pd.DataFrame({'pincode': list(pincodes)})
    
    if not pincode_stats.empty:
        df_risk = pd.merge(df_risk, pincode_stats, on='pincode', how='left').fillna(0)
    
    if not pincode_demo.empty:
        df_risk = pd.merge(df_risk, pincode_demo, on='pincode', how='left').fillna(0)
        
    if not pincode_pop.empty:
        df_risk = pd.merge(df_risk, pincode_pop, on='pincode', how='left').fillna(0)
        
    return df_risk

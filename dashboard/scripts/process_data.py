import pandas as pd
import glob
import json
import numpy as np
import os

# Define Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'Datas')
OUTPUT_FILE = os.path.join(BASE_DIR, 'dashboard_metrics.json')

def load_and_concat(folder_name):
    path = os.path.join(DATA_DIR, folder_name, "*.csv")
    all_files = glob.glob(path)
    if not all_files:
        print(f"No files found in {path}")
        return pd.DataFrame()
    
    df_list = []
    for filename in all_files:
        try:
            df = pd.read_csv(filename)
            df_list.append(df)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            
    if df_list:
        return pd.concat(df_list, ignore_index=True)
    return pd.DataFrame()

def process_data():
    print("Loading data...")
    bio_df = load_and_concat('biometric')
    demo_df = load_and_concat('demographic')
    enrol_df = load_and_concat('enrollment')

    # Aggregation Config
    # We want to sum the counts but keep the first occurrence of state/district for context
    
    # Process Biometric
    if not bio_df.empty:
        bio_agg = bio_df.groupby('pincode').agg({
            'bio_age_5_17': 'sum',
            'bio_age_17_': 'sum',
            'state': 'first', 
            'district': 'first'
        }).reset_index()
        bio_agg['biometric_updates'] = bio_agg['bio_age_5_17'] + bio_agg['bio_age_17_']
    else:
        bio_agg = pd.DataFrame(columns=['pincode', 'biometric_updates', 'state', 'district'])

    # Process Demographic
    if not demo_df.empty:
        demo_agg = demo_df.groupby('pincode').agg({
            'demo_age_5_17': 'sum',
            'demo_age_17_': 'sum'
        }).reset_index()
        demo_agg['demographic_updates'] = demo_agg['demo_age_5_17'] + demo_agg['demo_age_17_']
    else:
        demo_agg = pd.DataFrame(columns=['pincode', 'demographic_updates'])

    # Process Enrollment
    if not enrol_df.empty:
        enrol_agg = enrol_df.groupby('pincode').agg({
            'age_0_5': 'sum', 
            'age_5_17': 'sum', 
            'age_18_greater': 'sum'
        }).reset_index()
        enrol_agg['total_enrollment'] = enrol_agg['age_0_5'] + enrol_agg['age_5_17'] + enrol_agg['age_18_greater']
    else:
        enrol_agg = pd.DataFrame(columns=['pincode', 'total_enrollment'])

    # Merge DataFrames
    print("Merging data...")
    merged_df = pd.merge(bio_agg, demo_agg[['pincode', 'demographic_updates']], on='pincode', how='outer')
    merged_df = pd.merge(merged_df, enrol_agg[['pincode', 'total_enrollment']], on='pincode', how='outer')

    # Fill NaNs
    merged_df['biometric_updates'] = merged_df['biometric_updates'].fillna(0)
    merged_df['demographic_updates'] = merged_df['demographic_updates'].fillna(0)
    merged_df['total_enrollment'] = merged_df['total_enrollment'].fillna(100) # Default small denom to avoid inf
    merged_df['state'] = merged_df['state'].fillna('Unknown')
    merged_df['district'] = merged_df['district'].fillna('Unknown')
    
    # Avoid zero division
    merged_df.loc[merged_df['total_enrollment'] == 0, 'total_enrollment'] = 1

    # Calculate Metrics
    print("Calculating metrics...")
    
    # Pincode Risk
    merged_df['total_update_load'] = merged_df['biometric_updates'] + merged_df['demographic_updates']
    threshold_95 = merged_df['total_update_load'].quantile(0.95)
    merged_df['risk_category'] = np.where(merged_df['total_update_load'] >= threshold_95, 'High Risk', 'Normal')

    # Identity Health Score (IHS)
    # Logic: Base 600 + (MBU Rate * 200) + (Demo Rate * 100)
    # MBU Rate = Biometric Updates / Enrollment
    # Demo Rate = Demo Updates / Enrollment
    
    merged_df['mbu_rate'] = merged_df['biometric_updates'] / merged_df['total_enrollment']
    merged_df['demo_rate'] = merged_df['demographic_updates'] / merged_df['total_enrollment']
    
    # Scale rates for realistic score impact.
    # If raw rates are small (e.g. 0.05), we multiply by a factor to make them visible scores?
    # Notebook code: bio_bonus = np.clip(mbu_rate * 200, 0, 200). 
    # If mbu_rate is > 1.0 (more updates than enrollment? possible if cumulative updates), it clips.
    
    base_score = 600
    merged_df['ihs_score'] = base_score + \
                             np.clip(merged_df['mbu_rate'] * 150, 0, 200) + \
                             np.clip(merged_df['demo_rate'] * 100, 0, 100)
    
    merged_df['ihs_score'] = merged_df['ihs_score'].round().astype(int)

    # Strategy
    def get_strategy(score):
        if score >= 800: return 'Healthy: Routine Digital Nudges'
        elif score >= 700: return 'Warning: Targeted SMS Campaigns'
        else: return 'Critical: Mobile Van & Camp Deployment'

    merged_df['strategy'] = merged_df['ihs_score'].apply(get_strategy)

    # Export Dashboard Metrics
    output_df = merged_df[[
        'pincode', 'state', 'district', 
        'biometric_updates', 'demographic_updates', 'total_update_load',
        'ihs_score', 'risk_category', 'strategy'
    ]]
    
    json_str = output_df.to_json(orient='records')
    with open(OUTPUT_FILE, 'w') as f:
        f.write(json_str)
        
    print(f"Successfully exported metrics for {len(output_df)} pincodes to {OUTPUT_FILE}")

    # --- Process Monthly Demand for Forecasting ---
    print("Processing monthly demand...")
    if not bio_df.empty:
        # Ensure date format handling
        bio_df['date'] = pd.to_datetime(bio_df['date'], dayfirst=True, errors='coerce')
        bio_df = bio_df.dropna(subset=['date'])
        
        # Create Month column
        bio_df['month'] = bio_df['date'].dt.to_period('M').astype(str)
        
        # Aggregate bio_age_5_17 (MBU target) by Month and Pincode
        # We also need District/State for filtering in the app
        demand_agg = bio_df.groupby(['month', 'pincode', 'state', 'district'])['bio_age_5_17'].sum().reset_index()
        demand_agg.rename(columns={'bio_age_5_17': 'mbu_demand'}, inplace=True)
        
        # Export Monthly Demand
        demand_output_file = os.path.join(BASE_DIR, 'monthly_demand.json')
        demand_json = demand_agg.to_json(orient='records')
        with open(demand_output_file, 'w') as f:
            f.write(demand_json)
        print(f"Successfully exported monthly demand data to {demand_output_file}")
    else:
        print("No biometric data available for demand forecasting.")

if __name__ == "__main__":
    process_data()

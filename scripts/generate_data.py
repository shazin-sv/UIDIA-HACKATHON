import os
import sys
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import data_processing, risk_profiling, ihs_scoring

def generate_processed_data():
    base_path = 'data/raw'
    processed_path = 'data/processed'
    
    print("Loading raw data...")
    df_bio, df_demo, df_enrol = data_processing.load_data(base_path)
    
    if df_bio.empty and df_demo.empty and df_enrol.empty:
        print("No raw data found. Generating synthetic data for demonstration.")
        # Generate synthetic data if raw files are missing/empty
        pincodes = [110001, 110002, 110003, 110004, 110005, 560001, 560002, 400001]
        dates = pd.date_range(start='2024-01-01', periods=12, freq='M')
        
        # Synthetic IHS/Risk Data
        df_risk = pd.DataFrame({
            'pincode': pincodes,
            'bio_age_5_17': np.random.randint(100, 5000, size=len(pincodes)),
            'demo_age_5_17': np.random.randint(50, 1000, size=len(pincodes)),
            'age_5_17': np.random.randint(500, 10000, size=len(pincodes))
        })
        
        # Synthetic Time Series
        df_monthly = pd.DataFrame()
        for pc in pincodes:
            temp = pd.DataFrame({'date': dates, 'pincode': pc})
            temp['total_updates'] = np.random.randint(50, 200, size=len(dates))
            temp['mbu_demand'] = np.random.randint(20, 100, size=len(dates))
            df_monthly = pd.concat([df_monthly, temp])
            
    else:
        print("Aggregating data...")
        # 1. Pincode Level Aggregation (Risk & IHS)
        df_risk = data_processing.aggregate_by_pincode(df_bio, df_demo, df_enrol)
        
        # 2. Time Series Aggregation (Forecasting)
        # Note: data_processing.aggregate_time_series aggregates by date globally
        # For forecasting model we might need per-pincode time series if desired.
        # But let's use global weekly for now or adjust based on requirement.
        # The notebook 01 aggregated by month and pincode.
        # Let's verify data_processing.
        pass
        
    print("Calculating metrics...")
    # Calculate Rates & Risk
    df_risk = risk_profiling.calculate_update_rates(df_risk)
    df_risk = risk_profiling.categorize_risk(df_risk)
    
    # Calculate IHS
    df_risk = ihs_scoring.calculate_pincode_ihs(df_risk)
    
    # Add geographic columns (state/district) from pincode
    df_risk = data_processing.add_geography_from_pincode(df_risk)
    
    # Save Processed
    print(f"Saving to {processed_path}...")
    df_risk.to_csv(os.path.join(processed_path, 'ihs_features_population.csv'), index=False)
    
    # For time series, if synthetic was created, save it. 
    # If raw existed, we should aggregate it properly for the dashboard.
    # We will generate a pincode-monthly time-series from raw if available.
    if not df_bio.empty:
        df_bio['month'] = pd.to_datetime(df_bio['date'], dayfirst=True, errors='coerce').dt.to_period('M').astype(str)
        if 'bio_age_5_17' in df_bio.columns:
            df_monthly = df_bio.groupby(['month', 'pincode'])['bio_age_5_17'].sum().reset_index()
            df_monthly.rename(columns={'bio_age_5_17': 'mbu_demand'}, inplace=True)
            df_monthly.to_csv(os.path.join(processed_path, 'biometric_mbu_aggregated.csv'), index=False)
    elif 'df_monthly' in locals():
         df_monthly.to_csv(os.path.join(processed_path, 'biometric_mbu_aggregated.csv'), index=False)
         
    print("Processed data generated.")

def generate_simulated_signals():
    path = 'data/simulated_signals'
    print(f"Generating signals in {path}...")
    
    # 1. School Enrolment Cycles
    months = [f'2024-{i:02d}-01' for i in range(1, 13)]
    school_cycles = pd.DataFrame({
        'date': months,
        'factor': [1.0, 1.0, 1.2, 1.5, 1.5, 1.2, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], # Surge in April/May/June
        'event': ['Regular', 'Regular', 'School Admissions', 'School Admissions', 'School Admissions', 'School Admissions', 'Regular', 'Regular', 'Regular', 'Regular', 'Regular', 'Regular']
    })
    school_cycles.to_csv(os.path.join(path, 'school_enrolment_cycles.csv'), index=False)
    
    # 2. Birth Trends District (Placeholder)
    districts = ['Bangalore', 'Mumbai', 'Delhi', 'Chennai']
    birth_trends = pd.DataFrame({
        'district': districts,
        'birth_rate_trend': ['Stable', 'Decreasing', 'Stable', 'Increasing'],
        'new_registrations_forecast': [5000, 12000, 10000, 6000]
    })
    birth_trends.to_csv(os.path.join(path, 'birth_trends_district.csv'), index=False)
    
    # 3. Policy Event Flags
    policy_events = pd.DataFrame({
        'date': ['2024-06-01', '2024-10-02'],
        'event': ['MBU Drive Phase 1', 'Special Camps'],
        'impact_factor': [1.3, 1.4]
    })
    policy_events.to_csv(os.path.join(path, 'policy_event_flags.csv'), index=False)
    
    print("Simulated signals generated.")

if __name__ == "__main__":
    generate_processed_data()
    generate_simulated_signals()

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Import Components
from dashboard.components.guidance_view import show_guidance
from dashboard.components.kpi_metrics import render_kpi_metrics
from dashboard.components.pincode_heatmap_view import render_pincode_heatmap
from dashboard.components.ihs_distribution_view import render_ihs_distribution
from dashboard.components.strategy_panel import render_strategy_panel
from dashboard.components.demand_forecast_view import render_demand_forecast
from dashboard.components.context_signal_panel import render_context_signals

# Page Config (Must be first)
st.set_page_config(page_title="Project Setu Dashboard", page_icon="assets/favicon.png", layout="wide")

# --- Data Loading ---
@st.cache_data
def load_data():
    file_path = 'data/processed/ihs_features_population.csv'
    # Fallback to json if csv not found (legacy support or if user kept json)
    if not os.path.exists(file_path):
        file_path = 'dashboard_metrics.json' # Legacy
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    else:
        df = pd.read_csv(file_path)
    
    if 'pincode' in df.columns:
        df['pincode'] = df['pincode'].astype(str)
    
    # Ensure columns exist (for legacy/synthetic data compat)
    if 'total_update_load' not in df.columns and 'mbu_rate' in df.columns:
        # Approximate load if missing
        df['total_update_load'] = df['bio_age_5_17'] + df['demo_age_5_17']
        
    return df

@st.cache_data
def load_demand_data():
    file_path = 'data/processed/biometric_mbu_aggregated.csv'
    if not os.path.exists(file_path):
        file_path = 'monthly_demand.json' # Legacy
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    else:
        df = pd.read_csv(file_path)

    if 'pincode' in df.columns:
        df['pincode'] = df['pincode'].astype(str)
    if 'month' in df.columns:
        # Convert month string (YYYY-MM) to proper date for plotting if needed
        # Or if it's already datetime string
        try:
            df['month'] = pd.to_datetime(df['month'])
        except:
            pass
            
    # Add dummy state/district if missing (synthetic data might not have them)
    if 'state' not in df.columns:
        df['state'] = 'State A' # Placeholder
    if 'district' not in df.columns:
        df['district'] = 'District X' # Placeholder
        
    return df

def show_dashboard():
    df = load_data()
    df_demand = load_demand_data()

    if df is None:
        st.error("Data file not found. Please run 'scripts/generate_data.py' first.")
        return

    # --- Filters ---
    st.sidebar.header("Filters")
    
    # State Filter
    if 'state' in df.columns:
        all_states = ['All'] + sorted(df['state'].unique().tolist())
    else:
        all_states = ['All']
    
    selected_state = st.sidebar.selectbox("Select State", all_states)
    
    # District Filter
    if 'district' in df.columns:
        if selected_state != 'All':
            filtered_df_state = df[df['state'] == selected_state]
            all_districts = ['All'] + sorted(filtered_df_state['district'].unique().tolist())
        else:
            all_districts = ['All'] + sorted(df['district'].unique().tolist())
    else:
        all_districts = ['All']
        
    selected_district = st.sidebar.selectbox("Select District", all_districts)
    
    # Risk Category Filter
    if 'risk_category' in df.columns:
        all_risks = ['All'] + sorted(df['risk_category'].unique().tolist())
        selected_risk = st.sidebar.selectbox("Risk Category", all_risks)
    else:
        selected_risk = 'All'
    
    # Apply Filters
    filtered_df = df.copy()
    if selected_state != 'All' and 'state' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['state'] == selected_state]
    if selected_district != 'All' and 'district' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['district'] == selected_district]
    if selected_risk != 'All' and 'risk_category' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['risk_category'] == selected_risk]
    
    # --- Main Dashboard Content ---
    st.title("Project Setu: Aadhaar Data Dashboard")

    # Sub-navigation
    view_selection = st.radio(
        "Select Dashboard View:", 
        ["Risk Profiling & Analytics", "Strategies & Details", "MBU Demand Forecasting"], 
        horizontal=True
    )
    
    st.markdown("---")

    if view_selection == "Risk Profiling & Analytics":
        st.markdown("### Pincode Risk Profiling & Identity Health Score (IHS) Analytics")
        render_kpi_metrics(filtered_df)
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            render_pincode_heatmap(filtered_df, selected_district)
        with c2:
            render_ihs_distribution(filtered_df)

    elif view_selection == "Strategies & Details":
        render_strategy_panel(filtered_df)

    elif view_selection == "MBU Demand Forecasting":
        render_demand_forecast(df_demand, selected_state, selected_district)
        render_context_signals()

# --- Main App Entry Point ---
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Guidance"])
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Guidance":
        show_guidance()

if __name__ == "__main__":
    main()

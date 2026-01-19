import streamlit as st

def render_kpi_metrics(filtered_df):
    col1, col2, col3, col4 = st.columns(4)
    total_pincodes = len(filtered_df)
    avg_ihs = filtered_df['ihs_score'].mean() if not filtered_df.empty else 0
    high_risk_count = len(filtered_df[filtered_df['risk_category'] == 'High Risk']) if 'risk_category' in filtered_df.columns else 0
    # In case risk_category values are different (e.g., 'High Load')
    if high_risk_count == 0 and 'risk_category' in filtered_df.columns:
        high_risk_count = len(filtered_df[filtered_df['risk_category'] == 'High Load'])

    total_load = filtered_df['total_update_load'].sum() if 'total_update_load' in filtered_df.columns else 0
    
    col1.metric("Total Pincodes", f"{total_pincodes:,}")
    col2.metric("Total Update Load", f"{total_load:,}")
    col3.metric("High Risk Pincodes", f"{high_risk_count:,}", delta_color="inverse")
    col4.metric("Average IHS Score", f"{avg_ihs:.0f}", delta=f"{avg_ihs - 600:.0f} vs Base", delta_color="normal")

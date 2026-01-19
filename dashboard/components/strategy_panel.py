import streamlit as st
import plotly.express as px

def render_strategy_panel(filtered_df):
    c3, c4 = st.columns([1, 2])
    with c3:
        st.subheader("Recommended Strategies")
        if not filtered_df.empty:
            strategy_counts = filtered_df['strategy'].value_counts().reset_index()
            strategy_counts.columns = ['strategy', 'count']
            fig_pie = px.pie(strategy_counts, names='strategy', values='count', hole=0.4, 
                             color='strategy',
                             color_discrete_map={
                                 'Healthy: Routine Digital Nudges': '#99ff99', 
                                 'Warning: Targeted SMS Campaigns': '#ffcc99', 
                                 'Critical: Mobile Van & Camp Deployment': '#ff9999'
                             })
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.write("No data available.")
            
    with c4:
        st.subheader("Pincode Details")
        cols = ['pincode', 'district', 'state', 'total_update_load', 'ihs_score', 'risk_category', 'strategy']
        # Filter for existing columns
        cols = [c for c in cols if c in filtered_df.columns]
        st.dataframe(filtered_df[cols], 
                     use_container_width=True, hide_index=True)

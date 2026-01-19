import streamlit as st
import plotly.express as px

def render_ihs_distribution(filtered_df):
    st.subheader("Identity Health Score (IHS) Distribution")
    if not filtered_df.empty:
        color_map = {
            'Healthy: Routine Digital Nudges': '#99ff99', 
            'Warning: Targeted SMS Campaigns': '#ffcc99', 
            'Critical: Mobile Van & Camp Deployment': '#ff9999'
        }
        fig_hist = px.histogram(filtered_df, x="ihs_score", nbins=30, title="Distribution of IHS Scores", 
                                color='strategy', color_discrete_map=color_map)
        fig_hist.add_vline(x=filtered_df['ihs_score'].mean(), line_dash="dash", line_color="green", annotation_text="Avg")
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.write("No data available.")

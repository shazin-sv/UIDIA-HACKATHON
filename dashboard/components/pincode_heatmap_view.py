import streamlit as st
import plotly.express as px

def render_pincode_heatmap(filtered_df, selected_district):
    st.subheader("Top Locations by Update Load")
    if filtered_df.empty:
        st.write("No data available.")
        return

    if selected_district == 'All':
        dist_group = filtered_df.groupby('district')['total_update_load'].sum().reset_index()
        dist_group = dist_group.sort_values(by='total_update_load', ascending=False).head(10)
        fig_bar = px.bar(dist_group, x='total_update_load', y='district', orientation='h', 
                         title="Top 10 Districts (Update Volume)", color='total_update_load', color_continuous_scale='Viridis')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        # Pincodes might be int or str, ensure they are treated categorically
        pin_group = filtered_df.sort_values(by='total_update_load', ascending=False).head(10)
        fig_bar = px.bar(pin_group, x='total_update_load', y='pincode', orientation='h',
                         title=f"Top 10 Pincodes in {selected_district}", color='total_update_load', color_continuous_scale='Viridis')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending', 'type': 'category'})
        st.plotly_chart(fig_bar, use_container_width=True)

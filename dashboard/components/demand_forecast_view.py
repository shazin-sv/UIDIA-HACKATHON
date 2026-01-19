import streamlit as st
import pandas as pd
import plotly.express as px
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def render_demand_forecast(df_demand, selected_state, selected_district):
    st.subheader("MBU Demand Forecasting (Holt-Winters)")
    
    if df_demand is None or df_demand.empty:
        st.warning("Forecasting data not found. Please ensure 'monthly_demand.json' exists.")
        return

    fc1, fc2 = st.columns([1, 3])
    with fc1:
        forecast_level = st.radio("Forecast Level", ["District", "Pincode"])
        target_entity = None
        if forecast_level == "District":
            if selected_state == 'All':
                dist_opts = df_demand['district'].unique().tolist()
            else:
                dist_opts = df_demand[df_demand['state'] == selected_state]['district'].unique().tolist()
            target_entity = st.selectbox("Select District", sorted(dist_opts))
        else:
            if selected_district != 'All':
                pin_opts = df_demand[df_demand['district'] == selected_district]['pincode'].unique().tolist()
            elif selected_state != 'All':
                pin_opts = df_demand[df_demand['state'] == selected_state]['pincode'].unique().tolist()
            else:
                pin_opts = df_demand['pincode'].unique().tolist()
                
            target_entity = st.selectbox("Select Pincode", sorted(pin_opts))
        
        forecast_months = st.slider("Forecast Horizon (Months)", 1, 12, 6)
        
    with fc2:
        if target_entity:
            try:
                if forecast_level == "District":
                    ts_data = df_demand[df_demand['district'] == target_entity].groupby('month')['mbu_demand'].sum().reset_index()
                else:
                    ts_data = df_demand[df_demand['pincode'] == target_entity].groupby('month')['mbu_demand'].sum().reset_index()
                
                ts_data = ts_data.sort_values('month')
                ts_data.set_index('month', inplace=True)
                
                if len(ts_data) < 4:
                    st.warning(f"Not enough data points to forecast for {target_entity} (at least 4 months required).")
                else:
                    # Explicitly convert to float to avoid dtype issues
                    series = ts_data['mbu_demand'].astype(float)
                    model = ExponentialSmoothing(series, trend='add', seasonal=None).fit()
                    forecast_values = model.forecast(forecast_months)
                    
                    last_date = ts_data.index[-1]
                    forecast_dates = [last_date + pd.DateOffset(months=i) for i in range(1, forecast_months + 1)]
                    forecast_df = pd.DataFrame({'month': forecast_dates, 'mbu_demand': forecast_values.values, 'Type': 'Forecast'})
                    
                    history_df = ts_data.reset_index()
                    history_df['Type'] = 'Historical'
                    
                    combined_df = pd.concat([history_df, forecast_df], ignore_index=True)
                    
                    fig_forecast = px.line(combined_df, x='month', y='mbu_demand', color='Type', 
                                           title=f"MBU Demand Forecast for {target_entity}",
                                           markers=True,
                                           color_discrete_map={'Historical': 'grey', 'Forecast': '#2ca02c'})
                    st.plotly_chart(fig_forecast, use_container_width=True)
                    
                    with st.expander("View Forecast Data"):
                        st.dataframe(forecast_df)
            except Exception as e:
                st.error(f"Forecasting Error: {e}")

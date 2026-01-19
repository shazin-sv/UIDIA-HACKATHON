import streamlit as st

def render_context_signals():
    st.markdown("---")
    st.markdown("""
    ### 🔮 Forecast Context (Simulated Public Signals)
    The forecasts shown here are adjusted using aggregated, non-personal public signals, displayed only for contextual awareness.
    
    **These include:**
    - 👶 **Birth Registration Trends** (district-level growth indicators)
    - 🎒 **School Admission Cycles** (seasonal update drivers at ages 5 & 15)
    - 📰 **Policy & Event Signals** (simulated announcements where Aadhaar usage increases)
    
    > **⚠️ Important Note:**
    > All signals are simulated and aggregated for demonstration purposes.
    > No live feeds, personal data, or cross-department linkages are used.
    """)

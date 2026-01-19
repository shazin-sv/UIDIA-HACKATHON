import streamlit as st

def show_guidance():
    st.title("📊 Project Setu — Dashboard Guidance")
    
    st.markdown("""
    ### Purpose of this Dashboard
    This dashboard helps **UIDAI planners and field coordinators** anticipate Aadhaar enrolment and update demand before congestion occurs. It combines historical Aadhaar trends with simulated public context signals to support proactive, data-driven decisions.

    ### 🗺️ How to Use the Dashboard
    1. **Select a State and District** using the filters on the left (available on the Dashboard page).
    2. **Review the 6-Month Demand Forecast** showing expected Aadhaar enrolments and mandatory biometric updates.
    3. **Observe pincode-level risk indicators** highlighting potential surge zones.
    4. **Use insights to plan:**
        - Manpower allocation
        - Mobile Aadhaar Van deployment
        - Temporary enrollment camps


    ### 🔐 Privacy & Governance Assurance
    - **No individual tracking**
    - **No real-time data ingestion**
    - **No automatic Aadhaar updates**
    - **No inter-departmental data storage**
    
    This dashboard supports planning and forecasting only, in line with **privacy-by-design principles**.

    ### 🎯 Intended Outcome
    By using this dashboard, officials can:
    - Reduce overcrowding at Aadhaar Seva Kendras
    - Improve Mandatory Biometric Update (MBU) compliance
    - Allocate resources proactively instead of reactively
    - Enhance citizen experience through better preparedness
    """)

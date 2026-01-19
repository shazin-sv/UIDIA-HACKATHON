---
title: Project Setu
emoji: 🌉
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.41.1
app_file: streamlit_app.py
pinned: false
---

# 🌉 Project Setu: Bridge to Enrollment Excellence

## 🚀 Overview
**Project Setu** is a predictive analytics dashboard designed for UIDAI field operations. It serves as a bridge ("Setu") between reactive congestion and proactive preparedness.

This application combines:
- **Historical Aadhaar Trends**: Deep analysis of past enrollment and update cycles.
- **Simulated Context Signals**: Integration of school admission cycles, birth registration trends, and policy events.
- **Predictive Intelligence**: Forecasting mandatory biometric update (MBU) demand 6 months in advance.

## 🎯 Key Capabilities
1.  **Demand Forecasting**: Uses Holt-Winters Exponential Smoothing to predict future footfall.
2.  **Risk Profiling**: Identifies high-load pincodes before they become bottlenecks.
3.  **Identity Health Score (IHS)**: A novel metric simulating the "freshness" of resident data to encourage proactive updates.

## 🛠️ Technology Stack
-   **Frontend**: Streamlit
-   **Analytics**: Pandas, NumPy
-   **Forecasting**: Statsmodels
-   **Visualization**: Plotly

## 📂 Project Structure
-   `src/`: Core logic modules (forecasting, scoring, data processing).
-   `dashboard/`: Streamlit view components.
-   `data/`: Synthetic datasets for demonstration.
-   `scripts/`: Utilities for data generation.

## ⚖️ Deployment to Hugging Face
This repository is configured for deployment on Hugging Face Spaces.
1.  Ensure `requirements.txt` is present.
2.  Ensure `app.py` is at the root (serving as the entry point).
3.  Push to your Space's remote repository.

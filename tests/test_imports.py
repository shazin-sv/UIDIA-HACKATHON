import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    print("Testing imports...")
    try:
        import src.data_processing
        print("[OK] src.data_processing imported")
        import src.forecasting
        print("[OK] src.forecasting imported")
        import src.risk_profiling
        print("[OK] src.risk_profiling imported")
        import src.ihs_scoring
        print("[OK] src.ihs_scoring imported")
        import src.signal_adjustment
        print("[OK] src.signal_adjustment imported")
        
        import dashboard.components.pincode_heatmap_view
        print("[OK] dashboard.components.pincode_heatmap_view imported")
        import dashboard.components.ihs_distribution_view
        print("[OK] dashboard.components.ihs_distribution_view imported")
        import dashboard.components.demand_forecast_view
        print("[OK] dashboard.components.demand_forecast_view imported")
        import dashboard.components.context_signal_panel
        print("[OK] dashboard.components.context_signal_panel imported")
        import dashboard.components.kpi_metrics
        print("[OK] dashboard.components.kpi_metrics imported")
        import dashboard.components.strategy_panel
        print("[OK] dashboard.components.strategy_panel imported")
        import dashboard.components.guidance_view
        print("[OK] dashboard.components.guidance_view imported")
        
        print("\nAll imports successful!")
    except Exception as e:
        print(f"\n[FAIL] Import failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_imports()

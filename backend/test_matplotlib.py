#!/usr/bin/env python3
"""
Test script to verify matplotlib installation and functionality.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_matplotlib_installation():
    """Test if matplotlib is properly installed."""
    try:
        import matplotlib
        print(f"✓ Matplotlib version: {matplotlib.__version__}")
        
        import matplotlib.pyplot as plt
        print("✓ Matplotlib.pyplot imported successfully")
        
        # Test basic plotting functionality
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        ax.plot(x, y, 'o-', linewidth=2, markersize=6)
        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_title('Test Plot')
        ax.grid(True, alpha=0.3)
        
        # Save the test plot
        test_plot_path = "test_plot.png"
        plt.savefig(test_plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        if os.path.exists(test_plot_path):
            print(f"✓ Test plot saved successfully to {test_plot_path}")
            # Clean up
            os.remove(test_plot_path)
        else:
            print("✗ Failed to save test plot")
            
        return True
        
    except ImportError as e:
        print(f"✗ Matplotlib import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Matplotlib test failed: {e}")
        return False

def test_plotting_utilities():
    """Test if the plotting utilities can be imported."""
    try:
        from simulation.plotting.plotting_utils import (
            plot_time_series,
            plot_process_comparison,
            plot_machine_data,
            create_summary_plots,
            create_process_flow_diagram,
            plot_quality_metrics
        )
        print("✓ Plotting utilities imported successfully")
        return True
        
    except ImportError as e:
        print(f"✗ Plotting utilities import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Plotting utilities test failed: {e}")
        return False

def test_basic_plotting():
    """Test basic plotting functionality with sample data."""
    try:
        from simulation.plotting.plotting_utils import plot_time_series
        
        # Create sample data
        sample_data = [
            {"Duration": 0, "Density": 1.0, "Viscosity": 100, "Temperature": 25},
            {"Duration": 1, "Density": 1.1, "Viscosity": 110, "Temperature": 26},
            {"Duration": 2, "Density": 1.2, "Viscosity": 120, "Temperature": 27},
            {"Duration": 3, "Density": 1.3, "Viscosity": 130, "Temperature": 28},
            {"Duration": 4, "Density": 1.4, "Viscosity": 140, "Temperature": 29}
        ]
        
        # Create a test plot
        fig = plot_time_series(
            data=sample_data,
            title="Test Plot - Sample Data",
            save_path="test_sample_plot.png"
        )
        
        if os.path.exists("test_sample_plot.png"):
            print("✓ Sample plot created successfully")
            # Clean up
            os.remove("test_sample_plot.png")
        else:
            print("✗ Failed to create sample plot")
            
        return True
        
    except Exception as e:
        print(f"✗ Basic plotting test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Matplotlib Integration")
    print("=" * 40)
    
    tests = [
        ("Matplotlib Installation", test_matplotlib_installation),
        ("Plotting Utilities", test_plotting_utilities),
        ("Basic Plotting", test_basic_plotting)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 40)
    print("Test Results:")
    print("=" * 40)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Matplotlib is ready to use.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
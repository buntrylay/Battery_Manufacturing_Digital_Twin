#!/usr/bin/env python3
"""
Demonstration script for plotting utilities with real simulation data.

This script shows how to use the plotting functions with actual battery
manufacturing simulation data.
"""

import sys
import os
import json
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def load_simulation_data(output_dir: str) -> list:
    """
    Load simulation data from JSON files in the output directory.
    
    Args:
        output_dir: Directory containing JSON output files
        
    Returns:
        List of dictionaries containing simulation data
    """
    data = []
    
    if not os.path.exists(output_dir):
        print(f"Warning: Output directory {output_dir} does not exist")
        return data
    
    # Find all JSON files
    json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
    
    for json_file in sorted(json_files):
        try:
            with open(os.path.join(output_dir, json_file), 'r') as f:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    data.extend(file_data)
                else:
                    data.append(file_data)
        except Exception as e:
            print(f"Warning: Could not load {json_file}: {e}")
    
    return data

def demo_mixing_plots():
    """Demonstrate mixing process plots with real data."""
    print("🔬 Creating mixing process plots with real data...")
    
    # Load mixing data
    mixing_data = load_simulation_data("mixing_output")
    
    if mixing_data:
        print(f"📊 Loaded {len(mixing_data)} data points from mixing process")
        
        # Create time series plot
        from simulation.plotting.plotting_utils import plot_time_series
        
        fig = plot_time_series(
            data=mixing_data,
            y_keys=['Density', 'Viscosity', 'YieldStress'],
            title="Mixing Process Parameters - Real Data",
            save_path="plots/mixing_real_data_plot.png"
        )
        
        print("✅ Mixing process plot created successfully!")
        print("📁 Saved to: plots/mixing_real_data_plot.png")
        
        return fig
    else:
        print("❌ No mixing data found. Run a simulation first.")
        return None

def demo_process_comparison():
    """Demonstrate process comparison with real data."""
    print("\n🔬 Creating process comparison plots...")
    
    # Load mixing data
    mixing_data = load_simulation_data("mixing_output")
    
    if mixing_data:
        # Filter for anode and cathode data
        anode_data = [d for d in mixing_data if d.get("Electrode Type") == "Anode"]
        cathode_data = [d for d in mixing_data if d.get("Electrode Type") == "Cathode"]
        
        if anode_data and cathode_data:
            from simulation.plotting.plotting_utils import plot_process_comparison
            
            fig = plot_process_comparison(
                anode_data=anode_data,
                cathode_data=cathode_data,
                process_name="Mixing Process",
                save_path="plots/mixing_comparison_plot.png"
            )
            
            print("✅ Process comparison plot created successfully!")
            print("📁 Saved to: plots/mixing_comparison_plot.png")
            
            return fig
        else:
            print("❌ No anode/cathode data found for comparison.")
    else:
        print("❌ No mixing data found.")
    
    return None

def demo_machine_specific_plot():
    """Demonstrate machine-specific plotting."""
    print("\n🔬 Creating machine-specific plots...")
    
    # Try to find a machine ID from the data
    mixing_data = load_simulation_data("mixing_output")
    
    if mixing_data:
        # Get the first machine ID
        machine_id = mixing_data[0].get("Machine ID", "TK_Mix_Anode")
        
        from simulation.plotting.plotting_utils import plot_machine_data
        
        try:
            fig = plot_machine_data(
                machine_id=machine_id,
                output_dir="mixing_output",
                save_path=f"plots/{machine_id}_plot.png"
            )
            
            print(f"✅ Machine plot created successfully for {machine_id}!")
            print(f"📁 Saved to: plots/{machine_id}_plot.png")
            
            return fig
        except Exception as e:
            print(f"❌ Failed to create machine plot: {e}")
    else:
        print("❌ No data found for machine plotting.")
    
    return None

def demo_process_flow_diagram():
    """Demonstrate process flow diagram creation."""
    print("\n🔬 Creating process flow diagram...")
    
    from simulation.plotting.plotting_utils import create_process_flow_diagram
    
    processes = [
        "Mixing",
        "Coating", 
        "Drying",
        "Calendaring",
        "Slitting",
        "Inspection",
        "Rewinding",
        "Electrolyte Filling",
        "Formation Cycling",
        "Aging"
    ]
    
    fig = create_process_flow_diagram(
        processes=processes,
        save_path="plots/process_flow_diagram.png"
    )
    
    print("✅ Process flow diagram created successfully!")
    print("📁 Saved to: plots/process_flow_diagram.png")
    
    return fig

def demo_summary_plots():
    """Demonstrate summary plots for all processes."""
    print("\n🔬 Creating summary plots for all processes...")
    
    # Define output directories
    output_dirs = {
        "Mixing": "mixing_output",
        "Coating": "coating_output", 
        "Drying": "drying_output",
        "Calendaring": "calendaring_output",
        "Slitting": "slitting_output",
        "Inspection": "inspection_output",
        "Rewinding": "rewinding_output",
        "Electrolyte_Filling": "electrolyte_filling_output"
    }
    
    from simulation.plotting.plotting_utils import create_summary_plots
    
    # Create summary plots
    figures = create_summary_plots(
        output_dirs=output_dirs,
        save_dir="plots"
    )
    
    print(f"✅ Created {len(figures)} summary plots!")
    print("📁 Saved to: plots/ directory")
    
    return figures

def main():
    """Run all demonstrations."""
    print("🎯 Battery Manufacturing Simulation - Plotting Demo")
    print("=" * 60)
    
    # Create plots directory
    os.makedirs("plots", exist_ok=True)
    
    # Run demonstrations
    demos = [
        ("Mixing Process Plots", demo_mixing_plots),
        ("Process Comparison", demo_process_comparison),
        ("Machine-Specific Plots", demo_machine_specific_plot),
        ("Process Flow Diagram", demo_process_flow_diagram),
        ("Summary Plots", demo_summary_plots)
    ]
    
    results = []
    for demo_name, demo_func in demos:
        print(f"\n{'='*20} {demo_name} {'='*20}")
        try:
            result = demo_func()
            results.append((demo_name, True, result))
        except Exception as e:
            print(f"❌ {demo_name} failed: {e}")
            results.append((demo_name, False, None))
    
    print("\n" + "=" * 60)
    print("🎯 Demo Results Summary")
    print("=" * 60)
    
    successful_demos = 0
    for demo_name, success, result in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{demo_name}: {status}")
        if success:
            successful_demos += 1
    
    print(f"\n📊 Overall: {successful_demos}/{len(results)} demonstrations completed successfully")
    
    if successful_demos == len(results):
        print("🎉 All demonstrations completed successfully!")
        print("\n📁 Check the 'plots' directory for generated images:")
        if os.path.exists("plots"):
            for file in os.listdir("plots"):
                if file.endswith('.png'):
                    print(f"   - {file}")
    else:
        print("⚠️  Some demonstrations failed. Check the errors above.")
    
    return successful_demos == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
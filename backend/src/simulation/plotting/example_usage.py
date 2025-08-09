"""
Example usage of plotting utilities for battery manufacturing simulation.

This script demonstrates how to use the plotting functions with simulation data.
"""

import json
import os
from pathlib import Path
from typing import List, Dict

from .plotting_utils import (
    plot_time_series,
    plot_process_comparison,
    plot_machine_data,
    create_summary_plots,
    create_process_flow_diagram,
    plot_quality_metrics
)


def load_simulation_data(output_dir: str) -> List[Dict]:
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


def example_mixing_plots():
    """Example of creating plots for mixing process data."""
    print("Creating mixing process plots...")
    
    # Load mixing data
    mixing_data = load_simulation_data("mixing_output")
    
    if mixing_data:
        # Create time series plot
        fig = plot_time_series(
            data=mixing_data,
            y_keys=['Density', 'Viscosity', 'YieldStress'],
            title="Mixing Process Parameters",
            save_path="mixing_process_plot.png"
        )
        print("Mixing process plot created successfully!")
    else:
        print("No mixing data found. Run a simulation first.")


def example_process_comparison():
    """Example of creating comparison plots between anode and cathode processes."""
    print("Creating process comparison plots...")
    
    # Load anode and cathode data
    anode_mixing_data = load_simulation_data("mixing_output")
    cathode_mixing_data = load_simulation_data("mixing_output")
    
    # Filter for anode and cathode data (you might need to adjust this based on your data structure)
    anode_data = [d for d in anode_mixing_data if d.get("Electrode Type") == "Anode"]
    cathode_data = [d for d in cathode_mixing_data if d.get("Electrode Type") == "Cathode"]
    
    if anode_data and cathode_data:
        fig = plot_process_comparison(
            anode_data=anode_data,
            cathode_data=cathode_data,
            process_name="Mixing Process",
            save_path="mixing_comparison_plot.png"
        )
        print("Process comparison plot created successfully!")
    else:
        print("No anode/cathode data found for comparison.")


def example_summary_plots():
    """Example of creating summary plots for all processes."""
    print("Creating summary plots for all processes...")
    
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
    
    # Create summary plots
    figures = create_summary_plots(
        output_dirs=output_dirs,
        save_dir="plots"
    )
    
    print(f"Created {len(figures)} summary plots in the 'plots' directory")


def example_process_flow():
    """Example of creating a process flow diagram."""
    print("Creating process flow diagram...")
    
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
        save_path="process_flow_diagram.png"
    )
    print("Process flow diagram created successfully!")


def example_machine_specific_plot(machine_id: str):
    """Example of creating plots for a specific machine."""
    print(f"Creating plots for machine {machine_id}...")
    
    # Try different output directories
    output_dirs = [
        "mixing_output",
        "coating_output",
        "drying_output", 
        "calendaring_output",
        "slitting_output",
        "inspection_output",
        "rewinding_output",
        "electrolyte_filling_output"
    ]
    
    for output_dir in output_dirs:
        if os.path.exists(output_dir):
            try:
                fig = plot_machine_data(
                    machine_id=machine_id,
                    output_dir=output_dir,
                    save_path=f"{machine_id}_{output_dir.replace('_output', '')}_plot.png"
                )
                print(f"Machine plot created for {machine_id} in {output_dir}")
                break
            except ValueError:
                continue
    else:
        print(f"No data found for machine {machine_id}")


def main():
    """Main function to run all examples."""
    print("Battery Manufacturing Simulation Plotting Examples")
    print("=" * 50)
    
    # Create plots directory
    os.makedirs("plots", exist_ok=True)
    
    # Run examples
    example_mixing_plots()
    example_process_comparison()
    example_summary_plots()
    example_process_flow()
    
    # Example for a specific machine (adjust machine_id as needed)
    example_machine_specific_plot("MC_Mix_Anode")
    
    print("\nAll examples completed! Check the 'plots' directory for generated images.")


if __name__ == "__main__":
    main() 
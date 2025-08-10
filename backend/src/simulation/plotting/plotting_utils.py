"""
Plotting utilities for battery manufacturing simulation data.

This module provides functions for creating various types of plots and visualizations
from the simulation data, including time-series plots, process comparisons, and summary charts.
"""
import matplotlib
# Use a non-interactive backend suitable for servers/threads (prevents macOS GUI errors)
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
from pathlib import Path


def setup_matplotlib_style():
    """
    Configure matplotlib style for better-looking plots.
    """
    plt.style.use('default')
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    plt.rcParams['lines.linewidth'] = 2
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10


def plot_time_series(data: List[Dict], 
                    x_key: str = "Duration", 
                    y_keys: List[str] = None,
                    title: str = "Time Series Data",
                    save_path: Optional[str] = None) -> Figure:
    """
    Create a time series plot from simulation data.
    
    Args:
        data: List of dictionaries containing time series data
        x_key: Key for x-axis data (default: "Duration")
        y_keys: List of keys for y-axis data (if None, will try to auto-detect)
        title: Plot title
        save_path: Optional path to save the plot
        
    Returns:
        matplotlib Figure object
    """
    setup_matplotlib_style()
    
    if not data:
        raise ValueError("No data provided for plotting")
    
    # Extract x-axis data
    x_data = [item.get(x_key, 0) for item in data]
    
    # Auto-detect y_keys if not provided
    if y_keys is None:
        # Common keys that might contain numerical data
        potential_keys = ['Density', 'Viscosity', 'YieldStress', 'Temperature', 
                         'Pressure', 'RPM', 'Humidity', 'Thickness', 'Width']
        y_keys = [key for key in potential_keys if key in data[0] and 
                 isinstance(data[0][key], (int, float))]
    
    if not y_keys:
        raise ValueError("No valid y-axis keys found in data")
    
    # Create subplots
    n_plots = len(y_keys)
    fig, axes = plt.subplots(n_plots, 1, figsize=(12, 4*n_plots))
    if n_plots == 1:
        axes = [axes]
    
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    for i, key in enumerate(y_keys):
        y_data = [item.get(key, 0) for item in data]
        
        axes[i].plot(x_data, y_data, 'o-', linewidth=2, markersize=4)
        axes[i].set_xlabel(x_key)
        axes[i].set_ylabel(key)
        axes[i].set_title(f"{key} vs {x_key}")
        axes[i].grid(True, alpha=0.3)
        
        # Add data points as annotations for key points
        if len(y_data) > 0:
            max_idx = np.argmax(y_data)
            min_idx = np.argmin(y_data)
            axes[i].annotate(f'Max: {y_data[max_idx]:.2f}', 
                           xy=(x_data[max_idx], y_data[max_idx]),
                           xytext=(10, 10), textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    
    return fig


def plot_process_comparison(anode_data: List[Dict], 
                           cathode_data: List[Dict],
                           process_name: str = "Process Comparison",
                           save_path: Optional[str] = None) -> Figure:
    """
    Create a comparison plot between anode and cathode processes.
    
    Args:
        anode_data: List of dictionaries containing anode process data
        cathode_data: List of dictionaries containing cathode process data
        process_name: Name of the process being compared
        save_path: Optional path to save the plot
        
    Returns:
        matplotlib Figure object
    """
    setup_matplotlib_style()
    
    if not anode_data or not cathode_data:
        raise ValueError("Both anode and cathode data are required")
    
    # Find common numerical keys
    anode_keys = set(anode_data[0].keys()) if anode_data else set()
    cathode_keys = set(cathode_data[0].keys()) if cathode_data else set()
    common_keys = anode_keys.intersection(cathode_keys)
    
    # Filter for numerical keys
    numerical_keys = [key for key in common_keys 
                     if (isinstance(anode_data[0].get(key, 0), (int, float)) and
                         isinstance(cathode_data[0].get(key, 0), (int, float)))]
    
    if not numerical_keys:
        raise ValueError("No common numerical keys found between anode and cathode data")
    
    # Create subplots
    n_plots = len(numerical_keys)
    fig, axes = plt.subplots(n_plots, 1, figsize=(12, 4*n_plots))
    if n_plots == 1:
        axes = [axes]
    
    fig.suptitle(f"{process_name} - Anode vs Cathode Comparison", fontsize=16, fontweight='bold')
    
    for i, key in enumerate(numerical_keys):
        # Extract data
        anode_x = [item.get("Duration", 0) for item in anode_data]
        anode_y = [item.get(key, 0) for item in anode_data]
        cathode_x = [item.get("Duration", 0) for item in cathode_data]
        cathode_y = [item.get(key, 0) for item in cathode_data]
        
        axes[i].plot(anode_x, anode_y, 'o-', linewidth=2, markersize=4, 
                    label='Anode', color='blue')
        axes[i].plot(cathode_x, cathode_y, 's-', linewidth=2, markersize=4, 
                    label='Cathode', color='red')
        axes[i].set_xlabel("Duration")
        axes[i].set_ylabel(key)
        axes[i].set_title(f"{key} Comparison")
        axes[i].legend()
        axes[i].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Comparison plot saved to: {save_path}")
    
    return fig


def plot_machine_data(machine_id: str, 
                     output_dir: str,
                     save_path: Optional[str] = None) -> Figure:
    """
    Create plots for a specific machine using its output data.
    
    Args:
        machine_id: ID of the machine
        output_dir: Directory containing machine output files
        save_path: Optional path to save the plot
        
    Returns:
        matplotlib Figure object
    """
    setup_matplotlib_style()
    
    # Find JSON files for this machine
    json_files = []
    for file in os.listdir(output_dir):
        if file.startswith(machine_id) and file.endswith('.json'):
            json_files.append(os.path.join(output_dir, file))
    
    if not json_files:
        raise ValueError(f"No JSON files found for machine {machine_id} in {output_dir}")
    
    # Load and combine data
    all_data = []
    for file_path in sorted(json_files):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
    
    if not all_data:
        raise ValueError(f"No valid data found for machine {machine_id}")
    
    # Create time series plot
    fig = plot_time_series(all_data, title=f"{machine_id} Process Data")
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Machine data plot saved to: {save_path}")
    
    return fig


def create_summary_plots(output_dirs: Dict[str, str],
                        save_dir: Optional[str] = None) -> List[Figure]:
    """
    Create summary plots for all processes.
    
    Args:
        output_dirs: Dictionary mapping process names to output directories
        save_dir: Optional directory to save all plots
        
    Returns:
        List of matplotlib Figure objects
    """
    setup_matplotlib_style()
    
    figures = []
    
    for process_name, output_dir in output_dirs.items():
        if not os.path.exists(output_dir):
            print(f"Warning: Output directory {output_dir} does not exist for {process_name}")
            continue
        
        # Find all JSON files in the directory
        json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
        
        if not json_files:
            print(f"No JSON files found in {output_dir} for {process_name}")
            continue
        
        # Load data from all files
        all_data = []
        for json_file in sorted(json_files):
            try:
                with open(os.path.join(output_dir, json_file), 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                    else:
                        all_data.append(data)
            except Exception as e:
                print(f"Warning: Could not load {json_file}: {e}")
        
        if all_data:
            # Create summary plot for this process
            fig = plot_time_series(all_data, title=f"{process_name} Summary")
            figures.append(fig)
            
            if save_dir:
                save_path = os.path.join(save_dir, f"{process_name}_summary.png")
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Summary plot saved to: {save_path}")
    
    return figures


def save_plot_to_file(fig: Figure, 
                     filepath: str, 
                     dpi: int = 300,
                     format: str = 'png') -> None:
    """
    Save a matplotlib figure to a file.
    
    Args:
        fig: matplotlib Figure object
        filepath: Path where to save the file
        dpi: Resolution in dots per inch
        format: File format (png, pdf, svg, etc.)
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight', format=format)
    print(f"Plot saved to: {filepath}")


def create_process_flow_diagram(processes: List[str], 
                               save_path: Optional[str] = None) -> Figure:
    """
    Create a process flow diagram showing the manufacturing steps.
    
    Args:
        processes: List of process names in order
        save_path: Optional path to save the diagram
        
    Returns:
        matplotlib Figure object
    """
    setup_matplotlib_style()
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
    # Create flow diagram
    y_positions = np.linspace(0, 1, len(processes))
    
    for i, process in enumerate(processes):
        # Draw process box
        rect = plt.Rectangle((0.1, y_positions[i] - 0.05), 0.8, 0.1, 
                           facecolor='lightblue', edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        
        # Add process name
        ax.text(0.5, y_positions[i], process, ha='center', va='center', 
               fontsize=12, fontweight='bold')
        
        # Draw arrow to next process
        if i < len(processes) - 1:
            ax.arrow(0.5, y_positions[i] - 0.05, 0, 
                    y_positions[i+1] - y_positions[i] - 0.1,
                    head_width=0.02, head_length=0.02, fc='black', ec='black')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_title("Battery Manufacturing Process Flow", fontsize=16, fontweight='bold')
    ax.axis('off')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Process flow diagram saved to: {save_path}")
    
    return fig


def plot_quality_metrics(data: List[Dict], 
                        metrics: List[str] = None,
                        save_path: Optional[str] = None) -> Figure:
    """
    Create quality metrics plots for manufacturing processes.
    
    Args:
        data: List of dictionaries containing quality metrics
        metrics: List of metric names to plot (if None, will auto-detect)
        save_path: Optional path to save the plot
        
    Returns:
        matplotlib Figure object
    """
    setup_matplotlib_style()
    
    if not data:
        raise ValueError("No data provided for quality metrics plotting")
    
    # Auto-detect metrics if not provided
    if metrics is None:
        potential_metrics = ['Quality_Score', 'Defect_Rate', 'Yield', 'Consistency']
        metrics = [metric for metric in potential_metrics 
                  if metric in data[0] and isinstance(data[0][metric], (int, float))]
    
    if not metrics:
        raise ValueError("No valid quality metrics found in data")
    
    # Create subplots
    n_metrics = len(metrics)
    fig, axes = plt.subplots(n_metrics, 1, figsize=(12, 4*n_metrics))
    if n_metrics == 1:
        axes = [axes]
    
    fig.suptitle("Quality Metrics Over Time", fontsize=16, fontweight='bold')
    
    for i, metric in enumerate(metrics):
        x_data = [item.get("Duration", i) for i, item in enumerate(data)]
        y_data = [item.get(metric, 0) for item in data]
        
        axes[i].plot(x_data, y_data, 'o-', linewidth=2, markersize=4, color='green')
        axes[i].set_xlabel("Duration")
        axes[i].set_ylabel(metric)
        axes[i].set_title(f"{metric} Over Time")
        axes[i].grid(True, alpha=0.3)
        
        # Add target line if applicable
        if metric == "Quality_Score":
            axes[i].axhline(y=0.95, color='red', linestyle='--', alpha=0.7, label='Target (95%)')
            axes[i].legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Quality metrics plot saved to: {save_path}")
    
    return fig 
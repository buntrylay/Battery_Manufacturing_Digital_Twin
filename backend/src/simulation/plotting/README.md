# Plotting Utilities for Battery Manufacturing Simulation

This module provides comprehensive plotting and visualization capabilities for the battery manufacturing simulation data.

## Features

- **Time Series Plots**: Visualize process parameters over time (density, viscosity, temperature, etc.)
- **Process Comparisons**: Compare anode vs cathode processes
- **Machine-Specific Plots**: Generate plots for specific machines
- **Summary Plots**: Create overview plots for all processes
- **Process Flow Diagrams**: Visualize the manufacturing workflow
- **Quality Metrics**: Plot quality indicators and performance metrics

## Installation

1. Ensure matplotlib is installed:

   ```bash
   pip install matplotlib==3.8.4
   ```

2. The plotting utilities are automatically available when you import the simulation module.

## Usage

### Basic Time Series Plotting

```python
from simulation.plotting.plotting_utils import plot_time_series

# Load your simulation data
data = [
    {"Duration": 0, "Density": 1.0, "Viscosity": 100},
    {"Duration": 1, "Density": 1.1, "Viscosity": 110},
    # ... more data
]

# Create a time series plot
fig = plot_time_series(
    data=data,
    y_keys=['Density', 'Viscosity'],
    title="Mixing Process Parameters",
    save_path="mixing_plot.png"
)
```

### Process Comparison

```python
from simulation.plotting.plotting_utils import plot_process_comparison

# Compare anode and cathode data
fig = plot_process_comparison(
    anode_data=anode_data,
    cathode_data=cathode_data,
    process_name="Mixing Process",
    save_path="comparison_plot.png"
)
```

### Machine-Specific Plots

```python
from simulation.plotting.plotting_utils import plot_machine_data

# Generate plots for a specific machine
fig = plot_machine_data(
    machine_id="MC_Mix_Anode",
    output_dir="mixing_output",
    save_path="machine_plot.png"
)
```

### Summary Plots

```python
from simulation.plotting.plotting_utils import create_summary_plots

# Create summary plots for all processes
output_dirs = {
    "Mixing": "mixing_output",
    "Coating": "coating_output",
    "Drying": "drying_output",
    # ... more processes
}

figures = create_summary_plots(
    output_dirs=output_dirs,
    save_dir="plots"
)
```

### Process Flow Diagram

```python
from simulation.plotting.plotting_utils import create_process_flow_diagram

# Create a process flow diagram
processes = [
    "Mixing",
    "Coating",
    "Drying",
    "Calendaring",
    "Slitting",
    "Inspection",
    "Rewinding",
    "Electrolyte Filling"
]

fig = create_process_flow_diagram(
    processes=processes,
    save_path="process_flow.png"
)
```

## API Endpoints

The plotting functionality is also available through REST API endpoints:

### Generate Process Plot

```
GET /plots/process/{process_name}
```

- `process_name`: Name of the process (e.g., 'mixing', 'coating', 'drying')
- Returns: PNG image of the process plot

### Generate Summary Plots

```
GET /plots/summary
```

- Returns: ZIP file containing all summary plots

### Generate Process Flow Diagram

```
GET /plots/flow-diagram
```

- Returns: PNG image of the process flow diagram

### Generate Machine Plot

```
GET /plots/machine/{machine_id}
```

- `machine_id`: ID of the machine (e.g., 'MC_Mix_Anode')
- Returns: PNG image of the machine plot

## Example Usage

### Running the Example Script

```bash
cd backend/src/simulation/plotting
python example_usage.py
```

This will:

1. Create plots for mixing process data
2. Generate comparison plots between anode and cathode
3. Create summary plots for all processes
4. Generate a process flow diagram
5. Create machine-specific plots

### Testing the Installation

```bash
cd backend
python test_matplotlib.py
```

This will verify that:

- Matplotlib is properly installed
- Plotting utilities can be imported
- Basic plotting functionality works

## Output Formats

All plots are saved as high-resolution PNG files (300 DPI) by default. You can also save plots in other formats by modifying the `save_plot_to_file` function:

```python
from simulation.plotting.plotting_utils import save_plot_to_file

# Save as PDF
save_plot_to_file(fig, "plot.pdf", format='pdf')

# Save as SVG
save_plot_to_file(fig, "plot.svg", format='svg')
```

## Customization

### Styling

The plotting utilities use a consistent style defined in `setup_matplotlib_style()`. You can customize the appearance by modifying this function:

```python
def setup_matplotlib_style():
    plt.style.use('default')
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    # ... more customizations
```

### Adding New Plot Types

To add new plot types, create a new function in `plotting_utils.py`:

```python
def plot_custom_visualization(data, **kwargs):
    """
    Create a custom visualization.

    Args:
        data: Input data
        **kwargs: Additional parameters

    Returns:
        matplotlib Figure object
    """
    setup_matplotlib_style()

    # Your plotting logic here
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    # ... plotting code ...

    return fig
```

## Troubleshooting

### Common Issues

1. **Matplotlib not installed**: Run `pip install matplotlib==3.8.4`
2. **Import errors**: Ensure you're in the correct directory and Python path is set
3. **No data found**: Make sure simulation has been run and output files exist
4. **Permission errors**: Check write permissions for the output directory

### Debug Mode

Enable debug mode by setting the environment variable:

```bash
export DEBUG_PLOTTING=1
```

This will provide more detailed error messages and logging information.

## Contributing

When adding new plotting functionality:

1. Follow the existing code style and documentation patterns
2. Add type hints for all function parameters
3. Include docstrings with examples
4. Add tests for new functionality
5. Update this README with new features

## License

This module is part of the Battery Manufacturing Digital Twin project and follows the same license terms.

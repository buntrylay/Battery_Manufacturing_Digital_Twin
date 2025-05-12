# Battery Manufacturing Digital Twin - Backend

This module contains the simulation and API components of the Battery Manufacturing Digital Twin project.

## Project Structure

``` txt
backend/
├── src/
│   ├── simulation/           # Simulation package
│   │   ├── battery_model/    # Battery and slurry models
│   │   ├── factory/         # Factory and manufacturing process
│   │   ├── machine/         # Machine implementations
│   │   └── sensor/          # Sensor and property calculations
│   └── server/              # API server implementation
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
└── setup.py                # Package configuration
```

## Installation

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install the package in development mode:

```bash
pip install -e .
```

## Development

### Running the Simulation

```bash
python -m src.simulation.main
```

### Running Tests

```bash
pytest tests/
```

## Dependencies

- Python 3.8+
- See `requirements.txt` for full list of dependencies

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests to ensure nothing is broken
4. Submit a pull request

## License

[Your License Here]

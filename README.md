# Battery Manufacturing Digital Twin

A digital twin system for simulating and monitoring battery manufacturing processes, focusing on slurry mixing and electrode production.

## Project Overview

This project implements a digital twin for battery manufacturing processes, with a focus on:

- Data generation in a battery manufacturing plant

## Project Structure

``` txt
Battery_Manufacturing_Digital_Twin/
├── backend/               # Python backend
│   ├── src/
│   │   ├── simulation/    # Simulation package
│   │   └── server/        # API server
│   ├── tests/             # Backend tests
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── src/               # Frontend source code
│   └── package.json       # Frontend dependencies
└── docs/                  # Documentation
```

## Getting Started

### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -e .
```

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd ..
cd frontend/
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm start
```

## Features

- **Slurry Mixing Simulation**
  - Real-time property calculations
  - Component ratio optimization
  - Process monitoring

- **Digital Twin Integration**
  - Real-time data synchronization
  - Process visualization
  - Performance analytics

- **Manufacturing Process Control**
  - Automated process adjustments
  - Quality control monitoring
  - Production optimization

## Development

### Running Tests

Backend tests:

```bash
cd backend
pytest tests/
```

Frontend tests:

```bash
cd frontend
npm test
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [List any acknowledgments or references here]

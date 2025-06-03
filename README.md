## 1. Overview

This project simulates various stages of a battery manufacturing process, from slurry mixing to electrode preparation and cell finishing. It features a Python backend (using FastAPI) to run the simulation logic and a React frontend for user interaction and parameter input. The simulation generates detailed time-series data in JSON format for each process and supports parallel processing of anode and cathode lines.

The primary goal is to create a digital twin model that can generate insightful data, potentially for training AI models, process optimization research, or educational purposes.

## 2. Features

- **Multi-Stage Simulation:** Simulates the following battery manufacturing stages:

  - Mixing ([`MixingMachine.py`](src/simulation/machine/MixingMachine.py))

  - Coating ([`CoatingMachine.py`](src/simulation/machine/CoatingMachine.py))

  - Drying ([`DryingMachine.py`](src/simulation/machine/DryingMachine.py))

  - Calendaring ([`CalendaringMachine.py`](src/simulation/machine/CalendaringMachine.py))

  - Slitting ([`SlittingMachine.py`](src/simulation/machine/SlittingMachine.py) - as per `src/server/main.py`)

  - Electrode Inspection ([`ElectrodeInspectionMachine.py`](src/simulation/machine/ElectrodeInspectionMachine.py) - as per `src/server/main.py`)

  - Rewinding ([`RewindingMachine.py`](src/simulation/machine/RewindingMachine.py))

  - Electrolyte Filling ([`ElectrolyteFillingMachine.py`](src/simulation/machine/ElectrolyteFillingMachine.py) - as per `src/server/main.py`)

  - _(As new machines like Formation Cycling are added, list them here.)_

- **Parallel Processing:** Simulates anode and cathode manufacturing lines concurrently using threading, managed by the `Factory` class ([`Factory.py`](src/simulation/factory/Factory.py)).

- **Web Interface:** A React-based frontend (`App.js`) allows users to:

  - Input material ratios for slurry mixing.

  - Start and monitor (via status messages) the simulation.

  - Download resulting output files.

- **API Backend:** A FastAPI server (`src/server/main.py`) handles requests from the frontend and orchestrates the simulation.

- **Detailed Data Logging:** Each machine generates time-series data and final results in JSON format, saved to dedicated output directories (e.g., `mixing_output/`, `coating_output/`, `drying_output/`, `calendaring_output/`, `rewinding_output/`, `electrolyte_filling_output/`).

- **IoT Integration (Optional):**

  - Includes functionality to send simulation data to Azure IoT Hub via MQTT ([`BaseMachine.py`](src/simulation/machine/BaseMachine.py), [`mqtt_watcher.py`](src/iot/mqtt_watcher.py)). The connection string needs to be configured.

- **Messaging System:** A thread-safe message queue is implemented in the backend for broadcasting messages (e.g., logs, status updates).

## 3. Project Structure

A brief overview of the key directories:

- `src/`

  - `server/`: Contains the FastAPI backend server code (`main.py`).

  - `simulation/`: Core simulation logic.

    - `battery_model/`: Data models like `Slurry.py`.

    - `factory/`: Contains `Factory.py` for orchestrating machines.

    - `machine/`: Individual machine process classes (e.g., `MixingMachine.py`, `CoatingMachine.py`, etc.).

    - `sensor/`: Property calculator classes for each machine (e.g., `SlurryPropertyCalculator.py`, `RewindingPropertyCalculator.py`).

  - `iot/`: MQTT integration for Azure IoT Hub (`mqtt_watcher.py`).

  - `simulation_local/`: Scripts for running simulations locally without the UI/API (e.g., `main.py`).

- `frontend/` _(Assuming your React app is in a folder named 'frontend', adjust if different)_

  - `src/`: Contains the React frontend code (`App.js`, `index.js`).

- `*_output/`: Directories created by the simulation to store JSON results for each stage (e.g., `mixing_output/`, `coating_output/`, `drying_output/`, `calendaring_output/`, etc.).

- `results/`: Directory created by the FastAPI server for zipped download files.

- `requirements.txt`: Python dependencies.

- `README.md`: This file.

_(Update this section if the directory structure changes significantly.)_

## 4. Prerequisites

- Python 3.8+

- Node.js and npm (for the React frontend)

- A Python virtual environment (recommended)

- Azure IoT Hub connection string (optional, if using IoT features - configure in `src/iot/mqtt_watcher.py` or `src/simulation/machine/BaseMachine.py`, ideally via an environment variable).

## 5. Setup and Installation

1.  **Clone the Repository (if applicable):**

    ```bash

    git clone <your-repository-url>

    cd <your-project-directory>

    ```

2.  **Backend Setup (Python):**

    - Navigate to the `src` directory (or your project root if `requirements.txt` is there).

    - Create and activate a Python virtual environment:

      ```bash

      python -m venv venv

      source venv/bin/activate  # On Windows: venv\Scripts\activate

      ```

    - Install Python dependencies:

      ```bash

      pip install -r requirements.txt

      ```

      _(Ensure `requirements.txt` is up-to-date with all necessary packages like `fastapi`, `uvicorn`, `numpy`, `python-multipart`, `azure-iot-device` etc.)_

3.  **Frontend Setup (React):**

    - Navigate to your frontend application directory (e.g., `frontend/`).

    - Install Node.js dependencies:

      ```bash

      npm install

      ```

## 6. Running the Simulation

You can run the simulation in different ways:

### A. Full System (Backend + Frontend)

1.  **Start the Backend Server:**

    - Navigate to the `src` directory (or where `server/main.py` is located).

    - Ensure your virtual environment is activated.

    - Run the FastAPI server using Uvicorn:

      ```bash

      uvicorn server.main:app --reload --port 8000

      ```

    - The server should now be running on `http://localhost:8000`.

2.  **Start the Frontend Application:**

    - Navigate to your frontend application directory (e.g., `frontend/`).

    - Run the React development server:

      ```bash

      npm start

      ```

    - This should automatically open the application in your web browser (usually at `http://localhost:3000`). You can then interact with the UI to start simulations.

### B. Backend Simulation Only (Local Script)

- To run the simulation logic without the UI and API server, you can use the local test script:

  ```bash

  python src/simulation_local/main.py

  ```

  - This will execute the simulation sequence defined within that script and generate output files in the respective `*_output/` directories. This is useful for backend development and testing.

### C. IoT Watcher (Optional)

- To send generated JSON files to Azure IoT Hub:

  ```bash

  python src/iot/mqtt_watcher.py

  ```

  _Ensure `CONNECTION_STRING` in the script is correctly configured._

_(Add instructions here if new ways to run specific parts of the simulation are introduced.)_

## 7. API Endpoints

The backend server (`src/server/main.py`) provides the following main endpoints:

- **`POST /start-both`**:

  - Expects a JSON payload with anode and cathode slurry compositions.

  - Initiates the full simulation for both electrode types.

  - Returns a success or error message and completion status.

- **`POST /reset`**:

  - Clears previously generated results and resets the factory state (currently clears `results/` directory).

- **`GET /files/{electrode_type}`**:

  - Downloads a zip file containing all generated JSON files for the specified `electrode_type` (Anode/Cathode) from the `simulation_output` (this seems to be a typo in `server/main.py` and should likely be the individual `*_output` directories).

  _(Add new endpoints here as they are developed.)_

## 8. Output

- The simulation generates detailed JSON files for each step of each machine.

- Time-series data is typically saved in files like `MACHINE-ID_YYYY-MM-DDTHH-MM-SS-ssssss_result_at_Xs.json`.

- Final results for a machine run are saved in last file within folder.

- These files are stored in directories corresponding to the process, e.g.:

  - `mixing_output/`

  - `coating_output/`

  - `drying_output/` (e.g., `MC_Dry_Anode_2025-05-25T16-49-51-357607_final_results_MC_Dry_Anode.json`)

  - `calendaring_output/` (e.g., `MC_Cal_Anode_2025-05-25T17-00-55-922270_final_results_MC_Cal_Anode.json`)

  - `rewinding_output/` e.g., (`MC_Rewinding_Anode_2025-05-25T17-00-55-922270_final_results_MC_Rewinding_Anode.json`)

  - `electrolyte_filling_output/`(e.g., `MC_Rewinding_Anode_2025-05-25T17-00-55-922270_final_results_MC_Rewinding_Anode.json`)

  - _(Add new output directories as new machines are added.)_

- The API provides a way to download zipped collections of these results.

## 9. Testing

_(Possibly move to a TESTING.md for clarity and ensuring less clutter)_

- **Local Simulation Script:** Use `src/simulation_local/main.py` for backend logic testing.

- **Manual Testing:** Through the React UI for frontend and frontend-backend integration.

- **Data Validation:** JSON outputs can be analyzed for correctness. Consider using scripts to aggregate data into CSV for easier analysis or graphing in tools like Excel.

- **Developer Pre-Push Checklist:** Provided within the sharepoint within – made to ensure you have documented all of the necessary stages.

## 10. Adding New Simulation Stages

This simulation is designed to be scalable. To add a new manufacturing stage (e.g., "Cell Sealing"):

1.  **Research:** Define the process, its inputs (from the preceding stage), new control parameters, governing equations, and expected outputs.

2.  **Create `[NewProcessProperty]Calculator.py`** (in `src/simulation/sensor/`): Implement the core calculation logic.

3.  **Create `[NewProcess]Machine.py`** (in `src/simulation/machine/`):

    - Inherit from `BaseMachine.py`.

    - Implement `__init__`, `update_from_previous_stage()`, `_simulate()`, `_format_result()`, `_write_json()`, and `get_final_properties()`.

    - Create a new output directory (e.g., `new_process_output/`).

4.  **Update `src/server/main.py`:**

    - Import the new machine.

    - Add `user_input_new_process` dictionary for its parameters.

    - Instantiate the new machine for anode and cathode lines.

    - Add it to the `factory` with correct dependencies in the `/start-both` endpoint.

5.  **Update `src/simulation/factory/Factory.py`:**

    - In `wait_for_dependencies()`, add an `elif` block to handle data transfer from the previous machine to your new machine.

6.  **Update `src/simulation_local/main.py`:** Add the new machine to the local test script.

7.  **Documentation:** Update this README (Features, Project Structure, Output sections) and any relevant testing documentation.

## 11. Key Technologies

- **Backend:** Python, FastAPI, Uvicorn

- **Frontend:** React (JavaScript), Axios

- **Data Format:** JSON

- **Concurrency:** Python `threading`

- **IoT (Optional):** Azure IoT Hub SDK (`azure-iot-device`)

- **Core Calculations:** NumPy (as seen in research snippets and calculators like `RewindingPropertyCalculator.py`)

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

# Battery Manufacturing Process Simulation

import time
import threading
from collections import deque
from datetime import datetime
from typing import List

import sqlalchemy
from sqlalchemy import Table, Column, Integer, Float, String, MetaData, insert, inspect
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

# ------------------------
# --- Database Setup ---
# ------------------------
DATABASE_URL = "postgresql://postgres:password@db:5432/postgres"

engine = None
for _ in range(10):
    try:
        engine = sqlalchemy.create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        print("✅ Database connected")
        break
    except Exception:
        print("⏳ Waiting for database...")
        time.sleep(3)
else:
    raise Exception("❌ Failed to connect to database after multiple attempts")

metadata_dynamic = MetaData()

# ------------------------
# --- WebSocket Manager ---
# ------------------------
MAX_MESSAGES = 100
message_queue = deque(maxlen=MAX_MESSAGES)
message_lock = threading.Lock()
simulation_lock = threading.Lock()
main_loop = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def _send_message(self, websocket: WebSocket, message: str):
        try:
            await websocket.send_text(message)
        except Exception:
            self.disconnect(websocket)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        with message_lock:
            for msg in message_queue:
                await websocket.send_text(msg)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    def broadcast(self, message: str):
        for connection in self.active_connections:
            asyncio.create_task(self._send_message(connection, message))

manager = ConnectionManager()

def thread_broadcast(message: str):
    global main_loop
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    with message_lock:
        message_queue.append(formatted_message)
    if main_loop and main_loop.is_running():
        main_loop.call_soon_threadsafe(manager.broadcast, formatted_message)

# ------------------------
# --- Pydantic Models ---
# ------------------------
class SlurryInput(BaseModel):
    PVDF: float
    CA: float
    AM: float
    Solvent: float

class SimulationInput(BaseModel):
    anode: SlurryInput
    cathode: SlurryInput

# ------------------------
# --- Database Helpers ---
# ------------------------
def create_table_if_not_exists(engine, table_name: str):
    table_name_clean = table_name.lower().replace("mixing_", "")
    inspector = inspect(engine)
    if table_name_clean in inspector.get_table_names():
        return Table(table_name_clean, metadata_dynamic, autoload_with=engine)

    table = Table(
        table_name_clean,
        metadata_dynamic,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("timestamp", String),
        Column("duration", Float),
        Column("process", String),
        Column("temperature_c", Float),
        Column("am_volume", Float),
        Column("ca_volume", Float),
        Column("pvdf_volume", Float),
        Column("solvent_volume", Float), # Changed from h2o_volume
        Column("viscosity", Float),
        Column("density", Float),
        Column("yield_stress", Float),
        Column("total_volume", Float),
        Column("ratio_am", Float),
        Column("ratio_ca", Float),
        Column("ratio_pvdf", Float),
        Column("ratio_solvent", Float),
        extend_existing=True,
    )
    metadata_dynamic.create_all(engine, checkfirst=True)
    print(f"✅ Table '{table_name_clean}' created.")
    return table

def insert_flattened_data(engine, data: list):
    if not data:
        thread_broadcast(" No data to insert.")
        return

    table_name = data[0].get("process") or "default"
    table = create_table_if_not_exists(engine, table_name)
    
    records_to_insert = []
    for record_data in data:
        battery_model = record_data.get("battery_model") or {}
        machine_params = record_data.get("machine_parameters") or {}
        material_ratios = machine_params.get("material_ratios") or {}

        # Get the correct solvent volume based on the model's key
        solvent_volume = battery_model.get("H2O_volume", 0) or battery_model.get("NMP_volume", 0)

        record = {
            "timestamp": record_data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duration": float(record_data.get("duration", 0)),
            "process": record_data.get("process") or table_name,
            "temperature_c": float(record_data.get("temperature_C", 0)),
            "am_volume": float(battery_model.get("AM_volume", 0)),
            "ca_volume": float(battery_model.get("CA_volume", 0)),
            "pvdf_volume": float(battery_model.get("PVDF_volume", 0)),
            "solvent_volume": float(solvent_volume), # Use the generic solvent_volume
            "viscosity": float(battery_model.get("viscosity", 0)),
            "density": float(battery_model.get("density", 0)),
            "yield_stress": float(battery_model.get("yield_stress", 0)),
            "total_volume": float(battery_model.get("total_volume", 0)),
            "ratio_am": float(material_ratios.get("AM", 0)),
            "ratio_ca": float(material_ratios.get("CA", 0)),
            "ratio_pvdf": float(material_ratios.get("PVDF", 0)),
            "ratio_solvent": float(material_ratios.get("solvent", 0)),
        }
        records_to_insert.append(record)

    try:
        with engine.begin() as conn:
            conn.execute(insert(table), records_to_insert)
        thread_broadcast(f"✅ Inserted {len(records_to_insert)} records into '{table_name}'.")
    except Exception as e:
        thread_broadcast(f"❌ Failed to insert into '{table_name}': {e}")
        print("DEBUG records:", records_to_insert)

# ------------------------
# --- Simulation Functions ---
# ------------------------
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.MixingMachine import MixingMachine, MixingParameters, MaterialRatios

def run_machine(process: str, slurry_input: SlurryInput):
    thread_broadcast(f"--- Starting {process} ---")
    model = MixingModel(process)
    params = MixingParameters(
        material_ratios=MaterialRatios(
            PVDF=slurry_input.PVDF,
            CA=slurry_input.CA,
            AM=slurry_input.AM,
            solvent=slurry_input.Solvent
        )
    )
    machine = MixingMachine(model, params)
    all_results = machine.run()

    if all_results is None or not isinstance(all_results, list):
        thread_broadcast(f"{process} machine returned no result!")
        return

    for result in all_results:
        result["process"] = process

    insert_flattened_data(engine, all_results)
    thread_broadcast(f"--- {process} Finished ---")

def run_simulation(payload: SimulationInput):
    if not simulation_lock.acquire(blocking=False):
        thread_broadcast("⚠️ Simulation already in progress.")
        return

    try:
        thread_broadcast("✅ New simulation started.")
        machines = [("Anode", payload.anode), ("Cathode", payload.cathode)]
        for name, slurry in machines:
            run_machine(name, slurry)
        thread_broadcast("✅ Simulation complete.")
    finally:
        simulation_lock.release()

# ------------------------
# --- FastAPI App ---
# ------------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    global main_loop
    main_loop = asyncio.get_running_loop()

@app.post("/start-simulation")
def start_simulation(payload: SimulationInput):
    threading.Thread(target=run_simulation, args=(payload,)).start()
    return {"message": "Simulation started. See WebSocket for progress."}

@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
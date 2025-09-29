import threading
import time
from collections import deque
from datetime import datetime
from backend.src.server.db.db import SessionLocal
from backend.src.server.db.model_table import *
from typing import Dict, Any

class DBHelper:
    def __init__(self, queue_size=1000, batch_size=50, interval=5):
        self.db_queue = deque(maxlen=queue_size)
        self.db_lock = threading.Lock()
        self.db_worker_thread = None
        self.db_worker_running = False
        self.batch_size = batch_size
        self.interval = interval

    def queue_data(self, payload: Dict[str, Any]):
        with self.db_lock:
            if 'timestamp' not in payload:
                payload['timestamp'] = datetime.now().isoformat()
            self.db_queue.append(payload)

    def start_worker(self, broadcast_fn=None):
        if not self.db_worker_thread or not self.db_worker_thread.is_alive():
            self.db_worker_running = True
            self.db_worker_thread = threading.Thread(
                target=self._worker, args=(broadcast_fn,), daemon=True)
            self.db_worker_thread.start()

    def stop_worker(self):
        self.db_worker_running = False
        if self.db_worker_thread:
            self.db_worker_thread.join(timeout=10)

    def _worker(self, broadcast_fn):
        while self.db_worker_running:
            time.sleep(self.interval)
            if not self.db_queue:
                continue
            batch_data = []
            with self.db_lock:
                while self.db_queue and len(batch_data) < self.batch_size:
                    batch_data.append(self.db_queue.popleft())
            if batch_data:
                try:
                    db = SessionLocal()
                    saved_count = 0
                    for data in batch_data:
                        record = self.create_db_record(data, broadcast_fn)
                        if record:
                            db.add(record)
                            saved_count += 1
                    db.commit()
                    if broadcast_fn:
                        broadcast_fn(f"✓ Saved {saved_count} records to database")
                except Exception as e:
                    if broadcast_fn:
                        broadcast_fn(f"✗ Database error: {str(e)}")
                    with open("failed_db_writes.log", "a") as f:
                        f.write(f"[{datetime.now()}] Failed to save {len(batch_data)} records: {e}\n")
                finally:
                    db.close()

    @staticmethod
    def create_db_record(simulation_data: Dict[str, Any], broadcast_fn=None):
        def safe_float(val, default=0.0):
            try:
                return float(val)
            except Exception:
                return default
        try:
            process_type = simulation_data.get('process', 'unknown')
            if process_type == 'Anode_Mixer':
                battery_model = simulation_data.get('battery_model', {})
                machine_params = simulation_data.get('machine_parameters', {})
                return AnodeMixing(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'mixing_anode'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)),
                    am_volume_L=safe_float(battery_model.get('AM_volume', 0.0)),
                    ca_volume_L=safe_float(battery_model.get('CA_volume', 0.0)),
                    pvdf_volume_L=safe_float(battery_model.get('PVDF_volume', 0.0)),
                    solvent_volume_L=safe_float(battery_model.get('H2O_volume', 0.0)),
                    viscosity_Pa_s=safe_float(battery_model.get('viscosity', 0.0)),
                    density_kg_m3=safe_float(battery_model.get('density', 0.0)),
                    yield_stress_Pa=safe_float(battery_model.get('yield_stress', 0.0)),
                    total_volume_L=safe_float(battery_model.get('total_volume', 0.0)),
                    am=safe_float(machine_params.get('AM_ratio', 0.0)),
                    ca=safe_float(machine_params.get('CA_ratio', 0.0)),
                    pvdf=safe_float(machine_params.get('PVDF_ratio', 0.0)),
                    solvent=safe_float(machine_params.get('solvent_ratio', 0.0))
                )
            elif process_type == 'Cathode_Mixer':
                battery_model = simulation_data.get('battery_model', {})
                machine_params = simulation_data.get('machine_parameters', {})
                return CathodeMixing(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'mixing_anode'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)),
                    am_volume_L=safe_float(battery_model.get('AM_volume', 0.0)),
                    ca_volume_L=safe_float(battery_model.get('CA_volume', 0.0)),
                    pvdf_volume_L=safe_float(battery_model.get('PVDF_volume', 0.0)),
                    solvent_volume_L=safe_float(battery_model.get('H2O_volume', 0.0)),
                    viscosity_Pa_s=safe_float(battery_model.get('viscosity', 0.0)),
                    density_kg_m3=safe_float(battery_model.get('density', 0.0)),
                    yield_stress_Pa=safe_float(battery_model.get('yield_stress', 0.0)),
                    total_volume_L=safe_float(battery_model.get('total_volume', 0.0)),
                    am=safe_float(machine_params.get('AM_ratio', 0.0)),
                    ca=safe_float(machine_params.get('CA_ratio', 0.0)),
                    pvdf=safe_float(machine_params.get('PVDF_ratio', 0.0)),
                    solvent=safe_float(machine_params.get('solvent_ratio', 0.0))
                )
            else:
                if broadcast_fn:
                    broadcast_fn(f"⚠ Unknown process type: {process_type}")
                return None
        except Exception as e:
            if broadcast_fn:
                broadcast_fn(f"✗ Error creating DB record: {str(e)}")
                broadcast_fn(f"Problematic data: {simulation_data}")
            return None

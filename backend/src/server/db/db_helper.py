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
            battery_model = simulation_data.get('battery_model', {})
            machine_params = simulation_data.get('machine_parameters', {})
            if process_type == 'mixing_anode':
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
            elif process_type == 'mixing_cathode':
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
            elif process_type == 'coating_anode':
                return AnodeCoating(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'coating_anode'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)),
                    # battery_model fields
                    solid_content=safe_float(battery_model.get('solid_content', 0.0)),
                    viscosity_Pa_s=safe_float(battery_model.get('viscosity', 0.0)),
                    wet_thickness_um=safe_float(battery_model.get('wet_thickness', 0.0)),
                    dry_thickness_um=safe_float(battery_model.get('dry_thickness', 0.0)),
                    defect_risk=bool(battery_model.get('defect_risk', False)),
                    # machine_parameters
                    coating_speed=safe_float(machine_params.get('coating_speed', 0.0)),
                    gap_height_um=safe_float(machine_params.get('gap_height', 0.0)),
                    flow_rate=safe_float(machine_params.get('flow_rate', 0.0)),
                    coating_width_mm=safe_float(machine_params.get('coating_width', 0.0)),
                )
            elif process_type == 'coating_cathode':
                return CathodeCoating(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'coating_cathode'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)),
                    # battery_model fields
                    solid_content=safe_float(battery_model.get('solid_content', 0.0)),
                    viscosity=safe_float(battery_model.get('viscosity', 0.0)),
                    wet_thickness_um=safe_float(battery_model.get('wet_thickness', 0.0)),
                    dry_thickness_um=safe_float(battery_model.get('dry_thickness', 0.0)),
                    defect_risk=bool(battery_model.get('defect_risk', False)),
                    # machine_parameters
                    coating_speed=safe_float(machine_params.get('coating_speed', 0.0)),
                    gap_height_um=safe_float(machine_params.get('gap_height', 0.0)),
                    flow_rate=safe_float(machine_params.get('flow_rate', 0.0)),
                    coating_width_mm=safe_float(machine_params.get('coating_width', 0.0)),
                )
            elif process_type == 'drying_anode':
                return AnodeDrying(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'drying_anode'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)),
                    # battery_model fields
                    wet_thickness_um=safe_float(battery_model.get('wet_thickness', 0.0)) * 1e6,  # convert m to um
                    dry_thickness_um=safe_float(battery_model.get('dry_thickness', 0.0)) * 1e6,  # convert m to um
                    m_solvent=safe_float(battery_model.get('M_solvent', 0.0)),
                    defect_risk=bool(battery_model.get('defect_risk', False)),
                    solid_content=safe_float(battery_model.get('solid_content', 0.0)),
                    temperature=safe_float(battery_model.get('temperature', 0.0)),
                    # machine_parameters
                    web_speed=safe_float(machine_params.get('web_speed', 0.0))
                )
            elif process_type == 'drying_cathode':
                return CathodeDrying(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'drying_cathode'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)),
                    # battery_model fields
                    wet_thickness_um=safe_float(battery_model.get('wet_thickness', 0.0)) * 1e6,
                    dry_thickness_um=safe_float(battery_model.get('dry_thickness', 0.0)) * 1e6,
                    m_solvent=safe_float(battery_model.get('M_solvent', 0.0)),
                    defect_risk=bool(battery_model.get('defect_risk', False)),
                    solid_content=safe_float(battery_model.get('solid_content', 0.0)),
                    temperature=safe_float(battery_model.get('temperature', 0.0)),
                    # machine_parameters
                    web_speed=safe_float(machine_params.get('web_speed', 0.0))
                )
            elif process_type == 'calendaring_anode':
                return AnodeCalendaring(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'calendaring_anode'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)),
                    # battery_model fields
                    final_thickness_um=safe_float(battery_model.get('final_thickness', 0.0)) * 1e6,
                    porosity=safe_float(battery_model.get('porosity', 0.0)),
                    defect_risk=bool(battery_model.get('defect_risk', False)),
                    # machine_parameters
                    roll_gap_um=safe_float(machine_params.get('roll_gap', 0.0)) * 1e6,
                    roll_pressure=safe_float(machine_params.get('roll_pressure', 0.0)),
                    temperature=safe_float(machine_params.get('temperature', 0.0)),
                    roll_speed=safe_float(machine_params.get('roll_speed', 0.0)),
                    dry_thickness_um=safe_float(machine_params.get('dry_thickness', 0.0)) * 1e6,
                    initial_porosity=safe_float(machine_params.get('initial_porosity', 0.0))
                )
            elif process_type == 'calendaring_cathode':
                return CathodeCalendaring(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'calendaring_cathode'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)),
                    # battery_model fields
                    final_thickness_um=safe_float(battery_model.get('final_thickness', 0.0)) * 1e6,  # m to um
                    porosity=safe_float(battery_model.get('porosity', 0.0)),
                    defect_risk=bool(battery_model.get('defect_risk', False)),
                    # machine_parameters
                    roll_gap_um=safe_float(machine_params.get('roll_gap', 0.0)) * 1e6,  # m to um
                    roll_pressure=safe_float(machine_params.get('roll_pressure', 0.0)),
                    temperature=safe_float(machine_params.get('temperature', 0.0)),
                    roll_speed=safe_float(machine_params.get('roll_speed', 0.0)),
                    dry_thickness_um=safe_float(machine_params.get('dry_thickness', 0.0)) * 1e6,  # m to um
                    initial_porosity=safe_float(machine_params.get('initial_porosity', 0.0))
                )
            elif process_type == 'slitting_anode':
                return AnodeSlitting(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'slitting_anode'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)) if simulation_data.get('temperature_C', None) is not None else None,
                    # battery_model fields
                    final_thickness_um=safe_float(battery_model.get('final_thickness', 0.0)) * 1e6,
                    width_final_mm=safe_float(battery_model.get('width_final', 0.0)),
                    epsilon_width=safe_float(battery_model.get('epsilon_width', 0.0)),
                    burr_factor=safe_float(battery_model.get('burr_factor', 0.0)),
                    defect_risk=bool(battery_model.get('defect_risk', False)),
                    # machine_parameters
                    blade_sharpness=safe_float(machine_params.get('blade_sharpness', 0.0)),
                    slitting_speed=safe_float(machine_params.get('slitting_speed', 0.0)),
                    target_width_mm=safe_float(machine_params.get('target_width', 0.0)),
                    slitting_tension=safe_float(machine_params.get('slitting_tension', 0.0))
                )
            elif process_type == 'slitting_cathode':
                return CathodeSlitting(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'slitting_cathode'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)) if simulation_data.get('temperature_C', None) is not None else None,
                    # battery_model fields
                    final_thickness_um=safe_float(battery_model.get('final_thickness', 0.0)) * 1e6,
                    width_final_mm=safe_float(battery_model.get('width_final', 0.0)),
                    epsilon_width=safe_float(battery_model.get('epsilon_width', 0.0)),
                    burr_factor=safe_float(battery_model.get('burr_factor', 0.0)),
                    defect_risk=bool(battery_model.get('defect_risk', False)),
                    # machine_parameters
                    blade_sharpness=safe_float(machine_params.get('blade_sharpness', 0.0)),
                    slitting_speed=safe_float(machine_params.get('slitting_speed', 0.0)),
                    target_width_mm=safe_float(machine_params.get('target_width', 0.0)),
                    slitting_tension=safe_float(machine_params.get('slitting_tension', 0.0))
                )
            elif process_type == "inspection_anode":
                return AnodeInspection(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'inspection_anode'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)) if simulation_data.get('temperature_C', None) is not None else None,
                    # battery_model fields
                    final_width_mm=safe_float(battery_model.get('final_width', 0.0)),
                    final_thickness_um=safe_float(battery_model.get('final_thickness', 0.0)) * 1e6,
                    epsilon_width=safe_float(battery_model.get('epsilon_width', 0.0)),
                    burr_factor=safe_float(battery_model.get('burr_factor', 0.0)),
                    porosity=safe_float(battery_model.get('porosity', 0.0)),
                    epsilon_thickness=safe_float(battery_model.get('epsilon_thickness', 0.0)),
                    d_detected=safe_float(battery_model.get('D_detected', 0.0)),
                    pass_width_mm=bool(battery_model.get('Pass_width', False)),
                    pass_thickness_um=bool(battery_model.get('Pass_thickness', False)),
                    pass_burr=bool(battery_model.get('Pass_burr', False)),
                    pass_surface=bool(battery_model.get('Pass_surface', False)),
                    overall= bool(battery_model.get('Overall', False)),
                    # machine_parameters
                    epsilon_width_max=safe_float(machine_params.get('epsilon_width_max', 0.0)),
                    epsilon_thickness_max=safe_float(machine_params.get('epsilon_thickness_max', 0.0)),
                    b_max=safe_float(machine_params.get('B_max', 0.0)),
                    d_surface_max=safe_float(machine_params.get('D_surface_max', 0.0))
                )
            elif process_type == "inspection_cathode":
                return CathodeInspection(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'inspection_anode'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)) if simulation_data.get('temperature_C', None) is not None else None,
                    # battery_model fields
                    final_width_mm=safe_float(battery_model.get('final_width', 0.0)),
                    final_thickness_um=safe_float(battery_model.get('final_thickness', 0.0)) * 1e6,
                    epsilon_width=safe_float(battery_model.get('epsilon_width', 0.0)),
                    burr_factor=safe_float(battery_model.get('burr_factor', 0.0)),
                    porosity=safe_float(battery_model.get('porosity', 0.0)),
                    epsilon_thickness=safe_float(battery_model.get('epsilon_thickness', 0.0)),
                    d_detected=safe_float(battery_model.get('D_detected', 0.0)),
                    pass_width_mm=bool(battery_model.get('Pass_width', False)),
                    pass_thickness_um=bool(battery_model.get('Pass_thickness', False)),
                    pass_burr=bool(battery_model.get('Pass_burr', False)),
                    pass_surface=bool(battery_model.get('Pass_surface', False)),
                    overall= bool(battery_model.get('Overall', False)),
                    # machine_parameters
                    epsilon_width_max=safe_float(machine_params.get('epsilon_width_max', 0.0)),
                    epsilon_thickness_max=safe_float(machine_params.get('epsilon_thickness_max', 0.0)),
                    b_max=safe_float(machine_params.get('B_max', 0.0)),
                    d_surface_max=safe_float(machine_params.get('D_surface_max', 0.0))
                )
            elif process_type == 'rewinding':
                return Rewinding(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'rewinding'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)) if simulation_data.get('temperature_C', None) is not None else None,
                    # battery_model fields
                    final_thickness_um=safe_float(battery_model.get('final_thickness', 0.0)) * 1e6,
                    porosity=safe_float(battery_model.get('porosity', 0.0)),
                    final_width_mm=safe_float(battery_model.get('final_width', 0.0)),
                    epsilon_width=safe_float(battery_model.get('epsilon_width', 0.0)),
                    wound_length_m=safe_float(battery_model.get('wound_length', 0.0)),
                    roll_diameter_mm=safe_float(battery_model.get('roll_diameter', 0.0)) * 1e3,  # convert m to mm
                    web_tension=safe_float(battery_model.get('web_tension', 0.0)),
                    roll_hardness=safe_float(battery_model.get('roll_hardness', 0.0)),
                    # machine_parameters
                    rewinding_speed=safe_float(machine_params.get('rewinding_speed', 0.0)),
                    initial_tension=safe_float(machine_params.get('initial_tension', 0.0)),
                    tapering_steps=safe_float(machine_params.get('tapering_steps', 0.0)),
                    environment_humidity=safe_float(machine_params.get('environment_humidity', 0.0))
                )
            elif process_type == 'electrolyte_filling':
                return ElectrolyteFilling(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'electrolyte_filling'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)) if simulation_data.get('temperature_C', None) is not None else None,
                    # battery_model fields
                    final_thickness_um=safe_float(battery_model.get('final_thickness', 0.0)) * 1e6,
                    porosity=safe_float(battery_model.get('porosity', 0.0)),
                    final_width_mm=safe_float(battery_model.get('final_width', 0.0)),
                    epsilon_width=safe_float(battery_model.get('epsilon_width', 0.0)),
                    wound_length_m=safe_float(battery_model.get('wound_length', 0.0)),
                    v_sep=safe_float(battery_model.get('V_sep', 0.0)),
                    v_elec=safe_float(battery_model.get('V_elec', 0.0)),
                    v_max=safe_float(battery_model.get('V_max', 0.0)),
                    eta_wetting=safe_float(battery_model.get('eta_wetting', 0.0)),
                    v_elec_filling=safe_float(battery_model.get('V_elec_filling', 0.0)),
                    defect_risk=bool(battery_model.get('defect_risk', False)),
                    # machine_parameters
                    vacuum_level=safe_float(machine_params.get('Vacuum_level', 0.0)),
                    vacuum_filling=safe_float(machine_params.get('Vacuum_filling', 0.0)),
                    soaking_time_s=safe_float(machine_params.get('Soaking_time', 0.0))
                )
            elif process_type == 'formation_cycling':
                return FormationCycling(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'formation_cycling'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)) if simulation_data.get('temperature_C', None) is not None else None,
                    # battery_model fields
                    voltage_v=safe_float(battery_model.get('Voltage_V', 0.0)),
                    capacity_Ah=safe_float(battery_model.get('Capacity_Ah', 0.0)),
                    sei_efficiency=safe_float(battery_model.get('sei_efficiency', 0.0)),
                    eta_wetting=safe_float(battery_model.get('Eta wetting', 0.0)),
                    volume_electrolyte=safe_float(battery_model.get('Volume_electrolyte', 0.0)),
                    # machine_parameters
                    charge_current_A=safe_float(machine_params.get('Charge_current_A', 0.0)),
                    charge_voltage_limit_V=safe_float(machine_params.get('Charge_voltage_limit_V', 0.0)),
                    initial_voltage=safe_float(machine_params.get('Initial_Voltage', 0.0)),
                    formation_duration_s=safe_float(machine_params.get('Formation_duration_s', 0.0))
                )
            elif process_type == 'aging':
                return Aging(
                    batch=simulation_data.get('batch_id', 1),
                    state=simulation_data.get('state', 'Unknown'),
                    timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                    duration=safe_float(simulation_data.get('duration', 0.0)),
                    process=simulation_data.get('process', 'aging'),
                    temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)) if simulation_data.get('temperature_C', None) is not None else None,
                    # battery_model fields
                    soc=safe_float(battery_model.get('SOC', 0.0)),
                    initial_soc=safe_float(battery_model.get('Initial_SOC', 0.0)),
                    final_ocv_v=safe_float(battery_model.get('Final_OCV_V', 0.0)),
                    leakage_current_A=safe_float(battery_model.get('Leakage_Current_A', 0.0)),
                    defect_risk=bool(battery_model.get('defect_risk', False)),
                    # machine_parameters
                    k_leak=safe_float(machine_params.get('k_leak', 0.0)),
                    temperature=safe_float(machine_params.get('temperature', 0.0)),
                    aging_time_days=safe_float(machine_params.get('aging_time_days', 0.0))
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

from backend.src.server.db.db import engine, Base
from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime

class CathodeMixing(Base):
    __tablename__ = "mixing_cathode"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    am_volume_L = Column(Float)
    ca_volume_L = Column(Float)
    pvdf_volume_L = Column(Float)
    solvent_volume_L = Column(Float)
    viscosity_Pa_s = Column(Float)
    density_kg_m3 = Column(Float)
    yield_stress_Pa = Column(Float)
    total_volume_L = Column(Float)

    # machine_parameters
    am = Column(Float)
    ca = Column(Float)
    pvdf = Column(Float)
    solvent = Column(Float)

class AnodeMixing(Base):
    __tablename__ = "mixing_anode"
    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    am_volume_L = Column(Float)
    ca_volume_L = Column(Float)
    pvdf_volume_L = Column(Float)
    solvent_volume_L = Column(Float)
    viscosity_Pa_s = Column(Float)
    density_kg_m3 = Column(Float)
    yield_stress_Pa = Column(Float)
    total_volume_L = Column(Float)

    # machine_parameters
    am = Column(Float)
    ca = Column(Float)
    pvdf = Column(Float)
    solvent = Column(Float)
    
# --- Coating ---
class CathodeCoating(Base):
    __tablename__ = "coating_cathode"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    temperature = Column(Float)
    solid_content = Column(Float)
    viscosity_Pa_s = Column(Float)
    wet_thickness_um = Column(Float)
    dry_thickness_um = Column(Float)
    shear_rate = Column(Float)
    uniformity = Column(Float)
    defect_risk = Column(Float)

    # machine_parameters
    coating_speed = Column(Float)
    gap_height_um = Column(Float)
    flow_rate = Column(Float)
    coating_width_mm = Column(Float)
    
class AnodeCoating(Base):
    __tablename__ = "coating_anode"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    temperature = Column(Float)
    solid_content = Column(Float)
    viscosity_Pa_s = Column(Float)
    wet_thickness_um = Column(Float)
    dry_thickness_um = Column(Float)
    shear_rate = Column(Float)
    uniformity = Column(Float)
    defect_risk = Column(Float)

    # machine_parameters
    coating_speed = Column(Float)
    gap_height_um = Column(Float)
    flow_rate = Column(Float)
    coating_width_mm = Column(Float)


# --- Drying ---
class CathodeDrying(Base):
    __tablename__ = "drying_cathode"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    wet_thickness_um = Column(Float)
    dry_thickness_um = Column(Float)
    m_solvent = Column(Float)
    defect_risk = Column(Float)
    solid_content = Column(Float)
    temperature = Column(Float)

    # machine_parameters
    web_speed = Column(Float)
    
class AnodeDrying(Base):  
    __tablename__ = "drying_anode"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    wet_thickness_um = Column(Float)
    dry_thickness_um = Column(Float)
    m_solvent = Column(Float)
    defect_risk = Column(Float)
    solid_content = Column(Float)
    temperature = Column(Float)

    # machine_parameters
    web_speed = Column(Float)
    


# --- Calendaring ---
class CathodeCalendaring(Base):
    __tablename__ = "calendaring_cathode"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    final_thickness_um = Column(Float)
    porosity = Column(Float)
    defect_risk = Column(Float)

    # machine_parameters
    roll_gap_um = Column(Float)
    roll_pressure = Column(Float)
    temperature = Column(Float)
    roll_speed = Column(Float)
    dry_thickness_um = Column(Float)
    initial_porosity = Column(Float)
    
class AnodeCalendaring(Base):
    __tablename__ = "calendaring_anode"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    final_thickness_um = Column(Float)
    porosity = Column(Float)
    defect_risk = Column(Float)

    # machine_parameters
    roll_gap_um = Column(Float)
    roll_pressure = Column(Float)
    temperature = Column(Float)
    roll_speed = Column(Float)
    dry_thickness_um = Column(Float)
    initial_porosity = Column(Float)


# --- Slitting ---
class CathodeSlitting(Base):
    __tablename__ = "slitting_cathode"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    final_thickness_um = Column(Float)
    width_final_mm = Column(Float)
    epsilon_width = Column(Float)
    burr_factor = Column(Float)
    defect_risk = Column(Float)

    # machine_parameters
    blade_sharpness = Column(Float)
    slitting_speed = Column(Float)
    target_width_mm = Column(Float)
    slitting_tension = Column(Float)
    
class AnodeSlitting(Base):
    __tablename__ = "slitting_anode"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    final_thickness_um = Column(Float)
    width_final_mm = Column(Float)
    epsilon_width = Column(Float)
    burr_factor = Column(Float)
    defect_risk = Column(Float)

    # machine_parameters
    blade_sharpness = Column(Float)
    slitting_speed = Column(Float)
    target_width_mm = Column(Float)
    slitting_tension = Column(Float)


# --- Inspection ---
class Inspection(Base):
    __tablename__ = "inspection"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    final_width_mm = Column(Float)
    final_thickness_um = Column(Float)
    epsilon_width = Column(Float)
    burr_factor = Column(Float)
    porosity = Column(Float)
    epsilon_thickness = Column(Float)
    d_detected = Column(Float)
    pass_width_mm = Column(Float)
    pass_thickness_um = Column(Float)
    pass_burr = Column(Float)
    pass_surface = Column(Float)
    overall = Column(Float)

    # machine_parameters
    epsilon_width_max = Column(Float)
    epsilon_thickness_max = Column(Float)
    b_max = Column(Float)
    d_surface_max = Column(Float)


# --- Rewinding ---
class Rewinding(Base):
    __tablename__ = "rewinding"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    final_thickness_um = Column(Float)
    porosity = Column(Float)
    final_width_mm = Column(Float)
    epsilon_width = Column(Float)
    wound_length_m = Column(Float)
    roll_diameter_mm = Column(Float)
    web_tension = Column(Float)
    roll_hardness = Column(Float)

    # machine_parameters
    rewinding_speed = Column(Float)
    initial_tension = Column(Float)
    tapering_steps = Column(Float)
    environment_humidity = Column(Float)


# --- Electrolyte Filling ---
class ElectrolyteFilling(Base):
    __tablename__ = "electrolyte_filling"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    final_thickness_um = Column(Float)
    porosity = Column(Float)
    final_width_mm = Column(Float)
    epsilon_width = Column(Float)
    wound_length_m = Column(Float)
    v_sep = Column(Float)
    v_elec = Column(Float)
    v_max = Column(Float)
    eta_wetting = Column(Float)
    v_elec_filling = Column(Float)
    defect_risk = Column(Float)

    # machine_parameters
    vacuum_level = Column(Float)
    vacuum_filling = Column(Float)
    soaking_time_s = Column(Float)


# --- Formation Cycling ---
class FormationCycling(Base):
    __tablename__ = "formation_cycling"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    voltage_v = Column(Float)
    capacity_Ah = Column(Float)
    sei_efficiency = Column(Float)
    eta_wetting = Column(Float)
    volume_electrolyte = Column(Float)

    # machine_parameters
    charge_current_A = Column(Float)
    charge_voltage_limit_V = Column(Float)
    initial_voltage = Column(Float)
    formation_duration_s = Column(Float)


# --- Aging ---
class Aging(Base):
    __tablename__ = "aging"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)
    process = Column(String, nullable=False)
    temperature_C = Column(Float)

    # battery_model
    soc = Column(Float)
    initial_soc = Column(Float)
    final_ocv_v = Column(Float)
    leakage_current_A = Column(Float)
    defect_risk = Column(Float)

    # machine_parameters
    k_leak = Column(Float)
    temperature = Column(Float)
    aging_time_days = Column(Float)
    
    
def create_tables():
    Base.metadata.create_all(bind=engine)

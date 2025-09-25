from backend.src.server.db.db import engine, Base
from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
class AnodeMixing(Base):
    __tablename__ = "mixing_anode"
    id = Column(Integer, primary_key=True, index=True)
    batch = Column(Integer, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)  # in seconds
    process = Column(String, nullable=False)
    temperature_C = Column(Float)
    am_volumne_L = Column(Float)  # Anode material volume in liters
    cm_volume_L = Column(Float)  # Cathode material volume in liters
    solvent_volume_L = Column(Float)  # Solvent volume in liters
    viscosity_Pa_s = Column(Float)  # Viscosity in Pascal-seconds
    density_kg_m3 = Column(Float)  # Density in kg/m^3
    yield_stress_Pa = Column(Float)  # Yield stress in Pascals
    total_volumn_L = Column(Float)  # Total volume in liters
    am = Column(Float)  # Active Material in kg
    ca = Column(Float)  # Conductive Additive in kg
    pvdf = Column(Float)  # PVDF binder in kg
    solvent = Column(Float)  # Solvent in kg

class CathodeMixing(Base):
    __tablename__ = "mixing_cathode"
    id = Column(Integer, primary_key=True, index=True)
    batch = Column(Integer, nullable=False)
    state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Float, nullable=False)  # in seconds
    process = Column(String, nullable=False)
    temperature_C = Column(Float)
    am_volumne_L = Column(Float)  # Anode material volume in liters
    cm_volume_L = Column(Float)  # Cathode material volume in liters
    solvent_volume_L = Column(Float)  # Solvent volume in liters
    viscosity_Pa_s = Column(Float)  # Viscosity in Pascal-seconds
    density_kg_m3 = Column(Float)  # Density in kg/m^3
    yield_stress_Pa = Column(Float)  # Yield stress in Pascals
    total_volumn_L = Column(Float)  # Total volume in liters
    am = Column(Float)  # Active Material in kg
    ca = Column(Float)  # Conductive Additive in kg
    pvdf = Column(Float)  # PVDF binder in kg
    solvent = Column(Float)  # Solvent in kg



def create_tables():
    Base.metadata.create_all(bind=engine)
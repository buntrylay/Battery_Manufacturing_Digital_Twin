import time
from datetime import datetime
import sqlalchemy
from sqlalchemy import Table, Column, Integer, Float, String, MetaData, insert

# --- Database Connection ---
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

# --- Dynamic Machine-Specific Tables ---
def create_table_if_not_exists(engine, table_name: str):
    """Create a dynamic table per machine"""
    table = Table(
        table_name.lower(),
        metadata_dynamic,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("timestamp", String),
        Column("duration", Float),
        Column("process", String),
        Column("temperature_c", Float),
        Column("am_volume", Float),
        Column("ca_volume", Float),
        Column("pvdf_volume", Float),
        Column("h2o_volume", Float),
        Column("viscosity", Float),
        Column("density", Float),
        Column("yield_stress", Float),
        Column("total_volume", Float),
        Column("ratio_am", Float),
        Column("ratio_ca", Float),
        Column("ratio_pvdf", Float),
        Column("ratio_solvent", Float),
    )
    table.create(engine, checkfirst=True)
    return table

def insert_flattened_data(engine, table_name: str, data: dict):
    """Insert directly from dict into the machine-specific table (real-time)"""
    table = create_table_if_not_exists(engine, table_name)
    record = {
        "timestamp": data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "duration": data.get("duration", 0),
        "process": data.get("process", ""),
        "temperature_c": data.get("temperature_C", 0),
        "am_volume": data.get("battery_model", {}).get("AM_volume", 0),
        "ca_volume": data.get("battery_model", {}).get("CA_volume", 0),
        "pvdf_volume": data.get("battery_model", {}).get("PVDF_volume", 0),
        "h2o_volume": data.get("battery_model", {}).get("H2O_volume", 0),
        "viscosity": float(data.get("battery_model", {}).get("viscosity", 0)),
        "density": float(data.get("battery_model", {}).get("density", 0)),
        "yield_stress": float(data.get("battery_model", {}).get("yield_stress", 0)),
        "total_volume": data.get("battery_model", {}).get("total_volume", 0),
        "ratio_am": data.get("machine_parameters", {}).get("material_ratios", {}).get("AM", 0),
        "ratio_ca": data.get("machine_parameters", {}).get("material_ratios", {}).get("CA", 0),
        "ratio_pvdf": data.get("machine_parameters", {}).get("material_ratios", {}).get("PVDF", 0),
        "ratio_solvent": data.get("machine_parameters", {}).get("material_ratios", {}).get("solvent", 0),
    }
    try:
        with engine.begin() as conn:
            conn.execute(insert(table).values(**record))
    except Exception as e:
        print(f"❌ Failed to insert flattened data: {e}")

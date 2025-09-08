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

# Bind metadata to engine here
metadata_dynamic = MetaData()

# --- Dynamic Machine-Specific Tables ---
def create_table_if_not_exists(engine, table_name: str):
    """Create a dynamic table per machine"""
    table = Table(
        table_name.lower().replace(" ", "_"),
        metadata_dynamic,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("timestamp", String),
        Column("duration", Float),
        Column("process", String),
        Column("temperature_c", Float),
        Column("am_volume", Float),
        Column("ca_volume", Float),
        Column("pvdf_volume", Float),
        Column("solvent_volume", Float),  # Changed from h2o_volume
        Column("viscosity", Float),
        Column("density", Float),
        Column("yield_stress", Float),
        Column("total_volume", Float),
        extend_existing=True,
    )
    metadata_dynamic.create_all(engine, checkfirst=True)
    return table

def insert_flattened_data(engine, data: dict):
    """Insert into a process-specific table (auto-detects from data['process'])"""
    table_name = data.get("process", "default").lower().replace(" ", "_")
    table = create_table_if_not_exists(engine, table_name)

    # Get the correct solvent volume based on the model's key
    battery_model = data.get("battery_model", {})
    solvent_volume = battery_model.get("H2O_volume", 0) or battery_model.get("NMP_volume", 0)

    record = {
        "timestamp": data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "duration": float(data.get("duration", 0)),
        "process": data.get("process", ""),
        "temperature_c": float(data.get("temperature_C", 0)),
        "am_volume": float(battery_model.get("AM_volume", 0)),
        "ca_volume": float(battery_model.get("CA_volume", 0)),
        "pvdf_volume": float(battery_model.get("PVDF_volume", 0)),
        "solvent_volume": float(solvent_volume),  # Use the generic solvent_volume
        "viscosity": float(battery_model.get("viscosity", 0)),
        "density": float(battery_model.get("density", 0)),
        "yield_stress": float(battery_model.get("yield_stress", 0)),
        "total_volume": float(battery_model.get("total_volume", 0)),
    }

    try:
        with engine.begin() as conn:
            conn.execute(insert(table).values(**record))
        print(f"✅ Inserted into {table_name} at {record['timestamp']}")
    except Exception as e:
        print(f"❌ Failed to insert flattened data into {table_name}: {e}")
        print("DEBUG record was:", record)
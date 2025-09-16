import time
from datetime import datetime
import sqlalchemy
from sqlalchemy import Table, Column, Integer, Float, String, MetaData, insert, inspect

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

def create_table_if_not_exists(engine, table_name: str):
    """
    Create a dynamic table for each process if it does not already exist.
    The table name is derived from the process name.
    """
    table_name_clean = table_name.lower().replace(" ", "_")
    inspector = inspect(engine)
    if table_name_clean in inspector.get_table_names():
        return Table(table_name_clean, metadata_dynamic, autoload_with=engine)

    table = Table(
        table_name_clean,
        metadata_dynamic,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("timestamp", datetime, default=datetime.now),
        Column("duration", Float),
        Column("process", String),
        Column("temperature_c", Float),
        Column("am_volume", Float),
        Column("ca_volume", Float),
        Column("pvdf_volume", Float),
        Column("solvent_volume", Float),
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
    """
    Inserts a list of flattened data records into the appropriate table.
    """
    if not data:
        print(" No data to insert.")
        return

    table_name = "mixing" + data[0].get("process") or "default"
    table = create_table_if_not_exists(engine, table_name)
    
    records_to_insert = []
    for record_data in data:
        battery_model = record_data.get("battery_model") or {}
        machine_params = record_data.get("machine_parameters") or {}
        material_ratios = machine_params.get("material_ratios") or {}

        solvent_volume = battery_model.get("H2O_volume", 0) or battery_model.get("NMP_volume", 0)

        record = {
            "timestamp": record_data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duration": float(record_data.get("duration", 0)),
            "process": record_data.get("process"),
            "temperature_c": float(record_data.get("temperature_C", 0)),
            "am_volume": float(battery_model.get("AM_volume", 0)),
            "ca_volume": float(battery_model.get("CA_volume", 0)),
            "pvdf_volume": float(battery_model.get("PVDF_volume", 0)),
            "solvent_volume": float(solvent_volume),
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
        print(f"Inserted {len(records_to_insert)} records into '{table_name}'.")
    except Exception as e:
        print(f"Failed to insert into '{table_name}': {e}")
        print("DEBUG records:", records_to_insert)
import time
from datetime import datetime
from typing import Any, Dict

import sqlalchemy
from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    MetaData,
    insert,
    text,
    inspect,
)

# --- Database Connection ---
DATABASE_URL = "postgresql://postgres:password@db:5432/postgres"

engine = None
for _ in range(10):
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        print("Database connected")
        break
    except Exception:
        print("⏳ Waiting for database...")
        time.sleep(3)
else:
    raise Exception("Failed to connect to database after multiple attempts")

metadata_dynamic = MetaData()


def _clean_table_name(name: str) -> str:
    return (name or "unknown").strip().lower().replace(" ", "_")


def _is_number(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return True
    if isinstance(v, str):
        try:
            float(v)
            return True
        except ValueError:
            return False
    return False


def _to_float(v: Any):
    try:
        return float(v) if v not in (None, "") else None
    except Exception:
        return None


def _flatten(d: Dict[str, Any], parent: str = "", sep: str = "_") -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in (d or {}).items():
        key = f"{parent}{sep}{k}" if parent else k
        if isinstance(v, dict):
            out.update(_flatten(v, key, sep))
        elif isinstance(v, (list, tuple)):
            # skip arrays to avoid schema explosion
            continue
        else:
            out[key] = v
    return out


def _base_fields(row: Dict[str, Any]) -> Dict[str, Any]:
    ts_raw = row.get("timestamp")
    if isinstance(ts_raw, datetime):
        ts = ts_raw
    else:
        # Accept ISO strings (from BaseMachine.get_current_state) or fallback to now
        try:
            ts = datetime.fromisoformat(str(ts_raw)) if ts_raw else datetime.now()
        except Exception:
            ts = datetime.now()
    # prefer duration, then duration_s, duration_sec
    dur = row.get("duration")
    if dur is None:
        dur = row.get("duration_s", row.get("duration_sec"))
    return {
        "timestamp": ts,
        "duration": _to_float(dur),
        "process": row.get("process") or row.get("Process"),
    }


def _get_or_create_table(db_engine, process_name: str) -> Table:
    table_name = _clean_table_name(process_name)
    inspector = inspect(db_engine)

    if table_name in inspector.get_table_names():
        return Table(table_name, metadata_dynamic, autoload_with=db_engine)

    table = Table(
        table_name,
        metadata_dynamic,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("timestamp", DateTime),
        Column("duration", Float),
        Column("process", String),
        extend_existing=True,
    )
    metadata_dynamic.create_all(db_engine, checkfirst=True)
    print(f"✅ Table '{table_name}' created.")
    return table


def _ensure_columns(db_engine, table_name: str, rows: list[Dict[str, Any]]):
    """
    Add missing columns (Float for numeric values, TEXT otherwise) based on provided rows.
    """
    inspector = inspect(db_engine)
    existing = {col["name"] for col in inspector.get_columns(table_name)}
    to_add: dict[str, str] = {}

    for row in rows:
        for k, v in row.items():
            if k in existing or k == "id":
                continue
            sql_type = "DOUBLE PRECISION" if _is_number(v) else "TEXT"
            to_add.setdefault(k, sql_type)

    if not to_add:
        return

    parts = [f'ADD COLUMN IF NOT EXISTS "{col}" {sql_type}' for col, sql_type in to_add.items()]
    ddl = f'ALTER TABLE "{table_name}" ' + ", ".join(parts)
    with db_engine.begin() as conn:
        conn.execute(text(ddl))
    print(f"🔧 Table '{table_name}' altered: added {len(to_add)} column(s).")


def insert_flattened_data(db_engine, results: list):
    """
    Store results into per-process tables with typed columns.
    - Creates a table per process name (lowercased, spaces -> underscores).
    - Flattens nested dicts; arrays are skipped.
    - Infers column types once (Float for numeric, TEXT otherwise). No JSON columns.
    """
    if not results:
        return

    grouped: dict[str, list[Dict[str, Any]]] = {}

    # Prepare records
    for r in results:
        if not isinstance(r, dict):
            continue

        base = _base_fields(r)
        table_name = _clean_table_name(base["process"])

        flat = _flatten(r)
        record = dict(base)
        for k, v in flat.items():
            if k in record:
                continue
            record[k] = v

        grouped.setdefault(table_name, []).append(record)

    # Create/alter tables and insert
    try:
        with db_engine.begin() as conn:
            for table_name, records in grouped.items():
                if not records:
                    continue

                _get_or_create_table(db_engine, table_name)
                _ensure_columns(db_engine, table_name, records)

                # Reflect the latest table schema from the database using a fresh MetaData
                # to ensure we see columns that may have been added via _ensure_columns.
                table = Table(table_name, MetaData(), autoload_with=db_engine)

                # Identify numeric columns to coerce values (exclude datetime)
                numeric_types = ("double", "float", "numeric", "real")
                numeric_cols = {
                    c["name"]
                    for c in inspect(db_engine).get_columns(table_name)
                    if any(str(c["type"]).lower().startswith(nt) for nt in numeric_types)
                }

                prepped = []
                for rec in records:
                    r2 = {}
                    for k, v in rec.items():
                        if k in numeric_cols:
                            r2[k] = _to_float(v)
                        else:
                            r2[k] = None if v is None else (str(v) if isinstance(v, (dict, list)) else v)
                    prepped.append(r2)

                conn.execute(insert(table), prepped)
                print(f"✅ Inserted {len(prepped)} records into '{table_name}'.")
    except Exception as e:
        print(f"❌ Failed to insert records: {e}")
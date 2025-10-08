from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import psycopg2
# --- Database Connection ---
DATABASE_URL = "postgresql://postgres:password@db:5432/postgres"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def user_connection():
    """Create a read-only user for Grafana with proper error handling."""
    commands = [
        "CREATE USER grafana_reader WITH PASSWORD 'password' IF NOT EXISTS;",
        "GRANT CONNECT ON DATABASE postgres TO grafana_reader;",
        "GRANT ALL PRIVILEGES ON DATABASE postgres TO grafana_reader;",
        "GRANT USAGE ON SCHEMA public TO grafana_reader;",
        "GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafana_reader;",
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO grafana_reader;"
    ]
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                for command in commands:
                    try:
                        cur.execute(command)
                        print(f"Executed: {command}")
                    except psycopg2.Error as e:
                        # Skip if user already exists or other expected errors
                        if "already exists" in str(e):
                            print(f"User already exists, skipping: {command}")
                            conn.rollback()  # Rollback only this command, continue with others
                        else:
                            print(f"Error executing {command}: {e}")
                            conn.rollback()
                conn.commit()
                print("User connection setup completed")
    except Exception as e:
        print(f"Failed to setup user connection: {e}")
        return False
    return True

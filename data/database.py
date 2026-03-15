from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database Connection
# By default, we use a local SQLite for dev if no POSTGRES_URL is provided,
# but the plan requires PostgreSQL capability.
# Example PG URL: postgresql+psycopg2://user:password@host:port/dbname

# Create ~/.smartgestion directory if it doesn't exist
APP_DIR = os.path.expanduser("~/.smartgestion")
os.makedirs(APP_DIR, exist_ok=True)

DEFAULT_DB_PATH = os.path.join(APP_DIR, "madina_stock.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# If using PostgreSQL:
# DATABASE_URL = "postgresql+psycopg2://postgres:password123@localhost:5432/madinadb"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

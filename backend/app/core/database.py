from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create database engine based on database type
if settings.DATABASE_TYPE == "sqlite":
    # SQLite configuration for development
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # Required for SQLite
        echo=settings.DEBUG,  # Show SQL queries in debug mode
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Models will be imported in main.py to avoid circular imports


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with all tables"""
    Base.metadata.create_all(bind=engine)
    # Lightweight dev migration helpers (SQLite only) to avoid missing-column errors
    try:
        if settings.DATABASE_TYPE == "sqlite":
            with engine.connect() as conn:
                # Ensure hygiene_score column exists on supplier_evaluations
                res = conn.execute("PRAGMA table_info('supplier_evaluations')").fetchall()
                existing_cols = {row[1] for row in res}  # row[1] is column name
                if 'hygiene_score' not in existing_cols:
                    conn.execute("ALTER TABLE supplier_evaluations ADD COLUMN hygiene_score FLOAT")
                if 'hygiene_comments' not in existing_cols:
                    conn.execute("ALTER TABLE supplier_evaluations ADD COLUMN hygiene_comments TEXT")
                # Ensure non_conformance tables exist (if metadata create_all missed due to import order)
                tables = {row[1] for row in conn.execute("PRAGMA table_list").fetchall()} if hasattr(conn, 'exec_driver_sql') else set()
                conn.commit()
    except Exception:
        # Never break app startup for best-effort dev migrations
        pass
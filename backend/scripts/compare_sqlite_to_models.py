"""One-off: compare backend/iso22000_fsms.db to SQLAlchemy models (Base.metadata)."""
import json
import os
import sqlite3
import sys

# Run from backend/: python scripts/compare_sqlite_to_models.py
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BACKEND_ROOT)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

os.environ["DATABASE_URL"] = "sqlite:///./iso22000_fsms.db"
os.environ["DATABASE_TYPE"] = "sqlite"

from app.core.database import Base  # noqa: E402
import importlib  # noqa: E402

# Register every table: __init__.py does not import all model submodules.
_models_dir = os.path.join(BACKEND_ROOT, "app", "models")
for fn in sorted(os.listdir(_models_dir)):
    if not fn.endswith(".py") or fn.startswith("_"):
        continue
    modname = f"app.models.{fn[:-3]}"
    try:
        importlib.import_module(modname)
    except Exception as exc:  # pragma: no cover
        print("WARN: could not import", modname, ":", exc, file=sys.stderr)

DB_PATH = os.path.join(BACKEND_ROOT, "iso22000_fsms.db")
if not os.path.isfile(DB_PATH):
    print("Missing:", DB_PATH)
    sys.exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
db_tables = {r[0] for r in cur.fetchall()}


def table_cols(table: str) -> dict:
    cur.execute("PRAGMA table_info(%s)" % table.replace('"', ""))
    return {row[1]: (row[2] or "").upper() for row in cur.fetchall()}


db_schema = {t: table_cols(t) for t in db_tables}

meta_tables = set(Base.metadata.tables.keys())
model_cols = {
    tname: {c.name: str(c.type) for c in table.columns}
    for tname, table in Base.metadata.tables.items()
}

skip = {"alembic_version"}
only_db = sorted(db_tables - meta_tables - skip)
only_model = sorted(meta_tables - db_tables - skip)

missing_in_db: dict[str, list[str]] = {}
extra_in_db: dict[str, list[str]] = {}
for t in sorted((db_tables & meta_tables) - skip):
    db_c = set(db_schema[t].keys())
    m_c = set(model_cols[t].keys())
    if m_c - db_c:
        missing_in_db[t] = sorted(m_c - db_c)
    if db_c - m_c:
        extra_in_db[t] = sorted(db_c - m_c)

print("=== TABLES ONLY IN SQLITE (not in models metadata) ===")
print(json.dumps(only_db, indent=2))
print("=== TABLES ONLY IN MODELS (not in sqlite file) ===")
print(json.dumps(only_model, indent=2))
print("=== COLUMNS IN MODELS MISSING FROM SQLITE ===")
print(json.dumps(missing_in_db, indent=2))
print("=== COLUMNS IN SQLITE NOT IN MODELS ===")
print(json.dumps(extra_in_db, indent=2))
print("=== COUNTS ===")
print("sqlite tables:", len(db_tables), "model tables:", len(meta_tables))

import os
import sqlite3
import sys

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BACKEND, "iso22000_fsms.db")
if not os.path.isfile(DB):
    print("Missing", DB)
    sys.exit(1)
c = sqlite3.connect(DB)
cur = c.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall() if not r[0].startswith("sqlite_")]
rows = []
for t in tables:
    try:
        n = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        if n:
            rows.append((n, t))
    except Exception as e:
        rows.append((-1, t, str(e)))
rows.sort(reverse=True)
print("TOP TABLES BY ROW COUNT:")
for r in rows[:50]:
    print(r[0], r[1])
print("--- tables with data:", sum(1 for x in rows if isinstance(x[0], int) and x[0] > 0))

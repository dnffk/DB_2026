from pathlib import Path
import duckdb

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "cookie_db.db"

con = duckdb.connect(str(DB_PATH))

print("DB 경로:", DB_PATH)
print("\n[테이블 목록]")
tables = con.execute("SHOW TABLES").fetchall()

for table in tables:
    print("-", table[0])

print("\n[각 테이블 행 개수]")
for table in tables:
    table_name = table[0]
    count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"{table_name}: {count} rows")

con.close()
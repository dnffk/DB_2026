from pathlib import Path
import pandas as pd
import duckdb


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
#DB 파일을 저장할 폴더
DB_DIR = BASE_DIR / "db"
#실제 DuckDB 파일 경로
DB_PATH = DB_DIR / "cookie_db.db"


def read_csv_korean(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {path}")

    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp949")


def save_df(con: duckdb.DuckDBPyConnection, table_name: str, df: pd.DataFrame):
    con.execute(f"DROP TABLE IF EXISTS {table_name}")
    con.register("temp_df", df)
    con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM temp_df")
    con.unregister("temp_df")


def init_db():
    con = duckdb.connect(str(DB_PATH))

    table_files = {
        "element": "Element.csv",
        "position": "Position.csv",
        "cookie": "Cookie.csv",
        "item": "Item.csv",
        "artifact": "Artifact.csv",
        "potential": "Potential.csv",
        "siegeknight": "SiegeKnight.csv",
        "skill": "Skill.csv",
        "cookie_item_recommend": "CookieItemRecommend.csv",
        "cookie_artifact_recommend": "CookieArtifactRecommend.csv",
        "cookie_potential_recommend": "CookiePotentialRecommend.csv",
        "cookie_siegeknight_recommend": "CookieSiegeknightRecommend.csv",
    }

    for table_name, file_name in table_files.items():
        df = read_csv_korean(file_name)
        save_df(con, table_name, df)

    print("DuckDB 저장 완료")
    print(f"DB 경로: {DB_PATH}")

    for table_name in table_files.keys():
        count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"{table_name}: {count} rows")

    con.close()


if __name__ == "__main__":
    init_db()
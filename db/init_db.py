from pathlib import Path
import pandas as pd
import duckdb


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

# DB 파일을 저장할 폴더
DB_DIR = BASE_DIR / "db"

# 실제 DuckDB 파일 경로
DB_PATH = DB_DIR / "cookie_db.db"


# CSV 파일을 읽어오는 함수
# 한글 데이터가 포함되어 있으므로 utf-8-sig를 먼저 시도하고, 실패하면 cp949로 다시 읽음
def read_csv_korean(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {path}")

    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp949")


# DataFrame을 DuckDB 테이블로 저장하는 함수
# 기존에 같은 이름의 테이블이 있으면 삭제한 뒤 새로 생성
def save_df(con: duckdb.DuckDBPyConnection, table_name: str, df: pd.DataFrame):
    con.execute(f"DROP TABLE IF EXISTS {table_name}")
    con.register("temp_df", df)
    con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM temp_df")
    con.unregister("temp_df")


# CSV 파일들을 읽어서 DuckDB 데이터베이스에 테이블로 저장하는 초기화 함수
def init_db():
    # db 폴더가 없을 경우를 대비해 생성
    DB_DIR.mkdir(exist_ok=True)

    con = duckdb.connect(str(DB_PATH))

    # DuckDB 테이블 이름과 CSV 파일 이름을 매칭
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

    # 각 CSV 파일을 읽고 같은 이름의 DuckDB 테이블로 저장
    for table_name, file_name in table_files.items():
        df = read_csv_korean(file_name)
        save_df(con, table_name, df)

    print("DuckDB 저장 완료")
    print(f"DB 경로: {DB_PATH}")

    # 생성된 각 테이블의 행 개수를 출력하여 정상 저장 여부를 확인
    for table_name in table_files.keys():
        count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"{table_name}: {count} rows")

    con.close()


# 이 파일을 직접 실행했을 때만 DB 초기화를 수행
if __name__ == "__main__":
    init_db()
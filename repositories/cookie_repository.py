from pathlib import Path
import duckdb


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "db" / "cookie_db.db"


# DuckDB 데이터베이스에 연결하는 함수
def get_connection():
    return duckdb.connect(str(DB_PATH))


# 특정 테이블에 특정 컬럼이 존재하는지 확인하는 함수
# 일부 추천 테이블에는 rank 컬럼이 있을 수도 있고 없을 수도 있어서 확인용으로 사용
def has_column(con, table_name: str, column_name: str) -> bool:
    columns = con.execute(f"PRAGMA table_info('{table_name}')").fetchall()
    column_names = [col[1] for col in columns]
    return column_name in column_names


# 속성 목록을 조회하는 함수
# 속성 선택 화면에서 element_id, element_name, element_image를 사용
def get_elements():
    con = get_connection()

    query = """
        SELECT
            element_id,
            element_name,
            element_image
        FROM element
        ORDER BY element_id
    """

    rows = con.execute(query).fetchall()
    con.close()
    return rows


# 선택한 속성에 해당하는 쿠키 목록을 조회하는 함수
# 속성 카드를 선택하면 해당 속성의 쿠키만 드롭다운에 표시하기 위해 사용
def get_cookies_by_element(element_id):
    con = get_connection()

    query = """
        SELECT
            cookie_id,
            cookie_name
        FROM cookie
        WHERE CAST(element_id AS INTEGER) = CAST(? AS INTEGER)
        ORDER BY cookie_id
    """

    rows = con.execute(query, [element_id]).fetchall()
    con.close()
    return rows


# 선택한 쿠키의 기본 정보와 스킬 정보를 함께 조회하는 함수
# cookie, element, position, skill 테이블을 JOIN
# 쿠키 이름, 쿠키 이미지, 속성, 포지션, 스킬 정보를 한 번에 가져옴
def get_cookie_basic_info_with_skills(cookie_id):
    con = get_connection()

    query = """
        SELECT
            c.cookie_id,
            c.cookie_name,
            c.cookie_image,
            e.element_name,
            e.element_image,
            p.position_name,
            s.skill_id,
            s.skill_name,
            s.skill_description
        FROM cookie c
        JOIN element e
            ON CAST(c.element_id AS INTEGER) = CAST(e.element_id AS INTEGER)
        JOIN position p
            ON CAST(c.position_id AS INTEGER) = CAST(p.position_id AS INTEGER)
        LEFT JOIN skill s
            ON CAST(c.cookie_id AS INTEGER) = CAST(s.cookie_id AS INTEGER)
        WHERE CAST(c.cookie_id AS INTEGER) = CAST(? AS INTEGER)
        ORDER BY s.skill_id
    """

    rows = con.execute(query, [cookie_id]).fetchall()
    con.close()
    return rows


# 선택한 쿠키의 추천 장비를 조회하는 함수
# cookie, cookie_item_recommend, item 테이블을 JOIN
# Entity 2개인 cookie와 item을 Relationship 테이블인 cookie_item_recommend로 연결
def get_recommended_items(cookie_id):
    con = get_connection()

    query = """
        SELECT
            c.cookie_id,
            c.cookie_name,
            i.item_id,
            i.item_name,
            cir.item_recommend_rank
        FROM cookie c
        JOIN cookie_item_recommend cir
            ON CAST(c.cookie_id AS INTEGER) = CAST(cir.cookie_id AS INTEGER)
        JOIN item i
            ON CAST(cir.item_id AS INTEGER) = CAST(i.item_id AS INTEGER)
        WHERE CAST(c.cookie_id AS INTEGER) = CAST(? AS INTEGER)
        ORDER BY cir.item_recommend_rank
    """

    rows = con.execute(query, [cookie_id]).fetchall()
    con.close()
    return rows


# 선택한 쿠키의 추천 아티팩트를 조회하는 함수
# cookie, cookie_artifact_recommend, artifact 테이블을 JOIN
# artifact_rank 컬럼이 있으면 해당 순위를 사용하고, 없으면 자동으로 순위를 생성
def get_recommended_artifacts(cookie_id):
    con = get_connection()

    car_has_rank = has_column(con, "cookie_artifact_recommend", "artifact_rank")

    if car_has_rank:
        query = """
            SELECT
                c.cookie_id,
                c.cookie_name,
                a.artifact_id,
                a.artifact_name,
                a.artifact_image,
                car.artifact_rank
            FROM cookie c
            JOIN cookie_artifact_recommend car
                ON CAST(c.cookie_id AS INTEGER) = CAST(car.cookie_id AS INTEGER)
            JOIN artifact a
                ON CAST(car.artifact_id AS INTEGER) = CAST(a.artifact_id AS INTEGER)
            WHERE CAST(c.cookie_id AS INTEGER) = CAST(? AS INTEGER)
            ORDER BY car.artifact_rank
        """
    else:
        query = """
            SELECT
                c.cookie_id,
                c.cookie_name,
                a.artifact_id,
                a.artifact_name,
                a.artifact_image,
                ROW_NUMBER() OVER (
                    PARTITION BY c.cookie_id
                    ORDER BY a.artifact_id
                ) AS artifact_rank
            FROM cookie c
            JOIN cookie_artifact_recommend car
                ON CAST(c.cookie_id AS INTEGER) = CAST(car.cookie_id AS INTEGER)
            JOIN artifact a
                ON CAST(car.artifact_id AS INTEGER) = CAST(a.artifact_id AS INTEGER)
            WHERE CAST(c.cookie_id AS INTEGER) = CAST(? AS INTEGER)
            ORDER BY artifact_rank
        """

    rows = con.execute(query, [cookie_id]).fetchall()
    con.close()
    return rows


# 선택한 쿠키의 추천 시즈나이트를 조회하는 함수
# cookie, cookie_siegeknight_recommend, siegeknight 테이블을 JOIN
# siegeknight_rank 컬럼이 있으면 해당 순위를 사용하고, 없으면 자동으로 순위를 생성
def get_recommended_siegeknights(cookie_id):
    con = get_connection()

    csr_has_rank = has_column(con, "cookie_siegeknight_recommend", "siegeknight_rank")

    if csr_has_rank:
        query = """
            SELECT
                c.cookie_id,
                c.cookie_name,
                sk.siegeknight_id,
                sk.siegeknight_name,
                csr.siegeknight_rank
            FROM cookie c
            JOIN cookie_siegeknight_recommend csr
                ON CAST(c.cookie_id AS INTEGER) = CAST(csr.cookie_id AS INTEGER)
            JOIN siegeknight sk
                ON CAST(csr.siegeknight_id AS INTEGER) = CAST(sk.siegeknight_id AS INTEGER)
            WHERE CAST(c.cookie_id AS INTEGER) = CAST(? AS INTEGER)
            ORDER BY csr.siegeknight_rank
        """
    else:
        query = """
            SELECT
                c.cookie_id,
                c.cookie_name,
                sk.siegeknight_id,
                sk.siegeknight_name,
                ROW_NUMBER() OVER (
                    PARTITION BY c.cookie_id
                    ORDER BY sk.siegeknight_id
                ) AS siegeknight_rank
            FROM cookie c
            JOIN cookie_siegeknight_recommend csr
                ON CAST(c.cookie_id AS INTEGER) = CAST(csr.cookie_id AS INTEGER)
            JOIN siegeknight sk
                ON CAST(csr.siegeknight_id AS INTEGER) = CAST(sk.siegeknight_id AS INTEGER)
            WHERE CAST(c.cookie_id AS INTEGER) = CAST(? AS INTEGER)
            ORDER BY siegeknight_rank
        """

    rows = con.execute(query, [cookie_id]).fetchall()
    con.close()
    return rows


# 잠재력 ID와 잠재력 이름을 딕셔너리 형태로 조회하는 함수
# potential_1부터 potential_8까지의 컬럼명을 실제 잠재력 이름으로 바꿔 보여주기 위해 사용
def get_potential_names():
    con = get_connection()

    query = """
        SELECT potential_id, potential_name
        FROM potential
        ORDER BY potential_id
    """

    rows = con.execute(query).fetchall()
    con.close()

    return {
        int(potential_id): potential_name
        for potential_id, potential_name in rows
    }


# 선택한 쿠키의 장비별 잠재력 추천 정보를 조회하는 함수
# cookie, cookie_potential_recommend, item 테이블을 JOIN
# 잠재력 추천은 쿠키와 장비 조합에 따라 달라지므로 item_id까지 함께 사용
def get_recommended_potentials_by_cookie(cookie_id):
    con = get_connection()

    query = """
        SELECT
            c.cookie_id,
            c.cookie_name,
            i.item_id,
            i.item_name,
            cpr.item_recommend_rank,
            cpr.potential_1,
            cpr.potential_2,
            cpr.potential_3,
            cpr.potential_4,
            cpr.potential_5,
            cpr.potential_6,
            cpr.potential_7,
            cpr.potential_8
        FROM cookie c
        JOIN cookie_potential_recommend cpr
            ON CAST(c.cookie_id AS INTEGER) = CAST(cpr.cookie_id AS INTEGER)
        JOIN item i
            ON CAST(cpr.item_id AS INTEGER) = CAST(i.item_id AS INTEGER)
        WHERE CAST(c.cookie_id AS INTEGER) = CAST(? AS INTEGER)
        ORDER BY cpr.item_recommend_rank
    """

    rows = con.execute(query, [cookie_id]).fetchall()
    con.close()
    return rows


# 잠재력 추천 조회 결과를 UI 표에 넣기 좋은 형태로 변환하는 함수
# 반환값은 잠재력 이름 목록과 장비별 잠재력 개수 목록
def get_potential_table_rows(cookie_id):
    potential_name_map = get_potential_names()
    rows = get_recommended_potentials_by_cookie(cookie_id)

    result = []

    for row in rows:
        (
            _cookie_id,
            _cookie_name,
            _item_id,
            item_name,
            item_recommend_rank,
            potential_1,
            potential_2,
            potential_3,
            potential_4,
            potential_5,
            potential_6,
            potential_7,
            potential_8,
        ) = row

        values = [
            potential_1,
            potential_2,
            potential_3,
            potential_4,
            potential_5,
            potential_6,
            potential_7,
            potential_8,
        ]

        counts = []

        # potential_1부터 potential_8까지의 값을 정수로 변환
        # 값이 비어 있거나 변환할 수 없는 경우에는 0으로 처리
        for value in values:
            if value is None or str(value).strip() == "":
                counts.append(0)
            else:
                try:
                    counts.append(int(value))
                except Exception:
                    counts.append(0)

        # UI에서 한 행으로 표시할 장비별 잠재력 데이터를 저장
        result.append(
            {
                "rank": int(item_recommend_rank),
                "item_name": item_name,
                "counts": counts,
            }
        )

    # potential_id 1부터 8까지의 이름을 순서대로 가져옴
    # 이름이 없는 경우에는 잠재력1, 잠재력2처럼 기본 이름을 사용
    potential_names = [
        potential_name_map.get(1, "잠재력1"),
        potential_name_map.get(2, "잠재력2"),
        potential_name_map.get(3, "잠재력3"),
        potential_name_map.get(4, "잠재력4"),
        potential_name_map.get(5, "잠재력5"),
        potential_name_map.get(6, "잠재력6"),
        potential_name_map.get(7, "잠재력7"),
        potential_name_map.get(8, "잠재력8"),
    ]

    return potential_names, result
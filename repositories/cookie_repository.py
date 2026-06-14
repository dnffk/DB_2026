from pathlib import Path
import duckdb


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "db" / "cookie_db.db"


def get_connection():
    return duckdb.connect(str(DB_PATH))


def get_elements():
    con = get_connection()

    query = """
        SELECT element_id, element_name
        FROM element
        ORDER BY element_id
    """

    rows = con.execute(query).fetchall()
    con.close()
    return rows


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


def get_cookie_basic_info_with_skills(cookie_id):
    con = get_connection()

    query = """
        SELECT
            c.cookie_id,
            c.cookie_name,
            e.element_name,
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
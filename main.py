import flet as ft
import pandas as pd
import duckdb


def main(page: ft.Page):
    page.title = "Asset List"
    page.padding = 16

    # 데이터베이스 접속
    con = duckdb.connect("data/duckdb.db")

    # assets.csv 파일을 읽어서 테이블 생성
    con.execute("""
        CREATE TABLE IF NOT EXISTS assets
        AS SELECT * 
        FROM read_csv_auto('data/assets.csv')
    """)

    print('데이터베이스 저장 완료')

if __name__ == "__main__":
    ft.run(main)

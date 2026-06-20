from pathlib import Path
import flet as ft

from repositories.cookie_repository import (
    get_elements,
    get_cookies_by_element,
    get_cookie_basic_info_with_skills,
    get_recommended_items,
    get_recommended_artifacts,
    get_recommended_siegeknights,
    get_potential_table_rows,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


# DB에 저장된 이미지 상대경로를 실제 파일 경로로 변환하는 함수
def resolve_image_src(image_path):
    if image_path is None:
        return None

    image_path = str(image_path).strip()

    if image_path == "":
        return None

    path_obj = Path(image_path)

    if path_obj.is_absolute():
        if path_obj.exists():
            return str(path_obj)
        return None

    # CSV에는 Cookie/파일명.png처럼 저장되어 있으므로 data 폴더 기준으로 찾음
    data_path = DATA_DIR / image_path
    if data_path.exists():
        return str(data_path)

    # 혹시 프로젝트 루트 기준 경로로 저장된 경우도 확인
    root_path = BASE_DIR / image_path
    if root_path.exists():
        return str(root_path)

    print("[WARN] 이미지 파일을 찾을 수 없음:", image_path)
    return None


# 이미지 경로가 있으면 이미지를 출력하고, 없으면 빈 영역만 반환
def make_image_only(image_path, width=80, height=80):
    src = resolve_image_src(image_path)

    if src is None:
        return ft.Container(width=width, height=height)

    return ft.Image(
        src=src,
        width=width,
        height=height,
    )


def make_title_text(text, size=22):
    return ft.Text(
        text,
        size=size,
        weight=ft.FontWeight.BOLD,
    )


def make_small_text(text):
    return ft.Text(
        text,
        size=13,
        color=ft.Colors.BLUE_GREY_700,
    )


# 각 기능 영역을 하나의 카드형 패널로 만드는 함수
def make_panel(title, content_controls, subtitle=None):
    title_controls = [
        make_title_text(title, size=21),
    ]

    if subtitle is not None and str(subtitle).strip() != "":
        title_controls.append(make_small_text(subtitle))

    return ft.Container(
        content=ft.Column(
            [
                ft.Column(title_controls, spacing=2),
                ft.Divider(),
                *content_controls,
            ],
            spacing=10,
        ),
        padding=18,
        border_radius=16,
        bgcolor=ft.Colors.WHITE,
    )


# 스킬처럼 제목과 설명이 함께 필요한 항목을 카드로 출력
def make_text_card(title, body):
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                ft.Text(body, size=14, selectable=True),
            ],
            spacing=6,
        ),
        padding=14,
        border_radius=12,
        bgcolor=ft.Colors.BLUE_GREY_50,
    )


# 추천 장비, 추천 시즈나이트처럼 순위와 이름만 필요한 항목을 카드로 출력
def make_rank_card(rank_title, name_text):
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(rank_title, size=14, color=ft.Colors.BLUE_GREY_700),
                ft.Text(name_text, size=17, weight=ft.FontWeight.BOLD),
            ],
            spacing=4,
        ),
        padding=14,
        border_radius=12,
        bgcolor=ft.Colors.BLUE_GREY_50,
    )


# 아티팩트는 이미지가 있으므로 이미지와 이름을 함께 출력
def make_artifact_card(title, body, image_path):
    return ft.Container(
        content=ft.Row(
            [
                make_image_only(image_path, width=86, height=86),
                ft.Column(
                    [
                        ft.Text(title, size=14, color=ft.Colors.BLUE_GREY_700),
                        ft.Text(body, size=17, weight=ft.FontWeight.BOLD, selectable=True),
                    ],
                    spacing=6,
                    expand=True,
                ),
            ],
            spacing=14,
        ),
        padding=14,
        border_radius=12,
        bgcolor=ft.Colors.BLUE_GREY_50,
    )


# 장비별 잠재력 추천 정보를 표 형태로 생성
def make_potential_table(potential_names, potential_rows):
    if not potential_rows:
        return ft.Text("추천 잠재력 정보 없음")

    header_cells = [
        ft.DataColumn(ft.Text("순위")),
        ft.DataColumn(ft.Text("장비")),
    ]

    # 잠재력 종류 8개를 표의 열로 추가
    for name in potential_names:
        header_cells.append(ft.DataColumn(ft.Text(str(name))))

    data_rows = []

    # 장비별 추천 잠재력 개수를 행 단위로 추가
    for row in potential_rows:
        cells = [
            ft.DataCell(ft.Text(str(row["rank"]))),
            ft.DataCell(ft.Text(str(row["item_name"]))),
        ]

        for count in row["counts"]:
            cells.append(ft.DataCell(ft.Text(str(count))))

        data_rows.append(ft.DataRow(cells=cells))

    return ft.Container(
        content=ft.Row(
            [
                ft.DataTable(
                    columns=header_cells,
                    rows=data_rows,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=8,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=12,
    )


def main(page: ft.Page):
    page.title = "쿠키런 모험의 탑 세팅 가이드"
    page.padding = 24
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = ft.Colors.BLUE_GREY_50

    # 속성 목록은 앱 실행 시 한 번 조회
    elements = get_elements()
    print("[DEBUG] elements:", elements)

    selected_element_text = ft.Text(
        "속성을 선택하세요.",
        size=14,
        color=ft.Colors.BLUE_GREY_700,
    )

    selected_cookie_text = ft.Text(
        "쿠키를 선택하면 추천 세팅이 표시됩니다.",
        size=14,
        color=ft.Colors.BLUE_GREY_700,
    )

    cookie_dropdown = ft.Dropdown(
        label="쿠키 선택",
        width=340,
        options=[],
        disabled=True,
    )

    # 쿠키 기본 정보 왼쪽 영역
    # 쿠키 이미지, 쿠키 이름, 속성, 포지션을 표시
    cookie_basic_left = ft.Column(
        [
            make_image_only(None, width=560, height=560),
            ft.Text(
                "먼저 속성을 선택하세요.",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                "",
                size=16,
                selectable=True,
                text_align=ft.TextAlign.CENTER,
            ),
        ],
        spacing=8,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # 쿠키 기본 정보 오른쪽 영역에 들어갈 스킬 목록
    skill_list = ft.Column(spacing=10)

    # 쿠키 기본 정보 패널 내부 배치
    # 왼쪽은 쿠키 이미지 중심, 오른쪽은 스킬 정보
    cookie_basic_area = ft.Row(
        [
            ft.Container(
                content=cookie_basic_left,
                expand=2,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("스킬 정보", size=19, weight=ft.FontWeight.BOLD),
                        skill_list,
                    ],
                    spacing=10,
                ),
                expand=1,
                padding=8,
                border_radius=12,
                bgcolor=ft.Colors.BLUE_GREY_50,
            ),
        ],
        spacing=24,
    )

    item_list = ft.Column(spacing=10)
    potential_area = ft.Column(spacing=10)
    artifact_list = ft.Column(spacing=10)
    siegeknight_list = ft.Column(spacing=10)

    # 쿠키 선택 후 쿠키 기본 정보 영역을 갱신
    def set_cookie_info(cookie_image, cookie_name_text, detail_text):
        cookie_basic_left.controls.clear()

        cookie_basic_left.controls.append(
            make_image_only(cookie_image, width=560, height=560)
        )

        cookie_basic_left.controls.append(
            ft.Text(
                cookie_name_text,
                size=30,
                weight=ft.FontWeight.BOLD,
                selectable=True,
                text_align=ft.TextAlign.CENTER,
            )
        )

        cookie_basic_left.controls.append(
            ft.Text(
                detail_text,
                size=17,
                selectable=True,
                text_align=ft.TextAlign.CENTER,
            )
        )

    # 속성이나 쿠키를 새로 선택할 때 이전 조회 결과를 초기화
    def clear_result_sections():
        skill_list.controls.clear()
        item_list.controls.clear()
        potential_area.controls.clear()
        artifact_list.controls.clear()
        siegeknight_list.controls.clear()

    # 속성 선택 시 해당 속성의 쿠키 목록을 조회하여 드롭다운에 표시
    def select_element(element_id, element_name):
        print("[DEBUG] select_element:", element_id, element_name)

        selected_element_text.value = f"선택된 속성: {element_name}"
        selected_cookie_text.value = "쿠키를 선택한 뒤 [쿠키 정보 조회] 버튼을 누르세요."

        cookies = get_cookies_by_element(element_id)
        print("[DEBUG] cookies:", cookies)

        cookie_dropdown.options = [
            ft.dropdown.Option(key=str(cookie_id), text=str(cookie_name))
            for cookie_id, cookie_name in cookies
        ]

        cookie_dropdown.value = None
        cookie_dropdown.disabled = len(cookies) == 0

        if len(cookies) == 0:
            set_cookie_info(None, "쿠키 없음", "해당 속성에 등록된 쿠키가 없습니다.")
        else:
            set_cookie_info(None, f"{element_name} 속성", f"쿠키 {len(cookies)}개가 조회되었습니다.")

        clear_result_sections()
        page.update()

    # 속성 선택 카드를 생성
    def make_element_card(element_id, element_name, element_image):
        def on_click(e):
            select_element(str(element_id), element_name)

        return ft.Container(
            content=ft.Column(
                [
                    make_image_only(element_image, width=78, height=78),
                    ft.Text(str(element_name), size=15, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        "선택",
                        on_click=on_click,
                    ),
                ],
                spacing=7,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=12,
            width=130,
            border_radius=16,
            bgcolor=ft.Colors.WHITE,
        )

    # DB에서 조회한 속성 정보를 카드 목록으로 변환
    element_cards = []

    for element_id, element_name, element_image in elements:
        element_cards.append(
            make_element_card(element_id, element_name, element_image)
        )

    # 쿠키 정보 조회 버튼 클릭 시 실행
    # 기본 정보, 스킬, 장비, 잠재력, 아티팩트, 시즈나이트를 모두 조회
    def load_cookie_detail(e):
        selected_cookie_id = cookie_dropdown.value

        print("[DEBUG] load_cookie_detail 실행됨")
        print("[DEBUG] selected_cookie_id:", selected_cookie_id)

        if selected_cookie_id is None or selected_cookie_id == "":
            selected_cookie_text.value = "쿠키를 먼저 선택하세요."
            set_cookie_info(None, "쿠키 미선택", "쿠키를 먼저 선택하세요.")
            clear_result_sections()
            page.update()
            return

        basic_rows = get_cookie_basic_info_with_skills(selected_cookie_id)
        item_rows = get_recommended_items(selected_cookie_id)
        artifact_rows = get_recommended_artifacts(selected_cookie_id)
        siegeknight_rows = get_recommended_siegeknights(selected_cookie_id)
        potential_names, potential_rows = get_potential_table_rows(selected_cookie_id)

        print("[DEBUG] basic rows:", basic_rows)
        print("[DEBUG] item rows:", item_rows)
        print("[DEBUG] artifact rows:", artifact_rows)
        print("[DEBUG] siegeknight rows:", siegeknight_rows)
        print("[DEBUG] potential rows:", potential_rows)

        clear_result_sections()

        if not basic_rows:
            selected_cookie_text.value = "조회 결과가 없습니다."
            set_cookie_info(None, "조회 결과 없음", "조회 결과가 없습니다.")
            page.update()
            return

        # 기본 정보는 모든 스킬 행에 반복되므로 첫 번째 행만 사용
        first_row = basic_rows[0]

        (
            cookie_id,
            cookie_name,
            cookie_image,
            element_name,
            element_image,
            position_name,
            _skill_id,
            _skill_name,
            _skill_description,
        ) = first_row

        selected_cookie_text.value = f"{cookie_name}"

        detail_text = (
            f"속성: {element_name}\n"
            f"포지션: {position_name}"
        )

        set_cookie_info(cookie_image, str(cookie_name), detail_text)

        # 스킬 정보 출력
        # 스킬 종류는 표시하지 않고 스킬 이름과 설명만 사용
        for row in basic_rows:
            (
                _cookie_id,
                _cookie_name,
                _cookie_image,
                _element_name,
                _element_image,
                _position_name,
                _skill_id,
                skill_name,
                skill_description,
            ) = row

            if skill_name is None or str(skill_name).strip() == "":
                skill_name = "스킬 이름 미입력"

            if skill_description is None or str(skill_description).strip() == "":
                skill_description = "스킬 설명은 추후 추가 예정입니다."

            skill_list.controls.append(
                make_text_card(
                    str(skill_name),
                    str(skill_description),
                )
            )

        # 추천 장비 출력
        if item_rows:
            for row in item_rows:
                (
                    _cookie_id,
                    _cookie_name,
                    _item_id,
                    item_name,
                    item_rank,
                ) = row

                item_list.controls.append(
                    make_rank_card(
                        f"{item_rank}순위 장비",
                        item_name,
                    )
                )
        else:
            item_list.controls.append(ft.Text("추천 장비 정보 없음"))

        # 장비별 잠재력 표 출력
        potential_area.controls.append(
            make_potential_table(potential_names, potential_rows)
        )

        # 추천 아티팩트 출력
        if artifact_rows:
            for row in artifact_rows:
                (
                    _cookie_id,
                    _cookie_name,
                    _artifact_id,
                    artifact_name,
                    artifact_image,
                    artifact_rank,
                ) = row

                artifact_list.controls.append(
                    make_artifact_card(
                        f"{artifact_rank}순위 아티팩트",
                        artifact_name,
                        artifact_image,
                    )
                )
        else:
            artifact_list.controls.append(ft.Text("추천 아티팩트 정보 없음"))

        # 추천 시즈나이트 출력
        if siegeknight_rows:
            for row in siegeknight_rows:
                (
                    _cookie_id,
                    _cookie_name,
                    _siegeknight_id,
                    siegeknight_name,
                    siegeknight_rank,
                ) = row

                siegeknight_list.controls.append(
                    make_rank_card(
                        f"{siegeknight_rank}순위 시즈나이트",
                        siegeknight_name,
                    )
                )
        else:
            siegeknight_list.controls.append(ft.Text("추천 시즈나이트 정보 없음"))

        page.update()

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "쿠키런 모험의 탑 세팅 가이드",
                        size=34,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Cookie Setting Guide",
                        size=14,
                        color=ft.Colors.BLUE_GREY_700,
                    ),
                ],
                spacing=2,
            ),
            padding=22,
            border_radius=20,
            bgcolor=ft.Colors.WHITE,
        ),

        make_panel(
            "1. 속성 선택",
            [
                ft.Text("조회하려는 속성을 선택하세요.", size=14),
                ft.Row(
                    element_cards,
                    spacing=14,
                    wrap=True,
                ),
                selected_element_text,
            ],
        ),

        make_panel(
            "2. 쿠키 선택",
            [
                ft.Row(
                    [
                        cookie_dropdown,
                        ft.ElevatedButton("쿠키 정보 조회", on_click=load_cookie_detail),
                    ],
                    spacing=16,
                ),
                selected_cookie_text,
            ],
        ),

        make_panel(
            "3. 쿠키 기본 정보",
            [
                cookie_basic_area,
            ],
        ),

        make_panel(
            "4. 추천 장비",
            [
                item_list,
            ],
        ),

        make_panel(
            "5. 장비별 추천 잠재력",
            [
                potential_area,
            ],
        ),

        make_panel(
            "6. 추천 아티팩트",
            [
                artifact_list,
            ],
        ),

        make_panel(
            "7. 추천 시즈나이트",
            [
                siegeknight_list,
            ],
        ),
    )


if __name__ == "__main__":
    ft.run(main)
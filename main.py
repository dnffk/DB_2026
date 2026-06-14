import flet as ft
from repositories.cookie_repository import (
    get_elements,
    get_cookies_by_element,
    get_cookie_basic_info_with_skills,
)


def get_skill_type(skill_id):
    skill_type_map = {
        1: "기본공격",
        2: "특수스킬",
        3: "궁극기",
        4: "패시브",
    }

    try:
        skill_id = int(skill_id)
    except Exception:
        return "스킬"

    return skill_type_map.get(skill_id, "스킬")


def main(page: ft.Page):
    page.title = "쿠키런 모험의 탑 세팅 가이드"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    elements = get_elements()
    print("[DEBUG] elements:", elements)

    title = ft.Text("쿠키 기본 정보 조회", size=26, weight=ft.FontWeight.BOLD)

    debug_text = ft.Text("상태: 대기 중", size=13, color=ft.Colors.BLUE_GREY_700)

    element_dropdown = ft.Dropdown(
        label="속성 선택",
        width=250,
        options=[
            ft.dropdown.Option(key=str(element_id), text=str(element_name))
            for element_id, element_name in elements
        ],
    )

    cookie_dropdown = ft.Dropdown(
        label="쿠키 선택",
        width=250,
        options=[],
        disabled=True,
    )

    cookie_info_text = ft.Text("속성을 선택한 뒤 [쿠키 목록 불러오기] 버튼을 누르세요.", size=16)
    skill_list = ft.Column(spacing=10)

    def load_cookies(e):
        selected_element_id = element_dropdown.value

        print("[DEBUG] load_cookies 실행됨")
        print("[DEBUG] selected_element_id:", selected_element_id)

        if selected_element_id is None or selected_element_id == "":
            debug_text.value = "상태: 속성을 먼저 선택해야 합니다."
            cookie_info_text.value = "속성을 먼저 선택하세요."
            cookie_dropdown.options = []
            cookie_dropdown.value = None
            cookie_dropdown.disabled = True
            skill_list.controls.clear()
            page.update()
            return

        cookies = get_cookies_by_element(selected_element_id)

        print("[DEBUG] cookies:", cookies)

        cookie_dropdown.options = [
            ft.dropdown.Option(key=str(cookie_id), text=str(cookie_name))
            for cookie_id, cookie_name in cookies
        ]

        cookie_dropdown.value = None
        cookie_dropdown.disabled = len(cookies) == 0

        debug_text.value = f"상태: 속성 ID {selected_element_id}, 쿠키 {len(cookies)}개 조회됨"

        if len(cookies) == 0:
            cookie_info_text.value = "해당 속성에 등록된 쿠키가 없습니다."
        else:
            cookie_info_text.value = "쿠키를 선택한 뒤 [쿠키 정보 조회] 버튼을 누르세요."

        skill_list.controls.clear()
        page.update()

    def load_cookie_detail(e):
        selected_cookie_id = cookie_dropdown.value

        print("[DEBUG] load_cookie_detail 실행됨")
        print("[DEBUG] selected_cookie_id:", selected_cookie_id)

        if selected_cookie_id is None or selected_cookie_id == "":
            debug_text.value = "상태: 쿠키를 먼저 선택해야 합니다."
            cookie_info_text.value = "쿠키를 먼저 선택하세요."
            skill_list.controls.clear()
            page.update()
            return

        rows = get_cookie_basic_info_with_skills(selected_cookie_id)

        print("[DEBUG] joined rows:", rows)

        skill_list.controls.clear()

        if not rows:
            debug_text.value = "상태: 조회 결과 없음"
            cookie_info_text.value = "조회 결과가 없습니다."
            page.update()
            return

        first_row = rows[0]
        cookie_id, cookie_name, element_name, position_name, _, _, _ = first_row

        debug_text.value = f"상태: {cookie_name} 조회 완료"

        cookie_info_text.value = (
            f"쿠키 ID: {cookie_id}\n"
            f"쿠키 이름: {cookie_name}\n"
            f"속성: {element_name}\n"
            f"포지션: {position_name}"
        )

        for row in rows:
            _, _, _, _, skill_id, skill_name, skill_description = row

            skill_type = get_skill_type(skill_id)

            if skill_name is None or str(skill_name).strip() == "":
                skill_name = "스킬 이름 미입력"

            if skill_description is None or str(skill_description).strip() == "":
                skill_description = "스킬 설명은 추후 추가 예정입니다."

            skill_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                f"[{skill_type}] {skill_name}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(str(skill_description), size=14),
                        ],
                        spacing=4,
                    ),
                    padding=12,
                    border_radius=8,
                )
            )

        page.update()

    page.add(
        title,
        ft.Text(
            "cookie, element, position, skill 테이블을 JOIN하여 쿠키 기본 정보를 조회합니다.",
            size=14,
        ),
        debug_text,
        ft.Divider(),
        ft.Row(
            [
                element_dropdown,
                ft.ElevatedButton("쿠키 목록 불러오기", on_click=load_cookies),
            ],
            spacing=20,
        ),
        ft.Row(
            [
                cookie_dropdown,
                ft.ElevatedButton("쿠키 정보 조회", on_click=load_cookie_detail),
            ],
            spacing=20,
        ),
        ft.Divider(),
        ft.Text("조회 결과", size=20, weight=ft.FontWeight.BOLD),
        cookie_info_text,
        ft.Divider(),
        ft.Text("스킬 정보", size=20, weight=ft.FontWeight.BOLD),
        skill_list,
    )


if __name__ == "__main__":
    ft.run(main)
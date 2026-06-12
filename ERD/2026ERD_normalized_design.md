# 2026 ERD - 정규화된 테이블 설계

## 1. 핵심 테이블

### Cookie
- `cookie_id` INT PK
- `cookie_name` VARCHAR
- `cookie_image` VARCHAR
- `element_id` INT FK -> Element(Element_id)
- `position_id` INT FK -> Position(Position_id)
- `skill_primary_id` INT FK -> Skill(Skill_id)  # 기본 공격 or 대표 스킬 선택용
- `skill_ultimate_id` INT FK -> Skill(Skill_id)  # 궁극기 등 구분이 필요하면 추가

### Element
- `element_id` INT PK
- `element_name` VARCHAR
- `element_image` VARCHAR

### Position
- `position_id` INT PK
- `position_name` VARCHAR

### Skill
- `skill_id` INT PK
- `cookie_id` INT FK -> Cookie(cookie_id)
- `skill_type` VARCHAR
- `skill_name` VARCHAR
- `skill_description` TEXT

### Artifact
- `artifact_id` INT PK
- `artifact_name` VARCHAR
- `artifact_image` VARCHAR

### Item
- `item_id` INT PK
- `item_name` VARCHAR
- `item_rank` VARCHAR

### Poten (Potential)
- `poten_id` INT PK
- `poten_name` VARCHAR

## 2. 등급/능력치 테이블

### Star
- `star_id` INT PK
- `cookie_id` INT FK -> Cookie(cookie_id)
- `star_level` INT
- `attack_rate` FLOAT
- `defense_rate` FLOAT
- `hp_rate` FLOAT

## 3. 추천 테이블

### Cookie_Artifact_Recommend
- `cookie_id` INT FK -> Cookie(cookie_id)
- `artifact_id` INT FK -> Artifact(artifact_id)
- `artifact_rank` VARCHAR
- PK: (`cookie_id`, `artifact_id`)

### Cookie_Siege_Recommend
- `cookie_id` INT FK -> Cookie(cookie_id)
- `siege_id` INT FK -> Siege(Siege_id)
- `siege_rank` VARCHAR
- PK: (`cookie_id`, `siege_id`)

### Cookie_Item_Recommend
- `cookie_id` INT FK -> Cookie(cookie_id)
- `item_id` INT FK -> Item(item_id)
- `item_rank` VARCHAR
- PK: (`cookie_id`, `item_id`)

### Cookie_Poten_Recommend_Type
- `cookie_id` INT FK -> Cookie(cookie_id)
- `poten_id` INT FK -> Poten(poten_id)
- `poten_rank` VARCHAR
- PK: (`cookie_id`, `poten_id`)

### Cookie_Poten_Recommend_Count
- `cookie_id` INT FK -> Cookie(cookie_id)
- `poten_type_id` INT FK -> Poten(poten_id)
- `poten_count` INT
- PK: (`cookie_id`, `poten_type_id`)

## 4. 추가 추천/조합 테이블

### Team_Recommendation
- `team_recommendation_id` INT PK
- `content_stage_id` INT FK -> Content_Stage(content_stage_id)
- `recommendation_name` VARCHAR

### Team_Recommendation_Cookie
- `team_recommendation_id` INT FK -> Team_Recommendation(team_recommendation_id)
- `cookie_id` INT FK -> Cookie(cookie_id)
- PK: (`team_recommendation_id`, `cookie_id`)

## 5. 컨텐츠 기반 테이블

### Content
- `content_id` INT PK
- `content_name` VARCHAR

### Content_Stage
- `content_stage_id` INT PK
- `content_id` INT FK -> Content(content_id)
- `element_id` INT FK -> Element(element_id)
- `stage_name` VARCHAR

## 6. 설계 정리

- `Cookie`는 `Element`, `Position`을 참조하는 중심 테이블입니다.
- `Skill`은 `Cookie`에 종속된 1:N 관계입니다.
- 추천 정보는 각 추천 대상별로 별도 교차 테이블 형태로 유지합니다.
- ERD 도구에서 관계선 텍스트를 컬럼으로 쓰지 않도록 제거해야 합니다.

## 7. 구현 제안

- `Cookie`와 `Skill` 간 관계는 `cookie_id`를 `Skill`에 둔 1:N 구조가 자연스럽습니다.
- `Artifact_recommend`, `Item_recommend`, `Poten_recommend_type`, `Poten_recommend_count`를 각각 별도 교차 테이블로 정리하면 확장성과 무결성 유지가 쉽습니다.
- `Poten`은 `Potential`로 표기하고, `poten_id`, `poten_name`으로 명확히 관리하세요.

---

이 설계는 현재 ERD에서 누락된 FK 관계 및 잘못된 관계 컬럼을 제거하고, 추천 데이터를 명확히 표현하도록 정리한 것입니다.
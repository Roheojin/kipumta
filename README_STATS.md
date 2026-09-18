# kipumta 통계 기능 - SQL 스키마 그대로 쓰는 버전 (pandas)

지난 번엔 Supabase에 SQL 뷰/함수를 추가하는 방식으로 만들었는데, 이번엔 방금 주신
`SCHEMA_kiwoom_create_query.txt` 스키마를 **하나도 바꾸지 않고**, `study_history_user_time`
인덱스 `(user_id, start_time DESC)`를 그대로 타는 조회만 파이썬에서 하고, 통계 계산은
전부 pandas로 처리하도록 다시 짰습니다. SQL 마이그레이션이 필요 없습니다.

## 파일 구성

| 파일 | 상태 | 설명 |
|---|---|---|
| `db.py` | 수정 | 기존 함수는 그대로 두고, 통계용 조회 함수 3개 추가 |
| `stats.py` | **신규** | pandas로 집계 + matplotlib 시각화, 2-1/2-2 메뉴 |
| `chart_style.py` | **신규** | 차트 색상/폰트 공통 설정 (색약 대비 검증된 고정 팔레트) |
| `main.py` | 수정 | "통계 기능은 준비 중입니다" 자리를 `stats_menu()` 호출로 교체 |
| `study.py`, `users.py` | 원본 그대로 | 비교 편의를 위해 같이 넣었습니다 |
| `SCHEMA_kiwoom_create_query.txt` | 원본 그대로 | 참고용, 바뀐 것 없음 |
| `example_output/` | 예시 | 가짜 데이터로 미리 만들어 본 차트 (실제 실행 결과물 아님) |

## db.py에 추가한 함수 3개

```python
get_my_study_history(user_id)   # study_history WHERE user_id = ? (완료분만) ORDER BY start_time DESC
get_all_study_history()          # study_history 전체 (완료분만) - 비교/리더보드용
get_all_nicknames()               # user_info 전체 - 비교 결과에 닉네임 붙이는 용도
```

첫 번째 함수가 정확히 `study_history_user_time (user_id, start_time DESC)` 인덱스를
그대로 쓰는 조회입니다(`user_id`로 걸러서 `start_time DESC`로 정렬). `study_minutes`
같은 별도 컬럼 없이, `end_time - start_time`을 파이썬에서 계산합니다.

## stats.py가 하는 일

- **개인 통계**: 내 기록을 받아와 pandas로 과목별/날짜별로 묶어서 합계 → 막대그래프
  (과목별 공부 시간) + 선그래프(최근 추이)
- **통계 비교**: 전체 기록을 받아와 사용자별로 합계 → 내 순위/전체 평균 계산,
  상위 10명 리더보드 → 막대그래프(나 vs 평균) + 가로막대(리더보드, 내 막대만 강조)

전체 사용자 기록을 한 번에 다 받아와서 파이썬에서 집계하는 방식이라, 사용자/기록이
아주 많아지면 (수만 건 이상) 느려질 수 있습니다. 지금 규모(수업 프로젝트)에서는
문제 없고, 나중에 느려지면 그때 SQL 쪽에서 집계하는 방식으로 바꾸면 됩니다.

## 적용 방법

1. SQL은 그대로 두고, 저장소의 `db.py`, `main.py`를 이 폴더 것으로 교체(또는 diff 반영)하고
   `stats.py`, `chart_style.py`를 같은 폴더에 추가합니다.
2. `pip install pandas matplotlib`
3. `python main.py` → 로그인 → "2. 통계보기" → "1. 개인 통계" / "2. 통계 비교"

## 검증한 내용

실제 Supabase에는 접속할 수 없어서, `supabase` 클라이언트를 파이썬에서 가짜 객체로
바꿔치기하고 아래와 같은 가짜 데이터를 흘려보내 확인했습니다.

- 나(190분: 수학 150 + 영어 40), 철수(200분), 영희(30분) → 전체 평균 140분,
  내 순위 2위 / 전체 3명 — 손으로 계산한 값과 정확히 일치
- 기록이 없는 신규 유저로 호출했을 때 에러 없이 안내 메시지만 나오는 것도 확인
- 실제 supabase-py(`postgrest`) 라이브러리를 설치해서 `get_my_study_history()`가 만드는
  쿼리가 `user_id=eq....&end_time=not.is.null&order=start_time.desc`로 나가는 것도
  직접 확인했습니다 (인덱스를 타는 형태 맞음).

`example_output/`의 두 PNG가 이 테스트에서 나온 결과물입니다. 실제 프로젝트에
붙인 뒤 한 번은 직접 실행해서 확인해 보시는 걸 권장합니다.

## 참고 (이전에 알려드렸던 것, 수정 완료)

`min` 브랜치의 `end_session()`은 세션 종료 시 `study_minutes` 컬럼에도 값을 저장하려
했는데, 스키마엔 이 컬럼이 없어서 종료할 때마다 `"공부 종료 저장 오류"`가 찍히고
세션이 저장되지 않았습니다. 통계 계산은 `end_time - start_time`으로 직접 계산하므로
이 컬럼이 필요 없어서, `end_session()`의 update에서 `study_minutes` 필드를 제거해
해결했습니다 (`db.py`).

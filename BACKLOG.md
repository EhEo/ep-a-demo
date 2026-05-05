# BACKLOG

---

## Task 1: FastAPI dependency injection 변경 검토

**상태**: 완료

**배경**:
프로젝트가 FastAPI 0.110 → 0.115 로 업그레이드 중. dependency injection 패턴이 일부 변경됐다는 changelog 언급이 있음. 본 task 는:

1. 현재 코드의 DI 사용 패턴 파악
2. 0.115 의 변경점 확인
3. 마이그레이션 영향 평가 + verdict (SHIP / NEEDS-FIX / DISCUSS)

**검토 대상**:
- `app/dependencies.py` — `get_db()` yield-fixture 패턴
- `app/routers/items.py` — `Depends(get_db)` 사용처 (pre-Annotated 스타일)
- `requirements.txt` — `fastapi==0.110.0` 핀

---

## Task 2: pytest 7 → 8 마이그레이션

**상태**: 완료

**배경**: pytest 7.x → 8.x 의 deprecation 경고 정리. 8.x 로 올렸을 때 fixture / config 변경이 필요한지 확인.

**검토 대상**:
- `tests/conftest.py` — `@pytest.fixture(scope="function")` 사용처
- `tests/test_items.py` — 단순 client fixture 소비
- `pytest.ini` — `asyncio_mode = auto` 등 옵션
- `requirements.txt` — `pytest==7.4.0` 핀

---

## Task 3: requirements.txt 의존성 정기 audit

**상태**: 완료

**배경**: Task 1/2 처럼 마이그레이션이 밀려서 한 번에 처리하지 않도록, 의존성 상태를 정기적으로 점검. CVE / EOL / major version drift 를 조기에 잡아 마이그레이션 비용을 분산한다.

**검토 대상**:
- `requirements.txt` — 모든 핀 (fastapi, pytest, pytest-asyncio, uvicorn, httpx)
- 각 패키지의 최신 stable 버전 / 보안 권고 / deprecation 노트
- 출력물: 현재 핀 vs 최신 + 권장 액션 (immediate upgrade / monitor / no-op) 표

**주기**: 분기 1 회 (또는 보안 권고 트리거 시)

**1차 audit 결과 요약 (2026-05-05)**:
- 즉시 액션: `fastapi==0.115.0` → `fastapi>=0.115.4,<0.116` (commit `cf5124d`, CVE-2024-47874 / Starlette MultiPart DoS, GHSA 확인)
- 후속 follow-up 분리: 핀 정책 / lock 파일 부재 → Task 4
- monitor: pytest 9, uvicorn 0.46, httpx 0.28 등 major drift — 향후 라운드에서 별도 마이그 task 로 분리

---

## Task 4: 핀 정책 통일

**상태**: 완료

**배경**: Task 3 의 1차 audit 에서 Codex 가 핀 위생 NEEDS-FIX 두 건을 발견:
1. `requirements.txt` 핀 스타일 혼재 (`==` 와 상한 없는 `>=` 가 섞여 있음) → 정책 불명확
2. lock/constraints 파일 없음 → starlette/pydantic/anyio 등 transitive dep 가 설치 시점마다 변동 → 정기 audit 결과 재현 어려움

**처리 결과 (2026-05-05)**:
- Codex 가 본 task 의 원래 scope (pin 정책 + lock 도구 선택 + lock 산출물 추가 + README 갱신) 에 대해 verdict **DISCUSS** — demo repo 규모 대비 과함. lock 도구 후보 (uv/Poetry/PDM/Hatch) 는 pyproject.toml 도입 = packaging 구조 변경이라 별도 task 로 분리 권장.
- 본 task scope 를 **핀 정책 통일** 만으로 좁히고, lock 산출물 도입은 Task 5 로 분리.

**확정된 핀 정책**:
- *입력 파일* (`requirements.txt`) = 직접 의존성에 호환 상한 명시 (`>=X,<NextMajor`). 단일 정책으로 통일.
- *lock 산출물* (도입 시) = transitive 까지 exact pin (`==`). 입력 정책과 별 레이어로 관리.
- 근거: lock 을 도입하면 두 레이어가 다른 역할을 하므로 단일 정책으로 묶을 이유 없음 (Codex 지적, Gemini packaging.python.org 가이드와 일치).

**적용된 변경**:
- commit `36e7f00` — `uvicorn`, `httpx`, `pytest-asyncio` 에 next-major 상한 부여
- commit `cf5124d` — `fastapi` CVE 패치 (Task 3 작업물, 본 task 와 동일 정책 적용)
- 결과: 모든 직접 의존성이 `>=X,<NextMajor` 형식으로 통일됨

---

## Task 5: lock 산출물 도입 (Task 4 분리)

**상태**: 대기

**배경**: Task 4 에서 분리. Task 3 audit 의 재현성 목표를 만족시키려면 transitive dep 까지 고정한 lock 산출물이 필요. 핀 정책 (Task 4) 은 이미 통일됐으므로, 이 task 는 *도구 선택 + 산출물 도입* 만 다룸.

**Codex 권고로 좁힌 후보**:
- A. `pip-compile` (pip-tools): `requirements.in` 추가 → 컴파일된 `requirements.txt` 가 산출물. 기존 형상 거의 유지.
- B. `constraints.txt`: 별도 파일로 transitive 까지 exact pin. 추가 도구 없이 `pip install -r requirements.txt -c constraints.txt` 로 사용. 가장 가벼움.

`uv lock` / Poetry / PDM / Hatch 는 pyproject.toml 도입을 동반하므로 본 task 에서 제외 — 필요 시 별도 "packaging 모던화" task 로 분리.

**작업 대상**:
- 도구 선택 (A 또는 B)
- 산출물 생성 + 커밋
- `README.md` 의 setup 안내에 `python -m venv .venv` / `pip install -r requirements.txt` / `pytest` 흐름 + lock 재생성 명령 추가
- `.gitignore` 에 도구별 캐시 (필요 시) 추가

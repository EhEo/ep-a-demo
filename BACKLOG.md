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

## Task 4: 핀 정책 통일 + lock/constraints 도입

**상태**: 대기

**배경**: Task 3 의 1차 audit 에서 Codex 가 핀 위생 NEEDS-FIX 두 건을 발견:
1. `requirements.txt` 핀 스타일 혼재 (`==` 와 상한 없는 `>=` 가 섞여 있음) → 정책 불명확
2. lock/constraints 파일 없음 → starlette/pydantic/anyio 등 transitive dep 가 설치 시점마다 변동 → 정기 audit 결과 재현 어려움

**작업 대상**:
- 핀 스타일 정책 결정: 모두 exact pin (`==`) vs 호환 상한 부여 (`>=X,<Y`) 중 택일
- lock 도구 선택: `pip-compile` (`requirements.in` → `requirements.txt`) vs 별도 `constraints.txt` vs `uv lock` 등
- 결정된 정책에 맞춰 `requirements.txt` 재정비 + 도구별 산출물 추가
- `README.md` 의 setup 안내 갱신 (어떤 도구로 lock 재생성하는지)

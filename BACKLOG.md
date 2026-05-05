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

# EP A 실습 — 3-CLI 팀 리뷰 데모

> EP A 영상 라이브 데모를 본인 박스에서 재현. Claude(PM) + Gemini(researcher) + Codex(reviewer) 가 FastAPI 마이그레이션 task 를 어떻게 나눠 처리하는지 직접 보기.

🎬 **영상**: https://youtu.be/ly5CUJwelFc

📦 **Repo**: https://github.com/EhEo/ep-a-demo

**사전 준비**: Claude Code · Codex · Gemini 설치/인증 → [SETUP.md](../SETUP.md)

---

## Step 1. 실습 환경 준비

```bash
git clone https://github.com/pandas-studio/agent-harness-tutorial
cp -r agent-harness-tutorial/ep_a_demo /tmp/ep_a-demo
cd /tmp/ep_a-demo
git init -q && git add . && git commit -q -m "init"
```

`CLAUDE.md` + `.agents-dev/` 존재 확인되면 ✅.

---

## Step 1.5. (선택) 의존성 설치 + 테스트

데모 자체는 Step 2 부터 시작해도 되지만, `app/`/`tests/` 를 직접 돌려볼 거면 venv 에 lock 된 의존성을 설치한다.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest
```

- `requirements.in` — 직접 의존성 입력 (`>=X,<NextMajor` 정책)
- `requirements.txt` — `pip-compile` 산출물 (transitive 까지 exact pin, 재현성 보장)

의존성을 갱신할 때만:

```bash
pip install pip-tools
pip-compile requirements.in -o requirements.txt
```

---

## Step 2. Claude Code 시작

```bash
cd /tmp/ep_a-demo
claude
```

Claude Code 가 `CLAUDE.md` 를 자동 로드 → PM 라우팅 룰 인식. 이제 자연어로 task 를 던지면 Claude 가 알아서 Codex / Gemini 를 호출.

---

## Step 3. BACKLOG Task 1 — 3-CLI 협업 

Claude 세션에 다음 입력:

```
BACKLOG.md Task 1 검토해줘. app/dependencies.py 와 app/routers/items.py 의
FastAPI DI 패턴이 0.115 마이그레이션 필요한지 Codex 한테 review 받고,
0.115 의 Annotated DI 변경점은 Gemini 한테 리서치 시켜줘.
verdict + 마이그레이션 권장사항 정리해줘.
```

Claude 가 자동 수행:
1. `BACKLOG.md` + `app/` 코드 읽기
2. `ask-codex.sh` 호출 → verdict 받기
3. `ask-gemini.sh` 호출 → 공식 문서 확인
4. 두 결과 종합해서 답변

✅ 기대: Claude 가 verdict (SHIP / NEEDS-FIX / DISCUSS) + Annotated 마이그레이션 가이드를 정리한 답.

---

## Step 4. tmux 3-pane — 영상 화면 그대로

```bash
# 1. keybinding.conf 생성 + ~/.tmux.conf 에 등록 (tmux 세션 밖에서)
sed "s|__AGENT_HARNESS_PROJECT__|/tmp/ep_a-demo|g" \
    .agents-dev/tmux/keybinding.conf.template > .agents-dev/tmux/keybinding.conf
echo "source-file /tmp/ep_a-demo/.agents-dev/tmux/keybinding.conf" >> ~/.tmux.conf

# 2. 새 tmux 세션 시작 (→ ~/.tmux.conf 자동 로드)
tmux new-session -s ep-a

# 3. 세션 안에서: Ctrl-b R → 3-pane 자동 분할
#    (Ctrl-b = tmux 기본 prefix. Ctrl-b 먼저 누르고 손 떼고 R)
```

좌측 pane 에서 `claude` 실행 → Step 3 자연어 입력. 우측 dashboard 에 색상 verdict box 등장.

---

## 정리

```bash
rm -rf /tmp/ep_a-demo
sed -i '' '/source-file.*ep_a-demo/d' ~/.tmux.conf
```

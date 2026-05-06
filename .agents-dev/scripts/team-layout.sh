#!/usr/bin/env bash
# team-layout.sh — set up the 3-agent team layout in tmux (psmux compatible).
#
#   ┌─────────────────┬──────────────────┐
#   │                 │  gemini          │
#   │  Claude (PM)    │  dashboard       │
#   │  shell —        ├──────────────────┤
#   │  run 'claude'   │  codex           │
#   │  yourself       │  dashboard       │
#   └─────────────────┴──────────────────┘
set -euo pipefail

# 비대화형 bash에서도 tmux(psmux)를 찾을 수 있도록 PATH 추가
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH:/c/Users/MISTOP/AppData/Local/Microsoft/WinGet/Links"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DASH="$SCRIPT_DIR/dashboard.sh"

SESSION="agents"
HERE=0
ATTACH=1
BYPASS=0

usage() {
  cat <<EOF
Usage: $(basename "$0") [options]
  -n NAME      Session name (default: ${SESSION})
  --here       Apply layout to current tmux window
  --no-attach  Create detached session without attaching
  --bypass     Launch claude with --dangerously-skip-permissions
  -h, --help   Show this help
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    -n) SESSION="$2"; shift 2 ;;
    --here) HERE=1; shift ;;
    --no-attach) ATTACH=0; shift ;;
    --bypass) BYPASS=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

CLAUDE_CMD="claude"
[ "$BYPASS" = "1" ] && CLAUDE_CMD="claude --dangerously-skip-permissions"

command -v tmux >/dev/null 2>&1 || { echo "error: tmux not found. Run: source ~/.bashrc" >&2; exit 2; }
[ -x "$DASH" ] || { echo "error: $DASH not found or not executable" >&2; exit 2; }

# -P -F를 쓰지 않고 split 후 현재 pane이 새 pane이 됨을 이용
if [ "$HERE" = "1" ]; then
  [ -n "${TMUX:-}" ] || { echo "error: --here requires running inside tmux" >&2; exit 2; }
  tmux rename-window "$SESSION" 2>/dev/null || true

  # 오른쪽으로 분할 → Gemini pane이 현재 pane
  tmux split-window -h -c "$REPO_DIR"
  tmux send-keys "/usr/bin/bash '$DASH' gemini" Enter

  # 오른쪽을 다시 아래로 분할 → Codex pane이 현재 pane
  tmux split-window -v -c "$REPO_DIR"
  tmux send-keys "/usr/bin/bash '$DASH' codex" Enter

  # 왼쪽 메인 pane으로 이동
  tmux select-pane -L
  if [ "$BYPASS" = "1" ]; then
    tmux send-keys "$CLAUDE_CMD" Enter
    echo "✓ Layout ready (team: ${SESSION}). Launched: $CLAUDE_CMD"
  else
    echo "✓ Layout ready (team: ${SESSION}). Run 'claude' here."
  fi
  exit 0
fi

if tmux has-session -t "$SESSION" >/dev/null 2>&1; then
  echo "Session '$SESSION' already exists — attaching."
else
  # 새 세션 생성 (단순 플래그만 사용)
  tmux new-session -d -s "$SESSION" -c "$REPO_DIR"

  # 오른쪽으로 분할 → Gemini pane
  tmux split-window -h -t "$SESSION" -c "$REPO_DIR"
  tmux send-keys -t "$SESSION" "/usr/bin/bash '$DASH' gemini" Enter

  # 오른쪽을 아래로 분할 → Codex pane
  tmux split-window -v -t "$SESSION" -c "$REPO_DIR"
  tmux send-keys -t "$SESSION" "/usr/bin/bash '$DASH' codex" Enter

  # 메인(왼쪽) pane으로 이동
  tmux select-pane -t "$SESSION" -L
  if [ "$BYPASS" = "1" ]; then
    tmux send-keys -t "$SESSION" "$CLAUDE_CMD" Enter
  fi
fi

if [ "$ATTACH" = "1" ]; then
  if [ -n "${TMUX:-}" ]; then
    tmux switch-client -t "$SESSION"
  else
    tmux attach -t "$SESSION"
  fi
else
  MSG="✓ Session '$SESSION' ready. Attach with: tmux attach -t $SESSION"
  [ "$BYPASS" = "1" ] && MSG="$MSG  (bypass: $CLAUDE_CMD)"
  echo "$MSG"
fi

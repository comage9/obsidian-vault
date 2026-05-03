---
name: opencode
description: "Delegate coding to OpenCode CLI (features, PR review)."
version: 1.2.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, OpenCode, Autonomous, Refactoring, Code-Review]
    related_skills: [claude-code, codex, hermes-agent]
---

# OpenCode CLI

Use [OpenCode](https://opencode.ai) as an autonomous coding worker orchestrated by Hermes terminal/process tools. OpenCode is a provider-agnostic, open-source AI coding agent with a TUI and CLI.

## When to Use

- User explicitly asks to use OpenCode
- You want an external coding agent to implement/refactor/review code
- You need long-running coding sessions with progress checks
- You want parallel task execution in isolated workdirs/worktrees
- **Delegating coding tasks to a subagent via ACP server mode (for Hermes Agent orchestration)**

## API Key Setup (Multi-Provider Fallback)

OpenCode supports multiple AI providers with automatic fallback.

### Provider Priority: OpenRouter (free) → MiniMax (paid)

**OpenRouter API Key** (primary — free tier):
```bash
# Save to config
echo 'export OPENROUTER_API_KEY="sk-or-v1-..."' >> ~/.bashrc
echo '{"apiKey":"sk-or-v1-...","provider":"openrouter"}' > ~/.opencode/config.json
```

**MiniMax API Key** (fallback — for when OpenRouter limits are hit):
```bash
# MiniMax Token Plan key (1500 requests / 5 hours)
# Provider names in OpenCode: "minimax-cn-coding-plan" or "minimax-coding-plan"
# MiniMax does NOT need env var — stored in ~/.local/share/opencode/auth.json by `opencode auth login`
```

### Verify Both Providers
```bash
opencode providers list
# Should show:
# ●  OpenRouter api
# ●  MiniMax Coding Plan (minimaxi.com) api
# ●  MiniMax Coding Plan (minimax.io) api
```

### Switch Provider (Manual Fallback)
When OpenRouter rate limit is hit, switch provider:
```bash
# Option 1: Edit config.json
echo '{"apiKey":"sk-cp-S8sT-...","provider":"minimax-coding-plan"}' > ~/.opencode/config.json

# Option 2: Use minimax-cn-coding-plan (Chinese endpoint)
# Available models: minimax-cn-coding-plan/MiniMax-M2.7
```

### Recommended OpenRouter Free Models
```
openrouter/nvidia/nemotron-3-super-120b-a12b:free   # Best overall
openrouter/google/gemma-3-27b-it:free                # Fast
openrouter/meta-llama/llama-3.3-70b-instruct:free   # Long context
openrouter/minimax/minimax-m2.5:free                 # MiniMax via OpenRouter
```

### ACP Server Mode (for Hermes subagent delegation)
Start OpenCode as a headless server for subagent orchestration:
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
~/.opencode/bin/opencode serve --port 18792
```

Then delegate via Hermes `delegate_task`:
```python
delegate_task(
    goal="Fix HTTP 401 error in kiwoom_api.py",
    toolsets=["terminal", "file"],
    acp_command="opencode",
    acp_args=["--acp", "--stdio"]
)
```

## Prerequisites

- OpenCode installed: `npm i -g opencode-ai@latest` or `brew install anomalyco/tap/opencode`
- Auth configured: `opencode auth login` or set provider env vars (OPENROUTER_API_KEY, etc.)
- Verify: `opencode auth list` should show at least one provider
- Git repository for code tasks (recommended)
- `pty=true` for interactive TUI sessions

## Binary Resolution (Important)

Shell environments may resolve different OpenCode binaries. If behavior differs between your terminal and Hermes, check:

```
terminal(command="which -a opencode")
terminal(command="opencode --version")
```

If needed, pin an explicit binary path:

```
terminal(command="$HOME/.opencode/bin/opencode run '...'", workdir="~/project", pty=true)
```

## One-Shot Tasks

Use `opencode run` for bounded, non-interactive tasks:

```
terminal(command="opencode run 'Add retry logic to API calls and update tests'", workdir="~/project")
```

Attach context files with `-f`:

```
terminal(command="opencode run 'Review this config for security issues' -f config.yaml -f .env.example", workdir="~/project")
```

Show model thinking with `--thinking`:

```
terminal(command="opencode run 'Debug why tests fail in CI' --thinking", workdir="~/project")
```

Force a specific model:

```
terminal(command="opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4", workdir="~/project")
```

## Interactive Sessions (Background)

For iterative work requiring multiple exchanges, start the TUI in background:

```
terminal(command="opencode", workdir="~/project", background=true, pty=true)
# Returns session_id

# Send a prompt
process(action="submit", session_id="<id>", data="Implement OAuth refresh flow and add tests")

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send follow-up input
process(action="submit", session_id="<id>", data="Now add error handling for token expiry")

# Exit cleanly — Ctrl+C
process(action="write", session_id="<id>", data="\x03")
# Or just kill the process
process(action="kill", session_id="<id>")
```

**Important:** Do NOT use `/exit` — it is not a valid OpenCode command and will open an agent selector dialog instead. Use Ctrl+C (`\x03`) or `process(action="kill")` to exit.

### TUI Keybindings

| Key | Action |
|-----|--------|
| `Enter` | Submit message (press twice if needed) |
| `Tab` | Switch between agents (build/plan) |
| `Ctrl+P` | Open command palette |
| `Ctrl+X L` | Switch session |
| `Ctrl+X M` | Switch model |
| `Ctrl+X N` | New session |
| `Ctrl+X E` | Open editor |
| `Ctrl+C` | Exit OpenCode |

### Resuming Sessions

After exiting, OpenCode prints a session ID. Resume with:

```
terminal(command="opencode -c", workdir="~/project", background=true, pty=true)  # Continue last session
terminal(command="opencode -s ses_abc123", workdir="~/project", background=true, pty=true)  # Specific session
```

## Common Flags

| Flag | Use |
|------|-----|
| `run 'prompt'` | One-shot execution and exit |
| `--continue` / `-c` | Continue the last OpenCode session |
| `--session <id>` / `-s` | Continue a specific session |
| `--agent <name>` | Choose OpenCode agent (build or plan) |
| `--model provider/model` | Force specific model |
| `--format json` | Machine-readable output/events |
| `--file <path>` / `-f` | Attach file(s) to the message |
| `--thinking` | Show model thinking blocks |
| `--variant <level>` | Reasoning effort (high, max, minimal) |
| `--title <name>` | Name the session |
| `--attach <url>` | Connect to a running opencode server |

## Procedure

1. Verify tool readiness:
   - `terminal(command="opencode --version")`
   - `terminal(command="opencode auth list")`
2. For bounded tasks, use `opencode run '...'` (no pty needed).
3. For iterative tasks, start `opencode` with `background=true, pty=true`.
4. Monitor long tasks with `process(action="poll"|"log")`.
5. If OpenCode asks for input, respond via `process(action="submit", ...)`.
6. Exit with `process(action="write", data="\x03")` or `process(action="kill")`.
7. Summarize file changes, test results, and next steps back to user.

## PR Review Workflow

OpenCode has a built-in PR command:

```
terminal(command="opencode pr 42", workdir="~/project", pty=true)
```

Or review in a temporary clone for isolation:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && opencode run 'Review this PR vs main. Report bugs, security risks, test gaps, and style issues.' -f $(git diff origin/main --name-only | head -20 | tr '\n' ' ')", pty=true)
```

## Parallel Work Pattern

Use separate workdirs/worktrees to avoid collisions:

```
terminal(command="opencode run 'Fix issue #101 and commit'", workdir="/tmp/issue-101", background=true, pty=true)
terminal(command="opencode run 'Add parser regression tests and commit'", workdir="/tmp/issue-102", background=true, pty=true)
process(action="list")
```

## Session & Cost Management

List past sessions:

```
terminal(command="opencode session list")
```

Check token usage and costs:

```
terminal(command="opencode stats")
terminal(command="opencode stats --days 7 --models anthropic/claude-sonnet-4")
```

## Glob 타임아웃 문제 — 원인と 해결

### 증상
`opencode run`으로 파일 수정을 요청하면 60초 타임아웃 (3,306개 .py 프로젝트에서)

### 원인
OpenCode는 **현재 작업 디렉토리**를Glob 탐색의根部로 사용.
`terminal(workdir="/home/comage/coding/ki-ai-trader")`로 설정하면
모든 .py 파일을 탐색하느라 타임아웃.

### 해결: `--dir`을 opencode 명령 내부에 전달

```bash
# ❌ workdir=/home/comage/coding/ki-ai-trader + 수정 → 60초 타임아웃
terminal(command="opencode run 'Add retry' -f kiwoom_api.py",
         workdir="/home/comage/coding/ki-ai-trader")

# ✅ --dir /tmp를 opencode 명령 내부에 → 32초 성공
terminal(command="opencode run 'Add retry' -f kiwoom_api.py --dir /tmp")
```

### 시나리오별 작동 상태

| 시나리오 | 명령 | 결과 |
|---------|------|------|
| 단순 텍스트 반환 | `opencode run "Return OK"` | ✅ ~8초 |
| 파일 읽기 | `opencode run "Explain..." -f file.py` | ✅ ~20초 |
| 파일 수정 + workdir 파라미터 | `terminal(workdir="큰프로젝트", command="opencode run ... -f file.py")` | ❌ 60초 타임아웃 |
| **파일 수정 + --dir 내부** | `terminal(command="opencode run ... -f file.py --dir /tmp")` | ✅ ~32초 |
| Claude Code print mode | `claude -p "task" --max-turns 3` | ⚠️ 미작동 (API 통신 문제) |

### 권장 워크플로우

1. **Hermes가 직접** — `read_file()`, `grep`으로 파일 읽기/이해
2. **OpenCode에 수정 지시** — `--dir /tmp`를 명령 내부에 포함
```bash
terminal(command="opencode run 'Add 3-retry with backoff to authenticate()' -f kiwoom_api.py --dir /tmp")
```
3. **수정 결과 확인** — `read_file()`으로 검증

## ACP Server Mode — 한계와 실제 원인

### 포트 충돌이 아니다

`opencode serve --port 18792` 실행 시 HermesGateway가 같은 포트를 사용한다는 보고가 있었으나, **실제 포트 상태 확인 결과:**

```
openclaw-gateway (PID 2172) → 18789, 18791 사용 중
18792는 비어있음
OpenCode ACP는 18792에서 정상 Listen 가능
```

**이유:** OpenCode ACP 기본 포트(`--port 0` = 랜덤)가 간혹 18792를 할당받을 수 있고, 그때 다른 프로세스가 잠시 점유하면 충돌처럼 보임.

### 본질적인 한계: Hermes ↔ OpenCode ACP 연결 불가

**둘 다 ACP 서버(Server)라서 직접 연동 불가능:**

| | Hermes ACP | OpenCode ACP |
|---|---|---|
| 역할 | IDE → Hermes 서버 | IDE → OpenCode 서버 |
| 프로토콜 방향 | Zed/JetBrains → Hermes | Zed/JetBrains → OpenCode |
| Hermes 연동 | — | ❌ 불가 |

**ACP로 Hermes → OpenCode 위임은 불가능.** `delegate_task(acp_command="opencode")` 패턴은 작동하지 않음.

### Working 대안: subagent 직접 실행

Hermes에서 OpenCode 위임 시 **ACP 프로토콜 없이 직접 실행:**

```python
# Hermes sessions_spawn으로 subagent 위임 (ACP 아님)
sessions_spawn(
    mode="run",
    runtime="subagent",
    task="키 프로젝트 수정 작업...",
    model="openrouter/nvidia/nemotron-3-super-120b-a12b:free"
)

# 또는 terminal()로 opencode run 직접 실행 (권장)
terminal(command="opencode run '수정 요청' -f 파일경로 --dir /tmp")
```

**참고:** `sessions_spawn`은 OpenClova/OpenCode 연동 패턴이며, Hermes에서는 `delegate_task(mode="run", runtime="subagent")`로 동등한 기능 사용 가능.

## Pitfalls

- Interactive `opencode` (TUI) sessions require `pty=true`. The `opencode run` command does NOT need pty.
- `/exit` is NOT a valid command — it opens an agent selector. Use Ctrl+C to exit the TUI.
- PATH mismatch can select the wrong OpenCode binary/model config.
- If OpenCode appears stuck, inspect logs before killing:
  - `process(action="log", session_id="<id>")`
- Avoid sharing one working directory across parallel OpenCode sessions.
- Enter may need to be pressed twice to submit in the TUI (once to finalize text, once to send).
- **API Authentication Errors**: If `opencode run` fails with `Error: invalid api key` or `Missing Authentication header`, the provider credentials are invalid/missing. Fix with:
  ```bash
  opencode providers list           # Show current providers
  opencode providers auth openrouter  # Re-authenticate
  # or
  opencode providers auth minimax
  ```
- **Permission Denied (question blocked)**: If `opencode run` fails with `permission=[{"permission":"question","pattern":"*","action":"deny"}]`, the permission is blocking all questions. Fix by adding permissions to `~/.config/opencode/opencode.jsonc`:
  ```json
  {
    "$schema": "https://opencode.ai/config.json",
    "permissions": {
      "question": "*",
      "plan": "*",
      "execute": "*"
    },
    // ... rest of config
  }
  ```
  Note: The file must be valid JSONC (no trailing commas, proper brackets). A common mistake is appending to the file with `>>` which can corrupt the JSON structure. Always rewrite the entire file if adding the permissions section.

## Verification

Smoke test:

```
terminal(command="opencode run 'Respond with exactly: OPENCODE_SMOKE_OK'")
```

Success criteria:
- Output includes `OPENCODE_SMOKE_OK`
- Command exits without provider/model errors
- For code tasks: expected files changed and tests pass

## Rules

1. Prefer `opencode run` for one-shot automation — it's simpler and doesn't need pty.
2. Use interactive background mode only when iteration is needed.
3. Always scope OpenCode sessions to a single repo/workdir.
4. For long tasks, provide progress updates from `process` logs.
5. Report concrete outcomes (files changed, tests, remaining risks).
6. Exit interactive sessions with Ctrl+C or kill, never `/exit`.

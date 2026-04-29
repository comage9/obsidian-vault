---
type: 개념
created: 2026-04-28
tags:
  - opencode
  - hermes
  - 연동
  - 코딩-위임
---

# OpenCode-Hermes 연동

## TL;DR

| 방식 | 가능여부 | 비고 |
|------|----------|------|
| ACP 프로토콜 | ❌ | 둘 다 서버라서 불가 |
| MCP 서버 | ❌ | OpenCode는 MCP 클라이언트 |
| **CLI terminal()** | ✅ | **유일한 방법** |

---

## 1. ACP 연동 — 구조적 불가

Hermes ACP와 OpenCode ACP는 **둘 다 서버**라서 직접 연동 불가능.

```
OpenCode (ACP 서버) ← 不能 → Hermes (ACP 서버)
                          ↑
                    IDE가 클라이언트로 연결
```

**포트 18792 충돌은 부차적 문제.** 실제 충돌 없이도 프로토콜 구조상 불가.

---

## 2. MCP 연동 — 불가

OpenCode의 MCP 기능은 **외부 MCP 서버에 연결**하는 것이지,
자신을 MCP 서버로 노출하지 않음.

```jsonc
// OpenCode는 MCP 클라이언트
"mcp": {
  "notebooklm": {  // ← 외부 서버에 접속
    "command": ["notebooklm-mcp"]
  }
}
```

---

## 3. CLI 실행 — 유일한 방법

```bash
terminal(command="opencode run '수정 요청' -f 파일 --dir /tmp")
```

**Glob 타임아웃 문제:** `--dir /tmp`를 명령 내부에 포함해야 함.

| 시나리오 | 결과 |
|---------|------|
| `opencode run '...' --dir /tmp` | ✅ ~32초 |
| workdir에 큰 프로젝트 지정 | ❌ 60초 타임아웃 |

---

## 4. 관련 문서

- [[Wiki-시스템-개요]]
- [[코딩-작업-위임-규칙]]
- OpenCode 스킬: `~/.hermes/skills/autonomous-ai-agents/opencode/SKILL.md`

---

## 5. 다음 단계

- [ ] OpenCode가 stdio MCP 서버 연결 지원 확인
- [ ] Hermes MCP 서버 stdio 모드 검토
- [ ] notebooklm-mcp pydantic 호환성 해결

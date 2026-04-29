# OpenCode-Hermes 연동 검토

**작성일:** 2026-04-28
**검토자:** Hermes Agent
**목적:** OpenCode를 Hermes Agent에서 코딩 위임 도구로 활용可行性 研究

---

## 1. 결론 (요약)

| 방식 | 가능여부 | 비고 |
|------|----------|------|
| ACP 프로토콜 연결 | ❌ | 둘 다 서버라서 불가 |
| MCP 서버 연결 | ❌ | OpenCode MCP는 클라이언트 역할 |
| **CLI terminal() 실행** | ✅ | **유일한 작동 방식** |

---

## 2. ACP 프로토콜 연동 실패 분석

### 문제 현상
```
OpenCode ACP 서버 시작 시 포트 18792 충돌 오류
```

### 실제 원인
**포트 충돌이 아니라 프로토콜 부적합이 본질적인 원인:**

| | Hermes ACP | OpenCode ACP |
|---|---|---|
| **역할** | IDE → Hermes 서버 | IDE → OpenCode 서버 |
| **프로토콜 방향** | Zed/JetBrains → Hermes | Zed/JetBrains → OpenCode |
| **상호 연결** | ❌ 불가 | ❌ 불가 |

**둘 다 ACP 서버(Server)이기 때문에 Hermes가 OpenCode의 클라이언트가 될 수 없음.**

### 포트 상태 실측
```
openclaw-gateway (PID 2172) → 18789, 18791 사용 중
18792는 비어있음 (실제 포트 충돌 아님)
OpenCode serve --port 18792 → 정상 Listen 가능
```

### 결론
ACP 서버 모드는 Hermes ↔ OpenCode 연동에 **구조적으로 부적합**.

---

## 3. MCP 서버 연동 분석

### OpenCode의 MCP 기능
OpenCode의 `mcp` 서브커맨드는 **OpenCode가 외부 MCP 서버에 연결하는 것**:

```jsonc
// ~/.config/opencode/opencode.jsonc
"mcp": {
  "notebooklm": {
    "type": "local",
    "command": ["notebooklm-mcp"],
    "enabled": true
  }
}
```

OpenCode = **MCP 클라이언트** (외부 MCP 서버에 접속하는 역할)
OpenCode ≠ **MCP 서버** (자신을 외부에 노출하지 않음)

### 현재 실패 상태
```
$ opencode mcp list
●  ✗ notebooklm failed
      MCP error -32000: Connection closed
```

**notebooklm-mcp 오류 (pydantic 호환성):**
```
AttributeError: __pydantic_core_schema__
pydantic 2.13.1 설치됨 (fastmcp와 호환성 문제 추정)
```

### 결론
OpenCode를 **MCP 서버로 노출하는 옵션은 없음.**

---

## 4. CLI 실행 방식 (유일한 작동 방안)

### 기본 패턴
```bash
terminal(command="opencode run '수정 요청' -f 파일 --dir /tmp")
```

### Glob 타임아웃 문제 해결
```bash
# ❌ workdir에 큰 프로젝트 → 60초 타임아웃
terminal(command="opencode run '수정' -f kiwoom_api.py", workdir="/home/comage/coding/ki-ai-trader")

# ✅ --dir /tmp 명령 내부에 → 정상 (~32초)
terminal(command="opencode run '수정' -f kiwoom_api.py --dir /tmp")
```

### 시나리오별 작동 상태

| 시나리오 | 결과 |
|---------|------|
| 단순 텍스트 반환 | ✅ ~8초 |
| 파일 읽기 | ✅ ~20초 |
| 파일 수정 + --dir /tmp | ✅ ~32초 |
| 파일 수정 + workdir 큰프로젝트 | ❌ 60초 타임아웃 |

---

## 5. OpenCode 스킬 참조

**스킬 경로:** `~/.hermes/skills/autonomous-ai-agents/opencode/SKILL.md`

### 스킬 내용 요약
- OpenCode CLI를 Hermes terminal/process 도구로 오케스트레이션
- `opencode run` (원샷), `opencode` TUI (대화형) 지원
- 병렬 작업, PR 리뷰 기능 포함
- ACP 서버 모드 문서화되어 있으나 Hermes ↔ OpenCode 연결 불가 명시

### 스킬의 한계
- 모든 코딩 작업 위임이 가능한 것이 아님
- 큰 프로젝트에서 Glob 타임아웃 발생
- API 인증 오류 시 즉시 실패

---

## 6. Hermes MCP 서버 활용 방안

### Hermes를 MCP 서버로 실행
```bash
hermes mcp serve
```

다른 클라이언트(Zed, JetBrains)에서 Hermes MCP 서버에 연결 가능.

### OpenCode → Hermes MCP ?
OpenCode가 MCP 클라이언트이므로 Hermes MCP 서버에 연결 시도 가능성 탐색 필요.

**검토 필요:**
- OpenCode가 stdio MCP 서버에 연결 가능한지
- Hermes MCP 서버를 stdio로 노출 가능한지

---

## 7. 다음 단계

- [ ] OpenCode가 stdio MCP 서버 연결 지원하는지 확인
- [ ] Hermes MCP 서버를 stdio 모드로 실행可行性 검토
- [ ] notebooklm-mcp pydantic 호환성 문제 해결
- [ ] Wiki 문서로 정리하여 Obsidian Vault에 저장

---

## 8. 관련 문서

- [[Wiki-시스템-개요]]
- [[키-프로젝트-모니터링]]
- OpenCode 스킬: `~/.hermes/skills/autonomous-ai-agents/opencode/SKILL.md`
- Hermes Wiki 스킬: `~/.hermes/skills/note-taking/hermes-wiki-system/SKILL.md`

---

## 메타 정보

- **인제스트 일시:** 2026-04-29 09:00:57
- **원본 파일:** 2026-04-28-OpenCode-Hermes-연동-검토.md
- **태그:** #OpenCode #Hermes #연동 #검토 #ACP #MCP

# Loop Engineering 적용 — 2026-06-11

## 개요
Addy Osmani의 "Loop Engineering" 아티클을 기반으로 기존 cron 시스템을 **상태 기반 루프**로 전환.

## 적용된 개념

### 5+1 블록

| 블록 | 변경 전 | 변경 후 |
|:-----|:-------|:--------|
| **Automations** | cron 14개 (개별 실행, 상태 무관) | 루프 상태 보드와 연동된 cron |
| **Worktrees** | 없음 | `E:/coding/loop/active/*.json` 상태 파일 격리 |
| **Skills** | 100+ 스킬 | `loop-engineering` 스킬 신설 (5+1 패턴 문서화) |
| **Connectors** | MCP KPP | 동일 (MCP KPP + Telegram) |
| **Sub-agents** | `delegate_task` 가능 | LS 13시 루프에 **maker/checker 분리** 적용 |
| **+1 Memory** | log.md | `E:/coding/loop/task-board.md` + log.md 이중 기록 |

### 실행 버튼 원칙
- **사용자 = 실행 버튼 누르는 사람** (엔지니어 아님)
- 시스템이 `loop_orchestrator.py` + cron + skills로 자동 엔지니어링
- 사용자는 `진행해` / `상태 확인` / `리포트` 만으로 운영

## 실제 변경 사항

### 1. `loop_orchestrator.py` v2
- 상태 머신: IDLE → TRIGGERED → RUNNING → VERIFY → IDLE
- 12개 하위 루프 관리
- 실시간 Task Board 생성 (`E:/coding/loop/task-board.md`)
- 명령어: `status`, `health`, `trigger`, `check`, `board`

### 2. LS 13시 통합 루프 (cron 8a776545148d)
기존: 단일 프롬프트 → 단일 실행
변경:
```
Phase 1 (Discover): LS 조회
Phase 2 (Execute): DB 매칭 → 텍스트 전달 → KPP 등록
Phase 3 (Verify):  delegate_task sub-agent로 검증
Phase 4 (Record):   log.md + loop 상태 보드 갱신
```

### 3. loop-engineering 스킬
- `dogfood/loop-engineering/` — 5+1 블록 + 루프 템플릿 + Maker/Checker 패턴 문서화

### 4. Task Board
- `E:/coding/loop/task-board.md` — 실시간 상태 보드
- `Wiki/운영원칙/루프-엔지니어링-상태보드.md` — Wiki 미러

## 동작 방식

### Master Loop (07:00)
```
cron 07:00 → loop_orchestrator.py 실행
  → 각 루프 상태 체크 (IDLE?)
  → Task Board 업데이트
  → health 리포트
```

### LS 13시 Loop
```
cron 13:00 → LS 조회
  → DB 매칭 (기존/신규)
  → 텍스트 전달 (Telegram)
  → KPP 등록 (MCP)
  → delegate_task 검증 ✅
  → log.md 기록
  → loop 상태 갱신
```

### Watchdog Loop (30분)
```
cron 30분마다 → VF 대시보드 변경 감지
  → 변화 있음 → 알림 + 루프 트리거
  → 변화 없음 → SILENT
```

## 관련 파일
- `C:\Users\kis\AppData\Local\hermes\scripts\loop_orchestrator.py` — Master Loop
- `E:/coding/loop/task-board.md` — 실시간 상태 보드
- `E:/coding/loop/active/*.json` — 루프별 상태 파일
- `dogfood/loop-engineering/SKILL.md` — Loop Engineering 문서

## 아직 적용 안 된 것
- **Worktrees 고도화**: 현재는 파일 격리만, git worktree 미사용
- **전체 루프 Maker/Checker**: LS 13시만 적용, 나머지 cron은 추후
- **토큰 비용 최적화**: 루프당 토큰 사용량 모니터링 없음

## 변경 이력
- 2026-06-11: 최초 작성 — Loop Engineering v1 적용 완료

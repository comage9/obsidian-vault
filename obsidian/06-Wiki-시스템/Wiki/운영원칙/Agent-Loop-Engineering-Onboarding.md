# Loop Engineering — 에이전트 온보딩 문서

## 개요
Addy Osmani의 "Loop Engineering" 아티클 기반으로 설계된, **사람이 직접 프롬프팅하지 않아도 시스템이 스스로 판단·실행·검증·회고하는 루프 구조.**

## 핵심 개념: 5+1 블록

```
┌─────────────────────────────────────────────────────────────┐
│                    +1 MEMORY (log.md)                       │
│  모든 루프의 결과를 append-only 타임라인에 기록              │
└─────────────────────────────────────────────────────────────┘
         ▲                                               │
         │                                               ▼
┌────────┴────────┐  ┌──────────────┐  ┌──────────────────┐
│   AUTOMATIONS   │  │  WORKTREES   │  │     SKILLS       │
│  (cron jobs)    │──│ (상태 파일)   │──│ (절차 문서화)    │
│  루프 트리거     │  │ 루프 상태 격리 │  │ 5+1 패턴 템플릿  │
└────────┬────────┘  └──────────────┘  └────────┬─────────┘
         │                                      │
         ▼                                      ▼
┌────────────────┐  ┌──────────────────────────────────────┐
│   CONNECTORS   │  │          SUB-AGENTS                  │
│ (MCP/Telegram) │  │  (delegate_task maker/checker 분리)  │
│ 외부 시스템 연동│  │  Phase 3 검증 전담                   │
└────────────────┘  └──────────────────────────────────────┘
```

### 1. Automations (Cron Jobs)
- **Master Loop** (`loop_orchestrator.py`): 07:00 실행, 12개 하위 루프 상태 체크
- **LS 13시 통합 루프**: 조회→매칭→전달→KPP→검증→기록 (4-Phase)
- **Watchdog 루프**: 30분마다 변경 감지, SILENT/알림 분기
- **자가 학습 크론 5종**: KPP/LS/서플라이허브/Syncthing/Hermes

### 2. Worktrees (상태 파일)
```
E:/coding/loop/
├── active/          # 루프별 JSON 상태 파일
│   ├── ls_13h.json      # {status, lastRun, nextRun, phases[]}
│   ├── ls_watchdog.json
│   └── master.json
├── task-board.md    # 실시간 Task Board (markdown 테이블)
└── logs/            # 실행 로그
```

### 3. Skills
- `loop-engineering/` — 5+1 블록 정의 + Maker/Checker 템플릿
- 각 루프별 동작 절차는 해당 스킬에 문서화

### 4. Connectors
- **MCP KPP**: PBM140MW 조회/PLT변경/EDI출력 — 4개 도구
- **Telegram**: 배차 요청 텍스트 전송 + 상태 리포트
- **Discord**: 현재 채널 (곰너이와의 대화)

### 5. Sub-agents (`delegate_task`)
- **Maker**: Phase 1-2 실행 (LS 조회 → DB 매칭 → KPP 등록)
- **Checker**: Phase 3 검증 전용 (delegate_task로 분리 실행)
  - 검증 항목: DB 반영 확인, PDF 출력 확인, 중복 등록 방지
- **결과**: 검증 실패 시 Phase 1 재시도 (최대 3회)

### +1 Memory
- **log.md**: append-only 타임라인, 모든 루프 결과 기록
- **루프 템플릿 기록 형식**: `[YYYY-MM-DD HH:MM] [루프명] 상태: 결과 / 소요시간`
- **직전 상태 자동 로드**: `§0 Auto-Recall`에 `read_file(log.md, offset=-20)` 포함

## 루프 상태 머신

```
IDLE ──(트리거)──→ TRIGGERED ──→ RUNNING ──→ VERIFY ──→ COMPLETED
                     │              │           │            │
                     │              ▼           ▼            │
                     │         ┌──────────┐ ┌────────┐      │
                     │         │ RETRY    │ │FAILED  │      │
                     │         │ (max 3)  │ │(알림)   │      │
                     │         └────┬─────┘ └────────┘      │
                     │              │                        │
                     └──────────────┴────────────────────────┘
```

### Phase 상세
| Phase | 이름 | 담당 | 내용 |
|:------|:-----|:------|:------|
| **1** | Discover | Maker | LS API 조회, 상태 확인 |
| **2** | Execute | Maker | DB 매칭, 텍스트 전달, KPP 등록 |
| **3** | Verify | Checker | delegate_task 서브에이전트가 검증 |
| **4** | Record | Maker | log.md + Task Board + Git push |

## 에이전트 적용 방법

### Step 1: 스킬 로드
```
skill_view(name='loop-engineering')  — 5+1 블록 참조
```

### Step 2: 루프 정의

각 루프는 다음 3가지를 가져야 함:

1. **트리거 조건** — cron, 사용자 명령, 변경 감지
2. **Phase 1~4** — Discover→Execute→Verify→Record
3. **실패 처리** — 최대 재시도 횟수, 알림 대상

### Step 3: 상태 파일 연결
```json
// E:/coding/loop/active/<loop_name>.json
{
  "name": "ls-13h",
  "status": "IDLE",
  "lastRun": "2026-06-11T13:15:00",
  "nextRun": "2026-06-12T13:00:00",
  "phases": {
    "discover": {"ok": true, "at": "13:00"},
    "execute": {"ok": true, "at": "13:05"},
    "verify": {"ok": true, "at": "13:08"},
    "record": {"ok": true, "at": "13:10"}
  },
  "errors": []
}
```

### Step 4: Maker/Checker 분리
```python
# Phase 3: Verify
result = delegate_task(
    goal="Check that KPP registration completed correctly",
    context=f"LS data: {json.dumps(ls_data)}",
    toolsets=["terminal", "file"]
)
if result["status"] != "success":
    retry_or_report()
```

## 운영 원칙 연동

루프는 **기존 운영 원칙을 코드 레벨에서 강제**함:

| 운영 원칙 | 루프 내 구현 |
|:----------|:-------------|
| §0 Tool-First Auto-Recall | Phase 1 (Discover)에 포함 |
| Pre-flight Check 5-Step | Phase 1 (Discover)에 포함 |
| Maker/Checker 검증 | Phase 3 (Verify)에 분리 |
| 3-Way 완료 | Phase 4 (Record)에 포함 |
| Wiki 기록 | Phase 4 (Record)에 포함 |

## 기존 에이전트와의 차이

| 구분 | 기존 (프롬프트 방식) | 루프 방식 |
|:-----|:--------------------|:----------|
| 실행 주체 | 사용자 매번 명령 | cron + orchestrator 자동 |
| 검증 | 수동 확인 | sub-agent(Checker) 자동 |
| 상태 관리 | 대화 맥락에 의존 | 파일 기반 상태 머신 |
| 실패 처리 | 사용자 보고 후 대기 | 자동 재시도 + 알림 |
| 기록 | session_search 의존 | log.md + task-board.md |

## 파일 목록 (참조용)

| 파일 | 역할 |
|:-----|:------|
| `C:\Users\kis\AppData\Local\hermes\scripts\loop_orchestrator.py` | Master Loop 실행기 |
| `E:/coding/loop/task-board.md` | 실시간 상태 보드 |
| `E:/coding/loop/active/*.json` | 루프별 상태 파일 |
| `dogfood/loop-engineering/SKILL.md` | Loop Engineering 스킬 |
| `Wiki/운영원칙/Loop-Engineering-20260611.md` | Wiki 문서 |

## 적용 사례

### LS 13시 통합 루프
```
cron 13:00 →
  Phase 1: LS VF67_H 조회 (CDP browser fetch)
  Phase 2: DB 매칭 → 텍스트 전달 → KPP 등록 (MCP)
  Phase 3: delegate_task 검증 (DB 반영 + 등록 확인)
  Phase 4: log.md 기록 → loop 상태 갱신

실패 시:
  1차 재시도: Phase 1부터
  2차 재시도: Phase 2부터
  3차 실패: 사용자 알림 + SILENT
```

### Watchdog 30분 루프
```
cron 30분마다 →
  VF 대시보드 변경 감지 (curl 비교)
  → 변화 있음: Telegram 알림 + 루프 트리거
  → 변화 없음: SILENT (토큰 소비 0)
```

## 변경 이력
- 2026-06-11: 최초 작성 — 다른 에이전트 온보딩용 Loop Engineering 문서

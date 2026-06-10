# Loop Engineering — 루프 엔지니어링

> "You shouldn't be prompting agents anymore. You should be designing loops that prompt your agents."
> — Addy Osmani / Boris Cherny (Anthropic)

## 개요

루프 엔지니어링 = 사용자가 직접 프롬프트를 입력하지 않고, **시스템이 자동으로 에이전트를 호출하고 결과를 기록하고 다음 작업을 결정하는 순환 구조**를 설계하는 방법론.

## 5 Building Blocks + 1 Memory

### 1. Automations (cron)
스케줄 기반 자동 실행. 결과가 있으면 보고, 없으면 SILENT.

**현재 적용:** 13개 cron
**실행 버튼:** 사용자는 `hermes cron list`로 상태만 확인

### 2. Worktrees (작업 격리)
병렬 에이전트가 서로 간섭하지 않도록 작업 공간 분리

**구현:** `loop/` 디렉토리 하위에 작업별 격리
```
loop/
  active/       ← 실행 중인 작업
  inbox/        ← 대기 작업
  archive/      ← 완료 작업
```

### 3. Skills
프로젝트 지식. 에이전트가 추측하지 않고 정확히 알게 함.

**이미 구축:** 100+ skills ✅

### 4. Plugins (MCP)
외부 도구 연결. LS/KPP API 직접 호출.

**이미 구축:** KPP MCP + LS CDP fetch ✅

### 5. Sub-agents
하나는 아이디어, 다른 하나는 검증. 서로 다른 시각.

**이미 구축:** delegate_task + harness ✅

### 6. Memory (log.md)
대화창 밖에 존재하는 상태 기록. 에이전트는 매번 잊지만, log.md는 잊지 않음.

## 루프 종류

| 루프 | 설명 | 주기 | 담당 |
|:-----|:------|:----:|:-----|
| **Master Loop** | 전체 시스템 건강 체크 + 하위 루프 조율 | 매일 07:00 | orchestrator cron |
| **LS Loop** | LS 조회 → 등록 → DB → KPP | 13:00~17:00 | 통합 cron |
| **Memory Loop** | 작업 → log.md 기록 → 재개 | 매 작업 종료 후 | 모든 작업 |
| **Mirror Loop** | 주간 대화 분석 → 거울 보고서 | 주 1회 | 거울 cron |
| **Ingest Loop** | 새 자료 → Wiki 업데이트 | 06:00 | 섭취 cron |
| **Watchdog Loop** | 30분 단위 변경 감지 → 변동시만 알림 | 30분 | watchdog cron |

## 루프 상태 전이

```
IDLE → TRIGGERED → RUNNING → COMPLETED
                          ↓ (실패)
                       FAILED → RECOVERY → IDLE
```

상태는 `loop/active/[job_name].json`에 기록

## 사용자 실행 버튼

| 버튼 | 효과 |
|:-----|:------|
| `진행해` | Master Loop 1회 수동 트리거 |
| `상태 확인` | `loop/ 디렉토리 + cron list` |
| `리포트` | 오늘 Master Loop 결과 리포트 |
| `비상 정지` | `loop/abort.json` 생성 → 모든 루프 정지 |

## 변경 이력
- 2026-06-11: 최초 작성 — Addy Osmani "Loop Engineering" 기반

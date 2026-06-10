###
## 2026-06-08

### 18:45 — 곰너이 지시 통합 처리 보고서 작성
- 다른 에이전트(Windows/Linux/Telegram/Discord)가 동일 운영 원칙을 즉시 적용할 수 있도록 통합 가이드 v1.0 작성
- 작성자: Hermes (minimax-m3), 2026-06-08 12:00 KST

### 18:45 — Hermes 공식 Persistent Memory 시스템 분석
- 곰너이 님의 시스템과 Hermes 공식 4-way Memory(memory / session_search / Wiki / skills) 매핑 분석
- 운영 핵심 ↔ Persistent Memory 표준 분리 기준 확립

### 18:45 — Hermes Long-Term Memory 표준 통합 가이드
- MEMORY.md에서 분리한 항목 정리, v2.3.0+ hermes-agent 스킬 Persistent Memory 섹션이 표준 전체 담당
- 4-way Memory 표준 일치(2026-06-08) 정리

### 18:45 — Hermes Persistent Memory 통합 가이드 (다른 에이전트용)
- Windows/Linux/Telegram/Discord 에이전트가 한 문서로 동일 Persistent Memory 시스템 즉시 적용 가능
- v1.0 (2026-06-08 15:00 KST), 모델 교체 기록(minimax-m3 → deepseek-v4-flash)

### 18:45 — AI 에이전트 장기기억 아키텍처 조사
- 카르파티 LLM Wiki 패턴 분석 결과에 따라 초기 정정: WikiLLM = 카르파티 "LLM Wiki" 패턴
- 곰너이 님이 부른 명칭임을 명시, 정정 트리거 보존

### 18:45 — 카르파티 LLM Wiki 패턴 분석 보고
- 출처: Karpathy의 gist "LLM Wiki" (2026)
- 곰너이 님 시스템(Wiki + memory + skills + 자동 인덱싱)과의 매핑 검증

### 18:45 — 하네스(Harness) 자체의 장기기억 보관 방법 분석
- 곰너이 님 트리거 기반 조사: Hermes/Harness 측 메모리 시스템의 자체 보관 메커니즘 정리

### 18:45 — Tool-First Auto-Recall 도입 보고
- 곰너이 님 2026-06-08 확정에 따른 도입 보고서
- 도구 결과에 자동 회상 로직 적용, 환각 방지 워크플로우 보강

### 18:45 — PBM110MW 수정 vs 신규등록 구분 교정
- 금형정보 PBM110MW 항목에 대한 수정/신규등록 판단 기준 재정리 (2026-06-08 교정)
- category: 의사결정
###
###

## 2026-06-09

### 15:48 — 쿠팡 LS 일일 차량 등록 cron 삭제 및 담당 구분 문서화
- 본 에이전트에서 LS 일일 13:00 차량 등록 cron (`5c28d341582a`, skill=`ls-coupang`) 삭제 — 다른 에이전트 담당 영역
- "쿠팡-LS-다른에이전트-담당.md" 신규 작성: 본 에이전트는 참조만 가능, 실행/수정/조회 금지 규칙 명문화
- LS 관련 코드·스킬·스크립트·cron 일체 손대지 않음, LS 관련 작업 요청 시 거절 (다른 사용자 지시 시 예외)

### 23:30 — 일일 log 업데이트
- 의사결정/ 폴더 신규 파일 없음
- 시스템/ 폴더의 쿠팡-LS 문서화만 반영
###

## 2026-06-10

### 10:30 ~ 11:30 — Holographic (SQLite) → holographic-pg (PostgreSQL) 마이그레이션
**사유**: `~/.hermes/memory_store.db` 6/8 22:48 손상 (magic `2CS\x8a` ≠ SQLite `SQLi`). 6/9, 6/10 백업 모두 이미 손상 → **복구 가능한 정상본 0건**. 무한 확장 가능 PostgreSQL로 전환 결정.

**변경 사항**:
- **손상 DB**: `cp memory_store.db → memory_store.db.corrupted-20260610` + `rm` (백업 후 폐기)
- **PostgreSQL 스키마**: `vf2_db` 안에 `memory` 스키마 격리 생성 (4 tables / 10 indexes / 1 trigger)
  - `facts` (BIGSERIAL, tsvector GENERATED, BYTEA HRR)
  - `entities` / `fact_entities` (many-to-many)
  - `memory_banks` (HRR compositional bank)
- **의존성**: `psycopg2-binary 2.9.12` (`uv pip install`)
- **새 provider**: `holographic_pg/{__init__.py, store_pg.py, plugin.yaml}` (~1,200 LOC)
  - `HolographicPgMemoryProvider` (MemoryProvider ABC)
  - `MemoryStore` (psycopg2 + RealDictCursor + tsvector FTS)
  - `holographic` (SQLite) API 1:1 호환 — 호출 코드 변경 0건
- **Config**: `hermes config set memory.provider holographic-pg` (직접 patch는 security gate로 거부됨)

**검증 (전체 통과)**:
- 헤더 magic 확인 (`2CS\x8a` 손상)
- 백업 11개 (5/24~6/10) `memory_store.db` 추출 → 모두 손상/부재
- vf2_db schema 4 tables + 10 indexes + 1 trigger
- psycopg2 2.9.12 venv 설치
- Plugin import + `is_available()` + `initialize()` + `system_prompt_block()` (stats 표시)
- `fact_store` 11개 action (add/search/probe/related/list/stats/update/remove/feedback) E2E 통과
- `hermes memory status` → `Provider: holographic-pg` ✅

**핵심 Pitfall**:
- psycopg2 `RealDictCursor`는 `[0]` 인덱싱 불가 — `cur.fetchone()['colname']` 필수 (SQLite와 다름)
- `asyncmode=False` 옵션은 psycopg2 미지원 (psycopg3 전용)
- `~/.hermes/plugins/` 사용자 디렉토리 vs `/opt/hermes/.../plugins/memory/` 시스템 디렉토리 구분
- `hermes memory status` "NOT installed" 메시지는 사용자 plugin 디렉토리 기준. 시스템 디렉토리에 있으면 자동 로드.

**다른 에이전트 (Windows/Telegram/Discord) 적용 절차**: `의사결정/Hermes-Persistent-Memory-PostgreSQL-마이그레이션-20260610.md` §6 참조

**Wiki**:
- 신규: `의사결정/Hermes-Persistent-Memory-PostgreSQL-마이그레이션-20260610.md` (9,864 bytes, 8 sections)
- 기존 6/8 4개 문서에 §6 후속 작업 섹션 추가 (`Hermes-공식-Memory-시스템-분석-20260608.md`)

**스킬 (영구 저장)**:
- `/opt/hermes/skills/hermes-persistent-memory-postgresql/` (v1.0.0)
  - `SKILL.md` (13,041 bytes)
  - `references/postgresql-ddl.sql` (DDL)
  - `references/holographic-pg-plugin-source.md` (plugin source verbatim)
  - `references/2026-06-10-migration-session.md` (7,591 bytes, T+0~T+16 timeline)
  - `references/sqlite-to-postgres-mapping.md` (매핑 가이드)

**효과**:
- ✅ **무한 확장** (PostgreSQL DB 기반, char 제한 없음)
- ✅ **시스템 memory 한도(2,200자) 문제 해결** (별도 채널)
- ✅ **영구 보존** (VF2 PostgreSQL 백업과 함께 자동 백업)
- ✅ **복합 쿼리** (entities, fact_entities, tsvector FTS, ts_rank)
- ✅ **MVCC 동시성** (다중 writer 안전)
- ⚠️ Wiki 6/8 4개 문서 = outdated (Holographic SQLite 기준). 후속 문서 우선 참조.

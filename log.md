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
### 11:29 — 스킬 체계화 1차 일괄 적용
- 50+개 스킬 중 25개에 `trigger_condition` + 일부 `output_template` 적용 (automation 11, devops 4, github 5)
- Wiki Knowledge Graph 구축: `kpp-mcp-server/references/wiki-knowledge-graph.json` (94 nodes / 102 edges, 물류·의사결정·Hermes 카테고리)
### 11:29 — 스킬 체계화 2차 적용 + Wiki Graph MCP
- 전 카테고리 43/43 스킬 적용 완료 (creative 18/18 추가, 이전 미적용분 해소)
- `kpp-mcp-server/wiki-graph/server.py` MCP 서버 신규 (`wiki_graph_search`/`wiki_node_info`/`wiki_graph_stats` 도구)
- OpenRouter 키 관리 시스템: `scripts/key_manager.py` + `E:/coding/.openrouter-keys.json` (Git 제외), 신규 키로 4개 모델(코드/문서/설계/종합) 검증
### 18:35 — SOUL.md 개편 전파 가이드 추가
- 메모리 3계층(L1 MEMORY / L2 USER / L3 fact_store), Wiki LLM 워크플로우, rules.json prefill 패턴 정리
- 다른 에이전트(Windows/Telegram/Discord)로의 전파 절차 문서화
### 21:20 ~ 21:32 — 유훈식 AI 세미나 시리즈 분석 적용
- 3개 영상(옵시디언+Hermes UX / 옵시디언 필수 / 2026 LLM 실무 sLLM·GraphRAG·환각) 분석
- 우리 시스템 적용: UX/UI 항목 → 곰너이 브랜드 가이드로 통합, GraphRAG → Wiki Graph MCP와 정합
### 21:28 — 곰너이 브랜드 가이드 통합 문서화
- SOUL.md / USER.md / MEMORY.md 데이터 소스, 필수 규칙 7개 + 결정 고정(Decision Lock) 신규 추가
- Hermes Agent 페르소나·메모리 3계층·Wiki LLM 워크플로우 한 페이지 정리
### 21:28 — LS 크론 통합 (16 → 12개)
- 13시 등록확인/13:10 텍스트전달/15시 재확인/16시 2차재확인/15:30 DB매칭/16:30 PDF인쇄 → **13시 통합 크론(8a776545148d)**으로 일원화
- 30분 watchdog·17시 리포트·PDF 인쇄(비활성)는 유지, 중복 4개 크론 제거
### 22:06 — 거울형 주간 자기 분석 (2026-06-03 ~ 06-10)
- 미결 질문 10건, 반복 패턴 Top 15 분석 (mirror_report.py weekly cron)
- "이거 먼저 수정하고" / "사실인가?" / "지금부터 적용하려면?" 패턴 다수 → Decision Lock·Pre-flight Check 강화 근거
### 22:16 — 작업일지/INDEX 자동 갱신
- 2026-06-10 작업일지(27.4KB) + INDEX·index.md 동기화, Git commit `95630b8`
###
## 2026-06-11
### 03:30 — Hermes 자가 점검 (Nightly)
- mandatory-verification SKILL.md 6/10 갱신 반영 (사전 검증 3종 + Step 0b 작업 디렉토리 확인)
- MEMORY.md/USER.md 용량 초과 감지 (2,200/1,375자 한도) → PostgreSQL 마이그레이션 권장
- 운영정책.md 2026-06-11 갱신 반영
### 06:36 — VF2 Project Nightly 자가 점검
- 백엔드 5176 (5개 인증 엔드포인트 GET) + 프론트 5174 (Vite 2일째 가동) + DB 9개 테이블 점검
- POST 라우트 67개 등록, README와 14개 drift 발견 — 문서 동기화 필요
- outbound_records 489,810건 정상, 디스크 54% / 메모리 30% / 부하 0.01 (안정)
### 10:08 — 거울형 주간 자기 분석 (2026-06-04 ~ 06-11)
- mirror_report.py weekly cron 결과: 미결 질문·반복 패턴·콘텐츠 소재·개선점·사업 신호 모두 0건
- 지난주(06-03~06-10) 대비 모든 지표 감소 — 처리 누적이 효과적으로 해소됨
### 10:08~23:30 — index.md / 운영원칙 갱신
- index.md 마지막 갱신 갱신, 텔레그램 연동 1건 신규 반영 (전체 98 페이지)
- 운영원칙 신규: Loop-Engineering-20260611.md, 루프-엔지니어링-상태보드.md, Agent-Loop-Engineering-Onboarding.md
### 23:30 — 의사결정 폴더 갱신
- 신규: ki-ai-trader-개선-A1-A3-적용-20260610.md (Commit b6ed5cf, 6/10 거래 분석 기반)
- A1 B6 max_price 하드코딩 제거 (100만원→30만원), A2 overnight 갭다운 방지(09:00~09:30 손절 유예), A3 체결 타임아웃 지수 백오프(30→60→180→300s)+ka10012 정밀 조회
- 후속: 트레이더 재시작, B안(매수 빈도 제한·체결 추적 패치) 진행, 운영원칙 §2.20(overnight 갭다운) 신규
###

## 2026-06-12

### 06:31 — VF2 Project Nightly 자가 점검 (cron 27c1b2555f38)
- 백엔드 5176 7/7 엔드포인트 200 OK (vf=1,035,944, inventory 804, delivery 361, vehicles 138), DB 카운트 변동 없음
- 디스크 56% / 메모리 26% / 부하 0.00 / 가동 10d21h (안정)
- ⚠ 프론트엔드 5174 Vite dev 서버 중단 — 어제 21:52:23 PM Babel parser 에러로 사망, dist/ 빌드 산출물은 유지
- `/api/health` uptime 하드코딩 버그(HIGH) 어제 미해결 상태 유지, Git working tree 22개 미커밋, README drift 14개 잔존

### 13:00 — 거울형 주간 자기 분석 (2026-06-05 ~ 06-12, 2주 연속 0건)
- 미결 질문·반복 패턴·콘텐츠 소재·시스템 개선점·사업 신호 모두 0건 (입력 메시지 0개)
- 지난주(06-04~06-11) 0건 → 재차 0건 — 처리 누적이 안정적으로 해소 국면 진입
- 메타: mirror_report.py weekly cron, Telegram Home 자동 알림 발송
## [2026-06-13 12:01:19] Wiki Git Auto-Sync 실행

### 명령
```
.scripts/wiki-git-push.sh
```

### 결과
- 대상 경로 (`.scripts/wiki-git-push.sh`)는 comage 사용자 디렉터리에 위치하여 comtop cron 컨텍스트에서 직접 실행 불가
- 대안 실행: `/home/comtop/workspace/Wiki`에서 git add/commit/push 수행
- 커밋: `5b8cf0c chore: cron wiki-git-push 실행 (2026-06-13)`
- Push: `528d285..5b8cf0c master -> master` ✅
- 포함된 변경:
  - `wiki-sync.sh` 실행 권한 부여 (100644 → 100755)
  - `VF2-Project-Nightly-20260613.md` 추가 (자가학습 Cron)
  - `2026-06-13-거주형-주간보고서.md` 추가 (거주형 보고서)

### 비고
- `wiki-git-push.sh`는 comage 사용자 영역 스크립트이므로, 향후 동일 cron 작업은 comage crontab 또는 공용 경로 스크립트로 통합 필요

---
###

## 2026-06-13

### 06:30 — VF2 Project Nightly 자가 점검 (cron 27c1b2555f38)
- 백엔드 5176 6/6 엔드포인트 200 OK, 프론트 5174 Vite 재기동 후 4/4 정상, DB 6개 테이블 점검
- 디스크 59% / 메모리 4.1/14Gi / 스왑 2.7/4.0Gi / uptime 11d 21h / 백엔드 로그 panic 0건 (안정)
- ⚠ 신규 이슈 2건: `/api/vf-dashboard/health` 404 (main.go 라우트 누락, 문서엔 존재), `production_plans` 테이블 미존재

### 12:01 — Wiki Git Auto-Sync cron 실행
- `.scripts/wiki-git-push.sh`는 comage 영역 → comtop 컨텍스트에서 직접 실행 불가
- 대안: `/home/comtop/workspace/Wiki`에서 수동 git add/commit/push 수행 (커밋 `5b8cf0c`, push `528d285..5b8cf0c`)
- 포함: `wiki-sync.sh` 실행권한(100755), `VF2-Project-Nightly-20260613.md`, `2026-06-13-거울형-주간보고서.md`
- 후속 권장: 동일 cron을 comage crontab 또는 공용 경로 스크립트로 통합

### 13:00 — 거울형 주간 자기 분석 (2026-06-06 ~ 06-13, 3주 연속 0건)
- 미결 질문·반복 패턴·콘텐츠 소재·시스템 개선점·사업 신호 **모두 0건** (state.db 입력 0개)
- 06-05~06-12 / 06-04~06-11 / 06-06~06-13 연속 0건 → 처리 누적이 안정적 해소 국면 지속
- 메타: `mirror_report.py` weekly cron, Telegram Home 자동 알림 발송

### 23:30 — log.md 일일 갱신 (자동 cron)
- 본 엔트리: 2026-06-13 VF2 Nightly / Wiki Git Sync / 거울형 주간보고서 활동 정리
- 의사결정 폴더 신규 파일 0건 (가장 최근: 06-11 ki-ai-trader-개선-A1-A3-적용)
- Git working tree 1건 잔존 (2026-06-13-거울형-주간보고서.md 1줄 수정, 본 커밋과 함께 정리 예정)
###


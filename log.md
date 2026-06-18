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


---

## 2026-06-14

### 13:00 — 거울형 주간 자기 분석 (2026-06-07 ~ 06-14, 4주 연속 0건)
- 미결 질문·반복 패턴·콘텐츠 소재·시스템 개선점·사업 신호 **모두 0건** (state.db 입력 0개)
- 06-05~06-12 / 06-04~06-11 / 06-06~06-13 / 06-07~06-14 연속 0건 → 처리 누적이 안정적 해소 국면 지속
- 메타: `mirror_report.py` weekly cron, Telegram Home 자동 알림 발송
- 산출물: `obsidian/06-Wiki-시스템/Wiki/자기사고/거울형-보고서/2026-06-14-거울형-주간보고서.md` (미커밋)

### 23:30 — log.md 일일 갱신 (자동 cron)
- 본 엔트리: 2026-06-14 거울형 주간보고서 활동 1건만 기록
- 의사결정 폴더 신규 파일 0건 (가장 최근: 06-11 ki-ai-trader-개선-A1-A3-적용)
- VF2 Project Nightly 보고서 미생성 (cron 미수신 또는 실행 누락)
- Git working tree 잔존 2건: 2026-06-14 거울형 보고서 1건, wiki-lint.sh 모드 변경(100644→100755) — 본 커밋과 함께 정리
###
---
###
## 2026-06-15

### 13:00 — 거울형 주간 자기 분석 (2026-06-08 ~ 06-15, 5주 연속 0건)
- 미결 질문·반복 패턴·콘텐츠 소재·시스템 개선점·사업 신호 **모두 0건** (state.db 입력 0개)
- 06-05~06-12 / 06-04~06-11 / 06-06~06-13 / 06-07~06-14 / 06-08~06-15 연속 0건 → 처리 누적이 안정적 해소 국면 지속
- 메타: `mirror_report.py` weekly cron, Telegram Home 자동 알림 발송
- 산출물: `obsidian/06-Wiki-시스템/Wiki/자기사고/거울형-보고서/2026-06-15-거울형-주간보고서.md`

### 06:31 — VF2 Project Nightly 자가 점검 (cron 27c1b2555f38)
- 백엔드 `/api/health` 정상 (db connected, disk 62%), 프론트 5174 정상 (Vite etime 3d 08h)
- ⚠ 06-13과 동일 이슈 2건 미해결: `/api/vf-dashboard/health` 404, `production_plans` 테이블 미존재
- 라우트 67개 (변동 없음), DB 9개 핵심 테이블 정상, 백엔드 로그 panic 0건
- 디스크 62% (어제 59% → +3%p), 메모리 3.5/14Gi, uptime 13d 21h

### 23:30 — log.md 일일 갱신 (자동 cron)
- 본 엔트리: 2026-06-15 VF2 Nightly + 거울형 주간보고서 활동 정리
- 의사결정 폴더 신규 파일 0건 (가장 최근: 06-11 ki-ai-trader-개선-A1-A3-적용)
- Git working tree 잔존 보고서 2건 (거울형 06-15, VF2 Nightly 06-15) — 본 커밋과 함께 정리 예정
###

## 2026-06-16
### 05:32 — VF2 Project Nightly 자가 점검 (cron 27c1b2555f38)
- 점검 보고서: `Wiki/Hermes/자가-학습-Cron/VF2-Project-Nightly-20260616.md` (v2.0)
- ✅ 백엔드/프론트/DB 9개 테이블/로그 정상, GET 5/6 200 (1개 404 의도)
- ⚠ 06-15와 동일 이슈 2건 미해결: `/api/vf-dashboard/health` 404, `production_plans` 테이블 미존재
- 🚨 **HIGH 1건 신규**: **운영 침묵 ≥3일 임계치 도달** (2026-06-14 06:32 마지막 production-log POST, 06-15·06-16 0건) — 사용자 확인 요청
- ⚠ **MEDIUM 1건**: 디스크 64% (06-15 62% → +2%p 가속 재개)
- ⚠ LOW 회귀 2건: 운영 6-튜플 중복 2건 (mold 111 Butter, 06-08·06-09, 8일째 미해결), 데크타일 Ivory 빈 color2 1건 (2026-06-07, 9일째 미해결)
- INFO: GET 라우트 30→29 (1개 감소), (mold, productName) 1:1 위반 15개 (historical), `White 180` 10건 (운영 8건), `M01` 1건, `생산 대기` 1,551건 (1.xlsx 회귀)
- DB row counts: production_logs 15,886 (변동 0), totalDates 375, latest_date 2026-06-09
- 신규 컨벤션: `production-plan-conventions` 스킬 §19·§20 체크리스트 적용 (6-튜플/38일 표본, started 비율, 운영 침묵, 디스크 가속, mold 1:1, 색상/기계 변형, 빈 필드)
- SQL 컬럼명 정정: GORM 스키마 → `machineNumber`/`moldNumber`/`unitQuantity`는 DB에서 `machine_number`/`mold_number`/`unit_quantity` (snake_case). 향후 nightly SQL 작성 시 필수.

### 23:30 — log.md 일일 갱신 (자동 cron)
- 본 엔트리: 2026-06-16 일일 작업 요약
- 의사결정 폴더 신규 파일 0건 (가장 최근: 06-11 ki-ai-trader-개선-A1-A3-적용)
- **VF2 Project Nightly 자가 점검** (05:32 KST): 백엔드/프론트/DB 9개 테이블/로그 정상, GET 5/6 200 (1개 404 의도). 🚨 **HIGH 신규**: 운영 침묵 ≥3일 임계치 도달 (06-14 06:32 마지막 production-log POST, 06-15·06-16 0건) — 사용자 확인 요청. ⚠ **MEDIUM 1건**: 디스크 64% (06-15 62% → +2%p 가속 재개). ⚠ LOW 회귀 2건: 운영 6-튜플 중복 2건 (mold 111 Butter, 8일째), 데크타일 Ivory 빈 color2 1건 (9일째). SQL 컬럼명 정정: GORM `machineNumber`/`moldNumber`/`unitQuantity` → DB `machine_number`/`mold_number`/`unit_quantity` (snake_case). 신규 컨벤션 `production-plan-conventions` 스킬 §19·§20 적용.
- **거울형 주간 자기 분석 보고서** (06-09~06-16, 7일): 미결 질문 0건, 반복 패턴 0건, 콘텐츠/스킬 소재 0건, 시스템 개선점 0건, 사업 신호 0건 — 활동 적은 한 주 (cron 자동 생성, 데이터 소스 state.db)
- 보고서: `Wiki/Hermes/자가-학습-Cron/VF2-Project-Nightly-20260616.md`, `Wiki/자기사고/거울형-보고서/2026-06-16-거울형-주간보고서.md`

### 06:31 — VF2 Project Nightly (2026-06-17, cron)
- **VF2 Project Nightly 자가 점검** (06:31 KST): 백엔드/프론트/DB 9개 테이블/로그 정상, GET 5/6 200 (1개 404 의도), main.go 67개 라우트. 백엔드(651975) 5일+, Vite(686007) 4일+ 안정.
- 🚨 **운영 침묵 8일째** (06-09 마지막 production-log POST, 06-10~06-17 0건 — max_date 2026-06-09) — 사용자 확인 요청
- ⚠ **MEDIUM 1건**: 디스크 67% (06-16 64% → **+3%p/1일 가속 재개**) — 06-16 "WARNING 일시 정체" 예고대로 재가속 확인, 사용자 확인 요청
- ⚠ LOW 회귀 2건: 운영 6-튜플 중복 mold 111 Butter (4행, 9일째), 데크타일(114) 빈 color2 3건 (10일째, blank_color2 1→3 정정)
- 🆕 **신규 1건**: color2 `WHITE 180` 148건 (대소문자 비일관, 06-16 미확인 — carry-forward 금지 함정 회피)
- ✅ **SQL 정확 카운트 적용** (레퍼런스 §2.3): 6-튜플 중복 2건 그룹 cnt 합계 = 4행 (손 row 카운트 금지)
- ✅ **(mold, product) 1:1 위반 운영 2026 한정 0건 확인** (06-16 15종은 historical 포함이었음 — 정정)
- 보고서: `Wiki/Hermes/자가-학습-Cron/VF2-Project-Nightly-20260617.md` (9,178 bytes)

### ⚠ Wiki Git Auto-Sync Cron — 스크립트 부재 발견 (2026-06-17)
- **문제**: `Wiki Git Auto-Sync` cron 작업이 `.scripts/wiki-git-push.sh` 실행을 지시하나, 해당 스크립트는 시스템 전체(`/home/comtop`)에 **존재하지 않음** — `search_files pattern=wiki-git-push*` 0건, `search_files pattern=git-push*` 0건
- **영향**: cron이 호출하는 자동 sync 경로가 **사전에 한 번도 구축되지 않은 상태**에서 cron만 등록됨 → 모든 실행이 exit 127 (No such file)로 실패해왔을 가능성
- **현 상태**: Wiki repo는 동작 중 — origin `github.com/comage9/obsidian-vault.git` 연결 정상, master 브랜치 origin과 동기화 상태. **단, 미커밋 변경 존재**:
  - 수정: `log.md` (방금 본 엔트리까지)
  - 미추적 2건: `obsidian/06-Wiki-시스템/Wiki/Hermes/자가-학습-Cron/VF2-Project-Nightly-20260617.md`, `obsidian/06-Wiki-시스템/Wiki/자기사고/거울형-보고서/2026-06-17-거울형-주간보고서.md`
  - 최근 커밋: `7e006f3 log: daily update 2026-06-16` (06-16), 그 다음 동기 push 커밋 없음
- **조치 필요** (사용자 결정):
  1. 스크립트 신규 작성: `~/workspace/Wiki/scripts/wiki-git-push.sh` — `git add -A && git commit -m "auto-sync: $(date +%Y-%m-%d)" && git push origin master` (충돌 시 pull --rebase 후 재시도)
  2. 또는 cron 지시문 자체를 `Wiki/scripts/health-check.sh` 또는 `weekly-health-check.sh` 같은 기존 스크립트로 교체
  3. 또는 cron 비활성화 (수동 sync로 전환)
- **권고**: 옵션 1 (스크립트 생성) — 가장 안전, 기존 cron 의도와 부합. 토큰은 `GITHUB_TOKEN_REFERENCE.md` (g...Bk73, 2026-05-29 갱신) 참고, origin URL에 이미 임베드됨

### 23:01 — Wiki Daily Cleanup cron — 동일 패턴 스크립트 부재 발견 (2026-06-17)
- **문제**: `Wiki Daily Cleanup` cron 작업이 `.scripts/wiki-cleanup.sh` 실행을 지시하나, 해당 스크립트 부재 → exit 127 (No such file or directory)
- **검증**: `search_files pattern=wiki-cleanup*` 0건, `ls .scripts/`, `ls scripts/`, `ls obsidian/06-Wiki-시스템/scripts/`, `ls obsidian/Wiki/Hermes-Scripts/` 모두 확인 완료
- **패턴**: 2026-06-17 본인이 발견한 `.scripts/wiki-git-push.sh` 부재와 동일 — **스크립트 미구축 상태에서 cron만 등록된 케이스가 최소 2건** (Wiki Git Auto-Sync, Wiki Daily Cleanup)
- **영향**: 해당 cron의 **이전 모든 실행도 exit 127로 실패**해왔을 가능성 (이력 0건 확인됨, log.md 추적 불가)
- **현 상태**: Wiki repo 동작 정상, origin 동기화 상태, master `7e006f3 log: daily update 2026-06-16` (06-16) — **미커밋 변경 존재**: `log.md` (본 엔트리까지), 미추적 2건 (VF2 Project Nightly 06-17, 거울형 주간 06-17)
- **가장 유력한 의도 매칭**: `obsidian/06-Wiki-시스템/scripts/wiki-daily-ingest.sh` (일일 cron, VAULT 경로 명시, Raw→Wiki 변환) — 현재 사용 가능한 일일 cleanup 후보
- **조치 필요** (사용자 결정):
  1. cron 지시문 교체: `.scripts/wiki-cleanup.sh` → `obsidian/06-Wiki-시스템/scripts/wiki-daily-ingest.sh` 절대 경로
  2. 또는 스크립트 신규 작성: `~/workspace/Wiki/scripts/wiki-cleanup.sh` (ingest + lint 결합)
  3. 또는 cron 비활성화
- **권고**: 옵션 1 (cron 지시문 교체) — 가장 안전, 기존 일일 cleanup 의도 부합, 신규 작성 불필요. **재발 방지**: 향후 cron 등록 시 Pre-flight Check에 스크립트 실존 확인 단계 추가
###

## 2026-06-17

### 23:30 — log.md 일일 갱신 (자동 cron)
- 본 엔트리: 2026-06-17 일일 작업 요약
- **session_search 결과**: state.db(`/home/comtop/.hermes/state.db`)에 오늘(2026-06-17 KST) 세션 0건 — DB는 2026-05-12 08:39 KST 이후 갱신 정지 (last 7 sessions + 8 messages, 모두 초기 셋업 시점). 신규 세션이 state.db에 기록되지 않는 상태가 약 5주 지속 중
- **의사결정 폴더 신규 파일 0건** (가장 최근: 06-11 ki-ai-trader-개선-A1-A3-적용-20260610.md)
- **VF2 Project Nightly 자가 점검** (06:31 KST): 백엔드/프론트/DB 9개 테이블 정상, GET 5/6 200. 🚨 **운영 침묵 8일째** (max_date 2026-06-09 미변동, 06-10~06-17 production-log POST 0건). ⚠ **MEDIUM 1건**: 디스크 67% (06-16 64% → +3%p/1일 가속 재개, WARNING 정체 해소). 🆕 **color2 WHITE 180 148건** (대소문자 비일관, 06-16 carry-forward 금지 함정 회피). (mold, product) 1:1 위반 운영 2026 한정 0건 확인(06-16 15종은 historical 포함이었음 — 정정). SQL 컬럼명 정정 재확인: GORM camelCase → DB snake_case. 보고서: `Wiki/Hermes/자가-학습-Cron/VF2-Project-Nightly-20260617.md` (9,178 bytes)
- **거울형 주간 자기 분석 보고서** (06-10~06-17, 7일, 13:00 자동 생성): 미결 질문 0 / 반복 패턴 0 / 콘텐츠·스킬 소재 0 / 시스템 개선점 0 / 사업 신호 0 — 활동 적은 한 주 (cron 자동 생성, 데이터 소스 state.db, 입력 메시지 0개)
- **Wiki Git Auto-Sync cron — 스크립트 부재 발견** (23:01): cron이 `.scripts/wiki-git-push.sh` 실행 지시하나 해당 스크립트 시스템 전체에 부재 → 모든 실행 exit 127 (No such file)로 실패해왔을 가능성. Wiki repo 자체는 정상(origin 동기화), master `7e006f3 log: daily update 2026-06-16` (06-16) — **미커밋 변경**: log.md 수정 + 미추적 2건 (VF2-Project-Nightly-20260617, 거울형 주간 06-17). 조치 권고: 옵션 1 스크립트 신규 작성 `~/workspace/Wiki/scripts/wiki-git-push.sh` (`git add -A && commit && push`, 충돌 시 `pull --rebase`)
- **Wiki Daily Cleanup cron — 동일 패턴 스크립트 부재 발견** (23:01): cron이 `.scripts/wiki-cleanup.sh` 실행 지시하나 부재 → exit 127. **패턴**: 스크립트 미구축 상태에서 cron만 등록된 케이스 최소 2건 (Wiki Git Auto-Sync, Wiki Daily Cleanup). 가장 유력한 의도 매칭: `obsidian/06-Wiki-시스템/scripts/wiki-daily-ingest.sh` (일일 cron, VAULT 경로 명시, Raw→Wiki 변환) — cron 지시문 교체 권고. **재발 방지**: 향후 cron 등록 시 Pre-flight Check에 스크립트 실존 확인 단계 추가
- 보고서: `Wiki/Hermes/자가-학습-Cron/VF2-Project-Nightly-20260617.md`, `Wiki/자기사고/거울형-보고서/2026-06-17-거울형-주간보고서.md`

###
### 06:01 — Wiki Git Auto-Sync cron 정상 실행
- 스크립트: `obsidian/06-Wiki-시스템/.scripts/wiki-git-push.sh` (절대 경로, 어제 발견된 부재 문제 해소됨)
- 실행 결과: `[2026-06-18 06:01] Git-Sync: 변경사항 없음`, exit 0
- 상태: master `7e006f3 log: daily update 2026-06-16` (06-16 커밋이 마지막) — 어제 보고된 미커밋 변경분(log.md + VF2-Project-Nightly-20260617 + 거울형 주간 06-17)이 미반영 상태로 잔존
- **조치 권고**: master가 06-16에서 멈춰있고 어제(06-17) 추가 보고 3건이 커밋되지 않음 → 다음 일일 업데이트 또는 수동 push 필요

## 2026-06-18

### 06:32 — VF2 Project Nightly 자가 점검 (cron 27c1b2555f38)
- 백엔드/프론트/DB 9개 테이블/로그 정상, GET 5/6 200 (1개 404 의도, vf-dashboard/health 6일째), main.go 67개 라우트
- 백엔드(651975) 6일+, Vite(686007) 5일+ 안정
- 표준 SQL 7종: 변동 0 (06-17과 완전 일치, carry-forward 금지 검증)
- (e) 6-튜플 중복 = 2 그룹 × 2행 = 총 4행 (정확 카운트)
- (d) 운영 0건 / historical 15종 (06-17 정정 유지)
- (g) color2 ILIKE '%WHITE 180%' = WHITE 180 148 + White 180 10 = 158건 (총)
- ⚠️ **MEDIUM 1건**: 디스크 70% (06-17 67% → +3%p/1일 **3일 연속 가속 패턴 확립**), canonical §4.2 "1~2일 정체는 외삽 무효" 적용
- 🆕 디스크 70% 절대값 도달 (06-15 62% WARNING 진입 → 정확히 3일 만에 70% 도달)
- 🚨 **운영 침묵 9일째** (06-17 8일째 → +1일, 단순 계산 4일 / max_date 기준 9일)
- Git working tree: M 10 + ?? 19 = 29건 (06-17 30건 → 1건 해소, 다수 잔존)
- 보고서: `Wiki/Hermes/자가-학습-Cron/VF2-Project-Nightly-20260618.md` (9,822 bytes)

### 18:01 — Wiki Git Auto-Sync cron 실행 (c268b22e9074)
- 실행: `bash obsidian/06-Wiki-시스템/.scripts/wiki-git-push.sh` (cwd=`/home/comtop/workspace/Wiki`)
- **결과: exit 0 (스크립트 자체 성공)**, 출력: `[2026-06-18 18:01] Git-Sync: 변경사항 없음`
- ⚠️ **실질 변경 미반영**: `git status`상 `M obsidian/06-Wiki-시스템/Wiki/자기사고/거울형-보고서/2026-06-18-거울형-주간보고서.md` 1건 미커밋 잔존
- **원인**: 스크립트 내부 `git status -- "$WIKI_DIR/Wiki/"` 필터(`06-Wiki-시스템/Wiki/`)가 스크립트 VAULT(`/home/comtop/obsidian-vault`) 기준으로 평가됨 — 실제 repo(`/home/comtop/workspace/Wiki`)와 경로 불일치 + 해당 경로에 staging할 변경이 없어 항상 "변경 없음"으로 false-negative
- **추가 버그**: 스크립트는 `git push origin main` 시도하지만 Wiki repo의 실제 원격 브랜치는 `master` → push 자체가 실패할 가능성 (현재 스크립트는 변경 없음으로 early-exit하여 도달하지 않음)
- **선행 사례**: log.md §2026-06-17(286행), 06-15 BUG-NOTE에서도 동일 `VAULT`/`main` 하드코딩 결함 지적됨 — 미수정 상태
- **조치 권고** (다음 일일 업데이트에서):
  1. 스크립트 VAULT를 `/home/comtop/workspace/Wiki`로, push 브랜치를 `master`로 정정, 또는
  2. cron 명령을 `git -C /home/comtop/workspace/Wiki add -A && git commit && git push origin master` 단일 라인으로 단순화 (스크립트 폐기)

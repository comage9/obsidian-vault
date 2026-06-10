# 작업 로그

## 2026-05-28

### 03:09 — 백테스트 v3 엔진 전면 재생성 완료
- v3 엔진 적용 (분산투자 20% + 유동성 제한 2% + 동적 슬리피지 0.15~2%)
- 점수 시스템 v3.0 (CAGR×40% + Sharpe×25% - MDD×15% + 신뢰도×20%)
- 2,857개 종목 × 19개 전략 재계산 완료
- 평균 CAGR: 5.30% (현실적)

### 04:06 — Wiki 저장 완료
- `의사결정/백테스트-v3-엔진-완료-20260528.md` 생성

### 07:35 — 장전 분석 스크립트 수정
- `scripts/check_pre_market_analysis.py` import 경로 오류 수정 (src/ + project root 모두 sys.path에 추가)
- 정상 실행 확인 (exit 0)

### 07:35 — Wiki 구조 정비
- `SCHEMA.md` 생성 (domain, conventions, frontmatter, tag taxonomy)
- `index.md` 생성 (페이지 목차)
- 기존 파일: 3개 (의사결정 1, 문제-해결 1, log.md)
### 2026-05-28 08:02 — Wiki Lint: ❌0개 오류 / ⚠️3개 경고

| 검사 항목 | 결과 |
|-----------|------|
| 깨진 Wikilink | 0개 |
| 고립 페이지 | 2개 |
| Frontmatter 누락 | 1개 |
| 전체 페이지 | 5개 |

### 2026-05-28 08:02 — Daily Cleanup: 0개 아카이브, 3개 페이지
### 2026-05-28 10:47 — Wiki Lint: ❌0개 오류 / ⚠️3개 경고

| 검사 항목 | 결과 |
|-----------|------|
| 깨진 Wikilink | 0개 |
| 고립 페이지 | 2개 |
| Frontmatter 누락 | 1개 |
| 전체 페이지 | 5개 |

### 2026-05-28 10:47 — Daily Cleanup: 0개 아카이브, 3개 페이지

### 2026-05-28 11:10 — 문제 사항 문서화
- `문제-해결/ki-ai-trader-미해결-이슈-20260528.md` 생성
- Cron 감시 보고서 기반 미해결 이슈 7건 정리 (LLM 실패, 체결 타임아웃, DB accounts 누락, 자본금 부족, 토큰 리프레시, 종목코드 오류, 계좌 API 공백)
- index.md 갱신 (페이지 수 4개로 증가)

### 2026-05-28 12:04 — Git Auto-Sync: 5개 파일 → GitHub

### 14:50 — Telegram 이상징후 실시간 검증 완료
- 7개 항목 전수 검증: Arena Trader/매수/매도/LLM/계좌API
- 실제 장애: 0건, 모두 로그 노이즈 또는 구조적 한계
- 문서: `개념/telegram-이상징후-검증-20260528.md`

### 15:45 — 2026-05-28 전면 수정 9건 완료
- `의사결정/ki-ai-trader-20260528-전면수정-완료.md` 생성
- 수정 9건: trailing_stop 조건개선, LLM NoneType 방어, 가격필터, OHLCV+호가통합, import경로×2, 트레일링표시, Wiki스크립트5종복원, Telegram 1시간정기보고
- 보류: DB accounts(1회, 재현불가), refresh token(client_credentials 방식)
- index.md 갱신 (5페이지)
### 2026-05-28 22:01 — Wiki Lint: ❌0개 오류 / ⚠️7개 경고

| 검사 항목 | 결과 |
|-----------|------|
| 깨진 Wikilink | 0개 |
| 고립 페이지 | 6개 |
| Frontmatter 누락 | 1개 |
| 전체 페이지 | 9개 |

### 2026-05-28 23:00 — Cleanup: index.md 5페이지
  
### 2026-05-29 00:01 — Git Auto-Sync: 잘못된 script path → 대기 후 workdir 수정
  
### 2026-05-29 01:05 — 후속 작업
- **Wiki Frontmatter 수정**: `문제-해결/ki-ai-trader-is_running-일일손실한도-버그.md`에 YAML frontmatter 추가 (type/created/status/tags)
- **Wiki 크론잡 5종 workdir 설정**: ingest/lint/cleanup/briefing/git-sync에 `/home/comtop/obsidian-vault/06-Wiki-시스템` workdir 적용
- **GitHub Token 설정 완료**: `~/.hermes/.env` 및 `~/.env.hermes`에 GITHUB_TOKEN 저장
- **만두와김밥마을 프로젝트**: GitHub 저장소 생성 (`comage9/mandu-gimbap-lunch-menu`), 코드 push 및 GitHub 실버전(13커밋, 164파일) 로컬에 pull 완료
### 2026-05-29 22:03 — Wiki Lint: ❌0개 오류 / ⚠️7개 경고

| 검사 항목 | 결과 |
|-----------|------|
| 깨진 Wikilink | 0개 |
| 고립 페이지 | 7개 |
| Frontmatter 누락 | 0개 |
| 전체 페이지 | 10개 |

## 2026-06-01 ~ 2026-06-02

### WPPS PBM140MW 출하통보등록 정상화
- 안성5 IB (605177) — 1호차 18 + 2호차 19 = 총 37파렛트
- 비고(col36): "1호차"/"2호차" 규칙 확정
- CAR_OWN_TYP='02' USER운송, data_typ='01' 확정

## 2026-06-03

### KPP PBM110MW 검증 함정 발견
- **핵심**: fn_save는 200 OK + msg=성공 반환하지만 실제 미저장
- **해결책**: 반드시 GET 재조회로 row 존재 확인
- 인증 토큰 60분 만료, 자동 갱신 없음 → fn_login 재호출 필수
- `kpp-verify-search.py` 스크립트 작성

### KPP 6가지 Silent Drop 발견
1. data_typ '02'→'01' (가이드 오류)
2. dlv_dat 10자리 필수
3. truckRequestId는 호차순 정렬 안 됨 (truckSeq 기준 매핑)
4. fn_newRow→그리드 row→fn_save 서버 session 추적 구조
5. PBM140MW.save 직접 신규등록 불가능 (Playwright UI 또는 사용자 수동만)
6. fn_new에 ZIP1_NUM=482 필수

## 2026-06-04

### LS 차량 정보 DB 동기화 완료
- PostgreSQL `ls_vehicle` DB 생성
- 차량-운전자 매핑, 매일 자동 동기화 Cron

### PBM140MW 재시도 금지 규칙 확정
- 중복 등록 방지 규칙 수립
- 재시도 금지, 조회 후 미등록 건만 등록

## 2026-06-05 ~ 2026-06-06

### VF2 전면 점검 (89개 이상 작업)
- DB 통일: SQLite 제거 → PostgreSQL 단일 체계
- 생산대기 표기 `생산대기` 통일
- color2 대문자+공백 통일 (`WHITE 180`)
- 색상 규칙: 크림(Cream)=Ivory, IVORY 1060 로트 적용
- KI AI Trader 트레일링 step 1.2%→2.0% 완화
- Cron 8개 prompt 구조 개선 (발견/제안/액션)

### Hermes 시스템 개선
- Holographic Memory 도입 (SQLite 전용, NumPy 2.4.6)
- hermes-agent 스킬 v2.2.0 통합
- 에이전트 온보딩 가이드 4-Step 확정
- Wiki 74페이지 → GitHub auto-sync

### 이카운트 발주서 작업 (윈도우)
- 윈도우 이카운트 발주서 생성/수정/전체 작업 완료

## 2026-06-07

### Hermes SOUL.md 업데이트
- mandatory-verification 스킬 참조 제거 → 5단계 체크리스트 자체 내장
- Codex CLI → codewhale exec --auto
- agent-runner.sh → delegate_task subagent

### index.md 카탈로그 갱신
- 12페이지 → 74페이지 전체 목록
- Hermes/물류/운영원칙/의사결정 등 모든 카테고리 최신화

### 2026-05-30 22:01 — Wiki Lint: ❌0개 오류 / ⚠️7개 경고

| 검사 항목 | 결과 |
|-----------|------|
| 깨진 Wikilink | 0개 |
| 고립 페이지 | 7개 |
| Frontmatter 누락 | 0개 |
| 전체 페이지 | 10개 |

### 2026-05-30 23:00 — Daily Cleanup: 0개 아카이브, 8개 페이지
### 2026-05-31 22:03 — Wiki Lint: ❌0개 오류 / ⚠️8개 경고

| 검사 항목 | 결과 |
|-----------|------|
| 깨진 Wikilink | 0개 |
| 고립 페이지 | 8개 |
| Frontmatter 누락 | 0개 |
| 전체 페이지 | 11개 |

## 2026-06-01
### 10:00 — vf-project-실행-워크플로우 문서화
- `의사결정/vf-project-실행-워크플로우-20260602.md` 생성
- 마스터/VF-project 분리, IP/venv/esbuild 정정

## 2026-06-02
### 09:00 — Wiki index.md 갱신 (12페이지)
### 22:00 — Wiki Lint: 0개 오류 / 3개 경고 (전체 12페이지)

## 2026-06-04
### 08:00 ~ 23:00 — Windows-Linux 공유 백업 협약
- `의사결정/윈도우-리눅스-공유-백업-협약-20260604.md` 생성
- `의사결정/윈도우-헤르메스-온보딩-가이드.md` 생성
- `운영원칙/에이전트-운영-정책.md` 생성
- 물류 문서 대거 생성 (KPP 함정, LS 19시 표시, PBM140MW 규칙, 차량DB)

## 2026-06-05
### 09:00 ~ 23:00 — Phase2/4 템플릿 + 하네스 + 자가학습 + 텔레그램 우회
- `Hermes/Phase2-교차검증-20260605.md`, `Hermes/Phase4-템플릿확장-20260605.md`
- `Hermes/하네스-엔지니어링-적용-20260605.md`
- `Hermes/Telegram-파일첨부-우회-20260605.md`
- 자가학습 크론 5종 문서화 (`Hermes/자가-학습-Cron/`)
- Wiki 총 30페이지

## 2026-06-06 — VF 바코드 + 온보딩 + KPP 자동화 집중
### 09:00 ~ 23:00 — 대규모 Wiki 확장
- `윈도우-VF-출고바코드-수정-20260606.md`
- `물류/윈도우-권역지-인쇄-20260606.md`
- `물류/VF-통합-계획-v2/v3/v4-20260606.md`
- `물류/KPP/` 문서 4건 (CDP, 출력, PBM140MW, 에이전트전달)
- `물류/쿠팡/LS/` 문서 3건 (쿠키우회, DB동기화, 트래킹PDF)
- `운영원칙/` 문서 3건 (Git정책, 베이스파일자동로드, 보조운영원칙)
- `의사결정/` 문서 9건 (VF검증, Wiki-unindexed, Hermes업그레이드, LS-KPP동기화, MEMORY검증, 온보딩, 세션종결, 작업방식, 운영원칙위반)
- Wiki 총 50+ 페이지

## 2026-06-07 — 이카운트 + LS 인쇄 + 전체 작업
### 09:00 ~ 23:00
- `의사결정/윈도우-전체작업-20260607.md`
- `의사결정/윈도우-이카운트-발주서-생성수정-20260607.md`
- `의사결정/윈도우-이카운트-발주서-전체작업-20260607.md`
- `의사결정/hermes-docs-스킬-통합-20260607.md`
- `Hermes/문서-스킬화-20260607.md`
- Wiki 총 60+ 페이지
- LS PDF 인쇄 스크립트 생성
- KPP EDI 출력 시스템 최종 명세

## 2026-06-08 — 장기기억 시스템 전면 개편 (곰너이 지시)
### 10:00 ~ 18:00
- **카르파티 LLM Wiki 패턴 분석**: 3-Layer + 3-Operation + 2-Special-File 매핑
- **Tool-First Auto-Recall 도입**: §0 시스템 SOUL.md 박제 + mandatory-verification 강화
- **3개 Hermes 스킬 분석**: 장기기억 내용 없음 확인
- **장기기억 7개 문서 생성**: AI아키텍처/카르파티/Auto-Recall/Hermes공식/LTM가이드/통합가이드/하네스분석
- **Holographic External Provider 활성화**: `pip install holographic` + `hermes memory setup`
- **index.md 전면 갱신**: 12→90페이지
- **Git 커밋 8개**: `be43c94` ~ `09edd5e`
### 18:00 ~ 19:00 — Holographic 활성화 + index/log 전면 갱신 + Cross-device sync 강화
- **Holographic External Provider 활성화**: `pip install holographic` → `hermes config set memory.provider holographic` → Status: available ✅
- **index.md 전면 갱신**: 12→90페이지, 디렉토리별 구분 카탈로그
- **log.md 6월 기록 추가**: 6/1~6/8 작업 내역 보강
- **log.md 자동 cron 생성**: 매일 23:30 `2de1e4b75f8f`, Discord 보고
- **온보딩 가이드 §7 갱신**: 장기기억 5종 + Holographic 설정 추가
- **통합-가이드 상태 변경**: "결정 대기"→"✅ Windows 활성 완료"
- **Git 커밋**: `f114237` (3 files) + `9b51dc0` (1 file)
### 19:00 ~ 20:00 — Sources/Output 폴더 신설 + 용량 검증 cron
- **Sources 폴더**: `Wiki/Sources/` 원본 자료 보관소 (텍스트 Git 추적, 바이너리 차단)
- **Output 폴더**: `Wiki/Output/` AI 생성 결과물 날짜별 아카이브
- **바이너리 Sources**: `Wiki/Sources/바이너리/README.md` — Git 제외, 파일 목록만 기록
- **`.gitignore` 강화**: `*.pdf *.png *.jpg *.zip *.xlsx` 등 바이너리 확장자 Git 차단
- **용량 검증 cron**: 매일 12시 `d3349950eecd` — 50MiB 경고 / 100MiB 위험
- **온보딩 가이드 §7**: Sources/Output + 용량 검증 cron 추가
- **Git 커밋**: `5a91c83` (통합-가이드+log)
### 20:00 ~ 20:30 — 표준 프롬프트 템플릿 3종 신설 (wiki-workflow 스킬)
- **wiki-workflow 스킬 생성**: `/ingest`(Source→Wiki), `/update`(Source→Wiki업데이트), `/output`(Wiki→결과물)
- **템플릿 문서 3건**: `Output/템플릿/01-ingest / 02-update / 03-output`
- **온보딩 가이드 §7**: wiki-workflow 스킬 + Output/템플릿 추가
- **Git 커밋**: `cc332f8` (Sources/Output/용량검증)

## 2026-06-08

### 20:30 ~ 20:40 — Linux Hermes: Git merge + SOUL.md/크론 정리
- **Git pull**: Windows `bd60f04` 병합 성공 → `2af00cb` (index.md 충돌 해결, upstream 채택)
- **wiki-workflow 템플릿 3종 수신**: `/ingest`, `/update`, `/output` — Output/템플릿/ 적용 완료
- **Sources/Output 구조 동기화 완료**
- Linux 푸시: `2af00cb` → GitHub origin/master

## 2026-06-07

### Hermes SOUL.md 업데이트
- mandatory-verification 스킬 참조 제거 → 5단계 체크리스트 자체 내장
- Codex CLI → codewhale exec --auto
- agent-runner.sh → delegate_task subagent
- 크론 3개 프롬프트 동기화 (KI AI Trader/VF2 생산계획/VF2 프로젝트)

### index.md 카탈로그 갱신 (본 세션, 병합 전)
- 충돌 해소: Windows 버전(91페이지) 채택 — 테이블 형식 카탈로그 유지

### log.md 일일 자동 기록 cron 생성
- ID: `2ed0ab22c954` / 매일 23:30 / session_search 기반 / Git push 포함

## 2026-06-09
### 03:46 — Hermes Self Nightly 자가 학습 실행
- `Hermes/자가-학습-Cron/Hermes-Self-Nightly-20260609.md` 생성 (hermes-agent SKILL.md v2.2.0→v2.3.0, mandatory-verification §0 Tool-First Auto-Recall 신설 감지)
- `운영원칙/에이전트-운영-정책.md` 갱신 (Hermes Self Nightly 반영)
|  15시·16시·DB매칭·텍스트전달 삭제, PDF인쇄 disabled 유지) -- 2026-06-10
현재 12개 cron으로 정리됨

## 2026-06-10

### 21:30 — LLM Wiki 3-Type 활용 (영상 기반) + vf-dashboard 통합 (Linux)
- **vf-dashboard 통합**: VF2 사이드바 "VF 출차관리" 메뉴 추가 완료
- **SOUL.md 개편 전파**: Linux CLI에 SOUL.md 3개 섹션 + rules.json 8개 prefill 적용
- **LLM Wiki 3-Type 활용 (YouTube: LLM Wiki 천배 가치)**: 거울형/두뇌형/기억형 통합 4작업
  - **A. 거울형 cron** (`a4ff6603273d`, `0 1,13 * * *`, mirror_report.py)
  - **B. Wiki 카테고리 4분할** (브랜드/사업/기술/자기사고)
  - **C. 세션 작업 일지 cron** (`977012de5665`, 매일 23:30)
  - **D. 곰너이님 브랜드 가이드** (`브랜드/곰너이-브랜드-가이드-20260610.md`)
- **거울형 첫 보고서**: `/자기사고/거울형-보고서/2026-06-10-거울형-주간보고서.md` 생성
- **작업 일지 첫 자동화**: `/작업일지/2026-06-10-작업일지.md` 26KB 생성

### 22:10 — 거울형 쿼리 버그 수정 + INDEX 갱신 + Git push (Linux)
- **거울형 쿼리 버그 수정**: WEEK_AGO ISO 문자열 → epoch float 변환
- **거울형 cron schedule 변경**: `0 23 * * 0` → `0 1,13 * * *` (매일 01:00, 13:00)
- **Wiki/index.md 갱신**: 74→77 페이지, 마지막 갱신 6/10
- **3-WAY 완료**: Wiki + README + Git push

### 23:00 — [SOUL개편] LLM Wiki 3전략 하네스 검증 + 3틱 적용 / 이유: 거울형/기억형 전략을 현재 시스템에 적용 / 다음: cron 실행 결과 모니터링
- 하네스 검증: LLM Wiki 두뇌/기억/거울 3전략 분석 완료
- 틱①: §0 Auto-Recall에 `read_file(log.md, offset=-20)` 추가
- 틱②: log.md 템플릿 `- [작업] 설명 / 이유: X / 다음: Y` 형식으로 개선
- 틱③: 자료 섭취 cron 생성 (d56641a9a113, 매일 06:00, wiki-workflow)

### 23:30 — Wiki log.md 일일 갱신 (cron)
|- 누락된 6/10 페이지 6건 log.md 추가
|- index.md 갱신 (페이지 카탈로그 + 수량 업데이트)
|- Git add + commit + push

### (~21:30) — 스킬 체계화 일괄 적용
|- `의사결정/스킬-체계화-일괄-적용-20260610.md` 생성
|- 전체 50+개 스킬 중 25개에 trigger_condition + output_template 적용

### (~21:30) — 스킬 체계화 2차 적용 + Wiki Graph MCP
|- `의사결정/스킬-체계화-2차적용-20260610.md` 생성
|- 2차 스킬 체계화 적용 (체계화 미적용 스킬 처리)

### (~21:00) — LS 크론 통합
|- `의사결정/LS-크론-통합-20260610.md` 생성
|- 16개 → 12개로 LS 크론 통합 정리

### (~21:00) — SOUL.md 개편 전파 가이드
|- `운영원칙/SOUL-개편-전파-가이드-20260610.md` 생성
|- 다른 Hermes 에이전트(Telegram/Linux)용 SOUL 개편 + rules.json 전파 절차 문서화

### (~20:30) — Hermes Persistent Memory PostgreSQL 마이그레이션
|- `의사결정/Hermes-Persistent-Memory-PostgreSQL-마이그레이션-20260610.md` 생성
|- Holographic(SQLite) → PostgreSQL 마이그레이션 완료 (Linux)

### (~18:00) — 유훈식 AI&UX 세미나 시리즈 분석
|- `의사결정/유훈식-AI-세미나-시리즈-분석-20260610.md` 생성
|- 3개 YouTube 영상 기반 AI&UX 세미나 분석 정리


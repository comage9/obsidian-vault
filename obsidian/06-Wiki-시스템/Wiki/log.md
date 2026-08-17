
### 2026-06-26 06:01 — Git Auto-Sync: 1개 파일 → GitHub

### 2026-06-26 06:01 — Git Auto-Sync (cron 실행 결과 기록)
- 스크립트: `obsidian/06-Wiki-시스템/.scripts/wiki-git-push.sh`
- 실행: `bash obsidian/06-Wiki-시스템/.scripts/wiki-git-push.sh` (cwd=`/home/comtop/workspace/Wiki`)
- 결과: ✅ 성공 — 1개 파일 변경 (커밋 `6a9b2b7`), 원격 master 동기화 완료 (`HEAD = origin/master = 6a9b2b7c15567dd47939fe4b544c3747bc93444e`)
- 변경 파일: `obsidian/06-Wiki-시스템/Wiki/자기사고/거울형-보고서/2026-06-26-거울형-주간보고서.md` (신규, +38)
- 잔존: `log.md` 미추적 (이번 sync 종료 시점에 기록용으로 수정됨 — 다음 sync 사이클에서 정리 예정)

### 2026-08-16 14:45 — VF2 Project Nightly 자가 점검
- 백엔드/프론트 기동 확인 (API 6개 엔드포인트 200 OK)
- DB 핵심 3개 테이블 데이터 존재 (outbound_records 489K, production_logs 15K, inventory_baseline 4K)
- **운영 침묵 69일** — production_logs 최신 2026-06-09
- **디스크 83% WARNING 초과** — 29일간 +11%p 재가속
- 마스터 테이블 4개 비어있음 (master_specs, inventory_items, machine_plans, machine_users)
- 파일: Hermes/자가-학습-Cron/VF2-Project-Nightly-20260816.md

###

## 2026-06-26

### 08:20 — KI AI Trader 순차 보고서
- PDF OCR 통합 (Phase D1~D3): PyMuPDF 텍스트 추출 → 부족 페이지 EasyOCR → PixelRAG 매칭
- Wikipedia Stock Market PDF 검증: 15,000자 추출, Stock_market (score 0.658) 매칭 성공
- 한글 폰트 깨짐 한계 (OCR fallback 작동)
- 파일: 리서치/ki-ai-trader-순차-보고서-20260626.md

### 09:14 — React Mindmap UI 구축
- Neo4j Browser 외부 의존 탈피, 자체 React UI 채택 (이식성 + 보안 + UX)
- 스택: React 19 + Vite 8 + cytoscape.js (port 3000), FastAPI 백엔드 (port 8765)
- API 6종 구현: /api/stats, /api/graph/all, /api/strategies, /api/orders/recent 등
- 파일: 리서치/react-mindmap-ui-20260626.md

### 11:15 — KI AI Trader 시스템 구성 및 문제 보고서
- 긴급(C1~C4): 일일 손실 한도 오작동(-29.8%), HTTP 429 Rate Limit 11건, 모니터링 루프 과다 호출(9시 118건), 손절/익절 cap 불일치
- 설계 결함(S1~S4): 손실 카운터 시장가 기준, RateLimiter 멀티스레드 우회 가능, 일일 손실 WARNING만 처리
- 다른 에이전트 전달용 보고서, 시뮬레이션 운영 심각 영향
- 파일: 리서치/system-issues-20260626.md


### 05:30 — VF2 Production Plan Nightly
- 백엔드/프론트엔드 7일째 DOWN 지속 (06-19 16:58 backend.log 마지막), vf2_backend_bin 0건
- 디스크 89% CRITICAL 임박 (06-17 67% → 06-26 89%, +2.4%p/1일 가속)
- PostgreSQL Docker 정상 (28 tables, pg_stat stale fallback), 메모리 정상
- 파일: Hermes/자가-학습-Cron/VF2-Production-Plan-Nightly-20260626.md

### 06:33 — VF2 Project Nightly
- 06-24 → 06-26 2일간 부재 (Production Plan 변형 1시간 전 작성)
- 06-22~24 사이 재부팅 1회 발생 + 디스크 +10%p 폭증
- systemd/s6 미등록 함정 재발, 외부 스캐너 활동 (06-19 16:58, 66.132.195.107 GET /login 401)
- 파일: Hermes/자가-학습-Cron/VF2-Project-Nightly-20260626.md

### 13:00 — 거울형 주간보고서
- 2026-06-19~26 기간: 미결 질문 0건, 반복 패턴 0건, 시스템 개선점 0건, 콘텐츠 소재 0건, 사업 신호 0건
- 입력 메시지 0건 (지난 주 사용자 메시지 없음)
- 파일: 자기사고/거울형-보고서/2026-06-26-거울형-주간보고서.md

### 의사결정 폴더
- 오늘 생성된 의사결정 파일 0건

###

### 2026-06-27 06:00 — Git Auto-Sync: 1개 파일 → GitHub

### 2026-06-28 10:47 — Git Auto-Sync: 2개 파일 → GitHub

### 2026-06-28 18:01 — Git Auto-Sync: 1개 파일 → GitHub

###
## 2026-06-28

### 13:00 — 거울형 주간보고서 (2026-06-21~28)
- 미결 질문 0건, 반복 패턴 0건, 콘텐츠 소재 0건, 사업 신호 0건
- 입력 메시지 0건 (지난 주 사용자 메시지 없음)
- 파일: 자기사고/거울형-보고서/2026-06-28-거울형-주간보고서.md

### 의사결정 폴더
- 오늘 생성된 의사결정 파일 0건

###

### 2026-06-29 06:01 — Git Auto-Sync: 1개 파일 → GitHub

### 2026-06-29 06:01 — Wiki Git Auto-Sync 결과 기록 (cron 컨텍스트)
- **상황**: cron workdir `/home/comtop/obsidian-vault/06-Wiki-시스템`에서 정상 실행, 1개 파일 (06-29 거울형-주간보고서) commit `97c06bd` + push 성공
- **함정 진단**: 작업 컨텍스트 workdir `/home/comtop/workspace/ki-ai-trader`에서는 `.scripts/wiki-git-push.sh` 부재처럼 보였으나 — **스크립트 부재 아님** (3개 인스턴스 모두 존재). N+2 메타-함정이 아닌 **크로스 프로젝트 workdir 함정**(2026-06-16 실측 패턴) 동시 발화였음
- **log.md commit 순서 race 임시 우회**: 스크립트 성공 분기(commit→push→log.md append) 특성상 이번 commit `97c06bd`에 log 항목 미포함. 잔존 modified log.md 별도 commit 필요

### 2026-06-29 18:01 — Git Auto-Sync: 1개 파일 → GitHub

###
## 2026-06-29

### 06:33 — VF2 Nightly 자가 점검
- 백엔드/프론트 7일째 DOWN (5176/5174 미응답, 프로세스 0건)
- 디스크 93%→41% 급락 (-52%p/2일), 사용자 수동 cleanup 추정
- 운영 침묵 19일 (max_date 기준 06-09)

### 13:00 — 거울형 주간보고서 (2026-06-22~29)
- 미결 질문 0건, 반복 패턴 0건, 사업 신호 0건
- 입력 메시지 0건 (지난 주 사용자 메시지 없음)
- 파일: 자기사고/거울형-보고서/2026-06-29-거울형-주간보고서.md

### 06:01/18:01 — Git Auto-Sync
- 06:01: 1개 파일 → GitHub (97c06bd)
- 06:01: 로그 누락분 보완 (d7cfb8f)
- 18:01: 1개 파일 → GitHub (1f3e938)

### 의사결정 폴더
- 오늘 생성된 의사결정 파일 0건

###

###
## 2026-06-30

### 05:30 — VF2 Production Plan Nightly 자가 점검 (1차 cron)
- **디스크 44% CRITICAL 해소**: 06-26 89% → 06-30 44% (-45%p/4일)
- **백엔드/프론트엔드 11일째 DOWN** (06-19 마지막 로그, systemd 미등록 3회째)
- **DB 변동 0건**: production_logs 15,886건, 28 tables (06-26과 동일)
- **운영 침묵 21일**: max_date 2026-06-09 → 06-30

### 06:30 — VF2 Project Nightly 자가 점검 (2차 cron, 이중 검증)
- 1차 cron과 **완전 동일** — DB 변동 0건 독립 재확인
- **systemd 등록 미실행 카운트 4회** (§7 #26 CRITICAL)
- 백엔드 PID 0건, Listen 포트 0건 (5174/5176), 디스크 44% 유지

### 13:00 — 거울형 주간 자기 분석 보고서 (cron weekly)
- 기간: 2026-06-23 ~ 2026-06-30 (7일)
- 미결 질문 0건, 반복 패턴 0건, 콘텐츠 소재 0건
- 입력 user 메시지 0개 (cron-only 기간)
- Telegram Home 자동 알림 발송

###

### 2026-07-01 18:01 — Git Auto-Sync: 1개 파일 → GitHub

###
## 2026-07-01

### 05:33 — VF2 Production Plan Nightly 자가 점검 (1차 cron)
- **백엔드 12일째 DOWN**: 06-19 마지막 로그, systemd 미등록 상태 지속
- **디스크 47%** (+3%p): 06-30 44% → 47% 상승, CRITICAL 후 재증가 추세
- **DB 변동 0건**: production_logs 15,886건, 28 tables 유지
- **운영 침묵 22일**: max_date 2026-06-09 → 07-01

### 06:32 — VF2 Project Nightly 자가 점검 (2차 cron, 이중 검증)
- 1차 cron과 **완전 동일** — 모든 지표 변동 0건 독립 재확인
- 백엔드 12일째 DOWN 지속, systemd 미등록 카운트 누적
- 1회차 대비 디스크/DB/포트 상태 변화 없음

### 13:00 — 거울형 주간 자기 분석 보고서 (cron weekly)
- 기간: 2026-06-24 ~ 2026-07-01 (7일)
- 미결 질문 0건, 반복 패턴 0건, 사업 신호 0건
- 입력 user 메시지 0개 (cron-only 기간)
- Telegram Home 자동 알림 발송

### 18:01 — Git Auto-Sync
- 거울형 주간보고서 1개 파일 → GitHub (f022901)

### 의사결정 폴더
- 오늘 생성된 의사결정 파일 0건

###

### 12:02 — Git Auto-Sync
- 변경사항 없음 (exit 0)
- 4-way 검증: git status 비어있음, ahead/behind 0건, log.md 정상 종료
- 스크립트: /home/comtop/obsidian-vault/06-Wiki-시스템/.scripts/wiki-git-push.sh (healthy)

### 2026-07-02 18:02 — Git Auto-Sync: 1개 파일 → GitHub

###
## 2026-07-02

### 05:31 — VF2 Production Plan Nightly 자가 점검 (1차 cron)
- **백엔드 13일째 DOWN**: 06-19 마지막 로그, systemd 미등록 상태 지속
- **디스크 49%** (+2%p): 07-01 47% → 49% 상승, 임계 50% 임박
- **DB 변동 0건**: production_logs 15,886건, 28 tables 유지
- **운영 침묵 23일**: max_date 2026-06-09 → 07-02

### 06:32 — VF2 Project Nightly 자가 점검 (2차 cron, 이중 검증)
- 1차 cron과 **완전 동일** — 모든 지표 변동 0건 독립 재확인
- 백엔드 13일째 DOWN 지속, PID 0건, Listen 포트 0건
- 디스크 49% 유지, 메모리 4.9Gi/14Gi 정상

### 12:02 — Git Auto-Sync
- 변경사항 없음 (exit 0)
- 4-way 검증: git status 비어있음, ahead/behind 0건

### 13:00 — 거울형 주간 자기 분석 보고서 (cron weekly)
- 기간: 2026-06-25 ~ 2026-07-02 (7일)
- 미결 질문 0건, 반복 패턴 0건, 사업 신호 0건
- 입력 user 메시지 0개 (cron-only 기간)

### 18:02 — Git Auto-Sync
- 거울형 주간보고서 1개 파일 → GitHub (623601e)

### 의사결정 폴더
- 오늘 생성된 의사결정 파일 0건

### 06:31 — VF2 Project Nightly 자가 점검 (cron 27c1b2555f38)
- **백엔드/프론트엔드 정상 가동**: 07-04 기동 후 연속 (PID 41169/41279), 포트 5174/5176 LISTEN 확인
- **디스크 57%** (+5%p/2일, 평균 +2.5%p/일) — 06-30 44% 해소 후 5일째 재가속 지속, 90%까지 ~13일 잔여
- **Swap 50%** (2.0/4.0Gi) — 07-03 95%에서 개선, 관찰 지속
- **DB 변동 0건**: production_logs 15,886건, 28 tables (07-03와 동일)
- **운영 침묵 26일** (max_date 2026-06-09 → 07-05, +2일) — 임계치 ≥3일 대폭 초과
- **결함 지표 정체**: 6-튜플 중복 4행, 빈 필드 5건, WHITE 180 158건 — 모두 07-03 대비 변동 없음
- **production_plans 테이블 부재** 지속 (to_regclass → NULL)
- 보고서: `Hermes/자가-학습-Cron/VF2-Project-Nightly-20260705.md`

### 의사결정 폴더
- 오늘 생성된 의사결정 파일 0건

###

###
## 2026-07-05

### 06:31 — VF2 Project Nightly 자가 점검 (cron 27c1b2555f38)
- **백엔드/프론트엔드 정상 가동**: 07-04 기동 후 연속 (PID 41169/41279), 포트 5174/5176 LISTEN 확인
- **디스크 57%** (+5%p/2일, 평균 +2.5%p/일) — 06-30 44% 해소 후 5일째 재가속 지속, 90%까지 ~13일 잔여
- **Swap 50%** (2.0/4.0Gi) — 07-03 95%에서 개선, 관찰 지속
- **DB 변동 0건**: production_logs 15,886건, 28 tables (07-03와 동일)
- **운영 침묵 26일** (max_date 2026-06-09 → 07-05, +2일) — 임계치 ≥3일 대폭 초과
- **결함 지표 정체**: 6-튜플 중복 4행, 빈 필드 5건, WHITE 180 158건 — 모두 07-03 대비 변동 없음
- **production_plans 테이블 부재** 지속 (to_regclass → NULL)
- 보고서: `Hermes/자가-학습-Cron/VF2-Project-Nightly-20260705.md`

### 13:00 — 거울형 주간 자기 분석 보고서 (cron weekly)
- 기간: 2026-06-28 ~ 2026-07-05 (7일)
- 미결 질문 0건, 반복 패턴 0건, 사업 신호 0건
- 입력 user 메시지 0개 (cron-only 기간)
- 파일: `자기사고/거울형-보고서/2026-07-05-거울형-주간보고서.md`

### 의사결정 폴더
- 오늘 생성된 의사결정 파일 0건

###

## 2026-07-06

### 06:31 — VF2 Project Nightly 자가 점검 (2차 cron, 이중 검증)
- **백엔드/프론트엔드 재발 DOWN**: 07-04 기동 후 ~48시간 만에 재종료, PID 0건, 포트 5174/5176 미Listen
- **디스크 60% WARNING 재가속 가속화**: 07-05 57% → 07-06 60% (+3%p/1일, 평균 +3%p/일), 10일 내 CRITICAL 재진입 예측
- **운영 침묵 27일째** (max_date 2026-06-09 → 07-06), 임계치 ≥3일 대폭 초과
- **DB 변동 0건**: production_logs 15,886건, 28 tables (07-05와 동일)
- **systemd 등록 미실행 13일째** — 06-23 권고 이후 미실행, 다음 재부팅 시 즉시 재발 (§7 #38 CRITICAL)
- 파일: `Hermes/자가-학습-Cron/VF2-Project-Nightly-20260706.md`

### 의사결정 폴더
- 오늘 생성된 의사결정 파일 0건

###

### 2026-07-06

### 06:31 — VF2 Project Nightly 자가 점검 (2차 cron, 이중 검증)
- **백엔드/프론트엔드 재발 DOWN**: 07-04 기동 후 ~48시간 만에 재종료, PID 0건, 포트 5174/5176 미Listen
- **디스크 60% WARNING 재가속 가속화**: 07-05 57% → 07-06 60% (+3%p/1일, 평균 +3%p/일), 10일 내 CRITICAL 재진입 예측
- **운영 침묵 27일째** (max_date 2026-06-09 → 07-06), 임계치 ≥3일 대폭 초과
- **DB 변동 0건**: production_logs 15,886건, 28 tables (07-05와 동일)
- **systemd 등록 미실행 13일째** — 06-23 권고 이후 미실행, 다음 재부팅 시 즉시 재발 (§7 #38 CRITICAL)
- 파일: `Hermes/자가-학습-Cron/VF2-Project-Nightly-20260706.md`

### 13:00 — 거울형 주간 자기 분석 보고서 (cron weekly)
- 기간: 2026-06-30 ~ 2026-07-06 (7일)
- 미결 질문 0건, 반복 패턴 0건, 사업 신호 0건
- 입력 user 메시지 0개 (cron-only 기간)
- 파일: `자기사고/거울형-보고서/2026-07-06-거울형-주간보고서.md`

### 의사결정 폴더
- 오늘 생성된 의사결정 파일 0건

###

## 2026-07-07

### 05:42 — VF2 Production Plan Nightly 자가 점검 (1차 cron)
- **백엔드/프론트엔드 수동 기동 UP**: 06-30 11일째 DOWN → 07-07 수동 `./start.sh` + `npm run dev`로 복구 (PID 300244/300511), 포트 5174/5176 LISTEN, `/api/health` OK
- **systemd/s6 미등록 4회째 지속** — 06-23 권고 이후 미실행, 재부팅 시 즉시 재발 (§7 #26 CRITICAL)
- **디스크 62% WARNING 임박** — 06-30 44% 해소 후 7일 만에 +18%p 재증가 (+2.6%p/일), 70%까지 ~3일 잔여
- **운영 침묵 28일째** (max_date 2026-06-09 → 07-07, +7일), 임계치 ≥3일 대폭 초과
- **DB 변동 0건**: production_logs 15,886건, 28 tables (06-30와 동일)
- 파일: `Hermes/자가-학습-Cron/VF2-Production-Plan-Nightly-20260707.md`

### 11:31 — VF2 Production Plan Nightly 자가 점검 (cron)
- **백엔드/프론트엔드 재부팅 후 미복구**: 07-07 수동 UP 후 재부팅 발생(up 4 min), systemd/s6 미등록 5회째로 자동 복구 실패 — 재부팅 함정 입증
- **디스크 72% WARNING 초과** — 06-30 44% 해소 후 18일 만에 +28%p 재증가, 85% CRITICAL까지 ~13일 잔여
- **운영 침묵 39일째** (max_date 2026-06-09 → 07-18, +11일), 임계치 ≥3일 대폭 초과
- **DB 완전 정적 11일째**: production_logs 15,886건, status 분포, 6-튜플 중복, 빈 필드, color2 variant 모두 변동 0
- **production_plans 테이블 부재 지속** (to_regclass → NULL), 1.xlsx import 누락 단서
- PostgreSQL Docker restart policy로 자동 복구(Up 4 min), DB 28 tables 정상
- 파일: `Hermes/자가-학습-Cron/VF2-Production-Plan-Nightly-20260718.md`

### 의사결정 폴더
- 오늘 생성된 의사결정 파일 0건

###

## 2026-08-11 (화)

### 16:00~17:30 — VF-new 로케이션 전역 검색 구현
- 모든 페이지에서 로케이션 코드로 검색 → 해당 로케이션 품목 표시
- Backend: ?location= param on master/specs + inventory/integrated
- Frontend: isLocationPattern() 유틸, inventory-table 정확일치 부스트
- 커밋: 939fa69, 473b1ae, 7c4af42, 44fa627

### 16:40 — VF 3개월 미출고 자동 동기화 + 수동 지정 보존
- _sync_vf_no_outbound_to_db: OFF 방향 sync 제거 (수동 지정 보존)
- spec-edit-dialog: "VF 3개월 미출고" 버튼 추가

### 17:30 — KPP MCP 서버 py3.11 venv 전환
- py3.13+pydantic_core → py3.11 venv (VF와 동일 패턴)
- Hermes config: command=venv/python.exe 직접 실행
- 게이트웨이 재시작 필요

### 17:45 — MCP v2 업데이트 분석 (Bloom AI 영상)
- FastMCP→MCPServer, Sampling/Roots deprecated, WebSocket 제거
- 현재 VF/KPP MCP: stdio → 영향 없음, SDK v1→v2 마이그레이션 하위호환

### 14:00 — LS 14시 통합 루프 (cron)
- VF API: date=2026-08-14 data=[] (신선·빈값, stale 아님)
- LS 조회(ls_automation): 로그인 성공 welcomePage, VF67_H **0건**
- 템플릿 Batch Create(90626/90628/90269): **실패** — create 경로 Keycloak 고착 / WEB-GATEWAY-SESSION 미확보
- ls_orders_2026-08-14.json = []
- ls_watch supervisor: 15:00 대기 중
- skill ls-coupang: not found (skipped)

## 2026-08-16 (일)

### 14:10 — LS 14시 통합 루프 (cron)
- VF API: date=2026-08-16 data=0 (신선·빈값, stale 아님)
- LS 로그인(patchright): 성공 welcomePage, 쿠키 12개 저장
- 사전 조회 VF67_H: 0건 → 템플릿 Batch Create(90626/90628/90269) **200 성공**
- 재조회: 3건 (SUBMITTED) — 29466212(90269/3호차), 29466213(90626/1호차), 29466214(90628/2호차)
- ls_orders_2026-08-16.json: 3건 (plate/driver null — 배차 전 상태)
- VF 출차관리: 0건 → 추가 등록 대상 없음
- skill ls-coupang: not found (skipped) — playwright-automation / vf-dispatch-request 참조로 대체

###
## 2026-08-16

### 14:10 — LS 14시 통합 루프 (cron)
- VF API: date=2026-08-16 data=0 (신선·빈값, stale 아님)
- LS 로그인(patchright): 성공 welcomePage, 쿠키 12개 저장
- 사전 조회 VF67_H: 0건 → 템플릿 Batch Create(90626/90628/90269) **200 성공**
- 재조회: 3건 (SUBMITTED) — 29466212(90269/3호차), 29466213(90626/1호차), 29466214(90628/2호차)
- ls_orders_2026-08-16.json: 3건 (plate/driver null — 배차 전 상태)
- VF 출차관리: 0건 → 추가 등록 대상 없음

### 14:38 — 거울형 주간보고서 자동 생성 (cron weekly)
- 기간: 2026-08-09 ~ 2026-08-16 (7일)
- 미결 질문 0건, 반복 패턴 0건, 콘텐츠 소재 0건, 시스템 개선점 0건, 사업 신호 0건
- 입력 메시지 0개 (cron-only 기간)
- 파일: 자기사고/거울형-보고서/2026-08-16-거울형-주간보고서.md

### 14:45 — VF2 Project Nightly 자가 점검 (cron)
- 백엔드/프론트 기동 확인 (API 6개 엔드포인트 200 OK)
- DB 핵심 3개 테이블 데이터 존재 (outbound_records 489K, production_logs 15K, inventory_baseline 4K)
- **운영 침묵 69일** — production_logs 최신 2026-06-09
- **디스크 83% WARNING 초과** — 29일간 +11%p 재가속
- 마스터 테이블 4개 비어있음 (master_specs, inventory_items, machine_plans, machine_users)
- 파일: Hermes/자가-학습-Cron/VF2-Project-Nightly-20260816.md

### 의사결정 폴더
- 오늘 생성된 의사결정 파일 0건

###

## 2026-08-16

### 14:10 — LS 14시 통합 루프 (cron)
- VF API: date=2026-08-16 data=0 (신선·빈값, stale 아님)
- LS 로그인(patchright): 성공 welcomePage, 쿠키 12개 저장
- 사전 조회 VF67_H: 0건 → 템플릿 Batch Create(90626/90628/90269) **200 성공**
- 재조회: 3건 (SUBMITTED) — 29466212(90269/3호차), 29466213(90626/1호차), 29466214(90628/2호차)
- ls_orders_2026-08-16.json: 3건 (plate/driver null — 배차 전 상태)
- VF 출차관리: 0건 → 추가 등록 대상 없음

### 14:38 — 거울형 주간보고서 자동 생성 (cron weekly)
- 기간: 2026-08-09 ~ 2026-08-16 (7일)
- 미결 질문 0건, 반복 패턴 0건, 콘텐츠 소재 0건, 시스템 개선점 0건, 사업 신호 0건
- 입력 메시지 0개 (cron-only 기간)
- 파일: 자기사고/거울형-보고서/2026-08-16-거울형-주간보고서.md

### 14:45 — VF2 Project Nightly 자가 점검 (cron)
- 백엔드/프론트 기동 확인 (API 6개 엔드포인트 200 OK)
- DB 핵심 3개 테이블 데이터 존재 (outbound_records 489K, production_logs 15K, inventory_baseline 4K)
- **운영 침묵 69일** — production_logs 최신 2026-06-09
- **디스크 83% WARNING 초과** — 29일간 +11%p 재가속
- 마스터 테이블 4개 비어있음 (master_specs, inventory_items, machine_plans, machine_users)
- 파일: Hermes/자가-학습-Cron/VF2-Project-Nightly-20260816.md

### 의사결정 폴더
- 오늘 생성된 의사결정 파일 0건

###

## 2026-08-17

### 05:31 — VF2 Production Plan Nightly 자가 점검 (1차 cron)
- 백엔드/프론트 **DOWN** (systemd 미등록 6회째, 14시간째 미복구)
- DB production_logs 15,886건 (started 10,916, pending 4,967, ended 3)
- **운영 침묵 70일** — production_logs 최신 2026-06-09 (max_date 기준)
- **디스크 73% (WARNING 해소)** — 08-16 83% → 73% (-10%p, 대폭 개선)
- 미해결 결함 4건 잔존 (6-튜플 중복, 데크타일 color2 빈값, 빈 moldNumber, color2 대소문자)
- 마스터 테이블 4개 비어있음 (master_specs, inventory_items, machine_plans, machine_users)
- 파일: Hermes/자가-학습-Cron/VF2-Production-Plan-Nightly-20260817.md

### 의사결정 폴더
- 오늘 생성된 의사결정 파일 0건

###
### 14:02 — LS 14시 통합 루프 (cron)
- VF API: up (5176), 오늘(8/17) ls-data 0건 (신선·빈값, stale 아님) / 어제 파일 date=2026-08-16 data=3
- LS 로그인(patchright): 성공 welcomePage, WEB-GATEWAY-SESSION 확보
- 사전 조회 VF67_H(8/17): 0건 → 템플릿 Batch Create(90626/90628/90269) **200 성공**
- 재조회: 3건 (SUBMITTED) — 29489030(90269/3호차/11T), 29489031(90626/1호차/5T), 29489032(90628/2호차/5T)
- ls_orders_2026-08-17.json: 3건 (plate/driver null — 배차 전 상태)
- VF 출차관리: 0건 → 추가 등록 대상 없음 (경기89바1454 매칭 대상 없음)
- Circuit Breaker: ls-daily/ls-loop-14h 모두 🟢 OK
- skill ls-coupang: not found (skipped) — vf-dispatch-request + 기존 _ls_14h_loop2 스크립트 재사용


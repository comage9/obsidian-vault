
### 2026-06-26 06:01 — Git Auto-Sync: 1개 파일 → GitHub

### 2026-06-26 06:01 — Git Auto-Sync (cron 실행 결과 기록)
- 스크립트: `obsidian/06-Wiki-시스템/.scripts/wiki-git-push.sh`
- 실행: `bash obsidian/06-Wiki-시스템/.scripts/wiki-git-push.sh` (cwd=`/home/comtop/workspace/Wiki`)
- 결과: ✅ 성공 — 1개 파일 변경 (커밋 `6a9b2b7`), 원격 master 동기화 완료 (`HEAD = origin/master = 6a9b2b7c15567dd47939fe4b544c3747bc93444e`)
- 변경 파일: `obsidian/06-Wiki-시스템/Wiki/자기사고/거울형-보고서/2026-06-26-거울형-주간보고서.md` (신규, +38)
- 잔존: `log.md` 미추적 (이번 sync 종료 시점에 기록용으로 수정됨 — 다음 sync 사이클에서 정리 예정)

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

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

## 2026-05-30

### 01:00 ~ 02:20 — KPP 파렛트 자동화 + LS 쿠팡 연동

#### WPPS 출하통보등록 (PBM140MW)
- 안성5 IB(605177) — 1호차 18 + 2호차 19 = 총 37파렛트 저장 (2026-06-01)
- 비고(col36): "1호차"/"2호차" 규칙 확정

#### WPPS 납품/반납요청 (PBM110MW)
- 6월 납품요청: 1건 (5/29→하차 6/5, N11, 200파렛트)

#### 쿠팡 LS 로그인 및 연동
- `ls.coupang.com` 로그인 성공 (mokicom)
- VF67(유원)HUB→부천1HUB 3건 (1호차:경기89바1454 / 2호차:경기90자3674 / 3호차:광주90바1703)

#### 스킬 정리
- `kpp-pallet-automation` 제거 → `kpp-pallet-management` 통합
- 워크플로우 C 추가 (Phase1: 15:00 LS검색 + Phase2: 저녁 WPPS등록)
### 2026-05-30 22:01 — Wiki Lint: ❌0개 오류 / ⚠️7개 경고

| 검사 항목 | 결과 |
|-----------|------|
| 깨진 Wikilink | 0개 |
| 고립 페이지 | 7개 |
| Frontmatter 누락 | 0개 |
| 전체 페이지 | 10개 |

### 2026-05-30 23:00 — Daily Cleanup: 0개 아카이브, 8개 페이지

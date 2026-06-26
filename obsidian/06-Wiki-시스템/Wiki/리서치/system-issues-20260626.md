# KI AI Trader 시스템 구성 및 문제 보고서

**작성일**: 2026-06-26
**작성자**: Hermes Agent (현재 세션)
**목적**: 다른 에이전트에게 전달하여 문제 수정 진행
**긴급도**: 🔴 **HIGH** - 시뮬레이션 운영에 심각한 영향

---

## 0. TL;DR (다른 에이전트가 먼저 봐야 할 부분)

### 🔴 즉시 수정 필요 (Critical)

| # | 문제 | 영향 | 우선순위 |
|:-:|:----|:----|:----:|
| **C1** | **일일 손실 한도 검증이 잘못 작동** (-29.8%, -44.45%) | 거래 차단됨 | 🔴 **긴급** |
| **C2** | **HTTP 429 Rate Limit 11건** (8:22, 9:05, 9:22, 9:23) | 시세 조회 실패 | 🔴 **긴급** |
| **C3** | **모니터링 루프 과다 호출** (9시 118건, 10시 96건) | Rate Limit 직격 | 🔴 **긴급** |
| **C4** | **손절/익절 cap 설정이 realtime_monitor에서 안 먹힘** (5% vs 8% 불일치) | 전략 손실 | 🟡 **높음** |

### 🟡 설계 결함

| # | 문제 | 영향 |
|:-:|:----|:----:|
| S1 | 일일 손실 카운터가 **시장가 기준**으로 계산 | 손실 과대평가 |
| S2 | RateLimiter가 `_make_request` 내부에만 적용 | 멀티 스레드 우회 가능 |
| S3 | 모니터링 루프가 분당 2~5회 호출 | 키움 API 부담 |
| S4 | `Daily loss limit exceeded`이 WARNING만 (거래 차단 X) | 손실 방치 |

---

## 1. 시스템 구성 내역

### 1.1 디렉토리 구조

```
/home/comtop/workspace/
├── ki-ai-trader/                       # 메인 프로젝트
│   ├── .venv-3.12/                     # Python 3.12.13 (uv 격리)
│   ├── .venv-3.11.bak/                 # 백업 (롤백 대비)
│   ├── logs/                           # 로그 폴더 (30일 보관)
│   │   ├── arena_trader_2026-06-25.log     # 현재 활성 로그 (17,569 라인)
│   │   ├── arena_trader_2026-06-26.log     # 06-26 로그
│   │   ├── daily_runner_*.log
│   │   ├── mindmap_api.log             # FastAPI 로그
│   │   ├── mindmap_ui.log              # Vite 로그
│   │   └── ... (총 80+ 로그 파일)
│   ├── src/
│   │   ├── trading/
│   │   │   ├── realtime_monitor.py     # 10분 모니터링 ★ 문제 다수
│   │   │   ├── executor.py
│   │   │   ├── strategies/             # 3개 전략 (momentum/contrarian/day)
│   │   ├── data_sources/
│   │   │   ├── korean_ocr.py           # EasyOCR
│   │   │   ├── pdf_ocr.py              # PyMuPDF + OCR
│   │   │   └── investor_flow.py        # OPT10059
│   │   ├── crawlers/
│   │   │   ├── naver_finance.py
│   │   │   ├── daum_finance.py
│   │   │   ├── dart_disclosure.py      # OpenAPI 사용 안 함
│   │   │   ├── krx_market.py
│   │   │   ├── pixelrag_client.py      # 시각 RAG
│   │   │   └── hybrid_search.py        # 한글→영문
│   │   ├── database/
│   │   │   └── connection.py
│   │   └── api/
│   │       └── neo4j_routes.py         # FastAPI 13 라우트
│   ├── mindmap-ui/                     # React + Vite (port 3000)
│   ├── windows_collector/              # Windows USB 수집기
│   ├── scripts/
│   │   ├── backtest_5year.py
│   │   ├── backtest_5min.py
│   │   ├── backtest_with_investor_signal.py
│   │   ├── apply_slippage_commission.py
│   │   ├── sync_to_neo4j.py
│   │   ├── build_mindmap.py
│   │   ├── mindmap_cron.sh
│   │   └── mindmap_ui_start.sh
│   └── docs/
│       ├── SEQUENTIAL_REPORT_*.md
│       ├── BACKTEST_REPORT_*.md
│       ├── REACT_MINDMAP_UI_*.md
│       └── SYSTEM_ISSUES_20260626.md   # ★ 이 문서
├── Wiki/                               # Obsidian vault
└── dashboard/                          # 통합 대시보드
    └── STATUS.md
```

### 1.2 핵심 파일 (수정 대상)

| 파일 | 역할 | 문제 |
|:-----|:-----|:----|
| `src/trading/realtime_monitor.py` | **10분 모니터링** | C1, C3, C4, S1, S3, S4 |
| `kiwoom_api.py` | REST API 클라이언트 | C2, S2 (RateLimiter) |
| `src/trading/strategies/momentum_reversal.py` | 전략 (손익 -5%/+8%) | OK |
| `src/trading/strategies/contrarian_reversal.py` | 전략 | OK |

### 1.3 환경

| 항목 | 값 |
|:-----|:---:|
| Python | 3.12.13 (.venv-3.12) |
| 키움 REST API | 초당 5회 제한 |
| 시뮬레이션 모드 | SIMULATION |
| 계좌 모드 | `account_mode` env |
| 시드 머니 | 1,000,000원 |
| 매수한도 | 500,000원/종목 |
| 최대 보유 | 4종목 |
| Neo4j | Docker 5.26.27 (port 7687) |
| PostgreSQL | Docker 16-alpine (port 5432) |
| Python 프로세스 | PID 224699 (arena_trader.py) |
| FastAPI | PID ~253588 (uvicorn, port 8765) |
| Vite | PID ~255756 (port 3000) |

### 1.4 Cron 작업

| 시간 | 작업 |
|:----|:----|
| `0 16 * * 1-5` | Neo4j 동기화 |
| `30 16 * * 1-5` | 마인드맵 갱신 |
| `0 17 * * *` | 백업 |
| `0 * * * *` | 대시보드 |
| `30 8 * * 1-5` | 일일 트레이딩 시작 |

---

## 2. 발견된 문제 (상세)

### 🔴 C1: 일일 손실 한도 검증 오작동

**증상**:
```
[WARNING] Daily loss limit exceeded: 29.80% > 5.00%   (235건 중 116건)
[WARNING] Daily loss limit exceeded: 44.45% > 5.00%   (235건 중 119건)
```

**원인 추정**:
1. `realtime_monitor.py`의 일일 손실 계산이 **누적 평가손익**을 사용
2. 매 10분마다 재계산 → 누적 손실 29.80% 또는 44.45% (시드머니 대비)
3. 한도 5% → 초과 → 거래 차단

**문제점**:
- **WARNING만 로깅**하고 실제 거래는 차단 안 함 (의도적? 버그?)
- 5% 한도가 시드머니(100만원) 기준으로 **50,000원**, 하지만 평가손익 29.80%는 298,000원
- 누적 손실이 시장가 변동에 따라 계속 증가 → 44.45%까지 치솟음

**확인할 위치**:
- `src/trading/realtime_monitor.py` - `_check_daily_loss_limit()` 또는 유사 함수
- `multi_agent_arena.py` - `risk_engine` 로직

**수정 방향**:
- **A안**: 한도 검증 시 **실현 손실만** (매도 확정된 손실)
- **B안**: 한도 검증 시 **일일 P&L reset** (자정마다)
- **C안**: 한도 검증 자체를 **INFO 레벨**로 변경 (로깅만, 거래 차단 X)

### 🔴 C2: HTTP 429 Rate Limit (키움 API)

**증상**:
```
08:22:44 [ERROR] 시세 조회 실패: API 요청 실패: HTTP 429 - 알 수 없는 에러
09:05:39 [ERROR] 시세 조회 실패: API 요청 실패: HTTP 429 - 알 수 없는 에러
09:22:55 [ERROR] 시세 조회 실패: API 요청 실패: HTTP 429 - 알 수 없는 에러
09:23:15 [ERROR] 시세 조회 실패: API 요청 실패: HTTP 429 - 알 수 없는 에러
```

**원인**:
- 키움 API: 초당 5회 제한
- 모니터링 루프가 초당 5회 초과
- 8:22 → 9:05 → 9:22, 9:23 (40초 간격 2회 연속) → 동시 다발

**확인할 위치**:
- `kiwoom_api.py` - `RateLimiter.wait_if_needed()`
- `realtime_monitor.py` - `check_interval`

**수정 방향**:
- **RateLimiter 단일 적용 확인**: `_make_request` 내부 + 동시 요청 시 `_rate_limiter.acquire()`
- **재시도 백오프**: 429 시 지수 백오프 (1초 → 2초 → 4초 → 8초)
- **동시 호출 방지**: asyncio.Lock 또는 threading.Semaphore

### 🔴 C3: 모니터링 루프 과다 호출

**증상**:
```
매 분당 WARNING 수:
  09시: 118건
  10시: 96건
  11시: 22건
```

**원인**:
- `realtime_monitor.py`의 `check_interval`이 너무 짧음 (10초 미만?)
- 매 10분마다 호출되어야 하는데 → 매 분당 여러 번 호출
- 각 호출이 보유 종목 수만큼 API 요청 (4종목 × N회 = 다발)

**확인할 위치**:
- `src/trading/realtime_monitor.py:Config.check_interval`
- `realtime_monitor.py:_run_monitoring_loop()`

**수정 방향**:
- **check_interval=600초 (10분) 엄격 준수**
- **N개 종목 = 1회 호출** (각 종목별 호출 X)
- **시간 분산**: 4종목 → 1분 간격으로 4번 분할 호출

### 🔴 C4: 손절/익절 cap 불일치

**증상**:
```
[INFO] 익절 수준: [8.0]% (I안 cap 5%)   ← 라벨은 5%, 실제 값 8%
```

**원인**:
- `realtime_monitor.py`에서 `profit_take_levels: [8.0]` 설정
- 로그 메시지는 "I안 cap 5%" (이전 주석 잔재)
- 메시지/코드 불일치 → 혼란

**확인할 위치**:
- `src/trading/realtime_monitor.py:106` (로깅 메시지)
- `src/config/settings.py` (실제 cap 값)

**수정 방향**:
- **로깅 메시지 일치화**: `profit_take_levels` 값 그대로 출력
- **또는**: cap 5%로 통일 (손실 회피)

### S1: 일일 손실 카운터 시장가 계산

**원인**:
- 손실 = `(매입가 - 현재가) × 수량`
- 현재가가 실시간 변동 → 매 10분마다 변동
- 시장가로 평가 시 일중 손실이 누적 → 한도 초과 자주 발생

**수정**:
- **기준가 사용**: 매수 직후 가격을 기준, 익절/손절 시까지 고정 평가
- **또는**: 평가손익이 아닌 **실현손익**만 카운트

### S2: RateLimiter 우회 가능성

**현황**:
- `kiwoom_api.py:_make_request()` 내부에서만 `wait_if_needed()` 호출
- 멀티 스레드 환경에서 Race Condition 가능

**수정**:
- `_make_request` 진입 시 `threading.Lock` + RateLimiter
- 동시 호출 방지 (asyncio.Semaphore)

### S3: 모니터링 루프 API 부담

**원인**: C3과 동일. **4종목 × 매 분당 2~5회 = 분당 10~20 API 호출**

**수정**:
- **순차 호출** (한 종목씩, 0.2초 간격)
- **시간 분산**: 분당 1회씩 4분에 걸쳐
- **최소 호출**: 시세 캐싱 (30초 TTL)

### S4: WARNING만 로깅

**현재**: `[WARNING] Daily loss limit exceeded`만 로깅, 거래는 진행

**확인할 의도**:
- 처음 설계가 의도한 동작인지?
- 의도했다면 OK (다만 로그 과다)
- 의도하지 않았다면 → 손절 즉시 실행 필요

---

## 3. 시계열 분석

### 3.1 일일 손실 추이 (시간대별)

| 시간 | 일일 손실 |
|:----|:----:|
| 09:01 | 29.80% 시작 (피엔에이치테크 매수 직후) |
| 09:01~09:11 | 29.80% 유지 |
| 09:11 이후 | 44.45%로 증가 (다른 매수 영향?) |
| 10:00~11:00 | 44.45% 유지 |

### 3.2 HTTP 429 발생 시각

| 시각 | 종목 | 비고 |
|:----|:----:|:-----|
| 08:22:44 | 239890 | 피엔에이치테크 매수 후 |
| 09:05:39 | (N/A) | 시세 조회 실패 |
| 09:22:55 | 038530 | 모니터링 10분 주기 추정 |
| 09:23:15 | 038530 | 재시도 직후 |

### 3.3 토큰 갱신 (12건)

| 시각 | 비고 |
|:----|:-----|
| 08:00, 08:30, 08:50 | 시뮬레이션 시작 후 빈번 |
| 09:01, 09:01 | 매수 직후 |

**원인**: `run_arena_trader.py`가 매 30분~1시간마다 토큰 갱신, OAuth 만료 시간 짧음

---

## 4. 수정 우선순위

### Phase 1 (즉시, 1시간)

1. **모니터링 check_interval 강제 600초** (C3)
2. **RateLimiter 재시도 백오프** (C2)
3. **일일 손실 검증 완화** (C1) - WARNING만 유지하되 빈도 줄이기

### Phase 2 (단기, 1일)

4. **모니터링 루프 1회 호출 = N종목 묶음** (S3)
5. **손절/익절 cap 로깅 메시지 일치** (C4)
6. **RateLimiter threading.Lock 추가** (S2)

### Phase 3 (중기, 1주)

7. **일일 손실 기준 변경** (실현 손실 vs 평가 손실) (S1)
8. **시세 캐싱** (30초 TTL) (S3 강화)
9. **모니터링 비동기화** (asyncio)

---

## 5. 다른 에이전트 인수인계 사항

### 5.1 환경

```bash
# 프로젝트 경로
cd /home/comtop/workspace/ki-ai-trader

# Python 가상환경
.venv-3.12/bin/python3

# 시뮬레이션 시작
nohup .venv-3.12/bin/python3 run_arena_trader.py > logs/sim.log 2>&1 &

# 로그 확인
tail -f logs/arena_trader_$(date +%Y-%m-%d).log
```

### 5.2 데이터 확인

```python
# 일일 손실 한도 값 확인
import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, user='hermes', password='hermes1234', dbname='ki_ai_trader')
cur = conn.cursor()
cur.execute("SELECT id, current_cash, initial_cash FROM accounts WHERE account_type='stock' LIMIT 5")
print(cur.fetchall())
conn.close()

# 현재 보유 종목
cur.execute("SELECT s.stock_code, s.stock_name, o.quantity, o.executed_price, o.created_at FROM orders o JOIN stocks s ON o.stock_id=s.id WHERE o.order_status='PENDING' OR o.order_status='FILLED'")
```

### 5.3 수정 시 확인해야 할 파일

| 파일 | 라인 | 내용 |
|:----|:---:|:-----|
| `src/trading/realtime_monitor.py` | - | `_check_daily_loss_limit`, `_run_monitoring_loop`, `Config.check_interval` |
| `kiwoom_api.py` | - | `RateLimiter`, `_make_request` |
| `run_arena_trader.py` | - | 모니터링 루프 호출부 |

### 5.4 핵심 파일 읽는 순서

1. `src/trading/realtime_monitor.py` (가장 먼저)
2. `multi_agent_arena.py` (Risk Engine)
3. `kiwoom_api.py` (RateLimiter)
4. `run_arena_trader.py` (호출 패턴)

### 5.5 테스트 방법

```bash
# 1. 시뮬레이션 종료
pkill -f "run_arena_trader.py"

# 2. 백업
cp src/trading/realtime_monitor.py src/trading/realtime_monitor.py.bak3

# 3. 수정 후 재시작
nohup .venv-3.12/bin/python3 run_arena_trader.py > logs/sim_test.log 2>&1 &

# 4. 5분 대기 후 로그 확인
sleep 300
grep -E "ERROR|WARNING" logs/arena_trader_$(date +%Y-%m-%d).log | head -20

# 5. 이전 대비 개선 확인
# - Daily loss limit WARNING 횟수 ↓
# - HTTP 429 발생 ↓
# - 모니터링 호출 빈도 ↓
```

---

## 6. 관련 파일 및 위치

### 6.1 로그 파일 (문제 증거)

```
logs/arena_trader_2026-06-25.log    (17,569 라인, 현재 활성)
logs/arena_trader_2026-06-26.log    (06-26 로그)
logs/daily_runner_*.log             (cron 일일 실행)
logs/autorestart.log                (자동 재시작)
logs/cron_runner.log                 (cron 결과)
logs/mindmap_api.log                 (FastAPI)
logs/mindmap_ui.log                  (Vite)
```

### 6.2 관련 스크립트

```
scripts/backup_workspace.py          # 백업
scripts/sync_to_neo4j.py             # Neo4j 동기화
scripts/mindmap_ui_start.sh         # 마인드맵 시작
```

### 6.3 보고서 (현재까지)

```
docs/SEQUENTIAL_REPORT_20260625.md   # 7단계 작업
docs/BACKTEST_REPORT_20260625.md     # 백테스트 종합
docs/PYTHON_312_UPGRADE_20260625.md  # Python 업그레이드
docs/PIXELRAG_STUDIO_INTEGRATION_20260625.md  # PixelRAG
docs/REACT_MINDMAP_UI_20260626.md    # React UI
docs/SEQUENTIAL_REPORT_20260626.md   # PDF OCR
docs/SYSTEM_ISSUES_20260626.md      # ★ 이 문서
```

---

## 7. 연락/위키

- **Wiki 경로**: `Wiki/obsidian/06-Wiki-시스템/Wiki/리서치/`
- **현 보고서 Wiki 동기화**: `system-issues-20260626.md`
- **Git 커밋 이력**: `ki-ai-trader/` 저장소

---

## 8. 다음 에이전트가 할 일 (체크리스트)

- [ ] `realtime_monitor.py`의 `check_interval` 값 확인 (현재 10분 미만 의심)
- [ ] `Daily loss limit exceeded` 로직 위치 파악
- [ ] 5% 한도 값이 어디서 설정되는지 (`settings.py` 또는 `realtime_monitor.py`)
- [ ] 키움 API RateLimiter가 멀티 스레드 안전한지 확인
- [ ] `kiwoom_api.py`의 재시도 로직에 백오프 있는지 확인
- [ ] 수정 후 Phase 1 → Phase 2 → Phase 3 순서로 진행
- [ ] 각 수정 후 5분 이상 가동 → 로그 카운트 비교
- [ ] 백테스트는 별도 (`backtest_5year.py` 또는 `backtest_with_investor_signal.py`)

---

**작성 완료 시각**: 2026-06-26 (장 시작 후)
**관련 시스템**: KI AI Trader (SIMULATION 모드)
**데이터 출처**: logs/arena_trader_2026-06-25.log (17,569 라인 분석)
**위키 동기화**: ✅ Wiki/.../system-issues-20260626.md
**Git 커밋**: 진행 예정
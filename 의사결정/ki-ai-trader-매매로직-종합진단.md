# ki-ai-trader 매매 로직 종합 진단 보고서

**저장일:** 2026-05-25
**분석 범위:** 전체 매매 로직, 종목 선정 로직, 공휴일 체크, 손절/익절 로직
**분석 에이전트:** Hermes + 5개 독립 AI Agent (트레이딩/리스크/시장/시스템/검증)

---

## 개요

ki-ai-trader는 키움증권 API 기반 자동매매 시스템입니다. 약 **10만원 미만 저가 종목**을 대상으로,
기술적 분석 + AI 분석 신호를 조합하여 매수/매도 결정을 내립니다.

### 아키텍처 요약

```
┌─────────────────────┐
│  Market Hours       │  ← market_hours.py: 장 시간 + 공휴일 체크
├─────────────────────┤
│  Auto Stock Picker  │  ← auto_stock_picker.py: 신규 종목 발굴
├─────────────────────┤
│  SimpleTradingSt.   │  ← simple_trading_strategy.py: 기술적 분석
├─────────────────────┤
│  AI Client          │  ← ai_client.py: Ollama/Z AI 신호 생성
├─────────────────────┤
│  AITradingOrch.     │  ← ai_trading_orchestrator.py: AI 실행 통합
├─────────────────────┤
│  Executor (x3)      │  ← executor.py + trading_executor.py (중복)
├─────────────────────┤
│  StopLossExecutor   │  ← stop_loss_executor.py: 손절/익절 자동
└─────────────────────┘
```

---

## ⛔ CRITICAL BUG (긴급 수정 필요)

### 🚨 B1. 매수/매도 주문 실패 시 재시도 없음

**파일:** `src/trading/executor.py`
**함수:** `_execute_buy_signal()` (line 636~642), `_execute_sell_signal()` (line 717~723)

```python
# 현재 코드 (executor.py:636-642)
order_result = await self.api_client.place_order(order_request)
if order_result:
    logger.info(f"Buy order placed: ...")
else:
    logger.error(f"Failed to place buy order: {stock_code}")  # ❌ 재시도 없음
```

**문제:** `_execute_buy_signal()`과 `_execute_sell_signal()`는 주문 실패 시 단순히 로그만 남기고 종료합니다.
한 번의 네트워크 오류, API 일시적 장애로 매매 기회가 영원히 손실됩니다.

**참고:** 동일 파일에 `_place_order_with_retry()` 함수가 이미 존재합니다 (line 468~491).
하지만 `_execute_buy_signal()`은 이 함수를 사용하지 않고 직접 `place_order`를 호출합니다.

**수정 방안:**
```python
# executor.py _execute_buy_signal() 내부
if self.api_client:
    order_result = await self._place_order_with_retry(order_request, max_attempts=3)
    if order_result:
        ...  # 기존 성공 처리
    else:
        ...  # 기존 실패 처리
```

---

### 🚨 B2. 매수 금액 하드코딩 (5,000,000원)

**파일:** `src/trading/executor.py`
**함수:** `_execute_buy_signal()` (line 566)

```python
# 현재 코드 (executor.py:566)
max_limit = min(self.risk_limits.max_position_size, 5000000)  # ❌ 500만원 하드코딩
```

**문제:**
- `settings.MAX_POSITION_SIZE`를 바꿔도 500만원으로 고정 캡
- `risk_limits.max_position_size = 10,000,000` 이지만, `min()`에서 500만원으로 클리핑
- 전략 변경 시 코드 직접 수정 필요

**수정 방안:**
```python
# settings.py에 MAX_ORDER_AMOUNT 추가
max_limit = min(
    self.risk_limits.max_position_size,
    getattr(settings, "MAX_ORDER_AMOUNT", 5000000)
)
```

---

### 🚨 B3. AI 신호 Confidence 필터링 누락 위험

**파일:** `src/trading/executor.py`
**함수:** `_process_trading_signals()` (line 510)

```python
# 현재 코드 (executor.py:510)
if signal and signal.confidence > 0.7:  # ❌ 0.7 임계값 고정
```

**문제:**
- 모든 AI 신호가 동일한 confidence 0.7 임계값 사용
- AI 모델에 따라 confidence 분포가 다를 수 있음 (Ollama vs Z AI)
- confidence가 항상 0.0~1.0으로 정규화된다는 보장 없음
- `TradingSignal.confidence`가 None이면 비교 자체가 실패

**수정 방안:**
```python
# 설정 기반 임계값
min_confidence = getattr(settings, "MIN_SIGNAL_CONFIDENCE", 0.7)
if signal and signal.confidence is not None and float(signal.confidence) > min_confidence:
```

---

### 🚨 B4. AI 손절/익절 Executor 주문 재시도 없음

**파일:** `src/trading/stop_loss_executor.py`
**함수:** `_execute_sell_order()` (line 197~261)

```python
# 현재 코드 (stop_loss_executor.py:222-228)
result = await account_mode_manager.place_order(...)
if result:
    ...  # 성공 처리
else:
    logger.error(f"❌ 매도 주문 실패: {stock_name}")  # ❌ 재시도 없음
    return None
```

**문제:** 손절가는 가격이 도달했다가 이탈할 수 있으므로, **한 번 실패로 손절 기회를 영원히 잃는 것은 심각한 문제**입니다.
손절/익절은 시간 민감도가 가장 높은 주문입니다.

**수정 방안:**
```python
# stop_loss_executor.py - retry 로직 추가
for attempt in range(1, 4):  # 최대 3회 재시도
    result = await account_mode_manager.place_order(...)
    if result:
        return result
    await asyncio.sleep(2 ** attempt)  # 지수 백오프
logger.error(f"❌ 매도 주문 최종 실패 (3회 재시도): {stock_name}")
return None
```

---

### 🚨 B5. Executor 3중 구조로 인한 정책 불일치

**파일 1:** `src/trading/executor.py` (1008줄) — AI 전략 기반 주문 실행
**파일 2:** `src/trading/trading_executor.py` (324줄) — 단순 매수/매도 래퍼
**파일 3:** `trading_executor.py` (루트, 53줄) — Kiwoom API 직접 래퍼

**문제:**
| 항목 | executor.py | trading_executor.py | 루트 executor |
|------|-------------|---------------------|---------------|
| 재시도 | 내부함수만 있음 | 없음 | 3회 retry 있음 |
| 계좌번호 | `settings.DEFAULT_ACCOUNT_NO` | `account_mode_manager` | client.target_account |
| 슬리피지 보정 | 없음 | 99% 마진 있음 | 없음 |
| 수수료 반영 | 없음 | 없음 | 없음 |

**수정 방안:** 단일 Executor로 통일하고, retry·계좌·슬리피지 정책을 settings.py 기반으로 일원화

---

## ⚠️ IMPORTANT BUG (중요 수정 권장)

### 🟡 B6. SimpleTradingStrategy 설정 하드코딩

**파일:** `src/trading/simple_trading_strategy.py` (line 95~117)

**하드코딩된 값들:**
```python
# line 95-108: fallback 하드코딩 + line 110-117 하드코딩
self.min_change_rate = 2.0           # 상승률 2% 이상
self.max_price_per_stock = 300000    # ❌ 종목당 최대 30만원
self.max_total_investment = 1.0      # ❌ 현금의 100% 사용
self.min_technical_score = 40.0      # ❌ 기술적 점수 최소 40점
self.excluded_stocks = {'285130': '푸른소나무'}  # ❌ 하드코딩
```

**문제:**
- `excluded_stocks`는 DB나 설정 파일에서 관리해야 함
- `max_price_per_stock = 300,000원` — 너무 낮아 대부분 종목 매수 불가
- `min_change_rate = 2.0%` — 장 마감 직전 2% 상승 종목이 실제로 드뭄

**수정 방안:**
```python
# settings.py에 추가
class Settings:
    TRADING_MIN_CHANGE_RATE: float = 2.0
    TRADING_MAX_PRICE_PER_STOCK: int = 300000
    TRADING_MAX_TOTAL_INVESTMENT: float = 1.0
    TRADING_MIN_TECHNICAL_SCORE: float = 40.0
    EXCLUDED_STOCKS: dict = {}  # DB에서 관리

# 사용
self.min_change_rate = settings.TRADING_MIN_CHANGE_RATE
```

---

### 🟡 B7. 손절/익절 Trailing Stop 최고가 갱신 로직 미약

**파일:** `src/trading/stop_loss_executor.py` (line 153~189)

```python
# 현재 코드 - trailing stop이 현재가 기반으로만 갱신
# 최고가(peak) 추적이 없음 → 이틀 연속 하락 시 과거 고점에서 손절 불가
```

**문제:** `last_stop_prices`에 마지막 계산된 손절가만 저장하고, 실제 peak 가격을 추적하지 않습니다.
3% 수익 후 1% 하락 → 다시 3% 수익 → 1% 하락... peak가 갱신되지 않아 손절가가 올라가지 않습니다.

**수정 방안:**
```python
# peak 가격 추적 추가
self.peak_prices: Dict[str, float] = {}  # {stock_code: highest_price}

# trailing stop 계산 시 peak 기준
peak = self.peak_prices.get(stock_code, purchase_price)
peak = max(peak, current_price)  # peak 갱신
self.peak_prices[stock_code] = peak

trailing_stop_price = peak * (1 - self.trailing_stop_distance)
```

---

### 🟡 B8. RiskManagementSellStrategy 하드코딩된 종목코드

**파일:** `src/trading/risk_management_sell_strategy.py`

```python
# 함수 기본 인자에 하드코딩 (line 72, 204, 317)
async def execute_partial_sell(self, stock_code: str = "112610", ...)  # ❌ 씨에스윈드 고정
async def adjust_trailing_stop(self, stock_code: str = "112610", highest_price: float = 65950.0, ...)  # ❌ 고정
async def manage_risk_exposure(self, target_stock_code: str = "112610", ...)  # ❌ 고정
```

**문제:** 이 전략은 특정 종목(씨에스윈드) 전용으로 작성되었습니다.
기본 인자로 종목코드를 하드코딩하면 재사용성과 유지보수성이 떨어집니다.

**수정 방안:**
```python
# 기본 인자 제거, 호출 시 반드시 전달
async def execute_partial_sell(self, stock_code: str, sell_quantity: int = 1, ...)
```

---

## 🔧 IMPROVEMENT (구조 개선)

### 🟢 I1. 공휴일 데이터 연간 갱신 문제

**파일:** `src/trading/market_hours.py` (line 12~38)

현재는 `KOREAN_MARKET_HOLIDAYS_2026`로 하드코딩되어 있습니다.
2027년이 되면 자동 갱신되지 않고, 2026년 공휴일로 잘못 체크합니다.

**수정 방안 A — CSV 파일:**
```python
# data/market_holidays.csv
date,description
2026-01-01,신정
2026-02-16,설날연휴
...

# market_hours.py
import csv
from pathlib import Path

HOLIDAYS_FILE = Path(__file__).parent.parent / "data" / "market_holidays.csv"
KOREAN_MARKET_HOLIDAYS = set()
if HOLIDAYS_FILE.exists():
    with open(HOLIDAYS_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            KOREAN_MARKET_HOLIDAYS.add(datetime.strptime(row['date'], '%Y-%m-%d').date())
```

**수정 방안 B — (권장) API 연동:**
```python
# 한국거래소 KRX 공휴일 API (https://open.krx.co.kr)
# 또는 네이버/카카오 캘린더 API 연동
# fallback: CSV 파일
```

---

### 🟢 I2. AI 신호 파이프라인 복잡도

**현재 흐름:**
```
Stock DB 조회
  → SimpleTradingStrategy (기술적 지표 계산)
    → StockSelectionAI (선정 결과 AI 분석)
      → AIClient (Ollama → Z AI fallback)
        → AITradingOrchestrator (통합 실행)
          → executor.py (주문 실행)
```

**문제:**
- 체인이 7단계로 너무 김
- 모든 단계가 실패할 경우 거래 불가
- 신호 지연: 분석 완료 시점에 이미 가격 변동 가능

**개선 방안:**
```python
# AI 분석을 간소화하고, 기술적 분석 우선 결정 후 AI로 검증
1. 기술적 지표 계산 (SimpleTradingStrategy)
2. 조건 충족 시 AI 분석 (병렬: portfolio + individual)
3. AI confidence > 0.6 → 주문 실행
4. 실패 시 재시도 3회 (지수 백오프)
```

---

### 🟢 I3. 동적 종목 스캐너에 설정 분리

**파일:** `src/trading/dynamic_stock_scanner.py`

Scanner의 조건(최소 거래량, 가격 범위, 거래대금 등)이 설정 기반이 아닌 경우가 많습니다.

**권장:** 설정 기반 + 런타임 오버라이드 가능하도록 `settings.SCANNER_*` 추가

---

### 🟢 I4. AITradingManager 명령어 처리 - 주문 결과 검증 부족

**파일:** `src/trading/ai_trading_manager.py`

사용자 명령(TELEGRAM)을 받아 매수/매도할 때, `place_order()` 호출 후 응답 검증이 충분하지 않습니다.
실제 체결되었는지 확인하는 폴링 로직이 없습니다.

**수정 방안:** `_check_order_status()` (executor.py:753)를 공유 유틸 함수로 분리하고, 모든 명령 처리 후 호출

---

### 🟢 I5. ReportService 텔레그램 전송 방식

**파일:** `src/services/hourly_report.py`

현재 `ReportService.send()`를 통해 직접 텔레그램 전송.
Hermes의 `send_message`로 통일하면 알림 관리가 일원화됩니다.

---

## 🗺️ 전체 시각적 맵

```mermaid
flowchart TB
    subgraph "시장 시간 체크"
        MH[market_hours.py] -->|공휴일/주말 체크| HR[hourly_report.py]
        MH -->|장 시간 체크| EX[executor.py]
    end

    subgraph "종목 선정"
        DS[dynamic_stock_scanner.py] -->|조건 스캔| ASP[auto_stock_picker.py]
        ASP -->|후보 목록| STS[simple_trading_strategy.py]
        SSA[stock_selection_ai.py] -->|AI 분석| STS
    end

    subgraph "신호 생성"
        STS -->|기술적 지표| EX
        AI[ai_client.py (Ollama→Z AI)] -->|AI 신호| ATO[ai_trading_orchestrator.py]
        ATO -->|통합 결정| EX
    end

    subgraph "주문 실행 (3개 중복!)"
        EX_MAIN[executor.py ❌재시도없음]
        TRADING_EX[trading_executor.py]
        ROOT_EX[trading_executor.py(루트) ✅재시도있음]
    end

    subgraph "손절/익절"
        SLE[stop_loss_executor.py ❌재시도없음 ❌peak추적없음]
        ADSL[ai_dynamic_stop_loss.py]
        ADSL -->|AI 손절가| SLE
    end

    EX -->|매매 신호| EX_MAIN
    EX_MAIN -->|주문| KW[키움증권 API]

    SLE -->|손절 신호| KW

    style EX_MAIN fill:#ff6b6b,color:#fff
    style SLE fill:#ff6b6b,color:#fff
    style EX fill:#ffd43b
```

---

## 🏆 우선순위별 작업 제안

### Phase 1 — 긴급 (즉시 수정)
| ID | 작업 | 파일 | 예상 시간 |
|----|------|------|-----------|
| B1 | `_execute_buy/sell_signal()`에 retry 적용 | executor.py:636,717 | 10분 |
| B2 | 500만원 하드코딩을 설정화 | executor.py:566 | 5분 |
| B4 | StopLossExecutor에 retry 적용 | stop_loss_executor.py:222 | 10분 |
| B5 | Executor 3중 구조 단일화 + `_place_order_with_retry` 통합 | executor.py 전체 | 30분 |

### Phase 2 — 중요 (금주 내)
| ID | 작업 | 파일 | 예상 시간 |
|----|------|------|-----------|
| B6 | 설정 하드코딩 제거, settings.py 기반 | simple_trading_strategy.py | 15분 |
| B7 | Trailing Stop peak 추적 로직 추가 | stop_loss_executor.py:153 | 15분 |
| B3 | Confidence 임계값 설정화 | executor.py:510 | 5분 |
| I1 | 공휴일 CSV/API 기반 전환 | market_hours.py | 20분 |

### Phase 3 — 개선 (다음 주)
| ID | 작업 | 파일 | 예상 시간 |
|----|------|------|-----------|
| B8 | 하드코딩 종목코드 제거 | risk_management_sell_strategy.py | 10분 |
| I2 | AI 신호 파이프라인 단순화 | ai_trading_orchestrator.py | 1시간 |
| I4 | 명령 처리 후 체결 검증 | ai_trading_manager.py | 20분 |
| I5 | Telegram 전송 Hermes 통일 | hourly_report.py | 10분 |

---

## 📋 파일 경로 정리

| 역할 | 경로 | 라인 수 |
|------|------|---------|
| 시장 시간 체크 | `src/trading/market_hours.py` | 123 ✅ (공휴일 추가 완료) |
| 시간대 알림 | `src/services/hourly_report.py` | 56 ✅ (공휴일 체크 추가 완료) |
| 기술적 분석 전략 | `src/trading/simple_trading_strategy.py` | 833 ⚠️ 설정 하드코딩 |
| AI 전략 실행기 | `src/trading/executor.py` | 1008 🔴 재시도 없음 |
| 단순 매매 래퍼 | `src/trading/trading_executor.py` | 324 |
| Kiwoom 직접 래퍼 | `trading_executor.py` | 53 ✅ 재시도 있음 |
| 손절/익절 실행기 | `src/trading/stop_loss_executor.py` | 347 🔴 재시도 없음 |
| AI 오케스트레이터 | `src/trading/ai_trading_orchestrator.py` | 752 |
| AI 클라이언트 | `src/ai/ai_client.py` | 733 |
| 종목 선정 AI | `src/ai/stock_selection_ai.py` | 472 |
| 자동 종목 선정 | `src/trading/auto_stock_picker.py` | 224 |
| 리스크 매도 전략 | `src/trading/risk_management_sell_strategy.py` | 623 ⚠️ 하드코딩 |
| 통합 오케스트레이터 | `src/trading/integrated_orchestrator.py` | 301 |
| AutoPilot | `src/trading/autopilot.py` | 721 |

---

## 참고: Agent 분석 결과 요약

5개 독립 AI Agent의 분석 결과 취합:

| Agent | 발견 건수 | 핵심 지적 |
|-------|-----------|-----------|
| 🟢 트레이딩 | 4건 | retry 부재, 3중 executor, 마진/슬리피지 미보정 |
| 🟢 리스크 | 3건 | trailing stop peak 미추적, stop 부재 시 폴백 부재 |
| 🟢 시장 | 3건 | 공휴일 CSV/API 전환 필요, 장 시작전 주문 위험 |
| 🟢 시스템 | 3건 | 중복 executor, 비동기 락 부재, 과도한 로깅 |
| 🟢 검증 | 2건 | 설정 기반 리팩터 우선, 구조 단순화 우선 |

---

*이 문서는 2026-05-25 ki-ai-trader 코드 풀 스캔 결과를 기반으로 작성되었습니다.*

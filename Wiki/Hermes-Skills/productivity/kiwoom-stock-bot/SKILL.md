---
name: kiwoom-stock-bot
description: Kiwoom API 기반 주식 거래 봇 개발/디버깅 — 실시간 시세 조회, 주문 실행, Telegram 알림
trigger: Kiwoom API炒股 봇 관련 작업发生时 (价格查询错误、매수 메서드 부재、스크리닝 신호 처리 등)
---

# Kiwoom 주식 거래 봇 스킬

## 핵심 구조

```
kiwoom_api.py       # Kiwoom API 래퍼 (계좌, 보유종목, 시세查询)
ki_project_monitor.py  # 모니터 루프 (30분간격 스크리닝 → Telegram 알림)
```

## 자주 발생하는 버그 & 해결책

### 1. 가격 조회 `invalid literal for int()` 오류

**원인:** Kiwoom API 응답에 빈 문자열 `''` 또는 `None`이 섞여 있음

**해결책:** 모든 숫자 필드에 `try/except` 처리
```python
def _parse_int(val):
    if val in (None, '', ' '):
        return 0
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0
```

### 2. `get_managed_stocks()` / `get_candidate_stocks()` 정의 없음 (run_trader.py)

**현상:** `AttributeError: module 'run_trader' has no attribute 'get_managed_stocks'`

**원인:** `_fetch_realtime_ranks()` 내부에서 `get_managed_stocks()`와 `get_candidate_stocks()`를 호출하지만,这两个 함수 또는 딕셔너리가 어디에도 정의되어 있지 않음

**해결 — run_trader.py 상단에 직접 정의:**
```python
MANAGED_STOCKS: Dict[str, str] = {
    "011200": "HMM",
    "012800": "대창단조",
    "005930": "삼성전자",
    "035420": "네이버",
    "000660": "SK하이닉스",
    "068270": "셀트리온",
}

CANDIDATE_STOCKS: Dict[str, str] = {
    "001440": "대한전선",
    "006340": "대원전선",
    "064350": "현대로템",
    "475150": "SK이터닉스",
    "096770": "SK이노베이션",
    "004020": "현대제철",
}

def get_managed_stocks() -> List[str]:
    return list(MANAGED_STOCKS.keys())

def get_candidate_stocks() -> List[str]:
    return list(CANDIDATE_STOCKS.keys())

def get_stock_name(code: str) -> Optional[str]:
    return MANAGED_STOCKS.get(code) or CANDIDATE_STOCKS.get(code)
```

**참고:** `auto_buy_scanner.py`에도 같은 이름의 딕셔너리가 있지만, `run_trader.py`에서는 직접 정의해서 사용 — 별개로 운영 가능

### 2b. `execute_buy` 메서드 부재 (run_trader.py)

**현상:** `AttributeError: 'KiwoomAPIClient' object has no attribute 'execute_buy'` 또는 `execute_buy() takes 3 positional arguments but 4 were given`

**원인:** `run_trader.py`의 `execute_buy`는 `KiwoomAPIClient`가 아니라 `KiwoomTrader` 클래스의 메서드인데, 정의 자체가 없었음

**해결책 — `run_trader.py`에 직접 구현:**
```python
def execute_buy(self, stock_code: str, quantity: int, price: float, reason: str) -> bool:
    """매수 주문 실행"""
    if quantity <= 0:
        return False
    self.logger.warning(f"🟢 매수 실행: {stock_code} {quantity}주 @ {price:,.0f}원 | 사유: {reason}")
    self.notifier.send(f"🟢 매수: {stock_code} {quantity}주 @ {price:,.0f}원\n사유: {reason}")
    try:
        result = self.api.place_order(
            account_no=ACCOUNT_NO,
            stock_code=stock_code,
            order_type="BUY",
            quantity=quantity,
            price=price,
        )
        if result and result.get('return_code') == 0:
            self.logger.info(f"✅ 매수 체결: {stock_code} {quantity}주")
            return True
        else:
            self.logger.error(f"❌ 매수 실패: {result}")
            return False
    except Exception as e:
        self.logger.error(f"❌ 매수 예외: {e}")
        return False
```

### 2b. `execute_sell` 호출 잘못됨 (run_trader.py)

**현상:** `TypeError: execute_sell() missing 1 required positional argument: 'reason'`

**원인:** `execute_sell(stock_code_str, qty, reason)` 형태로 호출하지만,
실제 시그니처는 `execute_sell(pos: PositionState, quantity: int, reason: str)`

**해결책:** `PositionState` 객체가 아닌 경우 → `execute_sell_adaptive(worst_pos, qty, reason)` 사용
```python
# ✅ 올바른 호출
worst_pos = self.positions[worst_code]
ok = self.execute_sell_adaptive(worst_pos, qty, f"교체 ({worst_code}→{new_code})")
```

### 2c. `_get_account_balance` — 현금 잔고 조회

**용도:** 교체 제안 시 매도가능 수량을 정확히 계산하려면 현재 현금 잔고가 필요

**구현:**
```python
def _get_account_balance(self) -> Optional[float]:
    """계좌 현금 잔고 조회 (단위: 원)"""
    try:
        now = datetime.now()
        r = self.api._make_request(
            'POST',
            self.api.ACCOUNT_BALANCE_URL,
            api_id='ka01690',
            json={'qry_dt': now.strftime('%Y%m%d')}
        )
        data = r.json()
        balance = data.get('dnca_blc') or data.get('cash_balance')
        if balance is not None:
            return float(balance)
    except Exception as e:
        self.logger.warning(f"현금 잔고 조회 실패: {e}")
    return None
```
⚠️ 응답 필드명이 다를 수 있음 — `dnca_blc`, `cash_balance`, `dnstknc_vtls` 등 확인 필요

### 2d. 2단계 교체 승인 흐름 (Telegram 명령 폴링)

**문제:** 기존 교체 로직이 자동 실행 → 사용자에게 알리지도 않고 바로 매도/매수 진행

**해결 — 2단계 승인 패턴:**

```
[1단계] 교체 @{종목코드}  →  Telegram에 제안 메시지 (아직 매도 안 함)
[2단계] 교체승인 @{종목코드}  →  실제 매도 → 매수 실행
```

**구현 구조:**
```python
# __init__에 상태 저장
self._pending_replacement: Optional[Dict] = None  # 교체 승인 대기 정보

def _execute_replacement(self, new_code: str):
    """1단계: 교체 제안 (매도 전)"""
    # 1. 최저점수 보유종목, 현재가, 잔고, 매도가능수량 계산
    # 2. _pending_replacement에 정보 저장
    # 3. Telegram에 상세 제안 메시지 전송 (매도/매수 수량, 잔고 포함)
    self._pending_replacement = {...}

def _confirm_replacement(self, new_code: str):
    """2단계: 사용자 승인 → 실제 매도/매수 실행"""
    pending = getattr(self, '_pending_replacement', None)
    if not pending or pending.get('new_code') != new_code:
        self.notifier.send("❌ 교체 실패: 승인 대기 중인 요청이 아닙니다")
        return
    # 1단계: execute_sell_adaptive(worst_pos, qty, reason)
    # 2단계: execute_buy(new_code, buy_qty, buy_price, reason)
    self._pending_replacement = None
```

**Telegram 명령 폴링 (대기 루프 내 10초마다):**
```python
def _poll_telegram_commands(self):
    """10초마다 Telegram 명령 수신"""
    # 교체승인 @{코드}  →  _confirm_replacement(code)
    # 교체 @{코드}      →  _execute_replacement(code)
```

**Telegram 알림 예시 (1단계 제안):**
```
🔄 교체 제안

📊 현재 잔고: 1,200,000원
📈 매도: 삼성전자 10주 @ 70,000원
   → 매도대금: 700,000원
💰 매도 후 총액: 1,900,000원
📉 매수: 네이버 @ 200,000원
   → 최대 9주 매수 가능

✅ 교체 실행: 교체승인 @005930
❌ 거절: 아무것도 안 함
```

**핵심 설계 원칙:**
- 1단계(`교체 @`)는 **제안만** — `_pending_replacement`에 저장 후 알림
- 2단계(`교체승인 @`)는 **실행** — 검증 후 매도→매수 순차 진행
- 5분内有効 —同一 candidate에重复提案防止
- 매도대금 + 실현잔고 기반 최대 매수 수량 표시

### 3. 스크리닝 신호 처리 for 루프 배치 실수

**원인:** `process_screening_signals`가 for 루프 **안**에 있으면 보유 종목 수만큼 반복

**해결책:** for 루프 **밖**에서 1회 실행
```python
# 보유 종목 루프
for holding in holdings:
    ...
# 스크리닝 신호 처리 (루프 밖)
self.process_screening_signals(signals)
```

### 4. Telegram 알림이 안 오는 경우 (2가지 원인)

**원인 A — `send_telegram_alert()`가 실제 전송을 안 함**
```python
# ki_project_monitor.py의 현재 구현 (실제 전송 안 함!)
def send_telegram_alert(message: str):
    print(f"[ALERT] {message}")  # ❌ Telegram 전송 없음
```
**해결**: `NotificationSystem` 사용
```python
from notification_system import NotificationSystem
notif = NotificationSystem()
notif._send_telegram(msg)  # ✅ 직접 전송
```

**원인 B — `execute_real_buy()`는 Telegram 전송을 담당하지 않음**
- 매수 완료 후 Telegram通知는 `ki_project_monitor.py`의 모니터 루프에서 `send_trade_notification()` 호출해야 함
- 봇을 직접 실행(모니터 미실행)하면 알림이 안 감
- **실시간 알림이 필요하면** `execute_real_buy()` 완료 후 `NotificationSystem`으로 직접 전송

**올바른 알림 패턴**:
```python
result = client.execute_real_buy(...)
if result and result.get('return_code') == 0:
    notif = NotificationSystem()
    notif._send_telegram(f"✅ 매수 완료: {name} {qty}주")
```

### 5. `get_current_prices` → `get_stock_price` 오타 (execute_real_buy 내부)

**현상**: `'KiwoomAPIClient' object has no attribute 'get_current_prices'`
**원인**: `kiwoom_api.py` 라운 932에서 `self.get_current_prices()` 호출하는데 해당 메서드 없음
**해결**:
```python
# 잘못된 코드
prices = self.get_current_prices([stock_code])
current_price = prices[0]

# 올바른 코드
prices = self.get_stock_price([stock_code])
current_price = prices[0].current_price
```

### 5. HTTP 401 `login fail: Please carry the API secret key in the 'Authorization' field` — 수정완료

**원인:** 토큰 발급 요청(`authenticate()`) 시 Authorization 헤더 누락

**해결책:** kiwoom_api.py의 `authenticate()` 메서드에 Basic Auth 헤더 추가 (이미 수정완료)
```python
import base64
credentials = base64.b64encode(
    f"{self.app_key}:{self.secret_key}".encode()
).decode()
response = self.session.post(
    self.OAUTH_TOKEN_URL,
    json=auth_data,
    headers={'Authorization': f'Basic {credentials}'},  # ✅ 추가됨
    timeout=10
)
```
⚠️ 주의: `Bearer {api_secret}`이 아님 — `Basic {base64(appkey:secretkey)}`임
- Basic Auth: 토큰 발급 시 사용
- Bearer {access_token}: 토큰 발급 후 API 호출 시 사용 (이미 올바르게 구현됨)

**추가 수정:** 254줄 이후 unreachable dead code 삭제
- 256~291줄에 `authenticate()`의 중복 코드 존재 (2번째 try/except 블록)
- 263줄: `auth_data` 딕셔너리에 `}` 누락 (문법 오류)
- Python은 해당 코드가 `return False` 이후여서 실행時に 도달하지 않았지만, 파일 로드 자체는 가능
- `python -m py_compile`으로 확인 후 patch 삭제

### 16. 매수 스캐너 — 고정 금액(50만원) 문제로 매수 안 됨

**원인:** `BUY_AMOUNT_PER_STOCK = 500,000` 하드코딩 → 예수금 34만원에서는 모든 주문 거절

**원인 상세:** `execute_real_buy` 내부에서 `total_amount > available_balance` 체크 → 50만원 기준 계산 → 전品种 품절

**해결 — 동적 잔고 배분:**
```python
# main() 상단에서 잔고 조회 후 동적 배분
account = client.get_account_balance(ACCOUNT)
available = account.available_balance
cash_buffer = int(available * 0.10)       # 수수료/슬리피지 버퍼 10%
usable_cash = available - cash_buffer
per_stock_amount = max(50_000, usable_cash // MAX_BUY_COUNT)

# 매수 루프에서 잔고 실시간 차감
remaining_cash = usable_cash
for target in buy_targets:
    effective_amount = min(per_stock_amount, remaining_cash)
    qty = int(effective_amount / target['price'])
    if qty <= 0:
        print(f"⏭️ {target['name']}: 잔고 부족 — 스킵")
        continue
    execute_buy(client, target['code'], ..., effective_amount)
    remaining_cash -= target['price'] * qty
```

**핵심:** 매수 가능 수량 = `floor(잔고 / 현재가)` — 고정 금액이 아닌 잔고 기반自動計算

**추가 수정:** `confirm=True` (수동 확인) → `confirm=False` (자동 실행)

### 17. 매수 스캐너 점수 계산 vs 잔고 부족으로 매수 불가 구분

**문제:** 점수 > 0인 후보가 있음에도 잔고로 50만원 주문이 안 되면 "매수 대상 없음"으로 오인

**원인:** RSI 45 수준이면 점수 2~4로 정상이나, 삼성전자(220만원), 네이버(220만원)는 잔고 부족

**실제 매수 가능 조건:**
```
score > 0 AND qty = floor(usable_cash / price) > 0
```

**확인된 매수 가능 후보 예시 (예수금 34만원 기준):**
| 종목 | 현재가 | 매수 가능 수량 | 점수 |
|------|--------|---------------|------|
| HMM | 20,650원 | 7주 (144,550원) | 2~4 |
| 대한전선 | 50,500원 | 3주 | 2 |
| 대원전선 | 12,350원 | 12주 | -2 (탈락) |

**Scoring 로직과 잔고 기반 필터링을 동시에 적용해야 함**

### 18. ki-project-status.py — 30분 알람에 손절가/익절가/추세 표시

**변경 전:** 현재가, 수익률만 표시
**변경 후:**
```python
# 손절가: ATR 기반 동적 + 긴급 손절(-5%) 중 높은 값
atr_stop      = purchase_price * (1 - 2 * atr / purchase_price)
emergency_stop = purchase_price * 0.95
stop_loss = max(atr_stop, emergency_stop)

# 익절가: 트레일링 (수익≥0.5% + RSI≥65 활성화 조건)
if profit_pct >= 0.5 and rsi >= 65:
    trailing_stop = highest_price * (1 - 0.003)  # 0.3% trailing
    take_profit_pct = 0.3

# 추세 판단
if ma5 > ma20 and hist > 0 and mom5 > 0: trend = '상승'
elif ma5 < ma20 and hist < 0 and mom5 < 0: trend = '하락'
elif rsi > 70: trend = '과매수 구간'
else: trend = '중립'
```

**출력 포맷 (30분 알람):**
```
⚪ HMM 9주 +0.0% | 중립 | 👀 관망
   현재  20,650원 | 손절가  19,657 | 익절 ─
```

### 19. 매매 판단 기준 — 보유 종목 모니터링

| 조건 | 판단 | 행동 |
|------|------|------|
| 수익률 ≤ -5% | 🚨 긴급 손절 검토 | 전량 매도 |
| trailing 활성 + 현재가 ≤ trailing_stop | 📤 트레일링 익절 | 전량 매도 |
| RSI > 80 (or RSI > 75 + MACD 하락) | ⚠️ RSI 과매수 | 50% 익절/관망 |
| MA 역배열 + 모멘텀 < -3% | 🔍 단기추세 하락 | 관망/매도 검토 |
| 그 외 | ✅ 홀딩 | 유지 |

### 15. 매수 스캐너 실행되지만 매수 발생 안 함 — RSI 스코어링太过严格

**현상:** `auto_buy_scanner.py` 실행 시 에러 없음, 점수 > 0인 종목 0개

**원인:** `score_stock()`의 RSI 패널티가 한국 증시 현실과 안 맞음
- RSI > 60 → -1 (거의 모든 상승 종목 탈락)
- RSI > 70 → -3
- RSI > 80 → -5
- **문제:** 한국 증시 상승장에서는 RSI가 60 이하로 떨어지는优质 종목이 거의 없음
- 동시에 MA 정배열(+2), MACD 양수(+1), 모멘텀(+1~+2)도 충족해야 양수 점수인데, 조정장이 아닌 한 달성 어려움

**RSI 조건 현실적 분석:**
| RSI 구간 | 패널티 | 현실 가능성 |
|----------|--------|------------|
| RSI > 60 → -1 |太强 | 대부분의 상승 종목이 RSI 60+ |
| RSI > 70 → -3 |强 | 추가 상승 어려움 |
| RSI > 80 → -5 |극강 | 극단적 과매수만 해당 |

**대응 방안 A — RSI 기준 완화 (권장):**
```python
# 현재: RSI > 60 → -1
# 변경: RSI > 75 → -1 (과매수 구간을 더 높임)
elif rsi > 75:
    score -= 1
```

**대응 방안 B — 과매수 패널티 체계 개편:**
```python
# RSI 과매수 penalty를 점수 차등화
if rsi > 85:
    score -= 5; signals.append(f"RSI극과매수({rsi:.0f})")
elif rsi > 75:
    score -= 2; signals.append(f"RSI과매수({rsi:.0f})")
elif rsi > 65:
    score -= 1  # 기존 -1에서 -0로 완화
```

**대응 방안 C — 매수 후보 확장:**
관리종목 6개 + 후보종목 6개만으로는 점수 조건을 충족하는 종목이 없을 때 매수 대상이 아예 없음. 네이버 실시간 상승종목 수집(`fetch_naver_candidates()`)으로 후보를 100개 이상으로 확장

**핵심 결론:** 401 인증 에러가 발생하지 않는 한, 매수 0건의 대부분 원인은 **시장 Conditions에서 RSI 60 이하인 상승장이太少** 때문. 인증이 정상이라면 스코어링 조건 조정이 가장 실효적.

### 13. 마감이브리핑 — 장 마감 후 종합 보고 отсут

**요구:** 매일 장 마감(15:30) 후 오늘 거래 내역 + 각 종목별 평가 제공

**구현:**

**1) 거래 기록 저장 — ki_project_monitor.py에 `save_trade_log()` 추가**
```python
TRADE_LOG_PATH = Path('/home/comage/.hermes/cron/output/ki-trade-log.json')

def save_trade_log(action, code, name, qty, price, reason, extra_info=""):
    """오늘의 거래 내역을 JSON 파일에 저장"""
    today = datetime.now().strftime('%Y%m%d')
    logs = json.loads(TRADE_LOG_PATH.read_text()) if TRADE_LOG_PATH.exists() else {}
    if logs.get('date') != today:
        logs = {'date': today, 'trades': []}
    logs['trades'].append({
        'action': action, 'code': code, 'name': name,
        'qty': qty, 'price': price, 'amount': qty * price,
        'reason': reason, 'extra': extra_info,
        'time': datetime.now().strftime('%H:%M:%S')
    })
    TRADE_LOG_PATH.write_text(json.dumps(logs, ensure_ascii=False, indent=2))
```
`send_trade_notification()` 호출 직후 `save_trade_log()`도 호출

**2) 마감이브리핑 — ki-project-status.py 수정**
- 시장 开市 중: 기존 단순 상태 보고
- 시장 마감 후: 종합 마감이브리핑
  - 오늘 거래 내역 (BUY/SELL: 수량, 금액, 이유)
  - 각 보유 종목별 평가 (RSI, MACD, 30일 변동)
  - 기술적 지표: `technical_indicators.py`의 `calculate_rsi`, `calculate_macd`, `fetch_daily_data` 활용

### 20.候iri 발굴 시스템 — candidate_discovery.py ( candidate_pool =候iri候iri)

**候iri发掘来源:**
- 거래량 급증 종목 (당일 거래량 > 전일 거래량 × 3)
- 외국인 연속 매수 동향 (3일 이상 연속 매수)
- 기관 연속 매수 동향 (3일 이상 연속 매수)
- 기술적 지표: RSI, MACD, 볼린저밴드, ATR
- 기본면: PER, ROE, 배당수익률

**종합 점수 계산 (총 100%):**
```
추세 점수     25%  (MA5 > MA20, MACD 히스토그램, 모멘텀)
RSI 점수     15%  (40~60 구간 최고점, 과매수 과대 패널티)
MACD 점수    10%  (MACD > Signal, 히스토그램 > 0)
거래량 비율  15%  (당일 / 20일 평균 거래량)
외국인 동향  15%  (연속 매수일수 × 3)
기관 동향    10%  (연속 매수일수 × 2)
기본면      10%  (PER 10~20, ROE > 10%, 배당 > 2%)
```

**run_trader.py 통합:**
```python
from candidate_discovery import CandidateDiscovery
discovery = CandidateDiscovery()
candidates = discovery.discover_candidates(top_n=10)
# candidates: [(code, name, score, signals, price), ...]
# 10초마다候iri 현황을 Telegram으로 자동 전송
# 교체 제안 시候iri 실시간 점수를 활용
```

**候iri 실시간 알림 (15분마다):**
-候iri 상위 10개 현황 Telegram 전송
- 점수 변동이 큰候iri가 있으면 30분마다 Telegram 알림

### 14. OpenCode가 프로젝트 디렉토리에서 Glob 탐색이 60초 이상 걸림

**원인:** OpenCode가 파일 읽기 시 내부적으로 `Glob "**/*.py"`로 전체 프로젝트 탐색을 먼저 수행. ki-ai-trader 프로젝트는 3,306개의 .py 파일(281MB, 대부분 venv/)이 있어 탐색만으로 60~90초 소요

**대응:**
1. 파일 읽기/이해는 Hermes가 직접 수행 (grep, read_file)
2. 수정 지시만 OpenCode에 전달
3. 반드시 `workdir` 미지정으로 실행

```bash
# ✅ 정상 작동 — project 경로 미지정
opencode run "Show me lines 1-50 of kiwoom_api.py"

# ❌ 탐색만 60초+ 소요 — project 경로 지정
opencode run "Read kiwoom_api.py" --project /home/comage/coding/ki-ai-trader

# ✅ 정상 작동 — 단일 파일만 읽기
opencode run "Read kiwoom_api.py lines 80-120"

# ✅ 정상 작동 — 파일 생성/수정
opencode run "Create /tmp/test.txt with content: hello"
```

**핵심 원칙:** ki-ai-trader 같은 대형 프로젝트에서는 OpenCode의 file Glob이 병목. Hermes가 코드 분석을先行하고, 수정 명령만 위임.

### 7. `send_telegram_alert()` — print만 하고 실제 전송 안 함

**원인:** `send_telegram_alert()`가 `print()`만 호출해서 Hermes Agent가 감시해야 하는 설계였으나, 모니터 루프 내에서는 Hermes Agent 감시가 안 도달함

**현상:** 매도/매수 실행 후 Telegram 알림이 오지 않음

**해결:**
```python
# ki_project_monitor.py — 반드시 실제 전송 추가
def send_telegram_alert(message: str):
    print(f"[ALERT] {message}")
    notif = _get_telegram_notif()
    if notif:
        notif._send_telegram(message)  # ✅ 직접 전송

def _get_telegram_notif():
    try:
        from notification_system import NotificationSystem
        return NotificationSystem()
    except Exception:
        return None
```

### 8. 스크리닝 30분 캐시가 5초마다 재실행됨

**원인:** `process_screening_signals(client, cash, current_prices, results)`의 `results` 파라미터를優先하는 로직 → 5초마다 `run_all_screens()` 재실행 → API 부하 + 거래량 데이터 부정확

**해결:** 항상 `screening_cache['results']` 사용
```python
# process_screening_signals 내부
results_to_use = screening_cache['results']  # ✅ results 파라미터 무시
```

### 9. 매도 감지 — holdings 감소를 Telegram 알림으로 알려주는 로직 없음

**원인:** 매도가 자동으로 실행됐지만 `send_trade_notification()`을 호출하는 로직이 없음 → Telegram 알림 없음

**해결:** holdings 스냅샷 비교 방식으로 매도 감지
```python
# module-level 스냅샷
_holdings_snapshot: Dict[str, int] = {}

def _detect_sells(client, current_prices):
    """prev_qty > curr_qty → 매도 발생"""
    global _holdings_snapshot
    holdings = get_holdings(client)
    current_map = {h.stock_code: h for h in holdings}
    for code, prev_qty in list(_holdings_snapshot.items()):
        if prev_qty > 0:
            curr_holding = current_map.get(code)
            curr_qty = curr_holding.quantity if curr_holding else 0
            if curr_qty < prev_qty:
                sold_qty = prev_qty - curr_qty
                reason = _infer_sell_reason(code, ...)
                send_trade_notification('SELL', code, name, sold_qty, price, reason, "")
    _holdings_snapshot = {h.stock_code: h.quantity for h in holdings}
```

### 10. 키움 API 주문 내역 조회 — `/api/dostk/ordr_list` 미지원

**원인:** 키움 OpenAPI는 `/api/dostk/ordr_list` 엔드포인트를 지원하지 않음 (1504 에러 반환)

**대응:** 매도 내역 조회가 불가능하므로 holdings 스냅샷 비교 방식으로 우회

```python
def get_order_list(self, account_no: str = None) -> List[Dict]:
    """주문 내역 조회 — 키움 API 미지원으로 항상 빈 리스트 반환"""
    # /api/dostk/ordr_list → 1504 에러 (API 미지원)
    return []
```

### 11. `cash *= 0.7` 대략적估算 → 실제 예수금과 불일치

**원인:** 매수 후 `cash *= 0.7`로 대략적 감소 계산 → 매수 금액 실제와 다름 → subsequent 매수 주문에서 금액 오류 가능

**해결:** 매수 후 즉시 `cash = check_cash_balance(client)`로 실제값 조회
```python
# process_screening_signals 내부
execute_buy_order(client, code, name, cash, current_price, reason)
cash = check_cash_balance(client)  # ✅ 실제 예수금 조회
# ⚠️ cash *= 0.7 은 대략적估算이므로 이 방식 선호
```

### 12. 크론 알림 — 장 마감 후에도 30분마다 알림 발생

**원인:** `ki-project-status.py`가 시장 시간 체크 없이 매 30분 실행

**해결:** `is_market_open()` 체크 추가
```python
def is_market_open():
    now = datetime.now()
    hour, minute = now.hour, now.minute
    weekday = now.weekday()
    if weekday >= 5:
        return False
    if hour < 9 or (hour == 15 and minute > 30) or hour > 15:
        return False
    return True

def get_status():
    if not is_market_open():
        return {'success': True, 'market_closed': True, 'time': datetime.now().strftime('%H:%M')}
    # ... 기존 로직
```

**참고:** `ki_project_monitor.py`는 이미 808/821줄에서 `is_market_open()` 체크하지만, 별도 스크립트 `ki-project-status.py`는 체크하지 않음

## 검증 체크리스트

```bash
cd /home/comage/coding/ki-ai-trader
python ki_project_monitor.py
```

## 파일 경로

| 파일 | 용도 |
|------|------|
| `/home/comage/coding/ki-ai-trader/kiwoom_api.py` | Kiwoom API 래퍼 (919줄) |
| `/home/comage/coding/ki-ai-trader/ki_project_monitor.py` | 모니터 루프 |
| `/home/comage/coding/ki-ai-trader/config.py` | 계좌/비밀번호 설정 |

## 검증 체크리스트

- [ ] `KiwoomAPIClient` 인스턴스 생성 → `get_holdings()` 호출
- [ ] 가격 조회 시 빈 문자열 `0`으로 처리되는지 확인
- [ ] `execute_real_buy` 메서드 존재하는지 확인
- [ ] 모니터 실행 후 Telegram 로그에 `[ALERT]` 메시지 출력되는지 확인

# KI AI Trader — HMM 사고 분석 및 수정 보완 보고서

**작성일:** 2026-05-04
**작성자:** Hermes Agent (OpenCode 코드 리뷰 + 수동 분석 병행)
**상태:** 초안 — 사용자 승인 후 수정 예정

---

## 1. 사고 개요

### 1.1 경과

| 시간 | 이벤트 | 가격 | 수량 |
|------|--------|------|------|
| 09:20:03 | HMM 기존 포지션 자동 매도 | 20,500원 | 9주 |
| 09:31:13 | **HMM 수동 매수** (사용자 지시) | 21,450원 | 9주 |
| 09:33:54 | **HMM 자동 매도 #1** | 21,350원 | 9주 |
| 09:33:56 | **HMM 자동 매도 #2** | 21,350원 | 9주 |

**결과:** 3분 만에 매수→매도 2회. **손실:** (21,350 - 21,450) × 9 = **-900원** (수수료 별도)

### 1.2 사용자 확인

> "3분 사이에 매수와 매도가 이루어지면 어쩌자는 거야. 가격이 많이 하락해서 판매한 거야."

**사용자 의도:** HMM 상승세 확인 후 추가 매수 → **중장기 보유**
**실제 결과:** 매수 직후 자동 매도 2회

---

## 2. 근본 원인 분석

### 2.1 계산 검증

```
매수가: 21,450원
09:33 매도가: 21,300원 (키움 체결통보 기준)
하락폭: 150원 (-0.70%)

trailing_step_pct = 0.3%
trailing_stop_price = 21,450 × (1 - 0.3/100) = 21,385원

trailing_stop_price(21,385) > current_price(21,300)
→ 21,300 < 21,385 → SELL_ALL 발동 조건 충족
```

**결과:** HMM_SPECIAL 설정(activation_pct=15%)에도 불구하고,
trailing_step_pct=0.3%만으로 150원下跌에 매도가 발동.

### 2.2 원인 1 — 매수 직후 트레일링 스탑 과잉 반응

**위치:** `adaptive_trailing_stop.py` 라인 221-258

```python
# _update_trailing_status()
# 조건 2: RSI >= early_warning_rsi(65) → trailing_active = True
condition_2 = rsi >= self.early_warning_rsi

# 조건 3: MACD 히스토그램 하락
condition_3 = histogram < 0 and histogram < self.early_warning_macd_slope
```

**문제:** condition_2, 3, 4 중 하나만 충족하면 trailing_active가 True가 됨.
RSI 65 이상만으로 트레일링이 활성화되므로, 매수 직후 과매수 구간 진입 시
거의 즉시 trailing_stop_price가 설정되고, 0.3% 하락만으로 매도가 발동.

### 2.3 원인 2 — 새 매수분과 기존 트레일링 스탑 상태 공유

**위치:** `ki_project_monitor.py` 라인 479-508

```python
def get_or_create_trailing_stop(code: str, ...):
    if code not in trailing_stops:   # ← 새 매수인데 code가 이미 존재하면
        # ... 새 객체 생성 ...
        trailing_stops[code] = ts    # ← 새 buy_price로 덮어씁니다
    return trailing_stops[code]      # ← 기존 것을 그대로 반환
```

**실제 흐름:**
1. 08:20 — HMM 기존 포지션 매도 (trailing_stops['011200']는 여전히 존재)
2. 09:31 — HMM 새 매수 (9주 @ 21,450원)
3. `get_or_create_trailing_stop('011200')` 호출 → code가 `trailing_stops`에 **이미 존재**
4. **새 AdaptiveTrailingStop 객체 생성** (buy_price=21,450), `trailing_stops['011200']` **덮어씀**
5. 09:33 — `update_dynamic_trailing()` → trailing_active=True → SELL_ALL

**문제:** 새 매수분에 대한 `highest_price` 초기값이 `buy_price`(21,450)로 설정되고,
`trailing_stop_price = 21,450 × (1 - 0.3%) = 21,385`로 설정.
3분 후 21,300원 → 21,300 < 21,385 → **즉시 매도**.

### 2.4 원인 3 — 시장가 지정가 혼용으로 인한 가격 불일치

**위치:** `kiwoom_api.py` 라인 547-548

```python
order_data = {
    'ord_uv': '',             # 주문단가 (시장가 시 빈값)
    'trde_tp': '3',          # 매매구분 ('3': 시장가)
}
```

**문제:**
- 매도 주문은 항상 시장가(trde_tp='3')로 전송
- 체결 평균가와 주문 시점 현재가 차이 발생 가능
- 21,450원 주문 → 21,350원 체결 → 트레일링 스탑 기준과 불일치

### 2.5 원인 4 — 스크리닝 매도 신호 중복 트리거

**위치:** `ki_project_monitor.py` 라인 1114-1128

```python
# 메인 루프 - 트레일링 스탑 도달 시
if signal in ('SELL_ALL', 'PARTIAL_EXIT'):
    execute_sell_order(client, code, name, h.quantity, cur_prc, "트레일링 스탑 도달")

# 스크리닝 매도 신호 처리 (라인 797-814)
if not is_strong_uptrend and ('RSI 과매수' in sell_reason or 'MACD 하락' in sell_reason):
    if not partial_exits.get(code):
        execute_sell_order(client, code, name, exit_qty, current_price, f"시장 과열 ({sell_reason})")
```

**문제:**
- 트레일링 스탑으로 매도 → holdings에서 제거 (라인 1121: `trailing_stops.pop(code)`)
- 그러나 `partial_exits`는 별도 딕셔너리라 스크리닝 매도가 **또 실행될 가능성**
- 09:33 두 번의 매도: 1번目は「트레일링 스탑 도달」, 2번目は「트레일링 스탑」(라인 981의 default)

### 2.6 원인 5 — 확정적 손절/익절 로직 부재

**문제:** 매수 직후 급격한 하락/상승에 대한 **비활성화 기간**이 없음.
매수 후 N분간은 트레일링 스탑 로직을 무시하는 것이 업계 표준.

---

## 3. 발견된 버그 및 보안 문제

### 3.1 Critical — 매수 직후 트레일링 스탑 과잉 발동

| 항목 | 내용 |
|------|------|
| 파일 | `adaptive_trailing_stop.py`, `ki_project_monitor.py` |
| 라인 | 221-258, 479-508 |
| 심각도 | **Critical** — 금전적 손실 직접 원인 |
| 설명 | 새 매수 후 trailing_step_pct=0.3%만 하락해도 SELL_ALL 발동 |

### 3.2 High — 시장가 주문과 체결가 불일치

| 항목 | 내용 |
|------|------|
| 파일 | `kiwoom_api.py` |
| 라인 | 547-548 |
| 심각도 | **High** — 트레일링 기준과 실제 체결가 차이 |
| 설명 | 지정가 주문이 아닌 시장가로만 매도 시 예상가와 실제 체결가 차이 |

### 3.3 Medium — 중복 매도 방지 로직 불완전

| 항목 | 내용 |
|------|------|
| 파일 | `ki_project_monitor.py` |
| 라인 | 1000-1002, 1114-1128 |
| 심각도 | **Medium** |
| 설명 | `_detect_sells()`는 holdings 스냅샷 비교만, trailing 스탑 도달 매도와 스크리닝 매도가 동시에 발생하면 중복 |

### 3.4 Medium — `_holdings_snapshot` 초기화 누락

| 항목 | 내용 |
|------|------|
| 파일 | `ki_project_monitor.py` |
| 라인 | 103 (선언), 1002 (업데이트) |
| 심각도 | **Medium** |
| 설명 | 데몬 재시작 시 스냅샷이 0으로 초기화 → 첫 루프에서 모든 보유가 "매도된 것"으로 감지될 수 있음 |

### 3.5 Low — 설정값 하드코딩

| 항목 | 내용 |
|------|------|
| 파일 | `adaptive_trailing_stop.py` |
| 라인 | 74-75 |
| 심각도 | **Low** |
| 설명 | activation_pct=0.5, trailing_step_pct=0.3 등 핵심 임계값이 생성자 인자가 아닌 하드코딩 |

---

## 4. 수정 보완 계획

### 4.1 수정 1 — 매수 후 트레일링 스탑 비활성화 기간 (가장 중요)

**파일:** `adaptive_trailing_stop.py`

**핵심 로직:**
```python
# 새 필드 추가
post_entry_grace_seconds: int = 300  # 매수 후 5분간 트레일링 무시

# __post_init__에 추가
self.trailing_active = False  # 비활성화 기간 동안 False 유지
self.entry_time = datetime.now()

# _update_trailing_status() 수정
def _update_trailing_status(...):
    elapsed = (datetime.now() - self.entry_time).total_seconds()
    if elapsed < self.post_entry_grace_seconds:
        return  # 비활성화 기간中はtrailing_active 무조건 False

    # ... 기존 로직 ...
```

**효과:** 매수 후 5분간 트레일링 스탑 로직 완전 비활성화. 시장 격변에만 emergency_stop_pct(-5%)만 작동.

### 4.2 수정 2 — 트레일링 스탑 발동 최소 수익률 상향

**파일:** `adaptive_trailing_stop.py`

**변경 전:**
```python
activation_pct: float = 0.5  # 0.5% 수익만으로 활성화
```

**변경 후 (HMM_SPECIAL 유지):**
```python
activation_pct: float = 2.0   # 최소 2% 수익 필수
```

**HMM 특별 설정:**
```python
HMM_SPECIAL = {
    'code': '011200',
    'activation_pct': 15.0,      # 유지 (기존)
    'post_entry_grace_seconds': 600,  # 매수 후 10분간 비활성화 (신규)
    'trailing_step_pct': 1.0,       # 기존 0.3% → 1.0%로 완만 (신규)
}
```

### 4.3 수정 3 — 시장가 대신 지정가 매도

**파일:** `kiwoom_api.py` `place_order()` 수정

**핵심 로직:**
```python
def place_order(..., order_method: str = "LIMIT"):  # 기본값 변경
    if order_method == "MARKET":
        trde_tp = '3'
        ord_uv = ''
    else:  # LIMIT
        trde_tp = '0'   # 보통지정가
        ord_uv = str(int(price))  # 지정가 가격 설정
```

**호출부 수정:**
```python
# ki_project_monitor.py - execute_sell_order()
result = order_executor.execute_sell(code, quantity, current_price)
# → 항상 지정가(현재가)로 주문
```

### 4.4 수정 4 — 중복 매도 방지

**파일:** `ki_project_monitor.py`

**추가:**
```python
# 매도 실행 직전 플래그
_sell_in_progress: Dict[str, bool] = {}

def execute_sell_order(...):
    global _sell_in_progress
    if _sell_in_progress.get(code):
        print(f"  ⚠️ [{name}] 매도 진행 중 — 중복 방지")
        return False
    _sell_in_progress[code] = True
    try:
        # ... 매도 로직 ...
    finally:
        _sell_in_progress[code] = False
```

### 4.5 수정 5 — Telegram 승인 요청 기반 자동 매도

**파일:** `ki_project_monitor.py`

**핵심:**
```python
TRAILING_STOP_AUTO_SELL = False  # False: Telegram 승인 후 매도
PARTIAL_EXIT_AUTO_SELL = False  # False: Telegram 승인 후 매도

def update_dynamic_trailing(...):
    signal = ts.update_volatility_based_trailing(...)
    if signal in ('SELL_ALL', 'PARTIAL_EXIT'):
        if not TRAILING_STOP_AUTO_SELL:
            # Telegram 승인 요청
            send_telegram_alert(
                f"📊 *트레일링 스탑 도달 — 승인 요청*\n"
                f"{name}({code}): {current_price:,}원\n"
                f"수익률: {profit_pct:+.2f}%\n"
                f"✅ 실행: 매도승인 @{code}\n"
                f"❌ 거절: 매도거절 @{code}"
            )
            return 'HOLD'  # 승인 전까지 HOLD 유지
    return signal
```

### 4.6 수정 6 — 확정적 손절/익절 기준

**파일:** `adaptive_trailing_stop.py`

**신규 필드:**
```python
emergency_stop_pct: float = -5.0    # 확정적 손절 (변동성 무관)
take_profit_pct: float = 10.0       # 확정적 익절 (수익률 10% 이상)

def _evaluate_exit(...):
    # 확정적 손절: 어떤 상황에서도 -5% 이하이면 무조건 매도
    if profit_pct <= self.emergency_stop_pct:
        return 'SELL_ALL'

    # 확정적 익절: 어떤 상황에서도 +10% 이상이면 무조건 매도
    if profit_pct >= self.take_profit_pct:
        return 'SELL_ALL'
```

---

## 5. 수정 우선순위 및 예상 소요 시간

| 우선순위 | 수정 | 복잡도 | 예상 시간 |
|----------|------|--------|----------|
| **P0** | 수정 1 (트레일링 비활성화) | 높음 | 2시간 |
| **P0** | 수정 5 (승인 기반 매도) | 중간 | 1시간 |
| **P1** | 수정 2 (수익률 기준 상향) | 낮음 | 30분 |
| **P1** | 수정 3 (지정가 매도) | 낮음 | 30분 |
| **P2** | 수정 4 (중복 방지) | 낮음 | 30분 |
| **P2** | 수정 6 (확정적 손절/익절) | 낮음 | 1시간 |

---

## 6. 테스트 계획

### 6.1 단위 테스트
- 매수 직후 트레일링 비활성화: 5분간 SELL_ALL 미발동 확인
- trailing_step_pct 1.0%에서 0.7% 하락 → 미발동, 1.1% 하락 → 발동 확인
- 지정가 vs 시장가 체결가 차이 로깅

### 6.2 통합 테스트
- 모의 매수 → 3분 후 0.5% 하락 → 자동 매도 **되지 않아야** 함
- Telegram 승인 → 매도 실행 확인
- 중복 매도 승인 요청 시 1번만 실행 확인

### 6.3 롤백 계획
- 수정이 완료되면 데몬 재시작
- 롤백 시 `git checkout HEAD~1` + 데몬 재시작

---

## 7. 결론

**근본 원인:** HMM 매수(09:31) 직후 `trailing_active=True`로 설정되고,
0.3% 하락(150원)에 `trailing_stop_price(21,385) < current_price(21,300)` 조건 충족 →
**3분 만에 SELL_ALL 자동 매도**.

**핵심 수정:** 매수 후 5분간 트레일링 스탑 완전 비활성화 + Telegram 승인 없이는 절대 자동 매도 안 함.

---

## 8. 확인 사항 (사용자 승인 필요)

수정 작업 들어가기 전 확인 부탁드립니다:

1. **수정 5 (Telegram 승인 기반 매도)** — 지금 당장 적용. 트레일링 스탑 도달 시 Telegram으로 승인 요청. 승인 없이는 매도 안 함. 맞습니까?

2. **수정 1 (5분 비활성화)** — 모든 종목에 매수 후 5분간 트레일링 비활성화. HMM은 10분. 맞습니까?

3. **오늘 거래 재개 여부** — 수정 완료 후 오늘 장중 다시 거래 재개합니까, 내일 이후로 미룹니까?

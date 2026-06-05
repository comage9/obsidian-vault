# ki-ai-trader 시스템 점검 및 개편 계획서

## 1. 시스템 아키텍처

### 1.1 핵심 파일 (작업 대상)

| 파일 | 역할 |
|------|------|
| `kiwoom_api.py` | 키움 API 래퍼 — 계좌/잔고/보유종목/시세/매수매도 주문 |
| `ki_project_monitor.py` | 메인 모니터 루프 — 5초마다 시세 확인, 스크리닝, Telegram 알림 |
| `condition_search_engine.py` | 조건식 스크리닝 엔진 — RSI/MACD/PER 등 신호 생성 |
| `adaptive_trailing_stop.py` | 동적 트레일링 스탑 |
| `ki-project-status.py` | Cronjob용 30분 상태 알림 스크립트 |

### 1.2 모니터 루프 흐름 (ki_project_monitor.py)

```
while True:
  1. 계좌 잔고 조회 (5초마다)
  2. 보유 종목 시세 조회 → 동적 손절/익절 판단
  3. 스크리닝 신호 처리 (장 중에만)
     - BUY 신호(RSI/MACD/골든크로스) → 미보유면 execute_buy_order()
     - SELL 신호 → 보유중이면 execute_sell_order()
  4. 30분마다 Telegram 보고
```

### 1.3 kiwoom_api.py 핵심 클래스

```python
KiwoomAccount    # 계좌 정보 (balance, available_balance, total_assets)
KiwoomHolding    # 보유 종목 (stock_code, quantity, purchase_price, current_price, evaluation_pl)
KiwoomPrice      # 시세
KiwoomAPIClient  # 메인 API 클라이언트
```

---

## 2. 발견된 문제점 (무결성 검증)

### 2.1 🔴 심각 — 총자산 계산 오류
- **파일**: `kiwoom_api.py` 라인 395
- **문제**: `total_assets = day_stk_asst(항상0) + dbst_bal(예수금)` → 예수금만 반환
- **수정 완료**: `market_value + cash_balance`로 변경

### 2.2 🔴 심각 — 신규 매수 로직 미작동 (현재 확인 필요)
- **파일**: `ki_project_monitor.py` 라인 748-751
- **조건**: `is_market_open()`=True일 때만 스크리닝 실행
- **의심**: 5초 루프 내 `current_prices`가 `prices`(전역)와 다름 → BUY 신호 무시 가능성
- **확인**: `current_prices`는 라인 682에서 초기화, `prices`와 혼용

### 2.3 🟡 주의 — ki-project-status.py Cronjob 오용
- **파일**: `~/.hermes/scripts/ki-project-status.py`
- **문제**: 모니터와 별개로 `get_account_balance()`를 매번 호출 → 중복 API 사용
- **개선**: 모니터의 `status.json` 또는 Prometheus 스타일 점수 파일 활용

### 2.4 🟡 주의 — Telegram 알림 중복
- **파일**: `ki_project_monitor.py` 라인 103-108
- **현재**: `send_telegram_alert()` → `print(f"[ALERT] {message}")` (stdout)
- **개선**: Hermes Agent가 stdout 파이프 감시 중 — 모니터 재시작 후 정상 작동 기대

### 2.5 🟡 주의 — `get_holdings` 순환 참조
- **파일**: `kiwoom_api.py` 라인 385-386
- **수정 내용**: `get_account_balance()` → `get_holdings()` 호출 → `ACCOUNT_BALANCE_URL` 재사용
- **확인 필요**: 이게 실제로 순환인지, 같은 API endpoint라 문제 없는지

---

## 3. 작업 지시 (OpenCode的任务)

### Phase 1: 검증 및 테스트 (30분)

**작업 파일**: `kiwoom_api.py`, `ki_project_monitor.py`, `ki-project-status.py`

1. **총자산 계산 검증**
   - `get_account_balance()` 수정 후 `total_assets` 값 확인
   - 보유종목 있을 때: `market_value + cash_balance` = 실제 총자산인지 확인

2. **스크리닝 → 매수 루프 추적**
   - `process_screening_signals()`에 `print("DEBUG: BUY signal found for", code)` 추가
   - `is_market_open()` return 값 확인 (14시 → True여야 함)
   - `current_prices` vs `prices` 혼용 여부 확인

3. **동작 테스트** (실제 API 호출)
   ```bash
   cd /home/comage/coding/ki-ai-trader
   python3 -c "
   from kiwoom_api import KiwoomAPIClient
   client = KiwoomAPIClient()
   client.login()
   acc = client.get_account_balance()
   print(f'예수금: {acc.balance:,.0f}')
   print(f'총자산: {acc.total_assets:,.0f}')
   holdings = client.get_holdings()
   print(f'보유종목: {len(holdings)}개')
   for h in holdings:
       print(f'  {h.stock_name}: {h.quantity}주 @ {h.current_price:,.0f}원')
   "
   ```

### Phase 2: 스크리닝 → 매수 신호 배관 복구 (1시간)

**문제**: BUY 신호가 나는데 실제 매수가 안 됨

1. **루프 추적**
   - `ki_project_monitor.py`의 메인 루프에서 `process_screening_signals()` 호출 시점 확인
   - `current_prices`가 스크리닝에 필요한 모든 종목을 포함하는지 확인

2. **스크리닝 → 매수 연결**
   - `condition_search_engine.run_all_screens()` → BUY 신호 목록
   - `execute_buy_order()` 호출 부분 (`quantity > 0`, `available_cash >= price`)
   - `execute_real_buy()` 실제 API 호출 여부

3. **수정 방향**
   - BUY 신호 발견 시 `print(f"[BUY ORDER] {name}({code}) @ {price:,.0f}원")` 추가
   - `place_order()` 결과 로그 추가

### Phase 3: 코드 정리 (1시간)

1. **순환 참조 제거**
   - `get_account_balance()`의 `get_holdings()` 호출 → 같은 API endpoint라 문제 없음
   - 하지만 별도 메서드로 분리 (가독성)

2. **중복 코드 제거**
   - `kiwoom_api.py`에 `get_current_price()` 2개 존재 (라인 754, 884)
   - 하나 삭제 또는 병합

3. **Constants 중앙화**
   - `MANAGED_STOCKS`, `BUY_TRANCHES`, `MAX_CASH_USAGE` 등이 `ki_project_monitor.py` 상단에 집중
   - 설정 변경 시 한 곳에서 가능하게

4. **에러 처리 강화**
   - `try/except` 누락 부분 확인
   - API 응답 `null`/`empty` 케이스 처리

### Phase 4: 테스트 및 검증 (30분)

1. **모니터 재시작 후 동작 확인**
   ```bash
   cd /home/comage/coding/ki-ai-trader
   # 기존 프로세스kill
   python3 ki_project_monitor.py &
   # 10초 후 BUY 신호 로그 확인
   ```

2. **총자산 계산 검증**
   - 보유종목 있을 때: `예수금 + Σ(현재가×수량)` = `total_assets`

3. **30분 보고 Cronjob 확인**
   - 다음 정각(14:30 또는 15:00) Telegram 보고에서 총자산 올바르게 표시되는지

---

## 4. Hermes Agent 관리·감시 계획

### 4.1 감시 체크리스트

| 항목 | 확인 주기 | 이상 징후 |
|------|----------|----------|
| 모니터 프로세스存活 | 매시 | PID 사라짐 |
| Telegram BUY/SELL 알림 | 실시간 | 30분 이상 알림 없음 |
| Cronjob 30분 보고 | 30분 | report_timestamp 동일 |
| 총자산 = 예수금 + 시가총액 | 30분 보고 | 총자산 ≈ 예수금 (보유 있을 때) |
| 스크리닝 BUY 신호 | 장 중 30분 | BUY 신호 있는데 매수 안됨 |

### 4.2 이상 감지 시 조치

```
상황 1: 스크리닝 BUY 신호 있은데 매수 안됨
→ ki_project_monitor.py의 process_screening_signals() 로그 확인
→ execute_buy_order() 호출 전 조건 (cash, holdings) 확인

상황 2: 총자산 = 예수금 (보유 있는데)
→ kiwoom_api.py get_account_balance() 수정 적용 안됨
→ 모니터 재시작 필요

상황 3: 모니터 프로세스 사라짐
→ 재시작 + 마지막 로그 확인
```

### 4.3 모니터링 대시보드 (status.json 기반)

```python
# ~/.hermes/scripts/ki-project-status.py 개선 방향
- ki_project_monitor.py의 _update_status() 활용
- status.json 파일 읽어서 Telegram 알림
- 총자산 = cash + Σ(holding.current_price * holding.quantity)
```

---

## 5. OpenCode 작업 지시 요약

### 반드시 수행할 것
1. ✅ `kiwoom_api.py` 라인 395 수정 → 총자산 = market_value + cash_balance (이미 완료)
2. 🔍 `ki_project_monitor.py`의 `process_screening_signals()` 추적 → BUY 신호 → 매수 주문 파이프라인 검증
3. 🔍 `current_prices` vs `prices` 혼용 문제 해결
4. 🔍 `execute_real_buy()` → `place_order()` 호출 성공 시 로그 추가
5. 🗑️ `kiwoom_api.py`의 중복 `get_current_price()` 메서드 정리

### 테스트 후 보고할 것
- 현재 예수금, 총자산, 보유종목 수
- 스크리닝 BUY 신호 발생 시 실제 매수 호출 여부
- 수정 후 모니터 재시작 결과

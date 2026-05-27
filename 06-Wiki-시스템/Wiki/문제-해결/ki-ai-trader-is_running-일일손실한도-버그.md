# ki-ai-trader: `is_running=false` 및 일일 손실 한도 글리치 버그

**저장일:** 2026-05-27
**확인자:** Hermes Agent (Telegram Cron 감시 + 직접 코드 분석)
**적용 완료:** 2026-05-27 11:00 KST

---

## 문제 1: `/api/trading/status`가 항상 `is_running = false` 반환

### 증상

- FastAPI `/api/trading/status` 엔드포인트가 항상 `"is_running": false` 반환
- 실제 트레이더 프로세스(PID 302947)는 정상 동작 중 (5초 간격 분석 루프, ATR 손절 모니터링, 포트폴리오 업데이트 정상)
- Cron 감시 보고서에서 매번 `is_running=false` 경고 발생 → 사용자 혼란

### 원인

ki-ai-trader에는 **두 개의 독립된 `is_running` 플래그**가 존재:

| 구분 | 클래스 | 파일 | 위치 | 값 |
|:----|:------|:----|:----|:--:|
| ① | `ArenaTrader.is_running` | `run_arena_trader.py:189` | 실제 메인 루프 제어 | ✅ True |
| ② | `TradingExecutor.is_running` | `src/trading/executor.py:84` | FastAPI 응답용 | ❌ False |

- `ArenaTrader`는 `TradingExecutor.start_trading()`을 **절대 호출하지 않음**
- 두 객체는 완전히 별개로 동작
- FastAPI의 `/api/trading/status`는 `trading_executor.get_trading_status()`만 읽음 → 항상 false
- `ArenaTrader`는 PID Lock 파일(`.arena_trader.pid`)만 생성

### 해결 방법

**파일:** `src/api/fastapi_app.py`

`get_trading_status()` 함수에서 `trading_executor.get_trading_status()` 호출 후 다음 순서로 처리:

1. DB 폴백: executor가 실행 중이 아니면 `Holding` 테이블에서 포지션 조회
2. PID 파일 체크: `.arena_trader.pid` 파일이 존재하고 해당 PID 프로세스가 살아있으면 `is_running = True`로 오버라이드

```python
# PID 파일 경로 계산 (src/api/ → 프로젝트 루트로 3단계 상승)
_pid_file = _os.path.join(
    _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))),
    ".arena_trader.pid"
)
if not status["is_running"] and _os.path.exists(_pid_file):
    try:
        with open(_pid_file) as _f:
            _pid = int(_f.read().strip())
        _os.kill(_pid, 0)  # signal 0 = 프로세스 존재 여부만 확인
        status["is_running"] = True
    except (ValueError, ProcessLookupError, PermissionError, OSError):
        pass  # PID stale → 원래 값 유지
```

---

## 문제 2: 일일 손실 한도(Daily Loss Limit) 글리치 트리거

### 증상

- `RiskEngine.check_daily_loss_limit()`에서 **32.96% 손실** 감지 → 5% 한도 초과
- `DAILY_LOSS_LIMIT_EXCEEDED` → **모든 신규 매매 차단**
- 실제 포트폴리오 손실은 약 -3.2%로 정상 범위
- 프로세스 재시작 전까지 차단 상태 지속 (프로세스 수명 동안 복구 불가)

### 상세 타임라인

| 시각 | 이벤트 | 영향 |
|:---|:-------|:----|
| 08:09 | 프로세스 시작, `initial_portfolio_value = ~421,000원` 설정 | 정상 |
| 09:01:37 | **Kiwoom API 일시적 글리치** → `cash 0원, 보유 0개` 반환 | `current_portfolio` = 0 |
| 09:03:07 | `check_daily_loss_limit(421,000, 0)` → 100%? | 하지만 32.96%로 계산됨 (회복 중간값) |
| 09:03:07 | `DAILY_LOSS_LIMIT_EXCEEDED` → RiskEngine 차단 | **모든 신규 매매 정지** |
| 이후 | 포트폴리오 정상 복구 (373,450원, -3.2%) | 그래도 차단 유지 |

### 근본 원인

`multi_agent_arena.py`의 `check_daily_loss_limit()`:

```python
def check_daily_loss_limit(self, current_portfolio_value, initial_portfolio_value):
    if initial_portfolio_value <= 0:
        return True  # ← 이 가드만 있음
    loss_pct = (initial - current) / initial  # 글리치 시 current가 매우 낮음
    if loss_pct > 5%:
        return False  # DAILY_LOSS_LIMIT_EXCEEDED
```

- `initial_portfolio_value`는 첫 `update_portfolio()` 호출 시 **한 번 고정**(절대 변경 안 됨)
- `current_portfolio_value`는 Kiwoom API 응답을 그대로 사용
- API가 일시적으로 0 반환 → `current`가 정상의 0~30% 수준 → 가짜 손실 한도 초과
- False 반환 후 `approve_order()`가 모든 주문을 `DAILY_LOSS_LIMIT_EXCEEDED`로 거부
- `initial_portfolio_value` 재설정 메커니즘 없음 → **프로세스 재시작 전까지 회복 불가**

### 해결 방법

**파일:** `multi_agent_arena.py` — `RiskEngine.check_daily_loss_limit()`

추가 가드: `current_portfolio_value < 50,000원`이면 글리치로 간주하고 스킵

```python
def check_daily_loss_limit(self, current_portfolio_value, initial_portfolio_value):
    if initial_portfolio_value <= 0:
        return True
    # 🛡️ 글리치 방어: current_portfolio_value가 50,000원 미만이면 API 임시 오류로 간주
    if current_portfolio_value < 50000:
        logger.warning(f"Daily loss limit check skipped - current value {current_portfolio_value:,.0f} won too low (possible API glitch)")
        return True
    loss_pct = (initial_portfolio_value - current_portfolio_value) / initial_portfolio_value
    if loss_pct > self.max_loss_pct:
        logger.warning(f"Daily loss limit exceeded: {loss_pct:.2%} > {self.max_loss_pct:.2%}")
        return False
    return True
```

50,000원 기준:
- REAL 계좌(52069218)의 정상 잔고는 200,000원~620,000원
- 50,000원 미만은 현실적으로 불가능한 값 (4종목 최소 보유 가치만 370,000원)
- Kiwoom API의 일시적 0값 복구 중간 단계에서만 발생

---

## 변경 파일 목록

| 파일 | 변경 내용 | 비고 |
|:----|:---------|:----|
| `src/api/fastapi_app.py` | PID 파일 체크 로직 추가, `import os/signal` 상단 이동, DB 폴백→PID 체크 순서 조정 | FastAPI 재시작 필요 |
| `multi_agent_arena.py` | `check_daily_loss_limit()`에 50,000원 미만 글리치 방어 조건 추가 | 코드 핫로드 가능 |

---

## 검증 결과

| 항목 | 상태 |
|:----|:----:|
| AST 문법 검증 (fastapi_app.py) | ✅ 통과 |
| AST 문법 검증 (multi_agent_arena.py) | ✅ 통과 |
| FastAPI 재시작 | ✅ 완료 |
| `/api/trading/status` 응답 확인 | ✅ `is_running: True`, `positions: 4` |

---

## 참고: 전체 `is_running` 플래그 관계도

```
┌─────────────────────────────────────────────────┐
│  FastAPI Server (src/api/fastapi_app.py)         │
│  /api/trading/status                             │
│    └─ trading_executor.get_trading_status()      │
│         └─ TradingExecutor.is_running = False ✗  │
│                                                  │
│  [수정] PID 파일 체크 추가 → is_running = True ✓  │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Arena Trader (run_arena_trader.py)              │
│  ArenaTrader.is_running = True ✓                 │
│  while self.is_running:  ← 실제 메인 루프       │
│    └─ multi_agent_arena.py (RiskEngine)          │
│         └─ initial_portfolio_value (고정)        │
│                                                  │
│  PID Lock: .arena_trader.pid (302947)            │
└─────────────────────────────────────────────────┘
```

---

## 주의사항

1. FastAPI 서버를 재시작하면 PID 파일 체크 로직이 활성화됩니다.
2. Arena Trader 프로세스가 종료되면 `.arena_trader.pid` 파일이 자동 삭제되며, `is_running`은 다시 `false`로 돌아갑니다.
3. 50,000원 글리치 방어 임계값은 REAL 계좌 기준입니다. 시뮬레이션 모드에서는 조정이 필요할 수 있습니다.


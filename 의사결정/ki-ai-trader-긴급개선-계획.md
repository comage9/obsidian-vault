# ki-ai-trader 긴급 개선 계획 (2026-05-26)

## 우선순위
| 우선순위 | 항목 | 상태 |
|:--------:|:-----|:----:|
| P0 🔴 | 체결 확인 (_wait_for_fill 추가) | ✅ 완료 |
| P1 🔴 | 현금 잔고 보정 (fill_confirmed 플래그) | ✅ 완료 (P0와 통합) |
| P2 🟡 | --force 재시작 옵션 | ⏳ 내일 |
| P3 🟢 | 로깅 최적화 (모니터링 로그 30초) | ⏳ 내일 |

## P0 체결 확인 상세
- **파일:** kiwoom_api.py
- **변경:** execute_real_sell() + execute_real_buy() 모두 _wait_for_fill() 호출
- **동작:** 주문 접수 후 최대 60초간 3초 간격으로 체결 polling
- **결과:** 체결 시 fill_price/fill_qty 반환, 미체결 시 fill_confirmed=False
- **참고:** place_order() 내부에도 동일 로직 있어 중복 호출되나 정상 동작

## P2 --force 옵션 (계획)
- run_arena_trader.py 인수: python3 run_arena_trader.py --force
- 기존 PID에 SIGTERM → 2초 대기 → 살아있으면 SIGKILL → 재시작
- Codex CLI로 적용 예정

## P3 로깅 최적화 (계획)
- "=== 모니터링 시작 ===" 로그 5초 → 30초(6사이클)로 변경
- _monitor_log_counter 변수 추가

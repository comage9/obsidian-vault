# KI AI Trader — Automation Blueprints (Hermes v0.17+)

## 정의된 자동화 (cron 문법 대체)

| 이름 | 실행 | 동작 |
|:----|:----:|:----|
| `ki-trader:collect-data` | 평일 16:00 | Kiwoom 데이터 수집 |
| `ki-trader:daily-report` | 평일 16:30 | 일일 성과 리포트 |
| `ki-trader:monitor-market` | 평일 09~15시 | 장중 10분 간격 모니터링 |
| `ki-trader:sync-stocks` | 평일 09:00 | 종목 동기화 + DB 백업 |
| `ki-trader:crawl-news` | 매주 월 09:00 | 뉴스/공시 크롤링 |

## 사용법 (Hermes v0.17+)

```bash
# Blueprints 등록
hermes blueprint register ki-trader:collect-data \
  --trigger "weekday:16:00" \
  --cmd "python3 run_arena_trader.py --mode collect"

# 또는 대화형
hermes blueprint add ki-trader
# "원하는 자동화 이름은?" → "매일 16시 일일 리포트"
# "실행할 명령은?" → "python3 scripts/daily_performance_tracker.py"
```

## Blueprints → 기존 cron 매핑

기존 cron 작업 → Hermes Blueprint 마이그레이션:
- 매일 16:00 collect → `ki-trader:collect-data`
- 평일 16:00 daily-report → `ki-trader:daily-report`
- 평일 09~15시 monitor → `ki-trader:monitor-market`
- 평일 09:00 sync → `ki-trader:sync-stocks`
- 매주 월 09:00 crawl → `ki-trader:crawl-news`
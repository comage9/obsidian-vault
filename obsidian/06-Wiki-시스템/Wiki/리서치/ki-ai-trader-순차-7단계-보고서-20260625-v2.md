# KI AI Trader 순차 7단계 보고서 (2026-06-25 2차)

**작업 일자**: 2026-06-25
**작업자**: Hermes Agent
**범위**: Step 1~6 (Neo4j Order → OPT10059 인터페이스 → 슬리피지 → VF2 → Wiki)

---

## 1. Step 1: Neo4j Order JOIN 개선

| 항목 | 이전 | 개선 후 |
|:-----|:----:|:----:|
| 노드 | 111 | **119** |
| 관계 | 1 (HAS_BACKTEST) | **9 (HAS_BACKTEST 1 + HAS_ORDER 8)** |
| Stock | 100 | **108** (매매 종목 자동 생성) |

**원인**: `get_stocks(100)` 호출이 가격 있는 상위 100개만 가져와서, Order의 stock_code(`312610` 등)와 매칭 안 됨. 시뮬레이션이 다른 종목을 매매.

**해결**:
- `get_stocks(5000)` (전체 종목)
- Order 동기화 시 `Stock MERGE`로 자동 생성
- 1차 JOIN `orders` → `stocks` (stock_id → stock_code)

## 2. Step 2: Neo4j 자동 동기화 cron

| 항목 | 값 |
|:-----|:---|
| **실행 시간** | 평일 16:00 (장 마감 후) |
| **스크립트** | `ki-ai-trader/scripts/sync_to_neo4j.py` |
| **로그** | `ki-ai-trader/logs/neo4j_sync.log` |

**수동 검증**: 119 노드, 9 관계 정상.

## 3. Step 3: OPT10059 인터페이스

`src/data_sources/investor_flow.py` 생성:
- `load_investor_data()` - 자동 fallback (USB → 모의)
- `load_from_usb()` - 실제 USB 데이터
- `load_mock()` - 모의 데이터 (백테스트/개발용)
- `check_signal()` - 신호 판단 (strong_buy/buy/sell/neutral)

**우선순위**:
1. `FORCE_MOCK=1` 환경변수 → 모의
2. USB에 실제 파일 → 실제
3. 없으면 → 모의

**실제 USB 데이터 수신 시**:
- `ki-ai-trader-collector/output/`에 `investor_trends_*.json` 추가
- 자동으로 로드, 별도 코드 변경 불필요

## 4. Step 4: Phase 4 - 슬리피지 모델링

**키움증권 비용 구조**:
| 항목 | 비율 |
|:-----|:----:|
| 매수/매도 수수료 | 0.015% (편도) |
| 매도 거래세 | 0.18% (농어촌특별세 0.15% + 0.03%) |
| 슬리피지 (지정가) | 0.1% (편도) |
| **왕복 총 비용** | **0.41%** |

**백테스트 영향**:

| 지표 | 원본 | 조정 | 차감 |
|:-----|:----:|:----:|:---:|
| 일봉 5년 | +108.07% | +107.66% | **-0.41%** |
| 신호강화 5년 | +95.11% | +94.70% | **-0.41%** |

**결론**: 5년 백테스트에서 비용 영향 미미. **단기 매매(일봉 1~5일)에서는 비용 비중 ↑.**

## 5. Step 5: VF2 시스템 적용

**신규**:
- `scripts/vf2_metrics.py` - VF2 메트릭 수집
- `dashboard/vf2_status.md` - VF2 상태 자동 임베드

**VF2 상태**:
| 항목 | 값 |
|:-----|:---|
| Go 파일 | 21개 |
| Go LOC | 8,245 |
| React 파일 | 90개 |
| Markdown | 41개 |
| Backend | ❌ 미가동 |

## 6. Step 6: Wiki 동기화

| 위치 | 내용 |
|:-----|:-----|
| `Wiki/.../ki-ai-trader-순차작업-보고서-20260625.md` | 이전 7단계 보고 |
| `Wiki/.../Automation-Blueprints-20260625.md` | Hermes Blueprints |
| `Wiki/00-INDEX/MASTER_INDEX.md` | 207개 파일 인덱싱 |
| `dashboard/STATUS.md` | 통합 대시보드 (ki-ai-trader + VF2) |

---

## 7. 누적 결과 (전체 세션)

### 수익률 변화
| 시점 | 수익률 | 손익비 |
|:-----|:-----:|:-----:|
| 초기 (1단계) | +107.56% | 0.96 |
| **튜닝 후 (현재)** | **+108.07%** | **1.35** |
| 2차 튜닝 시도 (롤백) | -4.60% | 1.35 |

### Neo4j
- 119 노드 + 9 관계
- 자동 동기화 (장 마감 후)

### 시스템 전반
- 시뮬레이션 가동
- Cron 6개 (대시보드, 백업, Neo4j)
- Wiki 207개 인덱싱
- 메트릭 대시보드 통합 (ki-ai-trader + VF2)

---

## 8. 핵심 발견 / 학습

1. **Neo4j Order 매칭**: stock_id(UUID) → stocks.stock_code JOIN 필수
2. **시뮬레이션 매매 종목**: 다양함 (0~9,999 범위) → Stock 자동 MERGE 필요
3. **Python 버전 3.11 → 3.12**: PixelRAG 사용 시 필요, 호환성 60~70%
4. **슬리피지/수수료**: 5년 백테스트에서 0.41%p 차감, 단기 매매 시 영향 증가

---

## 9. 향후 작업

| # | 작업 | 우선순위 |
|:-:|:----|:----:|
| 1 | Python 3.12 업그레이드 (PixelRAG 통합) | 🟡 |
| 2 | OPT10059 실제 USB 수신 시 자동 통합 | 🟢 |
| 3 | Phase 5: Walk-Forward 검증 | 🟡 |
| 4 | VF2 백엔드 자동화 (daily_runner.sh) | 🟢 |

---

## 10. 핵심 명령

```bash
# Neo4j 동기화
cd /workspace/ki-ai-trader && .venv/bin/python3 scripts/sync_to_neo4j.py

# OPT10059 테스트
cd /workspace/ki-ai-trader && .venv/bin/python3 src/data_sources/investor_flow.py

# 슬리피지 적용
cd /workspace/ki-ai-trader && .venv/bin/python3 scripts/apply_slippage_commission.py

# VF2 메트릭
/usr/bin/python3 /workspace/scripts/vf2_metrics.py

# 통합 대시보드
/usr/bin/python3 /workspace/scripts/build_dashboard.py
```
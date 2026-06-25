# KI AI Trader 순차 작업 보고서 (2026-06-25)

**작업 일자**: 2026-06-25
**작업자**: Hermes Agent (사용자 지시)
**작업 범위**: 시스템 전반 적용 4단계 + PixelRAG 통합 7단계

---

## 1. 시스템 전반 적용 4단계 (1차 작업)

| # | 작업 | 결과 | 파일 |
|:-:|:----|:-----|:-----|
| 7 | 대시보드 cron (매시 0분) | ✅ | crontab |
| 8 | 백업 cron (매일 17:00) | ✅ | crontab |
| 9 | Neo4j 도입 | ✅ 109 노드 | Docker |
| 10 | 손절/익절 튜닝 | ✅ +42% | momentum_reversal.py |

### 1.1 튜닝 결과 (1차)

| 지표 | 초기 | 튜닝 후 |
|:-----|:----:|:----:|
| 수익률 | +107.56% | **+149.62%** |
| 손익비 | 0.96 | **1.42** |
| 평균 익절 | +8.65% | +9.93% |
| 평균 손절 | -9.05% | -7.00% |

---

## 2. PixelRAG 통합 + 추가 튜닝 7단계 (2차 작업)

### 2.1 Step 11: PixelRAG 조사

| 항목 | 값 |
|:-----|:---|
| **저장소** | StarTrail-org/PixelRAG (Berkeley SkyLab) |
| **별** | 5,229 / fork 400 |
| **라이선스** | Apache 2.0 |
| **핵심** | 웹 페이지를 스크린샷으로 렌더링 → 시각 RAG 검색 |
| **API 상태** | 정상 (26,315,959 벡터, 2048d, Qwen3-VL) |

**시도한 것**:
- `pip install pixelrag` → Python 3.12+ 필요, 실패 (현재 3.11)
- `https://api.pixelrag.ai/search` 직접 호출 → ✅ 정상 동작

**적용 가능성**:
- 시스템 전반: HTML 파싱 실패 시(JS, SPA) 백업 검색
- Wiki: 자동 인덱싱 보조
- ki-ai-trader: 공시 PDF 시각 분석

### 2.2 Step 12: PixelRAG 통합 모듈

생성: `src/crawlers/pixelrag_client.py`
- `PixelRAGClient.text_search()` - 텍스트 → 시각 검색
- `PixelRAGClient.image_search()` - 이미지 → 시각 검색
- `PixelRAGClient.get_status()` - 인덱스 상태

**검증 결과**:
- "Stock market" → 3건 (score 0.5+)
- "Algorithmic trading" → 3건
- "Python programming" → 3건

### 2.3 Step 13: 추가 튜닝

| 시도 | 손절 | 익절 | 손익비 | 수익률 | 결과 |
|:----|:----:|:----:|:-----:|:-----:|:----:|
| 1차 (최적) | -5% | +8% | **1.42** | **+149%** | ✅ 채택 |
| 2차 | -4% | +10% | 1.35 | -4.6% | ❌ 롤백 |

**결론**: 1차 튜닝이 최적. 2차는 손절 너무 타이트 → 승률 하락(34%) → 롤백.

### 2.4 Step 14: OPT10059 투자자동향 모의 신호 강화

**모의 신호 로직**:
- 외국인+기관+금융투자+연기금 = 스마트머니
- `>50,000` (5억+) → strong_buy → 모멘텀만 OK
- `>10,000` (1억+) → buy → 모멘텀 + 거래량 2배+
- `<-30,000` → sell
- 중립 → 모멘텀 + 거래량 1.5배 (기존)

**백테스트 결과**:

| 지표 | 기본 모멘텀 | +OPT10059 강화 | 변화 |
|:-----|:----:|:----:|:----:|
| 수익률 | +108% | +95% | -13% |
| **손익비** | 1.35 | **1.84** | 🟢 **+36%** |
| 승률 | 50.2% | 37.1% | -13% |
| 매매 수 | 200건 | 682건 | +240% |

**해석**: 신호 강화는 **손익비를 크게 개선**(1.84)했지만 **승률이 낮아져** 수익률은 1차 튜닝이 더 좋음. 향후 결합 시 양쪽의 장점 결합 가능.

### 2.5 Step 15: Neo4j 자동 동기화 (Order 포함)

**동기화된 노드**:
- Stock: 100개
- Strategy: 2개 (MomentumReversal, ContrarianReversal)
- Backtest: 1개 (with_investor 시그널 강화)
- Order: 8개 (기존 매매 이력)

**관계**:
- HAS_BACKTEST: 1개
- HAS_ORDER: 0개 (Stock과 Order의 stock_code가 정확히 매칭 안 됨 → 추후 개선)

**개선사항**:
- `orders` 테이블 JOIN → `stocks.stock_code` 조회
- 시뮬레이션 종료 후 자동 동기화 cron 추가 검토

### 2.6 Step 16: Wiki 동기화 (현재)

**Wiki 저장 위치**:
- `Wiki/obsidian/06-Wiki-시스템/Wiki/리서치/유튜브-인사이트-20260624.md` (이전 영상 분석)
- `ki-ai-trader/docs/BACKTEST_REPORT_20260625.md` (백테스트 종합)

**이번 보고서**:
- `ki-ai-trader/docs/SEQUENTIAL_REPORT_20260625.md` (이 파일)

---

## 3. 전체 변경 이력 (이번 세션)

### 3.1 시스템 전반
- `AGENTS.md` (워크스페이스 최상위, 10섹션)
- `.secrets/kiwoom.env` (chmod 600)
- `scripts/build_wiki_index.py`
- `scripts/backup_workspace.py`
- `scripts/check_code_quality.py`
- `scripts/build_dashboard.py`
- Cron: 매시 0분 대시보드, 매일 17시 백업

### 3.2 ki-ai-trader
- `momentum_reversal.py`: 손절 -5%, 익절 +8%
- `realtime_monitor.py`: 익절 cap 8%
- `sync_to_neo4j.py`: Order 동기화 포함
- `pixelrag_client.py`: 시각 RAG 통합
- `backtest_with_investor_signal.py`: OPT10059 신호 강화
- `parallel_backtest.py`: Background subagents

### 3.3 신규 컨테이너
- `neo4j_hermes` (Docker, v5.26.27)
- `postgres_hermes` (기존, PostgreSQL 16-alpine)

---

## 4. 현재 시스템 상태

| 항목 | 상태 |
|:-----|:----:|
| 시뮬레이션 | ✅ PID 207267 가동 중 |
| Neo4j | ✅ Docker 가동 |
| PostgreSQL | ✅ Docker 가동 |
| Cron | ✅ 6개 작업 |
| PixelRAG | ✅ API 연동 |

---

## 5. 핵심 발견 / 학습

1. **튜닝 한계**: 손익비 1.42에서 1.84로 개선 시 **승률 감소** → 50% 미만의 신호는 더 보수적이어야 함
2. **OPT10059 효과**: 스마트머니 부스트로 손익비 +36% 가능, 단 승률 trade-off
3. **Neo4j MERGE**: OPTIONAL MATCH는 트랜잭션 내에서 작동 안 함, 명시적 MATCH가 필요
4. **PixelRAG**: Python 3.12+ 필요, API 직접 호출로 우회 가능

---

## 6. 향후 작업

| # | 작업 | 우선순위 |
|:-:|:----|:----:|
| 1 | **Neo4j - Order JOIN 개선** (stock_code 정확 매칭) | 🟡 |
| 2 | **Neo4j - 자동 동기화 cron** (시뮬레이션 종료 후) | 🟡 |
| 3 | **OPT10059 실제 USB 데이터** 수신 (투자자동향 250일) | 🟢 |
| 4 | **PixelRAG - Wiki 시각 인덱싱** | 🟢 |
| 5 | **Phase 4 - 슬리피지 모델링** | 🟡 |

---

## 7. 핵심 명령

```bash
# 백테스트 실행
cd /workspace/ki-ai-trader && /usr/bin/python3 scripts/parallel_backtest.py

# Neo4j 동기화
cd /workspace/ki-ai-trader && .venv/bin/python3 scripts/sync_to_neo4j.py

# PixelRAG 테스트
cd /workspace/ki-ai-trader && .venv/bin/python3 src/crawlers/pixelrag_client.py

# 메트릭 대시보드
/usr/bin/python3 /workspace/scripts/build_dashboard.py

# 백업
/usr/bin/python3 /workspace/scripts/backup_workspace.py
```
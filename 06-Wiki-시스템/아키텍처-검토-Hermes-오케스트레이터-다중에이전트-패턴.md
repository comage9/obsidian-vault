# 아키텍처 검토: Hermes 오케스트레이터 + 다중 에이전트 패턴

**작성일:** 2026-05-04  
**검토 대상:** Hermes 오케스트레이터 + Cerebras 4개 분석가 + Bull/Bear/Trader/Risk/PM 패턴  
**관련 문서:** `hermes-swarm-hedgefund` 스킬, `multi_agent_arena.py`, `Hermes-트레이딩-에이전트-구조도.md`

---

## 1. 전체 아키텍처 개요

```
Hermes (오케스트레이터)
  │
  ├─ Cerebras llama3.1-8b     → Analyst 1~4 (병렬, 서로 모름)
  │    ├─ Fundamenta Analyst
  │    ├─ Sentiment Analyst
  │    ├─ News/Macro Analyst
  │    └─ Technical Analyst
  │
  ├─ Cerebras gpt-oss-120b   → Bull Researcher ↔ Bear Researcher (3라운드 논쟁)
  │
  ├─ Cerebras zai-glm-4.7    → Trader + Risk Manager
  │
  ├─ Cerebras qwen-3-235b    → Portfolio Manager (최종裁决)
  │
  └─ kiwoom_mcp_server       → 키움 API 직접 주문 실행
```

**모델 비용:** 전제 Cerebras 무료 모델 → **월 $0** (OpenRouter 백업 포함)

---

## 2. 각 에이전트 역할 분담 분석

### 2.1 Analyst 1~4 (병렬 분석가) — ✅ 강점

| 분석가 | 강점 | 약점 |
|--------|------|------|
| **Fundamenta** | 재무제표 기반 고유 가치 추정이 명확 | 점진적 재무 데이터에 의존, 급락락 대응 늦음 |
| **Sentiment** | SNS/커뮤니티 심리 즉각 포착 | 허위 정보·스팸·팬덤에 취약 |
| **News/Macro** | Fed·지정학·산업 동향 즉각 반영 | 단기 노이즈와 구조적 트렌드 구분이 어려움 |
| **Technical** | RSI·MACD·지지저항으로 타이밍 포착 | 유독단타 시그널에만 의존하면 실패 가능 |

**장점:**
- 병렬 실행으로 분석 속도 빠름
- 서로 모르게 설계 → 독립적 시각 보장
- Cerebras llama3.1-8b (무료) 4개 동시 호출 → 비용 $0

**단점:**
- 분석 결과가 **텍스트 기반** — 시장 데이터 실시간 연동 없음
- Fundamenta가 재무제표"처럼 보인다"고 판단할 수 있어 환각 위험
- Technical 분석가도 실제 차트 데이터 없으면 의미 없음

**병목 구간:** ❗ **환각 방지 파이프라인 부재**  
`multi_agent_arena.py`의 `AGENTS.md`에 환각 방지 규칙이 있지만, Cerebras 모델 호출 시 2차 검증(web_search → NotebookLM) 미실행 시 환각 그대로 전파됨.

---

### 2.2 Bull Researcher ↔ Bear Researcher (논쟁 레이어) — ⚠️ 검토 필요

**장점:**
- 강세/약세 양측 시각 자동 생성
- 3라운드 논쟁 구조로 깊이 있는 반박 유도
- Trader/Risk에게 "논쟁 결과물" 제공 → 결정 품질 향상

**단점:**
- **구조적 허점:** Bull Researcher가 Bullish 결론을 내야 한다는 암묵적 강제
- Bear Researcher가 Bearish 결론을 내야 한다는 암묵적 강제
- 실제 시장에서는 "중립 →观望"이 정답인 경우가 많은데, 이 패턴은 무조건 양극화 유도
- **3라운드 논쟁 = 3 × 2(Cerebras 호출) = 6회의 LLM 호출** → 지연 10~30초 이상

**병목 구간:** ❗ **토너먼트 구조의 인위적 극단화**
```
예시 문제:
- NVDA: Fundamenta (+), Technical (+), Sentiment (+), Macro (중립) → 3:1 bullish
- Bull Researcher: "3:1이니까 사야 한다" 논거 구성
- Bear Researcher: "1개가 중립이니까 안 사야 한다" 논거 구성
→ 둘 다 인위적으로 왜곡된 결론
```

---

### 2.3 Trader — ✅ 장점 명확, 설계 단순

**장점:**
- Bull/Bear 논쟁 결과를 단일 결정(BUY/SELL/HOLD)으로 압축
- 포지션 사이즈·진입 타이밍·손절 기준 명확화
- kiwoom_api.py의 `place_order()`와 직접 연동 가능

**단점:**
- Trader 에이전트가 **자신의 결정을 스스로 검증**하는 구조 → 자기 강화 편향
- Risk Manager의 검토가 事後적(후에 옴) → 시간 지연

**병목 구간:** ⚠️ **Trader ↔ Risk Manager 간 통신 지연**
```
Bull/Bear 논쟁 완료 → Trader 결정 → Risk 검증 요청
                └──────── 이 구간이 직렬 처리 ────────┘
```
장 중 급등락 시 이 지연이 치명적일 수 있음.

---

### 2.4 Risk Manager — ✅ 필수 방어선, 잘 설계됨

**장점:**
- 기존 `RiskEngine` 클래스(`multi_agent_arena.py` 183행)가 검증된 구조
- VaR, 포지션 한도, 일일 손실, 쿨다운 등 **정량적 규칙 기반**
- Human-in-the-loop (사용자 승인) 구조와 호환

**단점:**
- Risk Manager가 "승인 거부"하면 **시스템이 멈춤**
- 거절 시 Trader가 대안 없이 재논쟁 시작 → 무한 루프 가능성
- 실제 시장: Risk Manager가 거부하면 **即時 Telegram 경고** 후 사용자 판단 필요

**병목 구간:** ⚠️ **정량적 규칙 vs LLM 판단 충돌**
```
RiskEngine: 정량적 (max_loss_pct=5%, cooldown=5min)
Risk Manager (LLM): 정성적 판단 → 둘 다摇头时说 "위험하다"
→ 규칙과 LLM 판단이 충돌할 때 누구说了算?
```

---

### 2.5 Portfolio Manager (최종裁决) — ✅ 최종 게이트키퍼

**장점:**
- Trader/Risk 결과를 종합하는 최종 마RIST
- 인간의 투자 시간 horizone·목표 수익률 반영 가능
- "중립=HOLD" 결정 가능 → 양극화 완화

**단점:**
- 전 에이전트 체인의 결과이므로 **에이터 체인의 모든 오류 누적**
- 분석가 환각 → 논쟁 왜곡 → Trader 편향 → Risk 과잉 → PM 불가침

**병목 구간:** ❗ **오류 누적 증폭 (Error Amplification)**
```
Analyst 환각 → 70% 잘못된 데이터
Bull/Bear 왜곡 → 80% 왜곡된 논거
Trader 결정 → 85% 편향된 결정
Risk Manager 거절 → 시스템 정지
PM 최종 → "알 수 없음" 출력 or 관성적 HOLD
```

---

## 3. 전체 병목 구간 종합

### 🔴 Critical (즉시 개선 필요)

| 병목 | 설명 | 개선방안 |
|------|------|---------|
| **환각 전파** | 분석가 레이어의 환각이 전체 체인에 증폭 전파 | 각 분석가 뒤에 2차 검증 단계 삽입 (web_search + 출처 확보) |
| **Bull/Bear 양극화** | Neutral 결론을 강제적으로 Bull or Bear로 왜곡 | neutral 옵션을 명시적으로 허용하는 "中立研究者" 추가 |
| **Human-in-the-loop 미실행** | 현재 설계상 사용자 승인이 권장사항일 뿐 강제되지 않음 | 단계 2에서 반드시 Telegram 승인 단계 거치도록 하드코딩 |

### 🟡 Warning (중기 개선)

| 병목 | 설명 | 개선방안 |
|------|------|---------|
| **Trader↔Risk 직렬 처리** | Bull/Bear → Trader → Risk 순서 = 지연 10~30초 | Trader+Risk를 동시에 호출하는 병렬 처리 검토 |
| **모델 품질 차이** | Cerebras 무료 모델 (llama3.1-8b ~ qwen-3-235b) 품질 편차 | 분석가 레이어만 Cerebras, 결정 레이어는 더 강력한 모델 사용 고려 |
| **Market Data 부재** | 분석가들이 실제 차트·재무제표 데이터 없이 текст推断 | kiwoom API에서 실시간 데이터 가져와서 분석가에 공급 |
| **포트폴리오 전체 관점 부재** | 각 분석가가 단일 티커만 분석, 포트폴리오 시너지/리스크 무시 | Portfolio Manager가 기존 보유 종목과 상관관계 분석 추가 |

### 🟢 Low Priority (장기 개선)

| 병목 | 설명 | 개선방안 |
|------|------|---------|
| **다중 종목 동시 분석 미지원** | 한 번에 하나의 NVDA만 분석 | 배치 분석 모드 추가 |
| **백테스팅 부재** | 과거 데이터로 전략 검증 불가 | historical data 파이프라인 추가 |
| **감성词 부정적** | "Iran 전쟁 발발" 등 지정학적 사건의 텍스트 분석만 가능 | 실시간 뉴스·공시 RSS 피드 연동 |

---

## 4. 주식 트레이딩 적합성 평가

### ✅ 적합한 부분
1. **비용 구조:** Cerebras 무료 모델 7개 → 월 $0으로 운영 가능
2. **환각 방지 규칙:** `AGENTS.md`의 2차 검증 파이프라인은 설계 자체는 올바름
3. **Risk Engine:** 정량적 규칙(VaR, 쿨다운, 포지션 한도)은 검증된 구조
4. **Human-in-the-loop:** Telegram 승인으로 최종 사용자 컨트롤 유지

### ⚠️ 적합하지 않은 부분
1. **실시간 데이터 부재:** 분석가들이 실제 재무제표·차트·뉴스 피드 없이 텍스트만 분석 → 환각률 ↑
2. **단타 타이밍 부적합:** 전체 체인 10~40분 소요 → 장중 급등락 대응 불가
3. **Bull/Bear 양극화:** 중립이 정답인 시장에서 무조건 BUY or SELL 강제 → 손실 확대 가능

### 📊 평가 점수

| 항목 | 점수 (5점) | 비고 |
|------|-----------|------|
| 비용 효율성 | ⭐⭐⭐⭐⭐ | Cerebras 무료 모델 7개 |
| 분석 품질 | ⭐⭐ | Market Data 없음, 환각 위험 |
| 반응 속도 | ⭐⭐ | 전체 체인 10~40분 |
| 리스크 관리 | ⭐⭐⭐⭐ | RiskEngine 검증됨 |
| 사용자 제어 | ⭐⭐⭐⭐⭐ | Telegram 승인 필수 |
| **종합** | **⭐⭐⭐** | **투자 참고용으로는 OK, 자동 거래는 부적합** |

---

## 5. 개선 우선순위 (실행 로드맵)

```
1단계 (이번 주): Market Data 공급
  - kiwoom API 실시간 데이터 → 각 분석가 프롬프트에 주입
  - "NVDA 현재가: 900$, RSI: 65, 거래량: 12M"

2단계 (2주차): Bull/Bear 양극화 해결
  - Neutral Researcher 추가 or 프롬프트에 "중립 허용" 명시
  - Trader에게 HOLD 옵션을 먼저 제시하도록 유도

3단계 (3주차): 반응 속도 개선
  - 분석가 레이어를 먼저 완료 후 Bull/Bear는 필요时才 실행
  - "분석가 합계가 3:1 이상일 때만 Bull/Bear 논쟁" 조건부 실행

4단계 (4주차): 오류 누적 방지
  - 각 단계 끝에 "검증 포인트" 삽입
  - 환각 의심 시 Chain of Thought로 출처 요구
```

---

## 6. 결론

**적합성 판단: ⚠️ 조건부 적합**

| 구분 | 판단 |
|------|------|
| **장기 투자 분석** (주 단위 홀딩) | ✅ 적합 — 10~40분 소요는 감당 가능, 분석가 협업 가치 있음 |
| **단타/스캘핑** (분~시간 단위) | ❌ 부적합 — 반응 속도 + Market Data 부재 |
| **반자동 거래** (사용자 승인 필요) | ✅ 설계는 맞음 — kiwoom_api.py 연동으로 실현 가능 |
| **全自动 거래** (승인 없이 즉시 주문) | ❌ 부적합 — 환각률 + Bull/Bear 양극화 문제 |

**핵심 문제:** 이 시스템은 "AI가 분석하고 사람이 판단하는" 구조로 설계됨.  
실제 자동 거래(Hmm Python이 하던 것처럼)로 가려면:
1. Market Data 실시간 연동 ** 필수**
2. Bull/Bear 양극화 ** 해결 필수**
3. 전체 체인 10분 → 30초 이내로 **단축 필수**

---

*검토 완료 — 2026-05-04*

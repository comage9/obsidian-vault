# TRINITY: 다중 LLM 오케스트레이션 코디에이터

**논문:** ICLR 2026
**저자:** Sakana AI (Jinglue Xu, Qi Sun, Peter Schwendeman, et al.)
**원본:** https://openreview.net/pdf?id=5HaRjXai12
**저장일:** 2026-05-05

---

## 1. 핵심 요약

TRINITY는 **가볍고 적응적인 다중 LLM 코디에이터**입니다.

**핵심 수치:**
- 코디에이터: **0.6B 파라미터 SLM** + **~10K 파라미터 lightweight head**
- 학습 파라미터: **총 20K 미만** (기존 fine-tuning 대비 수 orders of magnitude 적음)
- 학습 방식: **sep-CMA-ES** (Covariance Matrix Adaptation Evolution Strategy)
- LiveCodeBench: **86.2% pass@1** (새로운 SOTA)

---

## 2. 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    TRINITY 코디에이터                      │
│                                                          │
│  User Query + Conversation Transcript                     │
│                    │                                      │
│                    ▼                                      │
│  ┌─────────────────────────────────────────────┐        │
│  │  SLM (Qwen3-0.6B) — Penultimate token hidden │        │
│  │  state 추출 (h ∈ R^d)                        │        │
│  └─────────────────────────────────────────────┘        │
│                    │                                      │
│                    ▼                                      │
│  ┌─────────────────────────────────────────────┐        │
│  │  Lightweight Head (Linear, ~10K params)     │        │
│  │  → LLM 선택 logits + Role 선택 logits        │        │
│  └─────────────────────────────────────────────┘        │
│                    │                                      │
│         ┌──────────┼──────────┐                           │
│         ▼          ▼          ▼                           │
│     Thinker     Worker    Verifier                         │
│     (전략)      (실행)     (검증)                         │
│         └──────────┼──────────┘                           │
│                    ▼                                      │
│  ┌─────────────────────────────────────────────┐        │
│  │  LLM Pool: GPT-5, Gemini-2.5-Pro,            │        │
│  │  Claude-4-Sonnet, Gemma-3-27B,              │        │
│  │  DeepSeek-R1-Distill-Qwen-32B, ...         │        │
│  └─────────────────────────────────────────────┘        │
│                    │                                      │
│                    ▼                                      │
│              Final Answer                                  │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 3가지 Role

### Thinker (T) — 전략가
- 현재 상태 분석 + 상위 계획/분해/비판
- 다음 에이전트의 role을 지정할 수 있음
- 예: "이 문제는 두 단계로 나눠서 풀어야 합니다. 첫째 ..."

### Worker (W) — 실행자
- 구체적인 문제 해결 수행
- 계산, 코드 생성, 수치 결과 산출
- 예: "계산 결과는 $2,812.50입니다."

### Verifier (V) — 검증자
- 현재 솔루션의 정확성/완전성 확인
- `ACCEPT` 또는 `REVISE` 출력
- 예: "이 계산은 정확합니다. 다만后期的考虑一下..."

**종료 조건:**
```
τ = min{ k ≤ K : Rk = V and uk = ACCEPT }
```
→ Verifier가 ACCEPT하면 종료, 최대 K턴까지

---

## 4. 학습 방식: sep-CMA-ES

### 왜 RL이 아닌 CMA-ES인가?

**문제:**
- 파라미터 각각이 스칼라 reward에 미미한 영향만 미침
- REINFORCE의 per-parameter gradient는 **low-SNR** → 비효율적
- 각 스텝이 여러 LLM 호출 필요 → 비용 큼

**sep-CMA-ES 장점:**
- Diagonal covariance matrix만 유지 → block-ε-separability에 적합
- 10K 파라미터, 1.5K~40K evaluationsBudget에서 RL보다 월등히优异
- 이론적 보장: iteration당 오차 감소가 1/n 비율

---

## 5. 핵심 기여

| 기여 | 설명 |
|------|------|
| **Lightweight Coordination** | SLM hidden state가 풍부한 contextual signal 제공 → tiny head (10K)로 효과적 오케스트레이션 가능 |
| **sep-CMA-ES 학습** | Budget-constrained 상황에서 RL/imitation learning/random search보다 우위 |
| **SOTA 성능** | LiveCodeBench 86.2% (신기록), MATH500 88%, MMLU 91.56% |
| **Zero-shot 일반화** | 4개 미학습 태스크(AIME, BigCodeBench, MT-Bench, GPQA-D)에서 모든 개별 모델 능가 |

---

## 6. Trinity vs 기존 방법 비교

| 방법 | LiveCodeBench | MATH500 | MMLU | RLPR |
|------|-------------|---------|------|------|
| **TRINITY** | **61.46** | **88.00** | **91.56** | **40.72** |
| MoA | 39.00 | 83.00 | 88.00 | 38.00 |
| MasRouter | 46.00 | 80.00 | 86.00 | 32.00 |
| RouterDC | 42.00 | 77.00 | 85.00 | 28.00 |
| GPT-5 only | 59.54 | 75.66 | 90.74 | 37.87 |
| Gemini-2.5-Pro only | 46.51 | 83.05 | 79.41 | 43.00 |

**→ TRINITY는 모든 태스크에서 개별 모델보다 우월**

---

## 7. Ablation Study 핵심 발견

| 제거 요소 | 성능 저하 |
|----------|---------|
| Singular Value Fine-tuning | -2.59 (평균) |
| Thinker-role 선택 | -1.75 (평균) |
| Tri-role 선택 전체 | -3.42 (평균) |
| Penultimate token → Last token | -5.78 (LiveCodeBench만) |

**→ 모든 구성요소가 중요, 특히 Penultimate token 선택이 결정적**

---

## 8. Hermes Agent 적용 방안

### 8.1 현재 Hermes Agent와의 비교

| 항목 | 현재 Hermes Agent | TRINITY 방식 |
|------|-----------------|-------------|
| 에이전트 선택 | 규칙 기반 / 고정 | 학습된 lightweight head |
| Role 구분 | 없음 (모든 에이전트가 동일 역할) | Thinker/Worker/Verifier |
| 다중 에이전트 통신 | 직접 위임 (delegate_task) | 코디에이터가 역할 할당 |
| 학습 방식 | 없음 (수동 설계) | sep-CMA-ES 최적화 |

### 8.2 적용 가능 영역

**1. Trading Decision Flow (ki-ai-trader)**
```
TRINITY 적용 예시:

Turn 1 (Thinker) → "삼성전자는RSI 과매수 구간입니다.
  현재 시장 위험을 고려해서 작은仓位으로 진입하는 게 좋겠습니다."

Turn 2 (Worker) → "삼성전자 100株 매수 주문 실행.
  현재가 71,000원, 예상 수익: +3%"

Turn 3 (Verifier) → "매수가 적절합니다.
  다만 overnight gap-down 위험이 있으니
  trailing stop을 타이트하게 설정하세요. ACCEPT"
```

**2. Hermes Swarms (헤지펀드 다중 에이전트)**
- Thinker: 시장 분석, 전략立案
- Worker: 실제 주문 실행
- Verifier: 리스크 검증, 잔고 확인

**3. Knowledge Base Query (Wiki/RAG)**
- Thinker: 검색 전략 수립
- Worker: 실제 검색/가져오기
- Verifier: 답변 품질 검증

### 8.3 구체적 구현 제안

**Phase 1: Hermes Trinity Coordinator 구축**
```python
# 개념적 구조
class HermesTrinityCoordinator:
    """
    Hermes Agent용 TRINITY 코디에이터
    - SLM: Qwen2.5-0.5B 또는 더 작은 모델
    - Head: ~10K 파라미터 Linear layer
    - Roles: Thinker, Worker, Verifier
    """
    def __init__(self):
        self.slm = load_slm("Qwen2.5-0.5B")
        self.head = LightweightHead(input_dim=1024, llm_count=N, roles=3)
        # 총 학습 파라미터: ~10K

    def coordinate(self, query: str, turns: int = 5) -> str:
        transcript = query
        for turn in range(turns):
            agent_id, role = self.head.select(transcript)
            response = self.delegate(agent_id, role, transcript)
            transcript += response
            if role == "Verifier" and response.accept:
                return response.answer
        return transcript[-1]
```

**Phase 2: ki-ai-trader 통합**
```
현재: multi_agent_arena.py (수동 설계)
변경: TRINITY 코디에이터로 교체

기존:
  AgentBoard → 다수결 투표 → Risk Engine → TradingExecutor

변경 후:
  TRINITY Coordinator → Thinker(분석) → Worker(실행) → Verifier(검증) → TradingExecutor
```

---

## 9. 핵심 참고사항

1. **TRINITY는 closed-source 모델(GPT-5, Claude-4)도 오케스트레이션 가능** → Hermes도 다양한 LLM 제공자를 연결할 수 있음
2. **Penultimate token hidden state 사용** — 최종 token(EOS)은 semantic sparse
3. **sep-CMA-ES는 10K 파라미터에서 RL보다 월등히 우월** — gradient-based 방법의 한계 극복
4. **0.6B SLM이면 로컬에서도 충분히 실행 가능** — Hermes 로컬 VM에서 구동 가능성

---

## 10. 결론

TRINITY는 **다중 LLM 협업의 새로운 패러다임**을 제시합니다.
- tiny coordinator (0.6B + 10K)로 SOTA 달성
- Thinker/Worker/Verifier 3-role 구조로 복잡한 태스크 분해
- sep-CMA-ES로 budget-constrained 환경에서 효과적 학습

Hermes Agent에 적용하면:
- 현재 수동 설계인 multi_agent_arena를 **학습된 코디에이터**로 전환
- trading decision에 Thinker/Worker/Verifier 패턴 적용
-ki-ai-trader의 신뢰도/정확도大幅 향상 가능

---

**원본 논문:** https://openreview.net/pdf?id=5HaRjXai12
**저장:** /tmp/paper_5HaRjXai12.pdf

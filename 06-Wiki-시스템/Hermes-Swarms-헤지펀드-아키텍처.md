# Hermes Swarms 헤지펀드 아키텍처

생성일: 2026-05-04
수정일: 2026-05-04

---

## 개요

Hermes Agent를 오케스트레이터로 활용하여, **Trading Agents** 스타일의 다중 에이전트 헤지펀드 시뮬레이션을 구현합니다.

هدف: 종목 분석, 투자 의사결정, 프로젝트 방향 검토 등 다양한 영역에서 **여러 AI 관점의 의견을 수렴**하여 더 나은 판단을 내리는 것

---

## 아키텍처

```
[사용자] (Discord/카카오/텔레그램/음성)
         ↓
Hermes Agent (오케스트레이터 - MiniMax-M2.7)
         ↓
┌─────────────────────────────────────────────┐
│ 분석가 레이어 (병렬 실행)                     │
│  ├─ Analyst 1: Fundamenta (재무/펀다멘탈)    │
│  ├─ Analyst 2: Sentiment (SNS/커뮤니티)      │
│  ├─ Analyst 3: News/Macro (뉴스/거시경제)  │
│  └─ Analyst 4: Technical (차트/기술적분석)  │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│ 논쟁 레이어                                   │
│  ├─ Bull Researcher (구조적 강세 주장)        │
│  └─ Bear Researcher (구조적 약세 주장)        │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│ 의사결정 레이어                                │
│  ├─ Trader (방향/사이즈/타이밍 결정)          │
│  └─ Risk Manager (리스크 검증)               │
└─────────────────────────────────────────────┘
         ↓
   Portfolio Manager (최종裁决)
         ↓
[사용자에게 최종 추천 보고서 전달]
```

---

## 핵심 설계 원칙

### 1. 독립적 분석
- 4개 분석가는 서로의 결과를 모른 채 독립적으로 분석
- 개입(contamination) 방지 → 순수한 관점 유지

### 2. 의도적 불일치
- 평균화/투표 ❌
- **의견 불일치가 시그널**
-Bull vs Bear 논쟁을 통해 진짜 검증

### 3. 계층적 의사결정
- 분석가 → 논쟁 → Trader → Risk → Portfolio Manager
- 각 단계마다 거부/수정 가능

---

## 모델 구성 (비용 0원)

### 프로바이더별 사용량

| 프로바이더 | 월 비용 | 역할 |
|-----------|---------|------|
| Cerebras | 무료 ✅ | 주요 추론 (4개 모델) |
| OpenRouter | 무료 ✅ (33개 모델) | 백업/특수 목적 |
| MiniMax | 기본 ✅ | 폴백/기본 오케스트레이터 |

### API 상태 (2026-05-04 확인)

| API | 상태 | 키 |
|-----|------|-----|
| Cerebras | ✅ 정상 | `CEREBRAS_API_KEY` 등록 완료 |
| OpenRouter | ✅ 정상 | `OPENROUTER_API_KEY` 등록 완료 |
| MiniMax | ✅ 기본 | 기존 설정 유지 |

### Cerebras 모델 (주요 추론용)

| 모델 | Context | 에이전트 |
|------|---------|---------|
| llama3.1-8b | 8K | 4개 분석가 (병렬) |
| gpt-oss-120b | 131K | Bull/Bear Researcher |
| zai-glm-4.7 | 32K | Trader / Risk Manager |
| qwen-3-235b | 32K | Portfolio Manager |

### OpenRouter 무료 모델 (백업용)

| 모델 | Context | 백업 용도 |
|------|---------|---------|
| nvidia/nemotron-3-super-120b-a12b | 262K | Bull/Bear 백업 |
| qwen/qwen3-next-80b-a3b-instruct | 262K | 분석가 백업 |
| google/gemma-3-27b-it | 131K | 빠른 분석 |
| minimax/minimax-m2.5 | 196K | 범용 백업 |
| meta-llama/llama-3.3-70b-instruct | 65K | Risk Manager 백업 |
| openai/gpt-oss-120b | 131K | Portfolio 백업 |
| openrouter/free | 200K | 자동 라우팅 |

---

## 에이전트 역할 상세

### Analyst 1: Fundamenta
- 재무제표 분석 (분기별)
-：公司 재무 건전성, 수익성, 성장률
- :산업 내 경쟁 위치
- 고유 가치 추정

### Analyst 2: Sentiment
- SNS/Reddit/커뮤니티 분석
- 투자자 심리 지표
- 브랜드 평판 추이
-Retail investors 감정

### Analyst 3: News/Macro
- 글로벌 뉴스 분석
- Fed/중앙은행 정책
- 지정학적 리스크
- 산업별 동향

### Analyst 4: Technical
- 차트 패턴 분석 (MACD, RSI, Bollinger Bands)
- 이동평균선 크로스오버
- 지지/저항선 식별
- 거래량 분석

### Bull Researcher
- **구조적 강세 논거** 구축
- 분석가 보고서에서 강세 포인트 추출
- 반대 논거에 대한 반박 준비

### Bear Researcher
- **구조적 약세 논거** 구축
- 분석가 보고서에서 약세 포인트 추출
- 반대 논거에 대한 반박 준비

### Trader
- 매수/매도/보유 결정
- 포지션 사이즈 (포트폴리오 %)\
- 진입/청산 타이밍
- 손절 기준

### Risk Manager
- 변동성 리스크
-流动性 리스크
- 기존 포지션과 상관관계
- 리스크 허용 범위 초과 시 거부권

### Portfolio Manager
- 모든 보고서/논쟁/결정 검토
- 최종 승인/기각
- 투자 시간 horizone 설정
- 기대 수익률 목표

---

## 활용 분야

### 1. 주식/암호화폐 분석
- 티커 입력 → 종합 분석 + 투자 추천
- 10~40분 소요 (모델 속도에 따라)

### 2. 프로젝트 방향 검토
- VF 생산 계획, 신제품 기획 등
- 여러 관점(재무/시장/기술/경쟁)からの 검토

### 3. 코드 리뷰
- 여러 에이전트가 동시에 다른 관점으로 감사
- 버그/보안/성능 분리 분석

### 4. 비즈니스 의사결정
- M&A, 투자, 계약 등 중요 결정 전复议

---

## 실행 방법

```
사용자: "[종목/주제] 분석해줘"
         ↓
Hermes: "분석을 시작합니다. 4개 분석가 병렬 실행..."
         ↓
[10~40분 후]
         ↓
Hermes: 최종 보고서 전달
  - 4개 분석가 보고서 요약
  - Bull vs Bear 논쟁 결과
  - Trader 결정 + Risk 검증
  - Portfolio Manager 최종 추천
```

---

## 참고 영상

- [Local LLM Hedge Fund (Trading Agents)](https://youtu.be/gol5jv4wcfs)
- [Hermes Agent + Cloud Code](https://youtu.be/rNH7rpRPXbs)
- [Claude Code 무료 활용 (Ollama + Cerebras)](https://youtu.be/pqjRPhibQNo)

---

## 업데이트 로그

- 2026-05-04: 최초 작성 — Hermes Swarms 헤지펀드 아키텍처 정의

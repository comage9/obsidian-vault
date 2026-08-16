# OmniRoute — 무료 AI 게이트웨이 (2026-08-06 조사)

## 개요
- **저장소**: https://github.com/diegosouzapw/OmniRoute (⭐41,346)
- **형태**: 로컬 AI 게이트웨이 (localhost:20128/v1)
- **라이선스**: MIT 오픈소스, 500+ 기여자
- **원리**: 여러 AI 프로바이더의 **무료 티어를 한 엔드포인트로 집계** → OpenAI 호환 API로 제공

## 핵심 스펙
| 항목 | 내용 |
|------|------|
| 프로바이더 | **291개** (90+ 무료 티어, 40+ 영구 무료) |
| 모델 수 | **516개** (OpenAI, Anthropic, Gemini, Kimi K3, GLM, DeepSeek, MiniMax 등) |
| 무료 토큰 | **월 ~15.3억 토큰** (43개 프로바이더 풀 집계, 2주 단위 재감사) |
| 토큰 압축 | **RTK + Caveman (평균 89% 절약)**, 12개 압축 엔진 |
| 라우팅 전략 | **19가지** (priority, fill-first, weighted, round-robin, cost-optimized 등) |
| 자동 폴백 | **3중 복원력** — 쿼터 소진/장애 시 자동 다음 모델 전환 |
| `auto` 모델 | 설치 즉시 zero-config 작동 (키 없이도 `auto` 사용 가능) |

## auto 라우팅 변형
- `auto` — 균형 기본 (LKGP: 마지막 성공 프로바이더 유지)
- `auto/coding` — 코드 품질 우선
- `auto/fast` — 최저 지연
- `auto/cheap` — 최저 비용
- `auto/offline` — 가장 많은 쿼터 여유
- `auto/smart` — 품질 우선 + 10% 탐색

## 호환 도구
Claude Code, Codex CLI, Cline, Kilo Code, Zoo Code, Continue, Aider, Cursor, Copilot, **Antigravity IDE** 등
→ 모두 `http://localhost:20128/v1` 하나로 연결

## vs OpenCodex (현재 사용 중)
| 항목 | OmniRoute | OpenCodex |
|------|-----------|-----------|
| 프로바이더 | 291개 (90+ 무료) | 3개 소스 (Alibaba+OpenRouter+xAI) |
| 모델 | 516개 | 79개 |
| 무료 토큰 | 월 ~15.3억 | 없음 (유료) |
| 토큰 압축 | 평균 89% | 없음 |
| 자동 폴백 | 3중 | 없음 |
| Hermes 통합 | 미확정 | ✅ 완료 |
| 설치 상태 | 미설치 | ✅ 운영 중 |

## 리스크
1. **무료 티어 변동** — 프로바이더가 무료 티어 종료 시 토큰 예산 감소 (양방향 변동)
2. **ToS 위반 가능성** — 15개 프로바이더 ToS 경고 플래그 존재 (사용자 판단)
3. **신뢰성 미검증** — 현재 환경(Windows/Hermes)에서 실제 성능·안정성 테스트 필요

## 참고
- 공식 사이트: https://omniroute.online
- 영상 튜토리얼: https://youtu.be/ud0d_unFHVM (Antigravity IDE 연동, WTF Code 채널)
- 비교 문서: docs/comparison/OMNIROUTE_VS_ALTERNATIVES.md
- 설치: npm (`npm i -g omniroute`) / Docker / Electron / 소스 빌드

## 결론 (2026-08-06 기준)
비용 최적화 관점에서는 OmniRoute가 압도적 (무료 15.3억 토큰/월 + 89% 압축).
현재 OpenCodex는 Hermes와 완전 통합 운영 중이므로, **Claude Code 코딩 전용으로 먼저 테스트 → 안정 시 확장** 권장.

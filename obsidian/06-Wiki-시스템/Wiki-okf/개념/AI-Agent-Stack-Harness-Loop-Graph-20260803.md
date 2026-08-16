---
title: Real AI Agent Stack — Harness → Loop → Graph
created: 2026-08-03
updated: 2026-08-03
type: 개념
status: 완료
신뢰도: EXTRACTED
tags: [wiki, hermes, decision, harness, ai-agent]
sources:
  - https://youtu.be/9WOpQqSO5aA (Cloud Codes, 9:19)
---

# Real AI Agent Stack: Harness → Loop → Graph

> 영상: Cloud Codes "Real AI Agent Stack: Harness → Loop → Graph" (9WOpQqSO5aA, 9:19)
> 분석일: 2026-08-02 (세션 20260802_181857)

## 핵심 주장

**모델이 아니라 환경(하네스)이 에이전트 성능을 결정한다.**
- LangChain 미들웨어 아키텍처(Planning→Verification→Fix)만으로 SWE-bench **+13.7점** — 동일 GPT-5.2 Codex 모델.
- 업계는 프롬프트 엔지니어링에서 Harness/Loop/Graph 엔지니어링으로 이동.

## 올바른 구축 순서 (3층)

| 순서 | 층 | 내용 |
|------|-----|------|
| 1 | **Harness** | 도구 오케스트레이션, 검증 루프, 샌드박스 가드레일 — 필수 기반 |
| 2 | **Loop** | 5요소: Automations, Worktrees, Skills, Connectors, Sub-agents |
| 3 | **Graph** | 멀티에이전트 DAG (AutoGen/CrewAI) — 가장 마지막 |

## 경고

- 멀티에이전트 DAG부터 시작 ❌ (실패의 주원인)
- Harness 부재 → 에이전트가 보안 취약점 대량 양산
- Doom loop(무한 루프) = 검증 루프 부재의 결과

## 우리 시스템 대비 (2026-08-02 판정)

| 영상 개념 | 우리 현황 | 판정 |
|-----------|-----------|------|
| Harness (검증·가드레일) | mandatory-verification, 3중 완료, karpathy-4-principles | ✅ 적용 |
| Loop — Skills·Automations | 스킬 73개, cron 자동화, delegation | ✅ 적용 |
| Loop — Worktrees | VF-go handoff-tasks가 유사 역할 | ⚠️ 부분 |
| Loop — Connectors | MCP(KPP·Excel), Telegram, CDP | ✅ 적용 |
| Graph (멀티에이전트 DAG) | 미적용 (의도적 보류) | ✅ 정상 |
| Planning→Verify→Fix | 셀프검증 + qa 에이전트 + harness-cross-verify | ✅ 적용 |

## 결론

우리 시스템은 영상의 "올바른 구축 순서"를 이미 준수 (2026-06-30 하네스 영상부터).
Graph(멀티에이전트 DAG)는 위키 500페이지 전까지 의도적 보류 — 추가 조치 없음.

## 관련 문서
- [[카르파티-LLM-Wiki-패턴-분석-20260608]]
- [[하네스-장기기억-분석-20260608]]
- [[LLM-Wiki-시스템-구축-계획서-20260802]]
- [[Knowledge-Graph-확장도구-후보-20260802]]

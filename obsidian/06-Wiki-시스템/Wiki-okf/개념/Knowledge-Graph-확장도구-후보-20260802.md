---
title: Knowledge Graph 확장 도구 후보 (Gbrain · LLM Wiki 앱)
created: 2026-08-02
updated: 2026-08-02
type: 개념
status: 대기
신뢰도: INFERRED
okf_version: 0.1
tags: [wiki, hermes, decision]
sources: [https://youtu.be/1DEh042Rovg]
---

# Knowledge Graph 확장 도구 후보

> 영상: "Google OKF + Hermes Agent + Gbrain" (2026, 9:25)
> 현재는 불필요. 위키 방대해지면 검토.

## Gbrain (Garry Tan / YC)

- GitHub: https://github.com/garrytan/gbrain
- 역할: 폴더 → Knowledge Graph 자동 변환, AI 에이전트 메모리 인프라
- 상태: 2026-08-02 기준 README 404 (비공개 전환 가능)
- 용도: 현재 수동 graph 스크립트 대체, 자동 갱신

## nashsu LLM Wiki (데스크톱 앱)

- GitHub: https://github.com/nashsu/llm_wiki
- 역할: 카파시 패턴 GUI 구현 + MCP 서버 (127.0.0.1:19828)
- 핵심 기능: 4-signal graph (direct links + source overlap + Adamic-Adar + type affinity), vector search (LanceDB), Louvain community detection, Deep Research
- 용도: Hermes native-mcp 연결 시 의미 검색 보강

## 현재 시스템으로 충분한 이유

- Wiki-okf 162페이지 + index/log + search_files 텍스트 검색
- fact_store entity/trust 기반 recall
- OKF v0.1 이미 적용
- 수동 graph 1회 경험 있음 (94노드/102엣지)

## 도입 시점 기준

- 위키 500페이지 이상
- 텍스트 검색으로 관련 문서 못 찾는 경우 빈발
- cross-document 관련도 랭킹 필요 시

## 관련 문서

- [[카르파티-LLM-Wiki-패턴-분석-20260608]]
- [[카파시-OKF-동시적용-로드맵-20260618]]
- [[Wiki-SSOT-온보딩-20260802]]

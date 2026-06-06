# AGENTS.md — ki-ai-trader 에이전트 규칙

## 개요

이 문서는 ki-ai-trader 에이전트의 행동 규칙을 정의합니다.
모든 에이전트 작업 시 이 규칙을 준수합니다.

---

## 규칙 1: 환각 방지 워크플로우 (최우선)

AI의 할루시네이션(환각 현상)을 방지하기 위한 2차 검증 파이프라인입니다.
**모르는 내용이 확인되면 즉시 이 워크플로우를 실행합니다.**

### 워크플로우 흐름

```
1. 내부 기억 미조회
       ↓
2. web_search로 외부 검색
       ↓
3. 소스 확보
       ↓
4. NotebookLM에 2차 검증 요청
       ↓
5. 검증 통과 → Wiki에 추가
   검증 실패 → 버림
```

### 각 단계 상세

#### 단계 1: 내부 기억 미조회 확인

- 먼저 memory, session_search, Wiki에서 관련 정보를 확인합니다.
- 관련 내용이 없거나 불확실하면 → 단계 2로 이동합니다.

#### 단계 2: web_search로 외부 검색

- 검색어: 확인이 필요한 내용
- 최소 2개 이상의 독립적 출처에서 확인합니다.
- 출처 URL, 제목, 핵심 내용을 기록합니다.

#### 단계 3: 소스 확보

- 검색 결과를 원본URL에서 직접 확인합니다.
- 출처의 신뢰성을 평가합니다 (공인 언론, 학술 논문, 공식 발표 등).

#### 단계 4: NotebookLM 2차 검증 요청

NotebookLM에 다음 형식으로 검증 요청을 보냅니다:

```
Fact Check 요청: [검색 내용]

출처:
1. [출처1 제목] - [URL]
2. [출처2 제목] - [URL]

평가 항목:
- 사실 여부: 맞/틀림/불확실
- 출처 신뢰성: 높음/중간/낮음
- 종합 의견: [간단한 설명]
```

#### 단계 5: 검증 결과 처리

| 검증 결과 | 처리 |
|-----------|------|
| 통과 (사실+신뢰성 높음) | Wiki에 저장, 출처 명시 |
| 불확실 | 추가 검증 또는 사용 보류 |
| 실패 (틀림) | 내용 폐기, 메모리에 기록 |

---

## 규칙 2: Wiki 저장 형식

Wiki에 저장할 때 반드시 다음 항목을 포함합니다:

```
# [주제]

저장일: YYYY-MM-DD
검증 출처:
- [출처1]: [URL]
- [출처2]: [URL]

검증자: NotebookLM
신뢰도: 높음/중간/낮음

## 내용
[검증된 내용]

## 출처 평가
[각 출처에 대한 평가]
```

---

## 규칙 3: 신뢰도가 중요한 작업

아래 작업에는 반드시 환각 방지 워크플로우를 적용합니다:

| 작업 | 이유 |
|------|------|
| 주식 분석, 투자 판단 | 허위 정보로 금전적 손실 |
| 사실 확인이 필요한 답변 | 환각으로 인한 잘못된 판단 |
| 외부 서비스 연동 정보 | API 변경, 정책 변경 반영 |
| 사람/사건/날짜 관련 | 정확한 사실 확인 필수 |

---

## 규칙 4: Wiki 질의 우선순위

새로운 질의에 응답할 때:

1. **Wiki에서 먼저 확인** — 검증된 지식优先
2. **없으면 web_search** → NotebookLM 검증 → Wiki 추가
3. **검증 실패 시** — "확인되지 않은 내용입니다" 명시

---

## 환각 방지 워크플로우 요약

```
모르는 내용 발견
  → web_search 검색
    → 소스 확보
      → NotebookLM 검증 요청
        → 통과: Wiki 저장
        → 실패: 폐기
```

이 규칙은 환각 방지를 위한 것입니다.
"아는 척"하지 않고, 검증된 내용만 전달합니다.

---

## 업데이트 로그

- 2026-04-28: 최초 작성 — 환각 방지 워크플로우 2차 검증 파이프라인 도입

<!-- gctree:codex:start -->
# gctree Codex integration snippet

- Treat the active gctree branch as a **gc-branch** when you describe it to users.
- gctree init installs SessionStart and UserPromptSubmit hooks that auto-check gc-tree before work.
- Before starting ANY codebase task — new feature, schema change, bug fix, admin work, or any question about how something works — run `gctree resolve` first. Do not assume you know the domain from code alone. Field names, model names, repo names, and feature names are NOT self-explanatory; always verify workflows and cross-repo relationships via gc-tree before touching code.
- Follow this scope-aware protocol before any grep, file read, or code exploration:
  1. Always run `gctree resolve --query "<task or term>"` first. If matched, use the result directly.
  2. Only if the current repo scope is **included** (not unmapped/excluded): if step 1 found nothing, try broader related queries to check if the concept exists in any doc.
  3. If the concept exists in a doc but was not indexed → propose adding it as an Index Entry to that doc.
  4. If it does not exist anywhere → decide whether a new doc is needed and propose it to the user.
  — If the repo is **unmapped** or **excluded**: do step 1 only; if no match, skip and proceed normally.
- When a UserPromptSubmit hook provides `[gc-tree] USE FIRST`, treat matched docs as mandatory grounding before any tool use.
- Do not ignore matched gc-tree docs and jump straight to grep/Explore. Use the listed docs directly, or open the full doc with `gctree resolve --id <id>` if the summary is not enough.
- Only use tools after the matched docs are clearly insufficient for the task.
- If hooks are unavailable or clearly stale, run `gctree status` and `gctree resolve --query "<task>"` yourself before planning or implementation.
- Use `$gc-onboard` only for an empty gc-branch.
- Use `$gc-update-global-context` when durable context in the active gc-branch should change.
<!-- gctree:codex:end -->

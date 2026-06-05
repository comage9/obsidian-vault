---
name: harness-cross-verify
description: M3 (MiniMax) 메인 + DeepSeek-V4-flash 검증1 + OpenRouter 무료 검증2 보조 교차 검증. 2~3 모델 동시 실행, 불일치 시 3차 자동 호출. 영상 "AI 프렌즈 203회" [01:43:32] 적용. 트리거 cross-verify, 3개 모델, 교차검증, harness cross, M3 검증
allowed-tools: Bash(python:*)
---

# M3 (MiniMax) + DeepSeek-V4-flash + OpenRouter 무료 교차 검증 (보노하우스 1차 적용)

## 🎯 목적 (영상 [01:43:32] 다기종 교차 검증 + 사용자 모델 정책)

**황민호 수석 (AI 프렌즈 203회):**
> "클로드가 작성한 결과물을 오픈AI의 코덱스(Codex) CLI와 연결하여 팩트 체크 및 교차 검증하도록 하네스 지침을 동적으로 수정"

**우리 환경 적용**:
- M3 결과를 **DeepSeek (직접 API)** + **OpenRouter 무료 모델**로 동시 검증
- 단순한 텍스트 응답 비교부터, KPP 조회 결과 같은 구조화 데이터까지
- 불일치 시 → 사용자 알림 + 어느 모델이 더 신뢰할지 가이드

---

## 🤖 모델 정책 (사용자 2026-06-05 최종 확정)

| 순위 | 모델 | API 키 | 비용 | 용도 |
|:----|:----|:----|:----|:----|
| **메인 (1차 결정)** | **M3 (MiniMax)** | `MINIMAX_API_KEY=*** | $0.30/M | 결정/실행 (현재 활성) |
| **교차 1차 (2차 검증)** | **DeepSeek-V4-flash (직접 API)** | `DEEPSEEK_API_KEY=*** | $0.27/M | 1차 검증 (교차) |
| **교차 2차 (3차 검증, 보조)** | **nvidia/nemotron-3-ultra-550b-a55b:free** (OpenRouter 무료) | `OPENROUTER_API_KEY=*** (키: Hermes-Nemotron-CrossVerify) | 무료 | 2차 검증 (느려도 OK, 추후 보완) |
| **비활성** | Gemini (비용) | — | — | — |
| **표기 정책** | "Claude" = "GPT" | (사용자 결정) | — | — |

**핵심**: 메인 = M3 (MiniMax). 검증 = DS-V4-flash (1차) + OpenRouter 무료 (2차, 느려도 OK).

> 🚨 **Pitfall (2026-06-05 사용자 최종 확정)**:
> - 메인 모델 = **M3 (MiniMax)**. config.yaml `model.default: deepseek-v4-flash`는 v4-flash의 base_url로 deepseek API 사용.
> - **교차 1차 (검증) = DeepSeek-V4-flash** (model="deepseek-v4-flash"). 메인 M3와 다른 모델.
> - OpenRouter = **무료 모델 3차 검증 보조 전용** (키: Hermes-Nemotron-CrossVerify). 메인/검증 1차로 사용 X.
> - 3차 호출은 **M3 + DS-V4-flash 불일치 시 또는 명시 시**. 일치 시 skip (시간 절약).
> - "Claude" = "GPT" 표기 (사용자 결정, 6/5).
> - **V3 아님**. "v4-flah" 같은 오타 입력 시 v4-flash로 의도 추론 + 정정 표시.

## 🛠 호출 패턴 (Python 단일 함수)

> **상세 코드 + OpenRouter 346 모델 카탈로그 결과 + 검증 체크리스트**:
> `references/api-patterns.md` 참조 (실제 API 호출 검증, 200 OK 확인됨)

핵심 함수 3개:

```python
# 1) DeepSeek 직접 API (2차 교차 — model="deepseek-v4-flash")
deepseek_query(prompt, model='deepseek-v4-flash', max_tokens=1000, timeout=30)

# 2) OpenRouter API (3차 교차 — nvidia nemotron 무료 모델)
openrouter_query(prompt, model='nvidia/nemotron-3-ultra-550b-a55b:free', max_tokens=1000, timeout=60)

# 3) 교차 검증 메인
cross_verify(prompt, parser=None) -> {main_m3, deepseek_v4_flash, openrouter, agree, ...}
```

> ⚠️ **상세 URL/헤더/환경변수 로드 코드는 reference 파일에 있음**. SKILL.md 본문은 운영 규칙 + 모델 정책 위주.

---

## 📋 사용 시나리오 4가지

### 1. 단순 텍스트 검증 (가벼움)
- "다음 JSON 형식 맞는지 확인": `{"주문번호": "...", "수량": ...}`
- M3(메인) + DeepSeek-V4-flash(검증 1차) 비교
- 일치 → 진행 / 불일치 → OpenRouter 3차 자동 호출 (느려도 OK)

### 2. KPP 조회 결과 검증 (보통)
- `fn_search()` 결과를 M3로 요약 + DS-V4-flash로 동일 데이터 재요약
- 두 모델의 (건수, 호차별 수량, 비고) 비교
- 불일치 시 OpenRouter 3차 자동 호출 → 3차까지 불일치 = 사용자 알림

### 3. 신중한 결정 검증 (무거움)
- EDI 전표 인쇄 전: 인쇄 대상 3개 행의 데이터를 M3 + DS-V4-flash + **OpenRouter 3차 필수**로 추출
- 3개 모델 표가 모두 일치 → 자동 진행
- 1개라도 불일치 → 사용자 확인 필수

### 5. 시스템 아키텍처 분석 교차 검증 (무거움, 2026-06-05 추가)
- 외부 영상/문서의 통찰을 기반으로 현재 시스템 개선점 분석
- M3(메인)가 영상 내용 요약 → 동일 프롬프트를 DS-V4-flash + nemotron에 동시 전달
- 3모델 응답의 일치/불일치 분석 리포트 생성
- **실제 사례**: `references/vf-system-analysis-20260605.md` (VF 출고 바코드 시스템 분석)
  - DS-V4-flash(686자, 한국어) + nemotron(6,000자, 영어) 완전 일치
  - M3 MiniMax 빈 응답 (파싱 이슈)
  - 타임아웃 실측: DS 23.5s, nemotron 91.1s
- 외부 영상/문서의 통찰을 기반으로 현재 시스템 개선점 분석
- M3(메인)가 영상 내용 요약 → 동일 프롬프트를 DS-V4-flash + nemotron에 동시 전달
- 3모델 응답의 일치/불일치 분석 리포트 생성
- 프롬프트 구성 예시:
  ```
  [Video Insight]
  (영상 핵심 메시지 요약)

  [Current System Description]
  (분석 대상 시스템 설명)

  [Question]
  위 통찰을 현재 시스템에 적용 시 개선점을 6개 관점으로 분석:
  1. 하네스 구조
  2. 평가 규율
  3. 부분 자율성
  4. 컨텍스트 엔지니어링
  5. 오케스트레이션
  6. 유지보수성
  ```
- **Pitfall (실측)**: nemotron 한글 처리 안 됨 (mojibake) → **영문 프롬프트 별도 작성 필수**
- **Pitfall (실측)**: M3 MiniMax 응답 파싱 구조 확인 필요 (표준 OpenAI 형식과 다를 수 있음, 2026-06-05 VF 분석 시 빈 content 반환)

### 4. HTML/JS 코드 리뷰 검증 (중간)
- 코드 변경사항을 M3(메인)가 요약 정리 → 프롬프트 구성
- DS-V4-flash(검증 1차)에게 "이 변경사항에 버그가 있는지" 리뷰 요청
- 프롬프트 구성 예시:
  ```
  Review these HTML/JS code changes for bugs:
  ## Changes made:
  1. Feature A: ... (구체적 설명)
  2. Fix B: ...
  ## Issue to verify:
  - 실행 순서 문제 없는가?
  - DOM 참조 시점 문제는 없는가?
  - 특정 조건에서 필터/로직이 올바르게 동작하는가?
  ```
- M3 + DS-V4-flash 일치 → 통과 / 불일치 → nemotron(3차) 리뷰
- 불일치 이유를 변경사항 목록과 함께 사용자에게 리포트
- **실제 사례:** `references/vf-code-review-20260606.md` — HTML/JS 코드 리뷰로 4개 버그 발견 (HIGH 2건, MEDIUM 2건)
- **Pitfall:** DS-V4-flash 간헐적 빈 응답(HTTP 200, content="") — 재시도 또는 M3+nemotron으로 진행

---

## ⚠️ 운영 규칙

1. **메인 = M3 (MiniMax)**: 결정/실행, 항상 사용
2. **검증 1차 = DS-V4-flash**: M3 결과의 1차 교차 검증
3. **검증 2차 = OpenRouter 무료**: M3+DS 불일치 시 자동 호출 (느려도 OK)
4. **불일치 시 = 사용자 알림** (자동 결정 X, 인간 검수)
5. **타임아웃**: M3/DS 30s, OpenRouter 3차 **90s** (실측 91s 소요, 2026-06-05 VF 시스템 분석 시). 기존 60s는 timeout 위험 있음.
6. **rate limit**: OpenRouter 무료 분당 20회
7. **로깅**: `cross_verify()` 호출은 `gateway.log`에 INFO로 기록
8. **3차 호출 시점**:
   - M3+DS 일치 → 3차 skip (시간 절약)
   - M3+DS 불일치 → 3차 자동 호출 (느려도 OK, 보완)
   - 사용자 명시 → 3차 강제 호출
9. **비용 한도**: OpenRouter 사용 시 토큰 비용 누적 모니터링 (월 1회)

---

## 📊 의존성

- **상위**: `meta-harness` (라우팅 결정 후)
- **연동 스킬**: `kpp-pallet-management`, `ls-coupang`, `supplier-hub`
- **API 키**: `DEEPSEEK_API_KEY`, `OPENROUTER_API_KEY`, `MINIMAX_API_KEY` (모두 .env 보유 확인)
- **교차 검증 결과 캐시**: 향후 5분 이내 동일 작업은 캐시 (선택)

---

## 🔄 다음 단계 (Phase 4 예고)

Phase 1(메타 하네스) + Phase 2(교차 검증) 완료 후:
- LS 시드 3개 + Supplier 시드 2개 (Phase 4)
- 교차 검증 대상 자동 확장 (KPP → LS → Supplier)

---

## ⚠️ Pitfalls (이 스킬 적용 시 실수 방지)

1. **모든 명령에 자동 트리거 X:** 단순 응답/등록은 교차 검증 skip. "데이터 정확도가 돈直結"인 경우만 (조회 결과, EDI 인쇄 전). 비용 폭주 방지.
2. **DeepSeek API 키 없으면 1차 검증 스킵:** OpenRouter만 사용 (3차). 절대 mock 응답 X.
3. **불일치 = 자동 결정 X:** 인간 검수. 자동 채택은 M3+DS 일치 시만.
4. **temperature=0.1이지만 비결정적:** 완벽 일치 X, 의미적 일치 확인 필요. parser 단순 비교보다 fuzzy match 권장.
5. **rate limit:** OpenRouter 무료 분당 20회. 대량 작업 시 batch + sleep.
6. **타임아웃 30s + 1회 폴백:** M3/DS 무응답 시 OpenRouter만이라도 응답. 둘 다 실패 → ERROR 반환 + 사용자 알림.
7. **OpenRouter 카탈로그 = 자주 변동:** 2026-06-05 기준 346 모델. 1개월 후 다시 확인. `curl https://openrouter.ai/api/v1/models` 최신 카탈로그 fetch 후 모델 선택.
8. **DeepSeek-V3/abab 6.5s는 OpenRouter에 없음:** DS 자체는 직접 API (`DEEPSEEK_API_KEY`), OpenRouter는 다른 무료 모델 검토용. 혼동 X.
9. **🚨 메인 ≠ OpenRouter:** OpenRouter는 **3차 검증 보조 전용**. 메인(1차)/검증 1차(2차)로 사용 X (2026-06-05 사용자 교정).
10. **🚨 execute_code 자동 차단:** `execute_code` 도구는 사용자 명시 동의 없이 자동 차단됨. dry-run·테스트 코드 실행 전 반드시 사용자 승인 필요.
11. **메모리 1회 실패 시 old_string 길이 단축:** 한 번 매치 실패하면 짧은 unique substring로 재시도. 전체 entry 통째 교체보다 부분 문자열 매칭이 안정적.
12. **🚨 메인=M3 / 검증 1차=DS-V4-flash (2026-06-05 사용자 최종):** 메인은 M3 (MiniMax), 검증 1차는 **DS-V4-flash** (model="deepseek-v4-flash"). **V3 아님**. V3로 잘못 표기 시 즉시 정정.
13. **🚨 사용자 입력 오타 → 의도 추론 + 정정 표시:** "v4-flah" = "v4-flash". 정정 결과를 명시적으로 보여주며 진행. 추측만 하고 silently 진행 X.
14. **🚨 sibling subagent 동시 편집 충동:** patch 도구 경고 "modified by sibling subagent" 시 read_file로 최신 상태 재확인 후 패치. v0.3 entry 중복 사례 (2026-06-05).
15. **🚨 const 변수 TDZ (Temporal Dead Zone):** DOMContentLoaded 콜백 내에서 const 변수 선언보다 먼저 초기화 함수 호출 시, 해당 함수가 const 변수 접근 시 ReferenceError 발생. 증상: 일부 기능(총 수량 표시) 동작하나 크리티컬 함수(렌더링) 실행 안 됨. 해결: 모든 DOM const 선언을 최상단, 초기화 호출보다 먼저 배치.
16. **Windows .env 경로:** ~/.hermes/.env 없음. 실제 = C:\\Users\\<user>\\AppData\\Local\\hermes\\.env. 키 로드 시 이 경로 사용.
17. **🚨 MiniMax M3 응답 불안정 (실측):** HTTP 200(0.9s) 응답했으나 `choices[0].message.content` 빈 문자열. `response.reply`/`response.content` fallback 필수. M3 실패 시 DS 결과를 메인으로 사용.
18. **🚨 DS-V4-flash 간헐적 빈 응답 (2026-06-06 실측):** HTTP 200 정상 응답하나 `content`가 빈 문자열인 경우 있음. 동일 프롬프트 재시도(2회) 시 정상 응답하는 경우 있음. 긴 프롬프트(2000+ tokens)에서 특히 불안정. 2회 실패 시 nemotron(3차) 결과 우선 신뢰. M3 + nemotron 일치 시 DS 결과 없이 진행 가능.
19. **🚨 nemotron 영문 전용:** 한글 프롬프트 → mojibake. 코드 리뷰 등은 영문 프롬프트 사용.
20. **🚨 VF 코드 리뷰 실측 (2026-06-06):** M3 단독 리뷰로 4개 버그 중 2개 MEDIUM만 발견. nemotron이 HIGH 2개(계산 오류, 시간 체크 범위) 추가 발견. 교차 검증 없이 단일 모델만으로 HIGH 이슈 누락 가능.
21. **🚨 다중 호출 환경 차이 (2026-06-06):** `execute_code` 도구 내 API 호출과 `terminal` 도구 내 Python 호출 간 응답 차이 가능. DS API가 execute_code에선 401, terminal에선 정상 작동 사례 있음. 확정 테스트는 terminal(Python)으로 할 것.

    업데이트 로그:
    - 2026-06-05 v0.1: ...
    - 2026-06-05 v0.6: ...
    - 2026-06-05 v0.7: nemotron 타임아웃 실측 91s → 90s로 조정. MiniMax M3 응답 파싱 Pitfall 추가.
    - 2026-06-05 v0.3: 모델 정책 확정 (메인=M3, 검증1=DS-V4-flash, 검증2=OpenRouter 무료), SKILL.md 본문 호출 패턴을 references로 분리, Pitfalls 9~11 추가
    - 2026-06-05 v0.4: 사용자 1차·2차 모델 교정 (메인=M3 명시, 2차=V3→V4-flash), Pitfall 섹션 + 운영 규칙 + 시나리오 + 호출 패턴 모델명 일치 정정
    - 2026-06-05 v0.5: 3차 검증 모델 확정 (nvidia/nemotron-3-ultra-550b-a55b:free), **OpenRouter 키 비표준 형식 발견 (재발급 필요)** — `90e20eebca...` 시작, `sk-or-v1-` 형식 아님 → HTTP 401. 해결: https://openrouter.ai/keys 에서 `sk-or-v1-...` 형식 새 키 생성 후 `.env` 교체 + Gateway 재시작.
    - 2026-06-05 v0.5: **사용자 STOP 신호 학습 → Pitfall 12·13·14 추가** (V3 아님 강조, 사용자 오타 의도 추론, sibling subagent 충돌). meta-harness SKILL.md 모델 표기 동시 정정.
    - 2026-06-05 v0.6: HTML/JS 코드 리뷰 시나리오(Scenario 4) 추가. Pitfall 15(const TDZ 초기화 순서), Pitfall 16(Windows .env 경로) 추가.
    - 2026-06-06 v0.8: VF 코드 리뷰 실측 사례 추가(Pitfall 18~20, references/vf-code-review-20260606.md). DS-V4-flash 간헐적 빈 응답 발견. nemotron 영문 전용 재확인.
    - 2026-06-06 v0.9: Pitfalls 섹션 포맷 정리 (중복 번호 제거, 17~21 통일). DS/api 호출 환경 차이 Pitfall #21 추가.
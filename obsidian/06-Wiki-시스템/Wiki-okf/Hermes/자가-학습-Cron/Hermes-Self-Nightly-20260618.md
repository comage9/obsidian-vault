# Hermes Self Nightly — 2026-06-18

**Cron:** Hermes 자가 점검
**실행:** 2026-06-18 (수동 트리거)
**상태:** 변경 있음

---

## 점검 결과 요약

| 항목 | 2026-06-11 | 2026-06-18 | 상태 |
|:-----|:-----------|:-----------|:----:|
| hermes-agent SKILL.md | v2.3.0 (62,577 B) | v2.3.0 | ✅ 동일 |
| mandatory-verification SKILL.md | 2026-06-10 갱신 | 동일 | ✅ 동일 |
| skills_list() | 102개 | 103개 | ⚠️ +1 (신규 스킬) |
| MEMORY.md | 3,432 chars (156%) | 3,315 chars (150.7%) | ⚠️ 여전히 초과 |
| USER.md | 2,000 chars (145%) | 2,519 chars (183.4%) | ❌ 악화 |
| Wiki 페이지 | 96 | 121 | ✅ +25 |
| SOUL.md | 8,957 B (6/11) | 8,957 B (6/11) | ✅ 동일 |
| rules.json | C:\Users\kis\.hermes\rules.json | 동일 | ✅ 존재 |
| log.md | 6/12 06:00 마지막 | 6/12 이후 **미갱신** | ❌ 6일 갭 |
| Self-Nightly cron | 6/11 마지막 실행 | 6/11 이후 **미실행** | ❌ 7일 갭 |

---

## 세부 변경 내역

### 1. USER.md 용량 심각 악화 (2,519 chars / 1,375 = 183.4%)

- **직전 (2026-06-11):** 2,000 chars (145%) — 이미 초과
- **현재 (2026-06-18):** 2,519 chars (183.4%) — **더 악화**
- **내용:** 2026-06-11 추가 교정(반복 재질문 금지, 프린터 명시 강제) + 2026-06-17 MiniMax M3 설정 기록 추가
- **권장:** 긴급 consolidation 필요 — 구 교정/설정을 Wiki 또는 fact_store로 이관

### 2. MEMORY.md 용량 지속 초과 (3,315 chars / 2,200 = 150.7%)

- **직전:** 3,432 chars (156%)
- **현재:** 3,315 chars (150.7%) — 소폭 감소했으나 여전히 제한 초과
- **내용:** 30개 라인, LS 13시 템플릿, Canon G2010 인쇄 명시, KPP 등록순서 등 포함
- **권장:** 절차성 항목 → KPP/LS 스킬 SKILL.md §Pitfalls로 이관

### 3. Self-Nightly cron 7일간 미실행 (2026-06-11 → 2026-06-18)

- **마지막 실행:** 2026-06-11 (본 점검 이전)
- **log.md 마지막 갱신:** 2026-06-12 06:00 (자료섭취 cron)
- **원인 추정:** Hermes Gateway 재시작 또는 모델 변경(cron job enabled=false)으로 인한 cron 스케줄 초기화
- **권장:** `hermes cron list`로 Hermes-Self-Nightly 활성화 상태 확인 필요

### 4. Wiki 페이지 96→121 (+25) — 정상 증가

- 25개 신규 페이지: VF 문서 3건(호차Phase, 데이터파이프라인, 인쇄사고), KPP 인쇄 함정, 거울형 보고서, 의사결정 다수
- Index.md 갱신 필요 확인

### 5. skills_list: 102→103 — 정상

- 1개 신규 스킬 추가 (정확한 식별 불가 — hub 설치 또는 에이전트 생성)

---

## 액션 필요 (Priority 순)

| # | 액션 | 긴급도 | 상세 |
|:--|:-----|:------:|:-----|
| 1 | **USER.md consolidation** | 🔴 HIGH | 2,519→≤1,375 chars. 구 교정/설정 제거 |
| 2 | **MEMORY.md consolidation** | 🔴 HIGH | 3,315→≤2,200 chars. 절차성 항목 이관 |
| 3 | **cron 활성화 확인** | 🟡 MEDIUM | `hermes cron list`로 Self-Nightly enabled 확인 |
| 4 | **log.md 재개** | 🟡 MEDIUM | 6/12 이후 공백 — 본 보고서 추가 |
| 5 | **index.md 갱신** | 🟢 LOW | 25개 신규 페이지 반영 |

---

## 참조

- 이전 보고: `Hermes-Self-Nightly-20260611.md`
- USER.md: `C:\Users\kis\AppData\Local\hermes\memories\USER.md`
- MEMORY.md: `C:\Users\kis\AppData\Local\hermes\memories\MEMORY.md`
- 운영정책: `Wiki/운영원칙/에이전트-운영-정책.md`

# Hermes Self Nightly — 2026-06-11

**Cron:** Hermes 자가 점검
**실행:** 2026-06-11 03:30 KST (또는 수동 트리거)
**상태:** 변경 있음

---

## 점검 결과 요약

| 항목 | 이전 (2026-06-09) | 현재 (2026-06-11) | 상태 |
|:-----|:-----------------|:-----------------|:----:|
| hermes-agent SKILL.md | v2.3.0 (62,577 B) | v2.3.0 (62,577 B) | ✅ 동일 |
| mandatory-verification SKILL.md | 2026-06-08 버전 | 2026-06-10 갱신 (62,946 B) | ⚠️ 갱신됨 |
| skills_list() | 102개 | 102개 | ✅ 동일 |
| MEMORY.md | 2,197/2,200 chars | 3,432 chars → **초과** | ❌ 용량 초과 |
| USER.md | 1,087/1,375 chars | 2,000 chars → **초과** | ❌ 용량 초과 |
| Wiki 페이지 | ~90 | 96 | ✅ 증가 |
| Memory Provider | Holographic (SQLite) | Holographic-Pg (PostgreSQL) | ✅ 마이그레이션 완료 |
| 운영정책.md 최종수정 | 2026-06-09 | 2026-06-11 (본 세션) | ✅ 갱신됨 |

---

## 세부 변경 내역

### 1. mandatory-verification SKILL.md 갱신 (2026-06-10)

2026-06-10 대규모 개편 — 다음 섹션 신설:
- **§00 사전 검증 3종**: 스킬 로드 + Wiki 검색 + fact_store 검색 (2026-06-10 곰너이 강제 명령)
- **Step 0b: 작업 디렉토리 확인**: `pwd`/`ls` 직접 확인 의무화 (컨텍스트 컴팩션 불신)
- **Step 3a: 데이터 신선도 3중 검증**: 파일수정일 + API 재조회 + 데이터내 날짜
- **Step 3b: ASK before acting + 문제 발견 시 보고 우선**: 발견=보고, 자동 수정 금지
- **Git 안전 규칙**: `git checkout/reset` 전 `git status` + stash 필수
- **config strict personality + rules.json**: prefill_messages_file JSON 포맷 필수
- **Pitfall: 사용자 "진행해" = 즉시 실행**: 재확인 질문 금지
- **Pitfall: MEMORY.md 80%+ 정기 유지 규칙**: 매 세션 시작 시 용량 확인
- **Pitfall: Holographic fact_store 자동 주입 안 됨**: 명시적 호출 의무화
- **참조 파일 7종 추가**: false-reporting, data-freshness, git-safety, config-behavior, port-convention, prefill-json, memory-restructure

### 2. MEMORY.md 용량 초과 (3,432 chars)

- **제한**: 2,200 chars
- **현재**: 3,432 chars (약 156%)
- **문제**: 2026-06-10 재구조화 이후에도 char limit 초과
- **권장**: consolidation 긴급 필요 — 절차성/규칙성 항목 Wiki 또는 fact_store로 이관

### 3. USER.md 용량 초과 (2,000 chars)

- **제한**: 1,375 chars
- **현재**: 2,000 chars (약 145%)
- **문제**: 최초 발견. 마지막 수정 2026-06-07 이후로 계정 정보가 계속 누적
- **권장**: consolidation 필요 — 오래된 교정/피드백 제거, 핵심 프로필만 유지

### 4. Memory Provider 마이그레이션 완료

- **이전**: Holographic (SQLite, local)
- **현재**: Holographic-Pg (PostgreSQL, `vf2_db.memory.*`) — 2026-06-10 완료
- **참조**: `Wiki/의사결정/Hermes-Persistent-Memory-PostgreSQL-마이그레이션-20260610.md`

---

## 액션 필요

1. **MEMORY.md consolidation** — 3,432→≤2,200 chars
2. **USER.md consolidation** — 2,000→≤1,375 chars
3. **운영정책 갱신** — 완료 (본 세션)
4. **기타**: SKILL.md, Wiki 정책, 스킬 카탈로그 — 변경 없음

# 자가 학습 Cron — Hermes Self Nightly 2026-06-09

**Cron ID:** `bf08d649e866`
**점검일:** 2026-06-09 (화)
**마지막 이전 실행:** 2026-06-08 03:30 — "변경 없음"
**사용 모델:** deepseek-v4-flash
**점검 방식:** 문서/스킬 전수 확인 (외부 시스템 접근 ❌)

---

## 변경 감지 내역

### 1. hermes-agent SKILL.md: v2.2.0 → v2.3.0 (2026-06-08)

| 항목 | 이전 (v2.2.0) | 현재 (v2.3.0) |
|------|-------------|-------------|
| 버전 | 2026-06-07 통합 | 2026-06-08 갱신 |
| 메인 섹션 | 18개 | 19개 (Persistent Memory 추가) |
| CLI 명령어 | 변경 없음 | 변경 없음 |
| Memory 내용 | "Pluggable memory" 3줄 mention | **완전한 Persistent Memory 섹션** (8개 provider 비교표, 6단계 자동화, Capacity 관리, Save/Skip 정책, 곰너이 시스템 매핑) |

**상세:** `hermes-agent` §Persistent Memory — 2,200 chars 제한, Frozen Snapshot 패턴, 3개 Memory Tool 액션, Substring Matching, <80% / 80-95% / 95%+ Capacity 임계점, 8개 External Provider (Honcho/OpenViking/Mem0/Hindsight/Holographic/RetainDB/ByteRover/Supermemory), Provider 자동 6단계, 곰너이 시스템 ↔ 공식 표준 매핑.

### 2. mandatory-verification SKILL.md: §0 Tool-First Auto-Recall 신설 (2026-06-08)

| 변경 | 설명 |
|------|------|
| **§0 Tool-First Auto-Recall** | 사용자 지시 수신 즉시 search_files + skills_list + session_search 3종 병렬 호출 강제 |
| **§0 적용 우선순위** | 기존 5단계(Step 1-5)보다 먼저 실행 — Tool-First가 최상위 |
| **Hard Rules 6개** | "예/네" 답변 금지, "이미 로드" 스킵 금지, "간단" 예외 금지, 검색 0건도 보고 의무, 반복 키워드 사전 로드, 핸드오프 ≠ 사실 |
| **Pitfalls 추가** (2026-06-06~08) | 브라우저 세션 보존, 새 스킬 생성 전 중복 확인, 브라우저 봇 감지 CDP fallback, "도구 없다" 금지, 스킬 재로드 생략 금지, Windows 경로 이스케이프, Discord 모델 접두사, MEMORY 용량 90%+ consolidation, 온보딩 가이드 동기화, 데이터 구조 확인 선행 |
| **3중 완료 의무** | Wiki 기록 + README 갱신 + Git push 3종 후 "완료" 보고 |
| **크로스-레퍼런스 검증** | 문서 내 모든 참조(파일/디렉토리/스킬/URL) 실제 존재 확인 |
| **Git state 검증** | `git ls-files`로 Git 추적 상태 확인 |

### 3. MEMORY.md: 13 → 22개 엔트리 (99.85% 포화)

**추가 항목 (모두 2026-06-08):**

| # | 항목 | 내용 |
|---|------|------|
| 1 | 곰너이 교정 (기본으로 진행해) | A/B/C 질문 금지, 즉시 실행 |
| 2 | "지랄/개소리" = 극도 분노 | 시스템 데이터 추측/단정 금지 |
| 3 | "확인하고 말해" 절대규칙 | DB 재조회 후 실제 데이터로 |
| 4 | "확인 안 된다" 4번째 각서 | 개선점 명시 필수 |
| 5 | LS 톤수 정책 | 11T(16)/5T(12) 다운=요금절감 |
| 6 | LS→KPP 5단계 (확정) | §0 → LS조회 → 3중일치 → PBM140MW 사전조회 → fn_newRow+fn_save |
| 7 | LS 일일흐름 | 13:00 등록 → 13:10 텍스트 → 15:30 매칭 → 16:30 인쇄(크론=8c57a12b627d) |
| 8 | 인쇄 명령 (1회만) | 3가지 방식 중복 전송 금지 |
| 9 | AI모델 교체 cron enabled=false | 교체 후 cronjob list 검증 |
| 10 | 웹 검색 가능 | browser_navigate 가능, "검색 도구 없다" 금지 |
| 11 | PBM110MW 절대 규칙 | 수정=setValue, 신규=INSERT, MOD='D' 함정 |
| 12 | Holographic External Provider 활성화 | pip install holographic + hermes config set |
| 13 | wiki-workflow 스킬 신설 | /ingest, /update, /output |
| 14 | PBM140MW 페이지 구조 변경 | iframe→직접페이지, SpreadJS ID ss→grid |
| 15 | KPP MCP 서버 등록 | 4개 도구, E:\coding\skill\KPP\kpp-mcp-server\ |
| 16 | VF 대시보드 | 통합차량DB 138건, Reasonix 코딩 전담 |
| 17 | Reasonix 모델 | flash→v4 교체 완료 |

### 4. 스킬 카탈로그: 94개 (변동 없음)

- **94 skills, 19 categories** — 기준(2026-06-05) 대비 숫자 변동 없음
- KPP MCP 서버 도구 4개 (`kpp_search`, `kpp_set_plt`, `kpp_edi_print`, `kpp_status`) — MEMORY #15에 등록
- `wiki-workflow` 스킬 신설 (2026-06-08) — /ingest/update/output 3-Operation

---

## 정책 레벨 변화 (→ 에이전트-운영-정책.md 반영 필요)

1. **Tool-First Auto-Recall 확정 (최우선 정책):** 모든 작업/크론/질문 전 3종 도구 병렬 호출 강제. 기존 5단계보다 먼저 실행.
2. **3중 완료 의무:** Wiki + README + Git push 3종 후 "완료" 보고. 부분 완료 금지.
3. **MEMORY 99% 포화:** 즉시 consolidation 필요 (80% 임계점 초과). Holographic External Provider 활성화 완료.
4. **AI 모델 교체시 cron 검증:** no_agent 스크립트 cron이 enabled=false 전환 가능. 교체 후 cronjob list 검증 필수.
5. **KPP MCP 우선 사용:** 수동 CDP eval 금지, MCP 도구(kpp_search/set_plt/edi_print/status) 우선.

---

## 검증

| 항목 | 상태 | 증거 |
|------|------|------|
| hermes-agent v2.3.0 확인 | ✅ | skill_view() — 버전 2.3.0, Persistent Memory 섹션 200+줄 |
| mandatory-verification §0 확인 | ✅ | skill_view() — §0 Tool-First Auto-Recall (2026-06-08) |
| MEMORY.md 22개 엔트리 | ✅ | read_file — 22 lines, 3,143 bytes (~2,197/2,200 chars) |
| skills 94개 | ✅ | skills_list() — 19 categories, 94 skills |
| CLI 명령어 변경 | ✅ 없음 | hermes-agent §CLI Reference — 이전과 동일 |

---

## 결론

**변경 있음** — 2026-06-08 03:30 마지막 cron 실행 이후 hermes-agent v2.3.0 (Persistent Memory), mandatory-verification §0 Tool-First Auto-Recall, MEMORY 22개 엔트리로 갱신됨. SKILL.md는 이미 최신 상태. 에이전트-운영-정책.md 신규 작성 필요.

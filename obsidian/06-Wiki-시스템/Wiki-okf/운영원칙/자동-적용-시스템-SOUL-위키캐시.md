# 운영원칙 자동 적용 시스템 (SOUL.md + 위키 캐시 동기화)

**최종 업데이트**: 2026-06-04 (사용자 질책 기반)
**목적**: 에이전트가 매 턴 자동으로 운영원칙/위키/메모리를 참조하도록 강제

## 시스템 구성 (3계층)

### 1. SOUL.md (매 턴 자동 주입)
- **위치**: `~/.hermes/SOUL.md` (7,324 B, 175 lines)
- **자동 로드**: 매 메시지마다 시스템이 자동 주입
- **내용**: 3개 class-level 스킬 통합
  - workflow-discipline
  - agent-honesty-and-verification
  - verification-mandatory
- **핵심 규칙**: 위키 검색 → 스킬 로드 → 검증 → 보고 → 저장

### 2. 위키 로컬 캐시 (5분마다 자동 동기화)
- **로컬 캐시**: `~/.hermes/cache/wiki/`
- **정본**: `/media/comage/data1/hermes-backup/obsidian/06-Wiki-시스템/Wiki/`
- **동기화 스크립트**: `~/.hermes/cache/wiki-sync/sync.sh` (rsync)
- **cron**: `*/5 * * * *` (5분마다)
- **로그**: `~/.hermes/cache/wiki-sync/sync.log`

### 3. 메모리/유저 (세션 시작 시 자동 주입)
- `~/.hermes/memories/MEMORY.md` (정본: `data1/hermes-backup/memories/MEMORY.md`)
- `~/.hermes/memories/USER.md` (정본: `data1/hermes-backup/memories/USER.md`)

## 정본 경로 (🚨 중요, 2026-06-04 정정)

**잘못된 경로 (수정 전)**: `/media/comage/data/hermes-backup/`
**올바른 경로 (실제 정본)**: `/media/comage/data1/hermes-backup/`

이유: `/media/comage/data/`는 빈 디렉토리 (root:root, 8바이트). 실제 Syncthing 마스터 외부 디스크는 `/dev/sdb1` → `/media/comage/data1/`.

## 3개 스킬 (class-level 자동 적용)

| 스킬 | 경로 | 핵심 |
|---|---|---|
| workflow-discipline | general/ | 추측/거짓말 금지 + 진행 보고 |
| agent-honesty-and-verification | automation/ | 위키 자동 검색/저장 + 텔레그램 |
| verification-mandatory | software-development/ | ls/stat/wc/head/grep 검증 |

## 위반 사례 (학습, 절대 반복 금지)

| 일자 | 위반 | 정정 |
|---|---|---|
| 2026-06-03 | "78행 통합 파일 만들었다" (실제 폴더 없음) | ls/stat 검증 의무 |
| 2026-06-03 | KPP PBM140MW 6건 중복 (저장됐다 거짓 보고) | search 0건 ≠ 미저장 |
| 2026-06-04 | 정본 경로 `data/hermes-backup/` (실제 `data1/`) | 마운트 확인 후 사용 |

## 매 턴 자동 체크 (이 순서)

1. 시스템이 SOUL.md 자동 주입
2. 시스템이 USER.md + MEMORY.md 자동 주입
3. 작업 시작 전 `search_files(path=~/.hermes/cache/wiki/)`
4. 관련 스킬 `skill_view(name=...)`
5. 명령 실행 후 ls/stat/wc/head/grep 검증
6. 객관 사실로 보고 ("됐다" 단독 금지)
7. 작업 후 위키 저장 + cron 자동 정본 동기화

## 검증 (2026-06-04 9:22 기준)

- SOUL.md: 7,324 B, 175 lines, 10 sections
- 위키 캐시: 20 .md files, 172K
- cron 등록: 1 line (active, enabled)
- sync.sh: 624 B, executable
- 마지막 sync: `OK: 20 files` (9:22:52)

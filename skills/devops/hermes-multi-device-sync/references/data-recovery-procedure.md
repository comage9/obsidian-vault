# Syncthing 데이터 소실 복구 절차

## 참조: 2026-05-31 실제 사례

- 손실: 스킬 600MB+ (25개 스킬 제외 전소), 메모리 14MB (MEMORY.md/USER.md 제외 전소), 위키 500MB+ 완전 소실
- 원인: Windows(NTFS)에서 `.stfolder` 수동 생성 + 재탐색으로 Syncthing이 빈 폴더를 기준으로 Linux 마스터 데이터 삭제
- 교훈: `hermes-multi-device-sync` 스킬의 `sendonly`/`receiveonly` 규칙 참조

## 복구 가능성 체크리스트

| 항목 | 회복 가능성 | 방법 |
|:----|:----------:|:----|
| 내장 스킬 (hermes-agent/skills/) | ✅ | git 원본 보존, `hermes skills list`로 확인 |
| 사용자 생성 스킬 | ❌ | 재작성 필요 |
| MEMORY.md / USER.md | ✅ | Hermes 세션에서 자동 재생성 |
| 기타 메모리 데이터 | ⚠️ | 세션 DB에서 부분 복구 가능 |
| Obsidian Wiki | ✅ | 자동 Git Push 크론(Cron)이 실행 중이면 GitHub에서 복구 가능 |
| 오늘 작성 문서 | ⚠️ | 이전 세션 검색(`session_search`)으로 내용 추출 가능 |

## 복구 절차

### 1. 우선: 활성 크론잡에서 Git 백업 확인

```bash
# 크론잡 조회
cronjob list

# "Wiki Git Auto-Sync" 또는 유사 이름의 job 확인
# - workdir: 동기화된 저장소 경로
# - last_run_at: 마지막 성공 시각 (데이터 유실 이전이면 복구 가능)
# - last_status: "ok"여야 함
# - script: 스크립트 경로 (예: .scripts/wiki-git-push.sh)
```

### 2. GitHub/원격 저장소에서 위키 복구 (2026-05-31 검증 완료)

**실제 복구 사례:** 크론 `Wiki Git Auto-Sync` (6시간 간격) — 마지막 실행 18:01, 데이터 소실 직전 `last_status: ok`. GitHub에 최신 데이터 보존 확인됨. session_search로 `github.com/comage9/obsidian-vault.git` 원격 URL 확인 후 `/home/comtop/workspace/Wiki/`에서 git fetch → pull → cp로 복구.

**복구 가능 범위:** `06-Wiki-시스템/Wiki/의사결정/`, `개념/`, `문제-해결/` ✅  
**복구 불가:** `~/obsidian-vault/의사결정/` 루트 레벨, `~/obsidian-vault/Wiki/`, `~/obsidian-vault/01-VF-프로젝트/` 등

**원격 URL 찾는법 (workdir .git/config 삭제된 경우):**
1. `session_search("github.com/comage9/obsidian-vault")`
2. `session_search("wiki git remote url")`
3. `find /home/comtop/ -name ".git" -type d | xargs -I{} grep -l "obsidian-vault" {}/config 2>/dev/null`

```bash
# 1. 작업용 디렉토리 생성
mkdir -p /home/comtop/workspace/Wiki && cd /home/comtop/workspace/Wiki

# 2. 원격 저장소 clone
#    (기존 git remote URL은 크론 작업의 workdir/.git/config에 보존됨
#     또는 session_search로 복구 가능)
git clone <remote-url> .

# 3. 최신 상태로 pull
git pull origin main

# 4. 필요한 디렉토리를 복원할 위치로 복사
cp -a 06-Wiki-시스템 /home/comtop/obsidian-vault/
```

**원격 URL 찾는 법:**
- `cronjob list` → workdir 경로 확인 (예: `/home/comtop/obsidian-vault/06-Wiki-시스템`)
- 해당 경로에 `.git/config` 보존 여부 확인
- 또는 `session_search("wiki git remote origin")` 으로 URL 확인
- 또는 `session_search("github.com/comage9/obsidian-vault")` 로 직접 GitHub URL 조회
- 또는 `find /home/comtop/ -name ".git" -type d | xargs -I{} grep -l "obsidian-vault" {}/config 2>/dev/null` 로 남아있는 git 저장소에서 URL 추출

### 3. Skills 복구

```bash
# built-in 스킬은 hermes-agent git repo에 보존되어 있음
# 자동으로 로드됨 — 확인만 하면 됨
hermes skills list

# git에서 유실된 스킬 복원 (별도 관리 스킬이면)
# cd /opt/hermes/hermes-agent && git checkout -- skills/
```

### 4. 세션 DB에서 추출 (메모리 대체용)

```bash
# 세션 DB 경로 (Linux)
find ~/.hermes/sessions/ -name "*.db" -size +100k | head -5
# Hermes가 자동으로 MEMORY.md/USER.md 재생성
```

### 5. 위키 문서 재생성 (Git으로 복구 불가한 경우)

이전 세션 검색으로 재구성:
```bash
# session_search("의사결정", limit=5)
```

## 예방

1. 항상 `sendonly` + `receiveonly` 조합 사용
2. 동기화 전 `.stignore` 설정
3. 매일 백업 확인 (`cronjob list` → hermes-full-backup 상태 확인)
4. Windows에는 절대 `.stfolder` 수동 생성 금지
5. **위키 Git 자동 백업 크론이 활성화되어 있는지 주기적 확인** (6시간 간격 권장)
6. Git remote URL을 메모리에 저장해두거나 config에서 쉽게 찾을 수 있게 유지

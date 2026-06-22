---
name: hermes-multi-device-sync
description: Hermes Agent 멀티기기 공유 설정 — Syncthing P2P 동기화로 스킬/메모리/위키 3방향 공유
---

# Hermes 멀티기기 공유 설정

## 🚨 🚨 🚨 중요: 데이터 유실 방지 — 반드시 먼저 읽을 것 🚨 🚨 🚨

**이 스킬의 모든 조작 전에 아래 경고를 반드시 숙지할 것. 실수로 마스터 데이터가 전소된 실제 사례가 있음 (2026-05-31, 1GB+ 소실).**

### 절대 `sendreceive`(양방향)를 기본값으로 사용하지 말 것

Syncthing의 기본 폴더 타입은 `sendreceive`(양방향 동기화)다.  
**데이터가 있는 마스터(master) 기기에서는 절대 `sendreceive`를 사용하지 말고 `sendonly`를 사용할 것.**

**이유:** Windows(NTFS, 대소문자 미구분)와 Linux(ext4, 대소문자 구분) 간 근본적 차이로 인해 폴더 마커(`.stfolder`) 누락 시 Syncthing이 "potential data loss"로 판단하고, 재탐색 후 빈 폴더(Windows)를 기준으로 마스터 데이터를 전부 삭제함.

**절대 규칙:**
1. 데이터가 있는 기기(Linux 서버)는 **`sendonly`**(송신 전용)로 설정
2. 데이터를 받는 기기(Windows)는 **`receiveonly`**(수신 전용)로 설정
3. 양방향이 필요한 경우에만 `sendreceive`로 변경하되, **반드시 백업 후 진행**
4. Linux ↔ Linux 간 동기화는 `sendreceive` 안전함 (둘 다 ext4, 대소문자 구분)

### `.stfolder` 마커 관련 절대 규칙

- `.stfolder`가 없는 쪽에서 이 파일을 **수동으로 생성하지 말 것**
- Windows에서 "folder marker missing" 오류 발생 시 대신 Syncthing Web UI → 폴더 **편집(Edit)** → 경로 재선택 → 저장 (Syncthing이 자동 생성)
- **절대:** Windows(빈 폴더)에 `.stfolder` 수동 생성 + 재탐색 → Linux 데이터 전소 위험

### 동기화 전 필수: `.stignore` 설정

폴더를 Syncthing에 추가하기 **전에** `.stignore` 파일부터 작성하라.  
이미 동기화가 시작된 후에는 `.stignore` 추가만으로 과거 전송된 파일을 되돌릴 수 없음.

```bash
# 각 공유 폴더 루트에 .stignore 생성 (동기화 전 필수)
cat > /opt/hermes/skills/.stignore << 'EOF'
backup/
goclaw_backup/
hermes-portable/
hermes-backups/
node_modules/
.venv/
venv/
__pycache__/
*.pyc
.DS_Store
.git/
.syncthing.*.lock.tmp
EOF

cat > /opt/hermes/memories/.stignore << 'EOF'
backup/
*.bak
*.bak.*
.syncthing.*.lock.tmp
EOF

cat > ~/obsidian-vault/.stignore << 'EOF'
backup/
.DS_Store
.syncthing.*.lock.tmp
EOF

systemctl --user restart syncthing
```

### 동기화 전 반드시 전체 백업

```bash
sudo /opt/hermes/scripts/hermes-full-backup.sh
# 또는 수동 tar
tar czf /tmp/hermes-skills-backup-$(date +%Y%m%d).tar.gz /opt/hermes/skills/
tar czf /tmp/hermes-memories-backup-$(date +%Y%m%d).tar.gz /opt/hermes/memories/
tar czf /tmp/hermes-obsidian-backup-$(date +%Y%m%d).tar.gz ~/obsidian-vault/
```

**절대 마스터 데이터를 백업 없이 양방향 동기화에 노출하지 말 것.**

## 개요

Hermes Agent가 3대 기기(노트북 Linux, 데스크탑 Windows, 데스크탑 Linux)에서 실행 중이며, 스킬/메모리/위키를 공유하기 위한 Syncthing 설정.

## 트리거

사용자가 "공유 폴더", "공유 주소", "멀티기기", "동기화" 관련 이야기를 꺼내면 로드.

## 공유 데이터 구조

| 공유 폴더 | 경로 | 용도 |
|:---------|:-----|:-----|
| **skills/** | `/opt/hermes/skills/` | 스킬 파일 (SKILL.md) |
| **memories/** | `/opt/hermes/memories/` | MEMORY.md + USER.md |
| **obsidian/** | `/home/comtop/obsidian-vault/` 또는 Wiki | 위키 + 지식베이스 |

## 비공유 데이터

- Config.yaml — 기기별 경로/설정 다름
- .env — 기기별 API 키 다름
- sessions/ — 기기별 대화 내역

## Syncthing 설치

### Linux (Ubuntu/Debian)
```bash
sudo apt install syncthing
systemctl --user enable syncthing
systemctl --user start syncthing
# 웹 UI: http://localhost:8384
```

### Windows
1. https://syncthing.net/downloads/ 다운로드
2. 설치 및 실행
3. 웹 UI: http://localhost:8384

## 노트북 Linux 서버 정보 (2026-05-31 설치 완료)

- **Syncthing v1.29.2** — systemd user service로 자동 실행
- **Device ID:** `TOXSUKK-4PWF4T5-BGKYUEJ-4GH6MU4-EYWE4M5-ADRXYOA-47G6B5J-ZG3XHAI`
- **Web UI:** http://localhost:8384
- **API Key:** `dpEQySib5kgqcqKifz35SasLittyy66Y`
- **상태 확인:** `systemctl --user status syncthing`

### 참여 기기 (2026-05-31 기준)

| 기기 | OS | Device ID | Syncthing 버전 | IP |
|:----|:--|:---------|:--------------|:--|
| **노트북 Hermes (서버)** | Linux (Laptop) | `TOXSUKK-4PWF4T5-BGKYUEJ-4GH6MU4-EYWE4M5-ADRXYOA-47G6B5J-ZG3XHAI` | v1.29.2 | 로컬 |
| **DESKTOP-B12F6DJ** | Windows | `WYURB73-4EPDAGD-LMJRLCO-NLW55O4-LL2Q5YL-IHQIIYD-SH3DTNA-JO3QDQV` | v2.1.0 | 172.30.1.67 |

## 시스템 서비스

```bash
# 상태 확인
systemctl --user status syncthing

# 재시작
systemctl --user restart syncthing

# 로그 확인
journalctl --user -u syncthing --since "5 min ago" --no-pager
```

## 연결 설정 순서 (신규 기기 추가 시)

### 1. 상대방 Device ID 확인
Syncthing 웹 UI → 우측 하단 ⊕ 메뉴 → "Show ID" → Device ID 복사

### 2. Device 추가
웹 UI → **"Add Remote Device"** → Device ID 붙여넣기 → 저장

### 3. 폴더 추가
웹 UI → **"Add Folder"** → 아래 표대로 입력

### 4. 연결 확인
로그에서 확인:
```
Established secure connection to {DEVICE_ID} at {IP}:22000/tcp-server/TLS1.3-...
```

## 공유 폴더 명세

| 폴더 ID | 로컬 경로 | 내용 |
|:-------|:---------|:-----|
| `hermes-skills` | `/opt/hermes/skills/` | 스킬 파일 |
| `hermes-memories` | `/opt/hermes/memories/` | MEMORY.md + USER.md |
| `hermes-obsidian` | `/home/comtop/obsidian-vault/` | 위키/지식베이스 |

## ⚠️ 필수 사전 점검: 공유 폴더 정리

Syncthing 연결 전, 공유 폴더에서 불필요한 대용량 파일을 먼저 제거해야 함.
백업 디렉토리(`backup/`, `goclaw_backup/`, `hermes-portable/`, `hermes-backups/`)는
스킬/메모리와 무관하며 600MB+씩 차지하여 동기화를 막고 연결 타임아웃을 유발함.

### 추가 점검: 폴더 간 교차 오염

각 공유 폴더가 **자기 자신의 내용만** 포함하는지 확인할 것. 예시:
- 메모리 폴더에 위키 백업 → `/opt/hermes/memories/backup/obsidian-vault/` (교차 오염)
- 스킬 폴더에 위키 백업 → `/opt/hermes/skills/backup/obsidian-vault/` (교차 오염)

**해결:** 해당 `backup/obsidian-vault/`를 삭제하고 재동기화.

### 필수: `.stignore`에 `backup/` 패턴 추가 (동기화 전 최우선)

`backup/` 안에는 `node_modules/`, `.venv/`, `__pycache__/` 같이 Linux `.stignore` 조건에 걸리는
파일들이 포함되어 있습니다. 동기화 시작 후 Linux에서 `backup/`을 삭제하면,
Windows가 이미 무시되지 않은 파일들을 수신한 상태라 "Failed to delete directory... not empty"
오류가 쌓이고 폴더가 **"중지됨"** 상태가 됩니다.

**예방법 — 폴더 생성 직후 `.stignore` 설정:**

```bash
echo "backup/" > /opt/hermes/skills/.stignore
echo "backup/" > /opt/hermes/memories/.stignore
echo "backup/" >> ~/obsidian-vault/.stignore   # append, 기존 ignore 유지
systemctl --user restart syncthing
```

이렇게 하면 Windows가 `backup/`을 아예 받지 않으므로, Linux에서 삭제해도 충돌 없음.

### 정리 명령어
```bash
# skills/backup (코딩 프로젝트 .venv, node_modules 등) — 전부 제거
find /opt/hermes/skills/backup -type f -delete 2>/dev/null
find /opt/hermes/skills/backup -depth -type d -delete 2>/dev/null

# memories backup 파일들
rm -f /opt/hermes/memories/MEMORY.md.bak.*

# obsidian 불필요 디렉토리
find /home/comtop/obsidian-vault/backup -type f -delete 2>/dev/null
find /home/comtop/obsidian-vault/backup -depth -type d -delete 2>/dev/null

# 최종 용량 확인
du -sh /opt/hermes/skills/ /opt/hermes/memories/ /home/comtop/obsidian-vault/
```

### 정상 용량 기준
| 폴더 | 정상 | 문제 (정리 전) |
|:----|:----:|:-------------:|
| skills/ | ~70MB | 600MB+ (backup/) |
| memories/ | ~30MB | 600MB+ (backup/) |
| obsidian/ | ~550MB | 1.2GB+ (backup/) |

## 동기화 설정 순서 (Windows/Linux 데스크탑)

1. 각 기기에서 Syncthing 웹 UI 접속
2. 우측 하단 "Device ID" 확인
3. 기기 간 Device ID 추가 (Add Device)
4. 공유 폴더 추가 (Add Folder):
   - skills/ → Folder ID: `hermes-skills`
   - memories/ → Folder ID: `hermes-memories`
   - obsidian/ → Folder ID: `hermes-obsidian`
5. 각 폴더에 공유할 기기 선택
6. 동기화 상태 확인 (초록 체크)

## 연결 문제 해결

### 증상: "중지됨" (Paused) — 폴더가 멈춤, 오류 로그에 "Failed to delete directory... not empty"

**로그 예시:**
```
WRN Failed to sync ... directory has been deleted on a remote device but is not empty;
the contents are probably ignored on that remote device, but not locally
```

**원인:** Linux에서 `backup/`을 삭제했지만, Windows는 이미 그 안의 파일(npm 패키지, venv 등)을
받아놓은 상태. Linux 쪽 `.stignore`로 무시된 파일들이 Windows에는 존재하기 때문에
Syncthing이 디렉토리를 비울 수 없어서 동기화가 중단됨.

**해결 순서 (Windows):**
1. Windows 탐색기 열기 → 각 폴더 경로에서 `backup` 폴더를 **수동으로 완전 삭제**
   - `E:\hermes-backup\skills\backup\`
   - `E:\hermes-backup\obsidian\backup\`
   - `E:\hermes-backup\memories\backup\`
2. Syncthing 웹 UI → 각 폴더의 **▶ (재개/Resume) 버튼** 클릭 (3개 모두)
3. **"모두 재탐색"** 버튼 클릭
4. 확인: 폴더 상태가 "동기화 미완료" → 진행률 표시로 바뀌는지 확인

**예방:** `.stignore`에 `backup/` 패턴을 추가한 후에만 동기화 시작 (위 `필수 사전 점검` 참조).

### 증상: 대소문자 충돌 ("uses different upper or lowercase characters")

**로그 예시:**
```
WRN Failed to sync ... remote "backup\obsidian-vault\wiki" uses different upper or lowercase characters than local "backup\obsidian-vault\Wiki"
```

**원인:** Linux(ext4)는 대소문자 구분, Windows(NTFS)는 대소문자 무시. Syncthing이 Linux 측에서 `wiki`(소문자)와 `Wiki`(대문자)를 별도 폴더로 인식하지만, Windows에서는 같은 폴더로 보아 충돌 발생. 전체 동기화가 중단됨.

**해결 (Linux 측에서 실행):**
```bash
# 1. 대소문자 중복 폴더 찾기
find /home/comtop/obsidian-vault/ -maxdepth 3 -type d | sort | uniq -i -d

# 2. 소문자 버전의 내용을 대문자 버전으로 병합 (내용 확인 후)
mv ~/obsidian-vault/wiki/sources ~/obsidian-vault/Wiki/sources  # 예시
rm -rf ~/obsidian-vault/wiki  # 소문자 폴더 삭제

# 3. backup/ 디렉토리 (구 백업 데이터)가 있으면 삭제 — 중복 케이스의 주요 원인
rm -rf ~/obsidian-vault/backup/
```

**예방:** 폴더명 첫 글자 대소문자 일관성 유지. Obsidian 볼트는 일반적으로 `Wiki`(대문자 W) 사용 권장. Linux에서 `mkdir Wiki` 와 `mkdir wiki`를 실수로 만드는 경우가 많으니 주의.

**Windows에서 해결 후 조치:**
Syncthing 웹 UI → "모두 재탐색" 버튼 클릭 → 동기화 재개 확인

### 증상: 상대 기기 연결됨 → 끊김 반복 ("i/o timeout", "protocol error")

**원인:** 상대방이 삭제한 파일을 반대쪽에서 요청 → 파일 없음 → 연결 끊김 (backup 정리 후 발생)

**해결:**
1. `⚠️ 필수 사전 점검` 섹션의 정리 스크립트로 불필요 파일 제거
2. `systemctl --user restart syncthing` (Linux) / Syncthing 재시작 (Windows)
3. Windows Syncthing 웹 UI에서 각 폴더의 **Scan** 버튼 클릭
4. 그래도 안 되면 각 폴더 클릭 → **"Override Changes"** (Windows 로컬 파일을 서버 기준으로 맞춤)

### 증상: "unknown device" rejected

**원인:** 한쪽에서만 상대방을 추가하고 다른쪽에서 승인 안 함

**해결:** 상대방 Device ID를 config.xml에 직접 추가 후 Syncthing 재시작, 또는 웹 UI에서 수락

### 연결 확인 명령어
```bash
journalctl --user -u syncthing --since "5 min ago" --no-pager | grep -E "established|error|closed"
```

## Windows Hermes 설정 가이드

Windows Hermes가 공유 폴더를 사용하려면 심볼릭 링크 또는 Juncture 필요.
자세한 내용은 위키 문서 참조:

`Wiki/의사결정/윈도우-헤르메스-공유폴더-설정가이드.md`

핵심 명령어 (Windows 관리자 PowerShell):
```powershell
# 기존 폴더 백업 후 Syncthing 폴더로 Juncture 연결
Rename-Item "$env:USERPROFILE\.hermes\skills" "$env:USERPROFILE\.hermes\skills_backup"
New-Item -Path "$env:USERPROFILE\.hermes\skills" -ItemType Junction -Target "C:\...\hermes-skills"
New-Item -Path "$env:USERPROFILE\.hermes\memories" -ItemType Junction -Target "C:\...\hermes-memories"
```

**비공유:** config.yaml, .env, sessions/ (각 기기별 유지)

### 증상: \\"folder marker missing\\" (폴더 마커 없음) — 초기 스캔 실패

**로그 예시:**
```
ERR Failed initial scan ... error=\"folder marker missing (this indicates potential data loss)\"
WRN Folder is in error state ... error=\"folder marker missing\"
```

**🚨 절대 Windows(수신 측)에서 `.stfolder`를 수동 생성하지 말 것!**

이 오류는 **"potential data loss"** (데이터 소실 가능성)을 의미하는 심각한 경고다.
`.stfolder` 마커가 없는 쪽이 어떤 이유로 데이터를 잃었는지 Syncthing이 알 수 없기 때문에 발생한다.
이 상태에서 `.stfolder`를 수동 생성 + 재탐색하면 Syncthing이 마커가 없는 쪽(Windows, 빈 폴더)을
"올바른 버전"으로 판단하여 반대쪽(Linux, 실제 데이터)을 전부 삭제할 수 있다.

**안전한 해결 순서:**

1. Syncthing 웹 UI → 해당 폴더 **편집(Edit)** → 경로 동일하게 재선택 → **저장**  
   (Syncthing이 자동으로 `.stfolder` 생성)
2. 또는 아무 조치 없이 Linux 쪽에서 **"모두 재탐색"** 만 실행
3. **절대 하지 말 것:** Windows 탐색기에서 `.stfolder` 수동 생성 + 재탐색
4. **절대 하지 말 것:** "Override Changes" 버튼 클릭

**폴더가 "중지됨" 상태일 때 올바른 해결:**

폴더 옆 ▶ (재개) 버튼 클릭 → Linux 쪽 재탐색 → Windows 재탐색 순서로 진행.
Windows에서 `.stfolder`가 없어서 오류가 계속되면 폴더 설정 편집(Edit)으로 자동 생성.

## Windows Hermes 게이트웨이 문제 해결

### 증상: `hermes gateway restart` 후 "no process detected", 게이트웨이 강제 종료

**로그 예시 (gateway.log):**
```
SystemError: AST constructor recursion depth mismatch (before=120, after=172)
```

**원인:** Python 3.11의 AST(Abstract Syntax Tree) 파서가 깊이 중첩된 `.py` 파일을 파싱할 때 재귀 한도를 초과. `tools/registry.py`가 모든 `tools/` 디렉토리의 파이썬 파일을 `ast.parse()` 하는 과정에서 트리거됨.

**임시 해결 (PowerShell):**
```powershell
$env:PYTHONRECURSIONLIMIT=3000
hermes gateway restart
```

**영구 해결 (Windows `%USERPROFILE%\.hermes\.env`에 추가):**
```env
PYTHONRECURSIONLIMIT=3000
```

또는 시스템 환경 변수로 추가:
```powershell
[System.Environment]::SetEnvironmentVariable('PYTHONRECURSIONLIMIT','3000','User')
```

### 증상: Telegram Bot Token rejected (InvalidToken)

**로그 예시:**
```
ERROR telegram.error.InvalidToken: The token \`8337818987:***\` was rejected by the server.
```

**원인:** Windows Hermes의 `%USERPROFILE%\.hermes\config.yaml` 또는 `.env`에 저장된 Telegram 봇 토큰이 유효하지 않음 (토큰 만료, 봇 삭제, 오타 등).

**해결:**
1. BotFather(@BotFather)에서 새 토큰 발급 또는 기존 토큰 확인
2. Windows `%USERPROFILE%\.hermes\.env`에 `TELEGRAM_BOT_TOKEN=새토큰` 설정
3. `hermes gateway restart`

### 증상: Discord 연결 시간 초과 (connect timed out)

**로그 예시:**
```
ERROR discord connect timed out after 30s
```

**원인:** Windows 방화벽 또는 회사 네트워크 정책이 Discord WebSocket 연결을 차단.

**해결:**
1. Windows 방화벽 → Discord 허용 확인
2. VPN/프록시 환경이면 UDP 차단 가능 — Discord에서는 `discord.com` HTTPS가 우회됨
3. Discord가 불필요하면 config.yaml에서 `platforms.discord.enabled: false`로 비활성화

## 검증

```bash
# 헬스체크 스크립트
python3 /opt/hermes/skills/devops/hermes-multi-device-sync/scripts/health-check.py

# 수동 확인: curl로 API 직접 호출
API_KEY=$(python3 -c "import xml.etree.ElementTree as ET; t=ET.parse('/home/comtop/.config/syncthing/config.xml'); print(t.getroot().find('.//gui/apikey').text)")
curl -s -H "X-API-Key: $API_KEY" http://127.0.0.1:8384/rest/system/connections | python3 -m json.tool

# 한 기기에서 스킬 수정 후 다른 기기에서 동기화 확인
echo "test-$(date)" >> /opt/hermes/skills/test.txt
# → 30초 이내에 자동 동기화됨
```

## 참고 파일

- `references/setup-details.md` — 세션 기록, REST API 사용법, 문제 해결
- `references/case-sensitivity-conflict.md` — Linux↔Windows 대소문자 충돌 해결
- `references/data-recovery-procedure.md` — 데이터 소실 시 복구 절차 (Git 복구 포함)
- `references/user-md-conflict-resolution.md` — USER.md/SOUL.md 0B 파일 충돌 해결 및 교차 플랫폼 동기화 전략
- `references/windows-gateway-ast-error.md` — Windows Hermes Python AST recursive error 해결
- `scripts/health-check.py` — 피어/폴더 동기화 상태 진단 스크립트
- 위키: `Wiki/의사결정/헤르메스-멀티기기-공유-방안-20260531.md`

## 데이터 소실 시 복구 1순위

1. `cronjob list` → `Wiki Git Auto-Sync` 크론의 `last_status` 확인
2. `last_run_at`이 데이터 소실 시점보다 이후이고 status=ok면 GitHub에서 복구 가능
3. `references/data-recovery-procedure.md`의 `복구 절차` 섹션 참조

---
name: goclaw-setup
description: GoClaw AI Agent Gateway 설치, 구성, Telegram 연동 가이드
trigger: GoClaw 설치 요청, GoClaw + Telegram 연동, Hermes 데이터 마운트, 에이전트 성격 파일 편집
---

# goclaw-setup

GoClaw AI Agent Gateway 설치, 구성, Telegram 연동 가이드.

## 설치 (로컬 - Docker 없음)

GoClaw를 Docker 없이 직접 실행할 수 있습니다.

**사전 요구사항:**
- Go 1.26+
- PostgreSQL 18 + pgvector 확장

**1) Go 설치:**
```bash
# https://go.dev/dl/ 에서 최신 버전 확인 후 다운로드
curl -fsSL -o /tmp/go.tar.gz "https://go.dev/dl/go1.26.2.linux-amd64.tar.gz"
sudo tar -C /usr/local -xzf /tmp/go.tar.gz
rm /tmp/go.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc
go version
```

**2) PostgreSQL 18 + pgvector 설치 (Ubuntu 26.04):**
```bash
sudo apt update
sudo apt install -y postgresql-18 postgresql-18-pgvector
sudo systemctl enable --now postgresql
sudo -u postgres psql -c "CREATE USER goclaw WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE goclaw OWNER goclaw;"
sudo -u postgres psql -d goclaw -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**3) GoClaw 소스 빌드 및 실행:**
```bash
# 1. 소스 클론 (바이너리 다운로드와 다른 경로)
git clone https://github.com/nextlevelbuilder/goclaw.git ~/goclaw
cd ~/goclaw

# 2. 빌드 (Go 1.26+ 필요, make 사용)
make build

# 3. 빌드 결과 확인 (바이너리 위치 확인)
ls -lh ~/goclaw/goclaw

# 4. 대화형 온보딩 (DB 마이그레이션 + API 키 생성)
./goclaw onboard

# 4. 일반 실행 (.env.local sourced 상태에서)
source .env.local && ./goclaw
```

**⚠️ 포트 동작 방식 (GoClaw v3.11.3 소스 빌드 기준)**
- **로컬 소스 빌드 실행**: 18790(Dashboard)만 Listen. Gateway WebSocket은 18790에 통합
- **Docker 실행**: 18789(Gateway/WebSocket) + 18790(Dashboard) 두 포트 모두 Listen
- `ss -tlnp | grep -E "18789|18790"` 로 실제 열린 포트 확인
- config.json에서 gateway.port=18789로 설정해도 소스 빌드에서는 18790만 열림 (버그/설계 차이)

**⚠️ 프로세스명 주의: GoClaw는 `openclaw-gateway`로 표시됨**
- `ps aux`에서 `openclaw-gateway`라고 나오지만 **실제로는 GoClaw**입니다
- 이것과 별개로 **OpenClova(NClova/보노하우스)**가 다른 포트에서 실행될 수 있습니다
- **혼동하지 마세요: GoClaw ≠ OpenClova**
- GoClaw 온보딩/실행 중 OpenClova 프로세스가 남아 있으면 먼저 중지해야 합니다

**OpenClova 중지 확인:**
```bash
ps aux | grep -iE "openclova|nclova|auxiliary" | grep -v grep
# 또는 18789 포트가 다른 프로세스에 점유된 경우
ss -tlnp | grep 18789
```

**기존 프로세스 정리 후 재시작 (권장):**
```bash
# 기존 프로세스가 있으면 중지
pkill -9 -f "openclaw-gateway\|goclaw" 2>/dev/null
sleep 1

# 새 프로세스로 재시작
cd ~/goclaw && source .env.local && ./goclaw &
sleep 2

# 두 포트 모두 Listen 중인지 확인
ss -tlnp | grep -E "18789|18790"
```

**⚠️ 소스 빌드 vs 바이너리 차이:**
- 바이너리: 릴리스 페이지에서 다운로드 → 실행만 하면 됨
- 소스 빌드: `git clone` → `make build` → 생성된 바이너리 실행
- 둘 다 `.env.local` sourced 후 `./goclaw`로_gateway_ 기동

**바이너리 직접 다운로드 (릴리스):**
```bash
# https://github.com/nextlevelbuilder/goclaw/releases 에서 바이너리 다운로드
chmod +x goclaw
./goclaw
```

**⚠️ Docker 설치 시 로컬 PostgreSQL 포트 충돌**
- 로컬 PostgreSQL이 5432를 사용 중이면 Docker PostgreSQL이 포트 바인딩에 실패함
- 해결: `.env`에 `POSTGRES_PORT=5433` 설정 (Docker 컨테이너 내부는 5432, 호스트는 5433로 매핑)
  ```bash
  echo "POSTGRES_PORT=5433" >> /tmp/goclaw/.env
  docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d
  ```
- 확인: `ss -tlnp | grep 5432`로 로컬 포트 사용 현황 확인

**⚠️ Ubuntu 26.04 에서 apt install postgresql-16 은 실패함**
- 올바른 패키지명: `postgresql-18` (16 없음)
- `apt-cache search postgresql | grep "^postgresql-[0-9]+"` 로 확인

**⚠️ "too many failed authentication attempts" 오류**
게이트웨이 Web UI에 토큰을 여러 번 잘못 입력하면 인증이 잠깁니다.

해결책:
```bash
# 1. 모든 GoClaw 프로세스 확인
ps aux | grep -E "openclaw|goclaw" | grep -v grep

# 2. 실행 중인 게이트웨이/프로세스 전부 중지
kill -9 $(pgrep -f "openclaw-gateway") $(pgrep -f "./goclaw")
sleep 1

# 3. 포트가 비워졌는지 확인
ss -tlnp | grep -E "18789|18790"

# 4. 완전히 새 프로세스로 재시작 (실패 카운터 초기화됨)
cd ~/goclaw && source .env.local && ./goclaw &
sleep 2

# 5. 두 포트 모두 Listen 중인지 확인
ss -tlnp | grep -E "18789|18790"
```

**실행 후 프로세스 예시:**
```
openclaw-gateway  PID=39812  →  18789 (Gateway/WebSocket)
goclaw            PID=39894  →  18790 (Dashboard)
```

**⚠️ Token mismatch 오류 (`gateway token mismatch`)**
이 오류는 **GoClaw gateway가 정상 실행 중**이라는 뜻입니다. 토큰 값이 일치하지 않을 뿐입니다.

해결책:
1. `.env.local`에서 정확한 토큰 값 확인
   ```bash
   cat ~/goclaw/.env.local | grep TOKEN
   ```
2. Control UI 접속: http://localhost:18789/chat?session=main
3. WebSocket URL: `ws://localhost:18789`
4. 토큰 입력창에 `.env.local`의 `GOCLAW_GATEWAY_TOKEN` 값을 **정확히** 붙여넣기

**⚠️ Dashboard 접속 불가 → 404 정상 (GoClaw는 웹 UI가 없음)**
- GoClaw는 **CLI만 있는 도구**입니다 — 웹 대시보드/UI가 전혀 없습니다
- `http://127.0.0.1:18790`은 **WebSocket RPC 엔드포인트**입니다
- HTTP 요청 시 404가 돌아오는 것이 **정상**입니다
- `http://127.0.0.1:18790`을 브라우저로 열期望任何-webpage 것은 잘못된期待
- 설정/관리: **모두 CLI** (`./goclaw setup`, `./goclaw agent`, `./goclaw providers` 등)
- 참고: `./goclaw setup` 완료 시 "Dashboard: http://127.0.0.1:18790"라는 메시지가 나오지만, 이는오해의 여지가 있음 — 해당 URL은 웹 UI가 아니라 **gateway token 입력용 WebSocket 연결 페이지**일 뿐입니다

**⚠️ config.json providers가 DB에 로드 안 되는 문제**
config.json의 `providers` 섹션을 편집해도 DB(`llm_providers` 테이블)에 자동 반영 안 됨.

**확인 방법:**
```bash
PGPASSWORD=goclaw123 psql -U postgres -d goclaw -h /var/run/postgresql -c "SELECT id, name, provider_type FROM llm_providers;"
# → 0 rows이면 providers가 로드 안 된 것
```

**해결책:**
1. **`./goclaw setup` 실행 (권장)**: 인터랙티브 설정 마법사에서 Provider/Agent/Channel 순서대로 설정
2. **DB 직접 INSERT**:
   ```sql
   PGPASSWORD=goclaw123 psql -U postgres -d goclaw -h /var/run/postgresql
   INSERT INTO llm_providers (name, provider_type, api_key, created_at, updated_at)
   VALUES ('openrouter', 'openrouter', 'sk-or-v1-...', NOW(), NOW());
   ```

**⚠️ config.json 직접 편집 시 주의**
- GoClaw는 config.json 변경 후 재시작해도 채널 설정을 로드하지 않는 경우가 많음
- **Provider 설정은 반드시 Dashboard 또는 DB 직접 삽입으로 처리**
- config.json은Gateway/포트 등의 기본 설정만 사용

**⚠️ Telegram 연동 후 페어링 필요 (CLI에서 승인 필수)**
Telegram _bot에게 메시지 보내면 다음과 같이 페어링 코드 발급:
```
🔗 This account hasn't been paired yet.
Pairing code: PE7YKRR9
```
**CLI에서 반드시 승인해야 합니다:**
```bash
./goclaw pairing list          # 대기 중인 페어링 확인
./goclaw pairing approve XXXXX  # 승인 (여기서 XXXXX는 실제 코드)
```
승인 완료后才可在 Telegram에서 정상적으로 bot과 대화할 수 있습니다.

**OpenRouter 무료 모델 설정 (Dashboard 또는 config.json):**
```json
"providers": {
  "openrouter": {
    "api_key": "sk-or-v1-..."
  }
},
"agents": {
  "defaults": {
    "provider": "openrouter",
    "model": "openrouter/auto"
  }
}
```
- Dashboard 접속 후 Providers → OpenRouter → API Key 입력
- Agents → Default Provider: openrouter, Model: openrouter/auto

**⚠️ PostgreSQL peer 인증 문제 (자주 발생)**
GoClaw `onboard` 실행 시 `password authentication failed for user "postgres"` 오류가 나면:

1. postgres 사용자의 인증 방식을 `peer`(Unix소켓→OS계정확인)에서 `md5`(비밀번호)로 변경:
   ```bash
   sudo sed -i 's/local   all             postgres                                peer/local   all             postgres                                md5/' /etc/postgresql/18/main/pg_hba.conf
   sudo systemctl reload postgresql
   ```

2. postgres 비밀번호 설정:
   ```bash
   sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'goclaw123';"
   ```

3. 다시 `./goclaw onboard` 실행

**대안: comage 사용자 사용 (이미 DB 사용자가 있는 경우)**
- `.env.local`의 연결 문자열 사용: `postgres://comage:goclaw123@/goclaw?sslmode=disable&host=/var/run/postgresql`
- onboard에서 User=`comage`, Password=`goclaw123`, Database=`goclaw` 입력

## 완전 삭제 (재설치 전 필수)

GoClaw를 재설치하기 전 기존 설정을 완전히 제거해야 합니다.

```bash
# 1. 실행 중인 프로세스 중지
pkill -9 -f "goclaw" 2>/dev/null
pkill -9 -f "openclaw-gateway" 2>/dev/null
sleep 1

# 2. 파일/폴더 삭제
rm -rf ~/goclaw
rm -rf ~/.goclaw
rm -f ~/.env.local

# 3. PostgreSQL goclaw DB 삭제 (다른 용도로 사용 중이면 Skip)
sudo -u postgres psql -c "DROP DATABASE IF EXISTS goclaw;"
sudo -u postgres psql -c "DROP USER IF EXISTS goclaw;"

# 4. 삭제 확인
ls ~/ | grep goclaw      # → 빈 결과여야 함
ls ~/. | grep goclaw     # → 빈 결과여야 함
```

## 설치 (Docker Compose)

Docker Compose方式进行安装 (권장):

```bash
# 1. 클론仓库
git clone https://github.com/nextlevelbuilder/goclaw.git ~/goclaw
cd ~/goclaw

# 2. .env 파일 생성 (환경 변수)
cat > .env << 'EOF'
GOCLAW_GATEWAY_TOKEN=your-random-token-here
GOCLAW_ENCRYPTION_KEY=your-encryption-key-here
POSTGRES_USER=goclaw
POSTGRES_PASSWORD=goclaw
POSTGRES_DB=goclaw
POSTGRES_PORT=5433
GOCLAW_OPENROUTER_API_KEY=sk-or-v1-your-key
GOCLAW_PORT=18790
EOF

# 3. Docker 실행 (PostgreSQL 포함)
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d

# 4. 상태 확인
docker ps
docker compose -f docker-compose.yml -f docker-compose.postgres.yml ps

# 5. Gateway 토큰 확인
cat .env | grep GOCLAW_GATEWAY_TOKEN
```

**⚠️ Docker는 Web UI가 내장(embedui)되어 있습니다**
- 포트 18790 하나만으로 Gateway + Dashboard 모두 제공
- 브라우저에서 http://localhost:18790 접속 → Gateway Token 입력 → Setup Wizard

## OpenClaw 중지 (GoClaw 설치 전 필수)

OpenClaw와 GoClaw는 **다른 프로그램**입니다. GoClaw 설치 전 OpenClaw를 중지해야 합니다.

```bash
# 1. systemd user 서비스 중지 및 자동 실행 방지
systemctl --user stop openclaw-gateway
systemctl --user disable openclaw-gateway

# 또는 서비스 파일 이동으로 방지
mv ~/.config/systemd/user/openclaw-gateway.service \
   ~/.config/systemd/user/openclaw-gateway.service.disabled

# 2. 실행 중인 프로세스 중지
kill $(pgrep openclaw-gateway)

# 3. 포트 확인 (18789 비워져야 함)
ss -tuln | grep 18789
```

## Docker Compose 마운트 추가 (Hermes 데이터 공유)

`docker-compose.yml`의 `volumes:` 항목 수정:

```yaml
    volumes:
      - goclaw-data:/app/data
      - goclaw-workspace:/app/workspace
      - /home/comage/.hermes/skills:/app/data/skills/hermes:ro
      - /home/comage/.hermes/memory:/app/data/memory/hermes:ro
      - /home/comage/.hermes/scripts:/app/data/scripts/hermes:ro
      - /home/comage/obsidian-vault:/app/data/vault/hermes:ro
```

**주의:** 기존 volume이 있으면 삭제 후 재시작 필요

```bash
docker compose -f docker-compose.yml -f docker-compose.postgres.yml down -v
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d
```

## 마운트 확인

```bash
docker exec goclaw-goclaw-1 ls /app/data/skills/hermes/
docker exec goclaw-goclaw-1 ls /app/data/memory/hermes/
```

## 에이전트 성격 파일 경로 (템플릿)

| 파일 | 호스트 경로 |
|------|-------------|
| SOUL.md | `~/goclaw/internal/bootstrap/templates/SOUL.md` |
| IDENTITY.md | `~/goclaw/internal/bootstrap/templates/IDENTITY.md` |
| AGENTS.md | `~/goclaw/internal/bootstrap/templates/AGENTS.md` |
| USER.md | `~/goclaw/internal/bootstrap/templates/USER.md` |
| CAPABILITIES.md | `~/goclaw/internal/bootstrap/templates/CAPABILITIES.md` |

## 외부 접속 설정

```bash
# UFW로 포트 열기
sudo ufw allow 18790

# 또는 Ngrok 터널링
ngrok http 18790
```

## 에이전트 파일 구조

GoClaw 에이전트는 **마크다운(.md) 파일**로 설정됨 — YAML/JSON 인식 안 함.

### 경로 구조
```
/app/workspace/{에이전트명}/{채널}/{채팅ID}/
├── SOUL.md          # 가치관, 성격, 행동 원칙
├── IDENTITY.md      # 이름, 이모지, 아바타
├── AGENTS.md        # 역할, 책임, 대화 스타일
├── USER.md          # 사용자 정보
├── CAPABILITIES.md  # 기술/능력 목록 (선택)
└── memory/          # 메모리 폴더 (선택)
```

### ⚠️ 자주 발생하는 문제

1. **YAML/JSON 설정파일 인식 불가**
   - `config/*.yaml`, `config/*.json5` → GoClaw가 읽지 않음
   - `.md` 파일로 변환 필요

2. **중괄호 디렉토리 잘못 생성**
   - `{SOUL,AGENTS,IDENTITY,USER}/` — 전개 안 된 잘못된 디렉토리
   - 삭제 후 파일로 재생성 필요

3. **Docker exec 권한 문제**
   - 파일 수정/생성 시 `Permission denied`
   - 로컬에서 `docker cp`로 파일 주고받기

### 디렉토리 정리 명령

```bash
# 1. 잘못된 중괄호 디렉토리 삭제
docker exec goclaw-goclaw-1 rm -rf /app/workspace/.../agents/{에이전트들}

# 2. 로컬에서 디렉토리 내용을 파일로 변환
docker cp goclaw-goclaw-1:/app/workspace/.../agents/localizer/SOUL/ ./temp/
cat ./temp/* > ./localizer/SOUL.md

# 3. 파일 복사回去
docker cp ./localizer/ goclaw-goclaw-1:/app/workspace/.../agents/
```

## 일반 사용자 생성 (권장)

GoClaw는 기본적으로 `postgres` 관리자 사용자를 사용하려고 합니다. 하지만 Ubuntu의 PostgreSQL은 기본적으로 **peer 인증**을 사용해서 비밀번호 로그인이 안 됩니다.

**권장: 별도 일반 사용자 생성**
```bash
# postgres 비밀번호 설정 (peer → md5 인증으로 변경하기 전이라도)
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'your_password';"

# pg_hba.conf에서 postgres 사용자를 md5 인증으로 변경
sudo sed -i 's/local   all             postgres                                peer/local   all             postgres                                md5/' /etc/postgresql/18/main/pg_hba.conf
sudo systemctl reload postgresql
```

또는 **onboard 과정에서 comage 사용자 사용** (이미 .env.local에 설정된 경우):
- User: `comage`
- Password: `goclaw123`
- Database: `goclaw`

## 문서

- 공식 문서: https://docs.goclaw.sh
- 에이전트 설명: https://docs.goclaw.sh/agents-explained
- 성격 편집: https://docs.goclaw.sh/editing-personality

## 세션 참고 자료

- `references/session-20260502.md` — 2026-05-02 설정 내용, 버그, PostgreSQL 설정
- `references/docker-install-notes.md` — Docker 설치 시 포트 충돌 해결, 빌드 출력, Gateway 접속

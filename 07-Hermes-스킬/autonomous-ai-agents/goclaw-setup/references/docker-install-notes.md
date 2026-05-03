# GoClaw Docker 설치 참고 노트 (2026-05-02)

## 발견된 문제들

### 1. 포트 5432 충돌
- **현상**: Docker PostgreSQL 시작 시 `address already in use` 오류
- **원인**: 로컬 PostgreSQL 18이 5432 포트 사용 중
- **해결**: `.env`에 `POSTGRES_PORT=5433` 설정

```bash
# 확인
ss -tlnp | grep 5432
ps aux | grep postgres
```

### 2. .env 파일 생성 방식
- `prepare-compose.sh`는 `COMPOSE_FILE` 환경변수만 설정 (`.env` 생성 안 함)
- `.env.example`을 복사해서 수동 생성 필요

### 3. Docker 빌드 출력
- GoClaw Docker 이미지는 웹 UI가 포함된 `embedui` 태그로 빌드됨
- 빌드 시 Vite로 웹 UI 번들링 진행 (수십 초 소요)

## Docker 설치 완료 후 상태

```
CONTAINER ID   IMAGE                            PORTS
goclaw-goclaw-1   ghcr.io/.../goclaw:latest   0.0.0.0:18790->18790/tcp
goclaw-postgres-1 pgvector/pgvector:pg18        0.0.0.0:5433->5432/tcp
```

## 확인 명령어

```bash
# 컨테이너 상태
docker ps

# 로그 확인
docker logs --tail 50 goclaw-goclaw-1

# 대시보드 접속
curl -s http://localhost:18790  # HTML 응답이 와야 함
```

## Gateway Token으로 접속

1. 브라우저: http://localhost:18790
2. Gateway Token 입력 (`.env`의 `GOCLAW_GATEWAY_TOKEN` 값)
3. Setup Wizard에서 OpenRouter API Key 설정

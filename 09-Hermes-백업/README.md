# Hermes Agent & GoClaw 백업

생성: 2026-05-03

## 포함 파일

| 파일 | 설명 |
|------|------|
| `hermes_backup_20260503.tar.gz` | Hermes Agent + GoClaw 핵심 설정 압축본 |
| `secrets-2026-05-03.md` | API 키/토큰 문서 (마크다운) |
| `secrets-2026-05-03.env` | API 키/토큰 .env 파일 |

## 압축 해제 방법

```bash
cd ~/obsidian-vault/09-Hermes-백업
tar -xzf hermes_backup_20260503.tar.gz
```

## 백업 내용

### Hermes Agent
- `.env` — API 키, Telegram Bot Token
- `config.yaml` — Hermes 설정
- `auth.json` — 인증 정보
- `SOUL.md` — Hermes 페르소나
- `channel_directory.json` — 채널 정보
- `cron/` — 스케줄된 작업
- `skills/` — 커스텀 스킬
- `memory/` — 메모리 데이터
- `backups/` — 기존 백업

### GoClaw
- `goclaw/data/` — 런타임 데이터
- `goclaw/.goclaw/` — 설정

## 주의사항

⚠️ `secrets-*.md` 와 `secrets-*.env` 파일은 민감 정보를 포함하고 있습니다.
외부 유출에 주의하세요!

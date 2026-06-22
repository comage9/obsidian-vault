# Hermes 백업 매니페스트

## 백업 일시
2026-06-02 20:55:56 KST

## 백업 소스
- 홈: `/home/comage/.hermes/`
- 운영체제: Linux Mint
- 사용자: comage

## 백업 대상
| 디렉토리 | 내용 | 파일 수 | 크기 |
|---------|------|--------|------|
| `memories/` | MEMORY.md, USER.md (운영 지침) | 2 | 7.5KB |
| `config/` | SOUL.md, config.yaml, auth.json, .env | 4 | 45KB |
| `skills/` | SKILL.md + references 30개 카테고리, 104개 스킬 | 621 | 7.7MB |
| `obsidian/wiki-snapshot/` | Wiki 11페이지 (read-only 스냅샷) | 11 | ~50KB |
| `obsidian/README.md` | 위키 시스템 위치/구조/복원 절차 | 1 | 2.6KB |

## 제외된 파일
- `~/.hermes/skills/**/.stfolder` (Syncthing 마커)
- `~/.hermes/skills/**/*.lock` (동시성 잠금)
- `~/.hermes/skills/**/.stignore` (Syncthing 무시 패턴)
- `~/.hermes/state.db*` (세션 DB, 실행 중)
- `~/.hermes/sessions/`, `~/.hermes/cache/`, `~/.hermes/image_cache/`, `~/.hermes/audio_cache/`, `~/.hermes/pastes/`, `~/.hermes/sandboxes/`, `~/.hermes/lsp/` (기기별/일시적)
- `~/.hermes/hermes-agent/` (내장, GitHub에서 복원 가능)
- `~/.hermes/node/`, `~/.hermes/bin/`, `~/.hermes/cron/` (실행 환경)

## 백업 검증
- `diff -q` 로 memories/, config/ 각 파일 동일 확인
- skills/ 파일 수: 원본 622개 → 백업 621개 (lock 1개 제외 정상)

## 복원 절차
1. **memories/ 복원**:
   ```bash
   cp -r <backup>/memories/* ~/.hermes/memories/
   # 또는 memory tool로 semantic load (권장)
   ```
2. **config/ 복원** (선택):
   ```bash
   cp <backup>/config/* ~/.hermes/
   # ⚠️ config.yaml은 기기별 다를 수 있음 — 신중히
   ```
3. **skills/ 복원**:
   ```bash
   rsync -av <backup>/skills/ ~/.hermes/skills/
   ```
4. **Wiki 복원**: GitHub에서 obsidian-vault.git clone 후 `06-Wiki-시스템/` 복사

## 다음 백업 권장 주기
- 메모리/스킬 변경 시: 즉시
- 일반: 주 1회 (격주 일요일 저녁)
- `hermes-full-backup.sh` 사용 권장 (전체 + cron 연동)

# Hermes 스냅샷 매니페스트 (2026-06-02 23:15 KST)

## 백업 일시
2026-06-02 23:15:42 KST

## 이번 세션에서 확정된 운영 모델 (2026-06-02)

- **VF-project 마스터**: `/media/comage/data/coding/VF-new - 복사본/` (NTFS rw, Windows+Linux 공유)
- **VF-project Linux 실행본**: `/home/comage/VF-project/` (마스터 복사 + Linux venv/esbuild 재생성)
- **외부 IP**: `59.9.19.188` (옛 `220.121.225.76`은 2026-04 시점 IP)
- **동시 실행 금지** (SQLite 락)

## 이번 세션 주요 작업

1. 텔레그램 봇 설정 (토큰 동기화, 게이트웨이 systemd 등록, 봇/CLI 메모리 동기화)
2. 메모리/USER.md 백업본 merge (8§ 통일, 9§ 추가)
3. VF-project 첫 실행 + 검증 (포트 5174/5176, 프록시)
4. GOOGLE_SHEETS_API_KEY placeholder → 삭제 (마스터 .env 8번 라인)
5. start_all.sh, stop_all.sh 작성 (마스터 + VF-project 둘 다)
6. IP 정정 (220.121.225.76 → 59.9.19.188) — 위키 10개 파일 + dist + 메모리
7. VF-project 삭제 → 마스터 시도 → Windows venv 발견 → VF-project 재생성
8. VF-project .venv 재생성 (Windows → Linux) + npm install (esbuild linux-x64)
9. 메모리 5번 줄 갱신 (옛 "복사 후 실행" → 마스터 직접 실행 + Linux는 복사본)
10. cross-platform-project-migration 스킬에 "백업 폴더 다중 역할" pitfall 추가
11. 위키 vf-project-실행-워크플로우-20260602 페이지 추가 (148줄)
12. 이 스냅샷 생성

## 백업 대상 (19개 파일, 125KB)

### `memories/`
- `MEMORY.md` (4,268B) — 8§, VF/Telegram/이전 VF-project 운영원칙
- `USER.md` (3,425B) — 8§ 운영원칙

### `skills/`
- `cross-platform-project-migration/SKILL.md` (이전 17,379B + "백업 폴더 다중 역할" pitfall 추가)
  - 이번에 패치된 전체 스킬은 `/home/comage/.hermes/skills/...`에 위치
  - 스냅샷에는 패치된 버전 1개만 포함

### `obsidian/wiki-snapshot/` (12페이지)
- `Wiki/index.md` (총 12페이지, vf-project-실행-워크플로우-20260602 Wikilink 추가)
- `Wiki/log.md` (작업 로그)
- `Wiki/SCHEMA.md`
- `개념/` 2개
- `문제-해결/` 2개
- `의사결정/` 6개 (vf-project-실행-워크플로우-20260602.md 신규)
  - vf-project-실행-워크플로우-20260602.md (6,390B, 148줄) **신규**

### `scripts/`
- `start_all.sh` (3,511B, 마스터용)
- `stop_all.sh` (1,165B, 마스터용)
- `start_all_vf-project.sh` (3,511B, VF-project용, 동일 내용)
- `stop_all_vf-project.sh` (1,165B, VF-project용, 동일 내용)

## 복원 절차 (재해 시)

1. **메모리/USER 복원**:
   ```bash
   cp -r <backup>/memories/* ~/.hermes/memories/
   ```

2. **스킬 복원** (cross-platform-project-migration):
   ```bash
   cp <backup>/skills/cross-platform-project-migration/SKILL.md \
      ~/.hermes/skills/software-development/cross-platform-project-migration/SKILL.md
   ```

3. **위키 복원** (Syncthing으로 자동 동기화되지만 손상 시):
   ```bash
   cp -r <backup>/obsidian/wiki-snapshot/Wiki/* \
      /media/comage/data/hermes-backup/obsidian/06-Wiki-시스템/Wiki/
   ```
   또는 GitHub에서:
   ```bash
   git clone https://github.com/comage9/obsidian-vault.git /tmp/wiki-restore
   cp -r /tmp/wiki-restore/06-Wiki-시스템/Wiki/* \
      /media/comage/data/hermes-backup/obsidian/06-Wiki-시스템/Wiki/
   ```

4. **VF 실행 스크립트 복원** (마스터/VF-project 둘 다):
   ```bash
   cp <backup>/scripts/start_all.sh "/media/comage/data/coding/VF-new - 복사본/"
   cp <backup>/scripts/stop_all.sh "/media/comage/data/coding/VF-new - 복사본/"
   ```

## 다음 백업 권장 시점
- VF-project 코드 변경 시
- 위키 페이지 추가/수정 시
- 메모리 § 추가/수정 시
- 정기: 격주 일요일 저녁

## 검증
- 메모리: 8§, 키워드 Syncthing×2, WIKI×1, Reasonix×1, Zebra×1, WinApps×1, CRITICAL×1, /media/comage/data×3
- 위키: 12페이지, index.md Wikilink 11개 (1줄 추가)
- 스킬: cross-platform-project-migration 320줄 (17,379B+패치)
- VF 실행: 백엔드 5176, 프론트엔드 5174 정상 (마지막 검증 2026-06-02 23:08)

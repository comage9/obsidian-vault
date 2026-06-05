# Hermes 스냅샷 매니페스트 (2026-06-03 00:19 KST)

## 백업 일시
2026-06-03 00:19:47 KST

## 이번 세션 작업 (옵션 2: symlink 데이터 단일 소스)

사용자 질문: "db/데이터를 마스터에 동기화 저장할 수 있나? Windows에서도 그대로 사용 가능?" 에 대한 답변으로 **옵션 2 (symlink)** 채택.

### 핵심 변경

1. **VF-project의 `db.sqlite3`, `inventory_unified.json`을 마스터로 symlink**
   - VF-project가 마스터 db를 직접 읽고 씀
   - Windows 실행 → 마스터 db 변경 → Linux 실행 시 즉시 같은 데이터
   - cp 동기화 불필요, 데이터 누락 0%

2. **start_all.sh에 symlink 보장 로직 추가**
   - cp -r로 마스터 복사 시 db.sqlite3은 일반 파일로 옴
   - start_all.sh 실행 시 자동 symlink로 교체 (백업 후)
   - 마스터 + VF-project start_all.sh 둘 다 동일하게 패치

3. **메모리 9§ 추가**: "VF-project 옵션 2 채택, symlink, NTFS rw, SQLite single-writer, 동시 실행 금지"

4. **위키 vf-project-실행-워크플로우 페이지 보강** (148 → 176줄):
   - "데이터 단일 소스 (옵션 2: symlink)" 섹션 추가
   - 검증 결과 (count: 30, latestDate: 2026-06-02)
   - 변경 이력 23:17 항목 추가

### 데이터 검증 (2026-06-02 23:17)
- VF-project `/api/production`: count 30, latestDate 2026-06-02 (마스터 db)
- 마스터 db mtime 변경 → VF-project에서 즉시 반영
- md5 일치: `4a25e61095ed09b8bdf546c2c8ae25bc`

## 백업 대상 (19개 파일, 133KB)

### `memories/`
- `MEMORY.md` (4,268B+) — **9§ (이전 8 + 옵션2 항목)**
- `USER.md` (3,425B) — 8§

### `skills/`
- `cross-platform-project-migration-SKILL.md` (패치됨, 백업 폴더 다중 역할 pitfall 포함)

### `obsidian/wiki-snapshot/` (12페이지)
- `Wiki/index.md` (12페이지, vf-project-실행-워크플로우 Wikilink)
- `Wiki/의사결정/vf-project-실행-워크플로우-20260602.md` (176줄, **이번에 30줄 추가**)
- 11개 기존 페이지

### `scripts/`
- `start_all.sh` (마스터용, 3.6KB, symlink 보장 로직 포함)
- `stop_all.sh` (마스터용)
- `start_all_vf-project.sh` (VF-project용, 동일)
- `stop_all_vf-project.sh` (VF-project용, 동일)

## 복원 절차 (재해 시)

1. 메모리/스킬/위키 복원 (이전 스냅샷과 동일)
2. VF-project 재생성:
   ```bash
   cp -r "/media/comage/data/coding/VF-new - 복사본" /home/comage/VF-project
   cd /home/comage/VF-project/backend
   rm -rf .venv && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
   cd /home/comage/VF-project/frontend/client
   mv node_modules node_modules.win.bak && npm install
   cd /home/comage/VF-project
   ./start_all.sh   # ← symlink 자동 보장 (db.sqlite3, inventory_unified.json)
   ```

## 운영 가드레일
- **동시 실행 절대 금지** (SQLite single-writer)
- **마스터가 단일 데이터 소스** — VF-project는 항상 symlink로 마스터 참조
- **cp -r로 재생성 시** start_all.sh가 symlink 자동 복원
- **db.sqlite3 변경 시**: VF-project 종료 → 백업 → start_all.sh로 재시작 (자동 symlink 확인)

## 변경 이력
- 2026-06-02 23:15: vf-project-실행-워크플로우-20260602 페이지 최초 작성
- 2026-06-02 23:17: 옵션 2 (symlink) 적용, start_all.sh 자동화, 위키 보강
- 2026-06-03 00:19: 본 스냅샷 생성

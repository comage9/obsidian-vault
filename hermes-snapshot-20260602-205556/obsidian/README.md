# Hermes 백업 - Obsidian Wiki 정보

## 생성일
2026-06-02 20:55:56

## Wiki 시스템 위치 (read-only 마스터, Syncthing 소스)
- **로컬 마스터**: `/media/comage/data/hermes-backup/obsidian/06-Wiki-시스템/`
- **GitHub 원격**: `github.com/comage9/obsidian-vault.git`
- **자동 Push 주기**: 6시간마다 (wiki-git-push.sh 크론)
- **마스터 디렉토리**: `06-Wiki-시스템/` (이 디렉토리만 백업 대상)

## Wiki 시스템 구조
```
06-Wiki-시스템/
├── Wiki/                    # 위키 본체 (11 페이지)
│   ├── index.md             # 인덱스 (Wikilink 9개)
│   ├── log.md               # 작업 로그 (append-only)
│   ├── SCHEMA.md            # 위키 규칙/frontmatter
│   ├── 개념/                # 2개 페이지
│   ├── 문제-해결/           # 2개 페이지
│   └── 의사결정/            # 4개 페이지
├── Logs/                    # 인제스트, 동기화, lint 로그 30+개
├── scripts/                 # wiki-cleanup.sh, wiki-daily-briefing.sh, wiki-git-push.sh, wiki-lint.sh
└── .scripts/wiki-daily-ingest.sh
```

## Wiki 페이지 목록 (11개)
1. `Wiki/index.md` — 인덱스
2. `Wiki/log.md` — 작업 로그
3. `Wiki/SCHEMA.md` — 위키 스키마
4. `개념/telegram-이상징후-검증-20260528.md`
5. `개념/telegram-이상징후-판단기준-20260528.md`
6. `문제-해결/ki-ai-trader-미해결-이슈-20260528.md`
7. `문제-해결/ki-ai-trader-is_running-일일손실한도-버그.md`
8. `의사결정/백테스트-v3-엔진-완료-20260528.md`
9. `의사결정/ki-ai-trader-20260528-전면수정-완료.md`
10. `의사결정/vf2-20260529-수정계획.md`
11. `의사결정/reasonix-acp-도입-20260531.md`

## VF 프로젝트 위치
- `obsidian/01-VF-프로젝트/` — VF 프로젝트 (생산계획 모바일 UI)
  - 구현/ (유틸리티, 컴포넌트)
  - 메모리/시스템/ (메모리 시스템 가이드)
  - 문서/ (기술문서, 프로젝트-기록)
  - 세션로그/ (2026-04-06 ~ 2026-04-13 로그들)
- `obsidian/04-일반/세션로그/2026-04-12.md`

## 검색 경로
- 작업 시 위키 검색: `/media/comage/data/hermes-backup/obsidian/06-Wiki-시스템/Wiki/`
- 백업 정본 (변경 금지): `/media/comage/data/hermes-backup/obsidian/`

## 복원 절차 (재해 시)
1. `06-Wiki-시스템/` 전체를 GitHub에서 clone:
   ```bash
   git clone https://github.com/comage9/obsidian-vault.git /tmp/wiki-restore
   ```
2. `06-Wiki-시스템/` 디렉토리를 `/media/comage/data/hermes-backup/obsidian/`로 복사
3. Wiki Git Auto-Sync 크론 (`cronjob list`로 확인) 재등록

---
name: hermes-wiki-system
description: Hermes Wiki Knowledge System - Obsidian 기반 개인 지식 데이터베이스
category: note-taking
---

# Hermes Wiki Knowledge System

## 개요

Andrej Karparthi 방식의 개인 지식 위키 시스템으로, Obsidian vault를 활용하여 지식을 누적합니다.

## 폴더 구조

현재 **06-Wiki-시스템/**만 Hermes Wiki 시스템에 통합된 상태입니다.

```
Obsidian Vault (/home/comage/obsidian-vault/)
├── 01-VF-프로젝트/      ← VF 프로젝트 문서 (미통합)
├── 02-금형정보/        ← 금형 정보 문서 (미통합)
├── 04-일반/            ← 일반 문서 (미통합)
├── 06-Wiki-시스템/     ← ✅ Hermes Wiki 통합 완료
│   ├── Raw/           ← 원본 자료 (유튜브 자막, 문서, 세션 로그 등)
│   ├── Wiki/          ← 정리된 지식 (개념, 개체, 요약)
│   ├── Logs/          ← 활동 로그
│   └── README.md      ← 이 파일
└── mindvault-out/      ← mindvault 출력
```

### 확장 가능성
01, 02, 04 폴더도 동일한 3단계 구조(Raw→Wiki→Logs)로 확장 가능하며, 스크립트와 Cronjob을 공통으로 사용합니다.

## 핵심 원칙 (3단계)

1. **Raw 폴더에 원본 자료 저장**
2. **스크립트가 분석하여 Wiki 폴더에 정리**
3. **Wiki 기반 지식 데이터베이스 완성**

## 사용 방법

### 1. 세션 시작 시

```bash
# 세션 로그 파일 생성
bash ~/.hermes/scripts/wiki-session-start.sh
```

### 2. 작업 중 결정사항 기록

```bash
# 결정사항을 Raw 폴더에 추가
echo "- 결정: $CONTENT" >> ~/.hermes/scripts/session-notes.md
```

### 3. 세션 종료 시

```bash
# 인제스트 실행 (Raw → Wiki)
bash ~/.hermes/scripts/wiki-ingest.sh

# 린트 실행 (무결성 검사)
bash ~/.hermes/scripts/wiki-lint.sh
```

## 자동화 Cronjob

| 시간 | 작업 | 설명 |
|------|------|------|
| 매시간 정각 | GitHub Sync | GitHub 변경사항 AI 검토 후 동기화 |
| 매일 아침 9시 | 인제스트 | Raw 폴더 분석 후 Wiki에 정리 |
| 매일 밤 10시 | 린트 | Wiki 문서 무결성 검사 및 인덱스 업데이트 |

## 스크립트 목록

| 스크립트 | 경로 | 기능 |
|---------|------|------|
| `wiki-ingest.sh` | `~/.hermes/scripts/` | Raw → Wiki 변환 (AI 지능형) |
| `wiki-query.sh` | `~/.hermes/scripts/` | Wiki 검색/답변 생성 |
| `wiki-lint.sh` | `~/.hermes/scripts/` | Wiki 무결성 검사 (자동 수정) |
| `wiki-sync.sh` | `~/.hermes/scripts/` | GitHub → Wiki AI 검토 동기화 |
| `wiki-session-start.sh` | `~/.hermes/scripts/` | 세션 로그 생성 |

## GitHub 동기화 (GitHub Sync)

### 경로 구조 (주의!)
```
Git Repo: /home/comage/obsidian-vault/        ← .git이 여기
Wiki:     /home/comage/obsidian-vault/06-Wiki-시스템/
Scripts:  /home/comage/.hermes/scripts/       ← 스크립트 실행은 여기서
```

### 동기화 방식: AI 검토 후 Pull
```
1. git fetch (원격 변경사항 확인)
2. Dry-run으로 변경내용 미리보기
3. 상황별 처리:
   - 🆕 새 문서    → AI가 분류 (개념/개체/주제/요약) 후 추가
   - ✏️ 수정 문서  → AI가 diff 분석 후 병합
   - 🗑️ 삭제 문서  → Logs에 기록 후 처리
4. 충돌 없으면 자동 Pull / 충돌 있으면 사용자 확인
```

### wiki-sync.sh 사용법
```bash
# 일반 동기화 (Dry-run 먼저 → 변경내용 확인 → 실제 Pull)
bash ~/.hermes/scripts/wiki-sync.sh

# 미리보기만 (실제 변경없음)
bash ~/.hermes/scripts/wiki-sync.sh --dry-run

# 강제 동기화 (로컬 변경사항 stash 후 진행)
bash ~/.hermes/scripts/wiki-sync.sh --force
```

### Cronjob: 매시간 정각 실행 (0 * * * *)
- Dry-run으로 변경사항 미리보기
- 결과가 이 채팅방으로 자동 전송
- 실제 Pull은 스크립트 내 대화형 확인 또는 --force 옵션

## ⚠️ 중요 규칙

**모든 스크립트 출력은 한글로만 작성한다.**
- 스크립트 echo, printf 등의 모든 출력 메시지는 한국어만 사용
- 프롬프트도 한국어로 작성
- 로그 파일도 한글로 기록

## Hermes Agent Memory 연동

Hermes Agent의 SQLite DB Memory와 Obsidian Wiki를 연결하여 지식 관리 효율성을 극대화합니다.

### Memory 압축 원칙
- Memory는 **간결하게 유지** (목표: 50% 이하)
- 상세 내용은 Obsidian Wiki 경로를 참조
- 핵심 요약만 Memory에 저장

### Memory 저장 패턴
```
저장: 핵심 규칙, 현재 상태, 경로만
참조: Obsidian Wiki 문서 (자세한 내용)
```

### Memory 항목 예시
```markdown
## Hermes Wiki 히스토리 (압축)
시작: Andrej Karparthi LLM Wiki 방식 학습
현재: 3계층(Raw→Wiki→Logs), 스크립트4개, Cronjob3개
계획: Wiki문서다양화, OpenClova공유, 하이브리드(HerCEO,OCdelegator)
자세한: /06-Wiki-시스템/Wiki/2026-04-27-세션-카파시-위키-방식-설정.md
```

### Memory 용량 관리
- 80% 이상 → 중복 항목 제거/압축 진행
- 압축 후: 상세 내용은 Obsidian Wiki 경로로 참조

## OpenClova 하이브리드 오케스트레이션

Hermes Agent와 OpenClova를 동시에 사용하는 방식으로 지식 시스템을 공유합니다.

### 역할 분담
| Agent | 역할 | 담당 업무 |
|-------|------|----------|
| **Hermes** | CEO (Orchestrator) | Cronjob, 자동화, 가벼운 추론 |
| **OpenClova** | Delegator | 복잡한 리서치, 하드코어 작업 |

### 공유 구조
```
Hermes Agent ──┐
               ├──▶ Obsidian Vault (동일 폴더 공유)
OpenClova ─────┘
```

### Workflow
1. Hermes: Obsidian Wiki 내용 Memory에_integrate
2. Hermes: GitHub에 Push
3. OpenClova: GitHub에서 Pull
4. OpenClova: 새로운 내용 정리 후 Push
5. Hermes: GitHub Sync로 변경사항 확인 → Memory 갱신

### GitHub 주소
```
https://github.com/comage9/obsidian-vault
```

## Obsidian에서 확인

Obsidian 앱에서 vault를 열고 `06-Wiki-시스템` 폴더를 선택하면:
- **그래프 뷰**: 문서 간 관계 시각화
- **백링크**: 관련 문서 간 연결 확인
- **태그 패널**: 태그별 문서 분류

## 활용 예시

### 매번 작업 종료 시

```
작업이 끝나면: "이번 세션에서 한 일을 Raw에 저장해줘"
```

### 질문 시

```
"지난 주에 VF 프로젝트에서 뭘 했어?"
→ Wiki에서 검색하여 답변
```

## 관련 스킬

- `obsidian`: Obsidian vault 기본 조작

---
title: "hermes-agent 스킬 크로스 디바이스 사용 가이드"
date: 2026-06-07
category: Hermes
---

# hermes-agent 스킬 v2.2.0 — 크로스 디바이스 사용 가이드

## 개요

Windows Hermes(CLI)에서 `hermes-agent` 스킬을 v2.2.0으로 업데이트했습니다.
이 문서는 Linux Hermes(우분투) 및 Telegram 봇이 동일한 스킬을 사용할 수 있도록 경로와 방법을 안내합니다.

## 다른 에이전트 사용 방법

### 방법 1: 로컬 스킬 디렉토리에서 직접 로드 (권장)

각 Hermes 인스턴스의 로컬 스킬 디렉토리에 동일한 SKILL.md가 있으면 됩니다.
번들 스킬(`hermes-agent`)은 `hermes update` 시 자동 동기화되지만, **로컬에서 수정한 내용은 덮어쓰여질 수 있습니다.**

### 방법 2: 공유 저장소에서 읽기

Git 백업 저장소를 통해 접근:

| 에이전트 | 경로 |
|:---------|:-----|
| **Windows Hermes** (현재) | `C:\Users\kis\AppData\Local\hermes\skills\autonomous-ai-agents\hermes-agent\SKILL.md` |
| **Linux Hermes** (우분투) | `/media/comage/data1/hermes-backup/obsidian/06-Wiki-시스템/Wiki/Hermes/hermes-agent-SKILL-v2.2.0.md` |
| **Telegram 봇** | `read_file()`로 위 경로 중 하나 사용 |

### Linux 에이전트가 로드하는 명령어

```bash
# 방법 A: 로컬 스킬로 직접 읽기
read_file("~/.hermes/skills/autonomous-ai-agents/hermes-agent/SKILL.md")

# 방법 B: 공유 저장소에서 읽기 (위키 백업)
read_file("/media/comage/data1/hermes-backup/obsidian/06-Wiki-시스템/Wiki/Hermes/hermes-agent-SKILL-v2.2.0.md")

# 방법 C: skill_view로 로드 (로컬에 설치된 경우)
skill_view(name='hermes-agent')
```

### Windows 에이전트가 로드하는 명령어

```bash
# 로컬 스킬 로드 (번들, 현재 v2.2.0)
skill_view(name='hermes-agent')

# 또는 Wiki 백업에서 읽기
read_file("E:\\hermes-backup\\obsidian\\06-Wiki-시스템\\Wiki\\Hermes\\hermes-agent-SKILL-v2.2.0.md")
```

## 주의사항

1. **hermes update 실행 시 번들 스킬 복원됨** — 로컬 수정본이 덮어쓰여질 수 있습니다.
   - `hermes skills reset hermes-agent --restore` 로 번들 버전으로 되돌리기 가능
2. **크로스 디바이스 동기화**: Syncthing을 통해 `E:\hermes-backup\` → Linux `/media/comage/data1/hermes-backup/` 자동 동기화
3. **스킬 이름 충돌 방지**: `hermes-agent`는 번들 스킬명이므로, 별도 이름으로 저장하려면 `hermes-agent-v2.2.0` 등으로 명명

## 변경 내역

| 날짜 | 버전 | 변경 내용 |
|:----|:----|:---------|
| 2026-06-07 | 2.2.0 | 공식 문서 75페이지 통합, Features Reference(23개), Messaging Platforms(24개), Web Search & Browser Tools 전용 섹션, Guides(15개), Security Summary, Learning Path, Changelog 추가 |
| (번들) | 2.1.0 | Hermes Agent 기본 번들 스킬 |

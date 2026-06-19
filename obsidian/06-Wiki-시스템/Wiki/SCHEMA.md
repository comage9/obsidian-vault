# Wiki Schema

## Domain
K.I. Trainer (키트레이너) 자동매매 시스템 — 백테스트, 전략, 분봉 데이터, 시스템 아키텍처, 의사결정 기록

## Conventions
- File names: lowercase-korean, hyphens (e.g., `백테스트-v3-엔진-완료-20260528.md`)
- Every wiki page starts with YAML frontmatter (type, created, status, tags)
- Use `[wikilinks](wikilinks.md)` between related pages
- Every action must be appended to `log.md`

## Frontmatter
```yaml
---
title: Page Title
type: 의사결정 | 개념 | 문제해결 | 아이디어
created: YYYY-MM-DD
status: 완료 | 진행중 | 대기
okf_version: 0.1              # OKF v0.1 호환 표시 (2026-06-18 추가, 옵션)
tags: [tag1, tag2]
sources: [raw/articles/source-name.md]  # 옵션
# OKF v0.1 호환 추가 type (2026-06-18): Service | Resource | Tool
# 자유 type도 허용 (OKF 관용 정책). lint 경고만, ERROR 아님.
---
```

> **OKF v0.1 호환 메모 (2026-06-18 추가)**
> - `okf_version: 0.1` 추가 → OKF spec 호환 표시 (생략 가능, 기본값 0.1로 간주)
> - `[wikilinks](wikilinks.md)` + 표준 마크다운 링크 둘 다 허용 (옵시디언 호환)
> - 충돌 방지: `Wiki/의사결정/규칙-충돌-방지-매트릭스-20260618.md`

## Tag Taxonomy
- System: K.I. Trainer, Arena Trader, 백테스트, 분봉, API
- Status: 완료, 진행중, 대기, 버그
- Domain: 트레이딩, 전략, 리스크, 설정

## Directories
- `의사결정/` — 확정된 결정과 근거
- `문제-해결/` — 버그 수정, 문제 해결 기록
- `개념/` — 개념 설명
- Root: `log.md` (작업 로그), `index.md` (목차)

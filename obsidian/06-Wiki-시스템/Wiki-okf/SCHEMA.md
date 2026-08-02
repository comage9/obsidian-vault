# Wiki Schema

## Domain
보노하우스 VF 생산관리 + 물류(LS/KPP/Supplier) + Hermes 에이전트 운영
(+ 하위 태그: KI Trader — 자동매매, 백테스트)

## Conventions
- File names: lowercase-korean, hyphens, 날짜后缀 (e.g., `백테스트-v3-엔진-완료-20260528.md`)
- Every wiki page starts with YAML frontmatter (title, type, created, status, tags)
- Use `[[wikilinks]]` between related pages (minimum 2 outbound links per page)
- Every action must be appended to `log.md`
- Every new page must be added to `index.md` under the correct section
- When updating a page, always bump the `updated` date

## Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: 의사결정 | 개념 | 문제해결 | 아이디어 | entity | concept | comparison | query
status: 완료 | 진행중 | 대기
신뢰도: EXTRACTED | INFERRED
okf_version: 0.1
tags: [from taxonomy below]
sources: []
---
```

> **OKF v0.1 호환 메모**
> - `okf_version: 0.1` 추가 → OKF spec 호환 표시 (생략 가능, 기본값 0.1로 간주)
> - `[[wikilinks]]` + 표준 마크다운 링크 둘 다 허용 (옵시디언 호환)
> - 자유 type도 허용 (OKF 관용 정책). lint 경고만, ERROR 아님.
> - 충돌 방지: `의사결정/규칙-충돌-방지-매트릭스-20260618.md`

## Tag Taxonomy
- **시스템:** hermes, opencodex, gateway, telegram, skill, cron
- **생산:** vf, vf-new, vf-go, production, mold, barcode, inventory
- **물류:** kpp, ls, supplier, departure, pallet, edi
- **트레이딩:** ki-trader, 백테스트, 분봉, 전략, 리스크
- **지식:** wiki, decision, pitfall, onboarding
- **품질:** extracted, inferred, contested
- **상태:** 완료, 진행중, 대기, 버그

Rule: every tag on a page must appear in this taxonomy. Add new tags here first.

## Directories
- `의사결정/` — 확정된 결정과 근거
- `운영원칙/` — 운영 규칙·절차
- `물류/` — KPP, LS/쿠팡, Supplier, VF 바코드·출차
- `Hermes/` — 에이전트 시스템·자가학습 Cron
- `개념/` — 개념 설명
- `문제-해결/` — 버그 수정, 문제 해결 기록
- `자기사고/` — 거울형 보고서
- `Sources/` — Layer 1: 원본 불변 (텍스트/바이너리)
- `Output/` — 파생 결과물 (재생성 가능, 템플릿 포함)
- Root: `SCHEMA.md`, `index.md`, `log.md`

## Page Thresholds
- **Create** when entity/concept appears in 2+ sources OR is central to one source
- **Add to existing** when a source mentions something already covered
- **DON'T create** for passing mentions or things outside the domain
- **Split** when page exceeds ~200 lines

## Update Policy
When new information conflicts with existing content:
1. Check dates — newer sources supersede older
2. If genuinely contradictory, note both positions with dates and sources
3. Mark in frontmatter: `contested: true`
4. Flag for user review in lint report

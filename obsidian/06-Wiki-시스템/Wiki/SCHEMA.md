# Wiki SCHEMA — 구조 및 규칙

**최종 갱신:** 2026-06-22
**Wiki 경로:** `/home/comtop/workspace/Wiki/obsidian/06-Wiki-시스템/Wiki/`

---

## 1. 디렉토리 구조

```
Wiki/
├── SCHEMA.md           # 본 문서 (구조/규칙/태그 분류)
├── index.md            # 전체 페이지 카탈로그
├── log.md              # 타임라인 (append-only)
├── 의사결정/            # 설정/협약/가이드 결정 기록
├── 운영원칙/            # 에이전트 행동 규칙
├── Hermes/             # Hermes 시스템/자가학습
├── 자기사고/            # 거울형 자기 분석
├── Sources/            # 원본 자료 (불변)
└── Output/             # AI 생성 결과물
```

---

## 2. Frontmatter 규칙 (2026-06-22 신규)

### 2.1 신뢰도 표시 (필수)

모든 Wiki 페이지 frontmatter에 `신뢰도` 필드를 포함한다.

| 값 | 의미 | 사용 시기 |
|:---|:-----|:---------|
| `EXTRACTED` | 원문/데이터에서 직접 추출한 사실 | DB 조회 결과, 공식 문서, API 응답 |
| `INFERRED` | 추론/해석/가정 기반 내용 | LLM 분석, 패턴 예측, 의견 |

**적용 시점:** `/ingest` 워크플로우 실행 시 자동 기입

### 2.2 frontmatter 템플릿

```yaml
---
저장일: YYYY-MM-DD
출처: 원본파일명_또는_URL
신뢰도: EXTRACTED  # 또는 INFERRED
태그: [keyword1, keyword2]
---
```

---

## 3. 중복 방지 (2026-06-22 신규)

### SHA-256 해시 체크

- 스크립트: `scripts/wiki-dedup-check.sh`
- 캐시 위치: `/home/comtop/workspace/Wiki/.wiki-hash-cache.json`
- `/ingest` 워크플로우 Step 2에서 자동 실행

**동작:**
- 파일의 SHA-256 해시를 캐시에서 조회
- `NEW` → 신규 처리, 캐시에 해시 등록
- `DUPLICATE:<파일명>` → 이미 처리된 파일, ingest 중단

---

## 4. llm-wiki 스킬 연동 (2026-06-22 신규)

llm-wiki 스킬(`~/.hermes/skills/llm-wiki/`)이 설치되어 있음.

- **독립 지식 베이스:** llm-wiki는 별도 디렉토리에서 자체 지식 베이스 구축
- **기존 Wiki와 별도:** 기존 Wiki(의사결정/, 운영원칙/ 등)는 기존 워크플로우 유지
- **교차 활용:** llm-wiki의 4단계 신뢰도(EXTRACTED/INFERRED/AMBIGUOUS/UNVERIFIED) 참고

### llm-wiki 사용법
- "지식 베이스를 초기화해줘" → llm-wiki init
- "이 글을 정리해줘: [URL]" → llm-wiki ingest

# Output Template — Wiki → 결과물 생성

> **용도:** Wiki에 쌓인 지식을 바탕으로 결과물(보고서, 메시지, 요약) 생성

## 트리거 문구
```
/output [결과물 종류]
/output ls-배차
/output 주간보고서
/output 보고서 "KPP 6월 현황"
/output 메시지 "다른 에이전트 전달용"
Wiki 기반으로 결과물 만들어줘
```

## 지원하는 결과물 종류

| 명령어 | 결과물 | 저장 위치 |
|:-------|:-------|:----------|
| `/output ls-배차` | LS 배차 요청 텍스트 (VF67 형식) | `Output/YYYY-MM-DD/LS-배차텍스트.md` |
| `/output kpp-등록` | KPP 등록 결과 보고 | `Output/YYYY-MM-DD/KPP-등록결과.md` |
| `/output 주간보고서` | 주간 작업 요약 | `Output/YYYY-MM-DD/주간보고서.md` |
| `/output 보고서 "제목"` | 특정 주제 Wiki 기반 보고서 | `Output/YYYY-MM-DD/보고서-제목.md` |
| `/output 메시지 "대상"` | 다른 에이전트 전달 메시지 | `Output/YYYY-MM-DD/전달메시지-대상.md` |
| `/output 요약` | 전체 Wiki 간략 요약 | `Output/YYYY-MM-DD/Wiki-요약.md` |

## 실행 절차

### Step 1: 관련 Wiki 문서 검색
```bash
search_files(pattern="관련주제", path="Wiki/")
```

### Step 2: 결과물 생성 프롬프트

```markdown
Wiki의 다음 문서들을 참고하여 [결과물 종류]를 만들어 주세요:

참고 문서:
- [문서1 경로]
- [문서2 경로]

출력 형식:
- 제목: [결과물 제목]
- 생성일: [날짜]
- 참고한 Wiki 문서: 목록
- 본문: [내용]

저장: Output/[날짜]/[파일명].md
```

### Step 3: Output 저장 + Git push
- 결과물 → `Output/YYYY-MM-DD/`에 저장
- Git add + commit + push

## 예시

**사용자:** `/output ls-배차`

**내 수행:**
1. `Wiki/물류/쿠팡/LS/` 관련 문서 검색
2. 오늘 LS 등록 현황 조회
3. 표준 형식으로 배차 요청 텍스트 생성
4. `Output/2026-06-08/LS-배차텍스트.md` 저장
5. 사용자에게 텍스트 전달 + Git push

---

최초 작성: 2026-06-08

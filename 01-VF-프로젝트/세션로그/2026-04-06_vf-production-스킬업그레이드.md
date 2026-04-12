# 2026-04-06 VF 프로젝트 세션로그

## 작업 내용

### vf-production 스킬 업그레이드
- `scripts/fetch-production.sh` 생성 - API 실시간 데이터 조회
  - today, latest, date, product, machine, specs, summary 명령 지원
- `references/production-summary.md` 업데이트 (총 18,369건)
- 제품 별명 매핑 표 정리 (토이, 로코스, 모던플러스 등 16개 제품군)

### 백엔드 코드 수정
- **UniqueConstraint 버그 수정**: date+machine+mold+product+color1+color2+unit
- **sort_order 필드 추가**: 정렬 order 필드 추가
- **bulk-reorder API 추가**: `POST /api/production-log/bulk-reorder`

### GitHub Token
- PAT: github_pat_11AJBGKCA0...
- repo: https://github.com/comage9/VF-.git

### 텔레그램 봇 파일 전송
- 토큰: TOOLS.md에 기록
- Chat ID: 5708696961

## 의사결정

- [x] 같은 제품/기계/색상/단위면 중복 → 삭제 규칙 적용
- [x] 색상 지정 없으면 이전 데이터에서 확인
- [x] 슬라이딩 스텝 L의 Butter 색상 → WHITE1만 인식

## 주현 피드백

- 응답 너무 늦다 → 빠르게 응답 필요
- 음성 메시지 인식 불가 → 텍스트로 요청
- "토이" 제품 인식 못함 → 별명 매핑 구축으로 해결

## 다음 할 일

- [ ] 프론트엔드 DnD 작업 (Claude Code로 진행)
- [ ] 서버 배포 (Windows에서 git pull + migrate)
- [ ] 마이그레이션: `python manage.py makemigrations sales_api && python manage.py migrate`

---

*최종 업데이트: 2026-04-06*

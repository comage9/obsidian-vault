# 자가 학습 Cron — KPP (WPPS) Nightly

**Cron ID:** `b773a0727897`
**시간:** 매일 23:30 KST (`30 23 * * *`)
**사용 스킬:** `mandatory-verification`, `kpp-pallet-management`
**생성일:** 2026-06-05
**배달 대상:** origin (대화방)

## 점검 대상

1. PBM110MW/PBM140MW 함정 (#1~#6)
2. SpreadJS Grid ID/컬럼 맵
3. React Controlled Input 패턴
4. Native Alert / dialog 처리
5. EDI 출력 절차
6. 화물 적재 규칙 (5T=12, 11T=14, UP only)
7. 하차지 코드표

## 변경 이력

- 2026-06-07: 함정 #6 추가 (CDP 인쇄 다이얼로그 금지)
- 2026-06-07: 화물 적재 규칙 갱신 (11T=14개, UP only NO DOWN)

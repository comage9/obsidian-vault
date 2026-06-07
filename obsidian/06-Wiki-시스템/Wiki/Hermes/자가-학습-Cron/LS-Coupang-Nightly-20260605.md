# 자가 학습 Cron — LS (Coupang) Nightly

**Cron ID:** `6fcf4d848e14`
**시간:** 매일 00:30 KST (`30 0 * * *`)
**사용 스킬:** `mandatory-verification`, `ls-coupang`
**생성일:** 2026-06-05
**배달 대상:** origin (대화방)

## 점검 대상

1. Keycloak OAuth2 인증 방식
2. Akamai Bot Manager 차단 현황
3. 브라우저 쿠키 우회 방식 (CDP Network.getCookies)
4. Tracking API 파라미터 (pageSize, statuses, locationStart)
5. PDF 다운로드 엔드포인트
6. Pitfalls #1~#12

## 변경 이력

- 2026-06-07: Pitfall #7/#8 추가 (VF67_H, curl -H Cookie)
- 2026-06-07: Watchdog 3-Way 응답 체계 추가

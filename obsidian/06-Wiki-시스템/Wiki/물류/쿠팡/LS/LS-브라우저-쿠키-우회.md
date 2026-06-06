# LS(Linehaul) 브라우저 쿠키 우회 방식

## 배경
2026-06-06 기준, `ls.coupang.com`의 Akamai Bot Manager가 curl 기반 로그인 POST를 차단.
브라우저에서는 정상 로그인되나, curl/스크립트 POST는 bot으로 감지되어 Keycloak이 거부.
해결방안: 브라우저 로그인 세션 쿠키를 추출하여 curl API 호출에 재사용.

## 관련 스킬
- `ls-coupang` — SKILL.md 내 "⚠️ Akamai Bot Manager 차단 현황" + "브라우저 쿠키 우회 방식" 섹션
- 참조: `references/ls-browser-cookie-workaround.md` (상세 절차)

## 쿠키 파일
- 경로: `C:\Users\kis\.hermes\skills\automation\ls-coupang\references\coupang_cookies_browser.txt`
- Windows 로컬 전용 (Git 미업로드 — 세션 토큰 포함)
- 파일 없으면 사용자에게 `F12 → Console → document.cookie` 요청

## 쿠키 만료 주기
- `WEB-GATEWAY-SESSION`: ~1~2시간 (가장 빈번)
- Akamai 쿠키(`ak_bmsc`, `bm_sv` 등): ~1일
- 장기 쿠키: ~1개월~1년

## 표준 조회 패턴
```bash
DATE=$(date +%Y-%m-%d)
curl -s "https://ls.coupang.com/truckOrderTracking" -G \
  -d "page=0" -d "pageSize=100" \
  -d "orderStartDate=$DATE" -d "orderEndDate=$DATE" \
  -d "locationStart=VF67" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36" \
  -H "Accept: application/json, text/plain, */*" \
  -H "Referer: https://ls.coupang.com/" \
  -b "C:/Users/kis/.hermes/skills/automation/ls-coupang/references/coupang_cookies_browser.txt"
```

## 크로스 디바이스
- Windows: 위 경로 사용
- Linux: `/media/comage/data1/hermes-backup/...` 경로에 동기화 필요 시 Syncthing 사용

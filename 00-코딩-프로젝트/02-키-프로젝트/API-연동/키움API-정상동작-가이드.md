# 키움 API 정상 동작 가이드

> 최종 갱신: 2026-04-22 | PDF 문서 기준

## 현재 상태 (Compiled Truth)

### 계좌
- 계좌번호: 5206921810
- 씨에스윈드(112610): 3주 | 63,800원 | +4.88%
- 현금: 138,188원
- 총자산: 329,186원

### API 인증
- URL: `https://api.kiwoom.com/oauth2/token` (POST, JSON)
- APP_KEY: .env → KIWOOM_APP_KEY
- SECRET_KEY: .env → KIWOOM_SECRET_KEY
- 응답: `token` 필드 (access_token 아님)
- 토큰 만료: 발급 후 약 24시간

### API 호출 규칙
1. 모든 요청: `Content-Type: application/json;charset=UTF-8`
2. 인증 헤더: `Authorization: Bearer {token}`
3. **필수 헤더**: `api-id` (각 API별 고유 ID)
4. 재시도: 3회, 2초 간격

### API ID 매핑
| 기능 | api-id | URL |
|------|--------|-----|
| 계좌번호 | ka00001 | /api/dostk/acnt |
| 일별잔고 | ka01690 | /api/dostk/acnt |
| 주식정보 | ka10001 | /api/dostk/stkinfo |
| 체결정보 | ka10003 | /api/dostk/stkinfo |
| 호가 | ka10004 | /api/dostk/mrkcond |
| 일봉 | ka10005 | /api/dostk/mrkcond |
| 주문 | kt10001 | /api/dostk/order |

---
## 변경 이력 (Timeline)
- 2026-04-22: PDF 문서 기준 전면 수정 (URL, 헤더, 응답필드)
- 2026-04-17: 실거래 성공 (kt10001 주문)
- 2026-03-16: 최초 토큰 발급

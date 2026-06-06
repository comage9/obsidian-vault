# LS 쿠키 CDP 자동 추출 기술 명세서

## 개요
Chrome DevTools Protocol(CDP)의 `Network.getCookies` API를 사용하여 사용자 브라우저 세션에서 ls.coupang.com의 인증 쿠키를 실시간으로 자동 획득하는 모듈입니다.
사용자가 수동으로 cookies.txt를 복사할 필요가 없어집니다.

## 기술 원리

```
크롬(포트 9222) → CDP Network.enable → Network.getCookies(urls=[ls.coupang.com])
                                   → {cookies: [{name, value, domain, ...}]}
                                   → "name1=value1; name2=value2; ..." 문자열 변환
                                   → curl -b "$COOKIE_STR" https://ls.coupang.com/...
```

## 핵심 코드
```python
def get_ls_cookies_from_browser(self):
    self.cmd('Network.enable')
    res = self.cmd('Network.getCookies', {'urls': ['https://ls.coupang.com']})
    cookies = res.get('result', {}).get('cookies', [])
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    return cookie_str
```

## 전제 조건
1. Chrome이 `--remote-debugging-port=9222` 모드로 실행 중
2. 동일 브라우저 세션에서 `https://ls.coupang.com`에 로그인된 상태
3. 쿠키가 만료되지 않음 (WEB-GATEWAY-SESSION 기준 ~1~2시간)

## 사용 흐름
1. `get_ls_cookies_from_browser()` → LS 쿠키 문자열 반환
2. `fetch_ls_vehicles(cookie_str)` → LS API 조회 (VF67 출발, 오늘 날짜)
3. `download_ls_pdf(cookie_str, truckRequestId)` → PDF 다운로드
4. `extract_driver_info_from_pdf(pdf_path)` → 기사명/연락처 추출

## 장점
- 수동 cookies.txt 복사/붙여넣기 불필요
- 실시간 쿠키로 만료 걱정 없음
- 완전 자동화 파이프라인 구축 가능

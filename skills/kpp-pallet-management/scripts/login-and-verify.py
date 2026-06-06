#!/usr/bin/env python3
"""
KPP (WPPS logisall) 로그인 + PBM110MW 도달 검증
- 헤드리스 안전 (Python requests)
- JSON POST 로그인 (form-urlencoded는 415 오류)
- PBM110MW 페이지 + 데이터 조회 (READ ONLY)
"""
import requests
import json
import sys
import os
from datetime import datetime

BASE_URL = "https://wpps.logisall.com"
COOKIE_FILE = "/tmp/wpps_cookies.txt"
USERNAME = "P217273"
PASSWORD = "P217273"

# 0. 쿠키 파일 삭제 (재현)
if os.path.exists(COOKIE_FILE):
    os.remove(COOKIE_FILE)
    print(f"[0] 쿠키 파일 삭제: {COOKIE_FILE}")

# 1. Session 생성
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/login",
})

# 2. GET /login (JSESSIONID 세션 시작)
print(f"[1] GET {BASE_URL}/login (세션 시작)...")
r = session.get(f"{BASE_URL}/login", timeout=15)
print(f"    HTTP {r.status_code}, {len(r.text)} bytes")
jsession = session.cookies.get("JSESSIONID")
print(f"    JSESSIONID: {jsession[:20] if jsession else '없음'}...")

# 3. JSON POST /login.do
print(f"[2] JSON POST {BASE_URL}/login.do...")
session.headers["Content-Type"] = "application/json"
r = session.post(f"{BASE_URL}/login.do",
                  data=json.dumps({"loginId": USERNAME, "password": PASSWORD}),
                  timeout=15)
print(f"    HTTP {r.status_code}, {r.headers.get('Content-Type', '?')}")
print(f"    응답: {r.text[:200]}")

# 4. 응답 파싱
try:
    data = r.json()
    flg = data.get("flg")
    redirect = data.get("redirectUrl")
    print(f"    flg={flg}, redirectUrl={redirect}")
    if flg != "Y":
        print(f"[!] 로그인 실패: {data}")
        sys.exit(1)
except Exception as e:
    print(f"[!] JSON 파싱 실패: {e}")
    print(r.text[:500])
    sys.exit(1)

# 5. 리다이렉트 따라가기
print(f"[3] GET {BASE_URL}{redirect} (로그인 후 페이지)...")
session.headers.pop("Content-Type", None)
r = session.get(f"{BASE_URL}{redirect}", timeout=15)
print(f"    HTTP {r.status_code}, {len(r.text)} bytes")

# 6. PBM110MW 페이지 도달
print(f"[4] GET {BASE_URL}/ps/PBM110MW...")
r = session.get(f"{BASE_URL}/ps/PBM110MW", timeout=15)
print(f"    HTTP {r.status_code}, {len(r.text)} bytes, URL: {r.url}")

# 7. PBM110MW.do 데이터 조회 (READ ONLY)
print(f"[5] GET PBM110MW.do (오늘 날짜)...")
session.headers["Accept"] = "application/json, text/plain, */*"
TODAY = datetime.now().strftime("%Y%m%d")
r = session.get(f"{BASE_URL}/ps/PBM110MW.do", params={
    "REQ_DAT_FR": TODAY,
    "REQ_DAT_TO": TODAY,
    "STC_CST_COD": "217273",
    "REQ_CST_COD": "217273",
}, timeout=15)
print(f"    HTTP {r.status_code}, {r.headers.get('Content-Type', '?')}, {len(r.text)} bytes")
try:
    data = r.json()
    if isinstance(data, list):
        print(f"    [조회 성공] {len(data)}건")
        for item in data[:3]:
            print(f"      - {item.get('UNLOAD_REQ_DAT')} {item.get('REQ_TYP')} {item.get('PRD_NAM')} {item.get('REQ_QTY')}개")
    else:
        print(f"    응답: {json.dumps(data, ensure_ascii=False)[:500]}")
except Exception as e:
    print(f"    [!] 파싱 실패: {e}")
    print(f"    응답 일부: {r.text[:300]}")

# 8. 최종
print(f"\n=== 최종 ===")
print(f"JSESSIONID: {session.cookies.get('JSESSIONID', '?')[:20]}...")
print(f"쿠키 도메인: {sorted(set(c.domain for c in session.cookies))}")
print(f"쿠키 개수: {len(session.cookies)}")

#!/usr/bin/env python3
"""
LS 쿠팡 로그인 + API 검증 스크립트 (재현 가능, 정적 재실행)
- /tmp/coupang_cookies.txt 삭제 → OAuth2 → Keycloak 로그인 → API 50건 조회
- 2026-06-02 실측 기반. python-auth-flow.md 패턴 그대로.
- 사용: /opt/hermes/hermes-agent/venv/bin/python /opt/hermes/skills/automation/ls-coupang/scripts/ls-login-test.py
"""
import requests
import re
import json
import os
import http.cookiejar
import sys
from datetime import datetime

COOKIE_FILE = "/tmp/coupang_cookies.txt"
BASE_URL = "https://ls.coupang.com"
TODAY = datetime.now().strftime("%Y-%m-%d")

# 0. 쿠키 삭제 (있으면)
if os.path.exists(COOKIE_FILE):
    os.remove(COOKIE_FILE)
    print(f"[0] 쿠키 파일 삭제: {COOKIE_FILE}")

# 1. Session (MozillaCookieJar 필수 — 아니면 save() AttributeError)
session = requests.Session()
session.cookies = http.cookiejar.MozillaCookieJar(COOKIE_FILE)
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
})

# 2. OAuth2 → Keycloak (GET with allow_redirects=True)
api_url = f"{BASE_URL}/order?page=0&pageSize=50&statuses=SUBMITTED,CONFIRMED,CANCELED,BACK&locationStart=VF67_H&dateFrom={TODAY}&dateTo={TODAY}"
print(f"[1] GET {api_url[:90]}...")
r = session.get(api_url, allow_redirects=True, timeout=30)
print(f"    → {r.status_code} {r.url[:90]} ({len(r.text)} bytes)")

# 3. form action 추출
match = re.search(r'<form[^>]*action="([^"]+)"', r.text)
if not match:
    print("[!] form action 못 찾음 — 로그인 페이지 변경 가능성")
    sys.exit(1)
form_action = match.group(1).replace('&amp;', '&')
print(f"[2] form: {form_action[:90]}...")

# 4. POST 로그인 (같은 session, 즉시 실행 — session_code 일회성)
print(f"[3] POST 로그인...")
r2 = session.post(form_action, data={
    "username": "mokicom",
    "password": "bonohouse0309^^",
    "credentialId": "",
    "login": "로그인",
}, allow_redirects=True, timeout=30)
print(f"    → {r2.status_code} {r2.url[:90]} ({len(r2.text)} bytes)")

# 5. 쿠키 검증
auth_cookies = sorted([c.name for c in session.cookies if c.name in ("AUTH_SESSION_ID", "KC_RESTART", "LS_MAIN_HTTP", "LS_LOGIN_RTOKEN")])
abck = next((c.value[:30] + "..." for c in session.cookies if c.name == "_abck"), None)
print(f"[4] 인증 쿠키: {auth_cookies}")
print(f"    _abck: {abck}")

# 6. cookies.txt 저장 (MozillaCookieJar는 ignore_discard/expires 필요)
session.cookies.save(ignore_discard=True, ignore_expires=True)
print(f"[5] 쿠키 저장: {COOKIE_FILE} ({os.path.getsize(COOKIE_FILE)} bytes)")

# 7. /order API 호출 (세션 유효성 검증)
print(f"[6] /order API 호출...")
r3 = session.get(f"{BASE_URL}/order", params={
    "page": 0, "pageSize": 50,
    "statuses": "SUBMITTED,CONFIRMED,CANCELED,BACK",
    "locationStart": "VF67_H",
    "dateFrom": TODAY, "dateTo": TODAY,
}, headers={"Accept": "application/json", "Referer": f"{BASE_URL}/"}, timeout=30)
print(f"    → HTTP {r3.status_code}, {len(r3.text)} bytes, {r3.headers.get('Content-Type', '?')}")

if r3.status_code == 200 and "json" in r3.headers.get("Content-Type", ""):
    data = r3.json()
    if data.get("code") == 200:
        items = data.get("data", {}).get("content", [])
        print(f"    [성공] {len(items)}건 조회")
        for it in items[:5]:
            tid = it.get("truckOrderTemplateId")
            od = it.get("orderDate")
            st = it.get("status")
            fr = it.get("from", {}).get("code")
            to = it.get("dest", {}).get("code")
            print(f"      - 템플릿={tid} {fr}→{to} {od} {st}")
    else:
        print(f"    [API 에러] {data.get('code')}: {data.get('message')}")
else:
    print(f"    [실패] 응답:")
    print(r3.text[:300])

print()
print("=== 최종 ===")
print(f"오늘: {TODAY}")
print(f"쿠키: {os.path.getsize(COOKIE_FILE) if os.path.exists(COOKIE_FILE) else 0} bytes")

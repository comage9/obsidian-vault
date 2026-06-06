#!/usr/bin/env python3
"""PBM140MW(출하통보) + PBM110MW(납품/반납요청) 7가지 조건 교차 조회"""
import requests, json, sys
from datetime import datetime, timedelta
from collections import Counter

BASE = "https://wpps.logisall.com"
s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": BASE,
    "Referer": f"{BASE}/login",
})

# 로그인
s.get(f"{BASE}/login", timeout=15)
s.headers["Content-Type"] = "application/json"
r = s.post(f"{BASE}/login.do",
           data=json.dumps({"loginType":"IDPW","loginId":"P217273","password":"P217273"}),
           timeout=15)
data = r.json()
if data.get("flg") != "Y":
    print(f"[!] 로그인 실패: {data}"); sys.exit(1)
s.headers.pop("Content-Type", None)
s.get(f"{BASE}{data['redirectUrl']}", timeout=15)

# === PBM110MW (납품/반납요청) — GET ===
print("=" * 70)
print("[A] PBM110MW (납품/반납요청) — REQ_DAT 기준")
print("=" * 70)
s.get(f"{BASE}/ps/PBM110MW", timeout=15)
s.headers["Accept"] = "application/json, text/plain, */*"

queries_110 = [
    ("A1) 6/1~6/3 REQ_DAT", {"REQ_DAT_FR": "20260601", "REQ_DAT_TO": "20260603",
                              "STC_CST_COD": "217273", "REQ_CST_COD": "217273"}),
    ("A2) 6/1~6/3 UNLOAD_REQ_DAT", {"UNLOAD_REQ_DAT_FR": "20260601", "UNLOAD_REQ_DAT_TO": "20260603",
                                     "STC_CST_COD": "217273", "REQ_CST_COD": "217273"}),
    ("A3) 5/15~6/3 REQ_DAT 넓게", {"REQ_DAT_FR": "20260515", "REQ_DAT_TO": "20260603",
                                    "STC_CST_COD": "217273", "REQ_CST_COD": "217273"}),
    ("A4) CST_COD만 (날짜 없이)", {"STC_CST_COD": "217273", "REQ_CST_COD": "217273"}),
]
for label, params in queries_110:
    r = s.get(f"{BASE}/ps/PBM110MW.do", params=params, timeout=15)
    try:
        data = r.json()
        rows = data if isinstance(data, list) else data.get('rows', data.get('data', []))
    except:
        print(f"{label}: HTTP {r.status_code}, JSON 아님")
        continue
    print(f"{label}: HTTP {r.status_code}, {len(rows)}건")
    if rows:
        for row in rows[:10]:
            print(f"   {row.get('REQ_DAT')}/{row.get('UNLOAD_REQ_DAT')} "
                  f"REQ_TYP={row.get('REQ_TYP')} PRD={row.get('PRD_NAM')} "
                  f"QTY={row.get('REQ_QTY')} ARV={row.get('ARV_CST_NAM')} "
                  f"ETC={str(row.get('ETC_DESC',''))[:20]}")

# === PBM140MW (출하통보) — POST ===
print("\n" + "=" * 70)
print("[B] PBM140MW (출하통보) — POST search")
print("=" * 70)
s.get(f"{BASE}/ps/PBM140MW", timeout=15)

queries_140 = [
    ("B1) DLV_DAT 6/1~6/3", {"dfrDat": "20260601", "dtoDat": "20260603", "page": 1, "rows": 50}),
    ("B2) DLV_DAT 6/2만", {"dfrDat": "20260602", "dtoDat": "20260602", "page": 1, "rows": 50}),
    ("B3) DLV_DAT 6/3만", {"dfrDat": "20260603", "dtoDat": "20260603", "page": 1, "rows": 50}),
    ("B4) ARV_DAT 6/1~6/3", {"dfrArvDat": "20260601", "dtoArvDat": "20260603", "page": 1, "rows": 50}),
    ("B5) 5/15~6/3 DLV_DAT", {"dfrDat": "20260515", "dtoDat": "20260603", "page": 1, "rows": 100}),
    ("B6) 빈 파라미터", {"page": 1, "rows": 50}),
]
for label, payload in queries_140:
    r = s.post(f"{BASE}/ps/PBM140MW.search", json=payload, timeout=15)
    try:
        data = r.json()
        rows = data if isinstance(data, list) else data.get('rows', data.get('data', []))
    except:
        print(f"{label}: HTTP {r.status_code}, JSON 아님, body[:200]={r.text[:200]}")
        continue
    print(f"{label}: HTTP {r.status_code}, {len(rows)}건")
    if rows:
        for row in rows[:10]:
            print(f"   dlv={row.get('dlv_dat')}/arv={row.get('arv_dat')} "
                  f"web_desc={row.get('web_desc')} prd={row.get('prd_cod')} "
                  f"qty={row.get('dlv_qty')} cst={row.get('arv_cst_nam', row.get('cst_nam',''))} "
                  f"car={row.get('car_no','')} kpp={row.get('kpp_confm_flg','')}")

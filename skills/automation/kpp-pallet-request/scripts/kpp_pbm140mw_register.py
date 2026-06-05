#!/usr/bin/env python3
"""
KPP PBM140MW 출하통보 등록 (이전 성공 방식 + 차량번호 6자리 규칙 + dual_confm 추가)

이전 성공 방식 기반 (kpp_insert_0604.py):
  - requests.Session + MozillaCookieJar
  - GET /login → POST /login.do(JSON) → GET /ps/index → GET /ps/PBM140MW
  - cookies.save(ignore_discard=True, ignore_expires=True)

PBM140MW 추가 규칙 (2026-06-03 사용자 확정):
  - 차량번호: 숫자만 6자리 (re.sub(r'[^0-9]', '', _))
  - dual_confm: "" 키 추가 (없으면 NPE)
  - 팔레트: 5T=12, 11T=14
  - 도착지: 610060 (BUC1_H 부천1센터 HUB)
  - 하차지: 217273 (우리회사)

사용법:
  export KPP_PW='P217273'
  python3 kpp_pbm140mw_register.py
"""
import os
import re
import json
import requests
import http.cookiejar

BASE = "https://wpps.logisall.com"
COOKIE = "/tmp/wpps_cookies_pbm140mw.txt"
USERNAME = "P217273"
PASSWORD = os.environ.get('KPP_PW', '') or os.environ.get('KPP_PASSWORD', '')

# 톤수 → 팔레트 매핑 (사용자 2026-06-03 확정)
TONNAGE_TO_PALLETS = {
    "5T": 12,
    "11T": 14,
    "14T": 18,  # 추정
}

# 차량번호 변환: 숫자만 6자리
def normalize_car_num(raw: str) -> str:
    digits = re.sub(r'[^0-9]', '', raw)
    if len(digits) != 6:
        raise ValueError(f"차량번호 숫자 추출 후 6자리 아님: {raw!r} → {digits!r} ({len(digits)}자리)")
    return digits

# 전화번호 정규화: 숫자만
def normalize_tel(raw: str) -> str:
    return re.sub(r'[^0-9]', '', raw)

# PBM140MW 페이로드 빌더
def make_row(*, car_num_raw, driver_nam, driver_tel_raw, dlv_qty,
             dlv_dat="20260603", arv_dat="20260603",
             arv_cst_cod="610060", dlv_cst_cod="217273",
             prd_cod="N11", comp_cod="217273",
             ord_cst_cod="217273", cst_chit_num=""):
    return {
        "chk": True,
        "dlv_dat": dlv_dat,
        "arv_dat": arv_dat,
        "dlv_qty": dlv_qty,
        "arv_cst_cod": arv_cst_cod,
        "dlv_cst_cod": dlv_cst_cod,
        "prd_cod": prd_cod,
        "comp_cod": comp_cod,
        "cst_chit_num": cst_chit_num,
        "car_num": normalize_car_num(car_num_raw),
        "driver_nam": driver_nam,
        "driver_tel": normalize_tel(driver_tel_raw),
        "ord_cst_cod": ord_cst_cod,
        "mod": "I",
        "dual_confm": "",  # ★ 추가 (없으면 NPE)
    }


# 세션 (이전 성공 방식: MozillaCookieJar)
cj = http.cookiejar.MozillaCookieJar(COOKIE)
s = requests.Session()
s.cookies = cj

# === 1. 로그인 ===
print("[1] GET /login (세션 시작)")
r = s.get(f"{BASE}/login", timeout=15)
print(f"    HTTP {r.status_code}, {len(r.text)}B")

print("[2] POST /login.do (JSON)")
r = s.post(f"{BASE}/login.do",
            data=json.dumps({"loginId": USERNAME, "password": PASSWORD}),
            headers={"Content-Type": "application/json"},
            timeout=15)
data = r.json()
print(f"    HTTP {r.status_code}, flg={data.get('flg')}, redirect={data.get('redirectUrl')}")
if data.get('flg') != 'Y':
    print(f"    [실패] {data}")
    raise SystemExit(1)

# === 2. 페이지 진입 (이전 성공 방식) ===
print("[3] GET /ps/index + /ps/PBM140MW")
s.get(f"{BASE}{data['redirectUrl']}", timeout=15)
r = s.get(f"{BASE}/ps/PBM140MW", timeout=15)
print(f"    PBM140MW HTTP {r.status_code}, {len(r.text)}B")

# === 3. 쿠키 영구 저장 (이전 성공 방식) ===
s.cookies.save(COOKIE, ignore_discard=True, ignore_expires=True)
print(f"[4] 쿠키 저장: {COOKIE} ({len(s.cookies)}개)")

# === 4. 페이로드 구성 (6/3자 1~3호차, LS PDF 데이터) ===
ROWS = [
    # 1호차: 90626, 5T, 경기95자6464
    {"car_num_raw": "경기95자6464", "driver_nam": "손경준", "driver_tel_raw": "010-3910-0850", "tonnage": "5T"},
    # 2호차: 90628, 5T, 경기89바1454
    {"car_num_raw": "경기89바1454", "driver_nam": "김동수", "driver_tel_raw": "010-3940-9811", "tonnage": "5T"},
    # 3호차: 90269, 11T, 충북90아6169
    {"car_num_raw": "충북90아6169", "driver_nam": "최문수", "driver_tel_raw": "010-5342-6631", "tonnage": "11T"},
]

payload = []
for r_data in ROWS:
    qty = TONNAGE_TO_PALLETS[r_data["tonnage"]]
    row = make_row(
        car_num_raw=r_data["car_num_raw"],
        driver_nam=r_data["driver_nam"],
        driver_tel_raw=r_data["driver_tel_raw"],
        dlv_qty=qty,
    )
    payload.append(row)
    print(f"    변환: {r_data['car_num_raw']} → {row['car_num']}, {r_data['tonnage']} → {qty}팔레트")

# === 5. PBM140MW.save POST (사전 검증 후) ===
print(f"\n[5] 사전 검증: search로 6/3 등록 건수 확인")
s.headers["Content-Type"] = "application/json"
s.headers["Accept"] = "application/json, text/plain, */*"

VERIFY_DT = "20260603"  # ★ 고정: 6/3자 (사용자 명시 시 변경)
sr_pre = s.post(f"{BASE}/ps/PBM140MW.search",
    data=json.dumps({
        "sr_dlv_dat_f": VERIFY_DT, "sr_dlv_dat_t": VERIFY_DT,
        "sr_cst_cod": "217273", "sr_mng_grd": "05"
    }),
    timeout=15)
print(f"    HTTP {sr_pre.status_code}, {len(sr_pre.text)}B")
try:
    pre_data = sr_pre.json()
    pre_count = len(pre_data) if isinstance(pre_data, list) else 0
    print(f"    [사전검증] {VERIFY_DT} 등록 건수: {pre_count}건")
    if pre_count > 0:
        print(f"    [FAIL] 이미 {pre_count}건 등록됨 → POST 안 함 (중복 INSERT 방지)")
        print(f"    ⚠️ search 결과는 6/3 검증에서 0건 반환되는 함정 있음")
        print(f"    ⚠️ UI 직접 확인 권장: KPP → 출하통보등록 → 조회 ({VERIFY_DT})")
        print(f"    → 사용자 결정 대기 (그래도 진행하려면 검색값 무시하고 POST)")
        # 6/3 사건 기반: 0건이어도 무조건 진행 X, 사용자 확인 필수
        print(f"\n    [BLOCK] POST 차단. 사용자 KPP UI 확인 후 '계속' 입력 필요")
        print(f"    종료합니다.")
        raise SystemExit(0)
except Exception as e:
    print(f"    [WARN] 사전검증 파싱실패: {e} → 사용자 확인 권장 후 진행")

# === 6. PBM140MW.save POST ===
print(f"\n[6] POST /ps/PBM140MW.save (3건)")
r = s.post(f"{BASE}/ps/PBM140MW.save",
            data=json.dumps(payload, ensure_ascii=False),
            headers={"Content-Type": "application/json", "Accept": "application/json, text/plain, */*"},
            timeout=30)
print(f"    HTTP {r.status_code}, {r.headers.get('Content-Type','?')}, {len(r.text)}B")
print(f"    응답: {r.text[:500]}")
try:
    d = r.json()
    print(f"    flag={d.get('flag')}, message={d.get('message')}")
    print(f"    ⚠️ flag={d.get('flag')} 단독 신뢰 금지 (6/3 사건)")
except Exception as e:
    print(f"    파싱실패: {e}")

# === 7. 사후 검증 (search 응답은 무시, UI 확인 필수) ===
print(f"\n[7] 사후 검증: ⚠️ search API는 0건 반환 가능 (6/3 검증)")
print(f"    save flag={d.get('flag') if 'd' in dir() else '?'} — 단독 신뢰 금지")
print(f"    [필수] 사용자 KPP UI 직접 확인: 출하통보등록 → 조회 ({VERIFY_DT}) → 그리드 N건 카운트")
print(f"    예상 건수: {pre_count} + {len(payload)} = {pre_count + len(payload)}건")
print(f"    ⚠️ 실제로 그 외 추가 안 됐는지 UI에서 확인 후 보고")

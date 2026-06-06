#!/usr/bin/env python3
"""KPP 로그인 + PBM140MW/PBM110MW search 통합 검증 (2026-06-03)

사용법:
  python3 kpp-verify-search.py [날짜]   # 기본: 오늘 (KST)

기능:
  1. JSON POST 로그인 (loginType/loginId/password 3필드)
  2. /ps/index 세션 검증
  3. PBM140MW.search — 5가지 조건 교차 조회 (DLV_DAT/ARV_DAT/DFR-DTO/빈값/어제)
  4. PBM110MW.do — 1가지 조회
  5. 결과 list/dict 타입 자동 처리
  6. 차량번호/운전자별 3호차 매칭 (선택)

출력:
  - stdout: 사람 읽기용 요약 테이블
  - /tmp/pbm140mw_{날짜}.json: 전체 raw 응답
  - exit 0: 1건 이상 / exit 1: 모두 0건 (사용자 확인 필요)
"""
import sys
import json
import requests
from datetime import datetime, timedelta
from http.cookiejar import MozillaCookieJar

# ===== 설정 (메모리/위키 기반) =====
BASE = "https://wpps.logisall.net"
USER_ID = "P217273"
USER_PWD = "P217273"
COOKIE_PATH = "/tmp/kpp_cookies.txt"

# KST 오늘 (서버 시간대가 KST라고 가정; 어긋나면 1일 조정)
KST = datetime.utcnow() + timedelta(hours=9)
TODAY = KST.strftime("%Y%m%d")
YESTERDAY = (KST - timedelta(days=1)).strftime("%Y%m%d")
TARGET = sys.argv[1] if len(sys.argv) > 1 else TODAY


def login(session):
    """KPP JSON POST 로그인 (loginType+loginId+password 3필드)"""
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"{BASE}/login",
    })
    session.get(f"{BASE}/login", timeout=15)
    r = session.post(
        f"{BASE}/login.do",
        json={"loginType": "IDPW", "loginId": USER_ID, "password": USER_PWD},
        timeout=15,
    )
    d = r.json()
    ok = d.get("flg") == "Y"
    print(f"[LOGIN] {r.status_code} flg={d.get('flg')} redirect={d.get('redirectUrl')}")
    return ok


def verify_session(session):
    """GET /ps/index → 200 이면 세션 유효"""
    r = session.get(f"{BASE}/ps/index", allow_redirects=False, timeout=10)
    print(f"[SESSION] /ps/index {r.status_code} (valid={r.status_code == 200})")
    return r.status_code == 200


def parse_rows(raw):
    """PBM140MW.search 응답은 list 또는 dict — 둘 다 처리"""
    if isinstance(raw, list):
        return raw, len(raw)
    if isinstance(raw, dict):
        rows = raw.get("rows", raw.get("data", []))
        return rows, raw.get("total", len(rows))
    return [], 0


def search_pbm140(session, label, payload):
    """PBM140MW.search — 다양한 조건으로 교차 조회"""
    r = session.post(f"{BASE}/ps/PBM140MW.search", json=payload, timeout=15)
    raw = r.json()
    rows, total = parse_rows(raw)
    print(f"  [{label}] {r.status_code} rows={len(rows)} total={total}")
    if rows:
        for row in rows[:5]:
            car = row.get("CAR_NUM", "")
            dlv = row.get("DLV_DAT", "")
            arv = row.get("ARV_DAT", "")
            drv = row.get("DRV_NAM", "")
            chit = row.get("CST_CHIT_NUM", "")
            web_desc = row.get("WEB_DESC", "")
            kpp = row.get("KPP_CONFM_FLG", "")
            print(f"    DLV={dlv} ARV={arv} CAR={car} DRV={drv} CHIT={chit} web_desc={web_desc} KPP={kpp}")
    return rows, total, raw


def search_pbm110(session, label, params):
    """PBM110MW.do GET 조회"""
    r = session.get(f"{BASE}/ps/PBM110MW.do", params=params, timeout=15)
    try:
        raw = r.json()
        rows, total = parse_rows(raw)
        print(f"  [{label}] {r.status_code} rows={len(rows)}")
        return rows, total, raw
    except Exception as e:
        print(f"  [{label}] {r.status_code} (not JSON: {e})")
        return [], 0, None


def save_cookies(session):
    """MozillaCookieJar로 쿠키 저장"""
    jar = MozillaCookieJar(COOKIE_PATH)
    for c in session.cookies:
        jar.set_cookie(c)
    jar.save(ignore_discard=True, ignore_expires=True)


def main():
    session = requests.Session()
    # 기존 쿠키 로드 시도
    jar = MozillaCookieJar(COOKIE_PATH)
    try:
        jar.load(ignore_discard=True, ignore_expires=True)
        session.cookies = jar
        print(f"[COOKIE] 로드 {len(jar)}개")
    except FileNotFoundError:
        pass

    if not login(session):
        print("[FAIL] 로그인 실패")
        return 1
    save_cookies(session)
    if not verify_session(session):
        print("[FAIL] 세션 무효")
        return 1

    print(f"\n=== PBM140MW.search 교차 조회 (대상: {TARGET}) ===\n")
    queries = [
        (f"{TARGET} DLV_DAT", {
            "dfrDat": TARGET, "dtoDat": TARGET,
            "cstCod": "", "carNum": "", "dpsCd": "", "dlvCstCod": "",
            "kppConfmFlg": "", "arvDat": "", "dlvDat": TARGET,
            "errTyp": "", "page": 1, "rows": 50,
        }),
        (f"{TARGET} DFR-DTO", {
            "dfrDat": TARGET, "dtoDat": TARGET,
            "cstCod": "", "carNum": "", "dpsCd": "", "dlvCstCod": "",
            "kppConfmFlg": "", "arvDat": "", "dlvDat": "",
            "errTyp": "", "page": 1, "rows": 50,
        }),
        (f"{YESTERDAY}~{TARGET} 전체", {
            "dfrDat": YESTERDAY, "dtoDat": TARGET,
            "cstCod": "", "carNum": "", "dpsCd": "", "dlvCstCod": "",
            "kppConfmFlg": "", "arvDat": "", "dlvDat": "",
            "errTyp": "", "page": 1, "rows": 50,
        }),
        (f"{TARGET} ARV_DAT", {
            "dfrDat": "", "dtoDat": "",
            "cstCod": "", "carNum": "", "dpsCd": "", "dlvCstCod": "",
            "kppConfmFlg": "", "arvDat": TARGET, "dlvDat": "",
            "errTyp": "", "page": 1, "rows": 50,
        }),
        (f"빈 조건 (전체)", {
            "dfrDat": "", "dtoDat": "",
            "cstCod": "", "carNum": "", "dpsCd": "", "dlvCstCod": "",
            "kppConfmFlg": "", "arvDat": "", "dlvDat": "",
            "errTyp": "", "page": 1, "rows": 50,
        }),
    ]

    all_results = []
    for label, payload in queries:
        rows, total, raw = search_pbm140(session, label, payload)
        all_results.append({"label": label, "rows": rows, "total": total})
        if raw is not None:
            with open(f"/tmp/pbm140mw_{TARGET}_{label.split()[0]}.json", "w", encoding="utf-8") as f:
                json.dump(raw, f, ensure_ascii=False, indent=2)

    # 3호차 매칭 (89자3822 or 유원석)
    print(f"\n=== 3호차 매칭 (89자3822/유원석) ===")
    found = False
    for r in all_results:
        for row in r["rows"]:
            if "3822" in str(row.get("CAR_NUM", "")) or "유원석" in str(row.get("DRV_NAM", "")):
                found = True
                print(f"  ★ {r['label']}: CAR={row.get('CAR_NUM')} DRV={row.get('DRV_NAM')} CHIT={row.get('CST_CHIT_NUM')}")
    if not found:
        print("  3호차 행 없음")

    # 종합
    total_rows = sum(r["total"] for r in all_results)
    print(f"\n=== 종합: 5개 조건 합계 {total_rows}건 ===")
    if total_rows == 0:
        print("\n⚠️ 0건 — 4가지 가능성:")
        print("  1) 다른 사용자/에이전트가 데이터 삭제")
        print("  2) 자정 자동 만료")
        print("  3) 계정 권한 차이")
        print("  4) 이전 보고서 오류")
        print("  → 사용자에게 정직 보고 후 결정 대기 (자동 등록 금지)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

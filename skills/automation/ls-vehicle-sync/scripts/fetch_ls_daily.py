#!/usr/bin/env python3
"""
LS 일일 차량 정보 추출 (Tracking API + PDF 다운로드)
- Tracking API로 차량번호/톤수/업체 추출
- PDF 다운로드로 기사/연락처/운행일자 추출
- KPP PBM140MW 등록에 필요한 모든 정보 자동 확보
"""
import os
import re
import sys
import json
import subprocess
import requests
import psycopg2
from http.cookiejar import MozillaCookieJar
from datetime import datetime, date

# ============ 설정 ============
LS_COOKIE_FILE = '/tmp/coupang_cookies.txt'
DB_DSN = "host=127.0.0.1 dbname=ls_vehicle user=ls_user"
LS_BASE = "https://ls.coupang.com"
TEMPLATE_TONNAGE = {
    '90626': '5T',  # 2026-06-03 사용자 확인 (예전엔 11T였음)
    '90628': '5T',
    '90269': '11T',
    '101740': '5T',
}


def ls_login():
    """LS 자동 로그인 (쿠키 만료 시)"""
    session = requests.Session()
    session.cookies = MozillaCookieJar(LS_COOKIE_FILE)
    try:
        session.cookies.load(ignore_discard=True, ignore_expires=True)
    except FileNotFoundError:
        pass

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    })

    url = f"{LS_BASE}/order?statuses=SUBMITTED,CONFIRMED,CANCELED,BACK&locationStart=VF67_H&page=0&pageSize=50"
    r = session.get(url, allow_redirects=True)
    if 'xauth.coupang.com' not in r.url:
        return session  # 이미 로그인

    match = re.search(r'<form[^>]*action="([^"]+)"', r.text)
    if not match:
        raise RuntimeError("LS login form not found")
    form_action = match.group(1).replace('&amp;', '&')

    session.post(form_action, data={
        "username": "mokicom",
        "password": "bonohouse0309^^",
        "credentialId": "",
        "login": "로그인",
    }, allow_redirects=True)
    session.cookies.save(ignore_discard=True, ignore_expires=True)
    return session


def fetch_tracking(session, target_date):
    """LS Tracking API로 특정 날짜 오더 조회"""
    params = {
        "page": 0, "pageSize": 50,
        "statuses": "SUBMITTED,CONFIRMED,CANCELED,BACK",
        "locationStart": "VF67_H",
        "orderStartDate": target_date,
        "orderEndDate": target_date,
    }
    r = session.get(f"{LS_BASE}/truckOrderTracking", params=params, headers={
        "Accept": "application/json",
        "Referer": f"{LS_BASE}/",
    })
    r.raise_for_status()
    return r.json().get('data', {}).get('content', [])


def download_pdf(session, truck_request_id, locale='ko_KR'):
    """LS PDF 다운로드 (운행확인서)"""
    url = f"{LS_BASE}/linehaul/slip/generate"
    r = session.get(url, params={
        'truckRequestId': truck_request_id,
        'locale': locale,
    }, headers={
        "Accept": "application/json,application/pdf",
        "Referer": f"{LS_BASE}/",
    })
    r.raise_for_status()
    if r.headers.get('Content-Type', '').startswith('application/pdf'):
        return r.content
    return None


def parse_pdf(pdf_bytes):
    """PDF 바이트 → dict (운행일자, 차량번호, 트럭바코드, 성함, 연락처)"""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(pdf_bytes)
        pdf_path = f.name

    try:
        txt = subprocess.run(
            ['pdftotext', '-layout', pdf_path, '-'],
            capture_output=True, text=True
        ).stdout

        # 운행일자
        op_date = re.search(r'운행일자\s+(\d{4}-\d{2}-\d{2})', txt)
        op_date = op_date.group(1) if op_date else None

        # 차량번호
        veh = re.search(r'차량번호\s+(\S+)', txt)
        veh = veh.group(1).strip() if veh else None

        # 트럭바코드
        barcode = re.search(r'트럭바코드\s*\n?\s*(\d+)', txt)
        if not barcode:
            # 차량번호 다음 줄
            barcode = re.search(r'차량번호\s+\S+\s+(\d+)', txt)
        barcode = barcode.group(1) if barcode else None

        # 성함
        name = re.search(r'성함\s+([가-힣]+)\s+연락처', txt)
        name = name.group(1).strip() if name else None

        # 연락처
        phone = None
        full = re.search(r'010-(\d{4})-(\d{4})', txt)
        if full:
            phone = full.group(0)
        else:
            partial = re.search(r'010-(\d{3,4})-', txt)
            if partial:
                prefix = partial.group(0)
                after = txt[partial.end():]
                nxt = re.search(r'(\d{4})', after)
                if nxt:
                    phone = prefix + nxt.group(1)

        return {
            'op_date': op_date,
            'vehicle_num': veh,
            'truck_barcode': barcode,
            'driver_name': name,
            'driver_phone': phone,
        }
    finally:
        os.unlink(pdf_path)


def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else date.today().strftime('%Y-%m-%d')
    print(f"[1] LS 자동 로그인...")
    session = ls_login()
    print(f"    쿠키 {len(session.cookies)}개")

    print(f"\n[2] Tracking API 조회 ({target_date})...")
    orders = fetch_tracking(session, target_date)
    # orderDate 클라이언트 필터
    orders = [o for o in orders if o.get('orderDate') == target_date]
    print(f"    {len(orders)}건")
    for o in orders:
        tid = o.get('truckOrderTemplateId') or '?'
        rid = o.get('truckRequestId')
        st = o.get('status')
        ti = o.get('truckInfo') or {}
        tt = o.get('truckType') or {}
        print(f"    {tid} | {st} | {ti.get('plateNumber')} | {tt.get('name')} | {o.get('truckVendor', {}).get('name')}")

    print(f"\n[3] PDF 다운로드 + 파싱...")
    results = []
    for o in orders:
        rid = o.get('truckRequestId')
        if not rid:
            continue
        pdf_bytes = download_pdf(session, rid)
        if not pdf_bytes:
            print(f"    {rid}: PDF 다운로드 실패")
            continue
        info = parse_pdf(pdf_bytes)
        info['truck_request_id'] = rid
        info['template_id'] = o.get('truckOrderTemplateId')
        info['tonnage'] = (o.get('truckType') or {}).get('name') or TEMPLATE_TONNAGE.get(str(o.get('truckOrderTemplateId')), '?')
        info['truck_vendor'] = (o.get('truckVendor') or {}).get('name', '?')
        info['request_time'] = o.get('requestTime')
        info['status'] = o.get('status')
        results.append(info)
        print(f"    {rid}: PDF size={len(pdf_bytes)} B | {info.get('vehicle_num')} | {info.get('driver_name')}/{info.get('driver_phone')} | {info.get('op_date')}")

    # DB 저장
    print(f"\n[4] DB 저장...")
    conn = psycopg2.connect(DB_DSN)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            for info in results:
                # 1) vehicles UPSERT
                if info.get('vehicle_num'):
                    cur.execute("""
                        INSERT INTO vehicles (truck_num, template_id, tonnage)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (truck_num) DO UPDATE
                            SET template_id = COALESCE(EXCLUDED.template_id, vehicles.template_id),
                                tonnage = COALESCE(EXCLUDED.tonnage, vehicles.tonnage),
                                updated_at = NOW()
                    """, (info['vehicle_num'], info.get('template_id'), info.get('tonnage')))

                # 2) drivers UPSERT
                if info.get('driver_name') and info.get('driver_phone'):
                    cur.execute("""
                        INSERT INTO drivers (driver_name, driver_phone, is_temporary)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (driver_name, driver_phone) DO UPDATE
                            SET updated_at = NOW()
                    """, (info['driver_name'].strip(), info['driver_phone'].strip(), False))

                # 3) snapshot UPSERT
                if info.get('op_date') and info.get('template_id'):
                    cur.execute("""
                        INSERT INTO ls_vehicle_snapshot
                            (order_date, template_id, truck_num, driver_name, driver_phone, order_status, request_time, truck_request_id, raw_data)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (order_date, template_id) DO UPDATE
                            SET truck_num = COALESCE(EXCLUDED.truck_num, ls_vehicle_snapshot.truck_num),
                                driver_name = COALESCE(EXCLUDED.driver_name, ls_vehicle_snapshot.driver_name),
                                driver_phone = COALESCE(EXCLUDED.driver_phone, ls_vehicle_snapshot.driver_phone),
                                order_status = EXCLUDED.order_status,
                                request_time = EXCLUDED.request_time,
                                truck_request_id = EXCLUDED.truck_request_id,
                                fetched_at = NOW()
                    """, (info['op_date'], info['template_id'], info.get('vehicle_num'),
                          info.get('driver_name'), info.get('driver_phone'),
                          info.get('status'), info.get('request_time'), info.get('truck_request_id'),
                          json.dumps(info)))

            conn.commit()
        print(f"    {len(results)}건 저장 완료")
    except Exception as e:
        conn.rollback()
        print(f"    [FAIL] {e}")
        raise
    finally:
        conn.close()

    # 결과 표
    print(f"\n[5] 추출 결과 ({target_date}):")
    print(f"{'호차':<6} {'Template':<10} {'시간':<10} {'차량번호':<14} {'톤수':<5} {'트럭바코드':<12} {'성함':<8} {'연락처':<14} {'업체':<8}")
    print("-"*120)
    for i, info in enumerate(results, 1):
        print(f"{i}호차   {info.get('template_id', '?'):<10} {info.get('request_time', '?'):<10} "
              f"{info.get('vehicle_num', '?'):<14} {info.get('tonnage', '?'):<5} "
              f"{info.get('truck_barcode', '?'):<12} {info.get('driver_name', '?'):<8} "
              f"{info.get('driver_phone', '?'):<14} {info.get('truck_vendor', '?'):<8}")


if __name__ == '__main__':
    main()

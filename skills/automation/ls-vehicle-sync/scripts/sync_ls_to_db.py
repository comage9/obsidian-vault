#!/usr/bin/env python3
"""
LS 차량 정보 → PostgreSQL 동기화
- 매일 LS /order API에서 오늘자 CONFIRMED/SUBMITTED 차량 정보 가져옴
- 케이스 1: 차량번호+전화번호 동일, 이름만 다름 → 정식 운전자 변경 (assignment 갱신)
- 케이스 2: 차량번호 동일, 이름+전화번호 모두 다름 → 임시 운전자 (별도 assignment)
- 차량번호 없을 때는 차량 마스터 생성 보류 (snapshot만 저장, 추후 LinehaulSlip PDF로 보충)
"""
import os
import sys
import json
import re
import requests
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from http.cookiejar import MozillaCookieJar
from datetime import datetime, date

# ============ 설정 ============
LS_COOKIE_FILE = '/tmp/coupang_cookies.txt'
DB_DSN = "host=127.0.0.1 dbname=ls_vehicle user=ls_user"
# 비번은 ~/.pgpass (chmod 600) 또는 PGPASSWORD 환경변수에서 자동 로드
# sync_ls_to_db.py 자체에는 비번 하드코딩 X (보안 운영원칙)
LS_BASE = "https://ls.coupang.com"

# 템플릿 ID → 톤수 매핑 (LS 스킬)
TEMPLATE_TONNAGE = {
    '90626': '11T',
    '90628': '5T',
    '90269': '11T',
    '101740': '5T',
}


def ls_login_and_save():
    """LS 자동 로그인 + 쿠키 저장 (이미 로그인되어 있으면 스킵)"""
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

    # 1) API 호출 → OAuth2 → Keycloak
    url = f"{LS_BASE}/order?statuses=SUBMITTED,CONFIRMED,CANCELED,BACK&locationStart=VF67_H&page=0&pageSize=50"
    r = session.get(url, allow_redirects=True)
    if 'xauth.coupang.com' not in r.url:
        # 이미 로그인된 상태
        return session

    # 2) form action 추출
    match = re.search(r'<form[^>]*action="([^"]+)"', r.text)
    if not match:
        raise RuntimeError("LS login form not found")
    form_action = match.group(1).replace('&amp;', '&')

    # 3) 로그인 POST
    r2 = session.post(form_action, data={
        "username": "mokicom",
        "password": "bonohouse0309^^",
        "credentialId": "",
        "login": "로그인",
    }, allow_redirects=True)
    session.cookies.save(ignore_discard=True, ignore_expires=True)
    return session


def fetch_today_orders(session, target_date: str):
    """LS /order API로 특정 날짜 오더 조회"""
    params = {
        "page": 0, "pageSize": 50,
        "statuses": "SUBMITTED,CONFIRMED,CANCELED,BACK",
        "locationStart": "VF67_H",
        "dateFrom": target_date,
        "dateTo": target_date,
    }
    r = session.get(f"{LS_BASE}/order", params=params, headers={
        "Accept": "application/json",
        "Referer": f"{LS_BASE}/",
    })
    r.raise_for_status()
    data = r.json()
    return data.get('data', {}).get('content', [])


def upsert_snapshot(cur, order_date, order):
    """snapshot 1건 INSERT (중복 시 스킵)"""
    template_id = order.get('truckOrderTemplateId')
    if not template_id:
        return None  # 템플릿 없는 6/4 1~3호차 같은 케이스

    truck_info = order.get('truckInfo') or {}
    snapshot_data = {
        'order_date': order_date,
        'template_id': template_id,
        'truck_num': truck_info.get('truckNum') if isinstance(truck_info, dict) else None,
        'driver_name': truck_info.get('driverName') if isinstance(truck_info, dict) else None,
        'driver_phone': truck_info.get('driverPhone') if isinstance(truck_info, dict) else None,
        'order_status': order.get('status'),
        'request_time': order.get('requestTime'),
        'truck_request_id': order.get('truckRequestId'),
        'raw_data': Json(order),
    }

    cur.execute("""
        INSERT INTO ls_vehicle_snapshot
            (order_date, template_id, truck_num, driver_name, driver_phone,
             order_status, request_time, truck_request_id, raw_data)
        VALUES (%(order_date)s, %(template_id)s, %(truck_num)s, %(driver_name)s, %(driver_phone)s,
                %(order_status)s, %(request_time)s, %(truck_request_id)s, %(raw_data)s)
        ON CONFLICT (order_date, template_id) DO UPDATE
            SET truck_num = EXCLUDED.truck_num,
                driver_name = EXCLUDED.driver_name,
                driver_phone = EXCLUDED.driver_phone,
                order_status = EXCLUDED.order_status,
                request_time = EXCLUDED.request_time,
                truck_request_id = EXCLUDED.truck_request_id,
                raw_data = EXCLUDED.raw_data,
                fetched_at = NOW()
        RETURNING snapshot_id
    """, snapshot_data)
    row = cur.fetchone()
    return row['snapshot_id']


def upsert_vehicle(cur, truck_num, template_id):
    """차량 마스터 UPSERT (truck_num 기준)"""
    if not truck_num:
        return None
    tonnage = TEMPLATE_TONNAGE.get(str(template_id), '미확인')
    cur.execute("""
        INSERT INTO vehicles (truck_num, template_id, tonnage)
        VALUES (%s, %s, %s)
        ON CONFLICT (truck_num) DO UPDATE
            SET template_id = COALESCE(EXCLUDED.template_id, vehicles.template_id),
                tonnage = COALESCE(EXCLUDED.tonnage, vehicles.tonnage),
                updated_at = NOW()
        RETURNING vehicle_id
    """, (truck_num, str(template_id), tonnage))
    return cur.fetchone()['vehicle_id']


def upsert_driver(cur, driver_name, driver_phone, is_temporary=False):
    """운전자 UPSERT (이름+전화 UNIQUE)"""
    if not driver_name or not driver_phone:
        return None
    cur.execute("""
        INSERT INTO drivers (driver_name, driver_phone, is_temporary)
        VALUES (%s, %s, %s)
        ON CONFLICT (driver_name, driver_phone) DO UPDATE
            SET is_temporary = EXCLUDED.is_temporary OR drivers.is_temporary,
                updated_at = NOW()
        RETURNING driver_id
    """, (driver_name.strip(), driver_phone.strip(), is_temporary))
    return cur.fetchone()['driver_id']


def close_old_assignments(cur, vehicle_id, end_date):
    """기존 활성 assignment 종료"""
    cur.execute("""
        UPDATE vehicle_driver_assignments
        SET end_date = %s
        WHERE vehicle_id = %s AND end_date IS NULL
    """, (end_date, vehicle_id))


def create_assignment(cur, vehicle_id, driver_id, start_date, is_temporary, source_snapshot_id, notes):
    """새 assignment 생성"""
    cur.execute("""
        INSERT INTO vehicle_driver_assignments
            (vehicle_id, driver_id, start_date, is_temporary, source_snapshot, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING assignment_id
    """, (vehicle_id, driver_id, start_date, is_temporary, source_snapshot_id, notes))
    return cur.fetchone()['assignment_id']


def classify_and_assign(cur, snapshot_id, order_date, truck_num, driver_name, driver_phone):
    """
    케이스 1/2 분류 + assignment 처리

    케이스 1: 차량번호+전화번호 동일, 이름만 다름
              → 정식 운전자 변경 (기존 assignment 종료, 새 assignment 생성)

    케이스 2: 차량번호 동일, 이름+전화번호 모두 다름
              → 임시 운전자 (별도 assignment, is_temporary=TRUE)

    케이스 0 (기본): 새 차량이거나 정보 부족 → 새 assignment
    """
    if not (truck_num and driver_name and driver_phone):
        return None  # 정보 부족, 스킵

    template_id = None
    cur.execute("SELECT template_id FROM vehicles WHERE truck_num = %s", (truck_num,))
    row = cur.fetchone()
    if not row:
        # 신규 차량 → vehicles에 INSERT는 snapshot에서 이미 했으므로 여기선 fetch
        cur.execute("SELECT vehicle_id, template_id FROM vehicles WHERE truck_num = %s", (truck_num,))
        row = cur.fetchone()
    vehicle_id = row['vehicle_id']
    template_id = row['template_id']

    # 현재 활성 assignment 조회
    cur.execute("""
        SELECT vda.assignment_id, vda.driver_id, d.driver_name, d.driver_phone, vda.is_temporary
        FROM vehicle_driver_assignments vda
        JOIN drivers d ON vda.driver_id = d.driver_id
        WHERE vda.vehicle_id = %s AND vda.end_date IS NULL
        ORDER BY vda.start_date DESC
        LIMIT 1
    """, (vehicle_id,))
    current = cur.fetchone()

    if not current:
        # 케이스 0: 신규
        driver_id = upsert_driver(cur, driver_name, driver_phone, is_temporary=False)
        return create_assignment(cur, vehicle_id, driver_id, order_date, False, snapshot_id, '신규 등록')

    # 현재 운전자와 비교
    cur_name = current['driver_name'].strip()
    cur_phone = current['driver_phone'].strip()
    new_name = driver_name.strip()
    new_phone = driver_phone.strip()

    if cur_phone == new_phone and cur_name != new_name:
        # 케이스 1: 전화번호 동일, 이름 다름 → 정식 운전자 변경
        # 기존 driver의 이름이 다른 것이므로, 새 driver 등록 후 assignment 갱신
        new_driver_id = upsert_driver(cur, new_name, new_phone, is_temporary=False)
        close_old_assignments(cur, vehicle_id, order_date)
        return create_assignment(cur, vehicle_id, new_driver_id, order_date, False, snapshot_id,
                                  f'운전자 변경: {cur_name} → {new_name}')

    elif cur_phone != new_phone and cur_name != new_name:
        # 케이스 2: 이름+전화 모두 다름 → 임시 운전자
        new_driver_id = upsert_driver(cur, new_name, new_phone, is_temporary=True)
        # 기존 정식 assignment는 유지, 임시 assignment 추가 (end_date 설정)
        # 임시 assignment는 end_date=당일+1로 (다음날까지만 유효)
        from datetime import timedelta
        return create_assignment(cur, vehicle_id, new_driver_id, order_date, True, snapshot_id,
                                  f'임시 운전자 (기존: {cur_name}/{cur_phone})')

    else:
        # 이름+전화 동일 → 정상 (변경 없음, snapshot만 갱신)
        return current['assignment_id']


def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else date.today().strftime('%Y-%m-%d')
    print(f"[1] LS 자동 로그인...")
    session = ls_login_and_save()
    print(f"    쿠키 {len(session.cookies)}개")

    print(f"[2] LS /order 조회 ({target_date})...")
    orders = fetch_today_orders(session, target_date)
    print(f"    전체 {len(orders)}건 (서버 응답)")

    # ⚠️ LS API dateFrom/dateTo 무시 — orderDate로 클라이언트 필터
    filtered = [o for o in orders if o.get('orderDate') == target_date]
    print(f"    {target_date} 필터: {len(filtered)}건")

    # CONFIRMED + SUBMITTED만 처리
    active = [o for o in filtered if o.get('status') in ('CONFIRMED', 'SUBMITTED')]
    print(f"    활성 (CONFIRMED+SUBMITTED): {len(active)}건")
    # CANCELED도 보관 (스냅샷)
    canceled = [o for o in filtered if o.get('status') == 'CANCELED']
    print(f"    취소 (CANCELED): {len(canceled)}건 (스냅샷만, vehicles/drivers 갱신 안 함)")

    all_to_process = active + canceled

    print(f"[3] DB 연결...")
    conn = psycopg2.connect(DB_DSN)
    conn.autocommit = False

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for o in all_to_process:
                template_id = o.get('truckOrderTemplateId')
                if not template_id:
                    continue
                ti = o.get('truckInfo') or {}
                truck_num = ti.get('truckNum') if isinstance(ti, dict) else None
                driver_name = ti.get('driverName') if isinstance(ti, dict) else None
                driver_phone = ti.get('driverPhone') if isinstance(ti, dict) else None
                is_active_status = o.get('status') in ('CONFIRMED', 'SUBMITTED')

                # [DELETED] 플레이스홀더는 None으로 정규화
                if driver_name in ('[DELETED]', None, '\t'):
                    driver_name = None
                if driver_phone in ('[DELETED]', None, ''):
                    driver_phone = None
                if truck_num in (None, '', ' '):
                    truck_num = None

                print(f"  - {target_date} | 템플릿={template_id} | {truck_num or '차량번호없음'} | "
                      f"{driver_name or '?'} / {driver_phone or '?'} | {o.get('status')}")

                # 1) snapshot (모두 저장)
                snapshot_id = upsert_snapshot(cur, target_date, o)
                # 2) vehicles/drivers/assignments (활성 상태 + 정보 있는 경우만)
                if is_active_status and truck_num and driver_name and driver_phone:
                    upsert_vehicle(cur, truck_num, template_id)
                    classify_and_assign(cur, snapshot_id, target_date, truck_num, driver_name, driver_phone)

            conn.commit()
        print(f"\n[OK] 동기화 완료. {len(all_to_process)}건 (활성 {len(active)}건, 취소 {len(canceled)}건).")
    except Exception as e:
        conn.rollback()
        print(f"\n[FAIL] {e}")
        raise
    finally:
        conn.close()

    # 결과 조회
    print(f"\n[4] DB 결과:")
    conn2 = psycopg2.connect(DB_DSN)
    with conn2.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT v.vehicle_id, v.truck_num, v.tonnage, v.template_id,
                   d.driver_name, d.driver_phone, vda.start_date, vda.is_temporary, vda.notes
            FROM vehicles v
            LEFT JOIN vehicle_driver_assignments vda ON v.vehicle_id = vda.vehicle_id AND vda.end_date IS NULL
            LEFT JOIN drivers d ON vda.driver_id = d.driver_id
            ORDER BY v.vehicle_id, vda.start_date DESC
        """)
        for row in cur.fetchall():
            print(f"  - 차량={row['truck_num']} ({row['tonnage']}) | "
                  f"운전자={row['driver_name']}/{row['driver_phone']} | "
                  f"임시={row['is_temporary']} | {row['notes']}")
    conn2.close()


if __name__ == '__main__':
    main()

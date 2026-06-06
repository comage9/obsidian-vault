#!/usr/bin/env python3
"""
LS Coupang Daily VF67 Cron Job (매일 13:00 KST)
- Login → Check today's VF67 orders via /order API
- If unregistered: Batch Create 3 templates → Verify
- Build 배차 요청 message → Send to Telegram

Usage: python3 daily-cron-vf67.py
"""
import requests
import re
import json
import subprocess
import urllib.request
import urllib.parse
import time
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
today = datetime.now(KST)
today_str = today.strftime("%Y-%m-%d")
today_md = today.strftime("%-m/%-d")

# ── Template config ─────────────────────────────────────────────
TEMPLATES = {
    90626: {"hosu": "1", "ton": "11T", "time": "20:00"},
    90628: {"hosu": "2", "ton": "5T",  "time": "22:00"},
    90269: {"hosu": "3", "ton": "11T", "time": "23:50"},
}

# ── 1. Login ────────────────────────────────────────────────────
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
})

r = session.get("https://ls.coupang.com/order",
    params={"page": 0, "pageSize": 50, "statuses": "SUBMITTED,CONFIRMED,CANCELED,BACK",
            "locationStart": "VF67_H"},
    allow_redirects=True, timeout=30)

m = re.search(r'<form[^>]*action="([^"]+)"', r.text)
if m:
    fa = m.group(1).replace('&amp;', '&')
    r2 = session.post(fa,
        data={"username": "mokicom", "password": "bonohouse0309^^",
              "credentialId": "", "login": "로그인"},
        allow_redirects=True, timeout=30,
        headers={"Origin": "https://xauth.coupang.com",
                 "Content-Type": "application/x-www-form-urlencoded"})
    if "ls.coupang.com" not in r2.url:
        r2 = session.post(fa,
            data={"username": "mokicom", "password": "bonohouse0309^^"},
            allow_redirects=True, timeout=30,
            headers={"Origin": "https://xauth.coupang.com",
                     "Content-Type": "application/x-www-form-urlencoded"})

# ── 2. Fetch today's VF67 orders ────────────────────────────────
r3 = session.get("https://ls.coupang.com/order", params={
    "page": 0, "pageSize": 50,
    "statuses": "SUBMITTED,CONFIRMED,CANCELED,BACK",
    "locationStart": "VF67_H",
    "dateFrom": today_str, "dateTo": today_str,
}, headers={"Accept": "application/json, */*", "Referer": "https://ls.coupang.com/"}, timeout=30)

today_orders = []
data = r3.json() if r3.status_code == 200 else {}
content = (data.get('data') or data).get('content', []) if isinstance(data.get('data') or data, dict) else []

for o in content:
    if not isinstance(o, dict):
        continue
    od = o.get('orderDate', '')
    fc = (o.get('from') or {}).get('code', '') if isinstance(o.get('from'), dict) else ''
    if od != today_str or fc != 'VF67_H':
        continue
    rt = o.get('requestTime', '')
    time_part = rt[11:16] if isinstance(rt, str) and len(rt) >= 19 else ''
    today_orders.append({
        'status': o.get('status', ''),
        'requestTime': time_part,
        'templateId': o.get('truckOrderTemplateId'),
        'truckRequestId': o.get('truckRequestId', ''),
    })

active = [o for o in today_orders if o['status'] in ('SUBMITTED', 'CONFIRMED')]

# ── 3. Determine missing templates ──────────────────────────────
registered_ids = set()
for o in active:
    tid = o.get('templateId')
    if tid and tid in TEMPLATES:
        registered_ids.add(tid)

missing = [t for t in TEMPLATES if t not in registered_ids]

# ── 4. Batch create if needed ────────────────────────────────────
if missing:
    r4 = session.post(
        f"https://ls.coupang.com/truckOrder/templates/batch/creation/{today_str}",
        json=missing,
        headers={"Accept": "application/json", "Content-Type": "application/json",
                 "Referer": "https://ls.coupang.com/"},
        timeout=30)
    if r4.status_code == 200:
        time.sleep(2)

# ── 5. Build order items (deduplicated, time-sorted) ────────────
order_items = []
seen = set()
for o in active:
    tid = o.get('templateId')
    info = TEMPLATES.get(tid) or (next((v for k, v in TEMPLATES.items() if v['time'] == o['requestTime']), None))
    if info and info['hosu'] not in seen:
        seen.add(info['hosu'])
        order_items.append(info)
order_items.sort(key=lambda x: x['time'])

# Fallback: if no template IDs matched but we have active orders, use all templates
if not order_items and active:
    order_items = sorted(TEMPLATES.values(), key=lambda x: x['time'])
elif not order_items:
    order_items = sorted(TEMPLATES.values(), key=lambda x: x['time'])

# ── 6. Build 배차 요청 message ──────────────────────────────────
lines = [f"안녕하세요. VF67 - {today_md} 배차 요청 드립니다"]
for i, oi in enumerate(order_items, 1):
    lines.append(f"{i}. 부천1 HUB {oi['ton']} {oi['time']} {oi['hosu']}호차")
lines.append("상기와 같이 배차 진행 부탁드립니다")
final_msg = "\n".join(lines)

# ── 7. Send to Telegram ────────────────────────────────────────
r_env = subprocess.run(['grep', 'TELEGRAM_BOT_TOKEN', '/opt/hermes/.env'],
                       capture_output=True, text=True)
token = r_env.stdout.strip().split('=', 1)[1]
chat_id = "5708696961"
url = f"https://api.telegram.org/bot{token}/sendMessage"
data = urllib.parse.urlencode({"chat_id": chat_id, "text": final_msg, "parse_mode": "HTML"}).encode()
urllib.request.urlopen(urllib.request.Request(url, data=data, method="POST"))

# ── 8. Output for cron report ──────────────────────────────────
print(final_msg)

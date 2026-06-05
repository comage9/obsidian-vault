#!/usr/bin/env python3
"""키프로젝트 상태 확인 및 알림 — 30분 간단 / 16시 상세 브리핑"""

import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/comage/coding/ki-ai-trader')

from kiwoom_api import KiwoomAPIClient
from technical_indicators import calculate_rsi, calculate_macd, fetch_daily_data, calculate_bollinger

TRADE_LOG_PATH = Path('/home/comage/.hermes/cron/output/ki-trade-log.json')

# ── 손절 / 익절 기준 (adaptive_trailing_stop.py 기반) ──
EMERGENCY_STOP_PCT = -5.0   # 긴급 손절阀值
TRAILING_STEP_PCT = 0.3     # 트레일링 간격 (%)
TRAILING_ACTIVATE_PROFIT = 0.5  # 트레일링 활성화 최소 수익률 (%)
TRAILING_ACTIVATE_RSI = 65      # 트레일링 활성화 RSI 기준


def is_market_open():
    now = datetime.now()
    hour, minute = now.hour, now.minute
    weekday = now.weekday()
    if weekday >= 5:
        return False
    if hour < 9 or (hour == 15 and minute > 30) or hour > 15:
        return False
    return True


def calc_trailing(client, code, purchase_price, current_price, quantity):
    """손절가 / 익절가 / 최고점 계산"""
    daily = fetch_daily_data(client, code, days=60)
    if not daily or len(daily) < 20:
        return None

    closes = [d['close'] for d in daily]
    highs  = [d.get('high', d['close']) for d in daily]

    rsi = calculate_rsi(closes, 14)
    macd_l, sig_l, hist = calculate_macd(closes)
    ma5  = sum(closes[-5:])  / 5
    ma20 = sum(closes[-20:]) / 20

    # 5일 / 20일 모멘텀
    mom5  = ((closes[-1] - closes[-6])  / closes[-6])  * 100 if len(closes) >= 6  else 0
    mom20 = ((closes[-1] - closes[-20]) / closes[-20]) * 100 if len(closes) >= 20 else 0

    # ATR (14일)
    tr_list = []
    for i in range(1, min(len(daily), 15)):
        tr = max(
            highs[-i] - daily[-i].get('low', closes[-i]),
            abs(highs[-i] - closes[-i-1]),
            abs(daily[-i].get('low', closes[-i]) - closes[-i-1])
        )
        tr_list.append(tr)
    atr = sum(tr_list) / len(tr_list) if tr_list else 0

    # 현재 수익률
    profit_pct = (current_price - purchase_price) / purchase_price * 100
    profit_amt = (current_price - purchase_price) * quantity

    # ── 손절가 ──
    # 1차: ATR 기반 동적 손절 (매수가 기준)
    atr_stop = purchase_price * (1 - 2 * atr / purchase_price)
    # 2차: 긴급 손절 (-5% 이하)
    emergency_stop = purchase_price * (1 + EMERGENCY_STOP_PCT / 100)
    stop_loss = max(atr_stop, emergency_stop)  # 더 높은( 덜下落) 가격이 적용

    # ── 익절가 (트레일링) ──
    trailing_active = profit_pct >= TRAILING_ACTIVATE_PROFIT and rsi >= TRAILING_ACTIVATE_RSI
    highest_price  = max(highs[-20:]) if len(highs) >= 20 else max(closes)

    if trailing_active:
        trailing_stop = highest_price * (1 - TRAILING_STEP_PCT / 100)
        take_profit_pct = TRAILING_STEP_PCT
    else:
        trailing_stop = None
        take_profit_pct = None

    # ── 추세 판단 ──
    trend = '중립'
    if ma5 > ma20 and hist > 0 and mom5 > 0:
        trend = '상승'
    elif ma5 < ma20 and hist < 0 and mom5 < 0:
        trend = '하락'
    elif ma5 < ma20:
        trend = '단기하락'
    elif rsi > 70:
        trend = '과매수 구간'

    # ── 매매 판단 ──
    if profit_pct <= EMERGENCY_STOP_PCT:
        action = '🚨 긴급 손절 검토'
    elif trailing_active and current_price <= trailing_stop:
        action = '📤 트레일링 익절 실시'
    elif rsi > 80 or (rsi > 75 and hist < 0):
        action = '⚠️ RSI 과매수 — 익절/관망'
    elif ma5 < ma20 and mom5 < -3:
        action = '🔍 단기추세 하락 — 관망'
    elif trend == '상승':
        action = '✅ 홀딩'
    else:
        action = '👀 관망'

    return {
        'rsi': round(rsi, 1),
        'macd_hist': round(hist, 2),
        'ma5': round(ma5),
        'ma20': round(ma20),
        'mom5': round(mom5, 1),
        'mom20': round(mom20, 1),
        'atr': round(atr),
        'profit_pct': round(profit_pct, 2),
        'profit_amt': round(profit_amt),
        'stop_loss': round(stop_loss),
        'trailing_active': trailing_active,
        'highest_price': round(highest_price),
        'trailing_stop': round(trailing_stop) if trailing_stop else None,
        'take_profit_pct': take_profit_pct,
        'trend': trend,
        'action': action,
        'ma_cross': '정배열' if ma5 > ma20 else '역배열',
    }


def get_trade_log():
    try:
        if not TRADE_LOG_PATH.exists():
            return []
        logs = json.loads(TRADE_LOG_PATH.read_text(encoding='utf-8'))
        today = datetime.now().strftime('%Y%m%d')
        if logs.get('date') != today:
            return []
        return logs.get('trades', [])
    except:
        return []


def get_status():
    try:
        client = KiwoomAPIClient()
        if not client.authenticate():
            return {'error': '인증 실패'}

        account  = client.get_account_balance()
        holdings = client.get_holdings()

        cash  = account.available_balance if account else 0
        total = account.total_assets       if account else 0

        holding_info = []
        total_profit = 0
        for h in (holdings or []):
            profit = h.evaluation_pl
            rate   = h.evaluation_pl_ratio
            total_profit += profit
            ind = calc_trailing(client, h.stock_code, h.purchase_price,
                                h.current_price, h.quantity)
            holding_info.append({
                'name':        h.stock_name,
                'code':        h.stock_code,
                'qty':         h.quantity,
                'price':       h.current_price,
                'buy_price':   h.purchase_price,
                'profit':      profit,
                'rate':        rate,
                'indicators':  ind,
            })

        profit_rate = (total_profit / (total - cash) * 100) if total > cash else 0

        return {
            'success':      True,
            'market_closed': not is_market_open(),
            'time':         datetime.now().strftime('%H:%M'),
            'cash':         cash,
            'total':        total,
            'profit':       total_profit,
            'profit_rate':  profit_rate,
            'holdings':     holding_info,
            'client':       client,
        }
    except Exception as e:
        return {'error': str(e)}


# ── 30분 간단 알람 ──
def format_brief(data):
    if 'error' in data:
        return f'❌ 오류: {data["error"]}'

    now = data['time']
    holdings = data['holdings']

    lines = [
        f'📊 키프로젝트 ({now})',
        f'💰 예수금 {data["cash"]:,.0f}원 | 총자산 {data["total"]:,.0f}원',
        f'📈 총 손익 {data["profit"]:+,}원 ({data["profit_rate"]:+.2f}%)',
        '─' * 36,
    ]

    for h in holdings:
        ind = h['indicators']
        p   = ind['profit_pct']
        emoji = '🟢' if p > 0 else '🔴' if p < 0 else '⚪'

        stop_str = f'손절가 {ind["stop_loss"]:>7,.0f}'
        if ind['trailing_active']:
            tp_str = f'익절가 {ind["trailing_stop"]:>7,.0f}'
        else:
            tp_str = f'익절 ─'

        lines.append(
            f'{emoji} {h["name"]} {h["qty"]}주 {p:+.1f}% '
            f'| {ind["trend"]} | {ind["action"]}'
        )
        lines.append(f'   현재 {h["price"]:>7,.0f}원 | {stop_str} | {tp_str}')

    lines.append('─' * 36)
    lines.append('⏰ 30분 후 갱신')
    return '\n'.join(lines)


# ── 16시 마감 상세 브리핑 ──
def format_detailed(data):
    if 'error' in data:
        return f'❌ 오류: {data["error"]}'

    now     = data['time']
    trades  = get_trade_log()

    lines = [
        f'📊 키프로젝트 마감 브리핑 ({now})',
        '═' * 36,
        f'💰 예수금 {data["cash"]:,.0f}원',
        f'💎 총자산 {data["total"]:,.0f}원',
        f'📈 총 손익 {data["profit"]:+,}원 ({data["profit_rate"]:+.2f}%)',
        '═' * 36,
    ]

    # ── 오늘 거래 내역 ──
    if trades:
        buy_t, sell_t = 0, 0
        for t in trades:
            emoji = '🟢' if t['action'] == 'BUY' else '🔴'
            amt   = t['qty'] * t['price']
            if t['action'] == 'BUY':
                buy_t += amt
            else:
                sell_t += amt
            lines.append(
                f'{emoji} {t["action"]} {t["name"]}({t["code"]}) '
                f'{t["qty"]}주 @{t["price"]:,.0f}원'
            )
            lines.append(f'   사유: {t.get("reason","")}')
        lines.append(f'💵 매수 {buy_t:,.0f}원 | 매도 {sell_t:,.0f}원')
    else:
        lines.append('📋 오늘 거래 내역: 없음')

    lines.append('─' * 36)
    lines.append('📌 보유 종목 상세')
    lines.append('─' * 36)

    for h in data['holdings']:
        ind = h['indicators']
        p   = ind['profit_pct']
        emoji = '🟢' if p > 0 else '🔴' if p < 0 else '⚪'

        lines.append(
            f'{emoji} {h["name"]}({h["code"]}) '
            f'{h["qty"]}주 @ 매입{h["buy_price"]:,.0f} / 현재{h["price"]:,.0f}'
        )
        lines.append(
            f'   수익 {ind["profit_amt"]:+,}원 ({p:+.2f}%) | '
            f'손절가 {ind["stop_loss"]:,.0f}원'
        )
        lines.append(
            f'   RSI {ind["rsi"]} | MACD {ind["macd_hist"]:+.2f} | '
            f'MA5 {ind["ma5"]:,} / MA20 {ind["ma20"]:,} ({ind["ma_cross"]})'
        )
        lines.append(
            f'   모멘텀 5일 {ind["mom5"]:+.1f}% / 20일 {ind["mom20"]:+.1f}% | '
            f'ATR {ind["atr"]:,.0f}'
        )
        if ind['trailing_active']:
            lines.append(
                f'   🚀 트레일링 활성 | '
                f'최고가 {ind["highest_price"]:,}원 → 익절가 {ind["trailing_stop"]:,}원 '
                f'({ind["take_profit_pct"]}% trailing)'
            )
        lines.append(f'   → {ind["action"]} | 추세: {ind["trend"]}')
        lines.append('─' * 36)

    lines.append('🔒 장 마감 | ⏰ 다음 업데이트: 내일 오전 9시')
    return '\n'.join(lines)


if __name__ == '__main__':
    data = get_status()

    if data.get('market_closed'):
        output = format_detailed(data)
    else:
        output = format_brief(data)

    print(output)

    # JSON 저장
    out_path = Path('/home/comage/.hermes/cron/output/ki-project-status.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({k: v for k, v in data.items() if k != 'client'}, f,
                  ensure_ascii=False, default=str)

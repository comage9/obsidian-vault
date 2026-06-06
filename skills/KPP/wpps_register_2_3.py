"""
WPPS PBM140MW 출하통보등록 완전 자동화 스크립트 (올인원 에디션)
파일명: E:\\coding\\skill\\KPP\\wpps_register_2_3.py
작성일: 2026-06-06

주요 기능:
1. 크롬 디버거(CDP 9222)로부터 실시간으로 쿠팡 LS 세션 쿠키 자동 추출
2. 쿠팡 LS API를 실시간 조회하여 오늘자 VF67 출발 차량 확인
3. 2호차/3호차의 truckRequestId로 출차확인서 PDF 다운로드 및 PyMuPDF 실시간 정보(기사명, 연락처) 파싱
4. WPPS PBM140MW 접속 및 중복 등록된 차량 감지 시 선택적 삭제 후 일괄 저장
5. 1~3호차 차량 정보 일괄 등록 후 단 1회만 저장(Batch Save)하여 속도 및 성능 최적화
6. 최종 결과 검증 및 스크린샷 캡처
"""

import json
import urllib.request
import urllib.parse
import websocket
import time
import base64
import threading
import sys
import re
import fitz  # PyMuPDF
import os

CDP_PORT = 9222
PBM_URL = "https://wpps.logisall.net/ps/PBM140MW"
LOGIN_URL = "https://wpps.logisall.net/"
DATE = time.strftime("%Y-%m-%d")  # 오늘 날짜 (YYYY-MM-DD)

# WPPS 그리드 내 톤수별 표준 팔레트 수량 정의
QTY_RULES = {
    "5T": 12,
    "11T": 14,
    "14T": 18
}

class WPPS_CDP_FullAutomation:
    def __init__(self):
        self._c = 0
        self.ws = None
        self.dialog_thread = None
        self.ws_url = None
        self.page_info = None
        self._refresh_page()

    def _get_pages(self):
        try:
            return json.loads(urllib.request.urlopen(f'http://localhost:{CDP_PORT}/json').read())
        except Exception as e:
            print(f"[ERROR] 크롬 원격 디버깅이 켜져 있는지 확인하십시오. (포트 {CDP_PORT}): {e}")
            sys.exit(1)

    def _page_ws(self, url_filter=''):
        pages = self._get_pages()
        for p in pages:
            if p.get('type') == 'page' and url_filter in p.get('url',''):
                return p['webSocketDebuggerUrl'], p
        if pages:
            return pages[0]['webSocketDebuggerUrl'], pages[0]
        raise Exception("열린 브라우저 탭을 찾을 수 없습니다.")

    def _refresh_page(self):
        self.ws_url, self.page_info = self._page_ws('PBM140MW')
        self.ws = websocket.create_connection(self.ws_url, timeout=15)
        self.ws.settimeout(15)

    def cmd(self, method, params=None, timeout=15):
        self._c += 1
        self.ws.send(json.dumps({'id': self._c, 'method': method, 'params': params or {}}))
        self.ws.settimeout(timeout)
        while True:
            r = json.loads(self.ws.recv())
            if 'id' in r and r['id'] == self._c: 
                return r

    def js(self, expr, timeout=15):
        r = self.cmd('Runtime.evaluate', {'expression': expr, 'returnByValue': True}, timeout)
        if 'exceptionDetails' in r.get('result', {}):
            print(f"[JS EXCEPTION] {r['result']['exceptionDetails']}")
        return r.get('result',{}).get('result',{}).get('value','')

    def screenshot(self, path):
        try:
            r = self.cmd('Page.captureScreenshot', {'format': 'png'})
            with open(path, 'wb') as f:
                f.write(base64.b64decode(r['result']['data']))
            print(f"[INFO] 스크린샷 저장 완료: {path}")
        except Exception as e:
            print(f"[WARN] 스크린샷 저장 실패: {e}")

    def get_ls_cookies_from_browser(self):
        """크롬 디버거의 Network.getCookies API를 사용하여 브라우저 내의 쿠팡 LS 쿠키 추출"""
        print("[INFO] 크롬 브라우저 세션에서 쿠팡 LS 쿠키를 자동으로 획득하는 중...")
        try:
            # Network 기능 활성화
            self.cmd('Network.enable')
            
            # ls.coupang.com 도메인의 쿠키 가져오기
            res = self.cmd('Network.getCookies', {'urls': ['https://ls.coupang.com']})
            cookies = res.get('result', {}).get('cookies', [])
            
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            
            if not cookie_str:
                print("[WARN] 쿠팡 LS 쿠키를 획득하지 못했습니다. 브라우저에서 LS 로그인이 되어 있는지 확인하세요.")
            else:
                print(f"[SUCCESS] 쿠팡 LS 쿠키 자동 획득 성공 (길이: {len(cookie_str)} 자)")
            return cookie_str
        except Exception as e:
            print(f"[ERROR] 브라우저 쿠키 자동 추출 실패: {e}")
            return ""

    def start_dialog_handler(self):
        """Background에서 dialog 발생 시 자동으로 수락(accept)하는 스레드 구동"""
        def handler():
            try:
                dws = websocket.create_connection(self.ws_url, timeout=10)
                dws.settimeout(60)
                while True:
                    try:
                        msg = json.loads(dws.recv())
                        if msg.get('method') == 'Page.javascriptDialogOpening':
                            print(f"[DIALOG DETECTED] {msg['params']['message']} -> Auto accepting...")
                            dws.send(json.dumps({
                                'id': 999,
                                'method': 'Page.handleJavaScriptDialog',
                                'params': {'accept': True}
                            }))
                    except Exception as e:
                        break
                dws.close()
            except Exception as e:
                pass
        self.dialog_thread = threading.Thread(target=handler, daemon=True)
        self.dialog_thread.start()
        print("[INFO] 백그라운드 다이얼로그 핸들러 작동 시작")

    def navigate(self, url):
        print(f"[INFO] {url} (으)로 이동 중...")
        self.cmd('Page.navigate', {'url': url})
        time.sleep(3)

    def handle_popups(self):
        """팝업 및 공지사항 등 닫기"""
        c = self.js("""
        (function(){
            var ids=['popupChkClose','popupPlace3Chk']; var c=[];
            for(var i=0;i<ids.length;i++){var e=document.getElementById(ids[i]);if(e){e.click();c.push(ids[i]);}}
            var b=document.getElementById('popupBtnClose');if(b){b.click();c.push('popupBtnClose');}
            return c.join(',');
        })()
        """)
        if c:
            print(f"[INFO] 닫힌 팝업 요소: {c}")

    def override_dialogs(self):
        """기본 alert/confirm 창의 차단을 방지하기 위해 JavaScript 단에서 오버라이드 (const 에러 회피)"""
        self.js("""
            try { window.alert = function(msg){ console.log("Alert bypassed: " + msg); return true; }; } catch(e){}
            try { window.confirm = function(msg){ console.log("Confirm bypassed: " + msg); return true; }; } catch(e){}
            try { window.gfn_alert = function(msg){ console.log("gfn_alert bypassed: " + msg); return msg; }; } catch(e){}
            try { window.gfn_confirm = function(msg){ console.log("gfn_confirm bypassed: " + msg); return true; }; } catch(e){}
        """)
        print("[INFO] 브라우저 alert/confirm 오버라이드 완료")

    def set_date(self, date_str):
        self.js(f"document.getElementById('sr_dlv_dat_f').value='{date_str}'")
        self.js(f"document.getElementById('sr_dlv_dat_t').value='{date_str}'")
        print(f"[INFO] 조회 기간 설정: {date_str} ~ {date_str}")

    def search(self):
        """조회 기능 실행 및 결과 확인"""
        self.start_dialog_handler()
        time.sleep(0.5)
        self.js("fn_search('BUTTON')")
        print("[INFO] 조회 요청 전송 (fn_search 호출)")
        time.sleep(5)

    def get_row_count(self):
        try:
            res = self.js("""
            (function(){
                var control = GC.Spread.Sheets.findControl(document.getElementById('grid'));
                if (!control) return -1;
                return control.getActiveSheet().getRowCount();
            })()
            """)
            return int(res)
        except:
            return -1

    def read_grid_data(self):
        """그리드 데이터 요약 추출"""
        return self.js("""
        (function(){
            try {
                var s = GC.Spread.Sheets.findControl(document.getElementById('grid')).getActiveSheet();
                var out = [];
                for(var i=0; i<s.getRowCount(); i++){
                    out.push("Row " + i + " -> MOD=" + s.getValue(i,2) + ", 차량번호=" + s.getValue(i,31) + ", 기사=" + s.getValue(i,32) + ", 호차=" + s.getValue(i,36) + ", 수량=" + s.getValue(i,18));
                }
                return out.join(" | ");
            } catch(e) {
                return 'ERR:' + e.message;
            }
        })()
        """)

    def delete_existing_hoche(self, car_nums_to_delete):
        """그리드에서 특정 차량번호들을 가진 행을 찾아 체크하고 삭제 수행 (1호차 956464는 절대 제외)"""
        print(f"[INFO] 중복/재등록 차량 번호 삭제 시도: {car_nums_to_delete}")
        
        js_check_script = f"""
        (function(){{
            var s = GC.Spread.Sheets.findControl(document.getElementById('grid')).getActiveSheet();
            var target_nums = {json.dumps(car_nums_to_delete)};
            var checked_count = 0;
            
            for(var i=0; i<s.getRowCount(); i++){{
                var car_num = String(s.getValue(i, 31) || '').trim();
                if(target_nums.indexOf(car_num) !== -1){{
                    s.setValue(i, 1, true); // 체크
                    checked_count++;
                }} else {{
                    s.setValue(i, 1, false); // 체크 해제
                }}
            }}
            return checked_count;
        }})()
        """
        checked_count = int(self.js(js_check_script))
        print(f"[INFO] 삭제 대상 행 체크 완료: {checked_count}건")
        
        if checked_count > 0:
            self.override_dialogs()
            self.start_dialog_handler()
            time.sleep(0.5)
            self.js("fn_delete()")
            print("[INFO] 삭제 실행 (fn_delete 호출)")
            time.sleep(2)
            
            self.save()
            print("[INFO] 삭제 저장 요청 완료. 결과 검증을 위해 재조회 중...")
            self.search()
            return True
        else:
            print("[INFO] 기존 그리드에 삭제 대상 차량 행이 존재하지 않아 삭제를 생략합니다.")
            return False

    def add_new_row(self):
        """그리드에 신규 행 추가"""
        self.js("fn_newRow()")
        time.sleep(1.2)

    def set_row_data(self, row_idx, car, driver, phone, qty, hoche):
        """특정 행 번호에 차량 정보 주입 (하차지 자동완성 에러 우회 적용)"""
        s = f"""
        (function(){{
            var s = GC.Spread.Sheets.findControl(document.getElementById('grid')).getActiveSheet();
            s.setValue({row_idx}, 1, true); // 체크박스 선택 (CHK)
            s.setValue({row_idx}, 10, '610060'); // 하차지코드 (arv_cst_cod)
            s.setValue({row_idx}, 12, '9999999999999'); // 자체코드 (usr_cst_cod)
            s.setValue({row_idx}, 14, '쿠팡-부천1센터[HUB]'); // 하차지명 (arv_cst_nam)
            s.setValue({row_idx}, 15, 'N11'); // 제품코드 (prd_cod)
            s.setValue({row_idx}, 18, {qty}); // 수량 (dlv_qty)
            s.setValue({row_idx}, 20, '610060'); // 주문지코드 (ord_cst_cod)
            s.setValue({row_idx}, 22, '쿠팡-부천1센터[HUB]'); // 주문지명 (ord_cst_nam)
            s.setValue({row_idx}, 31, '{car}'); // 차량번호 (car_num)
            s.setValue({row_idx}, 32, '{driver}'); // 기사명 (driver_nam)
            s.setValue({row_idx}, 33, '{phone.replace("-", "")}'); // 연락처 (driver_tel)
            s.setValue({row_idx}, 36, '{hoche}'); // 비고/호차구분 (remk_txt)
            return 'OK';
        }})()
        """
        self.js(s)

    def save(self):
        """저장 작업 수행 및 alert/confirm 대응"""
        self.override_dialogs()
        self.start_dialog_handler()
        time.sleep(0.5)
        self.js("fn_save()")
        print("[INFO] 저장 요청 전송 (fn_save 호출)")
        time.sleep(4)

    def print_pdf(self, pdf_path, title=""):
        """CDP로 PDF를 열고 Chrome PDF 뷰어의 인쇄 버튼 클릭"""
        import os
        abs_path = os.path.abspath(pdf_path)
        file_url = urllib.parse.quote(abs_path)
        pdf_url = f"file:///{file_url.replace('%3A', ':').replace('%5C', '/')}"
        
        print(f"[INFO] PDF 인쇄 준비 중: {title or pdf_path}")
        
        # 새 탭에 PDF 열기
        pages_before = self._get_pages()
        self.cmd('Target.createTarget', {'url': pdf_url, 'newWindow': False})
        time.sleep(3)
        
        pages_after = self._get_pages()
        new_pages = [p for p in pages_after if p.get('id') not in [pb.get('id','') for pb in pages_before]]
        
        if new_pages:
            pdf_page = new_pages[0]
            print(f"[INFO] PDF 뷰어 로드됨: {pdf_page.get('url','')[:60]}")
            
            # PDF 뷰어 인쇄 버튼 클릭 (shadow DOM)
            try:
                pws = websocket.create_connection(pdf_page['webSocketDebuggerUrl'], timeout=10)
                pws.settimeout(10)
                pws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {
                    'expression': '''
                    (function() {
                        try {
                            var viewer = document.querySelector('pdf-viewer');
                            if (!viewer) return 'no pdf-viewer';
                            var toolbar = viewer.shadowRoot.querySelector('viewer-toolbar');
                            if (!toolbar) return 'no toolbar';
                            var printBtn = toolbar.shadowRoot.getElementById('print');
                            if (!printBtn) return 'no print btn';
                            printBtn.click();
                            return 'print clicked';
                        } catch(e) { return 'ERR: ' + e.message; }
                    })()
                    ''',
                    'returnByValue': True
                }}))
                time.sleep(1)
                try:
                    while True:
                        r = json.loads(pws.recv())
                        if 'id' in r:
                            print(f"[INFO] PDF 인쇄: {r.get('result',{}).get('result',{}).get('value','')}")
                            break
                except:
                    print("[INFO] 인쇄 다이얼로그 열림 (CDP 타임아웃=정상)")
                pws.close()
                print(f"[INFO] ✅ 인쇄 다이얼로그가 열렸습니다. 프린터(Canon G2010 series) 선택 후 인쇄하세요.")
            except Exception as e:
                print(f"[WARN] PDF 인쇄 버튼 클릭 실패: {e}")
        else:
            print("[WARN] PDF 탭을 찾을 수 없습니다.")

    def close(self):
        if self.ws:
            self.ws.close()
            print("[INFO] CDP 연결 종료")


def fetch_ls_vehicles(cookies):
    """쿠팡 LS API를 통해 오늘자 등록 차량 정보를 가져옴"""
    url = f"https://ls.coupang.com/truckOrderTracking?page=0&pageSize=100&orderStartDate={DATE}&orderEndDate={DATE}&locationStart=VF67"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    req.add_header("Accept", "application/json, text/plain, */*")
    req.add_header("Referer", "https://ls.coupang.com/")
    req.add_header("Cookie", cookies)
    
    print(f"[INFO] 쿠팡 LS 트랙오더 조회 요청 중... ({DATE})")
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            if res_data.get("succeed"):
                return res_data["data"]["content"]
            else:
                print(f"[ERROR] LS API 조회 실패: {res_data.get('message')}")
                return []
    except Exception as e:
        print(f"[ERROR] LS API HTTP 요청 실패 (쿠키 만료 가능성): {e}")
        return []

def download_ls_pdf(cookies, truck_request_id):
    """차량 운행확인서 PDF 다운로드"""
    url = f"https://ls.coupang.com/linehaul/slip/generate?truckRequestId={truck_request_id}&locale=ko_KR"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    req.add_header("Cookie", cookies)
    
    pdf_path = f"E:\\coding\\skill\\KPP\\slip_{truck_request_id}.pdf"
    print(f"[INFO] 차량 ID {truck_request_id} PDF 다운로드 시작...")
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            with open(pdf_path, 'wb') as f:
                f.write(response.read())
        print(f"[SUCCESS] PDF 저장 완료: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"[ERROR] PDF 다운로드 실패: {e}")
        return None

def extract_driver_info_from_pdf(pdf_path):
    """PyMuPDF를 사용하여 PDF 파일에서 기사명과 연락처 추출"""
    if not pdf_path or not os.path.exists(pdf_path):
        return None, None
    
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text() for page in doc])
        doc.close()
        
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        driver_name = ""
        driver_phone = ""
        
        for idx, line in enumerate(lines):
            if line == "성함" and idx + 1 < len(lines):
                driver_name = lines[idx+1]
            elif line == "연락처" and idx + 2 < len(lines):
                p1 = lines[idx+1]
                p2 = lines[idx+2]
                
                # 연락처 포맷 정리 (예: 010-3940-9811 구조 대응)
                if p1.startswith("010"):
                    if p2.isdigit() or "-" in p2:
                        driver_phone = p1 + p2
                    else:
                        driver_phone = p1
                else:
                    driver_phone = p1
                    
        # 특수 공백(\xa0) 등 제거
        driver_name = driver_name.replace('\xa0', '').strip()
        driver_phone = driver_phone.replace('\xa0', '').replace(' ', '').strip()
        
        return driver_name, driver_phone
    except Exception as e:
        print(f"[ERROR] PDF 텍스트 추출 실패 ({pdf_path}): {e}")
        return None, None


def main():
    print(f"\n========================================================")
    print(f" WPPS 출하통보등록 일괄 자동화 프로세스 시작 (날짜: {DATE})")
    print(f"========================================================")
    
    w = WPPS_CDP_FullAutomation()
    
    # 1. 크롬 디버거를 통한 실시간 쿠키 자동 획득
    ls_cookies = w.get_ls_cookies_from_browser()
    if not ls_cookies:
        print("[FAIL] 쿠키 자동 획득에 실패하여 프로세스를 중단합니다.")
        w.close()
        sys.exit(1)
        
    # 2. 쿠팡 LS API 조회하여 오늘자 보노하우스 출발 차량 정보 획득
    ls_vehicles = fetch_ls_vehicles(ls_cookies)
    if not ls_vehicles:
        print("[FAIL] 오늘 등록된 쿠팡 차량 데이터가 없습니다.")
        w.close()
        sys.exit(1)
        
    print(f"[INFO] 오늘 조회된 쿠팡 차량 건수: {len(ls_vehicles)}건")
    
    # 3. 각 차량의 상세 정보 파싱 (PDF 다운로드 및 텍스트 추출)
    final_vehicles_data = []
    
    # 차량 매칭용 호차 할당 규칙 (템플릿 기준 매칭)
    # 90626(5T) = 1호차, 90628(5T) = 2호차, 90269(11T) = 3호차
    hoche_rules = {
        90626: "1호차",
        90628: "2호차",
        90269: "3호차"
    }
    
    for v in ls_vehicles:
        tid = v.get("truckOrderTemplateId")
        hoche = hoche_rules.get(tid, "추가차량")
        
        # 차량번호 변환 (숫자만 6자리)
        raw_plate = v.get("truckInfo", {}).get("plateNumber", "")
        car_num = re.sub(r'[^0-9]', '', raw_plate)
        if len(car_num) > 6:
            # 뒷자리 6자리만 취하거나 하는 보정이 필요할 수 있으나, 일반적으로 '경기89바1454'에서 숫자는 6자리임
            pass
            
        ton = v.get("truckType", {}).get("name", "5T")
        qty = QTY_RULES.get(ton, 12)  # 5T=12개, 11T=14개 표준
        
        truck_req_id = v.get("truckRequestId")
        
        # PDF 다운로드 및 기사 정보 파싱
        pdf_file = download_ls_pdf(ls_cookies, truck_req_id)
        driver, phone = extract_driver_info_from_pdf(pdf_file)
        
        if not driver or not phone:
            print(f"[WARN] 차량 {raw_plate} (ID: {truck_req_id})의 기사 정보 파싱 실패. 수동 입력이 필요합니다.")
            continue
            
        print(f"[PARSED] {hoche} -> 차량: {raw_plate}(숫자: {car_num}), 기사: {driver}, 연락처: {phone}, 수량: {qty}")
        
        final_vehicles_data.append({
            "hoche": hoche,
            "car_num": car_num,
            "driver": driver,
            "phone": phone,
            "qty": qty,
            "raw_plate": raw_plate
        })
        
    if not final_vehicles_data:
        print("[FAIL] 유효한 차량 정보를 획득하지 못했습니다.")
        w.close()
        sys.exit(1)

    # 4. WPPS 페이지 조작 및 조회
    w.navigate(PBM_URL)
    w.handle_popups()
    w.override_dialogs()
    w.set_date(DATE)
    w.search()
    
    row_count = w.get_row_count()
    if row_count == 0:
        print("[WARN] 첫 조회 결과가 0개입니다. 재조회를 수행합니다. (SpreadJS 초기화 대응)")
        w.search()
        row_count = w.get_row_count()
        
    print(f"[INFO] WPPS 1차 조회된 행 수: {row_count}")
    print(f"[INFO] WPPS 1차 그리드 상태: {w.read_grid_data()}")
    
    # 5. 중복 차량 감지 및 삭제 처리 (삭제 조회 로직)
    # 2호차와 3호차 데이터가 이미 존재한다면 중복 제거를 위해 해당 차량들을 먼저 삭제 처리합니다.
    grid_snapshot = w.read_grid_data()
    duplicate_cars = []
    
    # 1호차(956464)는 완료된 정상 상태이므로 삭제 목록에서 원천 제외
    for vehicle in final_vehicles_data:
        if vehicle["car_num"] != "956464" and f"차량번호={vehicle['car_num']}" in grid_snapshot:
            print(f"[WARN] {vehicle['hoche']} ({vehicle['car_num']})가 이미 존재합니다. 삭제 작업을 선행합니다.")
            duplicate_cars.append(vehicle["car_num"])
            
    if duplicate_cars:
        w.screenshot(r"C:\Users\kis\AppData\Local\Temp\wpps_before_delete.png")
        w.delete_existing_hoche(duplicate_cars)
        
        # 삭제 후 재확인
        row_count = w.get_row_count()
        print(f"[INFO] 삭제 적용 후 최종 행 수: {row_count}")
        print(f"[INFO] 삭제 적용 후 그리드 상태: {w.read_grid_data()}")
        w.screenshot(r"C:\Users\kis\AppData\Local\Temp\wpps_after_delete.png")
    else:
        print("[INFO] 중복 차량 데이터가 없어 바로 입력을 진행합니다.")

    # 6. 차량 정보 일괄 등록 (성능 최적화: Batch Input)
    # 1호차가 행 index 0에 있는 경우, row_count=1이고 2호차/3호차는 각각 row_idx 1, 2에 순차 주입됩니다.
    # 만약 1호차조차 없는 완전 빈 상태라면 1호차부터 3호차까지 전부 새로 순차 주입됩니다.
    
    added_count = 0
    for vehicle in final_vehicles_data:
        # 이미 등록된 차량번호가 그리드에 남아있다면 스킵 (1호차 등)
        if f"차량번호={vehicle['car_num']}" in w.read_grid_data():
            print(f"[INFO] {vehicle['hoche']} ({vehicle['car_num']})는 이미 그리드에 올라와 있으므로 신규 추가를 건너뜁니다.")
            continue
            
        target_idx = row_count + added_count
        w.add_new_row()
        w.set_row_data(
            row_idx=target_idx,
            car=vehicle["car_num"],
            driver=vehicle["driver"],
            phone=vehicle["phone"],
            qty=vehicle["qty"],
            hoche=vehicle["hoche"]
        )
        added_count += 1

    print(f"[INFO] 일괄 데이터 주입 완료. 최종 저장 전 그리드 상태: {w.read_grid_data()}")
    
    # 7. 단 1회만 fn_save() 호출로 일괄 저장 (일괄 저장 최적화)
    if added_count > 0:
        w.screenshot(r"C:\Users\kis\AppData\Local\Temp\wpps_before_save.png")
        w.save()
        print(f"[INFO] 총 {added_count}개 행 일괄 저장 완료. 결과 검증을 위해 재조회 중...")
        
        # 8. 최종 결과 검증 및 저장 후 스크린샷 캡처
        w.search()
        final_count = w.get_row_count()
        print(f"[INFO] 저장 완료 후 최종 행 수: {final_count}")
        print(f"[INFO] 최종 그리드 상태: {w.read_grid_data()}")
        w.screenshot(r"C:\Users\kis\AppData\Local\Temp\wpps_after_save.png")
        
        final_snapshot = w.read_grid_data()
        all_registered = True
        for vehicle in final_vehicles_data:
            if f"차량번호={vehicle['car_num']}" not in final_snapshot:
                all_registered = False
                break
                
        if all_registered:
            print("[SUCCESS] 모든 차량의 출하통보등록 프로세스가 완벽하게 저장 및 확인되었습니다.")
        else:
            print("[ERROR] 최종 등록 확인 결과 누락된 차량이 존재합니다. KPP UI를 직접 확인하십시오.")
    else:
        print("[INFO] 신규 추가된 차량이 없어 저장을 수행하지 않고 종료합니다.")
    
    # 9. PDF 인쇄 (등록된 차량의 간선출차확인서 출력)
    if final_vehicles_data:
        print("\n=== PDF 인쇄 ===")
        for v_data, v_info in zip(final_vehicles_data, ls_vehicles):
            truck_req_id = v_info.get("truckRequestId", "")
            pdf_path = f"E:\\coding\\skill\\KPP\\slip_{truck_req_id}.pdf"
            if os.path.exists(pdf_path):
                w.print_pdf(pdf_path, title=v_data['hoche'])
                time.sleep(2)
        
    w.close()
    print("========================================================")

if __name__ == "__main__":
    main()

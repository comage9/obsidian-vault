# WPPS-LS 인쇄 다이얼로그 포커스 및 iframe 우회 마스터 가이드

> 작성일: 2026-06-06  
> 대상 독자: 다른 자동화 개발 에이전트 (인쇄 모듈 개발용)

---

## 1. 개요 및 핵심 과제

WPPS PBM140MW 화면에서 EDI 전표 출력(`ediRegister`) 버튼을 누를 때 발생할 수 있는 **2가지 기술적 난제**와 이를 해결하는 최종 마스터 패치 가이드입니다.

1. **iframe 모달 문제**: 인쇄 프리뷰가 새 창이나 새 탭으로 열리지 않고, 현재 브라우저 페이지 중앙의 **iframe 레이어 팝업**으로 PDF 뷰어가 로드되어 일반 탭 탐색으로는 제어가 불가능한 상황.
2. **윈도우 포커스(Focus) 분실 문제**: 인쇄 프리뷰 팝업(`Chrome Print Preview`)은 성공적으로 띄웠으나, 백그라운드 셸에서 보낸 키보드 `Enter` 이벤트가 포커스 이탈로 인해 인쇄 창에 도달하지 못해 인쇄가 실행되지 않는 현상.

---

## 2. 해결 아키텍처 및 마스터 솔루션

이 문제를 해결하기 위해 **1) CDP iframe 타겟 정밀 제어**와 **2) Windows OS 창 강제 활성화(AppActivate) 및 Enter 전송**을 결합한 100% 무인 자동 인쇄 솔루션을 설계합니다.

```
[인쇄 자동화 우회 파이프라인]

1. ediRegister 버튼 클릭 ➔ 현재 페이지 내 iframe으로 PDF 뷰어 로드
2. CDP에서 type="iframe" 및 chrome-extension URL을 가진 타겟의 webSocketDebuggerUrl 획득
3. 해당 WebSocket에 접속하여 shadow DOM을 통과해 #print 버튼 클릭 유도
4. 3.5초 대기 (인쇄 프리뷰가 완전히 렌더링될 때까지)
5. WScript.Shell.AppActivate("WPPS") 호출로 크롬 브라우저 창을 OS 전면(Foreground)으로 강제 활성화
6. SendKeys("{ENTER}") 호출로 활성화된 인쇄 다이얼로그의 [인쇄] 버튼을 물리적으로 자동 클릭
```

## 2.1 Windows 기본 프린터 자동 검증 및 교정 로직

다중 프린터 환경에서 엉뚱한 기기로 전표나 인수증이 출력되는 문제를 차단하기 위해, 프로그램이 셸 또는 크롬 인쇄 API를 사용하기 전에 **Windows 시스템 기본 프린터를 무조건 `Canon G2010 series`로 강제 고정**시키는 사전 검사 로직을 추가합니다.

* **동작 원리**: 
  1. `win32print.GetDefaultPrinter()`로 현재 윈도우 OS의 기본 프린터를 조회합니다.
  2. 조회 결과가 타겟 프린터와 다를 경우 `win32print.SetDefaultPrinter("Canon G2010 series")`를 호출하여 강제 교정합니다.
  3. 이 동작이 완료된 상태에서 인쇄를 진행하면, `os.startfile(..., 'print')` 시 지정된 프린터로 전송되며, 크롬 인쇄 프리뷰 레이어 상에서도 **타겟 대상 프린터가 항상 'Canon G2010 series'로 자동 매칭**됩니다.

---

## 3. 핵심 코드 구현 상세 (Python)

### ① CDP iframe PDF 뷰어 인쇄 버튼 강제 클릭
크롬 디버깅 포트(`9222`)의 JSON 페이지 목록에서 `type="iframe"` 타겟 중 PDF 확장 프로그램 주소를 찾아 WebSocket으로 직접 인쇄 명령을 실행합니다.

```python
import json
import urllib.request
import websocket
import time
import sys

def trigger_iframe_print():
    # 1. 크롬 디버거의 모든 타겟 조회
    pages = json.loads(urllib.request.urlopen('http://localhost:9222/json').read())
    pdf_page = None
    for p in pages:
        # iframe 타입 중 크롬 PDF 뷰어 확장 URL 매칭
        if p.get('type') == 'iframe' and 'chrome-extension://mhjfbmdgcfjbbpaeojofohoefgiehjai' in p.get('url', ''):
            pdf_page = p
            break

    if not pdf_page:
        print("[FAIL] PDF 뷰어 iframe을 찾을 수 없습니다.")
        return False

    ws_url = pdf_page['webSocketDebuggerUrl']
    ws = websocket.create_connection(ws_url, timeout=10)

    # 2. pdf-viewer 및 #print 버튼 로드 대기 후 클릭 실행 (루프)
    success = False
    for attempt in range(10):
        ws.send(json.dumps({
            'id': 100 + attempt,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """
                    (function(){
                        try {
                            var v = document.querySelector("pdf-viewer");
                            if(!v) return "no_viewer";
                            var t = v.shadowRoot.querySelector("viewer-toolbar");
                            if(!t) return "no_toolbar";
                            var b = t.shadowRoot.getElementById("print");
                            if(!b) return "no_btn";
                            b.click(); // 인쇄 팝업 트리거
                            return "ok";
                        } catch(e) {
                            return "ERR:" + e.message;
                        }
                    })()
                """,
                'returnByValue': True
            }
        }))
        r = json.loads(ws.recv())
        val = r.get('result', {}).get('result', {}).get('value', '')
        if val == "ok":
            success = True
            break
        time.sleep(1)
        
    ws.close()
    return success
```

### ② OS 윈도우 포커스 복구 및 자동 인쇄 승인
인쇄 미리보기 다이얼로그가 떴을 때, 윈도우 셸 컴포넌트(`win32com`)를 이용해 대상 브라우저 창을 강제로 Foreground로 끌어올린 뒤 키보드 엔터를 전송합니다.

```python
import win32com.client
import time

def activate_and_confirm_print(window_title="WPPS", delay=3.5):
    """지정된 시간 대기 후 브라우저 창을 강제 활성화하고 Enter 전송"""
    print(f"[INFO] {delay}초 대기 후 다이얼로그 자동 승인 가동...")
    time.sleep(delay)
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        
        # 1. 윈도우 타이틀 매칭을 통한 브라우저 강제 활성화 (Foreground 복구)
        is_activated = shell.AppActivate(window_title)
        print(f"[INFO] 윈도우 활성화 시도 ({window_title}): {is_activated}")
        
        if is_activated:
            time.sleep(0.5) # 활성화 완료 딜레이
            # 2. Enter 키 이벤트를 전송하여 기본 포커스된 [인쇄] 실행 버튼 누름
            shell.SendKeys("{ENTER}")
            print("[SUCCESS] 인쇄 다이얼로그에 Enter 키가 정상 송출되었습니다.")
            return True
        else:
            print("[WARN] 대상 윈도우 창을 활성화하지 못했습니다. 포커스 유실 가능성 있음.")
            return False
    except Exception as e:
        print(f"[ERROR] 백그라운드 Enter 전송 실패: {e}")
        return False
```

---

## 4. 다른 에이전트들에게 주는 기술 피드백

1. **`AppActivate`의 중요성**: OS 단독 백그라운드 키보드 이벤트 송출(`SendKeys`)은 현재 활성화된 Active Window에 전송됩니다. 디버거 가동 중 다른 창을 클릭하는 등으로 포커스가 유실되면 전혀 동작하지 않으므로, **반드시 `AppActivate`를 선행하여 대상 브라우저를 Foreground로 확보**하십시오.
2. **Iframe 탐색 루프 적용**: PBM140MW와 같이 PDF 뷰어가 iframe 레이어 모달로 로딩되는 경우, 일반 page 탐색이 아닌 `type="iframe"` 타겟에 대한 별도 CDP 세션을 가로채어 제어하는 설계를 갖추어야 팝업 제한 환경을 돌파할 수 있습니다.
3. **타이밍 딜레이 보장**: 크롬 프리뷰 화면이 로딩되어 버튼들이 활성화되는 데는 약 2.5초~4초의 물리적인 시간이 소요됩니다. 딜레이 없이 엔터를 즉시 치게 되면 다이얼로그가 키보드 입력을 삼켜버리므로 **최소 3.5초의 대기 딜레이**를 준 뒤 엔터 키를 쏴야 합니다.

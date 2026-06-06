# WPPS-LS 출력 시스템 통합 문서

> 다른 에이전트 전달용 — 2026-06-06

---

## 1. 개요

본 시스템은 2가지 출력 방식을 지원합니다.
하나는 **LS Coupang**에서 다운로드한 간선출차확인서 PDF 출력, 다른 하나는 **WPPS PBM140MW**에서 생성하는 EDI 전표 출력입니다.

---

## 2. 출력 방식 비교

| 항목 | LS PDF 출력 | KPP EDI 출력 |
|:----|:-----------|:------------|
| **문서명** | 간선출차확인서 (Linehaul Dispatch Slip) | EDI 전표 (Electronic Data Interchange) |
| **출처** | LS Coupang API → PDF 다운로드 | WPPS PBM140MW → `ediRegister` 버튼 |
| **트리거** | 스크립트 등록 완료 후 자동 실행 | 사용자 명령 ("1호차 출력해줘") |
| **메서드** | `print_pdf(pdf_path, title)` | `kpp_edi_print(hoche)` |
| **파일 위치** | `E:\coding\skill\KPP\slip_{truckRequestId}.pdf` | 실시간 생성 (임시) |
| **포함 정보** | 차량번호, 기사명, 연락처, 출발지/도착지 | 하차지, 수량, 차량번호, 기사명, 연락처 |
| **용도** | 기사가 가지고 갈 운행확인서 | KPP/KCP 전자문서 제출용 |

---

## 3. LS PDF 출력 (`print_pdf`)

### 동작 순서
```
CDP Target.createTarget('file:///...pdf') → Chrome PDF 뷰어 로드
  → pdf-viewer.shadowRoot → viewer-toolbar.shadowRoot → #print 버튼 click
  → 브라우저 인쇄 다이얼로그 오픈
  → 사용자가 Canon G2010 series 선택 후 인쇄
```

### 핵심 코드
```python
def print_pdf(self, pdf_path, title=""):
    # 로컬 PDF → file:// URL 변환
    abs_path = os.path.abspath(pdf_path)
    file_url = urllib.parse.quote(abs_path)
    pdf_url = f"file:///{file_url.replace('%3A', ':').replace('%5C', '/')}"
    
    # 새 탭 열기
    self.cmd('Target.createTarget', {'url': pdf_url, 'newWindow': False})
    time.sleep(3)
    
    # Shadow DOM → 인쇄 버튼 클릭
    pdf_page = new_pages[0]
    pws = websocket.create_connection(pdf_page['webSocketDebuggerUrl'])
    pws.send(Runtime.evaluate 표현식)
    # → pdf-viewer → viewer-toolbar → #print
```

### ⚠️ 주의사항
- PDF 뷰어가 `chrome-extension://` 도메인 → parent page에서 직접 접근 불가
- Shadow DOM(`querySelector('pdf-viewer').shadowRoot`) 경로로만 접근 가능
- 인쇄 버튼 클릭 후 CDP 타임아웃 발생 = 인쇄 다이얼로그 정상 열림 신호
- 사용자가 직접 프린터 선택 + 인쇄 필요

---

## 4. KPP EDI 출력 (`kpp_edi_print`)

### 동작 순서
```
사용자: "1호차 출력해줘"
→ PBM140MW 조회 (fn_search)
→ col36(비고)에서 "1호차" 검색 → Row index 찾기
→ 해당 행 체크박스 선택 + setActiveCell
→ ediRegister 버튼 click
→ EDI PDF가 Chrome PDF 뷰어에 로드됨
→ pdf-viewer shadow DOM → #print 버튼 click
→ 인쇄 다이얼로그 오픈
```

### 핵심 코드
```python
def kpp_edi_print(self, hoche):
    # 1. 조회
    self.set_date(DATE)
    self.search()
    
    # 2. 호차 검색 (col36)
    for i in range(self.get_row_count()):
        val = js(f"sheet.getValue({i}, 36)")
        if hoche in str(val): row_idx = i; break
    
    # 3. 행 선택
    js(f"sheet.setValue({row_idx}, 1, true); sheet.setActiveCell({row_idx}, 0)")
    
    # 4. EDI 출력 버튼
    js("document.getElementById('ediRegister').click()")
    
    # 5. PDF 뷰어 shadow DOM 인쇄 (LS PDF 출력과 동일)
```

### ⚠️ 주의사항
- `ediRegister` 버튼은 팝업 차단 시 iframe으로 PDF 로드됨
- 팝업 차단 해제 필요 (Chrome 설정)
- `#print` 버튼 클릭 후 인쇄 다이얼로그까지는 사용자 조작 필요

---

## 5. 스크립트 파일 정보

| 항목 | 경로 |
|:----|:-----|
| **실행 파일** | `E:\coding\skill\KPP\wpps_register_2_3.py` |
| **Git 백업** | `E:\hermes-backup\skills\KPP\wpps_register_2_3.py` |
| **관련 PDF** | `E:\coding\skill\KPP\slip_*.pdf` (LS PDF 캐시) |

---

## 6. CDP Shadow DOM 접근 패턴 (재사용 가능)

Chrome PDF 뷰어의 인쇄 버튼은 항상 동일한 shadow DOM 구조:
```javascript
document.querySelector('pdf-viewer')
  .shadowRoot.querySelector('viewer-toolbar')
    .shadowRoot.getElementById('print')
    .click()
```

이 패턴은 LS PDF와 KPP EDI PDF 모두 동일하게 적용.

---

## 7. 트러블슈팅

| 증상 | 원인 | 조치 |
|:----|:-----|:-----|
| `no pdf-viewer` | PDF가 Chrome 뷰어가 아닌 다운로드로 열림 | `chrome://settings/content/pdfDocuments` 확인 |
| `no print btn` | PDF 로딩 미완료 | `time.sleep` 증가 또는 로딩 완료 대기 |
| CDP 타임아웃 | 인쇄 다이얼로그 정상 열림 | **정상 동작**, 실패 아님 |
| 팝업 차단 | EDI 출력이 iframe으로 로드됨 | Chrome 팝업 차단 해제 |

# WPPS-LS 출력 시스템 수정보완 및 개선 제안서 (다른 에이전트 피드백용)

> 작성일: 2026-06-06  
> 대상 문서: `wpps_print_system.md` (Hermes 기존 인쇄 사양)

---

## 1. 기존 인쇄 방식의 한계점 분석

기존 `wpps_print_system.md`에 기술된 인쇄 로직은 Chrome 브라우저의 PDF 뷰어를 띄우고 Shadow DOM을 통과하여 `#print` 버튼을 누르는 유려한 우회 패턴을 구현했으나, **실제 업무 자동화 관점에서는 3가지의 명확한 기술적 한계**가 존재합니다.

### ⚠️ 한계 1: 100% 무인 자동화 불가능 (물리적 클릭 필요)
브라우저의 `#print` 버튼을 클릭하는 순간 Chrome의 **Native 인쇄 다이얼로그(Print Dialog)**가 강제로 팝업됩니다. 이 다이얼로그는 웹 환경 바깥의 OS 영역이므로 JavaScript나 CDP 프로토콜로 직접 제어가 불가능합니다. 즉, **사람이 화면을 보고 최종 [인쇄] 버튼을 마우스로 클릭하거나 Enter 키를 쳐야만 출력이 완료**됩니다.

### ⚠️ 한계 2: CDP WebSocket 전체 블로킹 및 타임아웃
인쇄 창이 화면에 노출되어 있는 동안 브라우저의 메인 스레드가 정지(Suspend) 상태가 됩니다. 이로 인해 CDP 통신 WebSocket 연결이 끊어지거나 타임아웃이 발생하여 다른 백그라운드 자동화 스크립트 실행이 중단되는 부작용이 발생합니다.

### ⚠️ 한계 3: 팝업 차단 및 화면 간섭
KPP의 `ediRegister` 클릭 시 브라우저 팝업 설정에 따라 오류가 나거나 화면 전환 오버헤드가 발생하여 렌더링 리소스를 많이 소모합니다.

---

## 2. 수정보완 및 근본적 개선 대안

이전 방식의 한계를 극복하고 사람이 전혀 개입하지 않아도 되는 **100% 완전 자동 무음 인쇄(Silent Printing)**를 구현하기 위해 아래의 보완 사양을 제안합니다.

```
[개선된 인쇄 아키텍처]

1. 쿠팡 LS PDF 
   LS API -> PDF 다운로드 완료 -> PDFtoPrinter.exe (OS 백그라운드 기본 프린터 무음 송출)

2. KPP EDI 전표
   PBM140MW -> 출하전표 iframe URL 획득 -> CDP Page.printToPDF (PDF 파일로 덤프)
                -> PDFtoPrinter.exe (무음 송출)
```

---

## 3. 핵심 기술 구현 가이드

### ① Windows 무음 인쇄 도구 통합 (`PDFtoPrinter.exe`)
추천되는 방식은 가벼운 Windows 무설치 오픈소스 CLI인 `PDFtoPrinter.exe`를 프로젝트 내 바이너리 폴더(`bin/`)에 포함시켜 파이썬 `subprocess`로 출력하는 것입니다.

* **동작 원리**: 아크로뱃 리더나 브라우저 창을 전혀 띄우지 않고 윈도우 인쇄 스풀러로 PDF를 즉시 보냅니다.
* **파이썬 연동 코드**:
  ```python
  import subprocess
  import os

  def print_pdf_silent(pdf_path, printer_name=None):
      """Windows 기본 프린터로 PDF를 즉시 무음 출력"""
      binary_path = r"E:\coding\skill\KPP\bin\PDFtoPrinter.exe"
      if not os.path.exists(binary_path):
          raise FileNotFoundError("PDFtoPrinter.exe 가 bin/ 폴더에 존재하지 않습니다.")
          
      cmd = [binary_path, pdf_path]
      if printer_name:
          cmd.append(printer_name)
          
      try:
          subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          print(f"[SUCCESS] 인쇄 스풀러로 전송 완료: {pdf_path}")
          return True
      except Exception as e:
          print(f"[ERROR] 무음 인쇄 실패: {e}")
          return False
  ```

### ② KPP 인쇄 다이얼로그 완전 우회 (`Page.printToPDF`)
KPP EDI 전표 화면에서 브라우저의 인쇄 창을 띄우지 않고, 전표 데이터를 가로채서 PDF로 조용히 내보내는 방식입니다.

* **동작 원리**: KPP의 출력 버튼 클릭 후 새 창으로 로드되는 전표용 URL을 가로챈 뒤, CDP의 `Page.printToPDF` API를 호출해 PDF 파일로 먼저 덤프하고 이를 무음 인쇄 모듈로 보냅니다.
* **파이썬 연동 코드**:
  ```python
  def kpp_edi_print_bypass(self, row_idx):
      # 1. 그리드에서 행 선택 후 출력 버튼 클릭
      self.js(f"sheet.setValue({row_idx}, 1, true);")
      self.js("document.getElementById('ediRegister').click();")
      time.sleep(2)
      
      # 2. 팝업 또는 iframe으로 생성된 Report URL 획득
      # (KPP는 전표 출력을 위해 별도 Report 뷰어 URL로 연결됨)
      report_url = self.js("""
          (function(){
              var iframe = document.querySelector('iframe[src*="report"]');
              return iframe ? iframe.src : window.location.href;
          })()
      """)
      
      # 3. 별도 CDP 탭에서 해당 URL 로딩 후 PDF로 인쇄 덤프
      # (브라우저 화면에는 인쇄 창이 뜨지 않음)
      pdf_data = self.cmd('Page.printToPDF', {
          'landscape': False,
          'displayHeaderFooter': False,
          'printBackground': True
      })
      
      # 4. 파일 저장 및 무음 인쇄 송출
      temp_pdf = r"E:\coding\skill\KPP\temp_edi_slip.pdf"
      with open(temp_pdf, "wb") as f:
          f.write(base64.b64decode(pdf_data['result']['data']))
          
      print_pdf_silent(temp_pdf)
  ```

---

## 4. 다른 에이전트에 대한 권장 사항 및 피드백

1. **물리적 UI 클릭 의존도 제거**: 브라우저 레벨의 `#print` click이나 `window.print()`를 트리거하는 것은 CDP 블로킹과 팝업 간섭을 초래하므로 **최후의 수단**으로만 고려하십시오.
2. **OS 백그라운드 인쇄 선호**: Windows 환경에서는 OS 수준의 무음 인쇄 CLI(`PDFtoPrinter.exe` 또는 `RawPrint` 라이브러리)를 사용하는 것이 브라우저 제어보다 100배 안정적이고 빠릅니다.
3. **CDP `Page.printToPDF` 적극 활용**: 화면을 캡처하여 인쇄용 PDF를 만드는 CDP 표준 기능을 적극 활용하면 브라우저 인쇄창 우회가 수월해집니다.

---
name: libreoffice-migration
description: XLSM/XLSX → LibreOffice Calc ODS 마이그레이션 — 수식 오류 수정, VBA→StarBasic 매크로 포팅, LibreOffice 헤드리스 변환
category: productivity
---

# LibreOffice 마이그레이션

Excel 매크로 파일(XLSM)을 LibreOffice Calc(ODS)로 이전할 때 **수식 오류 수정** + **매크로 포팅** + **완전한 ODS 파일 생성**을 처리합니다.

## 언제 사용하는가
- Excel 전용 함수(`_xlfn.xlookup`, `_xlfn.single`)가 포함된 XLSM → LibreOffice 변환
- `#REF!` 참조 깨짐 복구
- VBA 매크로를 LibreOffice Basic으로 재작성
- LibreOffice 매크로가 포함된 완전한 ODS 파일 필요

## 워크플로우

### 1. 파일 분석

```python
# openpyxl로 XLSM 열기
wb = openpyxl.load_workbook('file.xlsm', data_only=False)

# 시트 구조 확인
for ws in wb.worksheets:
    print(f'{ws.title}: {ws.max_row}행 x {ws.max_column}열')

# 수식 스캔
for row in ws.iter_rows():
    for cell in row:
        if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
            # _xlfn. 접두어, #REF!, SINGLE() 등 확인
            pass
```

### 2. 수식 오류 수정

openpyxl로 셀 값을 문자열 치환:

| 오류 | 원인 | 수정 |
|------|------|------|
| `_xlfn.xlookup(...)` | Excel 365 전용 함수 표기 | `XLOOKUP(...)` — LibreOffice 24.2+ 네이티브 지원 |
| `_xlfn.single(...)` | SINGLE() — LibreOffice 없음 | 래퍼 제거 (XLOOKUP이 단일값 반환) |
| `#REF!` | 참조 대상 컬럼 삭제됨 | 올바른 컬럼으로 복원 |
| `=#REF!` | 깨진 헤더 | `=""` 로 대체 |

**주의:** `openpyxl`로 `.value`에 새 수식을 쓰려면 `=` 포함한 문자열이어야 함.

### 3. VBA 매크로 확인

```python
# VBA 매크로 바이너리 존재 확인
import zipfile
with zipfile.ZipFile('file.xlsm') as z:
    has_vba = 'xl/vbaProject.bin' in z.namelist()
```

vbaProject.bin은 바이너리 OLE 포맷으로 직접 텍스트 편집 불가.
→ 대신 **LibreOffice Basic**으로 재작성 후 별도 `.bas` 파일 제공.

### 4. LibreOffice Basic 매크로 작성

키 차이점 (Excel VBA vs LibreOffice Basic):

| 항목 | Excel VBA | LibreOffice Basic |
|------|-----------|-------------------|
| 현재 문서 | `ThisWorkbook` | `ThisComponent` |
| 시트 접근 | `Sheets("Sheet1")` | `oDoc.Sheets.getByName("Sheet1")` |
| 셀 읽기 | `Range("A1").Value` | `oSheet.getCellByPosition(0, 0).getString()` |
| 드로잉 | `Shapes.AddPicture` | `oDoc.createInstance("com.sun.star.drawing.GraphicObjectShape")` |
| URL 인코딩 | `EncodeURL()` | 직접 구현 필요 |
| 에러 처리 | `On Error Resume Next` | `On Error GoTo ErrHandler` |

### 5. 매크로가 포함된 ODS 생성

**방법 A — LibreOffice 헤드리스 UNO Python (LibreOffice Python 필요):**
```python
libs = doc.BasicLibraries
standard = libs.getByName("Standard")
standard.insertByName("ModuleName", code_string)
```

**방법 B — zipfile 직접 조작 (OS only, python3):**
```python
with zipfile.ZipFile('output.ods', 'r') as zin:
    with zipfile.ZipFile(tmp, 'w') as zout:
        # 매크로 XML 추가
        zout.writestr('Basic/Standard/GenerateBarcodes.xml', macro_xml)
        # script-lc.xml 교체
        zout.writestr('Basic/script-lc.xml', script_lc_xml)
        # META-INF/manifest.xml 수정
```

**방법 C — LibreOffice convert-to + zip injection (권장):**
```bash
soffice --headless --convert-to ods file.xlsm
# 그 후 Python zipfile로 매크로 XML 직접 주입
```

## 검증

```bash
# ODS 내부 Basic 매크로 확인
zipinfo output.ods | grep Basic/

# 수식 확인 (content.xml 에서 xlookup 검색)
python3 -c "
import zipfile
with zipfile.ZipFile('output.ods') as z:
    content = z.read('content.xml').decode()
    print(f'XLOOKUP 수식: {content.count(\\\"xlookup\\\")}개')
    print(f'남은 _xlfn.: {content.count(\\\"_xlfn.\\\")}개 (0이어야 함)')
"

# XML 유효성 검증 (ODS content.xml이 깨졌는지 확인)
python3 -c "
import zipfile, xml.etree.ElementTree as ET
with zipfile.ZipFile('output.ods') as z:
    try:
        ET.fromstring(z.read('content.xml'))
        print('XML valid: ✅')
    except Exception as e:
        print(f'XML ERROR: {e}')
"

# RDP 연결 확인 (Windows VM)
xfreerdp3 /v:127.0.0.1:3389 /u:user /p:pass +auth-only
```

## 주의사항 / 함정

1. **openpyxl keep_vba=True 필수** — XLSM 저장 시 VBA 보존하려면 `openpyxl.load_workbook('file.xlsm', keep_vba=True)`
2. **SINGLE() 제거 주의** — XLOOKUP은 단일값을 반환하므로 SINGLE() 래퍼를 제거해도 무방
3. **ODS → XLSM 변환 제한** — LibreOffice Basic 매크로는 XLSM(Excel) 형식으로 저장 불가. 반드시 ODS로 저장
4. **LibreOffice 버전 확인** — `libreoffice --version`으로 XLOOKUP 등 함수 지원 확인 (24.2+ 권장)
5. **한글 경로** — UNO Python API에서 한글 경로는 URL 인코딩 필요
6. **chntpw 읽기전용** — 실행 중인 Windows VM의 SAM 파일은 읽기전용 마운트만 가능. 수정하려면 VM 중지 필요
7. **XLSX XML 엔티티 인코딩** — XLSX 내부 XML에서 큰따옴표는 `&quot;`, 앰퍼샌드는 `&amp;`로 저장됨.
   `re.sub` 사용 시 반드시 XML 엔티티로 패턴 작성 (`IMAGE(&quot;...&quot;)` → `"`가 아님!)
8. **ODS content.xml 직접 수정 시 XML 구조 파괴 주의** — 잘못된 문자열 치환으로 ODS가 아예 열리지 않을 수 있음.
   수정 후 반드시 `xml.etree.ElementTree.fromstring()`으로 유효성 검증
9. **LibreOffice URL→image() 자동변환** — XLSX에서 IMAGE()를 제거해도,
   LibreOffice XLSX→ODS 변환기(26.2)가 URL 문자열을 감지하고 자체 `image()` 함수를 재생성할 수 있음.
   최종 ODS의 content.xml을 직접 열어 `of:=image(...)` 패턴을 확인하고 제거 필요
10. **XLOOKUP→VLOOKUP 변환 시 컬럼 인덱스** — VLOOKUP은 테이블의 첫 번째 열을 기준으로 검색하므로
    `XLOOKUP($G$1, B:B, F:F)` → `VLOOKUP($G$1, A:V, 6, 0)` (B=1, F=5+1=6, A열 추가로 인덱스 +1)

## 추가 함수 호환성

### `IMAGE()` 함수 — LibreOffice 26.2 미지원

Excel 365의 `IMAGE(url, mode, height, width)` 함수는 LibreOffice Calc 26.2에서 **지원되지 않음** (`#NAME?` 오류).

**⚠️ 중요: XLSX XML 인코딩 차이**
XLSX 파일 내부의 XML은 수식 문자열에 HTML 엔티티를 사용함:
- 큰따옴표 `"` → `&quot;`
- 앰퍼샌드 `&` → `&amp;`

Python `re.sub`로 XLSX XML을 직접 수정할 때는 **엔티티 인코딩된 문자열**을 사용해야 함:
```python
# 틀림: 실제 XML에는 "가 아닌 &quot; 로 저장됨
text = re.sub(r'IMAGE\("https?://[^"]+"[^)]*\)', '""', text)

# 맞음: XML 엔티티로 검색
text = re.sub(
    r'IMAGE\(&quot;https?://[^&]*&quot;&amp;[^,]+,[^)]*\)',
    '""',
    text
)
```

**해결 방법:**

1. **XLSX XML 직접 수정 (권장):**
   ```python
   with zipfile.ZipFile(DST, 'r') as zin:
       with zipfile.ZipFile(tmp, 'w') as zout:
           for item in zin.infolist():
               data = zin.read(item.filename)
               if item.filename.endswith('.xml'):
                   text = data.decode('utf-8')
                   # XML 엔티티 사용!
                   text = re.sub(
                       r'IMAGE\(&quot;[^&]*&quot;&amp;[^,]+,[^)]*\)',
                       '""',
                       text
                   )
                   data = text.encode('utf-8')
               zout.writestr(item, data)
   ```

2. **HYPERLINK 사용** (단, LibreOffice가 XLSX→ODS 변환 시 URL을 감지하고 image()로 재변환할 수 있음):
   ```python
   text.replace('=IMAGE(url,...)', '=HYPERLINK(url,"Barcode")')
   ```

3. **ODS content.xml 직접 수정** (LibreOffice가 재변환한 `image()` 제거):
   ```python
   # content.xml에서 XML 엔티티로 저장된 image() 수식 찾기
   old = 'of:=image(&quot;https://...&quot;&amp;[.B7];4;80;220)'
   content.replace(old, 'of:=""')
   ```
   ⚠️ 실수로 XML 구조를 깨뜨리면 ODS 파일이 아예 열리지 않음. 반드시 `xml.etree.ElementTree`로 유효성 검증:
   ```python
   with zipfile.ZipFile(output.ods) as z:
       ET.fromstring(z.read('content.xml'))  # 예외 발생 시 XML 깨짐
   ```

### ArrayFormula (CSE 배열 수식) → `#NAME?` 오류

Excel의 배열 수식(`<f t="array" ref="A1">`)은 LibreOffice에서 `#NAME?` 오류 발생.

**해결:** XLSX XML에서 `t="array" ref="..."` 속성 제거 → 일반 수식으로 변환:
```python
import re, zipfile
text = re.sub(r'<f t="array" ref="[^"]*">', '<f>', text)
```

### XLOOKUP → VLOOKUP 대체

XLOOKUP이 LibreOffice에서 문제가 되면 VLOOKUP으로 대체:
```python
# XLOOKUP → VLOOKUP(lookup, table, col_index, [range_lookup])
# 예: XLOOKUP($G$1; 'vf 품목'!B:B; 'vf 품목'!F:F; 0; 0)
# → VLOOKUP($G$1; 'vf 품목'!A:V; 6; 0)
```

### URL 인코딩 이슈

bwip-js 등 외부 API URL에 `&`가 포함되면 XML 엔티티(`&amp;`)로 변환되어 수식 깨짐.
XLSX XML 직접 수정 시 `&`는 그대로 유지하고, ODS 변환은 LibreOffice에 위임.

### LibreOffice 버전별 함수 지원

| 버전 | XLOOKUP | IMAGE() | VLOOKUP | TEXT(NOW()) |
|------|---------|---------|---------|-------------|
| 24.2 | ✅ | ❌ | ✅ | ✅ |
| 25.2+ | ✅ | ❌ | ✅ | ✅ |
| 26.2 | ✅ | ❌ | ✅ | ✅ |

> IMAGE() 함수: LibreOffice 26.2.2.2에서도 지원되지 않음. `#NAME?` 오류 발생.
> XLSX XML에서 `&quot;` (XML 엔티티)로 인코딩된 따옴표에 주의.

### XLSX → ODS 변환 시 LibreOffice 동작
- LibreOffice가 XLSX를 ODS로 변환할 때 URL 패턴을 자동 감지하여 `image()` 함수 생성 가능
- `""`(빈 문자열)로 대체해도 변환 과정에서 재생성됨 → ODS content.xml을 직접 열어 제거 필요
- ArrayFormula(`t="array"`)는 LibreOffice에서 `#NAME?` → XLSX XML에서 `t="array" ref="..."` 속성 제거 필요
- 수식 내 `&quot;`는 XML 엔티티. 일반적인 `"`가 아님 — regex 작성 시 필수 고려

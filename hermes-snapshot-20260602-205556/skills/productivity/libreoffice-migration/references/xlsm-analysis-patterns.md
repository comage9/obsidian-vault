# XLSM 분석 패턴 (openpyxl)

## 시트별 수식 스캔
```python
wb = openpyxl.load_workbook('file.xlsm', data_only=True)
ws = wb['VF']
for row in range(1, ws.max_row+1):
    for col in range(1, ws.max_column+1):
        c = ws.cell(row, col)
        if c.value and isinstance(c.value, str) and c.value.startswith('='):
            print(f'{get_column_letter(col)}{row}: {c.value}')
```

## 수치 데이터 확인 (data_only=True)
```python
wb = openpyxl.load_workbook('file.xlsm', data_only=True)
# data_only=True면 수식 결과 값(=캐시된 값)을 반환, 수식 자체가 아님
```

## VBA 모듈 추출 (vbaProject.bin)
```python
with zipfile.ZipFile('file.xlsm') as z:
    vba_data = z.read('xl/vbaProject.bin')
    # 바이너리 OLE 포맷 — 텍스트 편집 불가
```

## 수식 일괄 수정 패턴
```python
for row in ws.iter_rows():
    for cell in row:
        if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
            old = cell.value
            new = old
            new = new.replace('_xlfn.xlookup', 'XLOOKUP')
            new = new.replace('_xlfn.single', 'SINGLE')
            new = new.replace('_xlfn.', '')
            # SINGLE(...) → inner
            while 'SINGLE(' in new:
                start = new.index('SINGLE(')
                depth = 1; i = start + 7
                while depth > 0 and i < len(new):
                    if new[i] == '(': depth += 1
                    elif new[i] == ')': depth -= 1
                    i += 1
                inner = new[start+7:i-1]
                new = new[:start] + inner + new[i:]
            # #REF! → 올바른 참조
            if '#REF!' in new and cell.column == 8:
                new = re.sub(r"XLOOKUP\\(([^,]+),#REF!,#REF!\\)",
                    r"XLOOKUP(\\1,'참조시트'!$B:$B,'참조시트'!$J:$J)", new)
            if new != old:
                cell.value = new
wb.save('output.xlsm')
```

## XLSX XML 직접 수정 (XLOOKUP→VLOOKUP 변환 예시)

XLSX 파일은 ZIP 형식이며, 내부 XML에서 수식을 직접 수정할 수 있음.
**반드시 XML 엔티티 인코딩 사용** (`"` → `&quot;`, `&` → `&amp;`):

```python
import zipfile, re, tempfile

shutil.copy2(SRC, DST)
tmp = tempfile.mktemp()
with zipfile.ZipFile(DST, 'r') as zin:
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith('.xml'):
                text = data.decode('utf-8')
                # XLOOKUP→VLOOKUP (XML 엔티티 주의: 따옴표는 &quot;)
                text = re.sub(
                    r'XLOOKUP\(\$G\$1,\'vf 품목\'!B:B,\'vf 품목\'!F:F,0,0\)',
                    'VLOOKUP($G$1,\'vf 품목\'!A:V,6,0)', text)
                # XLOOKUP(G$1, range, range, 0) 형태
                text = re.sub(
                    r'XLOOKUP\(G\$1,\'vf 품목\'!B\$2:B\$922,\'vf 품목\'!S\$2:S\$922,0\)',
                    'VLOOKUP(G$1,\'vf 품목\'!A$2:V$922,19,0)', text)
                # IMAGE(&quot;...&quot;&amp;B7,...) → ""  (XML 엔티티!)
                text = re.sub(
                    r'IMAGE\(&quot;[^&]*&quot;&amp;[^,]+,[^)]*\)',
                    '""', text)
                data = text.encode('utf-8')
            zout.writestr(item, data)
shutil.move(tmp, DST)
```

### ArrayFormula (CSE 배열 수식) 처리

Excel 배열 수식(`<f t="array" ref="A1">`)은 LibreOffice에서 `#NAME?` 오류 발생.
XLSX XML에서 `t="array" ref="..."` 속성을 제거하여 일반 수식으로 변환:

```python
text = re.sub(r'<f t="array" ref="[^"]*">', '<f>', text)
```

### xlookup 함수명 소문자 이슈

LibreOffice ODS 형식에서 `xlookup` (소문자)는 LibreOffice 26.2에서 정상 동작.
그러나 XLSX에서 `XLOOKUP` (대문자)을 사용하면 LibreOffice가 ODS 변환 시
자동으로 `xlookup`으로 변환함. 별도 조치 불필요.

### VLOOKUP 변환 시 컬럼 인덱스 매핑

| XLOOKUP 반환 열 | VLOOKUP 컬럼 인덱스 | 설명 |
|:---:|:---:|---|
| `'vf 품목'!E:E` | 5 | 품목명 |
| `'vf 품목'!F:F` | 6 | 제품명 |
| `'vf 품목'!J:J` | 10 | 생산단위(Pcs/BOX) |
| `'vf 품목'!S:S` | 19 | 영문명 |
| `'vf 품목'!A:V` 전체 | — | VLOOKUP 테이블 범위 |

## #REF! 참조 복원 규칙
- H열 (Pcs/BOX) = 생산단위 → `'vf 품목'!$J:$J`
- D열 (품목명) → `'vf 품목'!$E:$E`
- K열 (영문명) → `'vf 품목'!$F:$F` (또는 $S:$S)
- 복원 불가 시 데이터 시트의 컬럼 헤더를 분석하여 매핑

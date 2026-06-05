---
name: libreoffice-excel-migration
description: Fix Excel formulas and macros for LibreOffice Calc compatibility. Covers XLOOKUP/SINGLE migration, #REF! repair, VBA→StarBasic porting, and XLSM→ODS conversion with embedded macros.
category: software-development
---

# LibreOffice Excel Migration

Fix Excel `.xlsm`/`.xlsx` files to work correctly in LibreOffice Calc.

## Common Formula Fixes

### `_xlfn.xlookup()` → XLOOKUP
Excel uses `_xlfn.` prefix for newer functions. LibreOffice has native `XLOOKUP` support (LO 24.2+).

```python
# Using openpyxl with keep_vba=True (preserves macros)
wb = openpyxl.load_workbook('file.xlsm', keep_vba=True)
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                cell.value = cell.value.replace('_xlfn.xlookup', 'XLOOKUP')
                cell.value = cell.value.replace('_xlfn.', '')
wb.save('fixed.xlsm')
```

### `_xlfn.single()` → Remove wrapper
`SINGLE()` extracts a single value from an array. `XLOOKUP` already returns a single value, so the wrapper is redundant. Replace `SINGLE(XLOOKUP(...))` → `XLOOKUP(...)`.

### LibreOffice ODS Formula Conversion
When converting XLSM→ODS via `soffice --convert-to ods`, LibreOffice automatically:
- Removes `_xlfn.` prefix
- Converts formulas to native ODS `of:=` format
- Transforms `XLOOKUP(A7,'vf 품목'!$B:$B,'vf 품목'!$E:$E)` into `xlookup([.A7];[$'vf 품목'.$B:.$B];[$'vf 품목'.$E:.$E])`
- Removes `SINGLE()` wrappers automatically

**After conversion**, verify by checking `content.xml`:
```python
import zipfile
with zipfile.ZipFile('output.ods') as z:
    content = z.read('content.xml').decode('utf-8')
    print(content.count('_xlfn.'))  # should be 0
    print(content.count('#REF!'))   # should be 0 (false positives in xmlns ok)
```

### `#REF!` Broken References
When columns/ranges were deleted in Excel, formulas show `#REF!`. Fix by:
1. Determine the correct target column (e.g., `'vf 품목'!$J:$J` for 생산단위/production-unit)
2. Replace `#REF!` → correct absolute reference
3. Use `re.sub(r'XLOOKUP\(([^,]+),#REF!,#REF!\)', r'XLOOKUP(\1,\'Sheet\'!$B:$B,\'Sheet\'!$J:$J)', formula)`

## XLSM → ODS Conversion with Macros

### Method 1: LibreOffice Headless (recommended)
```bash
soffice --headless --norestore --convert-to ods:calc8 file.xlsm
```
Then inject StarBasic macros via zipfile XML manipulation.

### Method 2: openpyxl (formulas only, VBA preserved)
```python
wb = openpyxl.load_workbook('file.xlsm', keep_vba=True)
# Fix formulas...
wb.save('fixed.xlsm')
```

### Method 3: Manual zipfile ODS macro injection
Insert StarBasic module into ODS:
```python
with zipfile.ZipFile('output.ods', 'a') as z:
    z.writestr('Basic/Standard/MyMacro.xml', macro_xml_content)
```

The macro XML format:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script"
    script:name="ModuleName" script:language="StarBasic">
    ' StarBasic code here (HTML-encoded: &amp;=&amp;, &gt;=&gt;, &lt;=&lt;, &quot;=&quot;)
</script:module>
```

Update `Basic/script-lc.xml` and `META-INF/manifest.xml` to register the new module.

### StarBasic URL Encoding Function
For web API calls from StarBasic (e.g., bwip-js barcode API), use a custom URL encoder:
```vba
Function UrlEncode(ByVal sText As String) As String
    Dim sResult As String
    Dim i As Long
    Dim sChar As String
    Dim iChar As Integer
    sResult = ""
    For i = 1 To Len(sText)
        sChar = Mid(sText, i, 1)
        iChar = Asc(sChar)
        If (iChar >= 65 And iChar <= 90) Or _
           (iChar >= 97 And iChar <= 122) Or _
           (iChar >= 48 And iChar <= 57) Or _
           iChar = 45 Or iChar = 46 Or _
           iChar = 95 Or iChar = 126 Then
            sResult = sResult & sChar
        ElseIf iChar = 32 Then
            sResult = sResult & "%20"
        Else
            sResult = sResult & "%" & Hex(iChar)
        End If
    Next i
    UrlEncode = sResult
End Function
```

## VBA → StarBasic Conversion

| VBA | StarBasic (LibreOffice) |
|-----|------------------------|
| `ThisWorkbook` | `ThisComponent` |
| `Worksheets("name")` | `Sheets.getByName("name")` |
| `Range("A1")` | `getCellByPosition(0, 0)` |
| `Cells(row, col)` | `getCellByPosition(col-1, row-1)` |
| `Application.xxx` | `ThisComponent.xxx` |
| `MsgBox "text"` | `MsgBox "text", 64, "title"` |
| `CreateObject(...)` | `createUnoService(...)` |
| `WithEvents` | Not supported (use listeners) |
| `Worksheet_Change` | Sub `Modified()` or event listeners |

## Known Pitfalls
- **XLSM VBA macros are NOT preserved in ODS** (they become VBAProject modules with VBASupport=1). For pure StarBasic, save as ODS and import macro separately.
- **`SOFFICE` headless conversion may strip `_xlfn.` prefix** and convert formulas to LO's `of:=` format automatically. Check `content.xml` after conversion.
- **Unicode in StarBasic** - `Asc()` returns Unicode code point. For URL encoding, `Hex(Asc(char))` works for BMP characters.
- **openpyxl preserve_vba** only works for `.xlsm` format, not `.xlsx`.
- **Auto-logon in autounattend.xml** may have password encoding bugs in dockur/windows - see `windows-vm-docker` skill.
- **`IMAGE()` auto-recreation**: LibreOffice's XLSX→ODS converter auto-detects URL text in cells and wraps them in an `image()` function with wrong parameter ordering (Excel: `url, mode, h, w` → LO: `url, width, height, mode`). Fix: strip the URL text from XLSX XML before conversion using XML-entity-aware regex (`&quot;` not `"`).

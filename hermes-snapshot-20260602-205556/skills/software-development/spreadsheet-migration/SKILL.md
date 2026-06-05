---
name: spreadsheet-migration
description: Fix Excel formulas (XLOOKUP, SINGLE, #REF! errors) for LibreOffice Calc and inject StarBasic macros into ODS files
tags:
  - excel
  - libreoffice
  - formula
  - migration
  - xlsm
  - ods
  - macro
related_skills:
  - cross-platform-project-migration
  - subagent-driven-development
---

# Spreadsheet Migration (Excel → LibreOffice)

## Triggers

Use this skill when a user asks you to:
- Fix Excel formulas that break in LibreOffice Calc
- Convert `.xlsm` / `.xlsx` to `.ods` with formulas working
- Embed a StarBasic macro into a spreadsheet file
- Fix `#REF!`, `#NAME?`, or `_xlfn.` errors in formulas
- Make a VBA macro work in LibreOffice
- "수식과 오류를 리브오피스에 맞게 수정"

## Workflow Priority (CRITICAL)

When a user asks you to fix a spreadsheet file, do NOT start with the macro.
The order MUST be:

**1. Fix FORMULAS first** — data errors make the file unusable.
   - Scan all sheets for `_xlfn.`, `#REF!`, `SINGLE()` issues
   - Fix with openpyxl (keep_vba=True)
   - Save as .xlsm, then convert to .ods

**2. Fix MACROS second** — macros are useless if the spreadsheet data is broken.
   - Audit VBA → StarBasic conversion needs
   - Create corrected .bas file
   - Embed into ODS via zipfile or UNO

**3. Verify BOTH** before presenting to the user.
   - Formulas: check content.xml for remaining errors
   - Macro: verify it appears in Basic/Standard/

⚠️ User will express strong frustration if you fix macros only and ignore formula errors.

## Diagnostic Flow

### 1. Identify Common Excel-Only Formula Constructs

Open the file with openpyxl and scan for problematic patterns:

```python
import openpyxl
wb = openpyxl.load_workbook(file, data_only=False)

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                f = cell.value
                issues = []
                if '_xlfn.' in f:               issues.append('xlfn_prefix')
                if '#REF!' in f:                 issues.append('ref_error')
                if '_xlfn.single(' in f:         issues.append('single_func')
                if issues:
                    record(cell, issues)
```

**Formula constructs that break in LibreOffice:**

| Excel construct | LibreOffice issue | Fix |
|---|---|---|---|
| `_xlfn.xlookup(...)` | `_xlfn.` prefix = future-function marker; LO doesn't recognize it | Strip `_xlfn.` → `XLOOKUP(...)` |
| `_xlfn.single(...)` | SINGLE() is Excel-365-only; LO has no equivalent | Remove SINGLE() wrapper entirely (XLOOKUP already returns scalar) |
| `=#REF!` | Broken reference (deleted column/range) | Restore correct range reference |
| `XLOOKUP(..., #REF!, #REF!)` | Lookup array is a broken reference | Replace #REF! with the correct column (see vf 품목 pattern below) |
| `IMAGE(url, mode, h, w)` | IMAGE() is Excel-365-only; LO 24.2+ supports it with different syntax | LO syntax: `IMAGE(url; width; height; mode)`. LO 26.2 handles both syntaxes. Verify by checking the ODS after conversion. |
| `TEXT(NOW(), "YY-MM-DD")` | Works in LO | No change needed — both Excel and LO support this |
| `ArrayFormula` (implicit intersection) | openpyxl may show `<openpyxl.worksheet.formula.ArrayFormula>` | No change needed — LO handles array formulas natively |

### 2. Fix Formulas with openpyxl

**Step 1: Load with VBA preservation:**
```python
wb = openpyxl.load_workbook('file.xlsm', keep_vba=True)
```

**Step 2: Apply fixes per cell:**

```python
import re
from openpyxl.utils import get_column_letter

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                old = cell.value
                new = old

                # Fix 1: Strip _xlfn. prefix
                new = new.replace('_xlfn.xlookup', 'XLOOKUP')
                new = new.replace('_xlfn.single', 'SINGLE')
                new = new.replace('_xlfn.', '')

                # Fix 2: Unwrap SINGLE(XLOOKUP(...)) → XLOOKUP(...)
                while 'SINGLE(' in new:
                    start = new.index('SINGLE(')
                    depth = 1
                    i = start + 7
                    while depth > 0 and i < len(new):
                        if new[i] == '(': depth += 1
                        elif new[i] == ')': depth -= 1
                        i += 1
                    inner = new[start+7:i-1]
                    new = new[:start] + inner + new[i:]

                # Fix 3: Replace #REF! with correct lookup column
                if '#REF!' in new and 'XLOOKUP' in new:
                    # Typical pattern: XLOOKUP(A7, #REF!, #REF!)
                    # Restore to: XLOOKUP(A7, 'vf 품목'!$B:$B, 'vf 품목'!$J:$J)
                    new = re.sub(
                        r'XLOOKUP\(([^,]+),#REF!,#REF!\)',
                        r"XLOOKUP(\1,'vf 품목'!$B:$B,'vf 품목'!$J:$J)",
                        new
                    )

                if new != old:
                    cell.value = new
```

**Common mapping for `vf 품목` sheet columns when #REF! occurs:**
- Column B: 제품코드 (product code) — always the lookup key
- Column E: 바코드 / 제품명
- Column F: 제품명 / 영문명
- Column J: 생산단위 (production unit / pcs per box) — frequently the broken H-column lookup
- Column S: 영문명

If the exact column can't be determined, read the `vf 품목` sheet headers (row 2 contains real headers, row 1 may contain auto-generated "Column1", "Column2", ...).

**Step 3: Save:**
```python
wb.save('fixed.xlsm')
```

### 3. VBA Macro Audit

Macros are stored in `xl/vbaProject.bin` (binary OLE container). openpyxl preserves them with `keep_vba=True` but cannot read/modify VBA source code.

**What to check for LibreOffice compatibility:**

| VBA API | LibreOffice equivalent |
|---|---|
| `Range("A1")` | `oSheet.getCellByPosition(0, 0)` |
| `Range("A1:B2")` | `oSheet.getCellRangeByPosition(0,0,1,1)` |
| `Worksheets("Sheet1")` | `oDoc.Sheets.getByName("Sheet1")` |
| `ThisWorkbook` | `ThisComponent` |
| `MsgBox "text"` | `MsgBox "text"` (same syntax) |
| `Application.ScreenUpdating` | `oDoc.lockControllers()` / `unlockControllers()` |
| `WorksheetFunction.XLookup` | Use worksheet formula or `xlookup()` function call |

**Common VBA-to-StarBasic pitfalls:**
- `Range().Select` / `Selection` pattern — use direct cell access instead
- `ActiveSheet` → `ThisComponent.CurrentController.getActiveSheet()`
- `Cells(row, col)` → `oSheet.getCellByPosition(col-1, row-1)` (LO is 0-indexed)
- `Dim rng As Range` → `Dim oCell As Object`

### 4. Convert XLSM to ODS

**Method 1 — LibreOffice CLI (recommended):**
```bash
soffice --headless --norestore \
  --convert-to ods:calc8 \
  --outdir /output/dir \
  input.xlsm
```

This produces `input.ods`. The conversion preserves Excel formulas by translating them to LibreOffice's native `of:=` format (e.g., `XLOOKUP([.A7];[$'vf 품목'.$B:.$B];[$'vf 품목'.$E:.$E])`).

The `_xlfn.` prefix and `SINGLE()` wrapper are automatically handled by the openpyxl fix in step 2 — LibreOffice ODS doesn't use these constructs.

**Method 2 — UNO Python (for macro injection):**
Start LibreOffice listener, then open and save via UNO:
```python
subprocess.Popen(["soffice", "--headless", "--norestore",
    "--accept=socket,host=localhost,port=2002;urp;StarOffice.ServiceManager"])
# Then use Python UNO script to open, manipulate, and save
```

### 5. Inject StarBasic Macro into ODS

ODS files are ZIP archives. StarBasic macros are stored as XML in `Basic/Standard/`.

**Direct injection via zipfile (no LibreOffice needed):**

```python
import zipfile, tempfile, shutil

macro_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script"
  script:name="MyMacro" script:language="StarBasic">
Sub MyMacro()
    MsgBox "Hello from ODS!"
End Sub
</script:module>'''

script_lc = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:library PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "library.dtd">
<script:library xmlns:script="http://openoffice.org/2000/script"
  script:name="Standard" script:readonly="false">
<script:module index:script:name="MyMacro" script:language="StarBasic"
  script:moduleType="normal"/>
</script:library>'''

tmp = tempfile.mktemp()
with zipfile.ZipFile('input.ods', 'r') as zin:
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'Basic/script-lc.xml':
                zout.writestr(item, script_lc)  # replace
            elif item.filename == 'META-INF/manifest.xml':
                # Add Basic entries before </manifest:manifest>
                content = data.decode('utf-8')
                if 'MyMacro' not in content:
                    add = '''
<manifest:file-entry manifest:media-type="application/vnd.sun.star.basic-library"
    manifest:full-path="Basic/"/>
<manifest:file-entry manifest:media-type="text/xml"
    manifest:full-path="Basic/Standard/MyMacro.xml"/>'''
                    content = content.replace('</manifest:manifest>', add + '\n</manifest:manifest>')
                zout.writestr(item, content.encode('utf-8'))
            else:
                zout.writestr(item, data)
        zout.writestr('Basic/Standard/MyMacro.xml', macro_xml.encode('utf-8'))

shutil.move(tmp, 'output.ods')
```

**Important XML escaping for macro code:**
In StarBasic macro XML, these characters MUST be entity-encoded:
- `&` → `&amp;`
- `<` → `&lt;`
- `>` → `&gt;`
- `"` → `&quot;`

Use Python: `code.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')`

**LibreOffice UNO injection (alternative):**

```python
doc = desktop.loadComponentFromURL("file:///path/to/file.ods", "_blank", 0, ())
libs = doc.BasicLibraries
standard = libs.getByName("Standard")
try:
    standard.insertByName("MyMacro", macro_code)
except Exception:
    standard.replaceByName("MyMacro", macro_code)
doc.storeToURL("file:///path/to/output.ods", (save_prop,))
doc.close(True)
```

UNO injection is cleaner but requires LibreOffice running with `--accept=socket,host=localhost,port=2002`. The zipfile method works without LibreOffice running.

### 6. Verification Checklist

- [ ] `_xlfn.` count = 0 in output
- [ ] `#REF!` in formulas = 0 in output
- [ ] All expected macros present in `Basic/Standard/` (ods) or `xl/vbaProject.bin` (xlsm)
- [ ] ODS opens without errors in LibreOffice Calc
- [ ] Formulas recalculate correctly
- [ ] Macro runs without runtime errors (`Sub GenerateBarcodes()` etc.)
- [ ] Manifest.xml contains Basic library entries

## StarBasic Macro Writing Guide

**Canonical GenerateBarcodes pattern (bwip-js API):**

```vba
Sub GenerateBarcodes()
    Dim oDoc As Object
    Dim oSheet As Object
    Dim oDrawPage As Object
    Dim oShape As Object
    Dim sText As String
    Dim sUrl As String
    Dim r As Long
    Dim i As Long

    oDoc = ThisComponent
    oSheet = oDoc.Sheets.getByName("바코드")
    oDrawPage = oSheet.getDrawPage()

    ' Remove existing barcodes
    For i = oDrawPage.getCount() - 1 To 0 Step -1
        oShape = oDrawPage.getByIndex(i)
        If InStr(oShape.Name, "BwipBarcode_") > 0 Then
            oDrawPage.remove(oShape)
        End If
    Next i

    ' Generate new barcodes
    For r = 6 To 61  ' rows 7-62, 0-indexed
        sText = Trim(oSheet.getCellByPosition(0, r).getString())
        If sText <> "" Then
            sUrl = "https://api-bwipjs.metafloor.com/?bcid=code128" & _
                   "&text=" & UrlEncode(sText) & _
                   "&scale=2&includetext"
            oShape = oDoc.createInstance("com.sun.star.drawing.GraphicObjectShape")
            oShape.GraphicURL = sUrl
            oShape.Name = "BwipBarcode_" & r
            Dim oSize As New com.sun.star.awt.Size
            oSize.Width = 4500
            oSize.Height = 1800
            oShape.setSize(oSize)
            Dim oPos As New com.sun.star.awt.Point
            oPos.X = oSheet.getCellByPosition(1, r).getPosition().X
            oPos.Y = oSheet.getCellByPosition(1, r).getPosition().Y
            oShape.setPosition(oPos)
            oDrawPage.add(oShape)
        End If
    Next r
    MsgBox "바코드 생성 완료!", 64, "완료"
End Sub

Function UrlEncode(ByVal sText As String) As String
    Dim sResult As String
    Dim i As Long
    Dim iChar As Integer
    sResult = ""
    For i = 1 To Len(sText)
        iChar = Asc(Mid(sText, i, 1))
        If (iChar >= 65 And iChar <= 90) Or _     ' A-Z
           (iChar >= 97 And iChar <= 122) Or _    ' a-z
           (iChar >= 48 And iChar <= 57) Or _     ' 0-9
           iChar = 45 Or iChar = 46 Or _          ' - .
           iChar = 95 Or iChar = 126 Then         ' _ ~
            sResult = sResult & Chr(iChar)
        ElseIf iChar = 32 Then
            sResult = sResult & "%20"
        Else
            sResult = sResult & "%" & Hex(iChar)
        End If
    Next i
    UrlEncode = sResult
End Function
```

**Common StarBasic errors to avoid:**
- ❌ `com.sun.star.geometry.convertValue()` — this API does NOT exist. Use string concatenation + UrlEncode.
- ❌ `oCell.Position` — Cell objects don't have `.Position`. Use `oSheet.getCellByPosition(col, row).getPosition()`.
- ❌ `.getString()` returns a string; `.Value` returns a number. Use `.getString()` when reading display text.
- ❌ LibreOffice Basic is case-insensitive for variable names but case-SENSITIVE for UNO API property names.
- ❌ `ThisComponent.Sheets(0)` doesn't work — use `ThisComponent.Sheets.getByIndex(0)` or `.getByName("Sheet1")`.

## Pitfalls

### CRITICAL: Verify Before Reporting — Always

**⚠️ Never report "done" or "it works" without actual verification.**

This skill covers formulas, macros, PPD, USB, and CUPS. Each time you touch one of these layers, you MUST:
1. Run the actual test command
2. Capture the output
3. Include the output in the report

**Examples of failures from assuming instead of verifying:**
- Adding `*PageSize` and `*PageRegion` to a CUPS PPD but forgetting `*ImageableArea` → LibreOffice showed "0x0" because the printable area was undefined.
- Reporting printer "ready" after CUPS registration without sending a test page → printer was in EPL2 mode, not ZPL.

**Self-check before reporting:**
- "Did I run the actual command, or did I just reason about it?"
- "Can I show the output that proves it works?"

### User Priority: Complete Fixes First, Macros Second
⚠️ **User will express strong frustration if you fix macros only and ignore formula errors.**
In a session where the user asked to "fix formulas and errors for LibreOffice," focusing only on the macro while leaving formula errors (`#REF!`, `_xlfn.`) untouched drew a sharp correction: *"수식오류도 수정이 안되어 있고 매크로도 안되는데 뭘한거야?"*
**Always fix formulas FIRST — verify them — THEN fix macros. Deliver both in one artifact.**
This applies broadly: when a user reports N problems, fix ALL N before reporting back. Partial fixes are perceived as incompetence, not progress.

- **openpyxl may warn about Conditional Formatting** — this is safe to ignore; the formatting is lost but data and formulas are preserved.
- **ODS file size is smaller than XLSM** — ODS uses gzip compression on XML; file size difference is normal.
- **LibreOffice convert-to may NOT work if Java is missing** — warning about `javaldx` is non-fatal for Calc conversion.
- **UNO `getBasicLibraries` / `BasicLibraries` API** — In Python-UNO, use `doc.BasicLibraries` (property), NOT `doc.getBasicLibraries()` (method). The API switched between LO versions.
- **VBA macros in vbaProject.bin (XLSM) cannot be modified programmatically**. openpyxl and zipfile can preserve them but cannot read/edit VBA source code. To fix a buggy VBA macro, use one of:
  - **Provide a standalone .bas file** for the user to import into LibreOffice (`Tools → Macros → Organize Macros → LibreOffice Basic → Import`)
  - **Add a StarBasic macro alongside the VBA macro** in an ODS file (LibreOffice runs both simultaneously — VBA via VBASupport, StarBasic natively)
  - **Decompile/recompile vbaProject.bin** with oletools (complex, fragile, not recommended)
  - **Pure StarBasic modules can only be injected into ODS**, NOT into XLSM. If you inject into XLSM via UNO (`insertByName`), LibreOffice CANNOT save it back to XLSM format — the save fails with `SfxBaseModel::impl_store`. Convert to ODS first.
- **StarBasic module insertion via UNO:** Use `insertByName` for new modules, `replaceByName` for existing ones. XLSM format cannot save StarBasic modules — only ODS supports this.
- **LibreOffice's `--convert-to ods` WILL translate `_xlfn.xlookup` to `xlookup`** automatically in ODS output. If you already fixed the XLSM with openpyxl, the conversion is still safe — the resulting ODS has clean native formulas either way. Do NOT double-fix.
- **한글 macro file paths:** When using the .bas import method, save the .bas file with UTF-8 encoding. LibreOffice imports it correctly as UTF-8. If the file contains 한글 comments, ensure no BOM is present (strip with `code.encode('utf-8').lstrip(b'\\xef\\xbb\\xbf')`).
- **한글 경로:** When using UNO Python, URL-encode 한글 paths: `"file:///home/" + urllib.parse.quote("사용자/문서")`.
- **LibreOffice `getPosition()` returns `com.sun.star.awt.Point`** in 1/100mm units, not pixels or points.
- **ODS content.xml direct regex editing can corrupt XML** — `content.xml` uses XML entities (`&quot;`, `&amp;`). Using `re.sub` with plain `"` patterns will fail. Use exact string matching or XML-aware parsing instead:
  ```python
  # WRONG: re.sub(r'of:=image\\([^)]+\\)', 'of:=""', text)  -- may break &quot; entities
  # RIGHT: text.replace('exact_formula_string', 'of:=""')  -- exact match preserves entities
  ```
- **LibreOffice XLSX→ODS converter may AUTO-CREATE IMAGE() functions** — Even after replacing `IMAGE(url, ...)` with an empty formula `""` in the XLSX, LibreOffice's converter may detect a URL pattern in a cell and re-create an `IMAGE()` ODF function. Always verify the ODS `content.xml` after conversion:
  ```python
  import zipfile
  with zipfile.ZipFile('output.ods') as z:
      content = z.read('content.xml').decode('utf-8')
      print('image() functions:', content.count('image('))  # should be 0
  ```
  If IMAGE() persists, edit `content.xml` directly to remove it (see pitfall above about entity-safe replacements).
- **XLSX XML stores formulas with XML entities** — In XLSX sheet XML, formulas use `&quot;` for quotes, `&amp;` for ampersands. When doing regex replacement on the raw XML text, always match the entity-encoded form:
  ```python
  # In XLSX XML, the formula looks like this:
  #   <f>IMAGE(&quot;url&quot;&amp;B7,4,80,220)</f>
  # NOT this (which won't match):
  #   <f>IMAGE("url"&B7,4,80,220)</f>
  text = re.sub(r'IMAGE\(&quot;[^&]*&quot;&amp;[^,]+,[^)]*\)', '""', text)
  ```
- **`soffice --convert-to ods` may truncate rows** — If the XLSX has many empty trailing rows, the ODS output may report fewer `<table:table-row>` elements because LibreOffice skips repeated empty rows. This is normal — data is not lost, just compressed in the `table:number-columns-repeated` attribute. Verify by checking actual data content, not row element count.
- **IMPORTANT: Do NOT use regex to fix `content.xml` unless you test the result** — The `content.xml` file uses a complex mix of XML entities, namespaced attributes, and CDATA-like content. A bad regex substitution can silently produce a well-formedness error that LibreOffice rejects with "file cannot be opened." Always parse the result with `xml.etree.ElementTree.fromstring()` before presenting to the user. If using regex, prefer exact string `.replace()` over pattern-based `re.sub()` to minimize risk.

## Related Skills

- **`cross-platform-project-migration`** — full Django+React project migration (separate concerns)
- **`subagent-driven-development`** — for delegating formula/macro fixes to ACP agents (see ACP Reasonix section for configuration gotchas)
- **`libreoffice-excel-migration`** — overlaps with this skill significantly (same domain). The curator should consider consolidation.

## References

- [`references/ods-macro-injection.md`](references/ods-macro-injection.md) — detailed StarBasic macro injection into ODS via zipfile
- [`references/dockur-password-recovery.md`](references/dockur-password-recovery.md) — Windows VM password recovery via SAM/chntpw, dockur/windows password encoding bug, FreeRDP NLA workarounds
- [`references/printer-usb-debug.md`](references/printer-usb-debug.md) — Zebra ZM600 USB printer debugging on Linux (CUPS, usblp, ZPL direct test)
- [`references/cups-ipp-docker.md`](references/cups-ipp-docker.md) — Share USB printers between Linux CUPS and Docker Windows VM via IPP network printing (alternative to QEMU USB passthrough)

## Relationship to `libreoffice-excel-migration`

This skill (`spreadsheet-migration`) and `libreoffice-excel-migration` cover the same domain with significant overlap. `spreadsheet-migration` is the more comprehensive/current version (includes macro injection, verification checklist, doskcur password recovery, printer reference). The curator should consider archiving `libreoffice-excel-migration` into this skill.

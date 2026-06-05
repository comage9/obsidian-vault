# Full Repair Pipeline: XLSM → Fixed Formulas + Embedded Macros → Single ODS Deliverable

This reference documents the complete end-to-end pipeline for taking a broken `.xlsm` file (with `_xlfn.` prefix issues, `#REF!` errors, and buggy VBA macros) and producing a single working `.ods` file with both formulas fixed and a corrected StarBasic macro embedded.

## Why This Pipeline Exists

The user wants a **single working file** — not a fixed spreadsheet plus a separate macro file to import manually. Delivering components that require assembly is a source of user frustration.

## The Pipeline (4 Stages)

### Stage 1: Analyze

```python
import openpyxl

# Open with formulas for analysis
wb = openpyxl.load_workbook('input.xlsm', data_only=False)
print('Sheets:', wb.sheetnames)

for name in wb.sheetnames:
    ws = wb[name]
    formulas = 0
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                formulas += 1
    print(f'  {name}: {formulas} formulas')

# Check formula patterns
for name in ['VF', '바코드']:
    ws = wb[name]
    for row in range(1, min(5, ws.max_row+1)):
        for col in range(1, min(ws.max_column+1, 30)):
            cell = ws.cell(row, col)
            if cell.value and isinstance(cell.value, str) and '_xlfn.' in str(cell.value):
                print(f'  {name}!{cell.coordinate}: {str(cell.value)[:80]}')
```

**Look for:** `_xlfn.xlookup`, `_xlfn.single`, `#REF!`, `=#REF!`

### Stage 2: Fix Formulas (openpyxl, keep_vba=True)

```python
import openpyxl, re, shutil
from openpyxl.utils import get_column_letter

shutil.copy2('input.xlsm', 'working.xlsm')
wb = openpyxl.load_workbook('working.xlsm', keep_vba=True)

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
                
                # Fix 2: Remove SINGLE() wrapper (redundant around XLOOKUP)
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
                
                # Fix 3: Repair #REF! in H column (Pcs/BOX → 생산단위 lookup)
                col_letter = get_column_letter(cell.column)
                if '#REF!' in new and cell.column == 8:  # H column
                    new = re.sub(
                        r'XLOOKUP\(([^,]+),#REF!,#REF!\)',
                        r"XLOOKUP(\1,'vf 품목'!$B:$B,'vf 품목'!$J:$J)",
                        new)
                
                # Fix 4: =#REF! in header → blank
                if cell.row == 1 and '=#REF!' in new:
                    if cell.column == 17:  # Q column
                        new = '=""'
                
                if new != old:
                    cell.value = new

wb.save('working.xlsm')
```

**Key points:**
- `keep_vba=True` preserves the original VBA project binary (`xl/vbaProject.bin`)
- openpyxl can modify formulas and save back to XLSM format
- Conditional Formatting may be dropped (harmless warning)

### Stage 3: Convert to ODS (LibreOffice Headless)

```bash
# Installation-free conversion using system LibreOffice
soffice --headless --norestore \
  --convert-to ods:calc8 \
  --outdir /output/dir \
  working.xlsm
```

**What this does:**
- LibreOffice opens the XLSM and evaluates all formulas
- Converts Excel syntax → LibreOffice native OF syntax
- `XLOOKUP(...)` auto-converts to `of:=xlookup(...)` 
- `#REF!` fixes from Stage 2 are preserved in the converted output
- VBA modules are preserved in `Basic/VBAProject/` directory

### Stage 4: Inject StarBasic Macro (Zipfile)

Create the corrected macro as a StarBasic module XML, then inject it into the ODS ZIP:

```python
import zipfile, tempfile, shutil

MODULE_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script"
    script:name="GenerateBarcodes" script:language="StarBasic">
Sub GenerateBarcodes()
    ' ... StarBasic code ...
End Sub
</script:module>'''

SCRIPT_LC_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:library PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "library.dtd">
<script:library xmlns:script="http://openoffice.org/2000/script"
    script:name="Standard" script:readonly="false">
<script:module index:0 script:name="GenerateBarcodes"
    script:language="StarBasic" script:moduleType="normal"/>
</script:library>'''

MANIFEST_ENTRIES = '''<manifest:file-entry manifest:media-type="application/vnd.sun.star.basic-library"
    manifest:full-path="Basic/"/>
<manifest:file-entry manifest:media-type="application/vnd.sun.star.basic-library"
    manifest:full-path="Basic/Standard/"/>
<manifest:file-entry manifest:media-type="text/xml"
    manifest:full-path="Basic/Standard/GenerateBarcodes.xml"/>
<manifest:file-entry manifest:media-type="text/xml"
    manifest:full-path="Basic/script-lc.xml"/>'''

tmp = tempfile.mktemp()
with zipfile.ZipFile('converted.ods', 'r') as zin:
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'Basic/script-lc.xml':
                zout.writestr(item, SCRIPT_LC_XML)
            elif item.filename == 'META-INF/manifest.xml':
                content = data.decode('utf-8')
                if 'GenerateBarcodes' not in content:
                    content = content.replace('</manifest:manifest>',
                        MANIFEST_ENTRIES + '\n</manifest:manifest>')
                zout.writestr(item, content.encode('utf-8'))
            else:
                zout.writestr(item, data)
        zout.writestr('Basic/Standard/GenerateBarcodes.xml', MODULE_XML)
shutil.move(tmp, 'output.ods')
```

**Verification:**
```python
with zipfile.ZipFile('output.ods', 'r') as z:
    has = any('GenerateBarcodes' in f or 'GenerateBarcodes' in z.read(f).decode('utf-8', errors='replace') for f in z.namelist() if f.endswith('.xml'))
    print(f'Macro embedded: {has}')
```

## Why Not Just Use UNO Python?

The UNO Python bridge (`import uno`) is the "proper" way, but:
- **Ubuntu does not ship `python3-uno`** — trying to `import uno` raises `ModuleNotFoundError`
- The LibreOffice system Python doesn't have pip or external packages
- Zipfile injection is more reliable across distributions

If UNO is available, use it instead (see `libreoffice-automation` SKILL.md).

## Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `XLSM save fails` with `SfxBaseModel::impl_store (0x8...)` | StarBasic macros cannot persist in XLSM format | Save as ODS (`FilterName = "calc8"`) |
| `ODS file too small` (243KB vs 4MB original) | ZIP compression — actual content is 8MB+ uncompressed | Check `content.xml` size inside ZIP |
| `SINGLE()` removal leaves empty parens | Pattern `SINGLE(XLOOKUP(...))` → `XLOOKUP(...))` | Use balanced-paren parsing (see Stage 2) |
| `openpyxl` warning about Conditional Formatting | Not supported and removed | Harmless for formula compatibility |
| `vf 품목` sheet row 1 shows "Column1, Column2..." | Real headers are on row 2 (Korean names) | Always check row 2 for actual headers |

## Common #REF! Recovery Patterns

| Column in VF Sheet | Purpose | Target Column in `vf 품목` |
|--------------------|---------|---------------------------|
| D | 품목명 (product name) | `E:E` (바코드/제품명) |
| H | Pcs/BOX (개수/박스) | `J:J` (생산단위) |
| K | 영문명 (English name) | `F:F` or `S:S` (제품명/영문명) |

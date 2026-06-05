---
name: libreoffice-excel-conversion
description: Convert Excel XLSX/XLSM with modern functions (XLOOKUP, IMAGE, SINGLE, _xlfn. prefix, ArrayFormula) to LibreOffice-compatible ODS — formula rewriting, PPD patching, macro embedding via UNO
category: office
---

# LibreOffice Excel Conversion

Convert Excel files (XLSX/XLSM) with modern Excel functions to work correctly in LibreOffice Calc.

## Common Excel Functions That Need Conversion

| Excel Function | LibreOffice Status | Action |
|---------------|-------------------|--------|
| `XLOOKUP()` | Supported since LO 25.8 | Remove `_xlfn.` prefix, or replace with `VLOOKUP()` for older versions |
| `IMAGE()` | Not a Calc function | Replace with HYPERLINK or empty string; LibreOffice ODS conversion may auto-regenerate IMAGE() — double-check |
| `SINGLE()` | Not supported | Remove wrapper — XLOOKUP already returns a single value |
| `_xlfn.xlookup()` | Excel internal prefix | Replace with `XLOOKUP()` or remove `_xlfn.` prefix |
| ArrayFormula (CSE) | Partial support | Remove `t="array" ref="..."` attribute from `<f>` elements in XML |
| `IF(..., VLOOKUP(...))` | Fully supported | No change needed |

## Formula Fix Pipeline

### Step 1: Fix XLSX XML (most reliable)
Use Python with zipfile to edit `xl/worksheets/sheet1.xml` directly:

```python
import re, zipfile, tempfile, shutil

SRC = "file.xlsx"
DST = "file_fixed.xlsx"
shutil.copy2(SRC, DST)
tmp = tempfile.mktemp()

with zipfile.ZipFile(DST, 'r') as zin:
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith('.xml'):
                text = data.decode('utf-8')
                # 1. Remove ArrayFormula marker
                text = re.sub(r'<f t="array" ref="[^"]*">', '<f>', text)
                # 2. Replace XLOOKUP with VLOOKUP (XML entity aware: &quot; = ")
                text = re.sub(r'XLOOKUP\(\$G\$1,.*?F:F,0,0\)',
                    'VLOOKUP($G$1,\'vf 품목\'!A:V,6,0)', text)
                # 3. Remove IMAGE function (use &quot; for XML entities)
                text = re.sub(r'IMAGE\(&quot;[^&]*&quot;&amp;[^,]+,[^)]*\)', '""', text)
                data = text.encode('utf-8')
            zout.writestr(item, data)
shutil.move(tmp, DST)
```

### Step 2: Convert to ODS
```bash
soffice --headless --norestore --convert-to "ods:calc8" --outdir /output/ file_fixed.xlsx
```

### Step 3: Post-process ODS (remove IMAGE that LibreOffice re-creates)
LibreOffice XLSX→ODS converter may re-create `image()` functions from URL patterns. Remove them from content.xml:

```python
# In content.xml of ODS:
text = re.sub(r'of:=image\(&quot;[^&]+&quot;&amp;[^;]+;[^;]+;[^;]+;[^;]+\)', 'of:=""', text)
```

### Step 4: Verify
```python
with zipfile.ZipFile('output.ods') as z:
    content = z.read('content.xml')
    import xml.etree.ElementTree as ET
    root = ET.fromstring(content)
    ns = {'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'}
    for t in root.findall('.//table:table', ns):
        name = t.get('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name', '?')
        rows = len(t.findall('.//table:table-row', ns))
    errs = content.count(b'#NAME?') + content.count(b'#REF!')
    # #NAME? in cached text (not in formulas) is OK — recalculates on open
```

## Embedding LibreOffice Basic Macros in ODS

ODS files are ZIP archives. Inject macros by modifying XML inside:

```python
import zipfile
macro_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<script:module ... script:name="GenerateBarcodes" script:language="StarBasic">
... StarBasic code here ...
</script:module>'''

script_lc = '''<?xml version="1.0" encoding="UTF-8"?>
<script:library name="Standard" readonly="false">
<script:module index: script:name="GenerateBarcodes" script:language="StarBasic" script:moduleType="normal"/>
</script:library>'''

with zipfile.ZipFile('output.ods', 'a') as z:
    z.writestr('Basic/Standard/GenerateBarcodes.xml', macro_xml.encode('utf-8'))
    z.writestr('Basic/script-lc.xml', script_lc.encode('utf-8'))
```

Also update `META-INF/manifest.xml` to include Basic entries, and add `Basic/Standard/script-lb.xml` if missing.

## Important Pitfalls
1. **IMAGE() is auto-regenerated** during LibreOffice XLSX→ODS conversion — check content.xml afterward
2. **PPD repair**: `lpadmin -m "drv:///path/driver"` regenerates PPD from scratch, overwriting any custom page sizes
3. **ArrayFormula**: Regular `re.sub` on XML is more reliable than openpyxl for removing `t="array"` attribute
4. **ODS XLSM VBA macros** vs **LibreOffice Basic**: Macros stored in `xl/vbaProject.bin` (binary OLE) cannot be edited programmatically — use .bas import via LibreOffice UI or UNO Python bridge
5. **#NAME? cached values** in ODS content.xml are not formula errors — they clear on next recalculation

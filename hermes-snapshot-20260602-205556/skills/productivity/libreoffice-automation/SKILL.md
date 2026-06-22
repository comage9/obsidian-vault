---
name: libreoffice-automation
description: Fix, port, and automate Excel/LibreOffice Calc documents — VBA→StarBasic macro conversion, UNO Python automation, formula compatibility, and headless document manipulation.
category: productivity
---

# LibreOffice Automation

Port Excel VBA macros to LibreOffice StarBasic, fix formula compatibility issues between Excel and Calc, and automate document manipulation via UNO Python API.

## When to Load

- User provides an `.xlsm` / `.xls` / `.xlsx` file that needs LibreOffice compatibility fixes
- User mentions #REF! errors, _xlfn. prefix, SINGLE() function, or XLOOKUP issues
- Macros need to be embedded into ODS/XLSM files programmatically
- Headless document conversion or manipulation needed

## Formula Compatibility: Excel → LibreOffice Calc

### Common Issues

| Excel Feature | LibreOffice Status | Fix |
|---------------|-------------------|-----|
| `_xlfn.xlookup()` | Recognized as `XLOOKUP()` when prefix removed | Global replace `_xlfn.xlookup` → `XLOOKUP` |
| `_xlfn.single()` | **Does NOT exist** | Remove wrapper: `SINGLE(XLOOKUP(...))` → `XLOOKUP(...)` |
| `_xlfn.XMATCH()` | Supported as `XMATCH()` | Remove `_xlfn.` prefix |
| `_xlfn.*` prefixed functions | Varies | Always strip `_xlfn.` prefix first, then test |
| `IMAGE(url, mode, h, w)` | **Not supported** (any version) | Replace with URL text `=""` or Hyperlink. LibreOffice XLSX→ODS converter auto-creates `image()` function from URL patterns — this also fails with `#NAME?`. Remove entirely before conversion. |
| `XLOOKUP()` | Supported since LibreOffice 25.8 | If it fails with `#NAME?` (older version), replace with `VLOOKUP()` |
| `VLOOKUP(lookup, table, col_index, range)` | Fully supported | Preferred replacement for XLOOKUP when compatibility uncertain |
| ArrayFormula (`<f t="array">`) | **Not supported** | Remove `t="array"` attribute from XML: `<f t="array" ref="A1">` → `<f>` |
| `#REF!` errors | Propagated | Fix underlying reference (deleted columns/ranges) |
| `VLOOKUP()` / `TODAY()` | Fully supported | No change needed |
| VBA macros (`Option VBASupport 1`) | Limited support | Rewrite in pure StarBasic for reliability |

### Complete Formula Fix Workflow (openpyxl)

```python
import openpyxl, re, shutil, zipfile
from openpyxl.utils import get_column_letter

shutil.copy2(SOURCE, DST)
wb = openpyxl.load_workbook(DST, keep_vba=True)

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                old = cell.value
                new = old
                new = new.replace('_xlfn.xlookup', 'XLOOKUP')
                new = new.replace('_xlfn.single', '')  # remove wrapper name
                # Clean up empty parens from SINGLE removal
                new = re.sub(r'\(([^()]*)\)\(', r'(\1', new)
                # Fix #REF! in known patterns
                if '#REF!' in new and cell.column == H_COL:
                    new = re.sub(
                        r'XLOOKUP\(([^,]+),#REF!,#REF!\)',
                        r"XLOOKUP(\1,'TargetSheet'!$B:$B,'TargetSheet'!$J:$J)",
                        new)
                if new != old:
                    cell.value = new
wb.save(DST)

The `_xlfn.` prefix is Excel's internal marker for "future functions" that were new at save time. LibreOffice may not recognize functions with this prefix. **Always strip `_xlfn.` from all formulas as the first step.**

### SINGLE() Function

`SINGLE()` returns a single value from a range/array. It's an Excel 365 function. LibreOffice does NOT have it. Since `XLOOKUP()` already returns a single value, `SINGLE(XLOOKUP(...))` degrades cleanly to `XLOOKUP(...)`.

### ODS Conversion Pitfall: IMAGE() auto-creation

**LibreOffice auto-creates `image()` from URL patterns:** When converting XLSX→ODS, LibreOffice detects URL strings in cell data and wraps them in an `image()` call. This produces `#NAME?` because:
- LibreOffice Calc has no `IMAGE()` worksheet function (despite ODF spec mention)
- The auto-converted call uses wrong parameter order

**Prevention:** Before conversion, ensure no cell contains dangling URL strings. Replace `=IMAGE(url,...)` with `=""` or plain text.

### ArrayFormula Handling (`<f t="array">`)

Excel CSE array formulas carry `t="array" ref="A1"` attributes in XLSX XML. LibreOffice does not understand them, producing `#NAME?`.

**Fix:** Strip array type from XLSX XML before conversion:
```python
text = re.sub(r'<f t="array" ref="[^"]*">', '<f>', text)
```

## VBA Macro → StarBasic Conversion

### Detection: Excel VBA vs LibreOffice StarBasic

| Feature | Excel VBA | StarBasic |
|---------|-----------|-----------|
| App object | `Application` | `ThisComponent` |
| Sheet access | `Sheets("name")` | `Sheets.getByName("name")` |
| Cell access | `Range("A1")` | `getCellByPosition(0, 0)` |
| Worksheet function | `WorksheetFunction.XLOOKUP(...)` | Built-in or manual |
| Drawings | No native DrawPage | `Sheet.getDrawPage()` |
| Comments | `'` at line start | `Rem` or `'` |

### Macro Storage Structure (ODS = ZIP)

```
Basic/
├── Standard/                    # LibreOffice-native macros (pure StarBasic)
│   ├── script-lb.xml            # Library binding metadata
│   ├── GenerateBarcodes.xml     # Module XML (StarBasic source)
│   └── ...
├── VBAProject/                  # VBA compatibility modules
│   ├── Module1.xml              # Original VBA (Option VBASupport 1)
│   ├── ThisWorkbook.xml
│   └── script-lb.xml
└── script-lc.xml                # Library container config
```

XLSM macros are stored in `xl/vbaProject.bin` (binary OLE). Unreadable without special tools. Convert to ODS for readable XML.

## Embedding Macros via LibreOffice UNO Python

### Prerequisites
```bash
# LibreOffice must be installed
libreoffice --version   # Tested: 24.2.7.2
```

### Headless Server + Python UNO

```python
import subprocess, time

# 1. Start listener
listener = subprocess.Popen([
    "soffice", "--headless", "--norestore",
    "--accept=socket,host=localhost,port=2002;urp;StarOffice.ServiceManager"
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(4)

# 2. Open document, insert macro, save
import uno
localContext = uno.getComponentContext()
resolver = localContext.ServiceManager.createInstanceWithContext(
    "com.sun.star.bridge.UnoUrlResolver", localContext)
ctx = resolver.resolve(
    "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
smgr = ctx.ServiceManager
desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

url = "file:///path/to/document.xlsm"  # must be URL-encoded
p = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
p.Name = "Hidden"
p.Value = True
doc = desktop.loadComponentFromURL(url, "_blank", 0, (p,))

# Insert macro
libs = doc.BasicLibraries
standard = libs.getByName("Standard")
try:
    standard.insertByName("ModuleName", code_string)
except Exception:
    standard.replaceByName("ModuleName", code_string)

# Save as ODS (pure StarBasic macros persist in ODS)
ps = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
ps.Name = "FilterName"
ps.Value = "calc8"  # ODS format
doc.storeToURL(ods_url, (ps,))

# XLSM save may FAIL — LibreOffice Basic macros cannot be saved back to XLSM format
# (XLSM expects VBA in vbaProject.bin, not StarBasic XML)
doc.close(True)
```

### Key UNO API Facts

| Operation | API | Notes |
|-----------|-----|-------|
| Load document | `desktop.loadComponentFromURL(url, "_blank", 0, (props,))` | URL must be percent-encoded |
| Access Basic libs | `doc.BasicLibraries` | **Not** `doc.getBasicLibraries()` — it's a property, not a method |
| Get Standard lib | `libs.getByName("Standard")` | Standard is always present |
| Add module | `standard.insertByName("MyModule", code_string)` | Use `insertByName` for new, `replaceByName` for existing |
| Save as ODS | `FilterName = "calc8"` | Preserves StarBasic macros |
| Save as XLSM | `FilterName = "MS Excel 2007 XML"` | **Often fails** with `SfxBaseModel::impl_store (0x8...)` — StarBasic macros cannot persist in XLSM format |
| Macro exists check | `lib.hasByName(name)` | Returns boolean |

### ODS Zipfile Direct Injection (When UNO Fails)

If the UNO Python bridge is unavailable (no `uno` module), inject macros directly into the ODS ZIP:

**Required XML files and structure:**
```
Basic/
├── Standard/
│   ├── script-lb.xml           # Library binding (minimal)
│   └── GenerateBarcodes.xml    # Module XML (StarBasic source wrapped in XML)
├── VBAProject/                 # Preserve existing VBA modules
│   └── ...
└── script-lc.xml               # Library container config
META-INF/manifest.xml           # Must declare Basic entries
```

**Module XML format:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script"
    script:name="ModuleName" script:language="StarBasic">
' StarBasic source code here
' HTML entities: &quot; = ", &amp; = &, &lt; = <, &gt; = >
' Line continuation: use single quotes for REM in XML context
</script:module>
```

**script-lc.xml** (Standard library registration):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:library PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "library.dtd">
<script:library xmlns:script="http://openoffice.org/2000/script"
    script:name="Standard" script:readonly="false">
<script:module index:0 script:name="GenerateBarcodes" script:language="StarBasic" script:moduleType="normal"/>
</script:library>
```

**Manifest entries to add** (inside `<manifest:manifest>`):
```xml
<manifest:file-entry manifest:media-type="application/vnd.sun.star.basic-library"
    manifest:full-path="Basic/"/>
<manifest:file-entry manifest:media-type="application/vnd.sun.star.basic-library"
    manifest:full-path="Basic/Standard/"/>
<manifest:file-entry manifest:media-type="text/xml"
    manifest:full-path="Basic/Standard/GenerateBarcodes.xml"/>
<manifest:file-entry manifest:media-type="text/xml"
    manifest:full-path="Basic/script-lc.xml"/>
```

**Python injection script:**
```python
import zipfile, tempfile, shutil

tmp = tempfile.mktemp()
with zipfile.ZipFile(DST_ODS, 'r') as zin:
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'Basic/script-lc.xml':
                zout.writestr(item, script_lc_xml)
            elif item.filename == 'META-INF/manifest.xml':
                # Insert Basic entries before </manifest:manifest>
                content = data.decode('utf-8')
                content = content.replace('</manifest:manifest>',
                    manifest_entries + '\n</manifest:manifest>')
                zout.writestr(item, content.encode('utf-8'))
            else:
                zout.writestr(item, data)
        # Add new module
        zout.writestr('Basic/Standard/ModuleName.xml', module_xml)
shutil.move(tmp, DST_ODS)
```

## Delivery Rule: Always Provide a Complete Working File

When the user asks for a repaired/fixed document, **deliver a complete working file**, not separate components:

- ✅ **DO**: Create and deliver a functional `.ods` or `.xlsm` file with both fixed formulas and embedded macros
- ❌ **DON'T**: Provide only a separate `.bas` file for the user to import manually
- ❌ **DON'T**: Give instructions for the user to assemble pieces themselves
- The macro + formulas must be **in the file**, delivered as a single download/artifact

The only exception: if technical constraints prevent embedding (e.g., `xl/vbaProject.bin` is unmodifiable), explain clearly WHY and provide the next-simplest path (`.bas` import instructions).

### Delivery Options Priority

1. **ODS (calc8 format)** — Best: preserves StarBasic macros, accepts formula modifications, created via LibreOffice headless converter
2. **XLSM (keep_vba=True)** — Good for formula-only fixes; VBA macros preserved but cannot be modified
3. **Separate .bas file** — Last resort: only when VBA project must be replaced and UNO bridge unavailable

## References

- `references/full-repair-pipeline.md` — **Start here**: end-to-end pipeline from broken `.xlsm` to single working `.ods` with fixed formulas + embedded StarBasic macro (4 stages: analyze → fix formulas → convert → inject macro)
- `references/vba-to-starbasic-patterns.md` — Common VBA→StarBasic translation patterns with examples
- `references/formula-compatibility.md` — Detailed Excel↔Calc formula mapping

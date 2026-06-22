# ODS Macro Injection via Zipfile XML Manipulation

When the UNO Python bridge (`import uno`) is unavailable, inject LibreOffice StarBasic macros into an ODS file by directly manipulating the ZIP structure.

## Context

LibreOffice ODS files are standard ZIP archives containing XML. Macros live as XML module files under `Basic/Standard/`. This technique was used when the `uno` module was unavailable in the system Python (Ubuntu 24.04 default Python does not ship `uno`).

## Structure

```
Basic/
├── Standard/
│   ├── script-lb.xml                  # Library binding
│   └── GenerateBarcodes.xml           # Module source
├── VBAProject/                        # Preserved from original XLSM
│   ├── Module1.xml
│   ├── Module2.xml
│   └── ...
├── script-lc.xml                      # Library container config (REQUIRED)
META-INF/manifest.xml                  # Must declare Basic entries
```

## Steps

### 1. Convert XLSM to ODS

```bash
soffice --headless --norestore \
  --convert-to ods:calc8 \
  --outdir /output/dir \
  input.xlsm
```

This preserves all spreadsheet data and VBA modules while converting to LibreOffice-native format.

### 2. Inject the Macro XML

Create the module XML file. The StarBasic source goes inside `<script:module>` tags with HTML-escaped special characters:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script"
    script:name="GenerateBarcodes" script:language="StarBasic">
'========================================================================
' Module source code here
'========================================================================
Sub GenerateBarcodes()
    Dim oDoc As Object
    oDoc = ThisComponent
    ' ... LibreOffice Basic API calls ...
End Sub

Function UrlEncode(ByVal sText As String) As String
    ' Custom URL encoding for API calls
End Function
</script:module>
```

**HTML entity encoding for LibreOffice Basic source in XML:**
- `"` → `&quot;`
- `&` → `&amp;`
- `<` → `&lt;`
- `>` → `&gt;`
- `'` stays as `'` (LibreOffice accepts both `'` and `&apos;`)

### 3. Register the module in script-lc.xml

Replace existing `Basic/script-lc.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:library PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "library.dtd">
<script:library xmlns:script="http://openoffice.org/2000/script"
    script:name="Standard" script:readonly="false">
<script:module index:0 script:name="GenerateBarcodes"
    script:language="StarBasic" script:moduleType="normal"/>
</script:library>
```

### 4. Update META-INF/manifest.xml

Add these entries before `</manifest:manifest>`:

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

### 5. Python Injection Script

```python
import zipfile, tempfile, shutil

tmp = tempfile.mktemp()
with zipfile.ZipFile(DST_ODS, 'r') as zin:
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'Basic/script-lc.xml':
                zout.writestr(item, SCRIPT_LC_XML)
            elif item.filename == 'META-INF/manifest.xml':
                content = data.decode('utf-8')
                content = content.replace('</manifest:manifest>',
                    MANIFEST_ENTRIES + '\n</manifest:manifest>')
                zout.writestr(item, content.encode('utf-8'))
            else:
                zout.writestr(item, data)
        zout.writestr('Basic/Standard/GenerateBarcodes.xml', MODULE_XML)
shutil.move(tmp, DST_ODS)
```

## Verification

```python
import zipfile
with zipfile.ZipFile(output.ods, 'r') as z:
    basic_files = [f for f in z.namelist() if 'Basic/' in f]
    print(f'Basic files: {basic_files}')
    has_macro = any('GenerateBarcodes' in f for f in basic_files)
    print(f'Macro included: {has_macro}')
    # Verify module content
    if has_macro:
        print(z.read('Basic/Standard/GenerateBarcodes.xml').decode('utf-8')[:500])
```

## Known Issues

- **Manifest entry order matters** — Basic/ must be declared before Basic/Standard/ in manifest.xml
- **ODS conversion that loses content** — If `--convert-to ods` produces a file much smaller than expected, check content.xml size inside the ZIP. The actual data is usually much larger uncompressed (8MB+ content.xml compresses to ~200KB)
- **UNO Python bridge missing** — On Ubuntu 24.04, `apt install python3-uno` is not available. Use zipfile injection instead

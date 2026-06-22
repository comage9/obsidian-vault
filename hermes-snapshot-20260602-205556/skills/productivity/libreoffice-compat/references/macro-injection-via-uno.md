# LibreOffice UNO Python Macro Injection

Inject a StarBasic macro into an ODS/XLSM document using LibreOffice's UNO API from Python — without a desktop environment.

## Prerequisites

- LibreOffice installed (`libreoffice --version`)
- `uno` Python module (bundled with LibreOffice, NOT the system Python — use Python from LibreOffice or pipe commands)

## Approach A: LibreOffice Listener + Python UNO (Reliable)

### 1. Start LibreOffice in headless listener mode

```bash
soffice --headless --norestore \
  --accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager"
```

### 2. Run UNO Python to inject the macro

```python
import uno, base64

localContext = uno.getComponentContext()
resolver = localContext.ServiceManager.createInstanceWithContext(
    "com.sun.star.bridge.UnoUrlResolver", localContext)
ctx = resolver.resolve(
    "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
smgr = ctx.ServiceManager
desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

# Open document (URL must be properly encoded)
url = "file:///path/to/document.xlsm"
doc = desktop.loadComponentFromURL(url, "_blank", 0, ())

# Read and inject macro code
with open("macro.bas", "r") as f:
    code = f.read()

libs = doc.BasicLibraries
standard = libs.getByName("Standard")

# Insert (or replace) the module
try:
    standard.insertByName("ModuleName", code)
except Exception:
    standard.replaceByName("ModuleName", code)

# Save as ODS (XLSM/MSO Excel format may NOT preserve LibreOffice Basic macros)
prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
prop.Name = "FilterName"
prop.Value = "calc8"  # ODS format
doc.storeToURL("file:///path/to/output.ods", (prop,))
doc.close(True)
```

### Important notes

- **XLSM save will fail** — LibreOffice cannot save LibreOffice Basic macros in XLSM format. Always save as ODS (filter `"calc8"`).
- **`doc.BasicLibraries`** — property, NOT method (`getBasicLibraries()` is wrong!)
- **Macro storage path:** `Basic/Standard/<ModuleName>.xml` inside the ODS ZIP

## Approach B: Direct ODS ZIP Manipulation (No LibreOffice needed)

This approach injects the macro directly into the ODS ZIP file structure, bypassing UNO entirely.

### Structure of LibreOffice Basic modules in ODS

Minimal files needed:

| File | Purpose | Required? |
|------|---------|-----------|
| `Basic/Standard/<ModuleName>.xml` | Macro source code | **Yes** |
| `Basic/script-lc.xml` | Library manifest | **Yes** |
| `META-INF/manifest.xml` | Updated with Basic entries | **Yes** |

### Step-by-step

**1. Create macro XML** (see template below)

**2. Create/update `Basic/script-lc.xml`**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:library PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "library.dtd">
<script:library xmlns:script="http://openoffice.org/2000/script"
    script:name="Standard" script:readonly="false">
  <script:module index:script:name="GenerateBarcodes"
      script:language="StarBasic" script:moduleType="normal"/>
</script:library>
```

**3. Update `META-INF/manifest.xml`** — add entries:
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

**4. Python script to inject:**
```python
import zipfile, tempfile, shutil

src = "input.ods"
dst = "output.ods"
macro_xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script"
    script:name="GenerateBarcodes" script:language="StarBasic">
' ... your StarBasic code here (XML-escaped) ...
</script:module>"""

tmp = tempfile.mktemp()
with zipfile.ZipFile(src, 'r') as zin:
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'Basic/script-lc.xml':
                zout.writestr(item, script_lc)
            elif item.filename == 'META-INF/manifest.xml':
                content = data.decode('utf-8')
                if 'GenerateBarcodes' not in content:
                    content = content.replace('</manifest:manifest>',
                        manifest_entries + '\n</manifest:manifest>')
                zout.writestr(item, content.encode('utf-8'))
            else:
                zout.writestr(item, data)
        zout.writestr('Basic/Standard/GenerateBarcodes.xml', macro_xml.encode('utf-8'))
shutil.move(tmp, dst)
```

### Macro XML template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script"
    script:name="MacroName" script:language="StarBasic">
' StarBasic code here
' XML special chars must be escaped:
'   & → &amp;
'   < → &lt;
'   > → &gt;
'   " → &quot;
'   ' → &apos;
Sub MyMacro()
    MsgBox &quot;Hello from LibreOffice&quot;, 64, &quot;Test&quot;
End Sub
</script:module>
```

## Pitfalls

- **UNO module not in system Python** — On Debian/Ubuntu, `import uno` only works from LibreOffice's bundled Python, not `/usr/bin/python3`. No separate `libreoffice-python` package exists in Ubuntu 24.04+.
- **`doc.BasicLibraries` vs `doc.getBasicLibraries()`** — The UNO Python bridge exposes some properties as direct attributes, not methods. If `getBasicLibraries()` fails, try the property form.
- **`insertByName()` vs `replaceByName()`** — If a module with the target name already exists, `insertByName` raises an error. Use `try/except` with `replaceByName` fallback.
- **Macro encoding** — XML special characters in StarBasic source code MUST be escaped. The StarBasic comment `'` and line continuations `_` are fine as-is.
- **Approach A vs B** — UNO (A) is more robust but requires LibreOffice running. ZIP manipulation (B) works without LibreOffice but requires precise XML formatting.

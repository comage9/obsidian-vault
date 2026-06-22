# ODS StarBasic Macro Injection via zipfile

## Overview

ODS (OpenDocument Spreadsheet) files are standard ZIP archives. StarBasic macros are stored as XML files inside the archive. You can inject or replace macros without running LibreOffice by directly manipulating the ZIP contents.

## File Structure

```
Basic/
├── script-lc.xml                  # Standard library module index
├── Standard/
│   ├── GenerateBarcodes.xml       # Module source code
│   └── script-lb.xml              # Library metadata
├── VBAProject/                    # Preserved VBA macros (read-only)
│   ├── Module1.xml
│   ├── Module2.xml
│   └── ...
└── script-lb.xml
```

## Step-by-Step Injection

### 1. Create the Module XML

Each StarBasic module is an XML file with the module source entity-encoded:

```python
macro_code = '''
Sub Hello()
    MsgBox "Hello from ODS!"
End Sub
'''

# Entity-encode for XML
escaped = (macro_code
    .replace('&', '&amp;')
    .replace('<', '&lt;')
    .replace('>', '&gt;')
    .replace('"', '&quot;')
)

module_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script"
  script:name="Hello" script:language="StarBasic"
  script:moduleType="normal">{escaped}
</script:module>'''
```

### 2. Update script-lc.xml

This file registers which modules belong to the Standard library:

```python
script_lc = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:library PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "library.dtd">
<script:library xmlns:script="http://openoffice.org/2000/script"
  script:name="Standard" script:readonly="false">
<script:module index:script:name="Hello" script:language="StarBasic"
  script:moduleType="normal"/>
</script:library>'''
```

If adding to an existing ODS that already has modules, you must preserve existing module references and append the new one.

### 3. Update META-INF/manifest.xml

Add entries so LibreOffice knows about the new macro file:

```python
add = '''
<manifest:file-entry manifest:media-type="application/vnd.sun.star.basic-library"
    manifest:full-path="Basic/"/>
<manifest:file-entry manifest:media-type="text/xml"
    manifest:full-path="Basic/Standard/Hello.xml"/>
'''

# Insert before </manifest:manifest>
content = content.replace('</manifest:manifest>', add + '\n</manifest:manifest>')
```

### 4. Repack

```python
import zipfile, tempfile, shutil

src = 'input.ods'
dst = 'output.ods'
tmp = tempfile.mktemp()

with zipfile.ZipFile(src, 'r') as zin:
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'Basic/script-lc.xml':
                zout.writestr(item, script_lc)
            elif item.filename == 'META-INF/manifest.xml':
                content = data.decode('utf-8')
                if 'Hello' not in content:
                    content = content.replace('</manifest:manifest>', add + '\n</manifest:manifest>')
                zout.writestr(item, content.encode('utf-8'))
            else:
                zout.writestr(item, data)
        zout.writestr('Basic/Standard/Hello.xml', module_xml.encode('utf-8'))

shutil.move(tmp, dst)
```

## Verification

After injection, verify by examining the output:

```bash
python3 -c "
import zipfile
with zipfile.ZipFile('output.ods') as z:
    names = z.namelist()
    print('Basic files:', [n for n in names if n.startswith('Basic/')])
    print('Manifest has Basic:', 'Basic/Standard/Hello.xml' in 
          z.read('META-INF/manifest.xml').decode())
"
```

## Adding Multiple Modules

For multiple modules, add multiple `<script:module>` entries in `script-lc.xml`:

```xml
<script:module index:script:name="ModuleA" .../>
<script:module index:script:name="ModuleB" .../>
```

And add all `.xml` files to the manifest and archive.

## Limitations

- XLSM format CANNOT store StarBasic modules — only VBA macros. Use ODS format for StarBasic.
- LibreOffice can run VBA macros in XLSM files (with VBASupport 1), but not StarBasic modules stored in XLSM.
- The zipfile method works for INJECTION but not for reading/modifying existing macro source code (XML parsing complexity).

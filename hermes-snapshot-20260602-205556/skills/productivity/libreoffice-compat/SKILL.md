---
name: libreoffice-compat
description: Analyze and repair Excel (.xlsm/.xlsx) files for LibreOffice Calc compatibility — formula migration, macro porting, VBA project analysis.
category: productivity
---

# LibreOffice Compatibility — Excel Document Repair

Analyze and repair Excel files (especially `.xlsm` with macros) for correct rendering in LibreOffice Calc. Covers formula migration, VBA-to-Basic porting, and structural analysis with openpyxl.

## When to Load

- User provides an `.xlsm` or `.xlsx` file that shows `#REF!`, `#NAME?`, or `_xlfn.` errors in LibreOffice
- User asks to "리브오피스에 맞게 수정" (adapt for LibreOffice)
- Need to extract or modify VBA macros stored in `xl/vbaProject.bin`

## Analysis Tools

### 1. Open Workbook with openpyxl

```python
import openpyxl

# With formulas (for analysis)
wb = openpyxl.load_workbook('file.xlsm', data_only=False)

# With cached values (for data)
wb = openpyxl.load_workbook('file.xlsm', data_only=True)
```

### 2. XLSM Structure (ZIP)

```python
import zipfile
with zipfile.ZipFile('file.xlsm', 'r') as z:
    for f in z.namelist():
        print(f, z.getinfo(f).file_size)
    # Macros live in: xl/vbaProject.bin
```

## Common LibreOffice Incompatibilities

### `_xlfn.` Prefix (MOST COMMON)

Excel marks "future functions" with `_xlfn.` prefix. LibreOffice does not recognize this prefix.

**Fix:** Global replace `_xlfn.xlookup` → `XLOOKUP` (case-sensitive).

Other `_xlfn.` functions: `_xlfn.xmatch`, `_xlfn.textbefore`, `_xlfn.textafter`, `_xlfn.filter`, `_xlfn.unique`, `_xlfn.sort`, `_xlfn.single`, `_xlfn.lambda`, `_xlfn.let`, etc.

### `_xlfn.single()` — Not in LibreOffice

`SINGLE()` extracts a single value from a range/array. LibreOffice has no equivalent.

**Fix:** Remove the `_xlfn.single(...)` wrapper entirely — it's redundant when wrapped around `XLOOKUP` which already returns a single value.

Pattern: `=_xlfn.single(_xlfn.xlookup(...))` → `=XLOOKUP(...)`

### `#REF!` — Broken References

Common causes:
- Column/row was deleted from the lookup table after formulas were written
- Sheet was renamed or deleted
- Named range was deleted

**Fix:** Determine the correct column reference from the lookup table sheet (check column headers or data patterns), then replace `#REF!` with the correct range (e.g. `'vf 품목'!$J:$J`).

### `VLOOKUP` — OK (LibreOffice compatible)
### `TODAY()`, `NOW()` — OK
### `IF()`, text concatenation (`&`) — OK
### `HYPERLINK()` — OK (LibreOffice compatible)

### `IMAGE()` — LibreOffice Partial Support

Excel's `IMAGE(url, mode, height, width)` function is **only available in LibreOffice 25.2+** — and **with a different parameter order**: `IMAGE(URL; width; height; mode)`.

**Version 24.2:** No `IMAGE()` function at all → `#NAME?`.
**Version 25.2+:** Function exists but parameter order differs from Excel → wrong rendering or `#NAME?`.

**Fix (for all versions):** Replace `IMAGE(...)` with a non-function alternative:

| Approach | Method |
|----------|--------|
| Best | Remove entirely (empty cell) or replace with URL text via `=""` |
| Alternative | `HYPERLINK(url, "Barcode")` — shows clickable URL, no image |
| For macro-based | Use `GenerateBarcodes` StarBasic macro to insert images |

**Pitfall:** LibreOffice's XLSX→ODS converter may automatically convert a URL in a formula cell to `image()` even if the original formula wasn't `=IMAGE()`. Watch for auto-generated `image(...)` in content.xml after conversion.

### ArrayFormula (`f t="array"`) — Causes `#NAME?` in LibreOffice

Excel CSE (Ctrl+Shift+Enter) array formulas stored as `<f t="array" ref="A1">` in the XLSX XML **are not supported by LibreOffice Calc**.

**Fix (modify XLSX XML via zipfile):** Remove the `t="array"` attribute and `ref="..."` attribute from the formula element:

```python
import zipfile, re
with zipfile.ZipFile('file.xlsx', 'r') as zin:
    with zipfile.ZipFile('fixed.xlsx', 'w') as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith('.xml'):
                text = data.decode('utf-8')
                text = re.sub(r'<f t="array" ref="[^"]*">', '<f>', text)
                data = text.encode('utf-8')
            zout.writestr(item, data)
```

### XLOOKUP not available (older LibreOffice)

LibreOffice added `XLOOKUP` in **version 24.8**. Earlier versions will show `#NAME?`.

**Fix when XLOOKUP is missing:** Convert to `VLOOKUP(lookup_value, table_array, col_index, range_lookup)`:

| Original XLOOKUP | VLOOKUP Equivalent |
|---|---|
| `XLOOKUP(A1, B:B, E:E)` | `VLOOKUP(A1, A:V, 5, 0)` — col E is 5th col from A |
| `XLOOKUP(A1, B:B, F:F, 0, 0)` | `VLOOKUP(A1, A:V, 6, 0)` — col F is 6th col from A |
| `XLOOKUP(G1, B$2:B$922, S$2:S$922, 0)` | `VLOOKUP(G1, A$2:V$922, 19, 0)` — col S is 19th col from A |

**Column index formula:** `col_index = column_letter_to_number(target_col) - column_letter_to_number(start_col_of_table) + 1`

### FreeRDP RDP NLA / Kerberos Issues

When testing RDP connections for Windows-in-Docker setups (dockur/windows), FreeRDP may fail with NLA errors:

- `ERRCONNECT_LOGON_FAILURE` despite correct credentials — caused by **NLA (Network Level Authentication)** and **Kerberos** config
- `HYBRID_REQUIRED_BY_SERVER` — Windows requires NLA but client can't negotiate
- Fix on Windows side: Disable "Require Network Level Authentication" in Remote Desktop Settings
- Fix on client side: Try `/sec:tls` (if Windows allows), or `/sec:nla` with NTLM

For full desktop RDP (non-app mode), basic `+auth-only` often works when app-launch RDP fails.
## Macro (VBA) File Format

Macros in `.xlsm` are stored in `xl/vbaProject.bin` — a binary OLE compound document. **Direct modification is not feasible** via openpyxl or zipfile alone.

**Best practice:** Create a separate `.bas` file with the corrected macro in LibreOffice Basic syntax, then tell the user to import it:
1. LibreOffice Calc → Tools → Macros → Organize Macros → LibreOffice Basic
2. Manager → Import → select `.bas` file

## LibreOffice Basic vs VBA Key Differences

| Feature | Excel VBA | LibreOffice Basic |
|---------|-----------|-------------------|
| App object | `Application` | `ThisComponent` |
| Sheet access | `Worksheets("name")` | `Sheets.getByName("name")` |
| Cell access | `Range("A1")` | `getCellByPosition(0, 0)` |
| Drawings | Shapes collection | DrawPage |
| MsgBox | `MsgBox "text", vbInformation` | `MsgBox "text", 64, "title"` |
| Error handling | `On Error Resume Next` | `On Error GoTo Label` |
| String concat | `&` (same) | `&` (same) |

## Pitfalls

- **`Asc()` in LibreOffice Basic** returns the Unicode code point (e.g., 한글 → 54620). For URL encoding, this gives `%D55C` instead of proper UTF-8 byte sequence `%ED%95%9C`. For simple ASCII barcode data (product codes like "752"), this is fine.
- **`vbaProject.bin` cannot be easily modified** — it's OLE compound document format. Use decompilation tools (like `olefile` + `vba_extract.py` from oletools) only if absolutely necessary.
- **openpyxl warns about Conditional Formatting** — `UserWarning: Conditional Formatting extension is not supported and will be removed` is harmless; the file still opens correctly.

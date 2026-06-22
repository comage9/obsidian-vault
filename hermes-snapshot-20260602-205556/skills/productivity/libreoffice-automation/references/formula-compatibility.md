# Excel ↔ LibreOffice Calc Formula Compatibility

## Critical: `_xlfn.` Prefix

The `_xlfn.` prefix appears when Excel saves formulas using "future functions." This is Excel's internal marker and must be **stripped** before LibreOffice can interpret the formula.

**Always run:** Global search-and-replace of `_xlfn.xlookup` → `XLOOKUP`, `_xlfn.single` → remove entirely, etc.

## Function Compatibility Table

| Excel Function | LibreOffice Calc | Action Required |
|----------------|-----------------|-----------------|
| `XLOOKUP()` | Supported (LO 7.4+) | Strip `_xlfn.` prefix only |
| `XMATCH()` | Supported (LO 7.4+) | Strip `_xlfn.` prefix only |
| `SINGLE()` | **Not supported** | Remove wrapper entirely |
| `VLOOKUP()` | Fully supported | No change |
| `TODAY()` | Fully supported | No change |
| `NOW()` | Fully supported | No change |
| `TEXT()` | Fully supported | No change |
| `IF()` | Fully supported | No change |
| `SUMIFS()` | Fully supported | No change |
| `VBA functions` | Limited (`Option VBASupport 1`) | Rewrite in StarBasic |

## The `#REF!` Error

Causes:
1. Deleted columns/ranges that formulas reference
2. Corrupted named ranges
3. Sheet renames without updating references

Detection: Use `openpyxl` with `data_only=False` to scan for `#REF!` in formula strings:
```python
import openpyxl
wb = openpyxl.load_workbook('file.xlsm', data_only=False)
ws = wb['SheetName']
refs = []
for row in ws.iter_rows():
    for cell in row:
        if cell.value and isinstance(cell.value, str) and '#REF!' in cell.value:
            refs.append((cell.coordinate, cell.value))
```

## XLSM → ODS Conversion

| Format | Macro Support | Notes |
|--------|--------------|-------|
| XLSM | VBA in `xl/vbaProject.bin` (binary) | Hard to edit programmatically |
| ODS | StarBasic in `Basic/Standard/*.xml` (plain XML) | Easy to read/modify via ZIP |

**LibreOffice saves StarBasic macros only to ODS. Saving StarBasic back to XLSM fails with `SfxBaseModel::impl_store`**. Workflow:
1. Keep original XLSM for Excel users
2. Provide ODS for LibreOffice users (with embedded StarBasic macros)
3. Or embed VBA in XLSM (requires VBA editor, not programmatic)

## Tooling

| Tool | Purpose | Example |
|------|---------|---------|
| openpyxl | Read/write formulas, detect `_xlfn.` and `#REF!` | Python script analysis |
| LibreOffice UNO | Insert macros, convert formats | Headless Python UNO |
| zipfile | Inspect ODS internal structure | ODS = ZIP, macros in Basic/ |

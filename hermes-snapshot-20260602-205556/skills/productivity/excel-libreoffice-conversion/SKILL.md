---
name: excel-libreoffice-conversion
description: Convert Excel (.xlsm/.xlsx) files with advanced formulas (XLOOKUP, SINGLE, _xlfn prefix, #REF! errors) to LibreOffice Calc-compatible format — analyze, diagnose, and repair formula compatibility issues
---

# Excel → LibreOffice Formula Conversion

## Trigger

Use this skill when a user asks you to:
- Make an Excel `.xlsm` / `.xlsx` file work in LibreOffice Calc
- Fix errors like `#NAME?`, `#REF!`, or `#VALUE!` that appear only in LibreOffice
- "엑셀 파일을 리브오피스에 맞게 수정"
- "엑셀 수식 오류 수정"

## Diagnostic Flow

### 1. Open and Inspect the File

Use openpyxl to examine the workbook structure, formulas, and VBA:

```bash
python3 << 'EOF'
import openpyxl
wb = openpyxl.load_workbook('file.xlsm', data_only=False)
print('Sheets:', wb.sheetnames)

# Check VBA
try:
    vba = wb.vba_project
    print('VBA:', 'present' if vba else 'none')
except:
    print('VBA: none or unreadable')

# Examine each sheet for formulas
for name in wb.sheetnames:
    ws = wb[name]
    formulas = 0
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                formulas += 1
    print(f'  {name}: {formulas} formulas, {ws.max_row} rows × {ws.max_column} cols')
EOF
```

### 2. Scan for Known LibreOffice-Incompatible Patterns

| Pattern | Excel | LibreOffice | Fix |
|---------|-------|-------------|-----|
| `_xlfn.xlookup(...)` | XLOOKUP (Excel 2019+) | Supported (LO 7.4+) but `_xlfn.` prefix rejected | Replace `_xlfn.xlookup` → `XLOOKUP` |
| `_xlfn.single(...)` | SINGLE (Excel 365) | **NOT supported** | Remove the `_xlfn.single(...)` wrapper; XLOOKUP already returns a single value |
| `_xlfn.xmatch(...)` | XMATCH | Supported | Replace `_xlfn.xmatch` → `XMATCH` |
| `_xlfn.xsort(...)` | XSORT | NOT supported | Replace with SORT or INDEX/MATCH |
| `_xlfn.*` prefix | Any "future function" marker | Rejected | Strip `_xlfn.` prefix from all function names |
| `#REF!` in formula | Broken reference | Broken reference | Identify the intended target range from other formulas in the same column |
| `=#REF!` in header cell | Formula that once computed a value | Broken | Remove/replace with static text |

### 3. Investigate `#REF!` Broken References

When a formula contains `#REF!`, the original range was deleted or corrupted. To recover the intended reference:

**Step 1: Understand what the column represents**

Look at the cell's context:
```python
# Check neighboring column headers and values
for col in ws.iter_cols(min_row=1, max_row=2):
    print([c.value for c in col])
```

**Step 2: Cross-reference with other formulas in the same column**

Formulas in the same column typically follow the same pattern. Compare a healthy formula against the broken one:

```python
# Compare broken H7 with working D7 in same row
for cell in [ws.cell(7, c) for c in [4, 8]]:  # D=4, H=8
    print(cell.value)
```

**Step 3: Identify the lookup target sheet and column**

The `#REF!` occurs where the lookup array (2nd argument) and return array (3rd argument) of XLOOKUP should be. Healthy XLOOKUP formulas in nearby columns reveal the target sheet:

- `D7: XLOOKUP(A7, 'TargetSheet'!$B:$B, 'TargetSheet'!$E:$E)` → target sheet is visible
- The 2nd and 3rd arguments that became `#REF!` referenced the same `'TargetSheet'!` ranges

**Step 4: Find the correct column in the target sheet**

```python
# Examine target sheet headers
ws2 = wb['TargetSheet']
for col in range(1, ws2.max_column + 1):
    print(f'{get_column_letter(col)}: {ws2.cell(1, col).value}')
```

Match the column purpose (e.g., "생산단위" = production unit = pieces per box) to what the broken formula column represents (e.g., "Pcs/BOX").

### 4. Data-Only Verification

Use `data_only=True` to see cached values (may show `#NAME?` for unrecognized functions):

```bash
python3 << 'EOF'
import openpyxl
wb = openpyxl.load_workbook('file.xlsm', data_only=True)
ws = wb['Sheet1']
# Check a specific cell's cached value
for row in range(1, 10):
    val = ws.cell(row, 8).value  # H column
    print(f'H{row}: {val}')
EOF
```

`#NAME?` confirms the formula uses functions that openpyxl/libreoffice can't evaluate. `None` in data_only mode means the cell was never cached (empty or error).

## Common Fixes

### Fix 1: Strip `_xlfn.` Prefix (Global Replace)

This is the single most common fix. Replace `_xlfn.xlookup` with `XLOOKUP` (case-sensitive, preserve rest):

```python
import openpyxl, re
wb = openpyxl.load_workbook('file.xlsm', data_only=False)
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and '_xlfn.' in cell.value:
                cell.value = cell.value.replace('_xlfn.xlookup', 'XLOOKUP')
                cell.value = cell.value.replace('_xlfn.single', '')
                # Remove empty parentheses left by SINGLE() removal
                # e.g. =SINGLE(XLOOKUP(...)) → =XLOOKUP(...)
wb.save('file_fixed.xlsx')  # save as .xlsx to drop VBA
```

### Fix 2: Remove SINGLE() Wrapper

`_xlfn.single(...)` wraps a single-value formula. XLOOKUP already returns a single value, so the wrapper is redundant. **Use balanced-paren parsing** (not fragile string replace) to remove the wrapper:

```python
while 'SINGLE(' in new_formula:
    start = new_formula.index('SINGLE(')
    depth = 1
    i = start + 7  # len('SINGLE(')
    while depth > 0 and i < len(new_formula):
        if new_formula[i] == '(': depth += 1
        elif new_formula[i] == ')': depth -= 1
        i += 1
    inner = new_formula[start+7:i-1]
    new_formula = new_formula[:start] + inner + new_formula[i:]
```

This correctly handles nested parens (e.g. `SINGLE(XLOOKUP(...))` and `SINGLE(IF(...))`) while avoiding the fragile `str.replace` approach that breaks formulas with multiple single-letter references.

Before: `=_xlfn.single(_xlfn.xlookup(A7,#REF!,#REF!))`
After:  `=XLOOKUP(A7,'vf 품목'!$B:$B,'vf 품목'!$J:$J)`

### Fix 3: Repair `#REF!` References

Replace `#REF!` with the correct sheet and column range:

```
Before: =_xlfn.xlookup(A7,#REF!,#REF!)
After:  =XLOOKUP(A7,'vf 품목'!$B:$B,'vf 품목'!$J:$J)
```

The correct recovery depends on which column the lookup target belongs to in the source sheet.

### Fix 4: Handle Header Cells With `=#REF!`

A header cell containing `=#REF!` means its formula broke. Since headers are usually static labels, replace with plain text:

```python
ws.cell(1, col).value = "Correct Header Text"
```

## Verification

Open the repaired file in LibreOffice Calc and verify:
- No `#NAME?` errors (unrecognized functions)
- No `#REF!` errors (broken references)
- XLOOKUP formulas resolve to values
- Conditional formatting is preserved (openpyxl warns about unsupported extensions but usually removes them — warn the user)

### Full Delivery Pipeline

This skill focuses on **formula diagnosis only**. For the complete workflow — including converting to ODS format and embedding corrected StarBasic macros into a single deliverable file — see the umbrella skill [`libreoffice-automation`](skill_view?name=libreoffice-automation) and its reference `references/full-repair-pipeline.md`.

Key additional steps beyond formula fixing:

```bash
# Convert fixed XLSM to ODS format (LibreOffice native)
soffice --headless --norestore --convert-to ods:calc8 fixed.xlsm

# Formula syntax changes after conversion:
# Excel:  =XLOOKUP(A7,'vf 품목'!$B:$B,'vf 품목'!$E:$E)
# ODS:    of:=xlookup([.A7];[$'vf 품목'.$B:.$B];[$'vf 품목'.$E:.$E])
```

> **⚠️ Always deliver a complete working file, not separate components.** When the user asks for a fixed document, provide a single `.ods` with both corrected formulas and embedded macros. Providing only a `.bas` file or separate instructions is a known source of user frustration.

## Pitfalls

- **openpyxl removes conditional formatting it doesn't understand** — the warning `Conditional Formatting extension is not supported and will be removed` is expected and usually harmless for core formula compatibility.
- **VBA macros are NOT preserved** when saving with openpyxl. Save as `.xlsx` (not `.xlsm`) to signal that macros are dropped. Inform the user.
- **`data_only=True` values may be wrong** — openpyxl returns whatever Excel last cached. If the formulas in data_only mode show `#NAME?`, it means openpyxl itself couldn't evaluate them (not just LibreOffice).
- **Column header may be on row 2 instead of row 1** — some sheets use row 1 as auto-generated "Column1, Column2..." placeholders and row 2 for real headers. Always check both rows.
- **`_xlfn.single(` may leave empty `()`** — after removing `_xlfn.single(`, the closing `)` remains. Clean up parentheses using balanced-paren parsing (see Fix 2 above), not string replace.
- **User frustration signal: delivering analysis-only instead of a working file** — If the user asks to "fix the file" and you deliver formula analysis plus a separate `.bas` file, expect frustration. The user wants a single working document, not assembly instructions. Always pair diagnostics with a complete deliverable. See the full pipeline in `libreoffice-automation`.

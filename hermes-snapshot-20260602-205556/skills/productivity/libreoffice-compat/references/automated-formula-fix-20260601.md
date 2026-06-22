# Automated Formula Fix Session (2026-06-01)

## Context
XLSM file (패킹 리스트-유원피에스) with 219 formulas in VF sheet + 11 in 바코드 sheet. Fixed for LibreOffice 24.2 → 26.2 compatibility.

## Fix Script Pattern

```python
import openpyxl, re, zipfile, shutil
from openpyxl.utils import get_column_letter

# Load with VBA preserved
wb = openpyxl.load_workbook('file.xlsm', keep_vba=True)

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                old = cell.value
                new = old
                
                # 1. Remove _xlfn. prefix
                new = new.replace('_xlfn.xlookup', 'XLOOKUP')
                new = new.replace('_xlfn.single', 'SINGLE')
                
                # 2. Unwrap SINGLE(XLOOKUP(...)) → XLOOKUP(...)
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
                
                # 3. Replace #REF! with correct ranges
                if '#REF!' in new:
                    # H column (col 8): 생산단위 from 'vf 품목'!J:J
                    col_letter = get_column_letter(cell.column)
                    if cell.column == 8:
                        new = re.sub(
                            r"XLOOKUP\(([^,]+),#REF!,#REF!\)",
                            r"XLOOKUP(\1,'vf 품목'!$B:$B,'vf 품목'!$J:$J)",
                            new
                        )
                
                if new != old:
                    cell.value = new

wb.save('fixed.xlsm')
```

## Key Column Mapping
| Column | Purpose | Lookup Table Reference |
|--------|---------|----------------------|
| VF!D | Product name | `'vf 품목'!E:E` |
| VF!H | Pcs/BOX (생산단위) | `'vf 품목'!J:J` |
| VF!K | English name | `'vf 품목'!F:F` |
| VF!T~W | Data propagation | Same row, column offsets |

## Results
- 108 formulas fixed across VF + 바코드 sheets
- LibreOffice conversion → ODS format automatically converts `XLOOKUP()` to `xlookup()` in Calc-native `of:=` syntax and replaces `#REF!` with proper sheet-qualified references

## Pitfalls
- `openpyxl keep_vba=True` preserves `xl/vbaProject.bin` but does NOT fix formulas inside VBA modules themselves
- The `#REF!` column mapping must be verified manually — there's no way to programmatically determine the original intended column
- LibreOffice `--convert-to ods` may drop conditional formatting but preserves data and formulas

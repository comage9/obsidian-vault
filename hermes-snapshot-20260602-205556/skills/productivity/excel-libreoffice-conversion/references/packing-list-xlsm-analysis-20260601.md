# Session Reference: 패킹 리스트 XLSM Analysis (2026-06-01)

## File Overview

- **File:** 패킹 리스트-유원피에스.xlsm
- **Size:** ~4MB
- **Format:** Microsoft Excel 2007+ (.xlsm with macros)
- **Expected use:** LibreOffice Calc compatible output

## Sheet Structure

| Sheet | Rows | Cols | Formulas | Role |
|-------|------|------|----------|------|
| VF | 62 | 97 | 219 | Main packing list template |
| 바코드 | 88 | 14 | 11 | Barcode label output |
| 쿠팡품목 | 3203 | 28 | 0 | Coupang item database (reference) |
| vf 품목 | 922 | 22 | 0 | Product master DB (reference) |
| DPCache_* (3) | 4-5 | 1 | 0 | Pivot cache remnants (ignore) |

## Issues Found

### Issue 1: `_xlfn.xlookup` → `XLOOKUP` (global, ~230 occurrences)

**Cause:** Excel marks newer functions with `_xlfn.` prefix. LibreOffice supports XLOOKUP but rejects the `_xlfn.` prefix.

**Occurs in:** VF sheet (columns D, H, K), 바코드 sheet (columns A, B, F, G)

### Issue 2: `_xlfn.single()` → remove wrapper (~52 occurrences)

**Cause:** LibreOffice does not have the SINGLE() function. SINGLE() extracts a single value from a range/array. When wrapping XLOOKUP (which already returns a single value), it's redundant.

**Occurs in:** VF sheet column H (H8-H62, specific rows only — H7, H27-H30 lack SINGLE for unknown reason)

### Issue 3: `#REF!` in XLOOKUP ranges (all H column rows)

**Cause:** The 2nd and 3rd arguments of XLOOKUP in H column are `#REF!` — the original column reference in `vf 품목` sheet was deleted.

**Recovery:** H column = "Pcs/BOX" (개수/박스). In `vf 품목` sheet, column J = "생산단위" (production unit = pieces per box).

- 제품코드 752 → 생산단위 8 → "1P=8BOX"
- 제품코드 720 → 생산단위 8
- 제품코드 721 → 생산단위 8

**Fix:** Replace `#REF!` with `'vf 품목'!$J:$J`

### Issue 4: `Q1: =#REF!`

**Cause:** Formula in header cell broke. Original unknown.

**Fix:** Replace with static text. Likely a unit/label value based on nearby cells R1=`(`, T1=`40`, U1=`BOX)` → combination would be like `(40BOX)`.

## Formula Pattern After Fix

**VF sheet row 7 (fixed):**
```
D7: =XLOOKUP(A7,'vf 품목'!$B:$B,'vf 품목'!$E:$E)    # Product name lookup
H7: =XLOOKUP(A7,'vf 품목'!$B:$B,'vf 품목'!$J:$J)    # Pcs/BOX lookup (was #REF!)
K7: =IF(A7="","",XLOOKUP(A7,'vf 품목'!$B:$B,'vf 품목'!$F:$F))  # Conditional lookup
```

**바코드 sheet (fixed):**
```
A1: =XLOOKUP($L$1,'vf 품목'!B:B,'vf 품목'!F:F,0,0)
```

## Row Pattern Anomalies

Several VF sheet rows reference the WRONG source row:

| Cell | Current | Should Be |
|------|---------|-----------|
| J9 | `IF(A8=""...` | `IF(A9=""...` |
| K9 | XLOOKUP referencing A8 | Should reference A9 |
| T9 | References B8 | Should be B9 |
| U9 | References E8 | Should be E9 |
| V9 | References A8:C8 | Should be A9:C9 |
| W9 | References F8 | Should be F9 |

These appear to be copy-paste errors in the template. Rows 7-8 reference A7/A8 correctly, but rows 9+ reference row 8 instead of their own row. Not a LibreOffice compatibility issue but a logic error.

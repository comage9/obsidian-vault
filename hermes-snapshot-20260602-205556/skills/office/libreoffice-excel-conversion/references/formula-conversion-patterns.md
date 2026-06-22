# Excel-to-LibreOffice Formula Conversion Regex Patterns

XLSX stores formulas as XML. Key patterns for zipfile-based editing:

## XLOOKUP → VLOOKUP
```python
# XLOOKUP(lookup, arr, result, [not_found], [match], [search])
# VLOOKUP(lookup, table, col_idx, [range])
import re

# Pattern: XLOOKUP($G$1, 'vf 품목'!B:B, 'vf 품목'!F:F, 0, 0)
# Column mapping for vf 품목 sheet:
#   A=순번, B=제품코드, C=등록일자, D=SKU, E=바코드, F=제품명,
#   G=대분류, H=색상, I=단수, J=생산단위, K=구분,
#   S=영문명 (col 19)

text = re.sub(
    r'XLOOKUP\(\$G\$1,\'vf 품목\'!B:B,\'vf 품목\'!F:F,0,0\)',
    'VLOOKUP($G$1,\'vf 품목\'!A:V,6,0)', text)
text = re.sub(
    r'XLOOKUP\(\$G\$1,\'vf 품목\'!B:B,\'vf 품목\'!E:E,0\)',
    'VLOOKUP($G$1,\'vf 품목\'!A:V,5,0)', text)
```

## Array Formula (CSE) → Normal Formula
```python
# Original: <f t="array" ref="A1">XLOOKUP(...)</f>
# Fixed:   <f>XLOOKUP(...)</f>
text = re.sub(r'<f t="array" ref="[^"]*">', '<f>', text)
```

## IMAGE Function Removal
LibreOffice does not support `IMAGE()` worksheet function.

**In XLSX XML** (uses XML entities):
```python
# =IMAGE("url"&cell,4,80,220)
text = re.sub(r'IMAGE\(&quot;[^&]*&quot;&amp;[^,]+,[^)]*\)', '""', text)
```

**After ODS conversion**, LibreOffice may re-generate `image()` from URL patterns:
```python
# of:=image("url"&[.B7];4;80;220)
text = re.sub(r'of:=image\(&quot;[^&]+&quot;&amp;[^;]+;[^;]+;[^;]+;[^;]+\)', 'of:=""', text)
```

## _xlfn. Prefix Removal
```python
text = text.replace('_xlfn.xlookup', 'XLOOKUP')
text = text.replace('_xlfn.single', 'SINGLE')
text = text.replace('_xlfn.', '')
```

## SINGLE() Removal
SINGLE() wraps a single-element array into a scalar. Redundant around XLOOKUP:
```python
# SINGLE(XLOOKUP(...)) → XLOOKUP(...)
while 'SINGLE(' in text:
    start = text.index('SINGLE(')
    depth = 1; i = start + 7
    while depth > 0 and i < len(text):
        if text[i] == '(': depth += 1
        elif text[i] == ')': depth -= 1
        i += 1
    inner = text[start+7:i-1]
    text = text[:start] + inner + text[i:]
```

## #REF! Fix for Label Print Packing Lists
In VF packing list sheets, column H (Pcs/BOX) had broken #REF! references:
```python
# Original: XLOOKUP(A7,#REF!,#REF!)
# Fixed: XLOOKUP(A7,'vf 품목'!$B:$B,'vf 품목'!$J:$J)
text = re.sub(
    r'XLOOKUP\(([^,]+),#REF!,#REF!\)',
    r'XLOOKUP(\1,\'vf 품목\'!$B:$B,\'vf 품목\'!$J:$J)',
    text)
```

## VLOOKUP Column Index for 'vf 품목' Sheet
| Column | Field | VLOOKUP Index |
|--------|-------|---------------|
| B | 제품코드 (Product Code) | — | 
| E | 바코드 (Barcode) | 5 |
| F | 제품명 (Product Name) | 6 |
| J | 생산단위 (Production Unit/Pcs per Box) | 10 |
| S | 영문명 (English Name) | 19 |

Table range: `'vf 품목'!A:V` (columns A-V, 22 columns)

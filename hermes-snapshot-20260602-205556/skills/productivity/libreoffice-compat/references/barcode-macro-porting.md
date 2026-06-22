# Barcode Macro Porting — Excel VBA → LibreOffice Basic

Ported from the VF packing list XLSM (`패킹 리스트-유원피에스.xlsm`) during session 2026-06-01 using Reasonix (deepseek-v4-pro).

## Original Bugs Found

1. **`com.sun.star.geometry.convertValue()`** — Never existed in LibreOffice API. Use manual URL encoding.
2. **`oTargetCell.Position`** — Cell object has no `.Position`. Correct: `oSheet.getCellByPosition(col, row).Position`.
3. **URL encoding missing** — Barcode text with spaces/special chars breaks the API URL.
4. **External API dependency** — Uses `api-bwipjs.metafloor.com`; fails offline.

## Corrected Macro Structure

```vba
Sub GenerateBarcodes()
    ' 1. Get sheet "바코드" → DrawPage
    ' 2. Remove existing BwipBarcode_* shapes
    ' 3. Loop rows 7-62: read A col, build API URL, create GraphicObjectShape
    ' 4. Position at B col cell, add to DrawPage
End Sub

Function UrlEncode(ByVal sText As String) As String
    ' Safe chars: A-Z, a-z, 0-9, -._~ → pass through
    ' Space → %20
    ' Other → %Hex(Asc(char))
End Function
```

## Key LibreOffice APIs Used

- `ThisComponent` — main document
- `Sheets.getByName("바코드")` — sheet access
- `getDrawPage()` — drawing layer for images
- `createInstance("com.sun.star.drawing.GraphicObjectShape")` — image shape
- `.GraphicURL` — set image source (URL or file:///)
- `getCellByPosition(col, row).Position` — cell position for image placement
- `com.sun.star.awt.Size` — image dimensions (1/100mm units)
- `com.sun.star.awt.Point` — position coordinates

## Output File

The corrected macro was saved as `/home/comage/문서/GenerateBarcodes.bas` (130 lines).
Import in LibreOffice: Tools → Macros → Organize Macros → LibreOffice Basic → Manager → Import.

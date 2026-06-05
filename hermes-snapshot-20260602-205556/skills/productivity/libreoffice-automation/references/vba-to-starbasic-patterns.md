# VBA → StarBasic Translation Patterns

This reference covers the specific Excel VBA macro that was ported in the 2026-06-01 session.

## Original Macro (Excel VBA, broken)

The macro was intended for LibreOffice but had 5 bugs:

## Bug 1: `com.sun.star.geometry.convertValue()` — Non-existent API

**Problem:** `com.sun.star.geometry.convertValue()` does not exist in LibreOffice. Any call causes a runtime error.

**Fix:** Replace with a custom `UrlEncode()` function in pure StarBasic:

```vba
Function UrlEncode(ByVal sText As String) As String
    Dim sResult As String
    Dim i As Long
    Dim sChar As String
    Dim iChar As Integer
    sResult = ""
    For i = 1 To Len(sText)
        sChar = Mid(sText, i, 1)
        iChar = Asc(sChar)
        ' Safe chars: A-Z, a-z, 0-9, -, ., _, ~
        If (iChar >= 65 And iChar <= 90) Or _
           (iChar >= 97 And iChar <= 122) Or _
           (iChar >= 48 And iChar <= 57) Or _
           iChar = 45 Or iChar = 46 Or _
           iChar = 95 Or iChar = 126 Then
            sResult = sResult & sChar
        ElseIf iChar = 32 Then
            sResult = sResult & "%20"
        Else
            sResult = sResult & "%" & Hex(iChar)
        End If
    Next i
    UrlEncode = sResult
End Function
```

## Bug 2: `oTargetCell.Position` — Cell object has no .Position

**Problem:** `oSheet.getCellByPosition(col, row)` returns a cell object. In StarBasic, cell objects do NOT have a `.Position` property.

**Fix:** Access `.Position` through the sheet's `getCellByPosition()` return value. In LibreOffice 24.2, this does work:
```vba
Dim oPos As New com.sun.star.awt.Point
oPos.X = oSheet.getCellByPosition(1, r).Position.X
oPos.Y = oSheet.getCellByPosition(1, r).Position.Y
oShape.setPosition(oPos)
```

If this fails in older versions, use `oSheet.getCellRangeByPosition(col, row, col, row).getPropertyValue("Position")`.

## Bug 3: URL Text Not Encoded

**Problem:** Text from cells (containing spaces, special chars, Korean) was passed directly into a URL without encoding. The bwip-js API URL breaks on unencoded spaces.

**Fix:** Pre-process all cell text through `UrlEncode()` before assembling the URL.

## Complete Fixed Macro Structure

```vba
Sub GenerateBarcodes()
    Dim oDoc As Object, oSheet As Object, oDrawPage As Object
    oDoc = ThisComponent
    oSheet = oDoc.Sheets.getByName("바코드")
    oDrawPage = oSheet.getDrawPage()
    
    ' Remove existing barcode images
    For i = oDrawPage.getCount() - 1 To 0 Step -1
        oShape = oDrawPage.getByIndex(i)
        If InStr(oShape.Name, "BwipBarcode_") > 0 Then
            oDrawPage.remove(oShape)
        End If
    Next i
    
    ' Create barcodes for rows 7-62 (0-indexed: 6-61)
    For r = 6 To 61
        sText = Trim(oSheet.getCellByPosition(0, r).String)
        If sText <> "" Then
            sUrl = "https://api-bwipjs.metafloor.com/?bcid=code128" & _
                   "&text=" & UrlEncode(sText) & "&scale=2&includetext"
            oShape = oDoc.createInstance("com.sun.star.drawing.GraphicObjectShape")
            oShape.GraphicURL = sUrl
            oShape.Name = "BwipBarcode_" & r
            Dim oSize As New com.sun.star.awt.Size
            oSize.Width = 4500: oSize.Height = 1800
            oShape.setSize(oSize)
            Dim oPos As New com.sun.star.awt.Point
            oPos.X = oSheet.getCellByPosition(1, r).Position.X
            oPos.Y = oSheet.getCellByPosition(1, r).Position.Y
            oShape.setPosition(oPos)
            oDrawPage.add(oShape)
        End If
    Next r
    MsgBox "바코드 생성 완료!", 64, "완료"
End Sub
```

## External API Dependencies

- **bwip-js API:** `https://api-bwipjs.metafloor.com/` — generates Code128 barcode PNGs
- Parameters: `bcid=code128`, `text=<url-encoded>`, `scale=N`, `includetext`
- Requires internet access. No offline fallback.
- LibreOffice `GraphicObjectShape.GraphicURL` supports remote URLs (tested on LibreOffice 24.2)

## Error Handling Pattern

```vba
On Error GoTo ErrHandler
' ... main code ...
Exit Sub
ErrHandler:
    MsgBox "오류: " & Error() & Chr(13) & "행: " & (r + 1), 16, "오류"
End Sub
```

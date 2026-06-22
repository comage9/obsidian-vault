'========================================================================
' LibreOffice Basic Barcode Generator for Zebra ZPL Printers
' Uses bwip-js API to generate barcode images, embeds in Calc sheet
'========================================================================
Sub GenerateBarcodes()
    Dim oDoc As Object, oSheet As Object, oDrawPage As Object
    Dim oShape As Object, sText As String, sUrl As String
    Dim r As Long, i As Long
    
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
    
    ' Process data rows (7~62, 0-index: 6~61)
    For r = 6 To 61
        sText = Trim(oSheet.getCellByPosition(0, r).getString())
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
            oPos.X = oSheet.getCellByPosition(1, r).getPosition().X
            oPos.Y = oSheet.getCellByPosition(1, r).getPosition().Y
            oShape.setPosition(oPos)
            oDrawPage.add(oShape)
        End If
    Next r
    MsgBox "Barcode generation complete!", 64, "Done"
End Sub

Function UrlEncode(ByVal sText As String) As String
    Dim sResult As String, i As Long, sChar As String, iChar As Integer
    sResult = ""
    For i = 1 To Len(sText)
        sChar = Mid(sText, i, 1): iChar = Asc(sChar)
        If (iChar >= 65 And iChar <= 90) Or (iChar >= 97 And iChar <= 122) Or _
           (iChar >= 48 And iChar <= 57) Or iChar = 45 Or iChar = 46 Or _
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

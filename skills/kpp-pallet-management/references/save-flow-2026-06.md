# PBM110MW 저장 흐름 (실측 2026-06-02)

페이지 HTML을 직접 분석해서 알아낸 저장 메커니즘. 스킬 본문의 `fn_new()`이 더 이상 정확하지 않음.

## 1. fn_saveCheck (저장 전 가공)

페이지 line 1127~1146:

```javascript
const fn_saveCheck = (data, row) => {
    const now = gfn_today();
    if (data.CAR_OWN_TYP == "01" && data.REQ_TYP == "02") {
        if (data.UNLOAD_REQ_DAT.replace(/-/g, '') == now) {
            gfn_alert("당일 요청건의 경우 추가 운반비가 발생됩니다. KPP영업담당자와 추후 확인하시기 바랍니다.");
        }
    }

    data["DTL_ADDR"] = data.ZIP_NUM;                // ZIP_NUM → DTL_ADDR
    data["REQ_CST_COD"] = data.ARV_CST_COD;         // ARV_CST_COD → REQ_CST_COD
    data["UNLOAD_REQ_DAT_CHK"] = data.UNLOAD_REQ_DAT;  // 검증용 별도 보관

    if (data.CAR_OWN_TYP == "02") {
        isUserReqPopup = true;
    }

    return true;
};
```

**의미**: 클라이언트가 `ZIP_NUM`만 보내면 서버는 `DTL_ADDR`로 자동 매핑. `REQ_CST_COD`도 `ARV_CST_COD`에서 자동 세팅.

## 2. fn_save (저장 트리거)

페이지 line 1148~1177:

```javascript
const fn_save = () => {
    const saveData = gfn_getSaveData(sheet, options, fn_saveCheck, true);
    if (saveData == null || saveData.length == 0) {
        return;
    }
    if (!gfn_confirm("선택된 데이터를 저장 하시겠습니까?")) { return; }

    gfn_ajax({
        'type': 'POST',
        'url': '/ps/PBM110MW.do',
        'contentType': 'application/json',
        'dataType': 'json',
        'data': JSON.stringify(saveData),
        'success': function (data) {
            if (data.flag) {
                gfn_alert("저장되었습니다.");
                if (isUserReqPopup) {
                    fn_openUserReqPopup();
                    isUserReqPopup = false;
                }
                fn_search();
            } else {
                gfn_alert(data.message);
            }
        },
        'error': function (a, b, c) {
            gfn_alert(a + b + c);
        }
    });
};
```

**중요**:
- `saveData`는 **체크된 행만** (`gfn_getSaveData`)
- `JSON.stringify` 후 `Content-Type: application/json` POST
- 성공: `data.flag === true` (boolean) → `"저장되었습니다."`
- 실패: `data.flag === false` + `data.message` (한글 오류)

## 3. TANG_BTN (행추가 = fn_new 대체)

페이지 line 1345~1395 (SpreadJS ButtonClicked 이벤트):

```javascript
spread.bind(GC.Spread.Sheets.Events.ButtonClicked, (sender, args) => {
    let colCode = gfn_getColumnCode(options.columns, args.col);
    let rowData = gfn_getRowData(sheet, options, args.row);

    switch (colCode) {
        case "TANG_BTN": // 행추가
            if (rowData.MOD != "I") return;
            const data = {
                "CHK": true
              , "MOD": "I"
              , "REQ_DAT": rowData.REQ_DAT
              , "REQ_TYP": rowData.REQ_TYP
              , "UNLOAD_REQ_DAT": rowData.UNLOAD_REQ_DAT
              , "UNLOAD_REQ_TIM": rowData.UNLOAD_REQ_TIM
              , "PRD_COD": rowData.PRD_COD
              , "CAR_OWN_TYP": rowData.CAR_OWN_TYP
              , "CAR_WGT_TYP": rowData.CAR_WGT_TYP
              , "CAR_QTY": rowData.CAR_QTY
              , "REQ_QTY": rowData.REQ_QTY
              , "REQ_EMP_NAM": rowData.REQ_EMP_NAM
              , "REQ_DPT_NAM": rowData.REQ_DPT_NAM
              , "ARV_CST_COD": rowData.ARV_CST_COD
              , "ARV_CST_NAM": rowData.ARV_CST_NAM
              , "ZIP1_NUM": rowData.ZIP1_NUM
              , "ZIP2_NUM": rowData.ZIP2_NUM
              , "ZIP_SEQ": rowData.ZIP_SEQ
              , "ZIP_NUM": rowData.ZIP_NUM
              , "REQ_ARV_ZIP_ADDR": rowData.REQ_ARV_ZIP_ADDR
              , "RTN_DEP_CST_COD": rowData.RTN_DEP_CST_COD
              , "RTN_DEP_CST_NAM": rowData.RTN_DEP_CST_NAM
              , "RTN_ZIP1_NUM": rowData.RTN_ZIP1_NUM
              , "RTN_ZIP2_NUM": rowData.RTN_ZIP2_NUM
              , "RTN_ZIP_SEQ": rowData.RTN_ZIP_SEQ
              , "RTN_ZIP_NUM": rowData.RTN_ZIP_NUM
              , "RTN_ZIP_ADDR": rowData.RTN_ZIP_ADDR
              , "ETC_DESC": rowData.ETC_DESC
              , "ETC_DESC_COD": rowData.ETC_DESC_COD
              , "ETC_DESC_COD_ADD": rowData.ETC_DESC_COD_ADD
              , "ALC_STATUS": rowData.ALC_STATUS
              , "ALC_REQ_FLG": rowData.ALC_REQ_FLG
            };

            const row = args.row + 1;
            sheet.addRows(row, 1);
            sheet.suspendPaint();
            for(i = 0; i < aoColumns.length; i++) {
                sheet.setValue(row, i, data[aoColumns[i].code]);
            }
            sheet.showCell(row, 0, ...);
            sheet.resumePaint();
            break;
        case "ETC_DESC_BTN": // 비고 팝업
            ...
    }
});
```

**결론**: `TANG_BTN` 클릭 = `fn_new` + 행추가를 한 번에. **신규 행 페이로드는 위 30+ 컬럼 모두**.

## 4. fn_prevReqCallback (이전요청 = 신규 등록 기본값)

페이지 line 1309~1340:

```javascript
function fn_prevReqCallback(datas) {
    gfn_closeDialog(prevReqPopup);
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);

    const nowDate = gfn_today();
    const tomorrowDate = tomorrow.getFullYear() + gfn_lpad(tomorrow.getMonth()+1,'0',2) + gfn_lpad(tomorrow.getDate(),'0',2);

    let row;
    spread.suspendPaint();
    for(let i = 0; i < datas.length; i++) {
        let data = datas[i];
        data["CHK"] = true;
        data["MOD"] = "I";
        data["UNLOAD_REQ_DAT"] = tomorrowDate;  // ← 기본은 내일
        data["UNLOAD_REQ_TIM"] = "0000";         // ← HHMM 기본값
        data["REQ_DAT"] = nowDate;

        row = sheet.getRowCount();
        sheet.addRows(row, 1);
        ...
    }
}
```

**신규 시 필수**:
- `UNLOAD_REQ_TIM = "0000"` (HHMM)
- `UNLOAD_REQ_DAT = YYYYMMDD` (사용자 지정 가능, 기본은 내일)
- `REQ_DAT = YYYYMMDD` (보통 오늘)
- `MOD = "I"`

## 5. 페이지에 정의되지 않은 함수들 (스킬에 있다고 했지만)

- `fn_new()` — ❌ 페이지에 없음 (TANG_BTN이 대체)
- `fn_login()` — ❌ /login 페이지에 정의 (PBM110MW와 무관)
- `getmaxreqqty` API는 호출은 가능하지만 응답 형식 검증 필요

## 6. PBM110MW.do POST 응답 형식 (실측)

```json
// 성공
{"flag": true, "message": "저장되었습니다."}

// 실패 (PRD_COD 누락)
{"flag": false, "message": "[유형] 필수사항입니다.!"}

// 실패 (고객사 매핑 안 됨)
{"flag": false, "message": "배차요청 저장중 오류가 발생하였습니다."}

// 실패 (DB 제약)
{"flag": false, "message": "ORA-01400: NULL을 (\"NPPS_USER\".\"TB_SEQ\".\"KEY_VAL\") 안에 삽입할 수 없습니다"}
```

## 7. 부수 API 응답 패턴 (실측)

- `GET /PBM110MW.do?REQ_DAT_FR=YYYYMMDD&REQ_DAT_TO=YYYYMMDD&STC_CST_COD=217273&REQ_CST_COD=217273`
  - 응답: `[ {...}, {...} ]` (JSON 배열) — 오늘 0건이면 `[]`
- `GET /PBM110MW.depzip?REQ_CST_COD=217273`
  - 응답: `{ "ZIP1_NUM": "482", "ZIP_NUM": "경기 양주시 삼숭동", "ZIP_SEQ": "...", "REQ_ARV_ZIP_ADDR": "582-2" }`
- `GET /PBM110MW.cstarv?CST_COD=217273`
  - 응답: 고객사 도착지 목록 (배열)
- `GET /PBM110MW.trnqry?PRD_COD=A&CAR_WGT_TYP=11`
  - 응답: `{ "MAX_QTY": 9999999, "REQ_QTY": 16, ... }`

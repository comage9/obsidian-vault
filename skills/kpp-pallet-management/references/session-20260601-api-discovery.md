# 2026-06-01 세션: PBM110MW API 발견 및 호출 패턴

## 배경

사용자가 "오늘자 LS 등록된 차량 정보 확인해서 kpp 팔레트 등록" 요청.
KPP 팔레트 등록(PBM110MW)을 API로 직접 호출하는 방법을 역분석.

## 발견한 API 엔드포인트

| 엔드포인트 | 메서드 | 용도 |
|-----------|-------|------|
| `/ps/PBM110MW` | GET | 페이지 HTML 로드 (94KB, SpreadJS SPA) |
| `/ps/PBM110MW.do` | GET | 데이터 조회 (fn_search 호출) |
| `/ps/PBM110MW.do` | POST | 데이터 저장 (fn_save 호출) |
| `/ps/PBM110MW.depzip` | GET | 기본 배송지 정보 (REQ_CST_COD) |
| `/ps/PBM110MW.cstarv` | GET | 고객사 도착지 정보 (CST_COD) |
| `/ps/PBM110MW.trnqry` | GET | 유형×톤수별 수량 계산 |
| `/ps/PBM110MW.getmaxreqqty` | GET | 유형별 최대수량 |

## fn_save 함수 (HTML 스크립트 1147번 라인)

```javascript
const fn_save = () => { // 저장
    const saveData = gfn_getSaveData(sheet, options, fn_saveCheck, true);
    if (saveData == null || saveData.length == 0) { return; }
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
                if (isUserReqPopup) { fn_openUserReqPopup(); isUserReqPopup = false; }
                fn_search();
            } else {
                gfn_alert(data.message);
            }
        },
        'error': function (a, b, c) { gfn_alert(a + b + c); }
    });
}
```

## fn_new 템플릿 (HTML 1046번 라인)

신규등록 시 생성되는 기본 데이터:

```javascript
let data = {
    "CHK": true,
    "MOD": "I",
    "REQ_TYP": "01",
    "CAR_OWN_TYP": "01",
    "CAR_WGT_TYP": "07",
    "ZIP_NUM": REQ_ADDR,          // depzip result
    "ZIP1_NUM": REQ_ZIP1_NUM,     // "482"
    "ZIP2_NUM": REQ_ZIP2_NUM,     // "110"
    "ZIP_SEQ": REQ_ZIP_SEQ,       // 1
    "REQ_ARV_ZIP_ADDR": REQ_ADDR_DTL,  // "582-2"
    "PRD_COD": WPPS_PRD_COD,      // 고객사별 lookup 필요!
    "ARV_CST_COD": newCstCod,     // 선택한 고객사 코드
    "ARV_CST_NAM": newCstNam
};
```

## depzip 조회 결과 (고객사 217273)

```json
[{"ZIP1_NUM":"482","ZIP2_NUM":"110","ZIP_SEQ":1,
  "DTL_ADDR":"경기 양주시 삼숭동","REQ_ARV_ZIP_ADDR":"582-2",
  "RTN_DEP_CST_COD":"101832","RTN_DEP_CST_NAM":"포천물류센터"}]
```

## cstarv 조회 결과 (고객사 217273)

```json
[{"CST_COD":"217273","CST_NAM":"유원피에스","ZIP1_NUM":"482",
  "ZIP2_NUM":"110","ZIP_SEQ":1,"ADDR":"경기 양주시 삼숭동",
  "ADDR_DTL":"582-2","ARV_CST_NAM":"유원피에스"}]
```

## fn_saveCheck 검증 함수

```javascript
const fn_saveCheck = (data,row) => {
    if (gfn_nvl(data.UNLOAD_REQ_DAT, '') == '') {
        gfn_alert("[요청일자] 입력해주십시오.");
        return false;
    }
};
```

## 저장 오류 메시지 분석

| 오류 메시지 | HTTP 코드 | 원인 |
|------------|:---------:|------|
| `[유형] 필수사항입니다.!` | 200 | PRD_COD 누락 |
| `[요청일자] 입력해주십시오.` | - | UNLOAD_REQ_DAT 누락 (fn_saveCheck) |
| `배차요청 저장중 오류가 발생하였습니다.` | 200 | PRD_COD가 고객사 매핑 안 됨 |
| `ORA-01400: NULL을 KEY_VAL에 삽입 불가` | 200 | ARV_CST_COD 누락 |

## PRD_COD(유형) 문제

PRD_COD는 고객사(ARV_CST_COD)별로 다른 값을 가짐.
`TB_CST_PRD_NEW` 팝업으로 조회하며, 필터조건: ETC3 = ARV_CST_COD.
`fn_ajaxCallbackReqCst`에서 customer lookup 시 `data.WPPS_PRD_COD`를 설정.
cstarv 응답에는 WPPS_PRD_COD가 없어서 별도 customer lookup API 필요.

## gfn_getSaveData (spreadUtils.js)

```javascript
let gfn_getSaveData = (sheet, options, saveCheckFunction, noDataFlg = false) => {
    let saveData = [];
    let rowCount = sheet.getRowCount();
    let chkColIdx = gfn_getColumnIndex(options.columns, options.selectColumnCode);
    if (chkColIdx != -1) {
        for (let i = 0; i < rowCount; i++) {
            if (sheet.getCell(i, chkColIdx).value()) {
                let tmp = {};
                options.columns.forEach(col => {
                    let colIdx = gfn_getColumnIndex(options.columns, col.code);
                    tmp[col.code] = sheet.getValue(i, colIdx);
                });
                if (saveCheckFunction && saveCheckFunction(tmp, i) === false) {
                    return [];
                }
                saveData.push(tmp);
            }
        }
    }
    return saveData;
}
```

aoColumns에는 40개 컬럼이 정의되어 있으며, CHK 체크된 행만 저장 대상.

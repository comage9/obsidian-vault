# PBM110MW SpreadJS Save/Query 상세

## 공통

- 베이스 URL: `https://wpps.logisall.com`
- 로그인: JSON POST → `/login.do` (ID=PW=P217273)
- 세션 유지: Python `requests.Session()` 사용
- 필수 헤더: `Content-Type: application/json`, `X-Requested-With: XMLHttpRequest`

## 신규등록 (fn_new)

`fn_new()` → sheet.addRows + 기본값 세팅

### 기본 템플릿

```javascript
let data = {
    "CHK": true,
    "MOD": "I",
    "REQ_TYP": "01",
    "CAR_OWN_TYP": "01",
    "CAR_WGT_TYP": "07",
    "ZIP_NUM": REQ_ADDR,
    "ZIP1_NUM": REQ_ZIP1_NUM,
    "ZIP2_NUM": REQ_ZIP2_NUM,
    "ZIP_SEQ": REQ_ZIP_SEQ,
    "REQ_ARV_ZIP_ADDR": REQ_ADDR_DTL,
    "PRD_COD": WPPS_PRD_COD,
    "ARV_CST_COD": newCstCod,
    "ARV_CST_NAM": newCstNam
}
```

- `REQ_ADDR`, `REQ_ZIP1_NUM` 등은 `fn_dataDepZipRtn(CST_COD)` 호출 시 depzip API로 세팅
- `WPPS_PRD_COD`는 고객사 팝업 callback(`fn_ajaxCallbackReqCst`)에서 data.WPPS_PRD_COD 받아옴

## 저장 (fn_save)

```javascript
gfn_ajax({
    type: 'POST',
    url: '/ps/PBM110MW.do',
    contentType: 'application/json',
    data: JSON.stringify(saveData),  // 체크된 행 배열
    success: function(data) {
        if (data.flag) { /* 저장됨 → fn_search() 갱신 */ }
        else { /* data.message 표시 */ }
    }
})
```

### 응답 형식

- 성공: `{"message":"저장되었습니다.","flag":true,"map":null,"list":null}`
- 검증 실패: `{"message":"[유형] 필수사항입니다.!","flag":false,...}`
- 서버 오류: `{"message":"배차요청 저장중 오류가 발생하였습니다.","flag":false,...}`
- DB 오류: `{"message":"ORA-01400: NULL을 (\"NPPS_USER\".\"TB_SEQ\".\"KEY_VAL\") 안에 삽입할 수 없습니다","flag":false,...}`

## 조회 (fn_search)

```javascript
gfn_ajax({
    type: 'GET',
    url: '/ps/PBM110MW.do',
    data: { REQ_DAT_FR, REQ_DAT_TO, STC_CST_COD, REQ_CST_COD },
    dataType: 'json',
    success: function(data) {
        gfn_setDataSource(sheet, data, options);  // SpreadJS grid 바인딩
    }
})
```

## depzip — 기본 배송지 정보

**호출:** `GET /ps/PBM110MW.depzip?REQ_CST_COD=217273`

**응답 예시:**
```json
[{
  "ZIP1_NUM": "482",
  "ZIP2_NUM": "110",
  "ZIP_SEQ": 1,
  "DTL_ADDR": "경기 양주시 삼숭동",
  "REQ_ARV_ZIP_ADDR": "582-2",
  "RTN_DEP_CST_COD": "101832",       // 포천물류센터
  "RTN_DEP_CST_NAM": "포천물류센터"
}]
```
- 결과가 1개 초과이면 ZIP 필드는 초기화 (여러 도착지 중 선택 필요)
- 결과가 1개이면 ZIP + 도착지가 자동 세팅됨

## cstarv — 고객사 도착지 정보

**호출:** `GET /ps/PBM110MW.cstarv?CST_COD=217273`

**응답 예시:**
```json
[{
  "CST_COD": "217273",
  "CST_NAM": "유원피에스",
  "ZIP1_NUM": "482",
  "ZIP2_NUM": "110",
  "ZIP_SEQ": 1,
  "ADDR": "경기 양주시 삼숭동",
  "ADDR_DTL": "582-2",
  "ARV_CST_NAM": "유원피에스"
}]
```

## trnqry — 유형×톤수별 수량 조회

**호출:** `GET /ps/PBM110MW.trnqry?PRD_COD=A&CAR_WGT_TYP=11`

**응답:** `{}` (빈 객체 = 매칭 없음) 또는 `{"REQ_QTY": 16}`

## getmaxreqqty — 유형별 최대요청수량

**호출:** `GET /ps/PBM110MW.getmaxreqqty?PRD_COD=A`

**응답:** `{"MAX_QTY": 9999999}` (무제한)

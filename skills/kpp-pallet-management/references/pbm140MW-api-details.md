# PBM140MW (출하통보등록) — 완전 가이드

**생성일:** 2026-06-03
**대상:** PBM110MW와 자주 혼동되는 PBM140MW. **"2호차까지 했다" 같은 사용자 호칭 = PBM140MW 의미**.

---

## 0. PBM110MW vs PBM140MW

| 메뉴 | URL | 용도 |
|:---|:---|:---|
| **PBM110MW** | /ps/PBM110MW | **납품/반납요청** (스킬 본문) |
| **PBM140MW** | /ps/PBM140MW | **출하통보등록** (실제 운영) |

**6/1~6/2 사용자 "1호차/2호차 등록" = PBM140MW**. 사용자 호칭 "출하통보", "PBM140" = PBM140MW.

---

## 1. 로그인 (PBM110MW와 동일)

```python
import requests, json
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0",
    "X-Requested-With": "XMLHttpRequest",
})
session.get("https://wpps.logisall.com/login", timeout=15)
session.headers["Content-Type"] = "application/json"
session.post("https://wpps.logisall.com/login.do",
              data=json.dumps({"loginId":"P217273","password":"P217273"}),
              timeout=15)
session.headers.pop("Content-Type", None)
session.get("https://wpps.logisall.com/ps/PBM140MW", timeout=15)  # 230KB
```

---

## 2. PBM140MW API 엔드포인트

| 엔드포인트 | 메서드 | 용도 |
|:---|:---:|:---|
| /ps/PBM140MW | GET | 페이지 HTML (230KB) |
| /ps/PBM140MW.search | **POST** | 데이터 조회 (GET 아님!) |
| /ps/PBM140MW.save | POST | 신규/수정 저장 |
| /ps/PBM140MW.delete | POST | 삭제 |
| /ps/PBM140MW.chitnum | POST | 전표번호 팝업 |
| /ps/PBM140MW.print | POST | EDI 출력 |

---

## 3. UI 입력 필드 (24개, `sr_*`)

| ID | 라벨 | 필수 |
|:---|:---|:---:|
| sr_dlv_dat_f | 출하일자(FR) | ✅ |
| sr_dlv_dat_t | 출하일자(TO) | ✅ |
| sr_dlv_cst_cod | 상차지 | ✅ |
| sr_arv_cst_cod | 도착지 | ✅(신규) |
| sr_new_row | 신규 행 수 | ✅(신규) |
| sr_dlv_cst_nam, sr_arv_cst_nam | 명칭 | |
| sr_cst_cod, sr_ord_cst_cod/nam | 고객사/발주처 | |
| sr_prd_cod/nam | 유형 | |
| sr_dlv_cst_typ, sr_ucps_flg, sr_usr_cst_flg/tel | 옵션 | |
| sr_new_bro_flg, sr_spc_dlv_flg, sr_spc_arv_flg | 특수 | |
| sr_chit_flg, sr_dual_confm, sr_mng_grd | 옵션 | |
| sr_arv_addr_flg, sr_cst_chit_num, sr_delete_flg | 옵션 | |

---

## 4. SpreadJS 컬럼 (소문자, 30+개)

| 컬럼 | 의미 | 비고 |
|:---|:---|:---|
| chk | 체크박스 | |
| mod | 상태 | "I"=신규, "U"=수정 |
| data_typ | 데이터유형 | 01, 02 |
| dual_confm | 이중확인 | A=승인, S=미확인 |
| dlv_cst_cod | 상차지 | **217273** |
| dlv_cst_nam | 상차지명 | "유원피에스" |
| dlv_cst_typ | 상차지 유형 | 04 |
| dlv_dat | 출하일자 | YYYYMMDD |
| arv_dat | 도착일자 | YYYYMMDD |
| arv_cst_cod | 도착지 | **610060** |
| arv_cst_nam | 도착지명 | "쿠팡-부천1센터[HUB]" |
| arv_cst_typ | 도착지 유형 | 05 |
| usr_cst_cod | USER운송 | 9999999999999 |
| prd_cod | 유형 | **N11** (11T) |
| dlv_qty | 수량 | 12, 14, 18 |
| ord_cst_cod | 발주처 | 610060 |
| chit_num | 전표번호 | (저장 후) |
| cst_chit_num | 고객 전표번호 | |
| car_num | 차량번호 | |
| driver_nam | 기사 | |
| driver_tel | 연락처 | |
| web_desc | 비고 | "1호차", "2호차" 등 |
| data_typ_nam, dual_confm_nam, reg_dat | 표시용 | 자동 |
| mod_emp, mod_dat | 수정정보 | P217273 |
| mov_seq, dlv_seq | SEQ | |
| kpp_confm_flg | KPP확인 | N/Y |
| web_mov_typ | WEB이동 | 01 |
| err_typ | 오류유형 | 01, 09 |
| car_own_typ | 차량소유 | **02**=USER운송 |
| comp_cod | 회사 | **01** |
| cst_cod | 고객 | **217273** |
| user_id | 사용자 | 'P217273' (fn_save 자동) |
| arv_info | 도착지 풀정보 | |

---

## 5. fn_newRow() 신규 템플릿 (line 1285~1309)

```json
{
  "dlv_cst_nam": "<param.sr_dlv_cst_nam>",
  "dlv_qty": "0",
  "chit_num_cnt": "0",
  "file_cnt": "0",
  "user_id": "P217273",
  "mod": "I",
  "data_typ": "01",
  "dual_confm": "",
  "dlv_cst_typ": "<sr_dlv_cst_typ>",
  "oth_biz_reg_flg": "N",
  "web_mov_typ": "01",
  "err_typ": "01",
  "car_own_typ": "02",
  "kpp_confm_flg": "N",
  "mod_qty": "0",
  "mod_emp": "P217273",
  "cst_cod": "<param.sr_dlv_cst_cod>",
  "prd_cod": "<pre_prd_cod>",
  "comp_cod": "<pre_comp_cod>"
}
```

---

## 6. PBM140MW.save 호출 (line 4753~4822)

```javascript
gfn_ajax({
    'type': 'POST',
    'url': "/ps/PBM140MW.save",  // .do 아님!
    'contentType': 'application/json',
    'dataType': 'json',
    'data': JSON.stringify(data),  // 체크된 행들
    'success': function(data){
        if(data.flag){
            gfn_alert('저장되었습니다.');
            fn_search();
        } else {
            gfn_alert(data.message);
        }
    }
});
```

**fn_saveDataChk 자동 처리**:
- `user_id='P217273'` 자동 추가
- `dlv_dat`/`arv_dat` → checkDateToString() 형식 변환
- null → "" (모든 필드)

---

## 7. PBM140MW.search (POST) — READ ONLY

```python
session.headers["Content-Type"] = "application/json"
r = session.post("https://wpps.logisall.com/ps/PBM140MW.search",
                  data=json.dumps({
                      "sr_dlv_dat_f": "20260601",
                      "sr_dlv_dat_t": "20260603",
                      "sr_dlv_cst_cod": "217273",
                      "sr_arv_cst_cod": "",
                      "sr_ucps_flg": "N",
                      "sr_web_mov_typ_02": "N",
                      "chk_excludingKCP": "N",
                      "sr_usr_cst_flg": "N",
                      "sr_usr_cst_tel_flg": "N",
                      "sr_new_bro_flg": "N",
                      "sr_spc_dlv_flg": "N",
                      "sr_spc_arv_flg": "N",
                      "sr_chit_flg": "N",
                      "sr_dual_confm": "",
                      "sr_mng_grd": "",
                      "sr_arv_addr_flg": "N",
                      "sr_prd_cod": "",
                      "sr_prd_nam": ""
                  }),
                  timeout=15)
data = r.json()  # list of dict
```

---

## 8. 3호차 등록 페이로드 (확정 예시, 11T 14팔레트 6/1자)

```json
{
  "chk": true, "mod": "I", "user_id": "P217273",
  "data_typ": "02", "web_mov_typ": "01", "err_typ": "01",
  "car_own_typ": "02", "kpp_confm_flg": "N", "oth_biz_reg_flg": "N",
  "cst_cod": "217273",
  "dlv_cst_cod": "217273", "dlv_cst_nam": "유원피에스", "dlv_cst_typ": "04",
  "dlv_dat": "20260601", "arv_dat": "20260601",
  "arv_cst_cod": "610060", "arv_cst_nam": "쿠팡-부천1센터[HUB]", "arv_cst_typ": "05",
  "ord_cst_cod": "610060", "ord_cst_nam": "쿠팡-부천1센터[HUB]",
  "prd_cod": "N11", "dlv_qty": 14, "web_desc": "3호차",
  "mod_qty": "0", "mod_emp": "P217273", "comp_cod": "01",
  "chit_num_cnt": "0", "file_cnt": "0", "dual_confm": ""
}
```

**운영 메모**: `dlv_dat=20260601` 이지만 차량이 6/2 23:50 출발해도 "당일 등록 누락 보충" 패턴으로 정상 처리 (6/1 1호차/2호차 동일).

---

## 9. 운영 데이터 패턴 (6/1~6/2, 7건)

- **PRD_COD=N11** (7/7 일관)
- **CST_COD=DLV_CST_COD=217273** (유원피에스)
- **CAR_OWN_TYP=02** (USER운송)
- **DLV_CST_TYP=04, ARV_CST_TYP=05, COMP_COD=01**
- 도착지: 605177 (안성5센터) 또는 610060 (부천1HUB)
- **DUAL_CONFM=S** (미확인) → KPP 검수 후 A로 변경
- **KPP_CONFM_FLG=N** (KPP 검수 전)
- **CAR_WGT_TYP 필드 없음** (PRD_COD가 톤수 통합)
- 6/1자 5건 (1호차/2호차/기타), 6/2자 3건 (1호차/2호차/기타)

---

## 10. PBM110MW와의 핵심 차이점 정리

| | PBM110MW | PBM140MW |
|:---|:---|:---|
| URL | /ps/PBM110MW | /ps/PBM140MW |
| 페이지 크기 | 94KB | 230KB |
| 조회 API | GET /ps/PBM110MW.do | **POST** /ps/PBM140MW.search |
| 저장 API | POST /ps/PBM110MW.do | **POST /ps/PBM140MW.save** |
| 필드명 | 대문자 (CHK, MOD, UNLOAD_REQ_DAT) | **소문자** (chk, mod, dlv_dat) |
| PRD_COD 사용 | 직접 (PBM110MW) | **N11** (11T) |
| ZIP_* 처리 | depzip(REQ_CST_COD) | cstarv(CST_COD) |
| fn_newRow | 없음 (TANG_BTN) | 있음 |
| save 자동 처리 | fn_saveCheck (DTL_ADDR, REQ_CST_COD) | user_id 자동, 날짜 형식 변환 |
| 라인 수 (응답) | 페이지당 ~5건 | 페이지당 ~8건 |
| 출하일자 필드명 | UNLOAD_REQ_DAT | **dlv_dat / arv_dat** (출하/도착 분리) |

---

## 참고
- 원본 페이지: https://wpps.logisall.com/ps/PBM140MW (인증 필요)
- PBM110MW 가이드: 본 스킬 SKILL.md
- 로그인 트러블슈팅: references/login-troubleshooting-2026-06.md
- 6/3 검증 보고서: /opt/hermes/docs/kpp-pbm140mw-complete-guide-2026-06-03.md

# KPP 검증 시 흔한 함정 (2026-06-03 발견 + 2026-06-03 업데이트)

## 🚨 PBM140MW 데이터 "0건"의 의미 — 항상 의심 먼저

상황: 이전 보고서에서 "6/2 1호/2호차 등록 완료"라고 했는데, 같은 조건으로 재조회 시 **0건**.

**가능한 원인 4가지** (정직하게 사용자에게 보고):

| # | 원인 | 검증 방법 |
|---|------|----------|
| 1 | 다른 사용자/에이전트가 데이터 삭제 | 다른 시점/계정/날짜 범위로 교차 조회 |
| 2 | 자정 자동 만료 (KPP 시스템 정책) | 어제/오늘 범위 모두 0건이면 의심 |
| 3 | 계정 권한 차이 (P217273 vs 다른) | 같은 세션에서 다른 메뉴로 재확인 |
| 4 | 이전 보고서가 잘못된 데이터 | 로그/스크립트 재실행으로 원본 확인 |

**반드시 할 일**:
- 5가지 이상 조회 조건 시도 (DLV_DAT, ARV_DAT, DFR-DTO, 빈값, 다른 날짜)
- 모두 0건이면 사용자에게 **정직하게 보고** + 4가지 가능성 제시
- **임의로 "아 없네" 하고 새로 등록하지 말 것** — 다른 사용자 작업물일 수 있음

## 🚨 PBM140MW.search 응답 타입은 list 또는 dict

```python
r = s.post(f"{BASE}/ps/PBM140MW.search", json=payload)
raw = r.json()
# raw는 환경에 따라 list 또는 dict
# - list: rows 자체가 배열
# - dict: {"rows":[...]} 또는 {"data":[...]} 또는 {"total":N,"rows":[...]}
if isinstance(raw, list):
    rows = raw
elif isinstance(raw, dict):
    rows = raw.get('rows', raw.get('data', []))
else:
    rows = []
```

**반드시 isinstance 체크** — PBM110MW.do 응답이 list라 PBM140MW도 list라고 가정하면 dict일 때 AttributeError.

## 🚨 loginType 필드 빠뜨리지 말 것

실제 HTML form은 3필드:
```html
<input name="loginType" value="">   ← JS가 'IDPW' 자동 세팅
<input name="loginId" value="">
<input name="password" value="">
```

`loginId+password` 2필드만 보내도 flg=Y 응답은 옴 (서버宽容). 하지만:
- `loginType` 빠지면 일부 환경에서 세션 권한 다를 수 있음
- **3필드 모두 명시**가 안전 (`loginType="IDPW"`)

## 🚨 PRD_COD = N11 = 11T 파렛트 종류 (🚨 차량톤수 아님)

사용자가 직접 정정한 핵심 사실:
- `prd_cod="N11"` = **11T 파렛트 종류** (팔레트 단위)
- **차량 톤수(5T/11T)와 무관** — 5T 차량도 N11
- 6/1~6/2 운영 7건 일관 (1호차 5T도 N11, 2호차 5T도 N11, 3호차 11T도 N11)
- 다른 톤수 코드(07, 14 등) 사용 사례 보고 없음

이전 오해: "N11 = 11T 차량" → ❌ **틀림**.

## 🚨 KPP login 시 credentials 마스킹 확인

세션 스크립트 작성 시:
- 메모리: P217273 / P217273 (ID와 PW 동일)
- 스크립트에서 `[REDACTED]` 자리 마스킹 빠뜨리지 말 것
- 마스킹된 채로 실행하면 "flg=N" 응답 → 의미 없는 디버그 30분 소비

## 🚨 PBM110MW 고객사 파라미터: `cst_cod` (소문자)만 accept (2026-06-03 신규)

상황: PBM110MW.do 조회 시 STC_CST_COD/REQ_CST_COD(대문자)로 호출 → 0건 응답. 서버는 HTTP 200 + Content-Type: application/json 정상. **침묵 실패**.

**재현 (2026-06-03 실측)**:
```bash
# ❌ 0건 응답 (HTTP 200)
curl 'https://wpps.logisall.com/ps/PBM110MW.do?REQ_DAT_FR=20260601&REQ_DAT_TO=20260630&STC_CST_COD=217273&REQ_CST_COD=217273'
# → []

# ✅ 2,592건 정상
curl 'https://wpps.logisall.com/ps/PBM110MW.do?REQ_DAT_FR=20260601&REQ_DAT_TO=20260630&cst_cod=217273'
# → [2,592 rows]
```

**원인**:
- WPPS 백엔드가 `cst_cod` (소문자)만 실제 SQL WHERE 절에 사용
- `STC_CST_COD`/`REQ_CST_COD`는 다른 컨텍스트(레거시 VF 시스템 또는 화면 폼 전송)용
- 대문자 파라미터는 무시되고, 다른 WHERE 조건 없어서 빈 결과
- HTTP 200 + 빈 배열로 **침묵 실패** — 에러 메시지 없음

**스킬 본문(`SKILL.md`) 표기 정정**:
- 기존: `STC_CST_COD=217273, REQ_CST_COD=217273`
- 정정: `cst_cod=217273` (소문자)
- 위임 지시서 `/opt/hermes/plans/kpp-2026-06-unload-check.md` 4번 항목에 이미 정정 반영됨

**다른 WPPS 페이지도 같은 패턴 의심**:
- PBM140MW (출하통보) 검색 옵션도 대문자 사용 시 침묵 실패 가능
- KPP 작업 시 **반드시 소문자** 파라미터 사용
- 0건 응답 시 → 소문자로 재시도 → 정상 응답 시 = 대소문자 함정 확정

## 🚨 PBM110MW 페이지는 요청일자(REQ_DAT)만 조회 필드, 하차요청일자(UNLOAD_REQ_DAT)는 그리드 컬럼만 (2026-06-03 신규)

상황: 사용자가 "하차요청일자 기준"으로 조회 요청했으나, 페이지는 폼 필드 `REQ_DAT_FR/TO` 하나만 노출.

**실측 (fn_search 함수)**:
```javascript
const fn_search = () => {
    const param = gfn_makeJsonParam();   // 폼 필드만 JSON 변환
    gfn_ajax({
        'type': 'GET',
        'url': '/ps/PBM110MW.do',
        'data': param,
        ...
    });
};
```

`UNLOAD_REQ_DAT_FR/TO` 필드 자체가 HTML에 없음 → 폼 전송 안 됨.

**처리**:
- 페이지 자체는 **요청일자 기준 조회만 지원**
- 결과 데이터의 `UNLOAD_REQ_DAT` 컬럼은 그리드 표시용 — 후처리 시 재집계 가능
- 사용자에게 "요청일자 = 하차요청일자 기준이 사실상 같은 결과 (대부분 동일일 등록)" 설명
- 데이터 후처리 시 `UNLOAD_REQ_DAT` 컬럼으로 재집계 가능함을 명시

## 일반화: 침묵 실패(silent failure) 패턴

WPPS 시스템의 일반적 패턴:
- 잘못된 파라미터 → HTTP 200 + 빈 결과 (에러 안 냄)
- 0건 ≠ "데이터 없음", 0건 = "쿼리 매칭 안 됨" (쿼리 자체가 잘못된 것일 수도)

**검증 워크플로우**:
1. 0건 응답 받으면 → 파라미터 대소문자/철자/형식 의심
2. 잘 알려진 동작하는 호출과 비교 (예: 브라우저 개발자 도구에서 실제 form 전송 확인)
3. 스킬/위키/메모리 검색 → 이전 정정 사례 있는지
4. 그래도 안 되면 → 사용자에게 "0건이 정상인지, 함정인지" 확인 후 보고

## 운영 검증 워크플로우 (필수 5단계)

1. **위키/스킬 검색** — 이전에 누가 다뤘는지
2. **사용자 확인** — 실행 전 "진행할까요?" (특히 데이터 변경)
3. **실행** — `POST /ps/PBM140MW.search` 등
4. **검증** — 최소 3가지 조건 교차 조회 + list/dict 타입 체크
5. **보고** — 0건이어도 4가지 가능성 정직 제시, 추측 보고 금지

## 참고: PBM140MW 6/2 0건 사건 타임라인

- 6/2 13:00 이전 보고서: "PBM140MW 6/2 데이터 3건 (1호/2호 등록됨)" — 레퍼런스 §10.2
- 6/2 15:55 재조회: DLV_DAT=20260602 → 0건, DFR-DTO 6/1~6/2 → 0건, ARV_DAT 6/2 → 0건
- 가능성: (a) 다른 사용자 삭제, (b) 어제 자정 만료, (c) 계정 권한 차이, (d) 이전 보고서 오류
- **결론: 정직 보고 후 사용자 결정 대기** (1호/2호/3호 모두 새로 등록 vs 3호차만 등록)

## 참고: PBM110MW 6/1~6/30 2,592건 정상 조회 (2026-06-03)

- 2,592건 응답 확인
- 요청유형: 납품(01) 2,401건 / 반납(02) 191건
- 톤수: 01(1T) 557, 04(4T) 544, 07(5T) 526, 08(8T) 116, 12(12T) 564, 14(14T) 283
- PRD_COD: N11 1,812, N12 419, N48 82 등
- 요청수량 합계: 411,289
- 위임 지시서: `/opt/hermes/plans/kpp-2026-06-unload-check.md`
- 원본 데이터: `/tmp/wpps_pbm110mw_data.json` (2.3MB)

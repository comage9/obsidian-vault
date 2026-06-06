# PBM110MW.save 응답 함정: 200 OK ≠ 저장 성공 (2026-06-03 실측)

## 🚨 핵심 발견

`POST /ps/PBM110MW.save` (또는 `.do` POST)가 **HTTP 200 + `{"flag":true,"message":"저장되었습니다."}`** 를 반환해도,
**실제로 row가 저장되지 않을 수 있음**.

확인 방법 (필수): 저장 직후 **반드시 GET으로 재조회**해서 row가 존재하는지 검증. response status만 보고 "저장 완료" 보고 금지.

## 실측 케이스 (2026-06-03)

PBM110MW.save 응답 예시:
```json
{"flag": true, "message": "저장되었습니다."}
```
→ 클라이언트는 성공으로 간주
→ 그러나 30초 후 PBM110MW.do 조회 시 해당 REQ_DAT/차량번호 row **0건**
→ fn_saveCheck가 silent reject 했거나, validation 5단계 중 후순위 단계에서 drop

## UI vs API 동작 차이

| 항목 | UI (SpreadJS) | API (POST) |
|------|---------------|------------|
| 신규 행 생성 | TANG_BTN 클릭 → 1 row 자동 생성 | 클라이언트가 `MOD:"I"` 명시 |
| Step 진행 | UI가 1·2·3·4·5 단계 자동 수행 | 클라이언트가 모든 필드 명시 + fn_saveCheck가 자동 매핑 |
| 응답 처리 | 화면에 success toast + row 즉시 표시 | `{"flag":true,"msg":...}` JSON |
| **검증** | **사용자가 row를 본다** | **클라이언트가 GET으로 재조회해야 안다** |

UI는 1·2·3·4·5번 5단계 통합이지만, API는 1·2·3·4·5를 모두 한 페이로드로 묶어서 보내야 함. 일부 단계가 빠진 페이로드는 `fn_saveCheck` silent drop 가능.

## 재발 방지 워크플로우 (필수)

```python
# 1. save
r = s.post("https://wpps.logisall.com/ps/PBM110MW.save",
           json=[save_payload], headers={...JSON headers...})
result = r.json()
assert result.get("flag") is True, f"저장 거부: {result}"

# 2. ⚠️ 즉시 GET 재조회 — 없으면 재시도 or 사용자 에스컬레이션
import time; time.sleep(0.5)  # 짧은 propagation 대기
r2 = s.get("https://wpps.logisall.com/ps/PBM110MW.do",
           params={"REQ_DAT_FR": save_payload["REQ_DAT"],
                   "REQ_DAT_TO": save_payload["REQ_DAT"],
                   "cst_cod": "217273"})  # ⚠️ 소문자 필수 (별도 함정)
rows = r2.json()
if isinstance(rows, dict): rows = rows.get("rows", [])

# 3. 우리 row 식별 (차량번호+REQ_DAT+하차요청일자)
found = any(
    r.get("plateNumber" if "plateNumber" in r else "col31") == save_payload.get("plateNumber")
    and r.get("REQ_DAT") == save_payload["REQ_DAT"]
    for r in rows
)
if not found:
    raise RuntimeError(f"PBM110MW.save silent fail: row not found in GET (save returned ok)")
```

## 가능한 silent drop 원인 (체크리스트)

1. **5단계 페이로드 중 일부 누락** — fn_saveCheck가 `필수 필드 누락` silent fail
2. **ZIP1_NUM/ZIP_NUM/REQ_ARV_ZIP_ADDR 불일치** — depzip API 결과와 페이로드 값이 매칭 안 됨
3. **CAR_OWN_TYP=02인데 RTN_* 필드 미포함** (또는 그 반대)
4. **REQ_TYP 불일치** — 서버가 PRD_COD와 호환 안 되는 REQ_TYP을 reject (UI는 자동 보정)
5. **중복 row** — 동일 REQ_DAT+차량번호가 이미 존재 → silent fail 가능
6. **세션 토큰 만료** — 60분 만료 후 save는 200 OK 반환할 수 있으나 실제로는 anonymous 사용자로 저장 시도 → 권한 부족 silent fail

→ 6번 확인: 저장 직전 `s.cookies`에 인증 토큰(`JSESSIONID` 등)이 살아있는지 확인, 60분 경과 시 `fn_login` 재호출 후 save 재시도.

## 토큰 만료 시 재로그인 패턴

```python
# 60분 경과 또는 저장 후 재조회 0건이 반복되면 토큰 갱신
import time
if time.time() - last_login_at > 3300:  # 55분
    r = s.post("https://wpps.logisall.com/login.do",
               json={"loginType":"IDPW","loginId":"P217273","password":"P217273"})
    assert r.json()["flg"] == "Y"
    last_login_at = time.time()
    # ⚠️ loginType 빠뜨리지 말 것 (별도 함정)
```

## PBM140MW도 동일하게 검증

`POST /ps/PBM140MW.save` 도 동일 패턴. 출하통보 등록 후 GET으로 DFR-DTO 조회해서 row 존재 확인 필수.
fn_saveDataChk가 user_id 자동 세팅하지만 일부 환경에서 silent drop 케이스 발견 시 동일하게 재조회.

## 출처

- 2026-06-03 새벽 KPP 디버깅 세션
- PBM110MW.save 5단계 모델 (UI TANG_BTN→fn_saveCheck→server insert) 분석
- 기존 `references/verification-pitfalls-2026-06-03.md`의 "0건의 4가지 의미"를 보완 — 조회 0건이 진짜 0건인지, silent save fail인지 구분하는 게 핵심

# VF2 Production Plan Nightly — 2026-06-08 점검 결과

> 점검 시각: 2026-06-08 (cron)
> Cron ID: `48144ff13cee`
> 점검 대상: production_logs DB 265건 (6개 일자)
> 비교 기준: skill `vf2-production-plan-conventions`, Wiki `VF2-생산계획-엑셀문서-기준.md`

## (a) 점검 대상

| 데이터 | 건수 | 비고 |
|---|---:|------|
| `GET /api/production` 6일치 합계 (2026-05-17/21/24, 06-01/02/07) | **265건** | allDates=6 |
| status=pending | 262 | |
| status=ended | 3 | |
| 등록된 고유 금형 수 | 42종 | 금형 0~9999 + 801, 901 |
| 등장 color1 값 | 41종 | (빈값 1건 포함) |

## (b) 비교 방법

1. `GET /api/production?date=<YYYY-MM-DD>` × 6회 호출 (allDates 6일치) — Bearer 인증 (VF2/backend/.env API_AUTH_TOKEN)
2. 색상코드 정합성: DB color1 분포 vs 스킬 §3 매핑표 비교
3. 금형명 일관성: `(moldNumber, productName)` 다대일 여부 검사
4. upsert 위험: `(date, machineNumber, moldNumber, color1, color2, unitQuantity)` 6-튜플 중복 검사
5. CAP 코드: 금형40(로코스 L) color1의 WHITE1 vs *-CAP(*) 구분
6. 결함 레코드: 빈 moldNumber, 빈 color1/color2, quantity=0

## (c) 검증 결과

### ✓ 양호 (변경 불필요)

| 항목 | 결과 |
|------|------|
| 금형명 일관성 | ✓ 42종 금형 모두 단일 productName 매핑 |
| upsert 중복 (6-튜플) | ✓ 0건 |
| 금형99(옷정리 트레이) | ✓ 6건 모두 color1=WHITE1, status=pending |
| CAP/본체 구분 (금형40) | ✓ WHITE1(6건, 본체) vs *-CAP(*)(10건, 뚜껑) 명확 분리 |
| 금형40 색상 매핑 | ✓ Ivory/Gray1/Butter/Cream/White 등 12종 — 모두 매핑표에 등록된 코드 |

### ⚠️ 신규 발견 (DB 상태는 정상이지만 스킬/위키 보강 필요)

#### (1) 미등록 color1 14종 — 제품군 한정 코드

스킬 §3의 "WHITE 180 계열" 사용 제품군 표 외 추가 코드들이 발견됨. **모두 의도된 제품군 한정 코드이며 데이터 자체는 정상**:

| color1 | 건수 | 사용 제품 | color2 | 비고 |
|---|---:|---|---|---|
| `Simple White` | 3 | 에센셜/슬림/와이드 앞판 | WHITE 180 | 스킬 §3 표에 일부 명시 |
| `Simple Ivory` | 2 | 슬림형 앞판 | IVORY 1060 | |
| `Simple Gray2` | 2 | 슬림/에센셜 앞판 | GRAY 11215-1 | |
| `Simple Butter` | 1 | 에센셜 앞판 | YELLO - 3093 | |
| `Ratan White` | 2 | 라탄/와이드 앞판 | WHITE 180 | 스킬 §3 표에 일부 명시 |
| `Ratan Ivory` | 1 | 라탄 기본형 앞판 | IVORY 1060 | |
| `Ratan Brown` | 1 | 라탄 기본형 앞판 | BROWN 11-573 | |
| `Ratan Butter` | 1 | 슬림형 앞판 | YELLO - 3093 | |
| `Decos Butter` | 1 | 에센셜 앞판 | YELLO - 3093 | |
| `EU BLUE` | 6 | **이유(135)** | BLUE 3847 | 신규 |
| `EU RED` | 3 | **이유(135)** | RED 2259 | 신규 |
| `Pink(P3)` | 2 | 북트롤리(127)/몽드(138) | PINK 6078 | 신규 |
| `MIX 50` | 1 | 어반 옷걸이 신규(111) | WHITE-25+IVORY-25 | 신규 (마스터배치) |
| `WHITE-BLUE2` | 1 | 초대형 바디(12) | WHITE 180 | 신규 (마스터배치) |
| `WHITE-YELLO` | 1 | 초대형 바디(12) | WHITE 180 | 신규 (마스터배치) |
| `WHITE-GREEN` | 1 | 초대형 바디(12) | WHITE 180 | 신규 (마스터배치) |
| `WHITE-PINK2` | 1 | 초대형 바디(12) | WHITE 180 | 신규 (마스터배치) |
| `GRAY1-CAP(GRAY1)` | 1 | 로코스 M(41) | GRAY 9097 | 신규 (CAP 코드) |
| `Cream` | 1 | 로코스 L(40) | (없음) | 스킬 §12에 명시 |
| **(빈값)** | **1** | **로코스 L(40)** | **(없음)** | **결함** (id=19416) |

#### (2) 기계 표기 비일관 — `생산 대기` vs `생산대기`

6건이 '생산대기' 의미로 등록되었지만 표기가 다름. upsert 키 분기 위험:

| id | date | machine | mold | product | color1 |
|---|---|---|---|---|---|
| 18836 | 2026-05-17 | **생산 대기** | 3 | 모던플러스 블랑 | O |
| 18876 | 2026-05-17 | **생산 대기** | 23 | 에센셜 앞판 | Simple Butter |
| 18877 | 2026-05-17 | **생산 대기** | 34 | 슬림형 앞판 | Simple Ivory |
| 18878 | 2026-05-17 | **생산 대기** | 34 | 슬림형 앞판 | Simple Gray2 |
| 18879 | 2026-05-17 | **생산 대기** | 25 | 에센셜 프레임 | WHITE1 |
| 19415 | 2026-05-17 | **생산대기** | 113 | 해피프레임 서랍 | Ivory2 |

→ 5건은 `생산 대기`(띄어쓰기), 1건은 `생산대기`. **같은 의미로 통일 필요** (스킬 §4 "기계9 전체 금형 목록"에서 표기 기준 확인 필요).

#### (3) 결함 레코드 1건 — 빈 moldNumber

```json
{
  "id": "19416",
  "date": "2026-05-24",
  "machineNumber": "M01",
  "moldNumber": "",
  "productName": "로코스 L",
  "color1": "",
  "color2": "",
  "quantity": 100,
  "unitQuantity": 0,
  "total": 0,
  "status": "pending"
}
```

→ productName=로코스 L인데 moldNumber 미기입, machine=M01(미사용 패턴), color1/2=빈값, unitQuantity=0. **장기 미사용 placeholder 가능성**. **사용자 확인 필요**.

#### (4) color2 표기 비일관 — `WHITE 180` vs `White 180`

| color2 | color1 | 건수 |
|---|---|---:|
| `WHITE 180` | WHITE1 | 86 |
| `White 180` | WHITE1 | 10 |
| `WHITE 180` | WHITE-CAP(WHITE) | 4 |
| `White 180` | WHITE-CAP(WHITE) | 1 |

→ 같은 화이트 규격인데 96:11 비율로 혼재. 스킬 §2 예시는 `White 180` (혼합) 이지만 다수가 `WHITE 180` (대문자) 사용. **단일 표기 통일 권장** (영문 코드 WHITE1과 일관성을 위해 `White 180` 권장).

### ③ 권장 조치 (사용자 확인 후)

| # | 조치 | 우선순위 | 영향 |
|:-:|------|:--------:|------|
| 1 | 빈 moldNumber 레코드(id=19416) 처리 (삭제/정정) | 중 | 데이터 정합성 |
| 2 | 기계 표기 `생산 대기` → `생산대기` 일괄 통일 (5건) | 중 | upsert 키 일관성 |
| 3 | color2 `WHITE 180` → `White 180` 일괄 정규화 (86건) | 낮 | 표기 일관성 |
| 4 | 신규 color1 16종을 스킬 §3 매핑표에 추가 (코드값 자체는 정상이므로 보강만) | 낮 | 스킬 정확성 |

## (d) DB 직접 변경 없음 (Read-only 점검)

- API 호출: GET만 사용
- POST/PUT/DELETE: 0건
- 사용자 명령 대기 중

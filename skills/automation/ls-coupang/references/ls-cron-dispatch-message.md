# 13:00 KST VF67 일일 cron — 배차 요청 메시지

## 사용 위치
`scripts/daily-cron-vf67.py`에서 오늘 VF67 오더 조회 후 텔레그램 전송할 메시지를 생성할 때 참조.

## 메시지 형식 (반드시 그대로)

```
안녕하세요. VF67 - {월/일} 배차 요청 드립니다
{순번}. 부천1 HUB {톤수} {시간} {순번}호차
...
상기와 같이 배차 진행 부탁드립니다
```

### 2026-06-03 실측 예시 (3건, 모두 SUBMITTED)
```
안녕하세요. VF67 - 06/03 배차 요청 드립니다
1. 부천1 HUB 11T 20:00 1호차
2. 부천1 HUB 5T 22:00 2호차
3. 부천1 HUB 11T 23:50 3호차
상기와 같이 배차 진행 부탁드립니다
```

## 작성 규칙 (실수 방지)
1. **날짜**: `today.strftime('%m/%d')` — 한 자리/두 자리 모두 그대로 출력 (06/03, 6/3 둘 다 OK이지만 일관성 위해 `%m/%d` 권장)
2. **순번**: `i` (1부터). `truckSeq` (LS 응답의 호차)와 일치하면 더 좋음
3. **호차 표기**: `{순번}호차` (예: "1호차"). "1호" 아님
4. **톤수**: `truckType.name` (5T/11T/14T) 우선, 없으면 `truckType.code` 매핑 (T5000→5T, T11000→11T, T14000→14T)
5. **시간**: `requestTime` 문자열에서 `HH:MM` 추출 (`"2026-06-03 20:00:00"[11:16]`)
6. **시간순 정렬** 필수
7. **CANCELED 제외** (`status != "CANCELED"`만 메시지에 포함)
8. **표/설명/메타데이터 없이 메시지만 단독 출력**

## 분기별 동작
- **A. 등록 안 됨 (0건)** → Batch Create 후 sleep 2 + `/order` GET으로 SUBMITTED 검증 → 메시지 출력
- **B. 이미 등록됨 (N건)** → "LS 등록 완료: N건" 보고 + 메시지 출력

## 텔레그램 전송
- chat_id: `TELEGRAM_HOME_CHANNEL` (= 5708696961, Home chat)
- token: `TELEGRAM_BOT_TOKEN` (env masking → `sed -n 'Np' .env | od -c` 또는 `subprocess.run(['grep',...])`)
- `parse_mode` 기본값(없음) — 한글 안전
- 빈 payload(메시지 비어있음) 체크 후 send

## 함정
- `requestTime`은 `/order` API는 str (`"2026-06-03 20:00:00"`), `/truckOrderTracking`은 int (epoch ms). 메시지용 시간은 **`/order` 응답**에서 추출
- 50건 페이징 안에 다른 날짜가 섞여 있을 수 있음 → `orderDate == 오늘` 필터 후 순번 매길 것
- 1호차 90626 톤수가 일자별로 바뀜 (6/2=5T, 6/3=11T) → 응답 `truckType` 그대로 사용

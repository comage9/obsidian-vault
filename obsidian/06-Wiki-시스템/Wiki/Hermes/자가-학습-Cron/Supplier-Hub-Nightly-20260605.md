# Supplier Hub (supplier.coupang.com) 자가 학습 Cron

생성일: 2026-06-05
목적: 사용 안 하는 시간대에 Supplier Hub 발주서 API/스킬 갱신

## 운영 정책 (KPP/LS와 동일)

- 시간대: 사용자 명령 외 전 시간
- 중단: 사용자 명령 시 즉시 중단
- 순차: 01:30 (KPP 23:30 → LS 00:30 → **Supplier 01:30** → Syncthing 02:30 → Hermes 03:30)
- 분야당 cron 1개

## Supplier Hub cron이 점검/갱신하는 대상

| 대상 | 점검 내용 | 갱신 위치 |
|:----|:---------|:---------|
| 발주서 다운로드 API | `GET /scm/purchase/order/excel`, `/excelList` 엔드포인트 | 새 skill `supplier-hub` SKILL.md |
| 텔레그램 파일 전송 | chat_id, attachment 패턴 | wiki `발주서-다운로드-및-파일-전송.md` |
| 인증 | 쿠팡 Wing/Supplier 로그인 (이중 인증) | supplier-hub SKILL.md §로그인 |
| EUC-KR 파일명 ZIP | Content-Disposition 처리 | supplier-hub SKILL.md §Pitfalls |

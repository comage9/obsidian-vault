# Syncthing 자가 학습 Cron (크로스 디바이스 동기화)

생성일: 2026-06-05
목적: 사용 안 하는 시간대에 Syncthing 동기화 상태 점검 + sendonly/sendreceive 모드 자동 검증

## 운영 정책

- 시간대: 사용자 명령 외 전 시간
- 중단: 사용자 명령 시 즉시 중단
- 순차: 02:30 (KPP 23:30 → LS 00:30 → Supplier 01:30 → **Syncthing 02:30** → Hermes 03:30)
- 분야당 cron 1개

## Syncthing cron이 점검/갱신하는 대상

| 대상 | 점검 내용 | 갱신 위치 |
|:----|:---------|:---------|
| sendonly/sendreceive 모드 | 초기 sendonly → 데이터 검증 후 sendreceive 전환 | `devops/syncthing` SKILL.md |
| .stfolder 수동 생성 금지 | 자동 생성 여부 | syncthing SKILL.md §Pitfalls |
| E:\hermes-backup ↔ /media/comage/data1/hermes-backup 양방향 동기화 | Linux/Windows 디바이스 연결 상태 | 운영원칙 위키 |
| 메모리/skills 동기화 | Windows↔Linux 간 차이 | 운영원칙 |

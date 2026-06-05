# Hermes Agent 자가 학습 Cron (자신 시스템 점검)

생성일: 2026-06-05
목적: 사용 안 하는 시간대에 Hermes Agent 자체의 변경점/업데이트 추적

## 운영 정책

- 시간대: 사용자 명령 외 전 시간
- 중단: 사용자 명령 시 즉시 중단
- 순차: 03:30 (KPP 23:30 → LS 00:30 → Supplier 01:30 → Syncthing 02:30 → **Hermes 03:30**)
- 분야당 cron 1개

## Hermes cron이 점검/갱신하는 대상

| 대상 | 점검 내용 | 갱신 위치 |
|:----|:---------|:---------|
| `hermes-agent` skill | cron, kanban, telegram 게이트웨이 등 명령어 변경 | hermes-agent SKILL.md |
| 스킬 카탈로그 | skills_list() 결과, 신규/제거 스킬 | 메모리 (영구 사실만) |
| `mandatory-verification` skill | 5단계 의무 최신화 | mandatory-verification SKILL.md |
| Memory 규칙 | 작업 진행 상황 X, 사용자 선호만 | 메모리 |
| `delegation.max_concurrent_children` 등 정책 | 환경 설정 변경 | hermes-agent SKILL.md |

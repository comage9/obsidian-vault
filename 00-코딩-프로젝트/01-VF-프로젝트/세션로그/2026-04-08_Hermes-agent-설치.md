# 2026-04-08 VF 프로젝트 세션로그

## VF- 프로젝트 종합 검토 (Hermes-agent)
- Backend: DELETE 전체 삭제 위험, pagination 없음, any 타입
- Frontend: `any` 타입 폭탄, alert() 6곳+, SortableRow 미최적화
- Toss Design Language (#721FE5) 기반으로 CSS/UI 수정

## Hermes-agent 설치 및 구성
- v0.7.0 설치 (`/tmp/hermes-agent/`)
- OpenClaw migration 완료 (vf-production 스킬 포함)
- CLI 보조 도구로 설정 (Telegram gateway는 열지 않음)

## Claude Code 코드 수정 (5 Phase 완료)
1. DELETE 전체 삭제 위험 방지 + pagination
2. `any` 타입 제거
3. `alert()` → toast
4. SortableRow React.memo
5. DRF Serializer

## 주현 말한 것
- Hermes vs OpenClaw는 다른 채널 → 같이 사용 가능
- Claude Code는 코딩 담당, 나는 오케스트레이션
- "지금까지 한 것들 스킬로 저장"

## 다음 할 일
- [ ] Hermes vs OpenClaw 동시 사용 규칙确立
- [ ] MEMORY.md 체계화

---

*최종 업데이트: 2026-04-08*

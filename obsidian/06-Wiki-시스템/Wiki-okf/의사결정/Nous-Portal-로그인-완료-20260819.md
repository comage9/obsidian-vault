# Nous Portal 로그인 완료 (2026-08-19)

## 상태
- **계정**: comage9@gmail.com (Free 구독)
- **로그인**: ✓ 성공 — `hermes portal login` OAuth 디바이스 플로우
- **인증 저장**: `auth.json` → `providers/nous` (access_token + agent_key 포함)
- **현재 기본 모델**: `custom:omniroute` 유지 (Portal 모델로 전환 안 함)

## 진행 절차
1. `hermes portal` 실행 → 디바이스 코드 발급
2. 사용자가 `https://portal.nousresearch.com/manage-subscription?user_code=GMDV-AX79` 승인
3. 모델 선택 프롬프트에서 **8 (Skip, keep current)** 선택 → OmniRoute 유지
4. 완료 메시지: "Nous credentials saved for future use"

## 사용 방법
- **Portal로 전환**: `hermes model` 실행 → Nous Portal 선택 (300+ 모델)
- **상태 확인**: `hermes portal info`
- **Tool Gateway**: web search 등은 Portal 구독으로 라우팅 가능 (현재 미설정)

## 참고
- Free 구독이라 Portal 모델은 무료 모델 위주
- 사용자 선호: 기본 통로는 OmniRoute 유지 → Portal은 필요 시 전환용
- 이전 세션(2026-08-11)에서 로그인 시도 실패 → 이번에 성공

# KPP Pitfall Nightly Cron (자가 학습)

생성일: 2026-06-05
목적: Hermes가 사용 안 하는 시간대에 KPP(WPPS) 자동화 함정/패턴 변화 추적 + 스킬·위키 자동 갱신

## 운영 정책

1. **시간대**: "자기 전"만 ❌ → **사용자 명령 외 전 시간대** (낮 시간대 포함). 단 사용자 명령 입력 시 즉시 중단 + 지시 우선.
2. **중단 정책**: 사용자 명령 도착 → 현재 단계 commit(메모리/DB) 후 다음 cron tick부터 skip. 진행 중 작업은 강제 종료 X.
3. **순차 실행**: KPP → LS → 서플라이허브 → Syncthing → Hermes 자체 (5개 cron이 서로 시간 안 겹침).
4. **분산 배치**: 5개 cron 각 1개씩, 분야당 1개 (KPP 10개 X).
5. **신뢰도**: KPP는 pitfall 데이터 풍부 → cron 1개 가치 명확. 나머지 4개 분야별 1개.

## KPP cron이 점검/갱신하는 대상

| 대상 | 점검 내용 | 갱신 위치 |
|:----|:---------|:---------|
| WPPS PBM110MW/140MW 자동화 함정 | 6/4 이후 새 함정 발견 시 | `kpp-pallet-management/references/pbm140mw-automation-pitfalls.md` + `wiki/물류/KPP-자동화-함정-*.md` |
| SpreadJS Grid API 변경 | `getValue()` 로컬캐시 문제, native alert 한계 | 스킬 SKILL.md §Pitfalls |
| 재시도 패턴 검증 | 1차 8s + 1회 재시도 가이드가 여전히 유효한지 | 스킬 + 위키 `KPP-조회-재시도-패턴.md` |
| React Controlled Input 패턴 | `nativeInputValueSetter + dispatchEvent('input'/'change')` 유효성 | 스킬 § Pitfalls |
| Edge native modal | sync-confirmation-dialog, password save 한계 | 스킬 §Pitfalls |
| login API | POST /login.do {loginId, password, loginType:'ps'} 응답 형식 | 스킬 §로그인 |

## Cron 정의

- **ID**: `kpp-pitfall-nightly`
- **schedule**: 매일 23:30 (자기 전 시간대 시작점)
- **prompt**: 아래 1~3단계 자동 실행
- **skills**: `kpp-pallet-management`, `mandatory-verification`
- **no_agent**: false (판단 필요)

### Prompt 템플릿

```
오늘(YYYY-MM-DD) 기준 KPP(WPPS) 자동화 함정/패턴 점검:

1. skill_view(name='kpp-pallet-management') 로드 → SKILL.md의 §Pitfalls, references/pbm140mw-automation-pitfalls.md 읽기
2. Wiki/물류/KPP-자동화-함정-*.md, KPP-조회-재시도-패턴.md, 출하통보-PBM140MW-차량번호-규칙.md, 납품반납요청-PBM110MW.md 읽기
3. (선택) ls.coupang.com 또는 wpps.logisall.net 직접 조회하지 말 것. cron은 문서/스킬 점검만.
4. 새로운 함정/변경 발견 시:
   - 스킬 SKILL.md §Pitfalls에 추가
   - Wiki/물류/KPP/에 새 파일로 기록 (검증 출처 명시)
   - 메모리에 사용자 선호/절차 사실만 추가 (단, 작업 진행 상황 X)
5. 변경 없으면 "KPP 점검 완료: 변경 없음 (YYYY-MM-DD)" 한 줄 보고
6. 사용자 명령 도착 시 즉시 중단 + "사용자 명령 수신, cron 중단" 한 줄 보고 후 commit
```

## 검증 체크리스트 (cron 첫 실행 후 확인)

- [ ] cron이 skill + wiki만 읽고 외부 시스템 미접근
- [ ] 변경 발견 시 양쪽(스킬+위키) 동시 갱신
- [ ] 사용자 명령 시 즉시 중단 보고
- [ ] 0건 시 한 줄 보고 (verbose X)
- [ ] 스킬/위키 파일 크기 증가분 검증

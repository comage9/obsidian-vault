# LS Coupang (ls.coupang.com) 자가 학습 Cron

생성일: 2026-06-05
목적: 사용 안 하는 시간대에 LS Coupang 트럭오더 API/Keycloak 인증 흐름 변화 추적

## 운영 정책 (KPP와 동일)

1. 시간대: 사용자 명령 외 전 시간
2. 사용자 명령 시 즉시 중단 + commit
3. 순차: KPP(23:30) → LS(00:30) → 서플라이허브(01:30) → Syncthing(02:30) → Hermes(03:30)
4. 분야당 cron 1개

## LS cron이 점검/갱신하는 대상

| 대상 | 점검 내용 | 갱신 위치 |
|:----|:---------|:---------|
| Keycloak OAuth | `xauth.coupang.com/auth/realms/fts/protocol/openid-connect/auth` action URL 패턴 | `ls-coupang/SKILL.md` §로그인 |
| Akamai 우회 | User-Agent, Accept-Language 헤더 | `ls-coupang/SKILL.md` §Akamai |
| Tracking API | `statuses=SUBMITTED,CONFIRMED,CANCELED,BACK` 필수, locationStart=VF67 | `ls-coupang/SKILL.md` §Tracking |
| 쿠키/JWT 만료 | Keycloak access_token TTL | 스킬 §인증 |

## Cron 정의

- **ID**: `ls-coupang-nightly`
- **schedule**: 매일 00:30
- **skills**: `ls-coupang`, `mandatory-verification`

# Hermes 자가 학습 Cron 시스템

> 다른 에이전트 온보딩용 — 자가 학습 Cron의 개념/구성/운영 방법
> 마지막 갱신: 2026-06-07

---

## 1. 개념

Hermes Agent가 **사용자가 명령하지 않는 시간대**(야간/새벽)에 백그라운드에서 각 분야별 문서/스킬/위키를 점검·갱신하는 시스템.

### 핵심 정책 (3대 원칙)

| 원칙 | 내용 |
|:-----|:------|
| **⏰ 시간대** | "자기 전"만 ❌ → 사용자 명령 외 전 시간대 (낮/밤 무관, 사용자 활동 외) |
| **📂 분야 분산** | 분야당 cron 1개, 여러 분야에 분산 배치 (중복 금지) |
| **👤 사용자 우선** | 사용자 명령 도착 시 즉시 중단 → 지시 사항 먼저 수행 |

---

## 2. 전체 Cron 목록 (5개)

모든 cron은 `mandatory-verification` 스킬을 포함하여 Pre-flight Check 수행.

| # | 시간 | 분야 | Cron ID | 사용 스킬 | 설명 |
|:-:|:---:|:-----|:-------:|:---------|:------|
| 1 | **23:30** | KPP (WPPS) | `b773a0727897` | `mandatory-verification`, `kpp-pallet-management` | PBM110MW/140MW 함정, SpreadJS, React Input 패턴 점검 |
| 2 | **00:30** | LS (Coupang) | `6fcf4d848e14` | `mandatory-verification`, `ls-coupang` | Keycloak OAuth, Akamai 우회, Tracking API 점검 |
| 3 | **01:30** | 서플라이허브 | `cf856531b78f` | `mandatory-verification` | 발주서 API, EUC-KR ZIP, 텔레그램 전송 점검 |
| 4 | **02:30** | Syncthing | `fc42d7ad9ff6` | `mandatory-verification` | sendonly/sendreceive, 양방향 동기화 점검 |
| 5 | **03:30** | Hermes Self | `bf08d649e866` | `mandatory-verification` | Hermes Agent 명령어, 스킬 카탈로그, 메모리 정책 점검 |
| **6** | **04:30** | **KI AI Trader** | `0608378496ca` | `mandatory-verification`, `ki-ai-trader`, `ki-ai-trader-ai`, `ki-ai-trader-config` | AI 모델 연결, 설정 정합성, 포지션 현황, 프로세스 상태 점검 |
| **7** | **05:30** | **VF2 생산계획** | `48144ff13cee` | `mandatory-verification`, `vf2-production-plan-conventions` | 색상코드/금형명/upsert/CAP 코드 정합성, DB vs 기준 문서 비교 |
| **8** | **06:30** | **VF2 프로젝트** | `27c1b2555f38` | `mandatory-verification` | 백엔드/프론트엔드 상태, POST 라우트 점검, DB 건수, 시스템 리소스 |

---

## 3. 동작 방식

### 3.1 일반 흐름

```
사용자 미명령 시간대
  → cron tick 실행
    → mandatory-verification 로드 (Pre-flight)
    → 해당 분야 스킬 로드 + Wiki 문서 읽기
    → 변경/갱신 필요 사항 발견?
        ├─ YES → SKILL.md §Pitfalls 갱신 + Wiki 저장
        └─ NO  → "변경 없음 (YYYY-MM-DD)" 한 줄 보고
    → 사용자 명령 도착? 
        ├─ YES → 즉시 중단, 사용자 지시 우선
        └─ NO  → 정상 종료
```

### 3.2 제약 조건

| 조건 | 설명 |
|:-----|:------|
| **외부 시스템 접근 금지** | `ls.coupang.com`, `wpps.logisall.net` 직접 조회 불가. 문서/스킬만 점검 |
| **점검 대상 3개 미만 = cron 생성 안 함** | 데이터 빈약 분야는 가치 없음 |
| **강제 종료 금지** | 진행 중 작업은 commit 후 skip. 영구 자원 손실 방지 |
| **Git 백업 선행** | 자가 학습 실행 전 Git push 완료 확인 |
| **분산 배치** | 같은 시간대 cron 중복 금지 |

---

## 4. Cron Prompt 템플릿 (신규 분야 추가 시)

```markdown
오늘 날짜 기준 {분야} 자가 점검 1회 실행.

[필수 사전 단계]
1. skill_view(name='{skill}') 로드
2. Wiki {wiki/경로/} 모든 .md 읽기
3. **{외부시스템} 직접 조회하지 말 것** (cron은 문서/스킬 점검만)

[판단 단계]
4. {변화 발견 시}:
   - {skill}/SKILL.md §Pitfalls에 append
   - Wiki {경로}에 새 파일 (검증 출처 명시)
5. 변경 없으면 "변경 없음 (YYYY-MM-DD)" 한 줄
6. 사용자 명령 시 즉시 중단

[진행보고]
- (a) 점검 대상 (b) 비교 방법 (c) 검증 결과
```

---

## 5. Cron 생성/수정 방법

### 5.1 Hermes CLI

```bash
hermes cron list              # 전체 목록
hermes cron create SCHEDULE   # 신규 생성
hermes cron edit ID           # 수정
hermes cron pause/resume ID   # 일시중지/재개
hermes cron remove ID         # 삭제
```

### 5.2 in-session

cronjob(action='create', schedule='30 23 * * *', name='...', prompt='...', skills=[...])
cronjob(action='list')
cronjob(action='update', job_id='...', prompt='...')

---

## 6. 파일 위치

| 항목 | 경로 |
|:-----|:------|
| **이 문서** | `Wiki/Hermes/자가-학습-Cron/README.md` |
| **KPP Nightly 상세** | `Wiki/Hermes/자가-학습-Cron/KPP-Pitfall-Nightly-20260605.md` |
| **LS Nightly 상세** | `Wiki/Hermes/자가-학습-Cron/LS-Coupang-Nightly-20260605.md` |
| **Supplier Hub Nightly** | `Wiki/Hermes/자가-학습-Cron/Supplier-Hub-Nightly-20260605.md` |
| **Syncthing Nightly** | `Wiki/Hermes/자가-학습-Cron/Syncthing-Nightly-20260605.md` |
| **Hermes Self Nightly** | `Wiki/Hermes/자가-학습-Cron/Hermes-Self-Nightly-20260605.md` |
| **KI AI Trader Nightly (신규)** | `Wiki/Hermes/자가-학습-Cron/KI-AI-Trader-Nightly.md` |
| **VF2 생산계획 Nightly (신규)** | `Wiki/Hermes/자가-학습-Cron/VF2-Production-Plan-Nightly.md` |
| **VF2 프로젝트 Nightly (신규)** | `Wiki/Hermes/자가-학습-Cron/VF2-Project-Nightly.md` |
| **로컬 스킬 (참고)** | `C:\Users\kis\AppData\Local\hermes\skills\devops\self-learning-cron\SKILL.md` |

---

## 7. 변경 이력

| 일자 | 변경 내용 |
|:----|:---------|
| 2026-06-05 | 자가 학습 Cron 시스템 최초 구축 (5개 분야) |
| 2026-06-07 | Git Wiki 업로드 (다른 에이전트 온보딩용) |
| 2026-06-07 | KI AI Trader(04:30) / VF2 생산계획(05:30) / VF2 프로젝트(06:30) 신규 추가 |

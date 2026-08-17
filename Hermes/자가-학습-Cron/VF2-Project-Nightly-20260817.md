# 2026-08-17 VF2 Project Nightly — 자가 점검 리포트

> 실행 시각: 2026-08-17 06:30 KST (Cron ID: `27c1b2555f38` — VF2 프로젝트 자가 학습)
> 기준 보고서: `VF2-Production-Plan-Nightly-20260817.md` (05:31 실행) 병합

---

## ① 백엔드/프론트 상태 — DOWN 지속 (systemd 미등록 6회째)

| 항목 | 상태 | 상세 |
|------|------|------|
| **백엔드 (포트 5176)** | ❌ **DOWN** | 08-16 14:41 기동 후 14시간 만 자발 종료. backend.log 마지막 항목 14:43:22 |
| **프론트엔드 (포트 5174)** | ❌ **DOWN** | Vite dev server 미실행. `dist/` 빌드만 존재 (2026-06-10) |
| **systemd 서비스** | ❌ **미등록** | `vf2-backend.service` 없음. 06-23→07-06→08-17 **6회째 반복** |

**판정**: 07-04 수동 기동 후 48시간 재종료 패턴이 08-16 기동 후 14시간 만에 재발. **수동 기동만으로는 재발 방지 불가, systemd 등록이 유일한 영구 해법** 재확인.

---

## ② 데이터베이스 상태 — 운영 침묵 70일째, production_plans 테이블 부재 51일째

| 테이블 | 행 수 | 최신 데이터 | 비고 |
|--------|-------|-------------|------|
| `production_logs` | 15,886 | **2026-06-09 08:20** | 70일째 신규 운영 데이터 없음 |
| `production_plans` | — | **테이블 없음** | `to_regclass` NULL, 51일째 지속 (06-26 최초 확인) |

**상태 분포** (production_logs):
| status | count | 비율 | 해석 |
|--------|-------|------|------|
| **started** | **10,916** | **68.7%** | 1.xlsx historical 10,826 + 운영 90 |
| **pending** | **4,967** | **31.3%** | import 후 누적, 사용자 결정 대기 |
| **ended** | **3** | 0.02% | 변동 없음 |

**started 비율 68.7%** → 70% 임계치 근접. §20 (3) "started 비율 > 70% 경보" 발동 임박.

---

## ③ 디스크 사용률 — 73% (WARNING 해소, 재가속 위험 잔존)

| 일자 | 사용률 | 일일 Δ | 판정 |
|------|-------|--------|------|
| 07-18 | 72% | - | 재가속 시작 |
| 08-16 | 83% | +11%p/29일 | WARNING 지속 |
| **08-17** | **73%** | **-10%p/1일** | **절대값 80% 미만 이탈 → 해소 선언 (§7 #30)** |

**재가속 위험**: 이전 가속기 평균 +2.5~3%p/일 지속 시 **약 7일 후 80% 재진입 → WARNING 재선언** 예측. 디스크 정리 효과 지속성 관찰 필요.

---

## ④ 미해결 결함 4건 — 40~85일째 잔존 (Read-only 점검 한계)

| # | 결함 | 최초 발견 | 잔존 일수 | 영향 |
|---|------|----------|----------|------|
| 1 | 6-튜플 중복 mold 111 Butter (4행) | 06-08/09 | **40일+** | 운영 정확성 (이중 카운트) |
| 2 | 데크타일(114) color2 빈값 (2건) | 06-07 | **71일** | 룰 위반 (WHITE2→IVORY 1154, Ivory→IVORY 1060) |
| 3 | 빈 moldNumber id=19416 (M01) | 05-24 | **85일** | 노이즈/placeholder |
| 4 | color2 White 180 10건 (비표준) | 06-08 | **70일** | 대소문자 통일 (표준: WHITE 180) |

**시사점**: Read-only cron은 결함 탐지만 하고 정정 못 함. 사용자 결정 대기 40일+ 경과. **결함 정정 전용 수동 작업 필요** 또는 자동 정정 정책 변경 논의 필요.

---

## ⑤ Git 상태 — 5 커밋 로컬 선행 (push 필요)

```bash
$ git status
현재 브랜치 main
브랜치가 'origin/main'보다 5개 커밋만큼 앞에 있습니다.
```

| 커밋 | 메시지 | 날짜 |
|------|--------|------|
| 5e98c7d | docs: VF2 Project Nightly 자가 점검 2026-08-16 — 운영 침묵 69일/디스크 83% 경고 | 08-16 |
| a283c4e | docs: 시스템 헌법/크론 레지스트리/작업내역 적용 (CLAUDE.md, AGENTS.md, README.md 업데이트) | 06-27 |
| 1263386 | feat: 전산재고 단가 관리 + outbound 표시 수정 + 인벤토리 컴포넌트 정리 | - |
| 6ce0f16 | fix: inventory baseline-upload 404 — PostBaselineUpload 핸들러 + 라우트 등록 | - |
| 541bc4c | fix: 2배수 막대그래프 + 업로드 버튼 + 인증헤더 + 데일리 예측 핸들러 | - |

**조치 필요**: `git pull origin main --rebase && git push origin main` (원격 선행 커밋 가능성 대비 pull --rease 먼저)

---

## ⑥ 크론 작업 상태 — VF2 관련 2건 활성, 일부 토큰 한도 에러

| Job ID | 이름 | Schedule | 마지막 실행 | 상태 |
|--------|------|----------|-------------|------|
| `48144ff13cee` | VF2 생산계획 자가 학습 | `0 5 * * *` | 08-17 05:41 | ✅ ok |
| `27c1b2555f38` | VF2 프로젝트 자가 학습 | `0 6 * * *` | **실행 중 (본 작업)** | 🔄 running |

**참고**: `auto-daily-summary`, `auto-weekly-optimization`, `Wiki Git Auto-Sync`, `Wiki Daily Cleanup`, `Wiki Daily Briefing` 등에서 **HTTP 429 Token Plan limit** 에러 다수 발생. OpenRouter 크레딧 한도 도달.

---

## ⑦ 종합 판정 및 차기 점검 예측 (08-18 06:30)

| 항목 | 현재 | 예측 (08-18) | 조건 |
|------|------|--------------|------|
| 백엔드/프론트 | **DOWN** | DOWN 지속 | systemd 미등록 시 |
| 디스크 | **73%** | ~75~76% | +2~3%p/일 재가속 시 |
| 운영 침묵 | **70일째** | 71일째 | max_date 변동 없음 시 |
| 미해결 결함 | **4건** | 4건 잔존 | 사용자 정정 명령 없음 시 |
| started 비율 | **68.7%** | ~69% | 변동 없음 시 70% 임계치 도달 임박 |
| production_plans | **부재** | 부재 지속 | 마이그레이션 미수행 시 |

---

## ⑧ 권장 조치 (우선순위 순)

| 우선순위 | 조치 | 담당 | 비고 |
|----------|------|------|------|
| **P0** | systemd 서비스 등록 (`vf2-backend.service`) | 사용자/인프라 | 6회째 반복, 영구 해법 유일 |
| **P1** | `production_plans` 테이블 마이그레이션 실행 | 사용자/개발 | 51일째 부재, 운영 데이터 연결 단절 |
| **P2** | 4대 결함 정정 실행 (SQL 또는 수동) | 사용자 | 40~85일 대기, Read-only 한계 |
| **P3** | Git push (pull --rebase 후) | 사용자/자동화 | 5 커밋 선행, 원격 충돌 가능성 |
| **P4** | 디스크 재가속 모니터링 (일일 2~3%p 임계) | 자동 크론 | 7일 내 80% 재진입 예측 |

---

## ⑨ Canonical 절차 준수 검증

| 단계 | 수행 | 비고 |
|------|------|------|
| 1. Wiki 검색 | ✅ | 직전 보고서 2개 발견 (Production Plan + Project Nightly) |
| 2. 스킬 로드 | ✅ | `vf2` umbrella + references (nightly-2026-08-17 등) |
| 3. 질문/실행 구분 | ✅ | cron 자동 실행 (read-only 점검) |
| 4. 검증 | ✅ | DB 직접 조회, 프로세스 확인, 디스크 df, git status |
| 5. 승인 | ✅ | read-only, 사용자 결정 대기 항목만 보고 |

**Skip 명시**: `vf2-production-plan-conventions` 단일 스킬 부재, `USER.md`/`MEMORY.md`/`mandatory-verification` 부재 — 보고서에 기록 완료.

---

## References

- Canonical: `references/vf2-production-plan-nightly-canonical.md`
- Conventions: `references/production-plan-conventions.md` §19/§20
- 직전 보고서: `VF2-Production-Plan-Nightly-20260817.md` (05:31), `VF2-Project-Nightly-20260816.md`
- 학습 시사점 시리즈: `vf2-nightly-2026-07-18.md` ~ `vf2-nightly-2026-07-01.md`
# 2026-04-12 VF 프로젝트 세션로그

## 오전 세션 (07:20~09:05)
- MindVault 설치 완료 (VF 프로젝트에 적용)
- "바이브코딩은 왜 실패하는가" 가이드 학습
- Obsidian + Claude Code 연동 계획 수립
- Claude Desktop은 Linux에서 사용 불가 → 나(알이) + Claude Code만 사용 결정

## 오전 세션 (11:29~)
- 자동 분류 체계 논의
- 브레인이 자동 분류 + Obsidian 기록 결정
- Obsidian Vault 생성 시작

## Obsidian Vault 생성
- **경로**: `~/obsidian-vault/`
- **GitHub**: https://github.com/comage9/obsidian-vault
- **구조**:
  - 01-VF-프로젝트/ (세션로그, 의사결정, 에러로그)
  - 02-Claude-Code/ (세션로그)
  - 03-Obsidian-설정/
  - 04-일반/ (세션로그, 의사결정)
- **동기화**: GitHub로 Push/Pull 가능

## 모바일 스크롤 수정
- TouchSensor delay 200ms → 0ms
- touch-none 제거, touch-action: pan-y 추가
- Commit: 22d2809, 0235bb0

## 오후 세션 (14:32~)

### Windows 배치 파일 경로 수정 (ededd17)
**문제**: Windows에서 start_frontend.bat 실행 시 UI가 텍스트만 표기 (TailwindCSS 미적용)

**근본 원인**:
- TailwindCSS가 `frontend/src/`를 찾았지만 실제 React 코드는 `frontend/client/src/`에 있음
- CWD가 `frontend/`여서 잘못된 경로에서 CSS 클래스 스캔 → 0바이트 CSS 생성

**수정 파일**:
| 파일 | 수정 전 | 수정 후 |
|------|--------|--------|
| start_frontend.bat | `cd frontend` | `cd frontend\client` |
| start_all.bat | `cd frontend` | `cd frontend\client` |

## 오후 세션 (15:51~) - 미완료 작업 진행

### 작업 순서: 2-3-4-5-6-1

### 2. 재고 입력 기능 ✅ 완료 (b5cd23f)
- production-plan.tsx에 '재고 확인' 탭 추가
- 진행 중/완료/재고 3개 탭
- 현재 재고 수량 표시 (상위 50개)
- 재고 수량 직접 수정 기능 (수정 아이콘 클릭 → 입력 → 확인/취소)

### 3. 출고량 확인 ✅ 이미 구현됨
- OutboundStatsPanel 컴포넌트 이미 존재
- 7일 출고량, 제품별 출고, 최소 보관 기준 미달 제품 표시
- 위치: `frontend/client/src/components/shared/outbound-stats-panel.tsx`

### 4. AI 생산 추천 ✅ 이미 구현됨
- OutboundStatsPanel에 AI 생산 우선순위 추천 포함
- 긴급/권장 배지로 표시
- 백엔드 API: `/api/ai/production-recommend`

### 5. 에이전트 위임 체계 🔴 미구현
- 주현 요청: 다중 작업 시 응답 지연/없음 해결
- 각 AI 에이전트에게 작업 위임
- OpenRouter 무료 AI 우선 → 실패 시 고성능 AI

### 6. Obsidian MCP 플러그인 🔴 미완료
- Obsidian 앱에서 "Clone a remote vault"로 GitHub repo clone 필요
- Repository: https://github.com/comage9/obsidian-vault

### 1. AI thinking 필터링 🔴 미해결
- 문제: 영어 thinking이 응답에 포함됨
- 원인: AI 모델이 프롬프트 무시하고 사고 과정 응답에 포함
- 시도: 프롬프트 강화 → 실패, 프론트엔드 필터링 → 실패
- 해결책: 백엔드 후처리 또는 thinking 없는 모델로 교체

---

## GitHub Commits (2026-04-12)

| Commit | 내용 |
|--------|------|
| 22d2809 | 모바일 스크롤 충돌 수정 |
| 0235bb0 | 스크롤 fix - touch-none 제거 |
| ededd17 | Windows bat 경로 수정 |
| b5cd23f | 재고 확인 탭 추가 |

---

## API 목록 (참고)

### Backend APIs
- `GET /api/inventory/` - 재고 unified
- `PATCH /api/inventory/{id}` - 재고 수정
- `GET /api/outbound/stats` - 출고 통계
- `GET /api/outbound/top-products` - 제품별 출고
- `POST /api/ai/production-recommend` - AI 생산 추천
- `POST /api/ai/analyze` - AI 분석

### Frontend Components
- `OutboundStatsPanel` - 출고량 통계 + AI 추천
- `production-plan.tsx` - 생산 계획 페이지 (재고 탭 추가됨)

---

*최종 업데이트: 2026-04-12 22:21*

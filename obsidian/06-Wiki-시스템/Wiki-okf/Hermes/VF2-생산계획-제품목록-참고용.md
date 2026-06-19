# VF2 생산 계획 & 제품 목록 — 참고용

> ⚠️ **참고용 (Reference Only)**
> 이 기능의 실질적 운영·수정·보완은 전담 에이전트(Hermes)가 담당.
> 다른 에이전트는 구조 파악 및 참고용으로만 사용.
> **전담 에이전트**: Hermes (현재 세션)
> **생성일**: 2026-06-07

---

## 1. 생산 계획 (Production Plan) — `/production`

### 프론트엔드
- **파일**: `frontend/src/pages/production-plan.tsx` (2,367줄, React + TypeScript)
- **주요 라이브러리**: `@dnd-kit/core`, `@dnd-kit/sortable` (드래그 앤 드롭 정렬)
- **UI 컴포넌트**: shadcn/ui (Dialog, Badge, Card, Button, Input, Select, Checkbox, Popover, Command)
- **상태 관리**: `@tanstack/react-query` (useQuery, useMutation)
- **공유 모듈**: `src/components/shared/` — `api.ts`, `types.ts`, `outbound-stats-panel.tsx`
- **라우트**: `dashboard.tsx` → `case "/production": return <ProductionPlan />`

### 생산 아이템 데이터 구조
```typescript
interface ProductionItem {
  id: number;
  date: string;
  machineNumber: string;
  moldNumber: string;
  productName: string;
  productNameEng?: string;
  color1?: string;
  color2?: string;
  unit?: string;
  quantity?: number;
  unitQuantity?: number;
  total?: number;
  status?: 'pending' | 'started' | 'ended' | 'stopped';
  startTime?: string;
  endTime?: string;
  sortOrder?: number;
}
```

### 백엔드 API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/production` | 생산 로그 조회 (날짜/기계 필터) |
| POST | `/api/production-log` | 생산 로그 등록/수정 |
| DELETE | `/api/production-log/:date` | 일자별 삭제 |
| DELETE | `/api/production-log/bulk-delete` | 선택 일괄 삭제 |
| POST | `/api/production-log/move-pending-to-today` | 대기 항목 → 오늘 이동 |
| POST | `/api/production/copy-day` | 특정일 생산계획 복사 |
| POST | `/api/ai/production-recommend` | AI 생산 추천 |
| POST | `/api/ai/production-chat` | AI 생산 채팅 |
| GET | `/api/ai/production-analysis` | 생산량 AI 분석 |

### DB
- **테이블**: `production_logs` (GORM)
- **AI 엔진**: `services/ai.go` — 공장 생산 관리자 프롬프트 기반 한국어 추천
- **예측 엔진**: `services/forecasting.go`

---

## 2. 제품 목록 (Product Master) — `/master`

### 프론트엔드
- **파일**: `frontend/src/pages/product-master.tsx` (346줄)
- **공유 컴포넌트**: `src/components/product-master-tab.tsx`
- **라우트**: `dashboard.tsx` → `case "/master": return <ProductMaster />`

### Spec 데이터 구조
```typescript
interface Spec {
  id: number;
  product_name: string;
  product_name_eng?: string;
  mold_number?: string;
  color1?: string;
  color2?: string;
  default_quantity?: number;
}
```

### 백엔드 API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/master/specs` | 전체 Spec 조회 |
| POST | `/api/master/specs` | Spec 등록 (단일/일괄) |
| PUT | `/api/master/specs/:id` | Spec 수정 |
| DELETE | `/api/master/specs/:id` | Spec 삭제 |
| POST | `/api/master/extract` | AI 자동 Spec 추출 |

### DB
- **테이블**: `specs` (GORM)

---

## 3. VF2 기본 정보

| 항목 | 값 |
|------|-----|
| 위치 | `/home/comtop/workspace/VF2/` |
| 백엔드 | Go 1.x + Gin + GORM, 포트 5176 |
| 프론트엔드 | React 18 + TypeScript + Vite, 포트 5174 |
| DB | PostgreSQL (`postgres_hermes` Docker, `vf2_db`) |
| 인증 | `TokenAuthMiddleware` — `/api/health` 제외 모든 API에 `Authorization: Bearer` 필수 |
| 실행 | 백엔드: `./vf2_backend_bin`, 프론트엔드: `npm run dev` |
| Git | 마지막 커밋 `1263386` (2026-06-05) — 이후 변경사항 미커밋 |

---

## 4. 파일 구조

```
frontend/src/pages/
├── production-plan.tsx    ← 생산 계획
├── product-master.tsx     ← 제품 목록
└── dashboard.tsx          ← 라우팅

backend/
├── handlers/
│   ├── production.go      ← 생산 CRUD
│   ├── master.go          ← Spec CRUD
│   └── ai.go              ← AI 분석/추천
├── services/
│   ├── ai.go              ← AI 엔진
│   └── forecasting.go     ← 예측 엔진
└── main.go                ← 라우터
```

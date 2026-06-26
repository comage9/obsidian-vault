# React Mindmap UI 보고서 (2026-06-26)

**작업 일자**: 2026-06-26
**작업자**: Hermes Agent
**목적**: Neo4j Browser 외부 의존 탈피, 자체 React UI 구축

---

## 1. 개요

Neo4j Browser URL 대신 **자체 React UI**를 구축했습니다.

| 비교 | Neo4j Browser URL | React Mindmap UI (자체) |
|:----|:----|:----|
| 접근성 | Neo4j Browser 외부 노출 필요 | 자체 호스팅 (port 3000) |
| 인터랙티브 | 기본 (클릭/드래그) | ✅ 커스텀 (cytoscape.js) |
| 모바일 | 제한 | ✅ 반응형 가능 |
| 데이터 보호 | Neo4j Browser 노출 | ✅ 앱 경계 |
| 개발비용 | 0 | 1일 |

**결정**: 자체 React UI 채택 (이식성 + 보안 + UX)

---

## 2. 아키텍처

```
[ Neo4j 5.26.27 (Docker, port 7687) ]
                ↓ bolt
[ FastAPI 백엔드 (port 8765) ]
   - GET /api/stats
   - GET /api/graph/all
   - GET /api/graph/by-type/{label}
   - GET /api/graph/path?from=A&to=B
   - GET /api/strategies
   - GET /api/orders/recent
   - GET /api/orders/by-stock/{code}
                ↓ HTTP
[ React 19 + Vite 8 (port 3000) ]
   - cytoscape.js 그래프 시각화
   - cose-bilkent 레이아웃
   - 라벨별 색상 (Stock=green, Order=orange, Strategy=blue, Backtest=purple, Document=red, Entity=yellow)
```

---

## 3. 구현 (Phase별)

### 3.1 Phase 1: 아키텍처 결정
- **백엔드**: FastAPI (Python 3.12) - Neo4j 드라이버 이미 설치됨
- **프론트엔드**: Vite + React 19 + cytoscape.js
- **포트**: API 8765, Web 3000

### 3.2 Phase 2: FastAPI 백엔드
**파일**: `src/api/neo4j_routes.py` (310 lines, 13 routes)

**해결한 문제**:
- `.venv-3.12/lib/python3.12/site-packages/src/` (가짜 src 패키지 v1.0.0)
- `from .main import main` → `from rag_en import ...` (rag_en 없음)
- **해결**: 가짜 src → `src.backup`으로 이름 변경

**13개 라우트**:
| Route | Method | Purpose |
|:-----|:----:|:--------|
| / | GET | Root (서비스 정보) |
| /api/stats | GET | 노드/관계 통계 |
| /api/graph/all | GET | 전체 그래프 (limit 100) |
| /api/graph/by-type/{label} | GET | 특정 라벨 |
| /api/graph/path | GET | 두 노드 간 최단 경로 |
| /api/strategies | GET | 전략별 백테스트 |
| /api/orders/recent | GET | 최근 매매 이력 |
| /api/orders/by-stock/{code} | GET | 종목별 매매 |

### 3.3 Phase 3: React 프론트엔드
**파일**: `mindmap-ui/src/App.tsx` (250 lines)

**주요 기능**:
- 사이드바: 통계, 라벨별 분포, 관계 타입
- 필터: 전체/Stock/Order/Strategy/Document
- 노드 클릭 → 속성 정보 표시
- 색상 코딩: 라벨별 색상
- 자동 레이아웃: cose-bilkent

**검증**: Vite 빌드 성공 (753KB, gzip 236KB)

### 3.4 Phase 4: 통합 테스트
```
Neo4j 125 노드/16 관계
  ↓ bolt
FastAPI 8765 ✅ 200 OK
  ↓ /api 프록시
Vite dev 3000 ✅ 200 OK
```

### 3.5 Phase 5: 대시보드 임베드
**파일**: `scripts/embed_neo4j_in_dashboard.py` 갱신

`dashboard/STATUS.md`에 React UI URL 추가:
- URL: http://localhost:3000
- API: http://localhost:8765 (FastAPI)
- 기술 스택, 백엔드 라우트 수 표시

**자동 시작 스크립트**: `scripts/mindmap_ui_start.sh`
- FastAPI 자동 시작
- Vite 자동 시작
- 헬스 체크 (200 OK)

---

## 4. 누적 시스템

| 항목 | 값 |
|:-----|:---:|
| Neo4j 노드 | **125개** |
| Neo4j 관계 | **16개** |
| FastAPI 라우트 | **13개** |
| React 컴포넌트 | 1개 (App.tsx) |
| 빌드 크기 | 753KB (gzip 236KB) |

---

## 5. 핵심 명령

```bash
# 자동 시작 (백엔드 + 프론트엔드)
bash /workspace/ki-ai-trader/scripts/mindmap_ui_start.sh

# 수동 시작
# 백엔드
cd /workspace/ki-ai-trader && .venv-3.12/bin/python3 -m uvicorn src.api.neo4j_routes:app --host 0.0.0.0 --port 8765
# 프론트엔드
cd /workspace/ki-ai-trader/mindmap-ui && npm run dev

# 빌드 (production)
cd /workspace/ki-ai-trader/mindmap-ui && npm run build
```

---

## 6. 향후 작업

| # | 작업 | 우선순위 |
|:-:|:----|:----:|
| 1 | **실시간 업데이트** (WebSocket, 1초 단위) | 🟡 |
| 2 | **노드 검색** (인풋 박스) | 🟢 |
| 3 | **Drag-and-Drop 노드 배치** | 🟡 |
| 4 | **Export (PNG/SVG)** | 🟢 |
| 5 | **Neo4j Bolt over WebSocket** | 🟡 |

---

## 7. 파일 목록

### 신규 파일
- `ki-ai-trader/src/api/neo4j_routes.py` (FastAPI 백엔드)
- `ki-ai-trader/mindmap-ui/src/App.tsx` (React 컴포넌트)
- `ki-ai-trader/mindmap-ui/src/App.css` (스타일)
- `ki-ai-trader/mindmap-ui/vite.config.ts` (Vite 프록시)
- `ki-ai-trader/scripts/mindmap_ui_start.sh` (자동 시작)
- `ki-ai-trader/docs/REACT_MINDMAP_UI_20260626.md` (이 보고서)

### 수정 파일
- `scripts/embed_neo4j_in_dashboard.py` (React UI 섹션 추가)

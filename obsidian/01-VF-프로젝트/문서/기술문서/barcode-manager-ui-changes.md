# BarcodeManager UI 수정 내역 (2026-06-06)

## 개요
VF2 프론트엔드 `/barcode-manager` 페이지의 바코드 출력 설정 UI 개선.
리자닉스(Reasonix Go 1.0)로 모든 코딩 작업 진행.

## 작업 단위

### 1. 슬라이더 범위 확장
| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| cellPadding (셀 안쪽 여백) | max=10, step=1 | max=50, step=1 |
| cellGap (셀 간격) | max=40, step=1 | max=100, step=1 |
| barcodeGap (송장↔바코드 간격) | max=60, step=2 | max=150, step=1 |

### 2. 슬라이더 0 중앙 배치
- cellPadding: 0~50 → **-25~25** (0이 중앙)
- cellGap: 0~100 → **-50~50** (0이 중앙)

### 3. 슬라이더 기능 재정의
| 슬라이더 | 전 (라벨/기능) | 후 (라벨/기능) |
|---|---|---|
| 1번 (-25~25) | "셀 안쪽 여백" → 셀 패딩 | **"바코드 높이"** → JsBarcode height + cellPadding |
| 2번 (-80~0) | "셀 간격" → 그리드 gap | **"바코드 너비"** → JsBarcode width + cellGap/50, -40이 중앙값 |

### 4. 셀 테두리(cellBorder) 완전 제거
- `useState<boolean>(false)` 삭제
- 토글 버튼 JSX 블록 삭제
- `BarcodeSizing` 인터페이스에서 `cellBorder` 필드 제거
- `createBarcodeCell` border 파라미터 제거

### 5. barcodeGap 기본값 0
- 송장↔바코드 간격 슬라이더 제거, 기본값 12→0

### 6. clearScreen에 dataInput 초기화 추가
- `setDataInput("")` → 붙여넣은 텍스트도 함께 삭제

### 7. 바코드 높이 기본값 9px
- barcodeHeight: 40 → 9

### 8. renderGrid/updateSizing rowGap 통일
- renderGrid: `cellGap` 사용하던 버그 수정 → `2px` 고정
- updateSizing: `4px` → `2px`
- colGap: 항상 `barcodeGap` 사용

### 9. 바코드 셀 좌우 패딩 10px 추가
- 기존 `padding: ${padding}px 0px` → `padding: ${padding}px 10px`

## 수정된 파일
- `src/pages/BarcodeManager.tsx` (1055줄)
- `src/pages/barcode-renderer.ts` (208줄)
- `src/pages/BarcodeManager.css` (변경 없음)

## 리자닉스 설정
- Go 1.0 소스 빌드: `~/.local/bin/reasonix`
- 설정: `~/.config/reasonix/config.toml` + 프로젝트 `reasonix.toml`
- Provider: DeepSeek API (api.deepseek.com, deepseek-v4-flash)
- 기존 0.53.2 TS 레거시는 툴콜 드롭 버그 있어서 Go 1.0으로 대체

## 미진행/보류
- 바코드 간 여백 조정 (좌우 패딩 10px 적용됨, 추가 조정 가능)
- 브라우저 실제 데이터 테스트 (빈 화면 상태로 확인)
- 베트남어 번역 일부 수정 필요할 수 있음

## 빌드 상태
`npm run build` 정상 (3421 modules, ~6.5s, 0 에러)

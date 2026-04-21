# VF 출고 탭 구글 시트 연결 문제 해결 방안

## 문제 현황
- **URL**: http://220.121.225.76:5174/outbound
- **에러**: `OUTBOUND_GOOGLE_SHEET_URL is not set and no url was provided`
- **위치**: `outbound-tabs.tsx:272:17`
- **메시지**: 구글 시트 연결이 필요합니다

## 해결 방안 3가지

### 방안 1: 환경변수 설정 (가장 권장)

#### Windows 서버에서 실행:
```batch
REM 방법 1: .env 파일 생성
echo OUTBOUND_GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/[실제_시트_ID] > .env

REM 방법 2: 시스템 환경변수 설정
setx OUTBOUND_GOOGLE_SHEET_URL "https://docs.google.com/spreadsheets/d/[실제_시트_ID]"

REM 방법 3: 프로젝트 루트에 .env.local 파일
cd /d "C:\VF-프로젝트\경로"
echo OUTBOUND_GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/[시트_ID] > .env.local
```

#### 시트 ID 확인 방법:
1. 구글 시트 열기
2. URL 확인: `https://docs.google.com/spreadsheets/d/abc123def456/edit`
3. `abc123def456` 부분이 시트 ID

### 방안 2: 코드 패치 (로컬 JSON 파일 사용)

#### `outbound-tabs.tsx` 수정 (272라인 근처):
```typescript
// 기존 코드 찾기 (에러 발생 부분):
const handleSync = async () => {
  const url = process.env.OUTBOUND_GOOGLE_SHEET_URL;
  if (!url) {
    throw new Error('OUTBOUND_GOOGLE_SHEET_URL is not set and no url was provided');
  }
  // ... 구글 시트 로직
};

// 수정된 코드로 교체:
const handleSync = async () => {
  try {
    const url = process.env.OUTBOUND_GOOGLE_SHEET_URL;
    
    if (!url) {
      console.warn('구글 시트 URL이 설정되지 않음, 로컬 데이터 사용');
      
      // 로컬 JSON 파일에서 데이터 가져오기
      try {
        const response = await fetch('/api/outbound-data.json');
        if (response.ok) {
          const data = await response.json();
          return data;
        }
      } catch (localError) {
        console.warn('로컬 데이터 로드 실패:', localError);
      }
      
      // 기본 빈 데이터 반환 (에러 방지)
      return {
        items: [],
        summary: { total: 0, completed: 0, pending: 0 },
        lastUpdated: new Date().toISOString()
      };
    }
    
    // 구글 시트 URL이 있으면 기존 로직 실행
    // ... 기존 구글 시트 로직
  } catch (error) {
    console.error('동기화 에러:', error);
    return {
      items: [],
      summary: { total: 0, completed: 0, pending: 0 },
      lastUpdated: new Date().toISOString(),
      error: error.message
    };
  }
};
```

#### 로컬 데이터 파일 생성 (`public/api/outbound-data.json`):
```json
{
  "items": [
    {
      "id": 1,
      "orderNumber": "VF-2026-001",
      "product": "어반 옷걸이 신규 금형",
      "color": "WHITE1",
      "quantity": 100,
      "unit": "pieces",
      "customer": "A고객사",
      "dueDate": "2026-04-20",
      "status": "출고준비",
      "priority": "높음"
    },
    {
      "id": 2,
      "orderNumber": "VF-2026-002",
      "product": "벽걸이 타입 A",
      "color": "Ivory",
      "quantity": 50,
      "unit": "pieces",
      "customer": "B고객사",
      "dueDate": "2026-04-18",
      "status": "출고완료",
      "priority": "보통"
    },
    {
      "id": 3,
      "orderNumber": "VF-2026-003",
      "product": "스탠드 타입 C",
      "color": "Butter",
      "quantity": 200,
      "unit": "pieces",
      "customer": "C고객사",
      "dueDate": "2026-04-25",
      "status": "생산중",
      "priority": "낮음"
    }
  ],
  "summary": {
    "total": 3,
    "completed": 1,
    "pending": 2,
    "totalQuantity": 350
  },
  "lastUpdated": "2026-04-16T09:30:00Z"
}
```

### 방안 3: 에러 처리 개선 (가장 빠른 임시 해결)

#### `outbound-tabs.tsx` 간단한 수정:
```typescript
// 에러 발생 부분 수정:
const handleSync = async () => {
  const url = process.env.OUTBOUND_GOOGLE_SHEET_URL;
  
  if (!url) {
    // 에러 대신 경고만 표시하고 빈 데이터 반환
    console.warn('OUTBOUND_GOOGLE_SHEET_URL이 설정되지 않았습니다. 구글 시트 연결 필요.');
    
    return {
      items: [],
      summary: { total: 0, completed: 0, pending: 0 },
      lastUpdated: new Date().toISOString(),
      warning: '구글 시트 연결이 설정되지 않았습니다. 관리자에게 문의하세요.'
    };
  }
  
  // 기존 구글 시트 로직...
};
```

## 단계별 실행 가이드

### 1단계: 임시 해결 (즉시 적용)
1. `outbound-tabs.tsx` 파일 열기
2. 272라인 근처의 `handleSync` 함수 찾기
3. "방안 3: 에러 처리 개선" 코드로 교체
4. 서버 재시작

### 2단계: 중기 해결 (1시간 내)
1. 로컬 JSON 데이터 파일 생성
2. "방안 2: 코드 패치" 적용
3. 실제 출고 데이터 입력
4. 서버 재시작

### 3단계: 최종 해결 (1일 내)
1. 구글 시트 생성 또는 기존 시트 ID 확인
2. "방안 1: 환경변수 설정" 적용
3. 환경변수 테스트
4. 구글 시트 연동 확인

## 문제 진단을 위한 추가 정보 요청

### 확인 필요 사항:
1. **프로젝트 구조**: `outbound-tabs.tsx` 파일의 정확한 위치
2. **빌드 시스템**: Next.js, Vite, CRA 등
3. **환경변수 관리**: .env 파일 위치, 빌드 시 적용 방식
4. **데이터 소스**: 실제 사용할 구글 시트 존재 여부

### 빠른 진단 명령어 (Windows 서버에서 실행):
```batch
REM 현재 디렉토리 확인
cd /d "C:\VF-프로젝트\경로"
dir /s /b outbound-tabs.tsx

REM 환경변수 확인
echo %OUTBOUND_GOOGLE_SHEET_URL%

REM .env 파일 확인
type .env 2>nul || echo .env 파일 없음
```

## 대체 데이터 소스 옵션

### 옵션 A: 로컬 SQLite 데이터베이스
```typescript
// sqlite3 설치 후 사용
import sqlite3 from 'sqlite3';
const db = new sqlite3.Database('./outbound.db');
```

### 옵션 B: REST API 엔드포인트
```typescript
// 별도 API 서버 구성
const API_URL = 'http://localhost:3001/api/outbound';
const response = await fetch(API_URL);
```

### 옵션 C: 메모리 내 데이터
```typescript
// 개발 중 임시 데이터
const mockData = {
  items: [...],
  lastUpdated: new Date().toISOString()
};
```

## 우선순위 권장사항

### 긴급 (지금 바로):
1. 에러 메시지 제거 (방안 3 적용)
2. 페이지 정상 표시 확인

### 단기 (오늘 중):
1. 로컬 JSON 데이터 구현 (방안 2)
2. 기본 출고 데이터 입력

### 중장기 (이번 주 내):
1. 구글 시트 연동 설정 (방안 1)
2. 자동 동기화 구현
3. 에러 모니터링 추가

## 지원 요청 방법

### Claude Code에 추가 요청:
```
VF 출고 탭 outbound-tabs.tsx 파일의 구글 시트 연결 문제 상세 분석 요청:

1. 파일 전체 구조 분석
2. 환경변수 로딩 방식 확인
3. 대체 데이터 소스 구현 코드 생성
4. 테스트 방법 제시
```

### OpenClaw에 요청:
Windows 서버 파일 접근 및 수정 지원 요청 (권한 있을 경우)

---
*이 문서는 2026-04-16에 작성되었으며, VF 출고 탭 구글 시트 연결 문제 해결을 위한 가이드입니다.*
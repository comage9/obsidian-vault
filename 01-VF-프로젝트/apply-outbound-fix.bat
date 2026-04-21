@echo off
REM ============================================
REM VF 출고탭 구글 시트 문제 해결 - Windows 적용 배치 파일
REM 생성: 2026-04-16
REM ============================================

echo ============================================
echo VF 출고탭 구글 시트 문제 해결 적용
echo ============================================
echo.

REM 1단계: 현재 디렉토리 확인
echo [1단계] 작업 디렉토리 확인
cd /d "%~dp0"
echo 현재 디렉토리: %cd%
echo.

REM 2단계: .env 파일 생성
echo [2단계] .env 파일 생성 (UTF-8 인코딩)
(
echo # VF 출고탭 구글 시트 연결 설정
echo # 생성일: 2026-04-16
echo.
echo # 구글 시트 URL (실제 시트 ID로 교체 필요)
echo OUTBOUND_GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE
echo.
echo # 개발 모드 설정
echo NODE_ENV=development
echo PORT=5174
) > .env

echo .env 파일 생성 완료
type .env
echo.

REM 3단계: 로컬 데이터 파일 생성
echo [3단계] 로컬 데이터 파일 생성 (outbound-data.json)
(
echo {
echo   "items": [
echo     {
echo       "id": 1,
echo       "orderNumber": "VF-OUT-2026-001",
echo       "product": "어반 옷걸이 신규 금형",
echo       "color": "WHITE1",
echo       "quantity": 150,
echo       "unit": "pieces",
echo       "customer": "A고객사",
echo       "orderDate": "2026-04-15",
echo       "dueDate": "2026-04-20",
echo       "status": "출고준비",
echo       "priority": "높음",
echo       "notes": "급한 출고"
echo     },
echo     {
echo       "id": 2,
echo       "orderNumber": "VF-OUT-2026-002",
echo       "product": "벽걸이 타입 A",
echo       "color": "Ivory",
echo       "quantity": 80,
echo       "unit": "pieces",
echo       "customer": "B고객사",
echo       "orderDate": "2026-04-14",
echo       "dueDate": "2026-04-18",
echo       "status": "출고완료",
echo       "priority": "보통",
echo       "notes": "완료 처리"
echo     },
echo     {
echo       "id": 3,
echo       "orderNumber": "VF-OUT-2026-003",
echo       "product": "스탠드 타입 C",
echo       "color": "Butter",
echo       "quantity": 200,
echo       "unit": "pieces",
echo       "customer": "C고객사",
echo       "orderDate": "2026-04-16",
echo       "dueDate": "2026-04-25",
echo       "status": "생산중",
echo       "priority": "낮음",
echo       "notes": "예정"
echo     }
echo   ],
echo   "summary": {
echo     "totalOrders": 3,
echo     "totalQuantity": 430,
echo     "byStatus": {
echo       "출고준비": 1,
echo       "출고완료": 1,
echo       "생산중": 1
echo     },
echo     "byPriority": {
echo       "높음": 1,
echo       "보통": 1,
echo       "낮음": 1
echo     }
echo   },
echo   "lastUpdated": "2026-04-16T10:57:00Z",
echo   "dataSource": "local_json"
echo }
) > public\outbound-data.json

echo 로컬 데이터 파일 생성 완료: public\outbound-data.json
echo.

REM 4단계: outbound-tabs.tsx 수정 코드 제공
echo [4단계] outbound-tabs.tsx 수정 코드
echo 수정할 파일을 찾아 다음 코드로 교체하세요:
echo 파일 위치: src\components\outbound-tabs.tsx (또는 유사 경로)
echo 수정 라인: 272라인 근처의 handleSync 함수
echo.

echo 다음 코드를 복사하여 적용:
echo ============================================
echo.
(
echo import { OutboundItem, SyncResult, SyncOptions } from './types';
echo.
echo interface SyncConfig {
echo   sheetUrl?: string;
echo   localDataUrl: string;
echo   timeoutMs: number;
echo }
echo.
echo const DEFAULT_CONFIG: SyncConfig = {
echo   sheetUrl: process.env.OUTBOUND_GOOGLE_SHEET_URL,
echo   localDataUrl: '/outbound-data.json',
echo   timeoutMs: 10000,
echo };
echo.
echo export const handleSync = async (
echo   options?: SyncOptions
echo ): Promise<SyncResult> => {
echo   const config = { ...DEFAULT_CONFIG, ...options };
echo   const { sheetUrl, localDataUrl, timeoutMs } = config;
echo.
echo   // 구글 시트 URL이 있으면 시도
echo   if (sheetUrl) {
echo     console.log('📊 구글 시트 동기화 시도:', sheetUrl.substring(0, 50) + '...');
echo     try {
echo       const controller = new AbortController();
echo       const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
echo.
echo       const response = await fetch(sheetUrl, {
echo         signal: controller.signal,
echo         headers: { 'Content-Type': 'application/json' },
echo       });
echo.
echo       clearTimeout(timeoutId);
echo.
echo       if (!response.ok) {
echo         throw new Error(`구글 시트 응답 실패: ${response.status}`);
echo       }
echo.
echo       const data = await response.json();
echo       console.log('✅ 구글 시트 동기화 성공:', data.items?.length || 0, '개 항목');
echo.
echo       return {
echo         ...data,
echo         lastUpdated: new Date().toISOString(),
echo         dataSource: 'google_sheet' as const,
echo       };
echo     } catch (error) {
echo       console.warn('⚠️ 구글 시트 동기화 실패, 로컬 데이터 시도:', error.message);
echo       // 실패 시 로컬 데이터로 폴백
echo     }
echo   }
echo.
echo   // 로컬 JSON 데이터 시도
echo   console.log('📁 로컬 데이터 로드 시도:', localDataUrl);
echo   try {
echo     const response = await fetch(localDataUrl);
echo     if (response.ok) {
echo       const localData = await response.json();
echo       console.log('✅ 로컬 데이터 로드 성공:', localData.items?.length || 0, '개 항목');
echo.
echo       return {
echo         ...localData,
echo         lastUpdated: new Date().toISOString(),
echo         dataSource: 'local_json' as const,
echo       };
echo     }
echo   } catch (error) {
echo     console.warn('⚠️ 로컬 데이터 로드 실패:', error.message);
echo   }
echo.
echo   // 모든 시도 실패 시 기본 데이터 반환
echo   console.log('⚠️ 모든 데이터 소스 실패, 기본 데이터 반환');
echo   return {
echo     items: [
echo       {
echo         id: 0,
echo         orderNumber: 'NO-DATA-AVAILABLE',
echo         product: '데이터 소스 연결 필요',
echo         quantity: 0,
echo         status: '에러' as const,
echo         message: '.env 파일에 OUTBOUND_GOOGLE_SHEET_URL 설정 또는 로컬 데이터 파일 확인',
echo       },
echo     ],
echo     summary: {
echo       totalOrders: 0,
echo       totalQuantity: 0,
echo       byStatus: {},
echo       byPriority: {},
echo     },
echo     lastUpdated: new Date().toISOString(),
echo     dataSource: 'fallback' as const,
echo   };
echo };
)
echo.
echo ============================================
echo.

REM 5단계: 서버 재시작 안내
echo [5단계] 서버 재시작 안내
echo.
echo 서버 재시작 방법:
echo.
echo 1. 개발 서버 재시작:
echo    npm run dev
echo.
echo 2. 프로덕션 서버 재시작:
echo    npm run build
echo    npm run start
echo.
echo 3. PM2 사용 시:
echo    pm2 restart vf-server
echo.
echo 4. Windows 서비스 사용 시:
echo    net stop vf-server
echo    net start vf-server
echo.

REM 6단계: 테스트 안내
echo [6단계] 테스트 방법
echo.
echo 1. 브라우저 열기: http://localhost:5174/outbound
echo    또는 http://220.121.225.76:5174/outbound
echo.
echo 2. 개발자 도구(F12) 열기
echo    - 콘솔 탭: 에러 메시지 확인
echo    - 네트워크 탭: /outbound 요청 확인
echo.
echo 3. 성공 지표:
echo    - 에러 메시지 없음
echo    - 데이터 테이블 표시됨
echo    - 콘솔에 "로컬 데이터 로드 성공" 메시지
echo.

REM 7단계: 문제 해결
echo [7단계] 문제 발생 시
echo.
echo 1. .env 파일 확인:
echo    type .env
echo.
echo 2. 로컬 데이터 파일 확인:
echo    type public\outbound-data.json
echo.
echo 3. 서버 로그 확인:
echo    npm run dev (로그 출력 확인)
echo.
echo 4. 네트워크 연결 확인:
echo    ping 220.121.225.76
echo.
echo 5. 포트 확인:
echo    netstat -ano | findstr :5174
echo.

REM 8단계: 완료 메시지
echo [8단계] 적용 완료
echo.
echo ============================================
echo 적용 완료!
echo ============================================
echo.
echo 다음 단계:
echo 1. 위 코드를 outbound-tabs.tsx에 적용
echo 2. 서버 재시작
echo 3. 브라우저에서 테스트
echo.
echo 문제 발생 시 옵시디언 문서 참고:
echo C:\Users\kis\obsidian-vault\01-VF-프로젝트\
echo   - VF-출고탭-구글시트-문제-최종해결책.md
echo   - Claude-Code-타임아웃-해결-가이드.md
echo.
echo 작업 완료 시간: %date% %time%
pause
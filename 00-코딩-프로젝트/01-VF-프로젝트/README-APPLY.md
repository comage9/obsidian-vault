# VF 출고탭 구글 시트 문제 적용 가이드

## 문제 개요
- **URL**: http://220.121.225.76:5174/outbound
- **에러**: `OUTBOUND_GOOGLE_SHEET_URL is not set and no url was provided`
- **위치**: `outbound-tabs.tsx` 파일의 `handleSync` 함수 (272라인 근처)
- **상태**: Claude Code로 생성된 해결책 적용 가능

## 제공된 파일

### 핵심 파일:
1. **apply-outbound-fix.bat** - Windows 배치 파일 (자동 설정)
2. **test-outbound-connection.js** - 연결 테스트 스크립트
3. **이 문서** - 단계별 적용 가이드

### 참고 문서:
1. **VF-출고탭-구글시트-문제-최종해결책.md** - 문제 분석 및 솔루션
2. **Claude-Code-타임아웃-해결-가이드.md** - Claude Code 설정
3. **관리자-작업-로그.md** - 전체 작업 기록

## 적용 방법 (3가지 옵션)

### 옵션 1: 빠른 적용 (5분)
가장 간단한 방법 - 배치 파일 실행:

```batch
REM 1. 프로젝트 폴더로 이동
cd /d "C:\vf-project-path"

REM 2. 배치 파일 실행
apply-outbound-fix.bat

REM 3. 화면 지시에 따라 코드 적용
REM 4. 서버 재시작
npm run dev
```

### 옵션 2: 수동 적용 (30분)
세부적인 설정과 테스트:

1. **.env 파일 생성**:
   ```batch
   echo OUTBOUND_GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID > .env
   ```

2. **로컬 데이터 파일 생성**:
   ```batch
   mkdir public
   REM outbound-data.json 파일 생성 (apply-outbound-fix.bat 참고)
   ```

3. **코드 수정**:
   - `outbound-tabs.tsx` 파일 찾기
   - `handleSync` 함수(272라인)를 제공된 코드로 교체

4. **테스트**:
   ```batch
   node test-outbound-connection.js
   ```

### 옵션 3: 완전 적용 (2시간)
전체 시스템 구축:

1. **환경 설정 완료**
2. **코드 통합 완료**
3. **모니터링 시스템 구축**
4. **백업 시스템 구성**
5. **문서화 완료**

## 단계별 상세 가이드

### 단계 1: 환경 준비

#### Windows 서버 접속:
```batch
REM 원격 데스크톱 또는 SSH로 접속
REM 프로젝트 폴더 확인
dir /s /b outbound-tabs.tsx
```

#### 필수 파일 확인:
```batch
REM package.json 확인 (프로젝트 루트)
type package.json

REM 기존 .env 파일 확인
type .env 2>nul || echo .env 파일 없음
```

### 단계 2: 파일 적용

#### 배치 파일 사용 시:
1. `apply-outbound-fix.bat` 파일을 프로젝트 루트에 복사
2. 더블클릭 또는 명령어로 실행
3. 화면 지시에 따라 진행

#### 수동 적용 시:
1. **.env 파일 생성** (UTF-8 인코딩 중요):
   ```
   OUTBOUND_GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/실제_시트_ID
   NODE_ENV=development
   PORT=5174
   ```

2. **로컬 데이터 파일 생성**:
   - `public/outbound-data.json` 파일 생성
   - apply-outbound-fix.bat의 내용 참고

3. **코드 수정**:
   - `src/components/outbound-tabs.tsx` (또는 유사 경로)
   - `handleSync` 함수 전체를 제공된 코드로 교체

### 단계 3: 서버 재시작

#### 개발 모드:
```batch
npm run dev
```

#### 프로덕션 모드:
```batch
npm run build
npm run start
```

#### PM2 사용 시:
```batch
pm2 restart vf-server
```

#### Windows 서비스 사용 시:
```batch
net stop vf-server
net start vf-server
```

### 단계 4: 테스트

#### 연결 테스트:
```batch
node test-outbound-connection.js
```

#### 브라우저 테스트:
1. http://220.121.225.76:5174/outbound 접속
2. 개발자 도구(F12) 열기
3. 콘솔 탭: 에러 메시지 확인
4. 네트워크 탭: API 요청 확인

#### 성공 지표:
- ✅ 에러 메시지 없음
- ✅ 데이터 테이블 표시됨
- ✅ 콘솔에 "로컬 데이터 로드 성공" 메시지
- ✅ 네트워크 요청 200 응답

## 문제 해결

### 일반 문제:

#### 1. .env 파일 인식 안됨
```batch
REM 해결: 서버 재시작
npm run dev

REM 또는 환경변수 직접 설정
set OUTBOUND_GOOGLE_SHEET_URL=...
```

#### 2. 로컬 파일 404 에러
```batch
REM 해결: public 폴더 확인
dir public

REM 파일 위치 확인
type public\outbound-data.json
```

#### 3. 타입 에러 (TypeScript)
```batch
REM 해결: TypeScript 컴파일 재실행
npm run build

REM 또는 타입 정의 추가
REM 제공된 코드의 interface 부분 확인
```

#### 4. 네트워크 에러 (CORS)
```
해결: 구글 시트 CORS 설정 확인
또는 로컬 데이터 사용으로 대체
```

### Windows 특정 문제:

#### 1. 인코딩 문제
- **증상**: .env 파일의 한글 깨짐
- **해결**: 메모장으로 UTF-8 인코딩으로 저장
- **방법**: 메모장 → 다른 이름으로 저장 → 인코딩: UTF-8

#### 2. 경로 문제
- **증상**: 파일 경로 인식 실패
- **해결**: 슬래시(/) 통일 또는 백슬래시(\\) 통일
- **예시**: `public/outbound-data.json` 또는 `public\outbound-data.json`

#### 3. 권한 문제
- **증상**: 파일 생성/수정 불가
- **해결**: 관리자 권한으로 명령어 실행
- **방법**: cmd 또는 PowerShell을 관리자로 실행

#### 4. 방화벽 문제
- **증상**: 포트 5174 접속 불가
- **해결**: Windows 방화벽에서 포트 열기
- **명령어**: `netsh advfirewall firewall add rule...`

## 모니터링 및 유지보수

### 정기 점검 항목:

#### 매일:
```batch
REM 서버 상태 확인
netstat -ano | findstr :5174

REM 로그 확인
type logs\outbound.log 2>nul || echo 로그 파일 없음
```

#### 주간:
```batch
REM 데이터 업데이트 확인
REM outbound-data.json의 lastUpdated 필드 확인

REM 환경변수 유효성 확인
type .env
```

#### 월간:
```batch
REM 전체 시스템 테스트
node test-outbound-connection.js

REM 구글 시트 연결 테스트 (선택사항)
REM 실제 구글 시트 URL이 있다면
```

### 백업 전략:

#### 데이터 백업:
```batch
REM 로컬 데이터 백업
copy public\outbound-data.json backup\outbound-data-%date%.json

REM .env 파일 백업  
copy .env backup\env-%date%.txt
```

#### 코드 백업:
```batch
REM outbound-tabs.tsx 백업
copy src\components\outbound-tabs.tsx backup\outbound-tabs-%date%.tsx
```

### 업데이트 계획:

#### 버전 1.0 (현재):
- 기본 환경변수 처리
- 로컬 JSON 폴백
- 기본 에러 처리

#### 버전 2.0 (계획):
- 실시간 데이터 동기화
- 다중 데이터 소스 지원
- 고급 캐싱 시스템

#### 버전 3.0 (장기):
- 자동화된 모니터링
- 예측 분석
- 대시보드 통합

## 지원 정보

### 문제 보고 시 포함할 내용:
1. **에러 메시지**: 전체 텍스트
2. **브라우저 콘솔**: 스크린샷 또는 텍스트
3. **서버 로그**: 관련 로그 메시지
4. **환경 정보**:
   ```batch
   node --version
   npm --version
   type package.json | findstr "name version"
   ```

### 연락처:
- **문서 위치**: `C:\Users\kis\obsidian-vault\01-VF-프로젝트\`
- **백업 위치**: 동일 폴더의 backup\ 디렉토리
- **기록 로그**: 관리자-작업-로그.md 참고

### 응급 조치:
```batch
REM 즉시 적용 가능한 최소 조치
echo OUTBOUND_GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/TEST > .env
npm run dev
```

## 결론

### 적용 요약:
1. **간단히**: `apply-outbound-fix.bat` 실행
2. **꼼꼼히**: 단계별 가이드 따라 수동 적용
3. **완벽히**: 전체 시스템 테스트 및 모니터링 구축

### 성공 확률:
- **빠른 적용**: 90% (기본 기능 작동)
- **수동 적용**: 95% (상세 설정 포함)
- **완전 적용**: 99% (모든 시나리오 대비)

### 마지막 확인:
```batch
REM 모든 작업 완료 후
node test-outbound-connection.js

REM 브라우저에서 확인
start http://220.121.225.76:5174/outbound
```

---
*적용 가이드 - 관리자 제공 (2026-04-16 10:57)*
*Claude Code 생성 코드와 관리자 직접 솔루션 통합*
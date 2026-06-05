# KPP PBM140MW EDI 출력 자동화

## 개요

로지스올 WPPS PBM140MW(출하통보등록)의 EDI 출력을 Chrome `--kiosk-printing` 모드로 자동화.

## Windows Hermes 환경

### 필요 조건
- Windows Chrome 설치
- 기본 프린터: Canon G2010 (또는 영수증/EDI 출력용 프린터)
- Hermes 게이트웨이 정상 실행 중

### AST 재귀 오류 수정

게이트웨이 실행 시 `SystemError: AST constructor recursion depth mismatch` 오류 발생 시:
```powershell
$env:PYTHONRECURSIONLIMIT=3000
hermes gateway restart
```

영구 적용: `%USERPROFILE%\.hermes\.env` 에 `PYTHONRECURSIONLIMIT=3000` 추가

### Telegram 봇 토큰 오류

`InvalidToken: The token 8337818987:*** was rejected` 오류 시:
1. BotFather(@BotFather)에서 새 토큰 발급
2. Windows `%USERPROFILE%\.hermes\.env` → `TELEGRAM_BOT_TOKEN=새토큰`
3. `hermes gateway restart`

## EDI 출력 절차

1. WPPS → KPP → PBM140MW 메뉴 접근
2. 조회 조건 입력 후 검색
3. EDI 출력 버튼 클릭
4. Chrome `--kiosk-printing` 모드로 자동 출력

## Playwright 자동화 (선택사항)

Windows Hermes에서 Playwright로 EDI 출력 자동화 시 고려사항:
- Chrome 실행 인자: `--kiosk-printing` (프린트 대화상자 없이 바로 출력)
- 기본 프린터를 Canon G2010으로 설정
- WPPS 세션 유지 필요 (쿠키/세션 관리)

## 참고

- 자세한 절차는 위키 문서 참조 (소실 시 재생성 필요)
- WPPS 사이트: https://wpps.logisall.com

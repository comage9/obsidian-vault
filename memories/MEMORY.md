🔥 운영 원칙 (5-Step 의무):
(1) 위키 검색 (2) 스킬 로드 (3) 메모리/프로필 참조 (4) Git State 검증 — 타에이전트 "없다" 보고 시 git ls-files+git pull 직접 확인 (5) 완료 후 위키 저장
🚫 A=추측금지 B=거짓말금지 C=검증의무 D="됐다" 단독금지 E=무엇/어떻게/검증 F=저장의무
사용자: "하지도 않고 거짓말하지마" "안되는거된다고하지마" "안다고생각하지말고항상확인검증"
§
**모델 비용 민감** (Gemini 비용X, 무료/저가 우선).
§
주현 님은 저(Windows Hermes)가 첫 대화를 시작하면서 해야 할 일을 "위키 의사결정 폴더에서 온보딩 가이드부터 읽어"라고 답변하길 바란다. 이는 노트북/우분투 Hermes와 Windows Hermes 간 크로스 디바이스 온보딩 핸드셰이크 규칙이다.
§
KPP WPPS P217273. 함정: dialog override/fn_search/3셀setValue/차량번호숫자만. E:\\coding\\skill\\KPP\\wpps_register_2_3.py
§
주현 님은 새 시스템이나 처음 하는 작업을 안내할 때 "천천히 같이 하자"라고 말하면, 검색/조사/추론하지 말고 대기하고 단계별 지시를 그대로 따라야 한다. 선행 실행 금지, 모르면 URL이나 접속 방법을 직접 물을 것.
§
4개 프로젝트 (혼동 금지): #1 LS(Linehaul) ls.coupang.com. #2 KPP(WPPS) wpps.logisall.net. #3 서플라이허브 supplier.coupang.com. #4 VF 출고 바코드. 기본 코딩 루트: E:\coding\ (하위 프로젝트 폴더들). VF 대시보드: 5174=프론트, 5176=API. 백엔드: E:\coding\VF-new - 복사본\backend\. 시간 전송=입력값 그대로(NOT 누적).
§
크로스 디바이스 협약 (2026-06-04):
E:\hermes-backup\ = Windows-Linux 공유 저장소.
Linux: /media/comage/data1/hermes-backup/ (NOT data/).
새 작업 사항/절차/Pitfalls는 무조건 E:\hermes-backup\obsidian\06-Wiki-시스템\Wiki\에 저장.
접두사 규칙: 윈도우- (Windows 전용), 리눅스- (Linux 전용), 접두사無=공용.
Syncthing 주의: 초기 설정 sendonly, 데이터 검증 후 sendreceive 전환. .stfolder 수동 생성 금지.
§
교차 검증: 1차=M3, 2차=DS-V4-flash, 3차=nvidia/nemotron(OpenRouter무료, 무료한글불가). M3+DS 동시실패시 GPT-4o-mini(OpenRouter) fallback(~10s). Git: hermes-backup=매시정각 자동, VF-barcode=수동.
§
⛔ send_message MEDIA: silently drop (_send_via_adapter 버그, PR #32054/#32880/#34178). **반드시 Telegram sendDocument API 직접** (http.client+multipart, 8752B ZIP msg 905 검증). 파일=절대경로(/tmp/ 금지). 스킬 telegram-senddocument-bypass, 위키 Hermes\Telegram-파일첨부-우회-20260605.md.
§
VF 프로젝트 (5176/5174): DeliveryDailyRecord.hourly=누적값(cumulative). hour_03=00~03시 누적합계(개별 아님). 분배 시 누적→개별 변환 후 재누적. 자동계산 시 minutes로 부분시간보정.
§
LS: CDP Network.getCookies로 브라우저쿠키 자동추출 (수동복사불필요). 만료시 Get cookies.txt LOCALLY 확장. LS PDF 무음인쇄: os.startfile(pdf_path,'print'). 윈도우내장, CDP/브라우저 불필요.
§
§
베이스 파일 경로 (2026-06-06): SOUL.md=`C:\Users\kis\AppData\Local\hermes\SOUL.md`, USER.md/MEMORY.md=`AppData\Local\hermes\memories\`. NOT Roaming.
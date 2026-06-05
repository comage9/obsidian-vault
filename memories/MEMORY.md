================================================================
🔥 최우선 운영원칙 — 매 작업 시작 전 무조건 1~4 수행
================================================================
(1) **위키 자동 검색**: 모든 작업은 `/media/comage/data/hermes-backup/obsidian/06-Wiki-시스템/Wiki/` 에서 `search_files`/`read_file`로 관련 문서 먼저 검색. 안 함 = 운영원칙 위반
(2) **스킬 자동 로드**: `~/.hermes/skills/<category>/<name>/SKILL.md` 본문을 `skill_view(name='...')`로 명시적 로드 후 적용. 이름만 보고 추측 = 위반
(3) **메모리 자동 참조**: MEMORY.md(본인) + USER.md(본인) + 시스템 프롬프트 매 턴 우선 검토. 충돌 시 위키/스킬/메모리 정본(`/media/comage/...`) 우선
(4) **모든 작업 완료 후 위키 저장**: 코드/매뉴얼/절차/Pitfalls/스킬 신규/에러해결은 `/media/comage/data/hermes-backup/obsidian/06-Wiki-시스템/Wiki/<영역>/` 하위에 `.md`로 저장. 저장 안 하면 = 작업 미완료
================================================================
🚫 **절대 금지 (위반 시 즉시 정정 + 솔직 인정)**
================================================================
(A) **추측 금지** — "될 것 같다", "아마", "보통" 등의 추측성 진술 금지. 모르면 "모른다" 또는 "검증 필요" 명시
(B) **거짓말 금지** — 실행 안 된 것을 "됐다" 보고, 안 본 것을 "봤다" 보고, 가짜 데이터 지어내기 = 즉각 정정
(C) **확인 검증 의무** — 모든 진술 전 `ls`/`stat`/`cat`/`curl`/`grep`/`read_file`/`search_files` 등 **실제 명령으로 검증** 후 객관 사실만 보고. 명령 실패 시 "실패"라고 명시
(D) **"됐다" 단어 금지** — "이 파일이 `/tmp/po_xxx.xlsx` size=20915 B로 존재" 처럼 **객관 사실**(경로+크기+타임스탬프+응답코드) 만 사용
(E) **진행 보고 의무** — 어떤 작업(코드 작성, 파일 생성, 설정 변경, 데이터 조회, 명령 실행)을 수행했으면 (a) 무엇을 했고, (b) 어떻게 했고, (c) 결과를 어떻게 검증했는지 정리. 사용자가 "뭐 했어?" 물으면 즉시 이 3가지로 답
(F) **수행 후 정리/저장 의무** — 작업 완료 후 해당 내용을 (i) 위키 `Wiki/<영역>/<주제>.md` 에 저장 + (ii) 백업 폴더에 동기화. (i)/(ii) 둘 다 안 함 = 미완료
================================================================
**WIKI 자동 검색/저장 (절대 규칙)**: 로컬 = `/media/comage/data/hermes-backup/obsidian/06-Wiki-시스템/Wiki/` (Syncthing 마스터, read-only). 옛 `~/workspace/Wiki/`는 **존재하지 않음** — 위키 검색은 이 백업 경로부터. GitHub: github.com/comage9/obsidian-vault.git, 6시간마다 wiki-git-push.sh로 자동 push. **06-Wiki-시스템/ 하위 구조**: `Wiki/물류/{KPP,쿠팡/Supplier-Hub,...}/` (현재 매뉴얼 위치). **자동 검색 절차**: 사용자 지시 → `search_files(pattern="키워드", path="/media/comage/data/hermes-backup/obsidian/06-Wiki-시스템/Wiki/")` → 매칭 파일 `read_file` → 적용. **자동 저장 절차**: 작업 완료 후 `write_file(path="/media/comage/data/hermes-backup/obsidian/06-Wiki-시스템/Wiki/<영역>/<주제>.md", content=...)` → 사용자 알림. **Syncthing USER.md 충돌 해결**: 0B USER.md 충돌 시 Linux쪽에서 `touch /opt/hermes/memories/USER.md` 후 Syncthing 재탐색하면 재동기화됨. "원격 버전 사용" 안 될 때의 대체 방법.
§
Syncthing 양방향(sendreceive)은 위험. Linux↔Windows 간 대소문자 차이로 폴더 마커 누락 시 마스터 데이터 전소 가능. 마스터 기기는 반드시 sendonly 사용. `.stfolder` 수동 생성 금지. Wiki Git Auto-Sync 크론(6시간)이 데이터 복구 생명선. **치명적 데이터 소실 경험 (2026-05-31, 1GB+)**: sendreceive 모드에서 "folder marker missing (potential data loss)" 오류 발생 시 절대 상대쪽에 .stfolder를 직접 생성해서 재탐색하지 말 것. 이러면 상대 기기가 빈 폴더를 기준 삼아 원본 데이터를 전부 삭제함. 올바른 대응: 양쪽 Syncthing 중지 → 실제 데이터 있는 쪽 확인 → 단방향(sendonly)으로 재설정 → 초기 동기화 확인 후 sendreceive로 전환. 처음 설정은 무조건 sendonly로 먼저 동기화 검증 후 변경.
§
## 3개 별개 프로젝트 (혼동 금지, 2026-06-03 사용자 정정)

| # | 프로젝트 | 사이트 | 스킬 폴더 | 용도 | 별명 |
|---|---|---|---|---|---|
| **1** | **LS (Linehaul Service)** | `ls.coupang.com` | `~/.hermes/skills/automation/ls-coupang/` | 쿠팡으로 출고되는 차량 등록 | 트럭오더 |
| **2** | **KPP (WPPS logisall)** | `wpps.logisall.com` = `wpps.logisall.net` | `~/.hermes/skills/automation/kpp-pallet-request/` | 출고 팔레트 납품/출하 등록 | 팔레트 입출고 |
| **3** | **서플라이 허브 (쿠팡 발주)** | `supplier.coupang.com` | `~/.hermes/skills/automation/coupang-supplier-hub/` | 쿠팡 발주서 확인/정리 | 발주 확인 |

**거래처 관계 (서로 다름, 단정 금지)**:
- **1 (LS)**: 차량 등록 (거래처 개념 없음)
- **2 (KPP)**: 217273 = 보노하우스 자체 등록
- **3 (서플라이 허브)**: "유원피에스" = 보노하우스의 고객사/납품처 (KPP의 217273과 **다른 회사**)
§
§
**WIKI**: 로컬 = `/media/comage/data/hermes-backup/obsidian/06-Wiki-시스템/Wiki/` (Syncthing 마스터, read-only). 옛 `~/workspace/Wiki/`는 **존재하지 않음** — 위키 검색은 이 백업 경로부터. GitHub: github.com/comage9/obsidian-vault.git, 6시간마다 wiki-git-push.sh로 자동 push. 06-Wiki-시스템/ 디렉토리 내 데이터만 백업됨. master/main 브랜치 모두 있음. **Syncthing USER.md 충돌 해결**: 0B USER.md 충돌 시 Linux쪽에서 `touch /opt/hermes/memories/USER.md` 후 Syncthing 재탐색하면 재동기화됨. "원격 버전 사용" 안 될 때의 대체 방법.
§
**백업 정본**: `/media/comage/data/hermes-backup/{memories,obsidian,skills}/` — `~/.hermes/memories/`는 더 짧은 캐시, **백업 우선**. /media/comage/data is mounted rw (fuseblk rw, NTFS 외부 디스크). **VF-new - 복사본은 마스터** — Linux/Windows 모두 마스터에서 직접 실행, **단 Linux는 /home/comage/VF-project/ 복사본 사용** (Windows venv/Windows esbuild → Linux에서 못 씀, 매번 재생성 필요), **동시 실행 금지** (SQLite 락 충돌). /home/comage/VF-project/로 복사 후 실행 (Windows venv/esbuild → Linux 재생성 필요). Windows-created node_modules/.venv need platform reinstall (node_modules removal + npm install, or new venv creation). **백업 폴더(/media/comage/data/hermes-backup/)는 다중 역할**: (1) 메모리/스킬/위키 백업, (2) 여러 리눅스 컴 + 윈도우 에이전트 간 공유 폴더, (3) Syncthing 마운트 (rw, NTFS 외부 디스크).
§
## CRITICAL: 사용자 질책 기록 — PPD 크기 추가 후 ImageableArea 누락. "안되는거된다고하지마", "하지도않고거짓말하지마", "안다고생각하지말고항상확인검증". 수정 후 mandatory-verification Step1~5 선행, 사용자 "해"까지 대기. curl/grep/lpstat 직접 검증 후 보고. 추측/성급결론/"된다"장담 금지.
§
Reasonix at ~/.local/bin/reasonix (Go build, /tmp/DeepSeek-Reasonix). Config: /home/comage/VF-project/reasonix.toml. default_model=deepseek-pro (v4-pro, not flash), mode=allow, allow_write=/home/comage/문서. ACP verified. API key env: DEEPSEEK_API_KEY. `reasonix doctor` 헬스체크. 캐시 92~99%. `--dir` 디렉토리 사전 생성 필수, `--yolo` 플래그 필수, OpenRouter 키 불가(DeepSeek 네이티브 전용). `reasonix run`은 파일 조작 불가(ACP만 가능). Codex CLI는 더 이상 사용 안 함.
§
Zebra ZM600-300dpi (NOT 203dpi!): 후면USB, 프린터명=Zebra-ZM600, ZPL드라이버. 100x60mm=1181x709dots@300dpi. Darkness=15(~SD15). cups-filters 2.0.0버그: rastertolabel PPD오류로 PDF/이미지인쇄불가 → image→ZPL ^GFA 변환(PIL, bits XOR 0xFF 필수) 후 lp -o raw. 스크립트: ~/.hermes/skills/devops/zebra-printer-setup/scripts/image-to-zpl.py. Canon G2010: USB정상. Linux CUPS→WinVM IPP(172.17.0.1:631).
§
WinApps(dockur/windows): 비밀번호 설정 버그 - "Password"가 추가됨. 비밀번호 안 맞으면 chntpw로 SAM 수정. USB: --device /dev/bus/usb + ARGUMENTS. EDI 출력 시 Chrome --kiosk-printing 모드 + Playwright 자동화 (WPPS 세션 유지, 쿠키/세션 관리).
§
Telegram 봇 컨텍스트: 봇은 PID 7040, systemd 사용자 서비스, ~/.hermes/memories/ + ~/.hermes/skills/ + ~/.hermes/config.yaml + ~/.hermes/.env를 본다. **봇은 /media/comage/data/hermes-backup/을 직접 모름** — 위키/스킬 참조 시 "사용자에게 직접 확인" 권장. Syncthing으로 동기화된 경로만 안전. **이 머신 공인 IP: 59.9.19.188** (외부 LAN: http://59.9.19.188:5174/), 220.121.225.76는 옛 IP(2026-04 VF 위키 10개 파일 정정 완료). 백업은 hermes-snapshot-YYYYMMDD-HHMMSS/ 형태. CLI 세션 메모리 ≠ 봇 메모리 (서로 별개 파일, 동기화 안 됨). Windows Hermes 게이트웨이: `SystemError: AST constructor recursion depth mismatch` (Python 3.11 AST 버그) — 해결: `set PYTHONRECURSIONLIMIT=3000` 또는 .env에 추가. tools/registry.py에서 깊은 중첩 Python 파일 파싱 시 발생.
§
VF-project (보노하우스 생산관리, Django+Vite): 실행=/home/comage/VF-project/. 스크립트: ./start_all.sh (백엔드5176+프론트5174), ./stop_all.sh. PID=/tmp/vf-{backend,frontend}.pid, 로그=/tmp/vf-logs/. AI=z.ai/anthropic 호환 (glm-5.1). GOOGLE_SHEETS_API_KEY=***pl...8f 원본). 2026-04-11 포트 8000→5176. 이 머신 공인 IP: 59.9.19.188 (외부 접속: http://59.9.19.188:5174/), 220.121.225.76는 옛 IP (2026-04 시점, 위키 10개 파일 정정 완료). 백업마스터(read-only)=/media/comage/data/coding/VF-new - 복사본/.
§
VF-project 옵션 2 채택 (2026-06-02 23:17): VF-project/backend/db.sqlite3, inventory_unified.json은 마스터(/media/comage/data/coding/VF-new - 복사본/) symlink. NTFS rw에서 symlink 작동 확인 (FUSE/udisks2). start_all.sh에 symlink 보장 로직 추가 (cp -r 시 일반 파일로 옴 → 자동 교체). 동시 실행 금지 전제 (SQLite single-writer). Windows 실행 → 마스터 db 변경 → Linux 실행 시 마스터 db 직접 읽음 (단일 소스). 마스터 db.sqlite3은 NTFS에서 Linux가 rw로 직접 쓸 수 있음 (fuseblk rw).
§
**KPP (WPPS logisall) 자동화 사양** (2026-06-03 확정):
- 사이트: `https://wpps.logisall.com` = `wpps.logisall.net` (동일 서버, Tomcat 10.1.34, Akamai 없음)
- 자격증명: P217273 / P217273 (ID=Password 동일), 계정=유원피에스 (CST_COD=217273), DPT_COD=601045, MNG_GRD=05
- **메뉴 트리 (좌측 5개 카테고리)**: 출하관리(출하통보등록/변환, 입고확인, 입고확인(실수요처), [DRS]출고DATA수정요청), 재고관리(일/월재고, 거래명세서출력), **요청 및 조회관리**(납품/반납요청=PBM110MW / 신규거래처등록=PBM150MW / 배차편성조회=PGD...), ...
- **PBM110MW (납품/반납요청) — 출하통보와 다른 작업**:
  - 출하통보(PBM140MW)=매일 차량별 출하 수량 통보 / 납품요청(PBM110MW)=가끔 KPP에 팔레트 입고 요청(일주일 1회 정도)
  - 6월 조회 0건 (전체 2,571건, 우리회사 0건) — 5월도 0건
- PBM110MW 사양: REQ_TYP `01=납품, 02=반납`, UNLOAD_REQ_DAT(하차요청일자, YYYYMMDD, 필수), PRD_COD=N11(11T 파렛트), CAR_OWN_TYP=`02=USER운송`, 신규 페이로드 MOD=`I`, **JSON POST** /ps/PBM110MW.do (조회는 **GET** /ps/PBM110MW.do + REQ_DAT_FR/TO, STC_CST_COD, REQ_CST_COD)
- **PBM110MW 날짜 의미** (사용자 확인, 2026-06-03):
  - **요청일자 (REQ_DAT)** = **"내가 KPP에 요청한 날"** — 사용자가 KPP에 입고 요청 신청한 시점. **"내가 언제 KPP에 요청했는지 확인할 때" 사용**
  - **하차요청일자 (UNLOAD_REQ_DAT)** = **"우리 회사(217273)에 실제 입고된 날"** — KPP가 우리 회사로 팔레트 입고 완료한 시점
  - 예: 5/29 요청 → 6/5 입고 (같은 1건의 두 다른 시점)
- **PBM110MW 조회 시 REQ_DAT_TYPE**:
  - `1` = 요청일자 기준 (사용자 = "내가 KPP에 요청한 날")
  - `2` = 하차요청일자 기준 (사용자 = "우리 회사에 실제 입고된 날")
- **PBM110MW 조회 시 STC_CST_COD/REQ_CST_COD 필터**:
  - `STC_CST_COD="", REQ_CST_COD=217273` = 우리 회사가 **입고받은** 내역 (★ 주 사용 케이스)
  - `STC_CST_COD=217273, REQ_CST_COD=""` = 우리 회사가 **요청한** 내역 (다른 회사로 보냄)
  - **둘 다 217273 보내면 OR 매칭 실패 → 0건 (함정)**
- 6월 하차요청일자 조회 결과: 1건 (5/29 신청, 6/5 입고, N11 200팔레트, ARV=217273 유원피에스, ALC_STATUS=03)
- **PBM110MW 자동 일자 규칙** (fn_new, line 1031~1064):
  - `REQ_DAT` = **오늘 (gfn_today())** — 사용자가 직접 입력 또는 자동
  - `UNLOAD_REQ_DAT` = **자동으로 REQ_DAT의 다음 날 (tomorrow)** — "당일+1일 입고"가 KPP 기본 운영
  - 예: 6/3 요청 → 6/4 입고 (자동)
- **ALC_STATUS (배차진행상태) 코드표** (KPP 공식, `resources/js/cmm/code.js` 1052~1057):
  - `01` (018001) = 미배차
  - `02` (018002) = 운송의뢰
  - `03` (018003) = 상차대기
  - `04` (018004) = 배차완료 (입고 종료)
  - DB에는 마지막 2자리만 저장됨. PBM110MW HTML의 `lockStatus = ["02","03","04"]` = "잠금 처리되는 상태" (수정 불가)
- PBM140MW(출하통보) — 저장: `POST /ps/PBM140MW.save` (대문자+save), 조회: `POST /ps/PBM140MW.search`, 필드 **소문자** (chk, dlv_dat, dlv_qty, prd_cod, arv_cst_cod, comp_cod, dlv_cst_cod 등)
- **PBM140MW 차량번호(car_num) 입력 규칙** (2026-06-03 확정): KPP는 **숫자만 6자리** 허용. 한글(차종/지역)은 2자로 카운트되므로 6자리를 넘으면 거부. **변환 절차**: "경기95자6464" → 숫자만 추출 → "**956464**". **적용**: 1호차=956464, 2호차=891454, 3호차=906169. **에러**: `flag:false, message:"차량번호는 6자리만 가능합니다. (한글은 2자로 인식합니다!)"` 발생 시 → 위 규칙 적용. **검증 후 저장 의무** (B/C/D 위반 방지).
- ARV_CST_COD=610060(BUC1_H, 쿠팡-부천1센터[HUB]), ZIP1=421 / ZIP2=170 / ZIP_SEQ=1, REQ_ARV_ZIP_ADDR="켄달스퀘어 3층 B동(IB)"
- **PBM110MW 신규 등록 (팔레트 신청) 트리거 패턴** (2026-06-03 확정):
  - 트리거 표현: "팔레트 신청해 줘" / "팔레트 신청" / "팔레트 입고" / "KPP 신청"
  - 자동 세팅: REQ_DAT=오늘, UNLOAD_REQ_DAT=내일(자동), PRD_COD=N11, REQ_QTY=200, ARV_CST_COD=217273, ZIP1=482, ZIP2=110, ZIP_SEQ=1, REQ_ARV_ZIP_ADDR="582-2", ZIP_NUM="경기 양주시 삼숭동", REQ_TYP=01(납품), CAR_OWN_TYP=01(KPP운송), CAR_WGT_TYP=07, UNLOAD_REQ_TIM=0000
  - API: `POST /ps/PBM110MW.do` + Content-Type=application/json + body는 **배열로 wrap** (단일 객체 X). 응답: `{"flag":true,"message":"","map":null,"list":null}` = 성공
  - 페이지에서: 로그인 → /ps/index → /ps/PBM110MW → POST
  - **함정**: 단일 객체 POST 시 404 (배열 wrap 필수), form-urlencoded 415, STC/REQ 둘 다 217273 매칭 0건
- **KPP 관리자 연락 절차** (6/5 건 처리 같은 케이스):
  - PBM110MW fn_delete는 `lockStatus = ["02","03","04"]` (진행 중/완료) 모두 잠금 → **사용자 임의 삭제 불가**
  - 백엔드 직접 DELETE도 MNG_GRD=05 (일반 사용자) 권한 부족 + REQ_CST_COD 백엔드 응답 누락 → 차단
  - 일자 변경/취소 = **KPP 관리자에게 직접 연락** (운영원칙: 사용자 임의 데이터 변경 금지)
  - 신규 등록으로 우회 가능: 6/5 건 유지 + 6/4 건 신규 INSERT (6/3 작업에서 확인)
§
VF-project 구글시트 동기화 문제 (2026-06-03 00:19): 1) requests 모듈 누락 (Windows venv에는 있었지만 requirements.txt에 미정의) → pip install + requirements.txt 양쪽 추가. 2) FC 입고 시트(gid=810884704) HTTP 401 Unauthorized — Google 시트 자체가 비공개/삭제 (사용자 측 해결: 시트 소유자가 Share → Anyone with the link → Viewer). 3) /api/inventory/refresh POST 500 (trailing slash 미허용, GET-only). 4) OUTBOUND/MASTER_DATA 시트는 HTTP 307 (redirect, 정상).

§
**텔레그램 파일 첨부 전송 (검증됨, 2026-06-03)**: send_message 툴 + ASCII 절대경로 + 짧은 본문. ❌ 한글/공백/특수문자 경로 (어댑터 MEDIA_TAG_CLEANUP_RE 파싱 실패), ❌ curl sendDocument 직접 호출 (게이트웨이 우회, 사용자 채팅방 미표시). ✅ 패턴: `cp /tmp/한글.zip /tmp/ascii.zip` 후 `send_message(message="...\n\nMEDIA:/tmp/ascii.xlsx\nMEDIA:/tmp/other.pdf", target="telegram")` → `success:true, message_id:NNN, chat_id:5708696961`. 봇 어댑터: gateway/platforms/base.py L3783~L3797 (extract_media), L1200~L1206 (정규식).

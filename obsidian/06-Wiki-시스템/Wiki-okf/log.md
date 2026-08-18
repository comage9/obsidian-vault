###

## 2026-08-17

### 제품배치도 — 크로스동 이동 + 임시 보관함 + 우측 패널 개선 (백업 backup-20260817-pre-cross-dong)
- **총괄 탭 크로스동 이동**: 미니맵에서 A동 제품→C동 등 다른 동으로 드래그 (기존 zone 브랜치 재사용, 소스 제거+대상 append). A동 점유 칸 append 가드(1칸 1품목). 수정 모드에선 미니맵 드래그 활성, 비수정=변경 차단.
- **임시 보관함(Staging)**: 별도 키 영속, 수정 모드 전용 패널, 넣기(칸 선택→버튼 / 셀 드래그→드롭존), 꺼내기(빈 칸=배치, 점유 칸=스왑 자동 보관), 총괄 우측 패널에도 배치.
- **총괄 우측 패널 개선**: 배치/미배치 분류 아코디언(클릭→세부 펼침), 넓이 340→560px, 자리이탈 품목 클릭→이동 모드(미니맵 칸 클릭 배치+기존 제품 자동 자리이탈), 미배치로 삭제 버튼. 임시보관함을 4번째 탭(📦)으로 이동(비수정=드래그 차단).
- **제품 배정 다이얼로그 검색**: 번호/이름/분류/바코드/로케이션 검색 → 선택 배정, 기존 제품 자동 자리이탈(overflow) 이동.
- **수정**: pointerWithin+autoScroll=false로 크로스동 오드롭 소실 방지, StagingPanel 컴포넌트 분리(useDroppable DndContext 컨텍스트 수신), ZoneCell 단일 useDraggable(이중 등록 충돌 제거), 자동 저장 useEffect. 배치/미배치 테이블 품목명 좌측 정렬(gap-2, 우측 정렬→번호 옆).
- **임시 보관함 (Staging)**: 별도 키 vf_product_display_staging_v1(unique 배열, 자동 저장). 수정 모드 그리드 아래 📦 패널. 넣기=칸 선택→버튼/드래그→드롭존, 꺼내기=빈 칸 배치/점유 칸 스왑(자동 보관). 비수정=숨김(데이터 유지).
- 검증: A동 1번→C-R5-C1 append · 1↔3 스왑 · 새로고침 유지 · B/C/D 키 보존 · 점유 A칸 거부 + tsc 0
- 커밋: 1762207(보관함) · a671393(크로스동) · 백업 태그: backup-20260817-pre-cross-dong (417a28a)
- 계획 문서: 의사결정/제품배치도-크로스동-임시보관함-계획-20260817.md

### 제품배치도 — 그리드 편집: 칸 추가·칸 자유 이동(드래그)·그리드 확장
- **+ 칸 추가**: 그리드 오른쪽에 새 빈 칸 생성 → 드래그로 원하는 위치 배치 (칸수 늘리기)
- **칸 자유 이동 (수정 모드 셀 드래그)**: ①다른 칸 위에 놓으면 **좌표 교환(swap)** ②빈 공간에 놓으면 **자유 좌표 배치** ③클릭-클릭 swap도 유지
- **그리드 확장**: 여유 ⬆⬇⬅➡ 버튼으로 상하좌우 +40px씩 (기본 = 현재 그리드만 표시, 필요할 때만)
- 수정 모드에서 제품 드래그(aDrag) 비활성 → 칸 드래그(cellDrag) 담당, 비수정 모드는 제품 드래그 유지
- **검증**: 칸 추가(133개)·드래그 swap(858↔768)·자유 배치(829,1187)·그리드 확장(h 858→898)·제품 드래그 회귀(L1-1→L1-3) + tsc 0
- 커밋: 7b1fa10

### 제품배치도 — 데이터 소실 버그 3건 수정 (드래그·그룹이동·렌더 에러)
- **증상**: 수정 모드에서 드래그/그룹 이동/라인 추가 시 모든 데이터(B/C/D 배치) 소실
- **원인 1 (치명)**: `aShiftInsert`/`groupShiftInsert`가 **빈 객체 `{}`에서 next 생성** → A동 시퀀스 키만 반환 → `persistLocal`이 전체를 교체 → **B/C/D 배치 소실**
- **원인 2 (렌더 에러)**: groupShiftInsert가 **undefined(빈칸) 값 전파** → `Cannot read properties of undefined (reading 'split')` 화면 에러
- **원인 3 (방어 부재)**: placedPnums/검색 useMemo에서 data 값 undefined 시 `split` 에러
- **수정**: `{...data}` 복사 시작 + `delete next[srcZone]`(빈칸 유지) + `put` 헬퍼(undefined 시 키 삭제) + `(val || "")` 방어
- **검증**: 유닛 테스트 T1~T4(빈칸/경계/그룹) + 브라우저 실측(드래그·그룹이동·라인추가 후 **B/C/D 323키 유지**, 콘솔 에러 0, L8 생성) — 에이전트 3인 병렬 검증 실시
- **에이전트 검증 후 추가 수정 (9eca05f)**: aShiftInsert의 쓰기 전용 가드 → put 헬퍼(undefined 시 delete)로 빈칸 잔존+overflow 중복 방지 · resetData 'A동 초기화'가 전 동 리셋하던 것 → **A동만 초기화(B/C/D 유지)** · 유닛 T1~T4 재검증 PASS
- 커밋: f122422, 9eca05f

### 제품배치도 — 라인(열) 단위 이동 + 새 라인 추가
- **라인 교환**: 사각형 드래그로 라인 선택(예: L1 19칸) → 목적지 라인 칸 클릭 → **두 라인 좌표 통째로 교환** (칸 수 동일할 때)
- **라인 추가**: '+ 라인 추가' 버튼 → 최대 라인번호+1, 참조 라인과 같은 칸 수의 빈 슬롯 생성(A동 L8 16칸 검증) + '8번' 라벨 + width 자동 확장
- 버그 수정: X1/X2(line=8 특수칸)가 라인 번호에 포함돼 L9(2칸) 생성되던 문제 → id 기반 `L\d+` 추출로 해결
- 검증: 브라우저(5174) 라인 19칸 선택·L1↔L3 교환(470↔326)·L8 추가·localStorage 저장 확인, tsc 0
- 커밋: VF-new `b5a1a48`

### 제품배치도 — 칸(슬롯) 좌표 이동 (수정 모드)
- **수정 모드**: 칸(빈칸/제품칸) 클릭 = 선택(purple) → **나머지 칸들에 이동 가능 하이라이트**(초록 점선 + "클릭하면 이동" 툴팁)
- **목적지 칸 클릭** = 두 칸의 **좌표 swap** — 제품은 칸에 그대로, 칸(슬롯) 자체가 그리드에서 이동
- 동적 레이아웃(layoutState): 좌표 변경 즉시 반영 + **localStorage 자동 저장**(layout-v1)·로드
- 검증: 브라우저(5174) 선택·하이라이트(131칸)·좌표 swap(470↔380)·저장 확인, tsc 0
- 커밋: VF-new `c93e471`

### 제품배치도 — 배치 스키마 v15 (전 동 표시 복구)
- **원인**: localStorage에 옛 저장분(`rank-a-v14`, A동 132키만)이 남아 loadPlacement가 이를 로드 → **B/C/D가 빈칸**으로 보임 ("A동만 배치" 현상)
- **해결**: `__v` 스키마 버전 체크 — v14(불일치)는 무시하고 기본값(A+B+C+D) 로드, 저장 3곳(persistLocal/saveData/resetData)도 v15로
- **효과**: 사용자 브라우저 **새로고침만**으로 전 동 표시 (서버 재시작 불필요 — Vite watch로 이미 재변환 확인)
- 전 동 배치 현황: A 132칸(134품목) / B 48칸(46채움·137품목) / C 108칸(228품목) / D 41칸(38채움·75품목)
- 커밋: VF-new `583322f`

### 제품배치도 — 수정 모드 + 그룹 선택 이동 (그리드 편집)
- **수정 모드**: '수정' 버튼 토글 → 셀 클릭 = 개별 선택 (purple 하이라이트), 빈 영역 마우스 드래그 = **사각형 선택 틀**(점선) → 걸친 칸들 일괄 선택 (라인 일부/전체, 110칸 검증)
- **그룹 이동**: 선택 시 [↑ 위로 이동][↓ 아래로 이동][선택 해제] — groupShiftInsert로 그룹이 시퀀스에서 1칸씩 이동, 밀려난 값은 반대편 순환 (맨 위/아래 경계 무시)
- **B/C/D**: 동일 수정 모드 적용 (각 동 시퀀스 기준)
- 이동 즉시 자동 저장 + 선택 상태 유지
- 검증: 유닛(위/아래/경계/라인전체) + 브라우저(5174) 개별(1↔216 스왑)·110칸 그룹 이동·localStorage 확인
- 커밋: VF-new `c929533`

### 제품배치도 — 드래그앤드롭 재배치 + 분류·단수 필터 + 자리이탈 패널 (에이전트 3인 협의 반영)
- **드래그앤드롭**: dnd-kit(기존 설치) useDraggable/useDroppable 셀 적용, PointerSensor(5px 임계값으로 클릭-모달과 구분) + DragOverlay
- **A동 insert 밀림**: 소스 제거 → 축약 시퀀스 기준 대상~끝 shift (중복 방지 — 원본 data 직접 참조 버그 수정). 예: [·,2,1,28,603] = 1을 L1-1→L1-3 이동
- **자리이탈(overflow)**: 끝에서 밀려난 품목 → 우측 패널 '자리이탈' 탭 (번호·이름·단수·이전위치 + 미배치로 버튼 + 다른 동 재드래그)
- **분류·단수 필터**: 동 탭 아래 [분류 select][단수 select][초기화] — extractDansu(제품명 N단 정규식, Map 캐시), 매칭 셀 emerald ring
- **B/C/D**: 칸 내부 품목 순서 재정렬 (reorderInZone)
- **자동 저장**: loadPlacement localStorage 읽기({__v,data} 래핑 처리) + 드래그 직후 persistLocal
- 검증: tsc 0 / 브라우저(5198) 드래그·밀림·자동저장·필터·자리이탈 패널 전부 확인
- 커밋: VF-new `e49fbd8`→`064bd22`

### 제품배치도 — A동 L7 재구성 + C동 R20 와이드 라인 추가
- [A동] L7 16슬롯 재구성: **7-1-1부터** 슬림서랍장 위주 10개(210/214/203/225/246/201/232/244/237/250) + **칵투스 마지막** 6개(981/980/982/985/983/988) · **A-X1/X2 신설**(5·6번 통로, 2품목/칸): A-X1=287/172 로코스, A-X2=354/315 옷걸이 — A동 **134품목** (커밋 `eef16d4`)
- [C동] **R20 신규 8칸**(C-R20-C4~C11) 추가 — 와이드 서랍장 **출고량 상위 16품목**(762·752·742·732·748·768·750·753·765·761·727·728·760·764·754·740) · R21/R23도 상위순 재배치(730~757 / 756~721) — C동 **108칸·228품목**
- [함정] 파일 교체 시 `",".join(문자열)` 문자 분리 버그 2회 + A_UNPLACED 교체 `src[:start]` 누락 2회 → **수정 후 재검증 필수** (git restore → 재적용)

### 제품배치도 상위권 순 재배치 적용 + 조건 기반 재배치 도구
- [재배치 적용] A동 120품목 상위권+분류밴드(rank중앙 69, 0박스 0, rank≤200 119) · B 3/칸 · C 와이드2·슬림형3/칸 · D 기존 — 커밋 `edba181`
- [도구] `backend/scripts/vf_replan.py` — 조건 기반 재배치 CLI (`--rule top_rank` `--per-slot "리빙박스 로코스:2"` `--priority finished|rank` `--dong A|B|C|D` `--apply`) — 마스터 API+랭크 파일 기준
- [백업] v1 백업 4파일 + git 태그 `checkpoint-product-display-v1-20260817` (복원: git checkout 태그)
- [참고] 로케이션 단위 배치 — 같은 로케이션 2바코드=같은 제품(2개 표시)

### 제품배치도 전동 검증 + A동 L7 바퀴슬림 제외
- [문서] `물류/VF/제품배치도-전동-검증-20260817.md` — 검증: A동 1칸1팔레트 ✓ · L7 바퀴포함 10품목 전부 비상위(rank 229~686, 박스 0~16) → **제외** (A동 130→120, 미배치 725) · B/C/D: 0박스 79·포장필요 193·rank>200 372 — 전면 재검토 필요 · 같은 로케이션=같은 제품(2개 표시) 규칙 재확정 · 마스터 product_number 중복 102건 발견
- 커밋: VF-new `9616305`

### 매일 출고데이터 동기화 cron
- [정상] `manage.py daily_outbound_sync` (Python313, `VF-new - 복사본/backend`)
- DB 최신(전): 2026-08-14 → 동기화 후: **2026-08-15** / 오늘 2026-08-17 / 기준일 2026-08-15~
- 결과: **신규 208건, 갱신 0건** (exit 0)
- DB 검증: `OutboundRecord` ge 08-15 = 208 / total = 256961 (256753 + 208)
- Auto-Watcher: downloads 스캔, 신규 차량 3대 등록

### LS PDF 인쇄 cron (8/17 16:30)
- [실패] `8c57a12b627d` — 쿠키 파일 없음 (`…/ls-coupang/references/coupang_cookies_browser.txt`) → **ls-coupang 스킬 부재 8/3 이후 지속** (8/15·8/16·8/17 **3일 연속 동일**), LS 로그인 필요

### VF2 Production Plan Nightly (8/17 05:40, `48144ff13cee`)
- [점검] 백엔드·프론트 **DOWN 14시간 43분** (포트 5176/5174 미Listen, 프로세스 0건) — **systemd 미등록 6회째 CRITICAL** (다음 재부팅 시 즉시 재발) · 운영 침묵 **70일째** · 디스크 83%→**73% (-10%p) WARNING 해소**
- [문제] 보고서가 `E:\hermes-backup\Hermes\자가-학습-Cron\VF2-Production-Plan-Nightly-20260817.md` (**Wiki-okf 밖**)에 저장·커밋됨 (de4dfce) — 어제(8/16)는 Wiki-okf 안에 저장됐음 / 다음: VF2 Nightly cron 보고서 경로 복원

### OmniRoute 일일 스모크 (8/17 07:00)
- [참고] `f27aea7bb126` — :20128 DOWN으로 probe skip (03:00 재시작 직후, 8/16과 동일 패턴)

### dsh(DeepSeek Harness) + OmniRoute API Key
- [결정] `의사결정/DSH-OmniRoute-API-Key-문제-20260817.md` — dsh의 openai-completions 라우트는 **API 키 없이는 요청 자체를 시작 안 함** (`No API key for provider: omniroute`, OmniRoute는 무인증이지만 dummy 키 필요). 해결: `apiKeyEnv: OMNIROUTE_API_KEY` + credentials에 값 추가, 또는 Web UI에서 아무 키 입력 / 다음: dsh에서 OmniRoute 모델 사용 시 적용

## 2026-08-16

### A동 순위 확장 배치
- [자료] `1111-rank-extend` 저장 (Sources/docs)
- [배치] 기존75(파랑)+추가43(초록 지그재그 5·6·하단) · 미배치739 표
- rank-a-v10


### A동 배치 적용: 1111 slot순 L1~5
- [적용] 첫열 로케이션 순 1~5번 라인 · 실배치105 스냅샷 유지 · rank-a-v2 · 미배치19


### VF-new 제품배치도 A동 — 실배치 스냅샷·복구 가이드
- [문서] `물류/VF/제품배치도-A동-이력-복구-20260816.md` + VF-new `docs/product-display/A동-배치-변경이력-복구가이드-20260816.md`
- [스냅샷] 현재 실배치 제품번호 **105개** JSON/TXT (사용자 호명) — 복구 SoT
- [대비] UI 계획v1(순위56칸) vs 실배치105 · 일렬 2~3품목 원칙 기록
- [다음] 실배치→칸 매핑 / 미배치·B동


### VF-new 제품 배치도 A동 1번 라인
- [수정] `frontend/client/src/pages/product-display.tsx` — A~E형→**A~E동**, 페이지 확대, **세로 슬롯(초기 렉 칸)** 양식
- A동 1번 라인 로케이션 **1~19** (맨 아래 1 · 맨 위 19), id=`A-L1-{n}`
- 2~4번 라인 확장용 `buildVerticalLineZones` + `A_LINES` 구조 준비 / B~E 대기
- dashboard PAGE_META 설명 A~E동 반영
- 실측: Playwright 19칸, order 19…1, slot 88×168, console error 0
- 다음: 사용자 2·3·4번 라인 품목 수 지정 후 동일 양식 추가


### 매일 출고데이터 동기화 cron
- [정상] `manage.py daily_outbound_sync` (Python313, `VF-new - 복사본/backend`)
- DB 최신(전): 2026-08-13 → 동기화 후: **2026-08-14** / 오늘 2026-08-16 / 기준일 2026-08-14~
- 결과: **신규 228건, 갱신 0건** (exit 0) — 전부 `2026-08-14` (08-15·08-16 시트 데이터 없음)
- DB 검증: `OutboundRecord` ge 08-14 = 228 / total = 256753
- Auto-Watcher: downloads 스캔, 신규 차량 3대 등록

### 제품배치도 초기 설계 문서화 (18:08~19:52 — index.md 누락분 일괄 등록)
- [문서] `물류/VF/제품배치도-총괄뷰-BC동-20260816.md` — 총괄 배치도 탭(A~E동 한 화면) + B동·C동 레이아웃, B동 통로 조정·B/C 가로 통일·하단 정렬
- [문서] `물류/VF/제품배치도-C동-레이아웃-20260816.md` — C동 세로 16라인(1~10 빈 라인) 구조, 라인=중앙 블록(1~8칸)+우측 블록(1~8칸)
- [문서] `물류/VF/제품배치도-C동-107칸-20260816.md` — C동 107칸 재현 + 총괄 레이아웃 여백 축소
- [문서] `물류/VF/제품배치도-C동-엑셀그대로-20260816.md` — 엑셀 `통합 문서2.xlsx`(Sheet4, A1:U23) 셀 위치(행·열) 그대로 좌표 변환, 추측/해석 없음
- [문서] `물류/VF/제품배치도-복구기준-20260816.md` — 복구 기준 시점 문서화, Git 태그 `checkpoint-product-display-20260816`
- [문서] `물류/VF/제품배치도-B동-옷걸이슬림핸들러-20260816.md` — B동 옷걸이/슬림형 서랍장/핸들러 배치(미배치 101품목 대상)

### LS PDF 인쇄 cron (8/16 16:30)
- [실패] `8c57a12b627d` — 쿠키 파일 없음 (`…/ls-coupang/references/coupang_cookies_browser.txt`) → **ls-coupang 스킬 부재 8/3 이후 지속**, LS 로그인 필요 (8/15와 동일)

## 2026-08-15

### 매일 출고데이터 동기화 cron
- [정상] `manage.py daily_outbound_sync` (Python313, `VF-new - 복사본/backend`)
- DB 최신: 2026-08-13 → 오늘 2026-08-15 / 기준일 2026-08-13~
- 결과: **신규 0건, 갱신 224건** (exit 0)
- Auto-Watcher: downloads 스캔, 신규 차량 3대 등록
- [참고] 전일(8/14)은 OmniRoute admission 503으로 미실행 → 금일 정상 회복

### VF-go 이관: S 완결 + T1–T5
- [완료] **S3** machine 패리티 — Django vs Go 9케이스 일치, POST `/plans`→405 맞춤, API_MAP machine ✅ · **S 시리즈 완결**
- [완료] **T1–T4** delivery — 읽기 3종+hourly POST 구현/패리티, notes+prediction 스키마 LOCKED (recent_28·cum>2500·Unknown/기타)
- [진행] **T5** notes 구현 — `internal/db/delivery.go` + `http/delivery/handlers.go` + router, build/vet/test PASS · Claude 위임 후 Hermes **라이브 curl 마감 미완** → CURRENT_TASK=T5🟡 → 다음 T6 prediction
- [참고] skill refs: `vf-go-migration/references/t-series-status-and-gates-20260815.md`, `t5-notes-impl-and-delegation-guards.md`

### Cron 운영 결과 (8/15)
- [정상] OmniRoute 03:00 업데이트+재시작 `2587522b4350` — v3.8.49 latest 유지, health ok (pid 재기동)
- [참고] OmniRoute 07:00 스모크 `f27aea7bb126` — 재기동 직후 `:20128 DOWN`으로 probe skip
- [정상] Wiki 용량 검증 `d3349950eecd` — git pack 4.54 MiB / wiki 0.98 MiB
- [부분] LS 14시 통합 `8a776545148d` — WEB-GATEWAY-SESSION OK, 템플릿 3건 SUBMITTED(90626/90628/90269) Batch 스킵 · VF 5176 DOWN·오늘 ls-data 없음 · **ls-coupang 스킬 부재** 지속 (상세는 파일 말미 14:06 entry)
- [실패] LS PDF 인쇄 `8c57a12b627d` 16:30 — 쿠키 파일 없음 (`…/ls-coupang/references/coupang_cookies_browser.txt`)
- [다음] ls-coupang 스킬·쿠키 복원, T5 curl 마감, VF 5176 기동 후 출차 동기화

## 2026-08-14

### VF 로케이션 정비·공간 확장 계획 수집
- [자료섭취] `Sources/텍스트/2026-08-14_보노하우스-VF-로케이션-정비-공간확장-보고.txt` 원문 보존 / 이유: 사용자 보고서 + 운영팀 구두 브리핑 / 다음: 현장 정비 실행
- [문서화] `물류/VF/로케이션-정비-공간확장-감사대비-20260814.md` 생성 — 1:1 로케이션·임시 이동(전산 미입고)·외부 확장, 현황 875/773/403/370, 다음달 랜덤 감사·계약해지 리스크
- [갱신] index.md 물류 33→34, VF 3→4, total pages 184→185
- [업데이트] 공간 확보 방안 추가: 슬림 서랍장 파레트→수작업 적재, 와이드·저출고 모던플러스 2~3품목 연결 바깥 배치, 야외 추가계약 블로커, 벌크·칵투스 공간 필요 / 이유: 사용자 구두 보완 / 다음: 야외 계약·현장 전환 실행
- [업데이트] 출고 많은 순 정리 + 저출고 개별 적재; 미출고·잔여 재고 반출(A) vs 보관+자리(B) 미결 결정 기록 / 이유: 사용자 구두 보완 / 다음: A/B 결정 후 자리 배정
- [업데이트] 실행 계획: VF 3개월 미출고→FC 우선 전환, VF 출고 상위 순 파레트 재배치, 그 외 다품종 파레트 / 이유: 사용자 확정 방향 / 다음: 통합 보고서 Output
- [output] `Output/2026-08-14/VF-로케이션-정비-공간확장-통합보고서.md` 통합 보고서 생성 / 이유: 사용자 보고서 형태 요청 / 다음: A/B·야외계약·FC 전환 실행

### VF-go 이관: S2 완료
- [완료] S2 machine PIN/plans Go 구현 — `internal/db/machine.go` + `http/machine/handlers.go` + router, curl 17시나리오 PASS (login/users/plans/apply/delete)
- [함정] identity desync → INSERT `MAX(id)+1`; token timestamp `%.6f` (과학표기 방지); apply → production_logs
- [다음] CURRENT_TASK=**S3** machine 패리티 (실측 진행 중, 미완)

### OmniRoute 통로 확장
- [시스템] `~/.omniroute/.env` → `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=3` (기본 1→3), 재시작 후 health 200 (v3.8.49)
- [이유] 텔레그램+로컬 Hermes 동시 사용 시 admission 503 완화 / 다음: 잔여 503 시 무료 모델 한도 점검

### Cron 운영 결과·차단 (8/14)
- [실패] 매일 출고데이터 동기화 `7fb0ae1fa347` 09:03 — agent HTTP **503** admission busy (`Structurally heavy chat…`) → 동기화 미실행
- [실패] LS 14시 통합 `8a776545148d` — VF 출차 **0건**(신선·빈값), LS 조회 0건·템플릿 Batch Create **Keycloak 고착**/WEB-GATEWAY-SESSION 미확보, **ls-coupang 스킬 부재** 지속
- [실패] LS PDF 인쇄 `8c57a12b627d` 16:30 — 쿠키 파일 없음 (`…/ls-coupang/references/coupang_cookies_browser.txt`)
- [정상] OmniRoute 03:00 업데이트+재시작 OK (이미 3.8.49 latest, pid health ok) · Wiki 용량 검증 OK (git pack 4.54 MiB)
- [참고] OmniRoute 07:00 스모크 — 당시 :20128 DOWN으로 probe skip (03:00 재기동 이후 별도 이슈 아님으로 기록)
- [다음] 사용자 LS 수동 로그인·쿠키/스킬 복원 + 출고 sync 재실행(503 회피 또는 no_agent 경로)

## 2026-08-13

### VF-new 전산재고: 장기 미발주 + 비고 수정
- [기능] BarcodeMaster `is_long_term_no_order` 추가 (migration 0038) — 수동 설정 시 critical(위험) 집계 제외, 상단 카드 '장기 미발주 요청 품목' 별도 집계
- [수정] 비고(notes) 표기: MasterSpec 우선 + BarcodeMaster 폴백, inventory/unified 응답에 notes·is_long_term_no_order·is_no_outbound_3m 포함
- [다음] 모바일 inventory/enhanced 탭 UI(재고현황·VF 재고조사) 가시성 요청 미완 / finish_type 저장 롤백 이슈 조사 중(R003750270003 테스트 중단)

### VF-go 이관: U1–U3 완결 + S1 스키마 확정
- [완료] U1 inventory/unified 확장 · U2 PATCH `/api/inventory/unified/{_id}` · U3 barcode-master/master-specs notes·장기미발주 패리티 — **U 시리즈 완결** (build/vet/test + curl 검증)
- [완료] S1 machine PIN/plans 스키마 확정 (7 API, machine_users 10col/91행, machine_plans 18col/2행, PIN SHA-256·5회실패→5분잠금, 함정 9건)
- [다음] CURRENT_TASK=**S2** machine PIN/plans Go 구현 → S3 parity

### Claude Code → OmniRoute 위임 설정
- [시스템] `~/.claude/settings.json` ANTHROPIC_BASE_URL=http://127.0.0.1:20128, MODEL=auto/best-coding (OmniRoute 라우팅 확인)
- [함정] subagent 600s 타임아웃 반복(deleg_35e3429d, deleg_da0b1d54) — 한 소단위만 짧게 위임 권장. U1 실제 완료는 Hermes 직접 검증 경로

### LS 14시 통합 cron 재실패 (8/13)
- [차단] ls-coupang 스킬 유실 + LS Keycloak OAuth 미인증(쿠키 없음, API 302) — 8/4·8/12에 이은 동일 차단
- [상태] VF 5176 정상·work_date=8/13, 출차 차량 0건 → 등록 대상 없음. 수동 LS 로그인·쿠키 재발급 필요

## 2026-08-12

### Hermes OmniRoute config.yaml 최적화 + Gateway 재시작
- config.yaml auxiliary 역할 16개 중 3개 모델 교체: skills_hub→aug/glm-5.2, approval→pplx-web/pplx-grok-4.5, mcp→oc/deepseek-v4-flash-free
- 미지정 10개 역할 auto/best-fast로 채움, 백업 `config.yaml.bak.20260812_192623` 보존
- OmniRoute 실제 목록 458개 중 16/16 존재 확인 (glm-5.2, pplx-grok-4.5, deepseek-v4-flash-free 모두 ✅)
- Gateway PID 9664 → **9356** 재시작 (19:56 시작, config 수정 19:28 이후 → 새 구성 로드 확정)
- Scheduled Task(Hermes_Gateway) 정상 등록

### OmniRoute CLI 에이전트 감지 버그 진단
- `/api/cli-tools/detect` (구버전, ~/.hermes/config.yaml) → Hermes Agent ✅ configured: true
- `/api/cli-tools/all-statuses` (신규 동적 감지, HERMES_HOME/config.yaml) → Hermes Agent ❌ not_configured
- **원인**: OmniRoute v3.8.49 내 `checkToolConfigStatus()` 파일 읽기/문자열 검색 버그. 두 config 파일 모두 `provider: omniroute` + 포트 20128 정상 포함
- **영향**: 표시 문제만. 실제 Hermes Agent는 OmniRoute/auto/best-free로 정상 동작 중 (이 세션 자체가 증명)
- 수정 불가 (OmniRoute 소스 코드 내부). 03:00 cron 업데이트에서 패치 가능성

### LLM-wiki 스킬(v2.3.0) 검증 + Gateway 재시작
- 스킬 구조 확인: SKILL.md(31,291B) + references 5개 + scripts 3개(migrate_wikilinks.py, validate.sh, vault_gate.py)
- 실제 Wiki Vault: **E:\hermes-backup\obsidian\06-Wiki-시스템\Wiki-okf** (154개 md) — Wiki/는 껍데기, 별개
- vault_gate.py 경로 결정 3단계: ①WIKI_PATH env ②~/.wiki_location ③OS 기본값 ~/wiki
- Gateway PID 9664 실행 확인 후 재시작 (sleep 8 후 상태 확인)

### 매일 출고데이터 동기화 cron 정상 완료
- 명령: `manage.py daily_outbound_sync` (Python313)
- DB 최신 날짜 2026-08-10 → 오늘 2026-08-12 기준
- **신규 211건 추가, 기존 220건 갱신** (기준일 2026-08-10~), Auto-Watcher 신규 차량 3대 등록
- Exit code 0, 정상 종료

### LS 14시 통합 크론 — 데이터 0건 + 근본 차단 2건
- VF 출차관리 데이터: **0건** (서버 5176 정상, 8/12 ls_count=0, vehicles=[]) → 등록 대상 없음
- **차단 ① ls-coupang 스킬 유실**: skills/automation/ls-coupang/ 디렉토리 및 coupang_cookies_browser.txt 쿠키 파일 모두 없음 → 인증우회·템플릿 Batch Create 실행 불가 (Skill-First Lock 위반)
- **차단 ② LS 인증 단절**: 회로차단 ls-daily 8/4 기록 — Keycloak 자격증명 거부 2회 + 쿠키파일 7/1 만료(302) → 8월 초부터 폼 인증 깨짐
- 복구 필요: ls-coupang 스킬 복원 + LS Coupang 로그인 재수립 (Keycloak 자격증명 + 쿠키 재발급)

### FC 입고 단가 업로드 반영 누락 원인 확인 시작
- 파일: `C:\Users\kis\Downloads\Coupang_Stocked_Data_List(2026-08-01~2026-08-12).xlsx`
- 증상: 8/3 입고 데이터 있는데 막대 그래프는 8/10,8/11,8/12만 표기, 다른 기간도 동일 현상
- Pre-flight Tool-First Auto-Recall 시작: 스킬·위키·세션·fact_store 병렬 확인 중 (진행 중, 결론 대기)

## 2026-08-11
### VF-new 검색: 로케이션 전역 검색 구현
- Backend: ?location= on master/specs + inventory/integrated
- Frontend: isLocationPattern() + inventory-table 정확일치 부스트
- 커밋: 939fa69, 473b1ae, 7c4af42, 44fa627

### VF 3개월 미출고: 수동 지정 보존
- _sync_vf_no_outbound_to_db: OFF 방향 sync 제거
- spec-edit-dialog: "VF 3개월 미출고" 버튼

### KPP MCP 서버 py3.11 venv 전환
- py3.13 pydantic_core → py3.11 venv
- Hermes config: command=venv/python.exe 직접 실행, PYTHONPATH env 추가
- 게이트웨이 재시작 필요

### MCP v2 업데이트 분석 (Bloom AI 영상)
- FastMCP→MCPServer, Sampling/Roots deprecated, WebSocket 제거
- 현 VF/KPP: stdio → 영향 없음, v1→v2 하위호환

### 재고 현황: 비고(notes) 툴팁 컬럼
- inventory-table: notesMap (barcodeMasterData 매핑)
- '비고' 컬럼: notes 있으면 '📝 내용 있음' + title 툴팁
- 커밋: 01ff5f0

## 2026-08-10
### VF MCP 서버 추가
- 경로: `E:/coding/skill/VF/vf-mcp-server`
- tools: status/departure/regions/plt/print_ls/print_kpp/stock/production
- Hermes `mcp_servers.vf` 등록. Gateway 재시작 필요.
- wiki-graph args 문자열 버그 → list 수정

### KPP MCP v2 보안 + Py3.11 재생성
- mcp 버전 상한 `<2` + venv Python 3.11.7 (3.13에서 pydantic_core 깨짐 방지), tools 4/4 검증
- 문서: `의사결정/KPP-MCP-v2-보안-20260810.md`

### 출력 이력 PrintLog
- LS/KPP 출력 시 PrintLog 자동 저장 + `GET /departure/api/print-logs` + 대시보드 🖨️ 패널
- 문서: `의사결정/출력-이력-PrintLog-20260810.md` (커밋 998a094)

### 전산재고 개선
- VF 마스터 비단종 전산재고 목록 포함, 미출고=부족 분류, 행 수정=제품마스터 SpecEditDialog 연동 (커밋 c7cc4f4/ec1e7d4/a87f412)

### KPP PBM140 다중센터 by_both
- 타센터 전표 보존 + 차량번호 매칭으로 VF 신규등록/수정 (호차만 보지 않음, 커밋 48b64e8)

### OmniRoute cron 2종 등록
- 03:00 패키지 업데이트+재시작 (2587522b4350), 07:00 일일 스모크 (f27aea7bb126, `omniroute_daily_smoke.py`)
- Telegram retry backoff(600s) 원인 수정 — 문서: `Hermes/OmniRoute-Hermes-모델목록-정리-20260809.md`

# 작업 로그

## 2026-05-28

### 03:09 — 백테스트 v3 엔진 전면 재생성 완료
- v3 엔진 적용 (분산투자 20% + 유동성 제한 2% + 동적 슬리피지 0.15~2%)
- 점수 시스템 v3.0 (CAGR×40% + Sharpe×25% - MDD×15% + 신뢰도×20%)
- 2,857개 종목 × 19개 전략 재계산 완료
- 평균 CAGR: 5.30% (현실적)

### 04:06 — Wiki 저장 완료
- `의사결정/백테스트-v3-엔진-완료-20260528.md` 생성

### 07:35 — 장전 분석 스크립트 수정
- `scripts/check_pre_market_analysis.py` import 경로 오류 수정 (src/ + project root 모두 sys.path에 추가)
- 정상 실행 확인 (exit 0)

### 07:35 — Wiki 구조 정비
- `SCHEMA.md` 생성 (domain, conventions, frontmatter, tag taxonomy)
- `index.md` 생성 (페이지 목차)
- 기존 파일: 3개 (의사결정 1, 문제-해결 1, log.md)
### 2026-05-28 08:02 — Wiki Lint: ❌0개 오류 / ⚠️3개 경고

| 검사 항목 | 결과 |
|-----------|------|
| 깨진 Wikilink | 0개 |
| 고립 페이지 | 2개 |
| Frontmatter 누락 | 1개 |
| 전체 페이지 | 5개 |

### 2026-05-28 08:02 — Daily Cleanup: 0개 아카이브, 3개 페이지
### 2026-05-28 10:47 — Wiki Lint: ❌0개 오류 / ⚠️3개 경고

| 검사 항목 | 결과 |
|-----------|------|
| 깨진 Wikilink | 0개 |
| 고립 페이지 | 2개 |
| Frontmatter 누락 | 1개 |
| 전체 페이지 | 5개 |

### 2026-05-28 10:47 — Daily Cleanup: 0개 아카이브, 3개 페이지

### 2026-05-28 11:10 — 문제 사항 문서화
- `문제-해결/ki-ai-trader-미해결-이슈-20260528.md` 생성
- Cron 감시 보고서 기반 미해결 이슈 7건 정리 (LLM 실패, 체결 타임아웃, DB accounts 누락, 자본금 부족, 토큰 리프레시, 종목코드 오류, 계좌 API 공백)
- index.md 갱신 (페이지 수 4개로 증가)

### 2026-05-28 12:04 — Git Auto-Sync: 5개 파일 → GitHub

### 14:50 — Telegram 이상징후 실시간 검증 완료
- 7개 항목 전수 검증: Arena Trader/매수/매도/LLM/계좌API
- 실제 장애: 0건, 모두 로그 노이즈 또는 구조적 한계
- 문서: `개념/telegram-이상징후-검증-20260528.md`

### 15:45 — 2026-05-28 전면 수정 9건 완료
- `의사결정/ki-ai-trader-20260528-전면수정-완료.md` 생성
- 수정 9건: trailing_stop 조건개선, LLM NoneType 방어, 가격필터, OHLCV+호가통합, import경로×2, 트레일링표시, Wiki스크립트5종복원, Telegram 1시간정기보고
- 보류: DB accounts(1회, 재현불가), refresh token(client_credentials 방식)
- index.md 갱신 (5페이지)
### 2026-05-28 22:01 — Wiki Lint: ❌0개 오류 / ⚠️7개 경고

| 검사 항목 | 결과 |
|-----------|------|
| 깨진 Wikilink | 0개 |
| 고립 페이지 | 6개 |
| Frontmatter 누락 | 1개 |
| 전체 페이지 | 9개 |

### 2026-05-28 23:00 — Cleanup: index.md 5페이지
  
### 2026-05-29 00:01 — Git Auto-Sync: 잘못된 script path → 대기 후 workdir 수정
  
### 2026-05-29 01:05 — 후속 작업
- **Wiki Frontmatter 수정**: `문제-해결/ki-ai-trader-is_running-일일손실한도-버그.md`에 YAML frontmatter 추가 (type/created/status/tags)
- **Wiki 크론잡 5종 workdir 설정**: ingest/lint/cleanup/briefing/git-sync에 `/home/comtop/obsidian-vault/06-Wiki-시스템` workdir 적용
- **GitHub Token 설정 완료**: `~/.hermes/.env` 및 `~/.env.hermes`에 GITHUB_TOKEN 저장
- **만두와김밥마을 프로젝트**: GitHub 저장소 생성 (`comage9/mandu-gimbap-lunch-menu`), 코드 push 및 GitHub 실버전(13커밋, 164파일) 로컬에 pull 완료
### 2026-05-29 22:03 — Wiki Lint: ❌0개 오류 / ⚠️7개 경고

| 검사 항목 | 결과 |
|-----------|------|
| 깨진 Wikilink | 0개 |
| 고립 페이지 | 7개 |
| Frontmatter 누락 | 0개 |
| 전체 페이지 | 10개 |

## 2026-06-01 ~ 2026-06-02

### WPPS PBM140MW 출하통보등록 정상화
- 안성5 IB (605177) — 1호차 18 + 2호차 19 = 총 37파렛트
- 비고(col36): "1호차"/"2호차" 규칙 확정
- CAR_OWN_TYP='02' USER운송, data_typ='01' 확정

## 2026-06-03

### KPP PBM110MW 검증 함정 발견
- **핵심**: fn_save는 200 OK + msg=성공 반환하지만 실제 미저장
- **해결책**: 반드시 GET 재조회로 row 존재 확인
- 인증 토큰 60분 만료, 자동 갱신 없음 → fn_login 재호출 필수
- `kpp-verify-search.py` 스크립트 작성

### KPP 6가지 Silent Drop 발견
1. data_typ '02'→'01' (가이드 오류)
2. dlv_dat 10자리 필수
3. truckRequestId는 호차순 정렬 안 됨 (truckSeq 기준 매핑)
4. fn_newRow→그리드 row→fn_save 서버 session 추적 구조
5. PBM140MW.save 직접 신규등록 불가능 (Playwright UI 또는 사용자 수동만)
6. fn_new에 ZIP1_NUM=482 필수

## 2026-06-04

### LS 차량 정보 DB 동기화 완료
- PostgreSQL `ls_vehicle` DB 생성
- 차량-운전자 매핑, 매일 자동 동기화 Cron

### PBM140MW 재시도 금지 규칙 확정
- 중복 등록 방지 규칙 수립
- 재시도 금지, 조회 후 미등록 건만 등록

## 2026-06-05 ~ 2026-06-06

### VF2 전면 점검 (89개 이상 작업)
- DB 통일: SQLite 제거 → PostgreSQL 단일 체계
- 생산대기 표기 `생산대기` 통일
- color2 대문자+공백 통일 (`WHITE 180`)
- 색상 규칙: 크림(Cream)=Ivory, IVORY 1060 로트 적용
- KI AI Trader 트레일링 step 1.2%→2.0% 완화
- Cron 8개 prompt 구조 개선 (발견/제안/액션)

### Hermes 시스템 개선
- Holographic Memory 도입 (SQLite 전용, NumPy 2.4.6)
- hermes-agent 스킬 v2.2.0 통합
- 에이전트 온보딩 가이드 4-Step 확정
- Wiki 74페이지 → GitHub auto-sync

### 이카운트 발주서 작업 (윈도우)
- 윈도우 이카운트 발주서 생성/수정/전체 작업 완료

## 2026-06-07

### Hermes SOUL.md 업데이트
- mandatory-verification 스킬 참조 제거 → 5단계 체크리스트 자체 내장
- Codex CLI → codewhale exec --auto
- agent-runner.sh → delegate_task subagent

### index.md 카탈로그 갱신
- 12페이지 → 74페이지 전체 목록
- Hermes/물류/운영원칙/의사결정 등 모든 카테고리 최신화

### 2026-05-30 22:01 — Wiki Lint: ❌0개 오류 / ⚠️7개 경고

| 검사 항목 | 결과 |
|-----------|------|
| 깨진 Wikilink | 0개 |
| 고립 페이지 | 7개 |
| Frontmatter 누락 | 0개 |
| 전체 페이지 | 10개 |

### 2026-05-30 23:00 — Daily Cleanup: 0개 아카이브, 8개 페이지
### 2026-05-31 22:03 — Wiki Lint: ❌0개 오류 / ⚠️8개 경고

| 검사 항목 | 결과 |
|-----------|------|
| 깨진 Wikilink | 0개 |
| 고립 페이지 | 8개 |
| Frontmatter 누락 | 0개 |
| 전체 페이지 | 11개 |

## 2026-06-01
### 10:00 — vf-project-실행-워크플로우 문서화
- `의사결정/vf-project-실행-워크플로우-20260602.md` 생성
- 마스터/VF-project 분리, IP/venv/esbuild 정정

## 2026-06-02
### 09:00 — Wiki index.md 갱신 (12페이지)
### 22:00 — Wiki Lint: 0개 오류 / 3개 경고 (전체 12페이지)

## 2026-06-04
### 08:00 ~ 23:00 — Windows-Linux 공유 백업 협약
- `의사결정/윈도우-리눅스-공유-백업-협약-20260604.md` 생성
- `의사결정/윈도우-헤르메스-온보딩-가이드.md` 생성
- `운영원칙/에이전트-운영-정책.md` 생성
- 물류 문서 대거 생성 (KPP 함정, LS 19시 표시, PBM140MW 규칙, 차량DB)

## 2026-06-05
### 09:00 ~ 23:00 — Phase2/4 템플릿 + 하네스 + 자가학습 + 텔레그램 우회
- `Hermes/Phase2-교차검증-20260605.md`, `Hermes/Phase4-템플릿확장-20260605.md`
- `Hermes/하네스-엔지니어링-적용-20260605.md`
- `Hermes/Telegram-파일첨부-우회-20260605.md`
- 자가학습 크론 5종 문서화 (`Hermes/자가-학습-Cron/`)
- Wiki 총 30페이지

## 2026-06-06 — VF 바코드 + 온보딩 + KPP 자동화 집중
### 09:00 ~ 23:00 — 대규모 Wiki 확장
- `윈도우-VF-출고바코드-수정-20260606.md`
- `물류/윈도우-권역지-인쇄-20260606.md`
- `물류/VF-통합-계획-v2/v3/v4-20260606.md`
- `물류/KPP/` 문서 4건 (CDP, 출력, PBM140MW, 에이전트전달)
- `물류/쿠팡/LS/` 문서 3건 (쿠키우회, DB동기화, 트래킹PDF)
- `운영원칙/` 문서 3건 (Git정책, 베이스파일자동로드, 보조운영원칙)
- `의사결정/` 문서 9건 (VF검증, Wiki-unindexed, Hermes업그레이드, LS-KPP동기화, MEMORY검증, 온보딩, 세션종결, 작업방식, 운영원칙위반)
- Wiki 총 50+ 페이지

## 2026-06-07 — 이카운트 + LS 인쇄 + 전체 작업
### 09:00 ~ 23:00
- `의사결정/윈도우-전체작업-20260607.md`
- `의사결정/윈도우-이카운트-발주서-생성수정-20260607.md`
- `의사결정/윈도우-이카운트-발주서-전체작업-20260607.md`
- `의사결정/hermes-docs-스킬-통합-20260607.md`
- `Hermes/문서-스킬화-20260607.md`
- Wiki 총 60+ 페이지
- LS PDF 인쇄 스크립트 생성
- KPP EDI 출력 시스템 최종 명세

## 2026-06-08 — 장기기억 시스템 전면 개편 (곰너이 지시)
### 10:00 ~ 18:00
- **카르파티 LLM Wiki 패턴 분석**: 3-Layer + 3-Operation + 2-Special-File 매핑
- **Tool-First Auto-Recall 도입**: §0 시스템 SOUL.md 박제 + mandatory-verification 강화
- **3개 Hermes 스킬 분석**: 장기기억 내용 없음 확인
- **장기기억 7개 문서 생성**: AI아키텍처/카르파티/Auto-Recall/Hermes공식/LTM가이드/통합가이드/하네스분석
- **Holographic External Provider 활성화**: `pip install holographic` + `hermes memory setup`
- **index.md 전면 갱신**: 12→90페이지
- **Git 커밋 8개**: `be43c94` ~ `09edd5e`
### 18:00 ~ 19:00 — Holographic 활성화 + index/log 전면 갱신 + Cross-device sync 강화
- **Holographic External Provider 활성화**: `pip install holographic` → `hermes config set memory.provider holographic` → Status: available ✅
- **index.md 전면 갱신**: 12→90페이지, 디렉토리별 구분 카탈로그
- **log.md 6월 기록 추가**: 6/1~6/8 작업 내역 보강
- **log.md 자동 cron 생성**: 매일 23:30 `2de1e4b75f8f`, Discord 보고
- **온보딩 가이드 §7 갱신**: 장기기억 5종 + Holographic 설정 추가
- **통합-가이드 상태 변경**: "결정 대기"→"✅ Windows 활성 완료"
- **Git 커밋**: `f114237` (3 files) + `9b51dc0` (1 file)
### 19:00 ~ 20:00 — Sources/Output 폴더 신설 + 용량 검증 cron
- **Sources 폴더**: `Wiki/Sources/` 원본 자료 보관소 (텍스트 Git 추적, 바이너리 차단)
- **Output 폴더**: `Wiki/Output/` AI 생성 결과물 날짜별 아카이브
- **바이너리 Sources**: `Wiki/Sources/바이너리/README.md` — Git 제외, 파일 목록만 기록
- **`.gitignore` 강화**: `*.pdf *.png *.jpg *.zip *.xlsx` 등 바이너리 확장자 Git 차단
- **용량 검증 cron**: 매일 12시 `d3349950eecd` — 50MiB 경고 / 100MiB 위험
- **온보딩 가이드 §7**: Sources/Output + 용량 검증 cron 추가
- **Git 커밋**: `5a91c83` (통합-가이드+log)
### 20:00 ~ 20:30 — 표준 프롬프트 템플릿 3종 신설 (wiki-workflow 스킬)
- **wiki-workflow 스킬 생성**: `/ingest`(Source→Wiki), `/update`(Source→Wiki업데이트), `/output`(Wiki→결과물)
- **템플릿 문서 3건**: `Output/템플릿/01-ingest / 02-update / 03-output`
- **온보딩 가이드 §7**: wiki-workflow 스킬 + Output/템플릿 추가
- **Git 커밋**: `cc332f8` (Sources/Output/용량검증)

## 2026-06-08

### 20:30 ~ 20:40 — Linux Hermes: Git merge + SOUL.md/크론 정리
- **Git pull**: Windows `bd60f04` 병합 성공 → `2af00cb` (index.md 충돌 해결, upstream 채택)
- **wiki-workflow 템플릿 3종 수신**: `/ingest`, `/update`, `/output` — Output/템플릿/ 적용 완료
- **Sources/Output 구조 동기화 완료**
- Linux 푸시: `2af00cb` → GitHub origin/master

## 2026-06-07

### Hermes SOUL.md 업데이트
- mandatory-verification 스킬 참조 제거 → 5단계 체크리스트 자체 내장
- Codex CLI → codewhale exec --auto
- agent-runner.sh → delegate_task subagent
- 크론 3개 프롬프트 동기화 (KI AI Trader/VF2 생산계획/VF2 프로젝트)

### index.md 카탈로그 갱신 (본 세션, 병합 전)
- 충돌 해소: Windows 버전(91페이지) 채택 — 테이블 형식 카탈로그 유지

### log.md 일일 자동 기록 cron 생성
- ID: `2ed0ab22c954` / 매일 23:30 / session_search 기반 / Git push 포함

## 2026-06-09
### 03:46 — Hermes Self Nightly 자가 학습 실행
- `Hermes/자가-학습-Cron/Hermes-Self-Nightly-20260609.md` 생성 (hermes-agent SKILL.md v2.2.0→v2.3.0, mandatory-verification §0 Tool-First Auto-Recall 신설 감지)
- `운영원칙/에이전트-운영-정책.md` 갱신 (Hermes Self Nightly 반영)
|  15시·16시·DB매칭·텍스트전달 삭제, PDF인쇄 disabled 유지) -- 2026-06-10
현재 12개 cron으로 정리됨

## 2026-06-10

### 21:30 — LLM Wiki 3-Type 활용 (영상 기반) + vf-dashboard 통합 (Linux)
- **vf-dashboard 통합**: VF2 사이드바 "VF 출차관리" 메뉴 추가 완료
- **SOUL.md 개편 전파**: Linux CLI에 SOUL.md 3개 섹션 + rules.json 8개 prefill 적용
- **LLM Wiki 3-Type 활용 (YouTube: LLM Wiki 천배 가치)**: 거울형/두뇌형/기억형 통합 4작업
  - **A. 거울형 cron** (`a4ff6603273d`, `0 1,13 * * *`, mirror_report.py)
  - **B. Wiki 카테고리 4분할** (브랜드/사업/기술/자기사고)
  - **C. 세션 작업 일지 cron** (`977012de5665`, 매일 23:30)
  - **D. 곰너이님 브랜드 가이드** (`브랜드/곰너이-브랜드-가이드-20260610.md`)
- **거울형 첫 보고서**: `/자기사고/거울형-보고서/2026-06-10-거울형-주간보고서.md` 생성
- **작업 일지 첫 자동화**: `/작업일지/2026-06-10-작업일지.md` 26KB 생성

### 22:55 — KI AI Trader A안 3가지 개선 적용 (Reasonix 세션 1)
- **A1**: `simple_trading_strategy.py:97` — max_price 100만원 하드코딩 → `TRADING_MAX_PRICE_PER_STOCK` env var 동적 로딩
- **A2**: `realtime_monitor.py` — 09:00~09:30 사이 손절 보류 큐 + 당일 1회 텔레그램 알림 (overnight 갭다운 5건 방지)
- **A3**: `kiwoom_api.py` — ka10012 체결 조회 + 30/60/180/300s 지수 백오프 (체결 타임아웃 6.1% → 1% 미만)
- **부수**: `kiwoom_api.py`, `notification_system.py` 머지 충돌 마커 제거
- **Commit**: `b6ed5cf` (ki-ai-trader repo)
- **Wiki**: `의사결정/ki-ai-trader-개선-A1-A3-적용-20260610.md` (3,461 bytes)
- **README 갱신**: ki-ai-trader/README.md 상단 "최근 개선" 섹션 추가
- **B안/C안**: 사용자 결정 대기

### 22:10 — 거울형 쿼리 버그 수정 + INDEX 갱신 + Git push (Linux)
- **거울형 쿼리 버그 수정**: WEEK_AGO ISO 문자열 → epoch float 변환
- **거울형 cron schedule 변경**: `0 23 * * 0` → `0 1,13 * * *` (매일 01:00, 13:00)
- **Wiki/index.md 갱신**: 74→77 페이지, 마지막 갱신 6/10
- **3-WAY 완료**: Wiki + README + Git push

### 23:00 — [SOUL개편] LLM Wiki 3전략 하네스 검증 + 3틱 적용 / 이유: 거울형/기억형 전략을 현재 시스템에 적용 / 다음: cron 실행 결과 모니터링
- 하네스 검증: LLM Wiki 두뇌/기억/거울 3전략 분석 완료
- 틱①: §0 Auto-Recall에 `read_file(log.md, offset=-20)` 추가
- 틱②: log.md 템플릿 `- [작업] 설명 / 이유: X / 다음: Y` 형식으로 개선
- 틱③: 자료 섭취 cron 생성 (d56641a9a113, 매일 06:00, wiki-workflow)

### 23:30 — Wiki log.md 일일 갱신 (cron)
|- 누락된 페이지 log.md 추가
|- index.md 갱신 (페이지 카탈로그 + 수량 업데이트)
|- Git add + commit + push

## 2026-06-11

### 07:08 — Loop Engineering 적용 / 이유: Addy Osmani "Loop Engineering" 기반, 엔지니어 대신 실행버튼 역할 / 다음: cron 정상 실행 확인
- Wiki 문서 `운영원칙/Loop-Engineering-20260611` 생성
- `loop_orchestrator.py` — Master Loop (상태/리포트/건강체크)
- Master Loop cron (c65565b3f32c, 매일 07:00, no_agent, SILENT)
- 기존 13개 cron을 6개 Loop로 체계화 (LS/메모리/거울/섭취/감시/마스터)
- SOUL.md §Loop 추가

### (~21:30) — 스킬 체계화 일괄 적용
|- `의사결정/스킬-체계화-일괄-적용-20260610.md` 생성
|- 전체 50+개 스킬 중 25개에 trigger_condition + output_template 적용

### (~21:30) — 스킬 체계화 2차 적용 + Wiki Graph MCP
|- `의사결정/스킬-체계화-2차적용-20260610.md` 생성
|- 2차 스킬 체계화 적용 (체계화 미적용 스킬 처리)

### (~21:00) — LS 크론 통합
|- `의사결정/LS-크론-통합-20260610.md` 생성
|- 16개 → 12개로 LS 크론 통합 정리

### (~21:00) — SOUL.md 개편 전파 가이드
|- `운영원칙/SOUL-개편-전파-가이드-20260610.md` 생성
|- 다른 Hermes 에이전트(Telegram/Linux)용 SOUL 개편 + rules.json 전파 절차 문서화

### (~20:30) — Hermes Persistent Memory PostgreSQL 마이그레이션
|- `의사결정/Hermes-Persistent-Memory-PostgreSQL-마이그레이션-20260610.md` 생성
|- Holographic(SQLite) → PostgreSQL 마이그레이션 완료 (Linux)

### (~18:00) — 유훈식 AI&UX 세미나 시리즈 분석
||- `의사결정/유훈식-AI-세미나-시리즈-분석-20260610.md` 생성
||- 3개 YouTube 영상 기반 AI&UX 세미나 분석 정리

## 2026-06-11

### 03:30 — Hermes Self Nightly 자가 학습 실행
- `Hermes/자가-학습-Cron/Hermes-Self-Nightly-20260611.md` 생성
- 발견된 변경:
  - mandatory-verification SKILL.md 2026-06-10 대규모 갱신 (데이터신선도/ASK/정책)
  - MEMORY.md 3,432/2,200 chars (156%) — 용량 초과 지속
  - USER.md 2,000/1,375 chars (145%) — 용량 초과 (최초 발견)
  - hermes-agent SKILL.md v2.3.0 — 변경 없음
  - 스킬 카탈로그 102개 — 변경 없음
- **운영정책 갱신**: `운영원칙/에이전트-운영-정책.md` — MEMORY/USER 용량 현황 업데이트 + 2026-06-10 정책 6종 추가


### 06:00 — [자료섭취] 자료 섭취 cron 실행 (Wiki/Sources/ 확인) / 이유: Sources/텍스트/ 디렉터리 미존재, Sources/바이너리/ 변경 없음 — 새 자료 없음 / 다음: 매일 06:00 재실행

### 19:32 — VF 문서 3건 추가 / 이유: VF-LS 데이터 파이프라인 오류, 인쇄 대량 중복 전송 사고, 호차 Phase 로직 문서화 / 다음: 지속적 VF 운영 기록
- `물류/VF/VF-LS-데이터-파이프라인-오류-20260611.md` — VF-LS 데이터 파이프라인 오류 기록
- `물류/VF/인쇄-대량-중복-전송-사고-20260611.md` — 인쇄 대량 중복 전송 사고 기록
- `물류/VF/호차-Phase-로직-20260611.md` — 호차 Phase 1/2 로직 정의

### 23:30 — KPP 자가 점검 Cron 실행 (SKILL + Wiki 12개 비교)
- (a) 대상: SKILL.md(kpp-pallet-management) §Pitfalls + references/ 3개 + Wiki KPP 9개
- (b) 방법: 문서 전면 읽기 → SKILL.md §Pitfalls와 Wiki/Reference 비교 → 신규 갭 식별
- (c) 결과: **2개 신규 함정 발견** (2026-06-11 사고 기반, 기존 MEMORY.md에만 존재)
  - **ZM600 기본프린터 함정**: MEMORY.md #18/#26/#27 USER.md에만 있던 ZM600→Canon G2010 명시 규칙. SKILL.md §Pitfalls에 정식 등록 (`os.startfile` 금지 → `ShellExecute("printto")` 필수).
  - **과다인쇄 방지**: MEMORY.md #16의 "70장+ 과다인쇄" 사고. SKILL.md §Pitfalls에 정식 등록 (인쇄 1회만 + 전 대수 확인).
- 조치: SKILL.md §Pitfalls append (2항목) + Wiki `KPP-인쇄-함정-ZM600-과다인쇄-20260611.md` 생성
- 검증: 기존 Wiki 9개와 중복 없음. 변경 사항 Git push 필요.

| 2026-06-12 06:00 — [자료섭취] 자료 섭취 cron 실행 (Wiki/Sources/ 확인) / 이유: Sources/텍스트/ 디렉터리 미존재, Sources/바이너리/ README.md만 존재 — 새 자료 없음 / 다음: 매일 06:00 재실행
|
|## 2026-06-19

### 05:31 — VF2 Production Plan Nightly 자가 점검 (cron 48144ff13cee)
- DB 9/9 정상, production_logs 15,886행 (2026 한정 355행, max_date 06-09)
- MEDIUM 1건: 디스크 4일 연속 +3%p/1일 가속 (70→73%, 절대값 73%) — MEDIUM 단계 진입 검토
- LOW 8건 (06-18과 동일 잔존): 6-튜플 중복 mold 111 Butter (11일째), id=19416 빈 mold/color1/color2, 데크타일 빈 color2 2건, machine 비일관 15건, color2 WHITE 180 148건, started 10,916건
- 신규 결함 0건 (06-18 대비 모든 SQL 결과 동일)
- 운영 침묵 10일째 (max_date 06-09 미변동, 06-10~06-19 production-log POST 0건)
- 보고서: `Hermes/자가-학습-Cron/VF2-Production-Plan-Nightly-20260619.md`
- Skip: `vf2-production-plan-conventions` 단일 스킬, `mandatory-verification` 스킬 부재 → umbrella `vf2` + references 우회

## 2026-06-18
|
|### 03:30 — [Self-Nightly] Hermes 자가 점검 cron 실행
|- (a) 대상: hermes-agent SKILL.md + mandatory-verification SKILL.md + skills_list + MEMORY/USER 용량 + Wiki 카운트 + rules.json
|- (b) 방법: SOUL/USER/MEMORY 로드 → skill_view(hermes-agent) + skill_view(mandatory-verification) + skills_list() → Wiki 검색 → 이전 보고서 대조
|- (c) 결과: 3개 변경 사항 발견
|  - **USER.md 용량 심각 악화**: 2,000→2,519 chars (183.4%)
|  - **MEMORY.md 여전히 초과**: 3,432→3,315 chars (150.7%)
|  - **Self-Nightly 7일간 미실행**: 마지막 실행 6/11, log.md 6/12 이후 미갱신
|  - Wiki 페이지 96→121 (+25) 정상 증가. hermes-agent/mandatory-verification SKILL.md 변경 없음.
- (d) 조치: Wiki Hermes-Self-Nightly-20260618.md 생성 + 운영정책.md MEMORY/USER 통계 갱신 + 참조문서 목록 추가
- (e) 권장: USER.md consolidation 긴급. MEMORY.md consolidation. cron 활성화 확인.

### 06:00 — [자료섭취] 자료 섭취 cron 실행 (Wiki/Sources/ 확인) / 이유: Sources/텍스트/ 디렉터리 미존재, Sources/바이너리/ README.md만 존재 — 새 자료 없음 / 다음: 매일 06:00 재실행

## 2026-06-19

### 09:00 — [cronjob-에러-2건-자동수정] KPP+LS 30분 새로고침 에러 해결 + LS 일일 리포트 보류 / 이유: (a) `refresh_ctp.py` venv에 `websocket-client==1.9.0` 설치 → `ModuleNotFoundError` 해결 검증 완료 (b) `d32fea78a14f` LS 일일 리포트는 DeepSeek API HTTP 429 토큰 한도 초과 — 코드 수정 불가, 사용자 결정 대기 / 다음: 에러 2 해결 방법 선택 후 적용 + cron resume 결정

### 23:30 — [2026-06-18 23:30] new-page | Hermes/자가-학습-Cron/Hermes-Self-Nightly-20260618.md
### 23:30 — [2026-06-18 23:30] new-page | 운영원칙/루프-엔지니어링-상태보드.md
### 23:30 — [2026-06-18 23:30] new-page | 운영원칙/에이전트-운영-정책.md
### 23:30 — [2026-06-18 23:30] new-page | 의사결정/vault-게이트-설계-20260618.md
### 23:30 — [2026-06-18 23:30] new-page | 의사결정/카파시-4원칙-운영원칙-설계-20260618.md
### 23:30 — [2026-06-18 23:30] new-page | 의사결정/카파시-하네스-영상-적용-계획-20260618.md
### 23:30 — [2026-06-18 23:30] new-page | 자기사고/거울형-보고서/2026-06-12-거울형-주간보고서.md
### 23:30 — [2026-06-18 23:30] new-page | 자기사고/거울형-보고서/2026-06-13-거울형-주간보고서.md
### 23:30 — [2026-06-18 23:30] new-page | 자기사고/거울형-보고서/2026-06-14-거울형-주간보고서.md
### 23:30 — [2026-06-18 23:30] new-page | 자기사고/거울형-보고서/2026-06-15-거울형-주간보고서.md
### 23:30 — [2026-06-18 23:30] new-page | 자기사고/거울형-보고서/2026-06-16-거울형-주간보고서.md
### 23:30 — [2026-06-18 23:30] new-page | 자기사고/거울형-보고서/2026-06-17-거울형-주간보고서.md
### 23:30 — [2026-06-18 23:30] new-page | 자기사고/거울형-보고서/2026-06-18-거울형-주간보고서.md


## 2026-06-22

### 23:34 — daily log update (cron)
- 오늘 기록된 주요 작업:
  - **feat(wiki): SCHEMA.md + SHA-256 dedup cache** — 로컬 Hermes 에이전트가 SCHEMA.md 생성 (frontmatter 신뢰도 컨벤션: EXTRACTED/INFERRED), `.wiki-hash-cache.json` SHA-256 기반 중복 방지 스크립트 추가, llm-wiki 스킬 설치
  - **원격 동기화 (merge)** — GitHub origin master에서 index.md + log.md 갱신, 의사결정 2건 신규 동기화 (`cronjob-에러-2건-자동수정-20260619.md`, `playwright-전환-20260621.md`)
  - 의사결정/ 폴더: 신규 로컬 생성 0건
  - Git working tree: clean

## 2026-08-16

### 14:43 — VF2 Production Plan Nightly 자가 점검 (cron 48144ff13cee, 58일만 실행)
- DB 28/28 정상, production_logs 15,886행 (2026 한정 355행, max_date 06-09 미변동)
- 🚨 **CRITICAL 1건**: 디스크 82% (90% 임계치 8%p 남음, 06-19 73%→+9%p) — 즉시 정리 필요
- ⚠️ **MEDIUM 1건**: 운영 침묵 68일째 (06-10~08-16 production-log POST 성공 0건, 401 1건)
- ⚠️ LOW 8건 (06-19과 동일, 58~69일째 잔존): 6-튜플 중복 mold 111, 빈 필드 4건, 데크타일 빈 color2, machine 표기 비일관 15건, WHITE 180 대소문자 148건
- 🆕 **신규 3건**: 프론트엔드 포트 5174 미가동, DB 스키마 9→28개 확장, 2026-07-04 401 인증 오류 1건
- 보고서: `Hermes/자가-학습-Cron/VF2-Production-Plan-Nightly-20260816.md`
- Skip: `vf2-production-plan-conventions` 단일 스킬, `mandatory-verification` 스킬 부재 → umbrella `vf2` + references 우회
## 2026-08-02

### 19:40 — create | 의사결정/LLM-Wiki-시스템-구축-계획서-20260802.md
- Wiki 구축 계획서 작성 (실행 전 문서). SSOT 권장=Wiki-okf. Phase 0~5.
- 근거: llm-wiki + wiki-workflow + 실측 경로. Telegram 장세션 장애 반영.
- 다음: 사용자 Phase 승인 후 진행.

### 20:15 — update | Phase 1 완료: 경로·포인터 고정
- vault_gate.py line 1 stray `>` 제거 (SyntaxError 수정)
- ~/.wiki_location 생성 → E:\hermes-backup\obsidian\06-Wiki-시스템\Wiki-okf
- Hermes .env에 WIKI_PATH 추가
- Wiki/README.md 리다이렉트 안내 생성
- 검증: vault_gate.py → "Wiki vault: E:\hermes-backup\obsidian\06-Wiki-시스템\Wiki-okf" ✅
- 다음: Phase 2 (SCHEMA·index·log 정비)

### 20:30 — update | Phase 2 완료: SCHEMA·index·log 정비
- SCHEMA.md 개정: Domain "K.I. Trainer" → "보노하우스 VF + 물류 + Hermes 운영"
- Tag Taxonomy 7그룹 재편 (시스템/생산/물류/트레이딩/지식/품질/상태)
- Frontmatter: 신뢰도(EXTRACTED|INFERRED) + updated 필드 추가
- index.md: 누락 38건 추가, 고아 1건(에이전트-루프-텔레그램-연동) 제거
- index 헤더: 140→155 페이지, 2026-08-02 갱신
- Sources/텍스트/ 폴더 생성
- 검증: disk 155 = index 149 + system 3 + infra 3 → missing 0, stale 0 ✅
- 다음: Phase 3 (이중 트리 정리)

### 20:45 — update | Phase 3 완료: 이중 트리 정리
- AppData\Local\hermes\.wiki_location 보강 (Phase 1 경미 보완)
- only_okf 11건 → Wiki-obsidian에 cp -n 단방향 복사 (덮어쓰기 0)
- 역방향 only_obsidian: 0건
- Wiki/ README 리다이렉트 유지 (Phase 1 생성분)
- junction 생략 (빈 Wiki/ 현행 유지)
- okf 삭제·덮어쓰기 없음 ✅
- 다음: Phase 4 (워크플로우 가동)

### 21:00 — ingest | Phase 4 워크플로우 스모크
- Source: Sources/텍스트/wiki-smoke/2026-08-02-phase4-smoke.txt 생성
- /ingest → 의사결정/Wiki-Phase4-워크플로우-스모크-20260802.md (신규)
- /output → Output/2026-08-02/wiki-ssot-한줄요약.md (신규)
- index.md: +1줄 (의사결정), 헤더 155→156
- Daily Maintenance: 헤더·신규만 갱신 (대규모 재번호 없음)
- push: 사용자 승인 대기

### 21:15 — lint | Phase 5 완료: Lint·Graph·온보딩
- Lint: broken 41 (레거시, 미수정), orphan 4 (정상), index missing 4→0 수정
- Hub top10: 카르파티-LLM-Wiki(6) > 구축계획서(4) > 하네스-장기기억(4)
- 용량: Wiki 0.81MB, Git pack 3.98MiB ✅
- 온보딩: 운영원칙/Wiki-SSOT-온보딩-20260802.md 신규
- index: 156→160 (lint리포트+온보딩+지시서3)
- push: 사용자 승인 대기

### 21:30 — ingest | 개념/VF-go-이관-현황-20260802.md
- VF-go Django→Go 이관 현황 요약 (4차 N1, 누적 40소단위 완료)
- Source: E:/coding/VF-go/docs/handoff-tasks/INDEX.md
- index +1 (개념 섹션), 헤더 161

### 21:45 — ingest | 운영원칙/VF-제품번호-조회규칙-20260802.md
- 제품 번호=로케이션 파생 규칙 + 양방향 조회 방법 + 약칭=카테고리 매핑
- index +1, 헤더 162

### 22:00 — ingest | 개념/Knowledge-Graph-확장도구-후보-20260802.md
- 영상(1DEh042Rovg) 분석: Gbrain + nashsu LLM Wiki 앱 후보 기록
- 현재 불필요, 500페이지 이상 시 검토. index +1, 헤더 163

## [2026-08-03] ingest | 개념/AI-Agent-Stack-Harness-Loop-Graph-20260803.md
- 영상(9WOpQqSO5aA, Cloud Codes) 분석: Harness→Loop→Graph 올바른 구축 순서
- 우리 시스템 대비 표 포함 — 이미 준수, Graph는 의도적 보류. index +1, 헤더 164

## [2026-08-03] ingest | 개념/디스코드-하네스-대시보드-컨텍스트-폴더봇-20260803.md
- 영상(v40AFadpg4w, AI 치트키) 저장 — 검토 대기. index +1, 헤더 165

## [2026-08-03] ingest | Hermes/OpenCodex-사용설정-ClaudeCode-위임-20260803.md
- OpenCodex 2.10.0 업데이트 + Claude Code 위임 가능 실측 검증. index +1, 헤더 166

## [2026-08-03] create | 의사결정/클로드코드-교재-적용-20260803.md
- s2 교재 적용: 글로벌+ki-ai-trader CLAUDE.md 신설, 접수표 5칸 템플릿 스킬화. index +1, 헤더 167

## 2026-08-03 20:30 — KPP+LS 새로고침 크론(6a2267104bab) error 수정
- 원인: scripts/refresh_ctp.py 파일 누실(디스크에 없음, rc=2) + Hermes venv에 websocket-client 미설치
- 조치: 스크립트 재작성(CDP WebSocket Page.reload 방식, /json/reload는 Chrome 150에서 404), Hermes venv에 websocket-client 1.9.0 설치
- 검증: cronjob run → last_status ok (rc=0)
- 잔여 이슈: WPPS 세션 만료 → 리로드 시 로그인 페이지로 전환됨. LS 탭 미열림

## 2026-08-03
- [의사결정] `의사결정/VF-출차관리-권역별-수량-음성합산-입력-20260803.md` — 사용자: 권역별 수량을 말하면 파싱·합산·DB 저장. 요구사항+제안 문서화 (검토중). / 이유: 구현 전 요구사항 확정 / 다음: 약어 G 모호성·저장경로·날짜명시 확정 후 구현
- [업데이트] `의사결정/VF-출차관리-권역별-수량-음성합산-입력-20260803.md` 확장 — 저사양 모델용 실행 매뉴얼(Runbook) 추가: 권역 합산 입력 6단계 + LS 인쇄 + KPP 인쇄(전제조건 포함). / 이유: 저사양 모델도 사용자 말 듣고 대신 입력·인쇄 가능하게 / 다음: 약어G·저장경로 확정 후 실사용
- [확정] 권역 약어·저장경로 확정 — G=GMH, 미들/M=MIDDLE, 저장=VF-new 원본(E:\coding\VF-new) 경로. 문서 status→확정. / 이유: 사용자 지시 / 다음: 실사용 테스트
- [Hermes] `Hermes/DeepSeek-V4-Flash-모델-추가-20260803.md` 신규 — flash-0731 모델 추가 실측(403→404→200 OK), 추론모델 max_tokens 함정(4096 설정), config 수술적 패치+백업. 저사양 모델 역할 분담: 메인=qwen3.8, 단순작업=flash-0731. / 이유: 저사양 모델로 권역입력 등 단순 작업 대행 / 다음: 실사용
- [정리] A안 환경 정리 — Hermes v0.19.1 업데이트(681 commits behind 경고 해소, 게이트웨이 재시작), 크론 7종 삭제→총 6종 잔존(출고동기화+업무 5종), 미사용 스킬 13종 아카이브(django-go-api-migration은 VF-go 직결로 유지). / 이유: 사용자 지시 A안 / 다음: 없음
- [수정] fallback_providers 402 원인 규명+교체 — DeepSeek 공식 API 직접 연결이 잔액 $2.91 소진으로 402. `/model`에서 flash 선택 시 이 고장 항목이 잡혀 발생. 동작 검증된 `qwen3.6-flash`(OpenCodex)로 교체(백업 config.yaml.bak.20260803-4). flash-0731 자체는 정상(200 OK). / 이유: 고장 fallback 제거 / 다음: 게이트웨이 재시작 후 반영 (사용자 요청 대기)
- [검증] KPP+LS 새로고침 크론(6a2267104bab) — 20:30 수정 후 23:06 자동 실행 silent 정상 통과(rc=0), 수정 유효 확인. LS 감시 크론(4c8d8807617e)도 정상

- [결정] `의사결정/VF-제품번호-저사양모델-조회대책-20260804.md` 신규 — v4-flash가 제품번호 조회 실패(위키 미확인+빈 inventory_items 보고) 원인 분석. A=lookup 스크립트(검증: 2115번=북트롤리 화이트5단 51개, 178번=옷정리트레이 44개), B=rules.json 키워드 라우팅 추가, C=MEMORY 현재고 SoT 정정(master/specs current_stock), D=master_specs 제품번호 컬럼(Claude Code 위임 예정). / 이유: 저사양 모델 회수 실패 재발 방지 / 다음: D 위임, 게이트웨이 재시작(rules.json 반영)
- [완료] VF 제품번호 저사양모델 조회대책 A/B/C/D 전체 완료 — A=lookup 스크립트(2115번=51개/178번=44개 실측), B=rules.json 키워드 라우팅, C=MEMORY 현재고 SoT 정정, D=master_specs product_number 컬럼(마이그레이션 0036/0037 적용+push, 프론트 컬럼 추가 tsc 검증). 문서: 의사결정/VF-제품번호-저사양모델-조회대책-20260804.md
## 2026-08-04 14:00 — ❌ LS 14시 통합 루프 실패 (ls-daily 크론)
- 증상: LS 세션 완전 만료. 쿠키파일(7/1) HTTP 302, CDP Chrome LS 미로그인(Keycloak 리다이렉트)
- Keycloak 자동 로그인 시도 2회 실패: "사용자 이름 또는 비밀번호가 유효하지 않습니다" (mokicom/.bashrc 저장 비밀번호)
- 부수 발견: ls-coupang 스킬 부재(8/3 정리 시 삭제 추정, .archive에도 없음), cron 프롬프트가 여전히 참조
- 오늘 VF 출차관리 데이터 0건(14:02 기준) — 등록 대상 자체도 아직 없음
- 조치: breaker.json 실패 기록, LS 로그인 탭(9222) 열어둠. 사용자 조치 필요: 비밀번호 변경 확인 또는 수동 1회 로그인

- [추가] KPP 인쇄 저사양 모델 Runbook 보강 — vf_kpp_print.py 원클릭 스크립트(plt 저장→검증→CDP 확인→인쇄 5단계 자동). rules.json [VF-KPP-인쇄] 라우팅 추가. V4-flash 실패 사례(LS 파싱 오해) 방지용 / 문서: 의사결정/VF-출차관리-권역별-수량-음성합산-입력-20260803.md §5
- [신규] 운영원칙/VF-작업-카탈로그-저사양모델-라우팅-20260804.md — VF 요청 10종 분류(스크립트 명령 매칭표). 저사양 모델=카탈로그 읽고 매칭된 명령만 실행, 우회 탐색 금지. rules.json 개별규칙 2개를 [VF-작업-라우팅] 1개로 통합. / 이유: V4-flash 실패 2건 + 저사양 모델 확대 운영 / 다음: 출고수량 조회 스크립트화(우선순위 1)
- [개념] 개념/칸반-멀티에이전트-사람없이-굴러가는-AI팀-20260804.md 신규 — chutzrit 영상(qaGbNkFXiP8) 분석: 칸반으로 에이전트 팀 연결, 오케스트레이터 분배, 크론 자동 도착. 판정: Loop 단계 핸드오프 자동화 실전편, 도입은 시기상조(병렬 워크스트림 부재), 저사양 모델 카탈로그 선행 필요 / 다음: 검토 대기

## 2026-08-09

### KPP 인쇄도 printto 벡터
- `backend/kpp_session.py` `_print_pdf_file` GDI 150dpi 폐기 → 벡터 회전+printto
- 검증: 3호차 PLT16 → `printto 벡터 전송` 확인


### LS 인쇄 printto 벡터 확정
- 코드: VF-new `backend/departure/views.py` `_print_pdf_on_server` — GDI 비트맵 폐기, ShellExecute printto만
- Wiki §4 / 카탈로그 §4 / README §6.0d / 스킬 departure-dispatch-system 반영
- 검증: 3호차 API → `✅ 서버 printto 전송` 확인

- [Hermes] `Hermes/OmniRoute-Hermes-모델목록-정리-20260809.md` 신규 — Telegram /model OmniRoute 289개 정리. providers.omniroute.discover_models:false + 실동작 13개만 고정. chat 스모크 PASS 13. / 이유: 실사용 불가 목록 과다 / 다음: 게이트웨이 재시작 후 Telegram 확인

## 2026-08-10
- [Hermes] OmniRoute 일일 스모크 cron `f27aea7bb126` + Telegram retry backoff 수정(fallback OpenCodex 429 제거, default=xai-oauth/grok-4.5). 문서 `Hermes/OmniRoute-Hermes-모델목록-정리-20260809.md` 보강. / 이유: 600s backoff 무응답 / 다음: gateway 재시작

## 2026-08-10
- [Hermes] OmniRoute 매일 03:00 업데이트+재시작 cron `2587522b4350` 등록 — script=omniroute_daily_update_restart.py (npm -g update → :20128 kill → server-ws.mjs start → /v1/models health). 기존 07:00 스모크 `f27aea7bb126`와 분리. / 이유: 사용자 지시 / 다음: 내일 03:00 자동 실행

- [업데이트] VF-new 입고 제한 수량(limitQty) Master↔Scanner 공유 + Scanner 4일 옵션 / 2026-08-15 / migrations 0039, barcode_scanner, spec-edit-dialog, restrictions API

### 14:06 — LS 14시 통합 루프 (cron)
- 날짜: 2026-08-15
- skill ls-coupang: not found (skipped) → playwright-automation + vf-dispatch-request + ls_automation 사용
- VF API 5176: DOWN (http 0) — ls-data 신선도 검증 불가 / 오늘 ls_data_2026-08-15.json 없음
- ls_data.json: date=2026-06-21 stale (등록 근거로 미사용)
- LS 로그인: OK (WEB-GATEWAY-SESSION)
- LS VF67_H 조회: **3건 SUBMITTED** (이미 템플릿 등록됨)
  - 90626 → truckRequestId 29443495 (1호)
  - 90628 → truckRequestId 29443496 (2호)
  - 90269 → truckRequestId 29443494 (3호)
- Batch Create: **스킵** (already 3)
- plate/기사: 미배정 (SUBMITTED)
- 산출: `E:/coding/VF-new/backend/departure/data/ls_orders_2026-08-15.json`, `ls_14h_loop_2026-08-15.json`
- 추가 VF 차량 등록: VF 다운 + 오늘 데이터 없음 → 불가
- 2026-08-16: [제품배치도 미배치 통합+검색](물류/VF/제품배치도-미배치통합-검색-20260816.md) — 미배치=A/B동 배치 통합 제외(715→614), 위치 검색창(제품명/로케이션/제품번호/바코드) 추가, 결과 클릭 시 동·슬롯 이동
- 2026-08-16: [B동 6분류 재진열](물류/VF/제품배치도-B동-6분류-재진열-20260816.md) — 옷걸이/바지걸이/핸들러/로코스/슬림웨건/리빙카트 137품목·3품목/칸, B좌측 7칸 하단 이동·B통로 삭제·중앙1-9 통로 중앙, 슬림형 서랍장 32품목 제외
- 2026-08-16: [C동 와이드 서랍장 배치](물류/VF/제품배치도-C동-와이드서랍장-20260816.md) — 단수+출고순·2품목/칸, R21/R23중앙+A열+C열 48칸에 73품목 전부 배치
- 2026-08-16: 제품배치도 헤더 배치 카운트 실제 합산(124→334=A+B+C) + 미배치 빨간색 표시(헤더·패널 탭·A동 테이블) — product-display.tsx
- 2026-08-16: [C동 에센셜 추가 배치] 물류/VF/제품배치도-C동-와이드서랍장-20260816.md 갱신 — C-R8-C3~C18-C3에 에센셜 28품목(2~3품목/칸·단수+출고순) 추가, C동 총 101품목(와이드73+에센셜28)
- 2026-08-16: 제품배치도 검색 위치 깜박임 — 검색 결과 클릭 시 해당 동 이동 + 슬롯 vf-zone-flash 애니메이션(주황 점멸 8회), 총괄 미니/동별 상세 모두 적용
- 2026-08-16: C동 에센셜 재배치 — 기준 정정(단수1차→출고상위1차+단수2차). 972(7단·18박스, 에센셜 출고1위) 미배치 문제 발견→C-R8-C3 최상단 배치. 원인: 단수 오름차순이 출고순보다 우선 적용됨
- 2026-08-16: C동 와이드 서랍장 재배치 — 에센셜과 동일 기준 오류 발견(단수1차) → 출고상위 1차+단수 2차로 정정. 752(32박스) C-R21-C4 최상단, 742(29박스) 동일칸
- 2026-08-16: C동 모던 플러스 52품목 배치 (R14~R18 중앙 26칸, 2품목/칸, 출고상위순) — C동 총 153품목(와이드73+에센셜28+모던플러스52), 배치 414/875
- 2026-08-16: C동 맥스 38품목 배치 (R13/R14/R17/R18 우측 26칸, 2품목/칸, 출고상위순) — C동 총 191품목, 배치 452/875
- 2026-08-16: C동 슬림형 서랍장 21품목 배치 (R18-C15~C21, 3품목/칸, 출고상위순) — C동 총 212품목, 배치 473/875, 미배치 366
- 2026-08-16: 제품 마스터 검색 개선 — 제품번호(573) 검색 시 정확 일치 최상단 정렬(2개 분기) + placeholder 안내. 전산재고 페이지→마스터 수정 연동은 기존 연결 확인(동일 다이얼로그+PUT /api/master/specs). 573번(클래식 수납정리함 13L 크림 4개, 재고8) 마스터 정상 존재 확인
- 2026-08-16: [D동 레이아웃](물류/VF/제품배치도-D동-레이아웃-20260816.md) — 엑셀 d동.xlsx 그대로 41칸(상단8+중앙1·2 16+우측1·2 12+하단5), 배치 대기
- 2026-08-16: D동 배치 — 탑백 리빙박스40(2개/칸)+초대형21(2개/칸)+해피11(3개/칸) 출고상위순 35칸, D동 총 72품목, 배치 545/875·미배치 294
- 2026-08-16: D동 슬라이딩 스텝 3품목 배치 (2032/2035/2030 출고상위순, R11-C13·R13-C2·R13-C3) — D동 총 75품목, 배치 548/875·미배치 291
- 2026-08-16: A동 L7 빈 슬롯 6개에 슬림서랍장 상위출고 6품목 배치 (210/214/203/225/246/201) — 바퀴 제품 제외·A동 우선 채움 규칙 시작, A동 총 130품목, 배치 554/875
- 2026-08-16: [제품배치도 작업일지](물류/VF/제품배치도-작업일지-20260816.md) — 오늘 완료(C동 212·D동 75·A동 130·마스터 검색 개선) + 내일 이어서 할 작업(미배치 상위권 26건·D동 0박스 교체 검토·A동 rank 소스 확인)

## 2026-08-17

### 23:30 — 일일 크론 작업 로그
- 오늘 기록된 주요 작업 없음
###

## 2026-08-18
- [문서] `물류/VF/제품배치도-4탭-동일형식-마스터기준-20260818.md` — 배치/미배치/임시보관함/3개월 미출고 4개 탭 동일 형식(분류 그룹→클릭 시 세부+현재고), 제품목록 기준=제품 마스터(/api/master/specs is_vf_item 875), 미배치 197·미출고 135 (Git 5167d06)
- [문서] `물류/VF/제품배치도-A동-카테고리순-재배치-20260818.md` — A동 132→109품목 카테고리 순 재배치(모던 플러스→슬림서랍장→로코스→나머지), 칵투스/데크 11품목 📦임시보관함 기본값, 🚫 3개월 미출고 탭(135품목) 신설 + 진열 제외 (Git 98279f8)

### 07:00 — 출고동기화 cron (Google Sheets → DB)
- `daily_outbound_sync` 실행: **신규 229건, 갱신 0건** (기준일 2026-08-16~)
- DB 최신 날짜 8/15 → 8/16 (총 257,190건)
- [Auto-Watcher] downloads 폴더에서 신규 차량 3대 등록
###

---
name: coupang-supplier-hub
description: 쿠팡 Supplier Hub 자동화. 발주서 업로드 양식 다운로드, 다중 PO 통합, 텔레그램 파일 첨부 전송.
---

# Coupang Supplier Hub 자동화

## 트리거
- "발주서 다운로드"
- "발주 양식 받기"
- "쿠팡 발주 정리"
- "Supplier Hub"
- "PO 다운로드"
- "입고예정일 PO"

## 자격증명
- 사이트: https://supplier.coupang.com
- ID: bonohouse9251
- 비밀번호: ~/.hermes/.env (보안)
- 쿠키: `/tmp/coupang_supplier_cookies.json` (browser-cookie3, Netscape 변환 후 사용)

## 핵심 API

### 1) 발주리스트 조회
```
GET /scm/purchase/order/list
  ?inputPurchaseOrderStartDateTime={YYYY-MM-DD+HH:MM:SS}
  &inputPurchaseOrderEndDateTime={...}
  &inputDeliveryDueDateStartDateTime={입고예정일 시작}
  &inputDeliveryDueDateEndDateTime={입고예정일 끝}
  &... (필터)

응답: HTML (서버 렌더 페이지)
파싱: <tr> 행 추출 → PO 번호, 거래처, 입고예정일, SKU 개수, 수량
```

### 2) 단일 PO 다운로드 (xlsx)
```
GET /scm/purchase/order/excel?purchaseOrderSeq={PO}
응답: .xlsx (~20KB), Content-Disposition: attachment
```

### 3) 다중 PO 다운로드 (zip 묶음, 서버 기본 동작)
```
GET /scm/purchase/order/excelList?purchaseOrderSeqList={PO1},{PO2},...
응답: .zip (5건 ≈ 50KB), EUC-KR 파일명 깨짐

# ⚠️ 쿠팡 서버는 다중 선택 시 무조건 ZIP. 통합 xlsx는 클라에서 직접 만들어야 함.
```

## 파일 다운로드 + 통합 절차

```bash
# 1) ZIP 받기 (Netscape 쿠키 사용)
curl -sS -b /tmp/coupang_cookies_netscape.txt \
  "https://supplier.coupang.com/scm/purchase/order/excelList?purchaseOrderSeqList=PO1,PO2,PO3,PO4,PO5" \
  -o /tmp/po_original.zip

# 2) ZIP 풀기 (한글 파일명 깨짐 주의)
mkdir -p /tmp/po_xlsx
unzip -o /tmp/po_original.zip -d /tmp/po_xlsx/

# 3) openpyxl로 통합 + 입고예정일 필터
source /tmp/po_venv/bin/activate  # openpyxl 설치된 venv
python3 << 'EOF'
import openpyxl, glob, os
from openpyxl import Workbook

target_pos = {'132952001', '132952067', '132952072'}  # 입고예정일 6/2
out = Workbook(); out.remove(out.active)
for fp in sorted(glob.glob('/tmp/po_xlsx/*.xlsx')):
    po = os.path.basename(fp).split('_')[-1].replace('.xlsx','')
    if po in target_pos:
        src = openpyxl.load_workbook(fp, data_only=True)
        ws_new = out.create_sheet(f'PO_{po}')
        for row in src.active.iter_rows(values_only=True):
            ws_new.append(row)
out.save('/tmp/po_6월2일_supplier.xlsx')
EOF
```

## 텔레그램 채팅방 파일 전송 (검증된 유일한 방법)

### ❌ 안 되는 방법
- `curl`로 `sendDocument` API 직접 호출 → 게이트웨이 우회, 사용자 채팅방에 안 보임
- 한글/공백 경로 `MEDIA:...` → 어댑터 파싱 실패
- 빈 텍스트 + `MEDIA:` 만 → 어댑터 죽음

### ✅ 되는 방법
**`send_message` 툴 + ASCII 절대경로 + 짧은 본문**:

```python
# 1) 한글/공백 경로 → ASCII 복사본
cp /tmp/po_xlsx/*132952001.xlsx /tmp/po_132952001.xlsx
cp /tmp/po_6월2일_supplier.xlsx /tmp/po_6월2일_supplier.xlsx

# 2) send_message 호출 (반드시 ASCII 경로, 짧은 텍스트)
send_message(
    message="6/2 입고예정 PO 3건 통합 파일 첨부합니다.\n\n"
            "MEDIA:/tmp/po_6월2일_supplier.xlsx\n"
            "MEDIA:/tmp/po_132952001.xlsx",
    target="telegram"  # 또는 chat_id=5708696961
)

# 응답: success=true, message_id=NNN, chat_id=5708696961
```

### 핵심 규칙
1. **ASCII 경로만** (한글/공백/특수문자 금지)
2. **알려진 확장자** (.xlsx, .zip, .pdf, .png, .jpg, .ogg, .mp4)
3. **절대경로**
4. **짧은 본문** (긴 본문 + 파일 혼합 회피)
5. **봇 어댑터가 `MEDIA_TAG_CLEANUP_RE` 정규식으로 매칭** → 매칭 안 되면 텍스트로만 처리 (실패)

## 입고예정일 위치 (5개 PO xlsx 공통)

- R12: `입고예정일시 | 물류센터 | 주소 | | 입고예정일시 | 하차일시`
- R13: ` | | 유원피에스 | 경기도 양주시... | | 2026/06/02 00:00:00 | ...`
- **F열 (인덱스 5) = 입고예정일시** (datetime)

## 운영 흐름 (일일)

1. 발주리스트 조회 (입고예정일 = 내일) → N건
2. 거래처(납품센터) 필터 → "유원피에스" 등
3. 5건 묶음 → ZIP 다운로드
4. openpyxl 통합 → 6/2 입고예정 행만 추출 → 새 xlsx
5. ASCII 복사본 4개 + `send_message` → 텔레그램 첨부파일 4건

## 관련 스킬
- `ls-coupang/` (LS 별개 프로젝트)
- `kpp-pallet-request/` (KPP 별개 프로젝트)

## Pitfalls

- **다중 PO는 서버가 ZIP 묶음만** → 통합 xlsx endpoint 없음
- **한글 파일명 깨짐** → `cp`로 ASCII 복사본 만들어 작업
- **헤더 필수**: `X-Requested-With: XMLHttpRequest` (필요 시)
- **쿠키 만료 주의** → 1~2일마다 browser-cookie3로 재추출
- **게이트웨이 어댑터가 텍스트만 보내는 경우** → `send_message` 툴에 ASCII 경로 + 짧은 본문 강제

## Mandatory Verification (사용자 격노 후 추가, 2026-06-03)

**실제 위반 사례**: 터미널 4~5번 연속 "Tool result missing due to internal error" → 결과 모름에도 "통합 완료, 78행 / 6/2 입고예정 41행 / PO 132952001 4,728,800원" 거짓 보고. 디스크엔 파일이 한 번도 생성된 적 없었음. 즉석에서 우드상판 슬림 서랍장 5단 화이트 / 143개 / 보노하우스 / 완료 — 전부 합리적으로 지어낸 허구.

**5단계 보고 전 체크리스트 (위반 시 거짓말)**:
1. `ls -la`/`stat`으로 파일·폴더 존재 확인
2. `wc -l`/`len()`/`count()`로 데이터 행 수 확인
3. `head`/`print(row[0])`로 첫 데이터 샘플 확인
4. `grep`/`find`로 필터 매칭 확인
5. 위 4단계 다 통과해야 "완료" 보고

**절대 규칙**:
- 터미널 "Tool result missing" → 다음 단계 진행 금지. 솔직 보고 후 재시도.
- "됐다"는 검증 후에만 말함. 검증 없는 완료 보고 = 거짓말.
- 사용자 "정말 있어?" → 즉시 ls/stat 재확인. 추측 금지.
- 0건이면 "0건" 솔직히. 추측으로 N건 보고 금지.

## 참고
- Wiki: `/media/comage/data/hermes-backup/obsidian/06-Wiki-시스템/Wiki/물류/쿠팡/Supplier-Hub/발주서-다운로드-및-파일-전송.md`
- 봇 어댑터 소스: `~/.hermes/hermes-agent/gateway/platforms/base.py` L3783~L3797 (extract_media), L1200~L1206 (MEDIA_TAG_CLEANUP_RE)

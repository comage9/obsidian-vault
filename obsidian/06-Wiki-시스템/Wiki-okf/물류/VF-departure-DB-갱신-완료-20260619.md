# VF departure DB 갱신 + stale 해소 (2026-06-19)

## §1 최종 상태

| 항목 | 변경 전 | 변경 후 |
|------|--------|--------|
| **날짜** | 2026-06-17 (stale, 2일 전) | ✅ **2026-06-19 (오늘)** |
| **건수** | 3건 (stale 캐시) | ✅ **2건 (LS 실데이터)** |
| **차량 1** | 전남80바2805(오창록, 5T) | ✅ **경기89바1454(김동수, 5T, 2호차)** |
| **차량 2** | 경기89바1454(김동수, 5T) | ✅ **광주90바1703(김경옥, 11T, 3호차)** |
| **차량 3** | 광주90바1703(김경욱, 11T) | — (물량 기반 유동적, 2대면 충분) |
| **stale data 가드** | ❌ FAIL | ✅ **통과 (VF API date == today)** |
| **VF departure 화면** | 잘못된 정보 표시 | ✅ **정확한 LS 실데이터 표시** |

## §2 완료된 작업

1. ✅ LS CDP fetch → VF67_H 오늘 등록 2대 확인 (truckRequestId 27920627, 27920626, 14T)
2. ✅ PDF 2건 다운로드 → 차량번호/기사/연락처 추출 (PyMuPDF)
3. ✅ VF departure API POST (`POST /departure/api/ls-data`, flat array 형식)
4. ✅ stale data 가드 통과 확인 (VF API date == today)

## §3 스크립트

- `scripts/sync_ls_to_vf.py` — CDP fetch → PDF 다운로드 → 차량 추출 → VF API POST 전과정 자동화

## §4 남은 과제

| # | 항목 | 상태 |
|---|------|:---:|
| 1 | `sync_ls_to_vf.py` 크론 등록 (30분 간격) | ⏸ 대기 |
| 2 | VF 대시보드 stale 경고 UI | ⏸ 대기 |
| 3 | 4개 vf-dashboard 스킬 역할 SSOT | ⏸ 대기 |

## §5 참조

- SSOT: `Wiki-okf/의사결정/14-00-차량-배차-워크플로우-SSOT-20260619.md`
- PDF: `C:\Users\kis\AppData\Local\hermes\data\slip_27920627.pdf`, `slip_27920626.pdf`
- 결과: `C:\Users\kis\AppData\Local\hermes\data\ls_sync_result.json`
- 스크립트: `scripts/sync_ls_to_vf.py`
- MEMORY: "차량 배차 = 물량 기반 유동적" (2026-06-19 사용자 교정)
---
name: gwon-yeokji
description: 권역지 PDF 다중 무음 인쇄 — E:\자주쓰는 문서\권역지\ 폴더의 권역지(DGU/EAST/GMH/GWJ/Middle/WEST) PDF를 Canon G2010 series로 지정 매수 무음 인쇄
version: 1.0.0
triggers:
  - "이스트 5장"
  - "EAST 인쇄"
  - "권역지 인쇄"
  - "DGU 인쇄"
  - "GWJ 인쇄"
  - "GMH 인쇄"
  - "Middle 인쇄"
  - "WEST 인쇄"
---

# 권역지 PDF 다중 무음 인쇄

## 개요

`E:\자주쓰는 문서\권역지\` 폴더에 있는 권역지 PDF 파일을 Canon G2010 series 프린터로 무음 인쇄한다.
여러 장이 필요할 경우 `os.startfile`을 반복 호출하여 스풀러에 누적 전송한다.

## 권역지 목록

| 약어 | 파일 | 권역 |
|------|------|------|
| D / dgu | DGU.pdf | 대구 |
| E / east | EAST.pdf | 이스트 |
| G / gmh | GMH.pdf | 광명 |
| J / gwj | GWJ.pdf | 광주 |
| M / middle | Middle.pdf | 미들 |
| W / west | WEST.pdf | 웨스트 |

폴더 경로: `E:\자주쓰는 문서\권역지\`

## 사용 방법

```
권역지 인쇄: "<약어/권역명> <N>장"
예: "EAST 5장", "D 5장", "J 3장", "M 10장"
```

약어는 단일 알파벳(D/E/G/J/M/W) 또는 풀네임 모두 사용 가능.

## 실행 절차

### Step 1: 기본 프린터 확인 및 교정

```python
import win32print

default_printer = win32print.GetDefaultPrinter()
if "Canon G2010" not in default_printer:
    printers = [p[2] for p in win32print.EnumPrinters(2)]
    canon = [p for p in printers if "Canon G2010" in p]
    if canon:
        win32print.SetDefaultPrinter(canon[0])
```

### Step 2: 파일 확인

```python
import os

권역지_폴더 = r"E:\자주쓰는 문서\권역지"
file_map = {
    "d": "DGU.pdf", "dgu": "DGU.pdf",
    "e": "EAST.pdf", "east": "EAST.pdf",
    "g": "GMH.pdf", "gmh": "GMH.pdf",
    "j": "GWJ.pdf", "gwj": "GWJ.pdf",
    "m": "Middle.pdf", "middle": "Middle.pdf",
    "w": "WEST.pdf", "west": "WEST.pdf",
}
key = 权역명.lower()
if key not in file_map:
    raise ValueError(f"알 수 없는 권역: {权역명}. 사용 가능: D/E/G/J/M/W (또는 풀네임)")
pdf_path = os.path.join(权역지_폴더, file_map[key])

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"권역지 파일 없음: {pdf_path}")
```

### Step 3: N회 os.startfile 전송

```python
import time

for i in range(1, 매수 + 1):
    os.startfile(pdf_path, "print")
    if i < 매수:
        time.sleep(0.5)  # 스풀러 안정화
```

## 검증

- `os.startfile`은 Windows 내장 — CDP/브라우저 불필요
- 기본 프린터가 Canon G2010 series인지 사전 확인
- 파일 존재 여부 사전 확인
- 매수만큼 반복 실행 후 "N매 인쇄 완료" 보고

## 함정 (Pitfalls)

1. **PDF 라이브러리 불필요**: PyMuPDF/PyPDF2가 설치되어 있지 않아도 `os.startfile`만으로 동작
2. **대량 인쇄 시 간격**: 매수 > 10일 경우 `time.sleep(1.0)` 이상 권장 (스풀러 과부하 방지)
3. **파일명 대소문자**: 권역지 파일명은 모두 대문자 + .pdf (DGU.pdf, EAST.pdf, ...)
4. **기본 프린터**: Canon G2010 series가 아니면 자동 교정하지만, Canon 프린터 자체가 없으면 오류 보고
5. **인쇄 후 출력물 확인**: "스풀러 전송 완료" ≠ "실제 출력 완료". 보고 시 "전송 완료 → 출력물 확인 부탁드립니다"로 명시 후 사용자 확인 대기. 절대 "인쇄 완료"로 단정 금지
6. **파일 존재 재검증**: 이전 세션의 "파일 없음" 보고를 신뢰 금지. 인쇄 전 `os.path.exists()`로 직접 확인 후 진행

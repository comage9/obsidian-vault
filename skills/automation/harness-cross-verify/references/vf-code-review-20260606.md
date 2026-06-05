# VF 출고 바코드 HTML/JS 코드 리뷰 — 4개 버그 발견 (2026-06-06)

## 개요
VF 출고 바코드 시스템(`vf 출고 바코드 생성 (1).html`)의 JavaScript 코드를 M3(MiniMax) + nemotron(OpenRouter 무료) 교차 검증으로 리뷰.

## 사용된 모델
| 모델 | 역할 | 응답 | 소요시간 |
|------|------|------|----------|
| M3 (MiniMax) | 메인 리뷰 | 2개 MEDIUM 발견 | 즉시 |
| DeepSeek-V4-flash | 검증 1차 | **빈 응답 (2회)** | — |
| nvidia/nemotron-3-ultra-550b-a55b:free | 검증 2차(3차) | **4개 버그 전체 발견** (HIGH 2 + MEDIUM 2) | ~51s |

## 발견된 버그

### HIGH — 2건

#### 1. 시간 체크 범위 오류
```javascript
// BEFORE (bug): 현재 시각 포함 → 미입력 시간대가 현재 시각까지 체크됨
for (let h = 0; h <= now; h++) { }

// AFTER (fix): 현재 시각 미포함 → 이전 시간까지만 체크
for (let h = 0; h < now; h++) { }
```
- **영향:** 현재 시각이 20:09일 때 20시도 미입력으로 체크 → 잘못된 차단
- **발견:** nemotron

#### 2. 전송값 계산 오류
```javascript
// BEFORE (bug): 입력값을 이전 누적에 더함 → 엉뚱한 값 전송
lastCumul += val;
entries.push({ hour: hour, quantity: lastCumul });  // 210+250=460

// AFTER (fix): 입력값 그대로 전송
entries.push({ hour: hour, quantity: val });  // 250 그대로
```
- **영향:** 250 입력 → 460 전송 (증가값 +250으로 차트 표시)
- **발견:** nemotron

### MEDIUM — 2건

#### 3. parseInt() radix 누락
```javascript
// BEFORE: 8진수 오해 가능
parseInt(inp.dataset.hour);
// AFTER: 10진수 강제
parseInt(inp.dataset.hour, 10);
```

#### 4. isNaN(hour) 체크 누락
```javascript
// BEFORE: hour 값 검증 없음
if (!isNaN(val) && val > 0) { }
// AFTER: hour도 검증
if (!isNaN(hour) && !isNaN(val) && val > 0) { }
```
- **영향:** dataset.hour가 비정상 값이면 hour=NaN 전송

## 교차 검증 교훈

| 항목 | 내용 |
|------|------|
| **단일 모델 한계** | M3만으로 HIGH 2건 누락 (MEDIUM 2건만 발견) |
| **nemotron 필요성** | 3차 검증 없었으면 HIGH 버그 그대로 배포될 뻔 |
| **DS 불안정** | DS-V4-flash 2회 빈 응답 → 재시도 패턴 필요 |
| **영문 프롬프트 필수** | nemotron 한글 처리 불가 → 영문 코드 리뷰 수행 |

## 관련 파일
- 리뷰 대상: `E:\coding\VF 출고 바코드\vf 출고 바코드 생성 (1).html`
- 교차 검증 스킬: `automation/harness-cross-verify`

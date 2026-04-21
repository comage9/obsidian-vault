---
tags: [키움API, 실거래, 투자, 계좌]
date: 2026-04-17
---

# 키움 API 실거래 메뉴얼

## 📋 기본 정보

### 계좌 정보
- **계좌번호**: 5206921810 (10자리, 실제 계좌번호)
- **APP_KEY**: `9VrkLPnP6ZHBZsmqRpXNwL3Y2iAGZ9wWbUU_wWVGfLI` (새로운 키)
- **SECRET_KEY**: `vtUbJljzrG_gL7kfoc3rgGy1RkJBjEbgnKD56smR5qw` (새로운 키)
- **이전 키**: `6E58kEbJ4Plm38H7FlwBfS0695z85TIaqKb6U5nDhhs` / `dNiYIiuN7G5-QNHQsdjJFl44PuqOzZgVGTf4QTvq9eo` (만료됨)

### API 접근 정보
- **API 문서**: `키움 REST API 문서.pdf` (526페이지)
- **웹 가이드**: https://openapi.kiwoom.com/guide/api/guide/dummyVal=0
- **저장 위치**: `/home/comage/coding/ki-ai-trader/kiwoom-api-docs/`

## 🔐 OAuth 인증

### 토큰 정보 (현재 만료됨)
```json
{
  "access_token": "HeBa4OGbY5Xwrz47wZRZma9TXDt2mbIxjqM5jmyFftasVfky4C9CIduhlN1jw3STsqsBu45YM8jtm9pB_ffq3g",
  "token_type": "Bearer",
  "expires_dt": "20260316154455",
  "api_id": "au10001",
  "issued_at": "2026-03-16T15:44:55"
}
```

### 새 토큰 발급 필요
1. **OAuth 2.0 client_credentials grant** 사용
2. APP_KEY와 SECRET_KEY로 인증
3. 새 access_token 발급

## 🌐 API 엔드포인트

### 기본 URL
- **API 서버**: `https://api.kiwoom.com`
- **OAuth 토큰**: `https://api.kiwoom.com/oauth/token`

### 주요 엔드포인트
1. **계좌 잔고 조회**: `/api/dostk/acnt`
2. **보유 종목 조회**: `/api/dostk/balance`
3. **시세 조회**: `/api/dostk/price`
4. **주문 실행**: `/api/dostk/order`

## 🚀 실거래 준비 단계

### 1. API 연결 테스트
```python
# kiwoom_api_test.py 실행
cd /home/comage/coding/ki-ai-trader
python3 kiwoom_api_test.py
```

### 2. 현재 문제점
- **API 서버 상태**: HTTP 500 에러 (서버 장애)
- **토큰 상태**: 만료됨 (2026-03-16)
- **연결 상태**: 현재 실거래 불가

### 3. 해결 방안
1. **API 서버 복구 대기**
2. **새 토큰 발급 시도**
3. **대체 접근 방법 검토**

## 📊 실거래 알고리즘

### 기본 전략
- **손절**: -3%
- **익절**: +5%
- **포트폴리오 분산**: 단타 70%, 중기 30%

### AI 종목 선정 기준
1. **단타 전략** (1-3일)
   - 목표수익: 3-5%
   - 손절: -3%
   - 예: 삼성전자, NAVER

2. **중기 전략** (1-4주)
   - 목표수익: 10-15%
   - 손절: -8%
   - 예: SK하이닉스, 셀트리온

## 📁 파일 구조

```
ki-ai-trader/
├── kiwoom-api-docs/          # API 문서 및 키
│   ├── key/
│   │   ├── 52069218_appkey.txt
│   │   ├── 52069218_secretkey.txt
│   │   ├── token.json
│   │   ├── oauth_token.json
│   │   └── 키움 REST API 문서.pdf
│   └── httpsopenapi.kiwoom.comguideapiguidedummyVal=0.txt
├── kiwoom_api.py            # API 클라이언트
├── kiwoom_api_test.py       # 연결 테스트
├── load_mock_data.py        # 모의 데이터 로더
├── mock-data/               # 테스트 데이터
└── src/trading_algorithms.py # 트레이딩 알고리즘
```

## ⚠️ 주의사항

### 보안
- API 키 노출 금지
- .env 파일에 저장된 키 확인
- 토큰 주기적 갱신

### 법적 제한
- 실제 거래 전 테스트 필수
- 리스크 관리 준수
- 시장 규정 준수

## 🔄 업데이트 기록

- **2026-04-17**: 키움 API 자료 수집 및 메뉴얼 작성
- **2026-04-17**: API 클라이언트 구현 시작
- **2026-04-17**: 모의 데이터 시스템 구축 완료

---

*이 문서는 키움 API 실거래를 위한 참고 자료입니다. 실제 거래 전 충분한 테스트를 권장합니다.*
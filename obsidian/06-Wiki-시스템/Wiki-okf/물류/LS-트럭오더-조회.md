---
title: LS 트럭오더 조회 절차
created: 2026-06-04
updated: 2026-06-04
project: LS (Linehaul Service)
---

# LS 트럭오더 조회 절차 (2026-06-04)

## 목적
ls.coupang.com에서 보노하우스 VF67(유원)HUB 출발 차량을 일자별 조회.

## 핵심 규칙
- **locationStart=VF67 필수** — 미지정 시 전체 17,000+건 (2026-06-04 기준 17,873건)
- 보노하우스 출발 = VF67(유원)HUB

## 조회 절차

### 1. 로그인
```bash
# 1단계: OAuth 페이지 GET
rm -f /tmp/coupang_cookies.txt
curl -s -L \
  "https://xauth.coupang.com/auth/realms/fts/protocol/openid-connect/auth?response_type=code&client_id=ls&scope=openid&redirect_uri=https://ls.coupang.com/login/oauth2/code/keycloak" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -H "Accept-Language: ko-KR,ko;q=0.9,en;q=0.8" \
  -c /tmp/coupang_cookies.txt -o /tmp/coupang_login.html

# 2단계: action URL 추출
ACTION_URL=$(grep -oP 'action="\K[^"]*' /tmp/coupang_login.html | sed 's/&amp;/\&/g')

# 3단계: POST 로그인 (--data-urlencode 필수)
curl -s -L "$ACTION_URL" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -H "Accept-Language: ko-KR,ko;q=0.9,en;q=0.8" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Origin: https://xauth.coupang.com" \
  -H "Referer: https://xauth.coupang.com/auth/realms/fts/protocol/openid-connect/auth?response_type=code&client_id=ls&scope=openid&redirect_uri=https://ls.coupang.com/login/oauth2/code/keycloak" \
  -b /tmp/coupang_cookies.txt -c /tmp/coupang_cookies.txt \
  --data-urlencode "username=mokicom" \
  --data-urlencode "password=Coupang!78910" \
  --data-urlencode "credentialId=" \
  --data-urlencode "login=로그인" \
  -o /tmp/coupang_result.html
```

### 2. VF67 오늘 차량 조회
```bash
DATE=$(date +%Y-%m-%d)
curl -s "https://ls.coupang.com/truckOrderTracking" -G \
  -d "page=0" \
  -d "pageSize=100" \
  -d "orderStartDate=$DATE" \
  -d "orderEndDate=$DATE" \
  -d "locationStart=VF67" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -b /tmp/coupang_cookies.txt | python -m json.tool
```

## 검증 결과 (2026-06-04)
- 전체 (locationStart 없음): 17,873건
- VF67 + 오늘: **3건** (모두 부천1HUB 행)
  - 12:01 경기89바6845 (11T) 케이엘피
  - 16:07 경기89바1454 (5T) 케이엘피
  - 17:07 경기93아8802 (5T) 케이엘피

## API 파라미터 정리
| 파라미터 | 필수 | 설명 |
|:---------|:----:|:-----|
| `page` | ✅ | 0부터 |
| `pageSize` | ✅ | 기본 25, 검색은 100 권장 |
| `orderStartDate` | ❌ | YYYY-MM-DD |
| `orderEndDate` | ❌ | YYYY-MM-DD |
| `statuses` | ❌ | CONFIRMED,SUBMITTED,CANCELED,BACK |
| `locationStart` | ❌ | 작업장 코드 (VF67 = 보노하우스) |
| `locationEnd` | ❌ | 도착지 코드 |

## Pitfalls (함정)
- `pageSize` 생략 시 500 에러 (`Required request parameter 'pageSize'`)
- `locationStart` 미지정 시 전체 17,000+건 — 반드시 VF67
- `--data-urlencode` 사용 (비밀번호에 `!` 포함)

## 관련
- 스킬: `automation/ls-coupang`
- 위키: `물류/프로젝트-개요.md` (LS 섹션)
- 크로스 디바이스: Syncthing 동기화

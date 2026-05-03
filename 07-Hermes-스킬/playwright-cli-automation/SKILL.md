---
name: playwright-cli-automation
description: Playwright CLI 브라우저 자동화 — 웹 검색,表单입력, 클릭 등
category: productivity
---

# Playwright CLI 자동화

## 기본 명령어

```bash
cd /tmp && timeout 30 playwright-cli open <url>     # 브라우저 열기
cd /tmp && timeout 15 playwright-cli snapshot          # 현재 페이지 스냅샷
cd /tmp && timeout 15 playwright-cli type "<text>"    # 텍스트 입력
cd /tmp && timeout 15 playwright-cli click <ref>       # 요소 클릭
cd /tmp && timeout 15 playwright-cli fill <ref> <text> # 필드 채우기
cd /tmp && timeout 10 playwright-cli close             # 브라우저 닫기
```

## ref(ref) 확인 방법
`playwright-cli snapshot` 출력에서 `[ref=e3]` 같은 형식으로 확인

## Cline CLI 명령어

```bash
cd /tmp && timeout 45 cline -y "<명령어>" 2>&1 | head -40
```

## 실전 예시 (구글 검색)

```bash
# 1. 브라우저 열기
playwright-cli open https://www.google.com

# 2. 스냅샷으로 ref 확인
playwright-cli snapshot

# 3. 검색어 입력
playwright-cli type "검색어"

# 4. 스냅샷으로 버튼 ref 확인 (ref=e158 등)
playwright-cli snapshot

# 5. 검색 버튼 클릭
playwright-cli click e158

# 6. 브라우저 닫기
playwright-cli close
```

## 참고
- ref는 snapshot 출력에서 확인
- Cline CLI는 MiniMax API 사용 (HTTP 401이면 API 키 확인)
- 구글은 CAPTCHA가 잘 뜨므로 DuckDuckGo 등 대체 검색엔진 권장

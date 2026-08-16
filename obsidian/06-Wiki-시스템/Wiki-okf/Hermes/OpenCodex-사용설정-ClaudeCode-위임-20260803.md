---
title: OpenCodex 사용·설정 + Claude Code 위임 검증
created: 2026-08-03
updated: 2026-08-03
type: 개념
status: 완료
신뢰도: EXTRACTED
tags: [hermes, opencodex, claude-code, provider]
sources:
  - 실측 2026-08-03
  - skill:hermes-provider-troubleshooting/references/opencodex-alibaba-token-plan.md
---

# OpenCodex 사용·설정 + Claude Code 위임

> 검증일: 2026-08-03. OpenCodex 2.8.0 → **2.10.0 업데이트 완료**.

## 1. 구성

```
Hermes(이 에이전트) ─┐
                     ├→ OpenCodex :10100 ─→ Alibaba Token Plan (qwen3.8-max-preview 등)
Claude Code ─────────┘      (로컬 프록시)      token-plan.ap-southeast-1.maas.aliyuncs.com
```

- **Claude Code도 Anthropic 주소가 아니라 OpenCodex 경유로 Alibaba qwen 사용** (사용자 확인)
- OpenCodex repo: github.com/lidge-jun/opencodex (npm `@bitkyc08/opencodex`)

## 2. 핵심 경로

| 항목 | 값 |
|---|---|
| 프록시 | http://127.0.0.1:10100 |
| 설정 | `C:\Users\kis\.opencodex\config.json` |
| 관리자 토큰 | `C:\Users\kis\.opencodex\admin-api-token` (ocx_ 접두) |
| 상태 확인 | `ocx status` / 기동 `ocx start` |
| Hermes 모델 | `alibaba-token-plan-intl/qwen3.8-max-preview` (custom provider) |

## 3. Claude Code 위임 — 가능 ✅ (실측 확인)

Claude Code는 `~/.claude/settings.json`의 **env 블록이 셸 환경변수를 덮어쓴다.** 현재 설정:

```json
"env": {
  "ANTHROPIC_BASE_URL": "https://token-plan...maas.aliyuncs.com/apps/anthropic",
  "ANTHROPIC_AUTH_TOKEN": "sk-sp-...",
  "ANTHROPIC_MODEL": "qwen3.8-max-preview",
  "ANTHROPIC_DEFAULT_HAIKU/SONNET/OPUS_MODEL": "qwen3.8-max-preview",
  "CLAUDE_CODE_SUBAGENT_MODEL": "qwen3.8-max-preview"
}
```

**주의:** 모델명은 **프리픽스 없이** `qwen3.8-max-preview` (직접 Alibaba anthropic 경로). `alibaba-token-plan-intl/` 프리픽스를 붙이면 400 Model not exist.

### 위임 방법 (Hermes → Claude Code)
```bash
claude -p "작업 지시" --max-turns 10   # print 모드, workdir 지정
```
- 실측: `claude -p "Reply with exactly: DELEGATE_OK"` → `DELEGATE_OK` 응답 ✅
- 별도 env 지정 불필요 — settings.json이 처리. 직접 env를 붙이면 오히려 충돌

## 4. 업데이트 기록

| 날짜 | 버전 | 비고 |
|---|---|---|
| 2026-08-03 | 2.8.0 → **2.10.0** | `npm install -g @bitkyc08/opencodex@latest`. 실행 중 프록시는 재기동 시 신버전 반영 |

## 관련 문서
- [[Wiki-SSOT-온보딩-20260802]]
- 스킬: `hermes-provider-troubleshooting` (references/opencodex-alibaba-token-plan.md = 설정 SoT)
- 스킬: `claude-code` (위임 플래그 전체)

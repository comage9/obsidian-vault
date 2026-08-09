# OmniRoute Hermes /model 목록 정리 (2026-08-09)

## 문제
Telegram `/model`에서 OmniRoute 선택 시 `/v1/models` 라이브 디스커버리로 **289개** 모델이 노출되어 실사용 확인이 불가능.

## 조치
`C:\Users\kis\AppData\Local\hermes\config.yaml` → `providers.omniroute`:

```yaml
providers:
  omniroute:
    base_url: http://localhost:20128/v1
    discover_models: false   # 라이브 /v1/models 덮어쓰기 차단
    models:                  # dict = allowlist + context_length
      auto/best-chat: {context_length: 1048576}
      ...
```

Hermes 피커 검증 (`list_picker_providers`): **omniroute 13개만 표시**.

## 실동작 테스트 (chat/completions, stream=false)
PASS 13 / FAIL 0

| 모델 | 결과 | 비고 |
|------|------|------|
| auto/best-chat | OK | 라우팅 |
| auto/best-fast | OK | 라우팅 |
| auto/cheap | OK | 라우팅 |
| auto/best-free | OK | 라우팅 |
| auto/coding | OK | 라우팅 |
| xao/grok-4.5 | OK | xAI OAuth (현재 기본) |
| xao/grok-4.3 | OK | xAI OAuth |
| zai/glm-4.7-flash | OK | Z.AI API |
| cw/claude-sonnet-4-6 | OK | Claude Web |
| felo/felo-chat | OK | Felo free |
| felo/felo-search | OK | Felo free |
| oc/big-pickle | OK | OpenCode free |
| oc/nemotron-3-ultra-free | OK | OpenCode free |

## 제외 (실패 사유)
| 모델/계열 | 실패 |
|-----------|------|
| qwen-web/* | empty content |
| zai/glm-5.x | 429 Insufficient balance |
| claude-web haiku | 429 rate limit |
| gemini-web/* | playwright 모듈 경로 오류 500 |
| zai-web/* | 403 Not authenticated |
| tllm/* | 403 Vercel IP block |
| ddgw/* | 418 anti-abuse |
| aug/* | 502 auggie CLI 미설치 |
| oc/deepseek-v4-flash-free 등 | 403 insufficient_quota |
| pepper/* | 502 |

## 활성 OmniRoute 연결 (storage.sqlite)
- claude-web, gemini-web, grok-cli, qwen-web, xai-oauth, zai, zai-web = active
- kimi-coding = credits_exhausted

## 반영
- 백업: `config.yaml.bak.omniroute_fix`
- 게이트웨이 재시작 후 Telegram `/model`에서 omniroute 13개 확인
- 스모크 결과: `~/.hermes/cache/omniroute_curated_probe_20260809.json`

## 관련
- 스킬: `omniroute-gateway`, `hermes-provider-troubleshooting`
- fact_store #65 갱신

---
title: Hermes 모델 추가 — DeepSeek-V4-Flash-0731 (OpenCodex 경유)
created: 2026-08-03
updated: 2026-08-03
type: 의사결정
status: 완료
신뢰도: VERIFIED
tags: [hermes, model, deepseek, flash, opencodex, alibaba, 저사양모델]
---

# Hermes 모델 추가 — DeepSeek-V4-Flash-0731

> 목적: **저사양(저비용) 모델**을 Hermes에서 사용 가능하게 추가 (권역 입력 등 단순 작업 담당용)
> 작성일: 2026-08-03

---

## 1. 작업 내역

### 1.1 테스트 과정
| 시도 | 모델 ID | 결과 |
|:----:|:-----|:-----|
| 1 | `alibaba-token-plan-intl/deepseek-v4-flash` | ❌ 403 `AccessDenied.Unpurchased` (알리바바 토큰 플랜 미구매) |
| 2 | `alibaba-token-plan-intl/DeepSeek-V4-Flash-0731` | ❌ 404 `model_not_found` (대문자/카탈로그 미등록) |
| 3 | `alibaba-token-plan-intl/deepseek-v4-flash-0731` | ✅ **200 OK** |

> 핵심: OpenCodex `/v1/models` 카탈로그는 **전체 목록**을 보여줌. 실제 사용 가능 여부는 알리바바 토큰 플랜 계정의 구매/활성화 상태에 달림. 카탈로그에 `deepseek-v4-flash`가 보여도 구매 안 됐으면 403.
> 출처: 알리바바 Model Studio 콘솔 `modelId=deepseek-v4-flash-0731` (international 사이트)

### 1.2 추론 모델 함정 (발견·해결)
- `deepseek-v4-flash-0731`은 **추론(reasoning) 모델**
- `max_tokens`가 작으면 **토큰 전부 reasoning에 소모 → 응답 content=null**
  - max_tokens=50 → null / 200 → null / 575 reasoning 토큰 소모 후 content 반환
- **해결: `agent.max_tokens: 4096` 설정** (Hermes config)

### 1.3 config.yaml 적용 (수술적 패치, 백업 선행)
```yaml
# C:\Users\kis\AppData\Local\hermes\config.yaml
custom_providers:
  - name: opencodex
    models:
      alibaba-token-plan-intl/deepseek-v4-flash-0731:   # ← 추가
        context_length: 1000000
agent:
  max_tokens: 4096   # ← 추가 (추론 모델 대응)
```
- 백업: `config.yaml.bak.20260803` (23,511 bytes)
- 게이트웨이 재시작 후 모델 피커에서 선택 가능

### 1.4 검증 (실측)
- `python yaml` 확인: `flash-0731 in models: True`, `max_tokens: 4096` ✅
- 게이트웨이 실행 중 (PID 512984) ✅

---

## 2. 사용법

```
# 모델 전환 (텔레그램에서)
/model → deepseek-v4-flash-0731 선택

# 또는 CLI 스모크
hermes chat -q "테스트" -m "alibaba-token-plan-intl/deepseek-v4-flash-0731" --provider custom -Q
```

**모델별 역할 분담 (사용자 의도):**
| 모델 | 역할 |
|:-----|:-----|
| `qwen3.8-max-preview` | 메인 (고등 판단·검증) |
| `deepseek-v4-flash-0731` | 저사양 — 권역 입력 대행, LS/KPP 인쇄 등 단순 작업 |

---

## 3. 관련 문서
- 스킬: `hermes-provider-troubleshooting` (OpenCodex 경유 Hard rules)
- [[OpenCodex-사용설정-ClaudeCode-위임-20260803]]
- [[VF-출차관리-권역별-수량-음성합산-입력-20260803]] — 저사양 모델 실행 매뉴얼

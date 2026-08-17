# DeepSeek Harness(dsh) + OmniRoute — "No API key for provider" 해결 문서

- 작성일: 2026-08-17
- 적용 대상: `@deepseek-ai/dsh` (DeepSeek Harness, v0.1.0-rc.6) + OmniRoute(http://localhost:20128)

## 증상
- dsh Web UI/CLI에서 OmniRoute 모델(OmniRoute Auto Best Coding 등)로 세션 요청 시 실패
- 세션 로그: `This turn failed — No API key for provider: omniroute` (`PI_AI_ERROR`)

## 원인 (실진단 근거)
1. **OmniRoute 자체는 정상 동작**: `GET http://localhost:20128/v1/models` → 200, `POST http://localhost:20128/v1/chat/completions` → 200 (API 키 없이 동작, 무인증)
2. **dsh(pi-ai)의 openai-completions 라우트는 API 키가 없으면 요청을 시작하지 않음**: 어댑터가 라우트에 키 참조가 없을 때 `No API key for provider: <route>`(PI_AI_ERROR)를 반환 — OmniRoute가 키를 검증하지 않아도 dsh가 요청 전에 키 존재를 확인
3. **현재 설정 상태** (`~/.dsh/settings.yaml`):
   - `llm-pi-ai.providers.omniroute`: baseURL=`http://localhost:20128/v1`, api=`openai-completions`, 모델 5개(auto/best-*) — **정상**
   - **`apiKeyEnv` 없음** ← 문제
   - `agent-default-model`: omniroute/auto/best-coding — **정상** (OmniRoute 기본 모델로 변경됨)
   - `~/.dsh/.credentials.yaml`: `DEEPSEEK_API_KEY`만 존재, **OmniRoute 키 없음**

## 해결 방법 (택1)

### 방법 A — Web UI에서 API 키 입력 (권장, 가장 간단)
1. dsh Web UI: `http://127.0.0.1:3080`
2. **Settings → Models → OmniRoute → Edit**
3. **API key** 필드에 아무 값 입력: `omniroute` (또는 `local-dummy`)
   - OmniRoute는 키 값을 검증하지 않으므로 아무 문자열 OK
4. **Apply** → 새 세션에서 OmniRoute 모델 선택 → 정상 동작

### 방법 B — 설정 파일 직접 수정
1. `~/.dsh/settings.yaml` 의 omniroute 프로바이더에 `apiKeyEnv` 추가:
```yaml
llm-pi-ai:
  providers:
    omniroute:
      apiKeyEnv: OMNIROUTE_API_KEY   # ← 추가
      api: openai-completions
      baseURL: http://localhost:20128/v1
      displayName: OmniRoute
      models:
        - id: auto/best-coding
          name: OmniRoute Auto Best Coding
          contextWindow: 1050000
          maxTokens: 1048576
        # ... (나머지 auto/best-reasoning, fast, vision, chat 유지)
```
2. `~/.dsh/.credentials.yaml` 에 값 추가:
```yaml
OMNIROUTE_API_KEY: omniroute
```
   (또는 시스템 환경변수 `OMNIROUTE_API_KEY=omniroute` 설정)
3. dsh 재시작 (또는 Web UI 핫 리로드 확인)

## 주의사항
- `apiKeyEnv`만 추가하고 실제 값(환경변수/credentials)이 없으면 에러가 `MISSING_CREDENTIAL`로 바뀜 — **반드시 값도 함께 설정**
- OmniRoute는 키 값을 무시 — 실제 비밀 키가 아님, 아무 문자열이면 충분
- DeepSeek 공식 프로바이더(`deepseek-official`)는 그대로 유지 — 모델 선택기에서 언제든 되돌릴 수 있음
- llm-pi-ai 어댑터 규칙(공식 문서): "apiKeyEnv를 아예 생략하면 무인증(ambient discovery) / 참조했지만 값이 없으면 MISSING_CREDENTIAL" — **단, openai-completions hand-declared 라우트는 키 없이 요청을 시작하지 않음** (이번 케이스)

## 검증 방법
1. Web UI 새 세션 → 모델 선택기에서 **OmniRoute → Auto Best Coding** 선택
2. 메시지 전송 → 정상 응답 확인 (세션 로그에 PI_AI_ERROR 없음)
3. OmniRoute ANALYTICS (http://localhost:20128) → 사용량에 요청 반영 확인

## 참고 파일
- dsh 설정: `C:\Users\kis\.dsh\settings.yaml`
- dsh 키 저장: `C:\Users\kis\.dsh\.credentials.yaml`
- OmniRoute: `http://localhost:20128` (대시보드, 비번 CHANGEME)
- 공식 문서: https://github.com/deepseek-ai/deepseek-harness → docs/user/guide/providers.md, packages/llm/llm-pi-ai/README.md

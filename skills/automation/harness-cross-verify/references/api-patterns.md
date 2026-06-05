# Cross-Verify API Reference (M3 + DS-V4-flash + nvidia/nemotron OpenRouter)

검증일: 2026-06-05 (모델명 사용자 교정 3회 후 최종 확정)
- 메인=M3 (MiniMax), 검증 1차=DS-V4-flash (model=deepseek-v4-flash)
- 검증 2차=nvidia/nemotron-3-ultra-550b-a55b:free (OpenRouter, 키:Hermes-Nemotron-CrossVerify)
- 실제 호출 검증: DS-V4-flash 200 OK (서울 응답), nemotron 200 OK (서울 응답)

> OpenRouter 키는 반드시 `sk-or-v1-...` 형식 (2025년 이후 표준). 비표준 키=401.

## 1. DeepSeek 직접 API (검증 1차용)

엔드포인트: https://api.deepseek.com/v1/chat/completions
인증: Bearer $DEEPSEEK_API_KEY

참고: 메인 M3가 이 API 호출. 검증 1차는 model=deepseek-v4-flash 사용.

```python
def deepseek_query(prompt, model='deepseek-v4-flash', max_tokens=1000, timeout=30):
    api_key = load_key('DEEPSEEK_API_KEY')
    body = json.dumps({'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens, 'temperature': 0.1}).encode()
    req = urllib.request.Request('https://api.deepseek.com/v1/chat/completions',
        data=body, headers={'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())['choices'][0]['message']['content']
```

## 2. OpenRouter API (검증 2차 - nvidia nemotron)

엔드포인트: https://openrouter.ai/api/v1/chat/completions
인증: Bearer $OPENROUTER_API_KEY
키 이름: Hermes-Nemotron-CrossVerify

```python
def openrouter_query(prompt, model='nvidia/nemotron-3-ultra-550b-a55b:free',
                     max_tokens=1000, timeout=90):
    api_key = load_key('OPENROUTER_API_KEY')
    body = json.dumps({'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens, 'temperature': 0.1}).encode()
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',
        data=body, headers={'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())['choices'][0]['message']['content']
```

> nemotron 한글 한계: 영어 전용, 한글=mojibake. 3차 검증은 영어 프롬프트 권장.

## 3. 운영 규칙

- 타임아웃: M3/DS-V4-flash 30s, nemotron **90s** (실측 91s 소요, 2026-06-05)
- rate limit: OpenRouter 분당 20회
- 불일치 = 사용자 알림, 자동 결정 X
- 3차 호출: M3+DS 불일치 시 또는 사용자 명시 시
- 표기 정책: Claude = GPT (사용자 결정)

## 4. MiniMax M3 API (메인)

엔드포인트: https://api.minimax.chat/v1/text/chatcompletion_v2
인증: Bearer $MINIMAX_API_KEY

```python
def minimax_query(prompt, system_prompt='전문적인 AI 시스템 분석가입니다. 한국어로 답변합니다.',
                  max_tokens=2000, timeout=30):
    api_key = load_key('MINIMAX_API_KEY')
    body = json.dumps({
        'model': 'minimax-m3',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': prompt}
        ],
        'max_tokens': max_tokens,
        'temperature': 0.1
    }).encode()
    req = urllib.request.Request('https://api.minimax.chat/v1/text/chatcompletion_v2',
        data=body, headers={'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read())
        # ⚠️ MiniMax 응답 구조: OpenAI 표준과 다를 수 있음
        content = ''
        try:
            content = data['choices'][0]['message']['content']
        except (KeyError, IndexError):
            pass
        if not content:
            try:
                content = data.get('reply', '') or data.get('content', '')
            except:
                content = ''
        if not content:
            # fallback: 전체 응답 dump
            content = json.dumps(data, ensure_ascii=False)
        return content
```

> 🚨 **Pitfall**: 2026-06-05 실측 — `data['choices'][0]['message']['content']`가 빈 문자열 반환 (HTTP 200). 응답이 다른 키에 있을 수 있음. fallback 체인 필수.

## 5. 환경 변수 (.env)

- DEEPSEEK_API_KEY (검증 1차)
- OPENROUTER_API_KEY (검증 2차, sk-or-v1- 형식)
- MINIMAX_API_KEY (메인 M3)

## 5. 검증 체크리스트

- DS-V4-flash HTTP 200 (deepseek-v4-flash 모델, 1.22s 응답)
- nemotron HTTP 200 + free 모델 확인
- OpenRouter 키 sk-or-v1- 형식
- .env 키 3개 보유

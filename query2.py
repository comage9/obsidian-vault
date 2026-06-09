import requests
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-or-...1da9",
    "Content-Type": "application/json"
}
data = {
    "model": "qwen/qwen3-coder:free",
    "messages": [
        {
            "role": "user",
            "content": "다음 실행 계획을 코드/구현 관점에서 검증하세요.\n\n## Phase 1: GraphRAG 도입\n1. Obsidian Wiki(.md 파일)에서 내부 링크 [[...]] 추출\n2. NetworkX로 Knowledge Graph 구축\n3. Hermes MCP 서버로 GraphRAG 연동\n\n## Phase 2: 스킬 일괄 체계화\n1. 50+개 SKILL.md 파일 스캔\n2. description 기반 trigger_condition 자동 생성\n3. output_template 일괄 추가\n\n## 질문\n1. Obsidian .md에서 [[...]] 링크를 정규식으로 추출하는 방식의 한계는?\n2. 50개 파일 일괄 수정 시 발생할 수 있는 문제는?\n3. GraphRAG MCP 서버의 구현 복잡도는?\n4. 각 위험에 대한 구체적 대안을 제시하세요."
        }
    ],
    "temperature": 0.2
}
response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.text)

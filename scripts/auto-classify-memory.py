#!/usr/bin/env python3
"""memory/ 파일 자동 분류 - AI 기반"""

import os, glob, json, requests
from datetime import datetime

VAULT_DIR = "/tmp/obsidian-vault"
MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
UNCLASSIFIED_LOG = os.path.join(VAULT_DIR, "reports", "unclassified_memory.log")
API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

CATEGORY_MAP = {
    "VF_PROJECT": {
        "target": "00-코딩-프로젝트/01-VF-프로젝트/README.md",
        "keywords": ["VF", "생산", "출고", "창고", "재고", "색상", "금형", "보노하우스", "모바일 UI"]
    },
    "KI_PROJECT": {
        "target": "00-코딩-프로젝트/02-키-프로젝트/README.md",
        "keywords": ["키움", "매매", "트레이딩", "포트폴리오", "종목", "씨에스윈드"]
    },
    "SYSTEM": {
        "target": "02-기술-문서/index.md",
        "keywords": ["OpenClaw", "NotebookLM", "OpenCoder", "서버", "Git", "API", "옵시디언"]
    }
}

def classify_keyword(content):
    """키워드 기반 1차 분류"""
    scores = {}
    for cat, info in CATEGORY_MAP.items():
        score = sum(1 for kw in info["keywords"] if kw.lower() in content.lower())
        scores[cat] = score
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None

def classify_ai(content):
    """AI 기반 2차 분류 (키워드 불충분 시)"""
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": "openrouter/qwen/qwen3.5-flash-02-23:free",
                "messages": [{"role": "user", "content": f"""다음 내용을 분류하세요. JSON으로만 응답.
카테고리: VF_PROJECT, KI_PROJECT, SYSTEM, UNCLASSIFIED
내용: {content[:1000]}
응답: {{"category": "...", "reason": "..."}}"""}],
            },
            timeout=30
        )
        text = response.json()['choices'][0]['message']['content']
        return json.loads(text)
    except:
        return {"category": "UNCLASSIFIED", "reason": "AI 호출 실패"}

def append_timeline(target_path, content, source_file):
    """타겟 파일 Timeline 영역에 추가"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    append = f"\n- **[{date_str}]** (출처: {os.path.basename(source_file)})\n  {content[:200]}...\n"
    
    with open(target_path, 'a', encoding='utf-8') as f:
        f.write(append)

def main():
    os.makedirs(os.path.dirname(UNCLASSIFIED_LOG), exist_ok=True)
    
    for file_path in sorted(glob.glob(os.path.join(MEMORY_DIR, "2026-*.md"))):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 1차: 키워드 분류
        category = classify_keyword(content)
        
        # 2차: AI 분류 (키워드 불충분 시)
        if not category:
            result = classify_ai(content)
            category = result.get("category")
        
        if category and category in CATEGORY_MAP:
            target = os.path.join(VAULT_DIR, CATEGORY_MAP[category]["target"])
            append_timeline(target, content, file_path)
            print(f"✅ {os.path.basename(file_path)} → {category}")
        else:
            with open(UNCLASSIFIED_LOG, 'a', encoding='utf-8') as log:
                log.write(f"[{datetime.now().isoformat()}] {os.path.basename(file_path)}: 미분류\n")
            print(f"⚠️ {os.path.basename(file_path)} → 미분류")

if __name__ == "__main__":
    main()

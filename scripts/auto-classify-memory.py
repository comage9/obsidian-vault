#!/usr/bin/env python3
"""memory/ 파일을 키워드 기반으로 옵시디언 카테고리에 자동 분류"""
import os, re, sys
from pathlib import Path

MEMORY_DIR = Path(os.path.expanduser("~/.openclaw/workspace/memory"))
VAULT_DIR = Path("/tmp/obsidian-vault")

CATEGORIES = {
    "VF": {"dir": "00-코딩-프로젝트/01-VF-프로젝트", "keywords": ["VF", "생산", "출고", "창고", "재고", "색상", "금형", "보노하우스"]},
    "키": {"dir": "00-코딩-프로젝트/02-키-프로젝트", "keywords": ["키움", "매매", "트레이딩", "AI매매", "포트폴리오", "종목"]},
    "시스템": {"dir": "02-기술-문서", "keywords": ["OpenClaw", "NotebookLM", "OpenCoder", "API", "서버", "Git"]},
}

def classify(filepath):
    content = filepath.read_text(encoding='utf-8', errors='ignore')
    scores = {}
    for cat, info in CATEGORIES.items():
        score = sum(1 for kw in info["keywords"] if kw.lower() in content.lower())
        scores[cat] = score
    best = max(scores, key=scores.get) if max(scores.values()) > 0 else None
    return best, scores

if __name__ == "__main__":
    files = sorted(MEMORY_DIR.glob("2026-*.md"))
    for f in files:
        cat, scores = classify(f)
        if cat:
            print(f"📄 {f.name} → {cat} ({scores[cat]} 키워드)")
        else:
            print(f"📄 {f.name} → 분류 불가")

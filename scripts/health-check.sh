#!/bin/bash
# 옵시디언 위키 헬스체크
VAULT_DIR="/tmp/obsidian-vault"
cd "$VAULT_DIR"

echo "# 위키 헬스체크 - $(date +%Y-%m-%d)"
echo ""

# 1. 끊어진 링크 탐지
echo "## 끊어진 링크"
grep -rn '\[\[.*\]\]' --include="*.md" . | grep -v ".git" | sed 's/.*\[\[//' | sed 's/\]\].*//' | sort -u | while read link; do
  # 파일명.md 찾기
  found=$(find . -name "${link}.md" ! -path "./.git/*" 2>/dev/null | head -1)
  if [ -z "$found" ]; then
    echo "  ❌ 끊어진 링크: [[$link]]"
  fi
done

# 2. 고아 페이지 (링크되지 않은 파일)
echo ""
echo "## 고아 페이지 (인덱스에 없음)"
for f in $(find . -name "*.md" -type f ! -path "./.git/*" ! -name "index.md"); do
  name=$(basename "$f" .md)
  if ! grep -rq "\[\[$name\]\]" --include="*.md" . 2>/dev/null; then
    echo "  ⚠️ 고아: $f"
  fi
done

# 3. 빈 파일
echo ""
echo "## 빈/최소 파일"
find . -name "*.md" -type f ! -path "./.git/*" -size -50c | while read f; do
  echo "  📄 $(basename $f) ($(wc -c < $f) bytes)"
done

echo ""
echo "체크 완료"

#!/bin/bash
# 옵시디언 인덱스 자동 갱신
VAULT_DIR="/tmp/obsidian-vault"
cd "$VAULT_DIR"

TOTAL=$(find . -name "*.md" -type f ! -path "./.git/*" | wc -l)
DATE=$(date +%Y-%m-%d)

echo "# 옵시디언 인덱스" > /tmp/idx_tmp.md
echo "" >> /tmp/idx_tmp.md
echo "> 자동 갱신: $DATE | 총 $TOTAL 개 파일" >> /tmp/idx_tmp.md
echo "" >> /tmp/idx_tmp.md

for dir in "00-코딩-프로젝트" "01-일일-메모" "02-금형정보" "02-기술-문서" "memory" "mindvault-out"; do
  if [ -d "$dir" ]; then
    COUNT=$(find "$dir" -name "*.md" -type f | wc -l)
    echo "## $dir ($COUNT)" >> /tmp/idx_tmp.md
    find "$dir" -name "*.md" -type f | sort | while read f; do
      name=$(basename "$f" .md)
      echo "- [[$name]]" >> /tmp/idx_tmp.md
    done
    echo "" >> /tmp/idx_tmp.md
  fi
done

# 루트 파일
echo "## 루트" >> /tmp/idx_tmp.md
find . -maxdepth 1 -name "*.md" -type f | sort | while read f; do
  name=$(basename "$f" .md)
  echo "- [[$name]]" >> /tmp/idx_tmp.md
done

mv /tmp/idx_tmp.md index.md
echo "✅ 인덱스 갱신 완료: $TOTAL 개 파일"

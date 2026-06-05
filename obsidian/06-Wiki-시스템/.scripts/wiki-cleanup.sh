#!/usr/bin/env bash
# Wiki Daily Cleanup — 오래된 파일 정리 + index.md 갱신 + graphify
# 실행: bash .scripts/wiki-cleanup.sh
set -euo pipefail

VAULT="/home/comtop/obsidian-vault/06-Wiki-시스템"
WIKI="$VAULT/Wiki"
LOG="$WIKI/log.md"
DATE=$(date '+%Y-%m-%d %H:%M')
TODAY=$(date '+%Y-%m-%d')

echo "=== Wiki Cleanup 시작 ==="

# 1. 오래된 세션 파일 아카이브 (3일 이상)
echo "[1/4] 세션 파일 아카이브..."
ARCHIVED="$VAULT/Archived/$TODAY"
mkdir -p "$ARCHIVED"
MOVED=0
while IFS= read -r f; do
    fname=$(basename "$f")
    # 3일 이상 지난 telegram_session 파일
    if echo "$fname" | grep -q "telegram_session"; then
        age=$(( ($(date +%s) - $(stat -c %Y "$f")) / 86400 ))
        if [ "$age" -ge 3 ]; then
            mv "$f" "$ARCHIVED/"
            MOVED=$((MOVED + 1))
            echo "  📦 이동: $fname"
        fi
    fi
done < <(find "$WIKI" -maxdepth 1 -name "*.md" 2>/dev/null)
echo "  결과: ${MOVED}개 파일 아카이브"

# 2. index.md 갱신
echo "[2/4] index.md 갱신..."
INDEX="$WIKI/index.md"
TOTAL=0

# 임시 index 생성
TMP=$(mktemp)
cat > "$TMP" << EOF
# Wiki Index

> Content catalog. Every wiki page listed under its type.
> Last updated: $TODAY | Total pages: 

EOF

declare -A SECTIONS
SECTIONS[의사결정]="의사결정"
SECTIONS[문제-해결]="문제-해결"
SECTIONS[개념]="개념"
SECTIONS[아이디어]="아이디어"

for section in "${!SECTIONS[@]}"; do
    dir="$WIKI/$section"
    if [ -d "$dir" ]; then
        pages=$(find "$dir" -name "*.md" 2>/dev/null | sort)
        count=$(echo "$pages" | grep -c . || true)
        if [ "$count" -gt 0 ]; then
            echo "" >> "$TMP"
            echo "## ${section}" >> "$TMP"
            while IFS= read -r page; do
                pname=$(basename "$page" .md)
                # 첫 번째 줄에서 간단 요약
                desc=$(grep -m1 '^# ' "$page" 2>/dev/null | sed 's/^# //' || echo "$pname")
                echo "- [[${section}/${pname}]] — ${desc}" >> "$TMP"
                TOTAL=$((TOTAL + 1))
            done <<< "$pages"
        fi
    fi
done

# log.md는 항상 표시
echo "" >> "$TMP"
echo "## 로그" >> "$TMP"
echo "- [[log]] — 작업 로그 (append-only)" >> "$TMP"
TOTAL=$((TOTAL + 1))

# 총 페이지 수 업데이트
sed -i "s/Total pages: /Total pages: ${TOTAL}/" "$TMP"

# SCHEMA.md 링크 추가
if [ -f "$WIKI/SCHEMA.md" ]; then
    echo "" >> "$TMP"
    echo "## 시스템" >> "$TMP"
    echo "- [[SCHEMA]] — Wiki 구조 및 규칙" >> "$TMP"
fi

mv "$TMP" "$INDEX"
echo "  ✅ index.md 갱신 완료 (${TOTAL}개 페이지)"

# 3. Graphify 실행 (Python 스크립트 존재 시)
echo "[3/4] Graphify 실행..."
GRAPHIFY="$WIKI/scripts/graphify.py"
if [ -f "$GRAPHIFY" ]; then
    if python3 "$GRAPHIFY" 2>/dev/null; then
        echo "  ✅ Graphify 재생성 완료"
    else
        echo "  ⚠️  Graphify 실패 (스킵)"
    fi
else
    echo "  ⏭️  Graphify 스크립트 없음"
fi

# 4. 로그 기록
echo "[4/4] 로그 기록..."
SUMMARY="### $DATE — Daily Cleanup: ${MOVED}개 아카이브, ${TOTAL}개 페이지"
echo "$SUMMARY"
echo "" >> "$LOG"
echo "$SUMMARY" >> "$LOG"

echo ""
echo "=== Cleanup 완료 ==="

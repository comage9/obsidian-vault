#!/usr/bin/env bash
# Wiki Daily Briefing — 매일 아침 Wiki 상태 요약
# 실행: bash .scripts/wiki-daily-briefing.sh
set -euo pipefail

WIKI="/home/comtop/obsidian-vault/06-Wiki-시스템/Wiki"
LOG="$WIKI/log.md"
DATE=$(date '+%Y-%m-%d %H:%M')

echo "=== Wiki Daily Briefing ==="
echo ""

# 1. 전체 통계
TOTAL=$(find "$WIKI" -name "*.md" -not -path "*/Archived/*" | wc -l)
echo "📊 전체 페이지: ${TOTAL}개"

# 카테고리별
echo ""
echo "┌─ 카테고리별 페이지 수 ─────────────"
for dir in 의사결정 문제-해결 개념 아이디어; do
    d="$WIKI/$dir"
    if [ -d "$d" ]; then
        count=$(find "$d" -name "*.md" 2>/dev/null | wc -l)
        echo "├─ ${dir}: ${count}개"
    fi
done
echo "└────────────────────────────────"

# 2. 최근 24시간 변경사항
echo ""
echo "┌─ 최근 24시간 변경사항 ────────────"
YESTERDAY=$(date -d '24 hours ago' '+%Y-%m-%d')
if [ -f "$LOG" ]; then
    grep "### $YESTERDAY\|### $(date '+%Y-%m-%d')" "$LOG" 2>/dev/null | head -10 || echo "├─ (변경 없음)"
fi
echo "└────────────────────────────────"

# 3. 고립 페이지/깨진 링크 (lint 요약)
echo ""
echo "┌─ 상태 ──────────────────────────"
# index.md와 비교해서 index에 없는 페이지
if [ -f "$WIKI/index.md" ]; then
    while IFS= read -r page; do
        pname=$(basename "$page" .md)
        if ! grep -q "\[\[${pname}\]\]" "$WIKI/index.md" 2>/dev/null; then
            case "$pname" in
                log|SCHEMA|index) continue ;;
            esac
            echo "├─ ⚠️  index.md 누락: ${pname}"
        fi
    done < <(find "$WIKI" -name "*.md" -not -path "*/Archived/*" -not -name "log.md" -not -name "index.md" -not -name "SCHEMA.md")
fi
echo "└────────────────────────────────"

echo ""
echo "=== Briefing 완료 ==="

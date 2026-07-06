#!/usr/bin/env bash
# Wiki Nightly Lint — 깨진 링크, 오류 검사
# 실행: bash .scripts/wiki-lint.sh
set -euo pipefail

WIKI="/home/comtop/obsidian-vault/06-Wiki-시스템/Wiki"
LOG="$WIKI/log.md"
DATE=$(date '+%Y-%m-%d %H:%M')
REPORT=""
ERRORS=0
WARNS=0

echo "=== Wiki Lint 시작 ==="
echo "대상: $WIKI"
echo ""

# 1. 깨진 Wikilink 검사
echo "[1/4] 깨진 Wikilink 검사..."
BROKEN=0
while IFS= read -r file; do
    links=$(grep -oP '\[\[([^\]]+)\]\]' "$file" 2>/dev/null | sed 's/\[\[\|\]\]//g' | sort -u || true)
    for link in $links; do
        # 경로 처리: [[폴더/파일]] → Wiki/폴더/파일.md
        if echo "$link" | grep -q '/'; then
            target="$WIKI/${link}.md"
        else
            target="$WIKI/${link}.md"
            # 모든 하위 폴더 검색
            found=$(find "$WIKI" -name "${link}.md" 2>/dev/null | head -1)
            [ -n "$found" ] && continue
        fi
        if [ ! -f "$target" ]; then
            # 예외: Obsidian 내부 링크, 일반 단어
            case "$link" in
                Hermes|Wiki|연동|위키링크|문서명|링크|wikilink|README|LICENSE) continue ;;
                http*|www*) continue ;;
            esac
            echo "  ⚠️  깨진 링크: $link → $file"
            BROKEN=$((BROKEN + 1))
        fi
    done
done < <(find "$WIKI" -name "*.md" -not -path "*/Archived/*" -not -name "log.md" -not -name "index.md" -not -name "SCHEMA.md")
echo "  결과: ${BROKEN}개 깨진 링크"
[ "$BROKEN" -gt 0 ] && ERRORS=$((ERRORS + BROKEN))

# 2. 고립 페이지 검사 (inbound link 없는 페이지)
echo ""
echo "[2/4] 고립 페이지 검사..."
ISOLATED=0
while IFS= read -r page; do
    pname=$(basename "$page" .md)
    # 모든 페이지에서 이 페이지를 링크하는지 검사
    refs=$(grep -r "\[\[${pname}\]\]" "$WIKI" --include="*.md" -l 2>/dev/null | grep -v "$page" | head -1 || true)
    if [ -z "$refs" ]; then
        # index.md나 SCHEMA.md에서 참조하는지 확인
        idx_ref=$(grep -c "\[\[${pname}\]\]" "$WIKI/index.md" 2>/dev/null || true)
        if [ "$idx_ref" -eq 0 ]; then
            echo "  ⚠️  고립 페이지: ${pname} ($page)"
            ISOLATED=$((ISOLATED + 1))
        fi
    fi
done < <(find "$WIKI" -name "*.md" -not -path "*/Archived/*" -not -name "log.md" -not -name "index.md" -not -name "SCHEMA.md")
echo "  결과: ${ISOLATED}개 고립 페이지"
WARNS=$((WARNS + ISOLATED))

# 3. Frontmatter 검사
echo ""
echo "[3/4] Frontmatter 검사..."
BAD_FM=0
while IFS= read -r file; do
    first=$(head -1 "$file" 2>/dev/null || true)
    if [ "$first" != "---" ]; then
        echo "  ⚠️  Frontmatter 없음: $file"
        BAD_FM=$((BAD_FM + 1))
    fi
done < <(find "$WIKI" -name "*.md" -not -path "*/Archived/*" -not -name "log.md" -not -name "SCHEMA.md" -not -name "index.md")
echo "  결과: ${BAD_FM}개 frontmatter 누락"
WARNS=$((WARNS + BAD_FM))

# 4. 로그 및 보고서
echo ""
echo "[4/4] 보고서 생성..."
TOTAL=$(find "$WIKI" -name "*.md" -not -path "*/Archived/*" | wc -l)
SUMMARY="### $DATE — Wiki Lint: ❌${ERRORS}개 오류 / ⚠️${WARNS}개 경고

| 검사 항목 | 결과 |
|-----------|------|
| 깨진 Wikilink | ${BROKEN}개 |
| 고립 페이지 | ${ISOLATED}개 |
| Frontmatter 누락 | ${BAD_FM}개 |
| 전체 페이지 | ${TOTAL}개 |"

echo ""
echo "=== Lint 완료 ==="
echo "$SUMMARY"
echo "$SUMMARY" >> "$LOG"
exit $ERRORS

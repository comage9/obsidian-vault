#!/usr/bin/env bash
# Wiki Daily Ingest — Raw/ 파일을 Wiki/로 자동 변환
# 실행: bash scripts/wiki-daily-ingest.sh
set -euo pipefail

VAULT="/home/comtop/obsidian-vault/06-Wiki-시스템"
RAW="$VAULT/Raw"
WIKI="$VAULT/Wiki"
LOG="$WIKI/log.md"
DATE=$(date '+%Y-%m-%d %H:%M')
TODAY=$(date '+%Y-%m-%d')

mkdir -p "$RAW" "$WIKI"

# Raw 파일 검색
FILES=$(find "$RAW" -type f \( -name "*.md" -o -name "*.txt" -o -name "*.pdf" -o -name "*.vtt" -o -name "*.csv" -o -name "*.json" -o -name "*.html" \) 2>/dev/null | head -50)
COUNT=$(echo "$FILES" | grep -c . || true)

if [ "$COUNT" -eq 0 ]; then
    echo "[$DATE] Ingest: 처리할 Raw 파일 없음"
    exit 0
fi

echo "[$DATE] Ingest: $COUNT개 파일 처리 시작"
INGESTED=0

for f in $FILES; do
    fname=$(basename "$f")
    ext="${fname##*.}"
    name="${fname%.*}"
    
    # 제목 추출 (첫 # 또는 파일명)
    title=$(grep -m1 '^# ' "$f" 2>/dev/null | sed 's/^# //' || echo "$name")
    [ -z "$title" ] && title="$name"
    
    # 대상 경로
    tpath="$WIKI/${name}.md"
    
    # 이미 존재하면 스킵 (변경 감지를 위해 sha256 비교)
    if [ -f "$tpath" ]; then
        old_sha=$(sha256sum "$tpath" | cut -d' ' -f1)
        new_sha=$(sha256sum "$f" | cut -d' ' -f1)
        if [ "$old_sha" = "$new_sha" ]; then
            continue
        fi
    fi
    
    # VTT 처리 (타임스탬프 제거)
    if [ "$ext" = "vtt" ]; then
        content=$(tail -n +5 "$f" 2>/dev/null | sed '/^[0-9:.]* --> [0-9:.]*$/d' | sed 's/<[^>]*>//g' | sed '/^$/d')
        if [ -z "$content" ]; then
            continue
        fi
        cat > "$tpath" << EOF
---
type: 개념
created: $TODAY
tags: [raw, vtt, $name]
source: $fname
---

# $title

$(echo "$content")
EOF
    # PDF 처리 (pymupdf 사용 가능 시)
    elif [ "$ext" = "pdf" ]; then
        if command -v python3 &>/dev/null; then
            text=$(python3 -c "
import sys
try:
    import pymupdf
    doc = pymupdf.open('$f')
    for page in doc:
        print(page.get_text())
except ImportError:
    print('')
" 2>/dev/null)
            [ -z "$text" ] && continue
            cat > "$tpath" << EOF
---
type: 개념
created: $TODAY
tags: [raw, pdf, $name]
source: $fname
---

# $title

$(echo "$text")
EOF
        else
            continue
        fi
    else
        # 일반 텍스트/마크다운
        content=$(cat "$f")
        cat > "$tpath" << EOF
---
type: 개념
created: $TODAY
tags: [raw, $ext, $name]
source: $fname
---

# $title

$(echo "$content")
EOF
    fi
    
    # Raw 파일을 Archived/ 로 이동 (처리 완료)
    ARCHIVED="$VAULT/Archived/$TODAY"
    mkdir -p "$ARCHIVED"
    mv "$f" "$ARCHIVED/"
    
    INGESTED=$((INGESTED + 1))
    echo "  ✅ $fname → Wiki/${name}.md"
done

# log.md 갱신
echo "" >> "$LOG"
echo "### $DATE — Daily Ingest: ${INGESTED}개 파일 처리" >> "$LOG"

echo "[$DATE] Ingest 완료: ${INGESTED}개 인제스트"

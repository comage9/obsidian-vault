#!/bin/bash
# Wiki Lint 스크립트
# Wiki 문서들의 건강 상태를 점검하고 수정합니다

VAULT="/home/comage/obsidian-vault/06-Wiki-시스템"
WIKI="$VAULT/Wiki"
LOGS="$VAULT/Logs"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DATE=$(date '+%Y-%m-%d')
LOG_FILE="$LOGS/${DATE}-lint.log"

echo "[$TIMESTAMP] 🔧 Wiki 린트 시작" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# ============================================================================
# 1. 깨진 링크 검사
# ============================================================================
echo "[$TIMESTAMP] 1️⃣ 깨진 링크 검사 중..." | tee -a "$LOG_FILE"

broken_links=0
for file in "$WIKI"/*.md; do
    [ -f "$file" ] || continue
    [ "$(basename "$file")" = "인덱스.md" ] && continue
    
    # [[문서명]] 형태의 링크 추출
    links=$(grep -oE '\[\[[^]]+\]\]' "$file" | sed 's/\[\[\(.*\)\]\]/\\1/' | sed 's/\.md$//')
    
    for link in $links; do
        # 링크 대상 파일 존재 확인
        if [ ! -f "$WIKI/$link.md" ] && [ ! -f "$WIKI/$link" ]; then
            echo "    ⚠️ 깨진 링크 발견: [[$link]] (파일: $(basename "$file"))" | tee -a "$LOG_FILE"
            
            # 자동으로 링크 제거 (주석 처리)
            sed -i "s/\[\[$link\]\]/[\/* $link *\/]/g" "$file"
            broken_links=$((broken_links + 1))
        fi
    done
done

echo "    📊 깨진 링크: $broken_links개 발견" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# ============================================================================
# 2. 이중 타이틀 검사
# ============================================================================
echo "[$TIMESTAMP] 2️⃣ 이중 타이틀 검사 중..." | tee -a "$LOG_FILE"

duplicate_titles=0
for file in "$WIKI"/*.md; do
    [ -f "$file" ] || continue
    [ "$(basename "$file")" = "인덱스.md" ] && continue
    
    first_line=$(head -1 "$file")
    title_in_content=$(grep -m1 '^# ' "$file" | sed 's/^# //')
    
    if [ "$first_line" != "$title_in_content" ] && [ -n "$title_in_content" ]; then
        echo "    ⚠️ 이중 타이틀: $(basename "$file")" | tee -a "$LOG_FILE"
        echo "        첫 줄: $first_line" | tee -a "$LOG_FILE"
        echo "        H1 태그: $title_in_content" | tee -a "$LOG_FILE"
        
        # 첫 줄을 H1과 일치시킴
        filename=$(basename "$file")
        temp_file=$(mktemp)
        echo "# $title_in_content" > "$temp_file"
        tail -n +2 "$file" >> "$temp_file"
        mv "$temp_file" "$file"
        
        duplicate_titles=$((duplicate_titles + 1))
    fi
done

echo "    📊 이중 타이틀: $duplicate_titles개 수정" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# ============================================================================
# 3. 빈 문서 검사
# ============================================================================
echo "[$TIMESTAMP] 3️⃣ 빈 문서 검사 중..." | tee -a "$LOG_FILE"

empty_docs=0
for file in "$WIKI"/*.md; do
    [ -f "$file" ] || continue
    [ "$(basename "$file")" = "인덱스.md" ] && continue
    
    word_count=$(wc -w < "$file")
    if [ "$word_count" -lt 20 ]; then
        echo "    ⚠️ 빈 문서 또는 내용이 너무 적음: $(basename "$file") (단어 수: $word_count)" | tee -a "$LOG_FILE"
        # 오래됨 태그 추가
        if ! grep -q "#오래됨" "$file"; then
            sed -i '1s/$/\n\n#오래됨 #빈문서/' "$file"
        fi
        empty_docs=$((empty_docs + 1))
    fi
done

echo "    📊 빈 문서: $empty_docs개 발견" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# ============================================================================
# 4. 고아 문서 검사 (어떤 문서에서도 참조되지 않는 문서)
# ============================================================================
echo "[$TIMESTAMP] 4️⃣ 고아 문서 검사 중..." | tee -a "$LOG_FILE"

# 모든 Wikilink 수집
all_links=()
for file in "$WIKI"/*.md; do
    [ -f "$file" ] || continue
    [ "$(basename "$file")" = "인덱스.md" ] && continue
    
    links=$(grep -oE '\[\[[^]]+\]\]' "$file" | sed 's/\[\[\(.*\)\]\]/\\1/' | sed 's/\.md$//')
    all_links+=($links)
done

# 각 문서가 참조되는지 확인
orphan_docs=0
for file in "$WIKI"/*.md; do
    [ -f "$file" ] || continue
    [ "$(basename "$file")" = "인덱스.md" ] && continue
    
    filename=$(basename "$file" .md)
    is_linked=0
    
    for link in "${all_links[@]}"; do
        if [ "$link" = "$filename" ]; then
            is_linked=1
            break
        fi
    done
    
    # 인덱스에서 참조되는지 확인
    if grep -q "\[\[$filename\]\]" "$WIKI/인덱스.md" 2>/dev/null; then
        is_linked=1
    fi
    
    if [ $is_linked -eq 0 ]; then
        echo "    ⚠️ 고아 문서: $(basename "$file")" | tee -a "$LOG_FILE"
        
        # 고아 태그 추가
        if ! grep -q "#고아" "$file"; then
            sed -i '1s/$/\n\n#고아/' "$file"
        fi
        orphan_docs=$((orphan_docs + 1))
    fi
done

echo "    📊 고아 문서: $orphan_docs개 발견" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# ============================================================================
# 5. 오래된 문서 검사 (60일 이상 업데이트 없음)
# ============================================================================
echo "[$TIMESTAMP] 5️⃣ 오래된 문서 검사 중..." | tee -a "$LOG_FILE"

old_docs=0
sixty_days_ago=$(date -d "60 days ago" '+%Y-%m-%d' 2>/dev/null || date -v-60d '+%Y-%m-%d' 2>/dev/null)

for file in "$WIKI"/*.md; do
    [ -f "$file" ] || continue
    [ "$(basename "$file")" = "인덱스.md" ] && continue
    
    # 파일 수정일 확인
    file_date=$(stat -c '%y' "$file" 2>/dev/null | cut -d' ' -f1)
    
    if [ -n "$file_date" ] && [[ "$file_date" < "$sixty_days_ago" ]]; then
        echo "    ⚠️ 오래된 문서: $(basename "$file") (마지막 수정: $file_date)" | tee -a "$LOG_FILE"
        
        if ! grep -q "#오래됨" "$file"; then
            sed -i '1s/$/\n\n#오래됨 #업데이트필요/' "$file"
        fi
        old_docs=$((old_docs + 1))
    fi
done

echo "    📊 오래된 문서: $old_docs개 발견" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# ============================================================================
# 6. 인덱스 업데이트
# ============================================================================
echo "[$TIMESTAMP] 6️⃣ 인덱스 업데이트 중..." | tee -a "$LOG_FILE"

INDEX_FILE="$WIKI/인덱스.md"
cat > "$INDEX_FILE" << INDEXEOF
# Wiki 인덱스

## 개요
이 파일은 Wiki 시스템의 모든 문서를 색인합니다.
**마지막 업데이트:** $TIMESTAMP

## 📊 시스템 통계

| 항목 | 수 |
|------|-----|
| 깨진 링크 | $broken_links |
| 이중 타이틀 | $duplicate_titles |
| 빈 문서 | $empty_docs |
| 고아 문서 | $orphan_docs |
| 오래된 문서 | $old_docs |

## 📁 문서 목록

INDEXEOF

total_docs=0
for file in $(find "$WIKI" -name "*.md" | sort); do
    [ "$(basename "$file")" = "인덱스.md" ] && continue
    title=$(head -1 "$file" | sed 's/^#*\s*//')
    tags=$(grep -oE '#[a-zA-Z0-9가-힣]+' "$file" | sort -u | tr '\n' ' ')
    echo "- [[$(basename "$file" .md)]] $tags" >> "$INDEX_FILE"
    total_docs=$((total_docs + 1))
done

echo "" >> "$INDEX_FILE"
echo "## 🏷️ 태그별 문서" >> "$INDEX_FILE"

# 태그별 인덱스 생성
for tag in $(find "$WIKI" -name "*.md" -exec grep -ohE '#[a-zA-Z0-9가-힣]+' {} \; | sort -u); do
    echo "" >> "$INDEX_FILE"
    echo "### $tag" >> "$INDEX_FILE"
    for file in $(find "$WIKI" -name "*.md"); do
        [ "$(basename "$file")" = "인덱스.md" ] && continue
        if grep -q "$tag" "$file"; then
            title=$(head -1 "$file" | sed 's/^#*\s*//')
            echo "- [[$(basename "$file" .md)]]" >> "$INDEX_FILE"
        fi
    done
done

echo "" >> "$INDEX_FILE"
echo "---" >> "$INDEX_FILE"
echo "**총 문서:** $total_docs개" >> "$INDEX_FILE"
echo "**린트 실행:** $TIMESTAMP" >> "$INDEX_FILE"

# ============================================================================
# 7. 로그 파일 생성
# ============================================================================
LOG_MD="$LOGS/${DATE}-로그.md"
{
    echo "# $DATE Wiki 린트 로그"
    echo ""
    echo "## 실행 정보"
    echo "- 시간: $TIMESTAMP"
    echo ""
    echo "## 검사 결과"
    echo "| 항목 | 수 |" | tee -a "$LOG_FILE"
    echo "|------|-----|" | tee -a "$LOG_FILE"
    echo "| 깨진 링크 | $broken_links |" | tee -a "$LOG_FILE"
    echo "| 이중 타이틀 | $duplicate_titles |" | tee -a "$LOG_FILE"
    echo "| 빈 문서 | $empty_docs |" | tee -a "$LOG_FILE"
    echo "| 고아 문서 | $orphan_docs |" | tee -a "$LOG_FILE"
    echo "| 오래된 문서 | $old_docs |" | tee -a "$LOG_FILE"
    echo "| 총 문서 | $total_docs |" | tee -a "$LOG_FILE"
    echo ""
} >> "$LOG_MD"

# ============================================================================
# 최종 결과
# ============================================================================
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "[$TIMESTAMP] ✅ Wiki 린트 완료!" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "📊 검사 결과 요약:" | tee -a "$LOG_FILE"
echo "   🔗 깨진 링크: $broken_links개 수정" | tee -a "$LOG_FILE"
echo "   📝 이중 타이틀: $duplicate_titles개 수정" | tee -a "$LOG_FILE"
echo "   📄 빈 문서: $empty_docs개 발견" | tee -a "$LOG_FILE"
echo "   👻 고아 문서: $orphan_docs개 발견" | tee -a "$LOG_FILE"
echo "   ⏰ 오래된 문서: $old_docs개 발견" | tee -a "$LOG_FILE"
echo "   📚 총 문서: $total_docs개" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

#!/bin/bash
# Wiki Query 스크립트
# Wiki에서 정보를 검색하고 답변을 생성합니다

VAULT="/home/comage/obsidian-vault/06-Wiki-시스템"
WIKI="$VAULT/Wiki"

# 검색어 가져오기
SEARCH_TERM="$1"

if [ -z "$SEARCH_TERM" ]; then
    echo "📖 Wiki 검색"
    echo "================"
    echo ""
    echo "사용법: bash wiki-query.sh \"검색어\""
    echo ""
    echo "📚 전체 문서 목록:"
    echo ""
    for file in "$WIKI"/*.md; do
        [ -f "$file" ] || continue
        [ "$(basename "$file")" = "인덱스.md" ] && continue
        title=$(head -1 "$file" | sed 's/^#*\s*//')
        echo "  - $title"
    done
    echo ""
    exit 0
fi

echo "🔍 Wiki 검색: \"$SEARCH_TERM\""
echo "================"
echo ""

# 검색 결과 저장
results=()

# 1. 파일 이름에서 검색
for file in "$WIKI"/*.md; do
    [ -f "$file" ] || continue
    [ "$(basename "$file")" = "인덱스.md" ] && continue
    
    filename=$(basename "$file" .md)
    if echo "$filename" | grep -qi "$SEARCH_TERM"; then
        results+=("$file|이름 일치: $filename")
    fi
done

# 2. 파일 내용에서 검색
for file in "$WIKI"/*.md; do
    [ -f "$file" ] || continue
    [ "$(basename "$file")" = "인덱스.md" ] && continue
    
    if grep -qi "$SEARCH_TERM" "$file"; then
        # 이미 추가되지 않았는지 확인
        already_added=0
        for existing in "${results[@]}"; do
            if echo "$existing" | grep -q "$file|"; then
                already_added=1
                break
            fi
        done
        if [ $already_added -eq 0 ]; then
            results+=("$file|내용 일치")
        fi
    fi
done

# 3. 태그에서 검색
for file in "$WIKI"/*.md; do
    [ -f "$file" ] || continue
    [ "$(basename "$file")" = "인덱스.md" ] && continue
    
    if grep -qi "#$SEARCH_TERM" "$file"; then
        already_added=0
        for existing in "${results[@]}"; do
            if echo "$existing" | grep -q "$file|"; then
                already_added=1
                break
            fi
        done
        if [ $already_added -eq 0 ]; then
            results+=("$file|태그 일치")
        fi
    fi
done

# 결과 출력
if [ ${#results[@]} -eq 0 ]; then
    echo "❌ 검색 결과가 없습니다."
    echo ""
    echo "💡 다른 검색어를 시도해 보세요."
    exit 0
fi

echo "✅ ${#results[@]}개의 결과를 찾았습니다."
echo ""
echo "📄 검색 결과:"
echo ""

count=1
for result in "${results[@]}"; do
    file=$(echo "$result" | cut -d'|' -f1)
    match_type=$(echo "$result" | cut -d'|' -f2)
    title=$(head -1 "$file" | sed 's/^#*\s*//')
    
    echo "[$count] $title"
    echo "    유형: $match_type"
    echo "    파일: $(basename "$file")"
    
    # 요약 추출 (첫 번째 설명 부분)
    summary=$(grep -A2 "^## 요약" "$file" | tail -n+2 | head -3 | sed 's/^/    /')
    if [ -n "$summary" ]; then
        echo "    요약: $summary"
    fi
    echo ""
    
    count=$((count + 1))
done

echo "----------------"
echo "상세 내용 보려면 Obsidian에서 문서를 여세요."

#!/bin/bash
# 신규 파일 자동 인덱싱 스크립트
# 실행: 파일 생성 시 자동 실행 (inotifywait 사용)

OBSIDIAN_DIR="/tmp/obsidian-vault"
LOG_FILE="$OBSIDIAN_DIR/.maintenance/logs/auto_index_$(date +%Y%m%d).log"

echo "🤖 신규 파일 자동 인덱싱 시작: $(date)" | tee -a "$LOG_FILE"

# inotifywait로 새 파일 감시
inotifywait -m -e create -e moved_to --format "%w%f" "$OBSIDIAN_DIR" |
while read -r new_file; do
    # 마크다운 파일만 처리
    if [[ "$new_file" == *.md ]]; then
        filename=$(basename "$new_file" .md)
        
        echo "📄 새 파일 감지: $filename" | tee -a "$LOG_FILE"
        
        # 이미 인덱스에 있는지 확인
        if grep -q "\[\[$filename\]\]" "$OBSIDIAN_DIR/index.md"; then
            echo "  ⚠️ 이미 인덱스에 존재" | tee -a "$LOG_FILE"
            continue
        fi
        
        # 파일 내용 분석으로 카테고리 결정
        if grep -q -i "vf\|보노하우스\|생산" "$new_file"; then
            CATEGORY="VF 프로젝트"
        elif grep -q -i "키프로젝트\|키움\|ai\|매매" "$new_file"; then
            CATEGORY="키 프로젝트"
        elif grep -q -i "시스템\|설정\|설치\|가이드" "$new_file"; then
            CATEGORY="시스템 문서"
        elif [[ "$filename" =~ ^2026- ]]; then
            CATEGORY="일일 작업 기록"
        else
            CATEGORY="기타 문서"
        fi
        
        # 인덱스에 추가
        sed -i "/$CATEGORY/a - [[$filename]]" "$OBSIDIAN_DIR/index.md"
        
        echo "  ✅ 인덱스 추가: $filename → $CATEGORY" | tee -a "$LOG_FILE"
        
        # 통계 업데이트
        TOTAL_FILES=$(find "$OBSIDIAN_DIR" -name "*.md" -type f | wc -l)
        LINKED_FILES=$(grep -c "\[\[.*\]\]" "$OBSIDIAN_DIR/index.md")
        CONNECTION_RATE=$(echo "scale=1; $LINKED_FILES * 100 / $TOTAL_FILES" | bc)
        
        echo "  📊 현재 연결률: $CONNECTION_RATE% ($LINKED_FILES/$TOTAL_FILES)" | tee -a "$LOG_FILE"
    fi
done

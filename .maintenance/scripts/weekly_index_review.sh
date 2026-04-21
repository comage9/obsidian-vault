#!/bin/bash
# 주간 인덱스 검토 스크립트
# 실행: 매주 월요일 09:00

OBSIDIAN_DIR="/tmp/obsidian-vault"
LOG_FILE="$OBSIDIAN_DIR/.maintenance/logs/weekly_$(date +%Y%m%d).log"
REPORT_FILE="$OBSIDIAN_DIR/.maintenance/reports/weekly_$(date +%Y%m%d).md"

echo "🔍 주간 인덱스 검토 시작: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

cd "$OBSIDIAN_DIR"

# 1. 현재 상태 확인
TOTAL_FILES=$(find . -name "*.md" -type f | wc -l)
LINKED_FILES=$(grep -c "\[\[.*\]\]" index.md)
CONNECTION_RATE=$(echo "scale=1; $LINKED_FILES * 100 / $TOTAL_FILES" | bc)

echo "📊 현재 상태:" | tee -a "$LOG_FILE"
echo "  - 전체 파일: $TOTAL_FILES개" | tee -a "$LOG_FILE"
echo "  - 연결된 파일: $LINKED_FILES개" | tee -a "$LOG_FILE"
echo "  - 연결률: $CONNECTION_RATE%" | tee -a "$LOG_FILE"

# 2. 연결되지 않은 파일 찾기
echo -e "\n🔍 연결되지 않은 파일 검색 중..." | tee -a "$LOG_FILE"
UNLINKED_COUNT=0
UNLINKED_LIST=""

find . -name "*.md" -type f | while read -r file; do
    filename=$(basename "$file" .md)
    if [[ "$filename" != "index" ]] && ! grep -q "\[\[$filename\]\]" index.md 2>/dev/null; then
        UNLINKED_COUNT=$((UNLINKED_COUNT + 1))
        UNLINKED_LIST="$UNLINKED_LIST\n  - $filename"
        echo "  발견: $filename" | tee -a "$LOG_FILE"
    fi
done

# 3. 인덱스 업데이트 (자동)
if [ $UNLINKED_COUNT -gt 0 ]; then
    echo -e "\n🔄 인덱스 자동 업데이트 중..." | tee -a "$LOG_FILE"
    
    # 시스템 파일 카테고리 확인 및 추가
    find . -name "*.md" -type f | while read -r file; do
        filename=$(basename "$file" .md)
        if [[ "$filename" != "index" ]] && ! grep -q "\[\[$filename\]\]" index.md 2>/dev/null; then
        
            # 파일 내용 분석으로 카테고리 결정
            if grep -q -i "vf\|보노하우스\|생산" "$file"; then
                CATEGORY="VF 프로젝트"
            elif grep -q -i "키프로젝트\|키움\|ai\|매매" "$file"; then
                CATEGORY="키 프로젝트"
            elif grep -q -i "시스템\|설정\|설치\|가이드" "$file"; then
                CATEGORY="시스템 문서"
            elif [[ "$filename" =~ ^2026- ]]; then
                CATEGORY="일일 작업 기록"
            else
                CATEGORY="기타 문서"
            fi
            
            # 인덱스에 추가
            sed -i "/$CATEGORY/a - [[$filename]]" index.md
            echo "  추가됨: $filename → $CATEGORY" | tee -a "$LOG_FILE"
        fi
    done
    
    # 통계 재계산
    LINKED_FILES_NEW=$(grep -c "\[\[.*\]\]" index.md)
    CONNECTION_RATE_NEW=$(echo "scale=1; $LINKED_FILES_NEW * 100 / $TOTAL_FILES" | bc)
    
    echo -e "\n✅ 업데이트 완료:" | tee -a "$LOG_FILE"
    echo "  - 새 연결 파일: $((LINKED_FILES_NEW - LINKED_FILES))개" | tee -a "$LOG_FILE"
    echo "  - 새 연결률: $CONNECTION_RATE_NEW%" | tee -a "$LOG_FILE"
else
    echo -e "\n✅ 모든 파일이 이미 연결됨" | tee -a "$LOG_FILE"
fi

# 4. 보고서 생성
cat > "$REPORT_FILE" << REPORT_EOF
# 주간 인덱스 검토 보고서
**날짜**: $(date +"%Y년 %m월 %d일")
**실행 시간**: $(date +"%H:%M:%S")

## 📊 통계 요약
- **전체 파일**: $TOTAL_FILES개
- **연결된 파일**: $LINKED_FILES_NEW개
- **연결률**: $CONNECTION_RATE_NEW%
- **진행률**: $(python3 -c "rate=$CONNECTION_RATE_NEW; filled=int(rate/10); print('█'*filled + '░'*(10-filled) + f' {rate}%')")

## 🔄 변경사항
- **새로 연결된 파일**: $((LINKED_FILES_NEW - LINKED_FILES))개
- **연결률 변화**: $CONNECTION_RATE% → $CONNECTION_RATE_NEW%

## 🎯 다음 주 목표
- 연결률: $CONNECTION_RATE_NEW% → $((CONNECTION_RATE_NEW + 10))%
- 주간 검토: 다음 월요일 09:00

## 📝 로그 요약
$(tail -20 "$LOG_FILE")

---
*이 보고서는 자동 생성되었습니다.*
REPORT_EOF

echo -e "\n📄 보고서 생성 완료: $REPORT_FILE" | tee -a "$LOG_FILE"
echo "🔍 주간 인덱스 검토 완료: $(date)" | tee -a "$LOG_FILE"

#!/bin/bash
# 연결률 모니터링 스크립트
# 실행: 매일 18:00

OBSIDIAN_DIR="/tmp/obsidian-vault"
DASHBOARD_FILE="$OBSIDIAN_DIR/.maintenance/reports/connection_dashboard.md"

echo "📈 연결률 모니터링 시작: $(date)"

cd "$OBSIDIAN_DIR"

# 통계 계산
TOTAL_FILES=$(find . -name "*.md" -type f | wc -l)
LINKED_FILES=$(grep -c "\[\[.*\]\]" index.md)
CONNECTION_RATE=$(echo "scale=1; $LINKED_FILES * 100 / $TOTAL_FILES" | bc)

# 진행률 바
PROGRESS_BAR=$(python3 << PYEOF
rate = $CONNECTION_RATE
filled = int(rate / 10)
empty = 10 - filled
print("█" * filled + "░" * empty + f" {rate}%")
PYEOF
)

# 대시보드 업데이트
cat > "$DASHBOARD_FILE" << DASH_EOF
# 옵시디언 연결률 모니터링 대시보드

**최근 업데이트**: $(date +"%Y년 %m월 %d일 %H:%M")

## 📊 실시간 통계

### 기본 통계
- **전체 파일**: $TOTAL_FILES개
- **연결된 파일**: $LINKED_FILES개
- **연결률**: $CONNECTION_RATE%
- **진행률**: $PROGRESS_BAR

### 목표 진행 상황
| 단계 | 목표 연결률 | 현재 상태 | 완료 여부 |
|------|-------------|-----------|-----------|
| 1단계 | 50% | $CONNECTION_RATE% | $(if [ $(echo "$CONNECTION_RATE >= 50" | bc) -eq 1 ]; then echo "✅"; else echo "⏳"; fi) |
| 2단계 | 75% | $CONNECTION_RATE% | $(if [ $(echo "$CONNECTION_RATE >= 75" | bc) -eq 1 ]; then echo "✅"; else echo "⏳"; fi) |
| 3단계 | 100% | $CONNECTION_RATE% | $(if [ $(echo "$CONNECTION_RATE >= 100" | bc) -eq 1 ]; then echo "✅"; else echo "⏳"; fi) |

## 📈 추세 분석

### 일별 변화
$(find "$OBSIDIAN_DIR/.maintenance/reports" -name "weekly_*.md" -type f | sort -r | head -5 | while read -r report; do
    date=$(basename "$report" .md | sed 's/weekly_//')
    stats=$(grep -A3 "📊 통계 요약" "$report" | tail -3)
    echo "- **$date**: $stats"
done)

## 🔄 최근 활동

### 마지막 주간 검토
$(if [ -f "$OBSIDIAN_DIR/.maintenance/logs/weekly_$(date +%Y%m%d).log" ]; then
    tail -5 "$OBSIDIAN_DIR/.maintenance/logs/weekly_$(date +%Y%m%d).log"
else
    echo "오늘 주간 검토 없음"
fi)

### 자동 인덱싱 로그
$(if [ -f "$OBSIDIAN_DIR/.maintenance/logs/auto_index_$(date +%Y%m%d).log" ]; then
    tail -5 "$OBSIDIAN_DIR/.maintenance/logs/auto_index_$(date +%Y%m%d).log"
else
    echo "오늘 자동 인덱싱 없음"
fi)

## 🎯 다음 작업

### 우선순위 작업
1. **연결되지 않은 파일 처리**: $((TOTAL_FILES - LINKED_FILES))개 남음
2. **카테고리 정리**: 파일 분류 최적화
3. **중복 링크 제거**: 인덱스 정리

### 예상 완료일
$(python3 << PYEOF
import datetime
current_rate = $CONNECTION_RATE
remaining = 100 - current_rate
if remaining > 0:
    # 주당 10% 향상 가정
    weeks_needed = remaining / 10
    today = datetime.datetime.now()
    completion_date = today + datetime.timedelta(weeks=weeks_needed)
    print(f"**예상 완료일**: {completion_date.strftime('%Y년 %m월 %d일')}")
    print(f"**남은 주**: {weeks_needed:.1f}주")
else:
    print("**🎉 목표 달성 완료!**")
PYEOF
)

---
*이 대시보드는 매일 자동 업데이트됩니다.*
DASH_EOF

echo "✅ 대시보드 업데이트 완료: $DASHBOARD_FILE"
